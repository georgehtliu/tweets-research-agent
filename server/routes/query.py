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
from typing import Optional, List
from . import query_router


class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str
    fast_mode: Optional[bool] = None  # Override config; None = use config default


class ModelComparisonQueryRequest(BaseModel):
    """Request model for parallel model comparison"""
    query: str
    models: List[str]  # e.g. ["grok-4-fast-reasoning", "grok-3", "grok"]
    fast_mode: Optional[bool] = None


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


@query_router.post("/query/compare-models")
def compare_models_query(request: ModelComparisonQueryRequest):
    """
    Run a single query across multiple models in parallel
    
    Request body:
        {
            "query": "your research question",
            "models": ["grok-4-fast-reasoning", "grok-3", "grok"],
            "fast_mode": true  // optional
        }
    
    Returns:
        Server-Sent Events stream with progress updates and results for each model
    """
    from app import get_agent_service, get_project_root
    from evaluation.compare_models import MODEL_CONFIGS
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def generate():
        try:
            query_text = request.query.strip()
            if not query_text:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Query cannot be empty'})}\n\n"
                return
            
            # Validate models
            valid_models = []
            for model in request.models:
                if model in MODEL_CONFIGS:
                    valid_models.append(model)
                else:
                    yield f"data: {json.dumps({'type': 'model_error', 'model': model, 'message': f'Unknown model: {model}'})}\n\n"
            
            if not valid_models:
                yield f"data: {json.dumps({'type': 'error', 'message': 'No valid models selected'})}\n\n"
                return
            
            yield f"data: {json.dumps({'type': 'comparison_start', 'models': valid_models, 'query': query_text})}\n\n"
            
            # Results container: model_name -> {result, error, logs, done}
            results = {model: {'result': None, 'error': None, 'logs': [], 'done': False} for model in valid_models}
            
            # Queue for streaming logs in real-time
            log_queue = queue.Queue()
            
            def run_model(model_name: str):
                """Run query for a single model"""
                try:
                    model_config = MODEL_CONFIGS[model_name]
                    agent_service = get_agent_service()
                    agent_instance, _ = agent_service.initialize_agent(model_config=model_config)
                    
                    # Collect logs and stream them in real-time
                    logs = []
                    def log_handler(event_type, data):
                        log_entry = {'type': event_type, 'timestamp': time.time(), 'model': model_name, **data}
                        logs.append(log_entry)
                        # Stream log immediately
                        log_queue.put(('log', log_entry))
                    
                    agent_instance.progress_callback = log_handler
                    
                    result = agent_instance.run_workflow(query_text, fast_mode=request.fast_mode)
                    results[model_name]['result'] = result
                    results[model_name]['logs'] = logs
                except Exception as e:
                    import traceback
                    error_msg = str(e)
                    results[model_name]['error'] = error_msg
                    results[model_name]['traceback'] = traceback.format_exc()
                    # Stream error log
                    log_queue.put(('log', {
                        'type': 'error',
                        'timestamp': time.time(),
                        'model': model_name,
                        'message': error_msg
                    }))
                finally:
                    results[model_name]['done'] = True
                    # Signal completion
                    log_queue.put(('done', model_name))
            
            # Start models in parallel
            executor = ThreadPoolExecutor(max_workers=len(valid_models))
            futures = {executor.submit(run_model, model): model for model in valid_models}
            
            # Stream logs and wait for completion
            completed_models = set()
            while len(completed_models) < len(valid_models):
                try:
                    # Check for new logs
                    item_type, item_data = log_queue.get(timeout=0.5)
                    if item_type == 'log':
                        # Stream log event
                        yield f"data: {json.dumps({'type': 'model_log', 'log': item_data})}\n\n"
                    elif item_type == 'done':
                        completed_models.add(item_data)
                except queue.Empty:
                    # Check if any futures completed
                    for future in list(futures.keys()):
                        if future.done():
                            model_name = futures.pop(future)
                            try:
                                future.result()  # Get any exceptions
                            except Exception as e:
                                pass  # Already handled in run_model
                    continue
            
            executor.shutdown(wait=True)
            
            # Send model completion events
            for model_name in valid_models:
                if results[model_name]['error']:
                    yield f"data: {json.dumps({'type': 'model_complete', 'model': model_name, 'status': 'error', 'error': results[model_name]['error']})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'model_complete', 'model': model_name, 'status': 'success', 'result': results[model_name]['result']})}\n\n"
            
            # Generate comparison summary
            comparison_summary = {
                'query': query_text,
                'models': valid_models,
                'results': {},
                'summary': {}
            }
            
            for model_name in valid_models:
                if results[model_name]['error']:
                    comparison_summary['results'][model_name] = {'error': results[model_name]['error']}
                else:
                    result = results[model_name]['result']
                    # Defensive check: ensure result is a dict
                    if result is None:
                        comparison_summary['results'][model_name] = {
                            'error': 'No result returned from workflow',
                            'logs': results[model_name]['logs']
                        }
                    elif not isinstance(result, dict):
                        comparison_summary['results'][model_name] = {
                            'error': f'Invalid result format: expected dict, got {type(result).__name__}',
                            'raw_result': str(result)[:200] if result else 'None',  # Truncate for safety
                            'logs': results[model_name]['logs']
                        }
                    else:
                        # Safely extract analysis (might be None or not a dict)
                        analysis = result.get('analysis')
                        if isinstance(analysis, dict):
                            confidence = analysis.get('confidence', 0)
                        else:
                            confidence = 0
                        
                        comparison_summary['results'][model_name] = {
                            'success': True,
                            'confidence': confidence,
                            'execution_steps': result.get('execution_steps', 0),
                            'replan_count': result.get('replan_count', 0),
                            'summary': result.get('final_summary', ''),
                            'logs': results[model_name]['logs']
                        }
            
            # Find best performers
            successful = {k: v for k, v in comparison_summary['results'].items() if v.get('success')}
            if successful:
                best_confidence = max(successful.items(), key=lambda x: x[1].get('confidence', 0))
                most_efficient = min(successful.items(), key=lambda x: x[1].get('execution_steps', float('inf')))
                comparison_summary['summary'] = {
                    'best_confidence': {'model': best_confidence[0], 'value': best_confidence[1]['confidence']},
                    'most_efficient': {'model': most_efficient[0], 'value': most_efficient[1]['execution_steps']}
                }
            
            # Send final comparison summary
            yield f"data: {json.dumps({'type': 'comparison_complete', 'summary': comparison_summary})}\n\n"
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Model Comparison API Error: {error_details}")
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


