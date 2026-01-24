"""
Evaluation routes - Batch evaluation and model comparison endpoints
"""
import json
import time
import queue
import threading
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List

from . import evaluation_router


class EvaluationRequest(BaseModel):
    """Request model for evaluation endpoint"""
    max_queries: Optional[int] = None
    delay: float = 1.0
    model: Optional[str] = None
    save_individual: bool = True
    parallel: bool = False
    max_workers: int = 3


class ModelComparisonRequest(BaseModel):
    """Request model for model comparison endpoint"""
    max_queries: Optional[int] = None
    delay: float = 1.0
    models: Optional[List[str]] = None


@evaluation_router.post("/evaluate")
def run_evaluation(request: EvaluationRequest):
    """
    Run batch evaluation on test queries
    
    Request body:
        {
            "max_queries": 10,  // Optional: limit number of queries
            "delay": 1.0,       // Delay between queries (sequential mode only)
            "model": "grok-4-fast-reasoning",  // Optional: override model
            "save_individual": true,  // Save individual result files
            "parallel": false,  // Use parallel execution
            "max_workers": 3  // Max concurrent workers (parallel mode)
        }
    
    Returns:
        Server-Sent Events stream with progress updates and final metrics
    """
    from app import get_project_root
    
    def generate():
        try:
            project_root = get_project_root()
            
            # Import here to avoid circular imports
            from evaluation.evaluator import BatchEvaluator
            from evaluation.metrics import MetricsCalculator
            
            # Setup model config if specified
            model_config = None
            if request.model:
                model_config = {
                    "PLANNER_MODEL": request.model,
                    "ANALYZER_MODEL": request.model,
                    "REFINER_MODEL": request.model,
                    "SUMMARIZER_MODEL": request.model
                }
            
            # Initialize evaluator
            evaluator = BatchEvaluator(project_root, model_config=model_config)
            
            # Load queries
            queries = evaluator.load_test_queries()
            
            # Create progress queue
            progress_queue = queue.Queue()
            result_container = {'result': None, 'error': None, 'done': False}
            
            def run_evaluation_thread():
                try:
                    evaluation_data = evaluator.run_evaluation(
                        queries,
                        max_queries=request.max_queries,
                        delay_between_queries=request.delay,
                        save_individual_results=request.save_individual,
                        parallel=request.parallel,
                        max_workers=request.max_workers
                    )
                    
                    # Save evaluation
                    output_file = evaluator.save_evaluation(evaluation_data, None)
                    evaluation_data["output_file"] = str(output_file)
                    
                    result_container['result'] = evaluation_data
                except Exception as e:
                    import traceback
                    result_container['error'] = str(e)
                    result_container['traceback'] = traceback.format_exc()
                finally:
                    result_container['done'] = True
            
            # Start evaluation thread
            eval_thread = threading.Thread(target=run_evaluation_thread, daemon=True)
            eval_thread.start()
            
            # Stream progress (simplified - could enhance with more detailed progress)
            query_count = request.max_queries or len(queries)
            for i in range(query_count):
                if result_container['done']:
                    break
                
                # Send progress update
                progress = {
                    'type': 'evaluation_progress',
                    'query_number': i + 1,
                    'total_queries': query_count,
                    'message': f'Running query {i + 1}/{query_count}...'
                }
                yield f"data: {json.dumps(progress)}\n\n"
                
                # Wait a bit (actual progress comes from agent's progress_callback)
                time.sleep(request.delay)
            
            # Wait for thread to complete
            eval_thread.join(timeout=300)  # 5 minute timeout
            
            # Send final result
            if result_container['error']:
                yield f"data: {json.dumps({'type': 'error', 'message': result_container['error']})}\n\n"
            else:
                result = result_container['result']
                yield f"data: {json.dumps({'type': 'complete', 'result': result})}\n\n"
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Evaluation API Error: {error_details}")
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


@evaluation_router.post("/compare-models")
def compare_models(request: ModelComparisonRequest):
    """
    Compare different Grok models
    
    Request body:
        {
            "max_queries": 5,  // Optional: limit queries per model
            "delay": 1.0,     // Delay between queries
            "models": ["grok-4-fast-reasoning", "grok-3"]  // Optional: specific models
        }
    
    Returns:
        Server-Sent Events stream with comparison progress and results
    """
    from app import get_project_root
    
    def generate():
        try:
            project_root = get_project_root()
            
            from evaluation.compare_models import compare_models, MODEL_CONFIGS
            from evaluation.evaluator import BatchEvaluator
            
            # Load queries
            evaluator = BatchEvaluator(project_root)
            queries = evaluator.load_test_queries()
            
            # Filter models if specified
            model_configs = MODEL_CONFIGS
            if request.models:
                model_configs = {name: MODEL_CONFIGS[name] for name in request.models if name in MODEL_CONFIGS}
                if not model_configs:
                    yield f"data: {json.dumps({'type': 'error', 'message': f'No valid models found. Available: {list(MODEL_CONFIGS.keys())}'})}\n\n"
                    return
            
            # Send initial progress
            yield f"data: {json.dumps({'type': 'comparison_start', 'models': list(model_configs.keys()), 'total_queries': request.max_queries or len(queries)})}\n\n"
            
            # Run comparison
            comparison = compare_models(
                project_root,
                queries,
                model_configs=model_configs,
                max_queries=request.max_queries,
                delay_between_queries=request.delay
            )
            
            # Send final result
            yield f"data: {json.dumps({'type': 'complete', 'result': comparison})}\n\n"
        
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


@evaluation_router.get("/evaluation/models")
def get_available_models():
    """Get list of available Grok models for evaluation and comparison"""
    try:
        from evaluation.compare_models import MODEL_CONFIGS
        import config
    except ImportError:
        return {"models": ["grok-4-fast-reasoning"], "default": "grok-4-fast-reasoning"}
    models = list(MODEL_CONFIGS.keys())
    default = getattr(config.ModelConfig, "PLANNER_MODEL", models[0] if models else "grok-4-fast-reasoning")
    return {"models": models, "default": default}


@evaluation_router.get("/evaluation/queries")
def get_test_queries():
    """Get list of test queries for evaluation"""
    from app import get_project_root
    from pathlib import Path
    
    project_root = get_project_root()
    queries_file = project_root / "server" / "evaluation" / "test_queries.json"
    
    if not queries_file.exists():
        raise HTTPException(status_code=404, detail="Test queries file not found")
    
    with open(queries_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return {
        "queries": data.get("queries", []),
        "metadata": data.get("metadata", {})
    }


