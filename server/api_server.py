"""
API Server for Grok Agentic Research Agent
Provides REST API endpoints for the web UI
"""
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import json
import os
import sys
import time
from pathlib import Path

# Add server directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from data_generator import MockXDataGenerator
from agent import AgenticResearchAgent
import config

# Get the project root directory (parent of server/)
PROJECT_ROOT = Path(__file__).parent.parent
CLIENT_DIR = PROJECT_ROOT / 'client'

app = Flask(__name__, static_folder=str(CLIENT_DIR / 'static'), static_url_path='')
CORS(app)  # Enable CORS for frontend

# Global agent instance (initialized on first request)
agent = None
data = None

def initialize_agent():
    """Initialize the agent and load data"""
    global agent, data
    
    if agent is None:
        # Load or generate data
        # Use absolute path relative to project root
        data_file = config.DATA_FILE
        if not Path(data_file).is_absolute():
            data_file = PROJECT_ROOT / data_file
        data_path = Path(data_file)
        
        if data_path.exists():
            print(f"📂 Loading data from {data_file}...")
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"   ✅ Loaded {len(data)} posts")
        else:
            print(f"📝 Generating mock dataset...")
            generator = MockXDataGenerator(seed=42)
            data = generator.generate_dataset(
                num_posts=config.MOCK_DATA_SIZE,
                include_threads=True
            )
            generator.save_to_file(data_file)
            print(f"   ✅ Generated {len(data)} posts")
        
        # Initialize agent
        try:
            agent = AgenticResearchAgent(data)
            print("✅ Agent initialized")
        except ValueError as e:
            print(f"❌ Error initializing agent: {e}")
            raise
    
    return agent, data

@app.route('/')
def index():
    """Serve the main HTML page"""
    index_path = CLIENT_DIR / 'static' / 'index.html'
    if not index_path.exists():
        return jsonify({
            "error": "HTML file not found",
            "path": str(index_path),
            "client_dir": str(CLIENT_DIR),
            "exists": index_path.exists()
        }), 404
    
    # Read and return the HTML file
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        from flask import Response
        return Response(html_content, mimetype='text/html')
    except Exception as e:
        return jsonify({"error": str(e), "path": str(index_path)}), 500

@app.route('/api/query', methods=['POST'])
def query():
    """
    Main API endpoint for research queries with Server-Sent Events
    
    Request body:
        {
            "query": "your research question"
        }
    
    Returns:
        Server-Sent Events stream with progress updates and final result
    """
    def generate():
        try:
            # Get query from request
            request_data = request.get_json()
            if not request_data or 'query' not in request_data:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Missing query in request body'})}\n\n"
                return
            
            query_text = request_data['query'].strip()
            if not query_text:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Query cannot be empty'})}\n\n"
                return
            
            # Initialize agent if needed
            agent_instance, _ = initialize_agent()
            
            # Create a queue for progress events
            import queue
            progress_queue = queue.Queue()
            
            def progress_handler(event_type, data):
                event_data = {
                    'type': event_type,
                    'timestamp': time.time(),
                    **data
                }
                progress_queue.put(event_data)
            
            # Set progress callback
            agent_instance.progress_callback = progress_handler
            
            # Start workflow in a thread
            import threading
            result_container = {'result': None, 'error': None, 'done': False}
            
            def run_workflow():
                try:
                    result = agent_instance.run_workflow(query_text)
                    result_container['result'] = result
                    
                    # Save results
                    output_dir = PROJECT_ROOT / "output"
                    output_dir.mkdir(exist_ok=True)
                    output_file = output_dir / "research_result.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                except Exception as e:
                    import traceback
                    result_container['error'] = str(e)
                    result_container['traceback'] = traceback.format_exc()
                finally:
                    result_container['done'] = True
            
            # Start workflow thread
            workflow_thread = threading.Thread(target=run_workflow, daemon=True)
            workflow_thread.start()
            
            # Stream progress events
            while not result_container['done'] or not progress_queue.empty():
                try:
                    # Get progress event with timeout
                    event = progress_queue.get(timeout=0.5)
                    yield f"data: {json.dumps(event)}\n\n"
                except queue.Empty:
                    # Check if thread is still alive
                    if not workflow_thread.is_alive() and result_container['done']:
                        break
                    # Send heartbeat to keep connection alive
                    yield f": heartbeat\n\n"
                    continue
            
            # Wait for thread to complete
            workflow_thread.join(timeout=1)
            
            # Send final result
            if result_container['error']:
                yield f"data: {json.dumps({'type': 'error', 'message': result_container['error']})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'complete', 'result': result_container['result']})}\n\n"
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ API Error: {error_details}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        agent_instance, data_instance = initialize_agent()
        return jsonify({
            "status": "healthy",
            "agent_initialized": agent_instance is not None,
            "data_loaded": data_instance is not None and len(data_instance) > 0
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/api/examples', methods=['GET'])
def examples():
    """Get example queries"""
    return jsonify({
        "examples": [
            "What are people saying about AI safety?",
            "Find the most discussed topics this week",
            "Compare sentiment about crypto vs traditional finance",
            "What are the main concerns about machine learning?",
            "Find posts from verified accounts about Python"
        ]
    })

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 8080))
    
    print("\n" + "="*70)
    print("🚀 Starting Grok Agentic Research API Server")
    print("="*70)
    print("\nAPI Endpoints:")
    print("  GET  /              - Web UI")
    print("  POST /api/query     - Submit research query")
    print("  GET  /api/health    - Health check")
    print("  GET  /api/examples  - Get example queries")
    print(f"\nClient directory: {CLIENT_DIR}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"\n🌐 Server running on: http://localhost:{port}")
    print("\n" + "="*70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)