@query_router.get("/tweets")
def get_tweets(page: int = 1, per_page: int = 20, category: Optional[str] = None, language: Optional[str] = None):
    """
    Get paginated tweets with optional filters
    
    Query parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
        category: Filter by category (optional)
        language: Filter by language (optional)
    
    Returns:
        JSON with tweets, pagination info, and total count
    """
    from app import get_agent_service
    
    try:
        print(f"📊 Tweets API called: page={page}, per_page={per_page}, category={category}, language={language}")
        agent_service = get_agent_service()
        _, data = agent_service.initialize_agent()
        
        print(f"✅ Loaded {len(data)} total posts from dataset")
        
        # Apply filters
        filtered_data = data
        if category:
            filtered_data = [p for p in filtered_data if p.get("category") == category]
            print(f"   Filtered by category '{category}': {len(filtered_data)} posts")
        if language:
            filtered_data = [p for p in filtered_data if p.get("language") == language]
            print(f"   Filtered by language '{language}': {len(filtered_data)} posts")
        
        # Calculate pagination
        total = len(filtered_data)
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Get page of tweets
        page_tweets = filtered_data[start_idx:end_idx]
        
        print(f"   Returning page {page}: {len(page_tweets)} tweets (total: {total})")
        
        return {
            "tweets": page_tweets,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Tweets API Error: {error_details}")
        raise HTTPException(status_code=500, detail=str(e))
