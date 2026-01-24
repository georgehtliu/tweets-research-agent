"""
Query routes - Research query endpoints with SSE
"""
import json
import time
import queue
import threading
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from . import query_router


class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str
    fast_mode: Optional[bool] = None  # Override config; None = use config default


@query_router.post("/query")
def query(request: QueryRequest):
    """
    Main API endpoint for research queries with Server-Sent Events
    
    Request body:
        {
            "query": "your research question",
            "fast_mode": true  // optional; skip evaluate/critique for speed
        }
    
    Returns:
        Server-Sent Events stream with progress updates and final result
    """
    from app import get_agent_service, get_project_root
    
    def generate():
        try:
            # Validate query
            query_text = request.query.strip()
            if not query_text:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Query cannot be empty'})}\n\n"
                return
            
            # Initialize agent if needed
            agent_service = get_agent_service()
            agent_instance, _ = agent_service.initialize_agent()
            
            # Create a queue for progress events
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
            result_container = {'result': None, 'error': None, 'done': False}
            
            def run_workflow():
                try:
                    result = agent_instance.run_workflow(
                        query_text,
                        fast_mode=request.fast_mode
                    )
                    result_container['result'] = result
                    
                    # Save results
                    project_root = get_project_root()
                    output_dir = project_root / "output"
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
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )
