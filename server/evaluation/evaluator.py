"""
Batch Evaluation Runner
Runs agent on multiple queries and collects metrics
"""
import json
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add server directory to path
server_dir = Path(__file__).parent.parent
sys.path.insert(0, str(server_dir))

from agent import AgenticResearchAgent
from services.agent_service import AgentService
from evaluation.metrics import MetricsCalculator
import config


class BatchEvaluator:
    """Batch evaluation runner for testing agent on multiple queries"""
    
    def __init__(self, project_root: Path, model_config: Optional[Dict] = None):
        """
        Initialize evaluator
        
        Args:
            project_root: Project root directory
            model_config: Optional dict to override model config (for model comparison)
        """
        self.project_root = project_root
        self.model_config = model_config
        self.agent_service = AgentService(project_root)
        self.results: List[Dict] = []
        
        # Override model config if provided
        if model_config:
            self._apply_model_config(model_config)
    
    def _apply_model_config(self, model_config: Dict):
        """Temporarily override model config for this evaluation"""
        for key, value in model_config.items():
            if hasattr(config.ModelConfig, key):
                setattr(config.ModelConfig, key, value)
    
    def load_test_queries(self, queries_file: str = None) -> List[Dict]:
        """
        Load test queries from JSON file
        
        Args:
            queries_file: Path to test queries JSON (default: evaluation/test_queries.json)
            
        Returns:
            List of query dictionaries
        """
        if queries_file is None:
            queries_file = self.project_root / "server" / "evaluation" / "test_queries.json"
        else:
            queries_file = Path(queries_file)
        
        if not queries_file.exists():
            raise FileNotFoundError(f"Test queries file not found: {queries_file}")
        
        with open(queries_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get("queries", [])
    
    def run_evaluation(
        self,
        queries: List[Dict],
        max_queries: Optional[int] = None,
        delay_between_queries: float = 1.0,
        save_individual_results: bool = True,
        parallel: bool = False,
        max_workers: int = 3
    ) -> Dict:
        """
        Run evaluation on multiple queries
        
        Args:
            queries: List of query dictionaries
            max_queries: Maximum number of queries to run (None = all)
            delay_between_queries: Seconds to wait between queries (for sequential mode)
            save_individual_results: Save individual result files
            parallel: Use parallel execution (default: False)
            max_workers: Maximum concurrent workers for parallel mode
            
        Returns:
            Dict with all results and summary metrics
        """
        if max_queries:
            queries = queries[:max_queries]
        
        print(f"\n{'='*70}")
        print(f"🚀 Starting Batch Evaluation")
        print(f"{'='*70}")
        print(f"Total Queries: {len(queries)}")
        print(f"Mode: {'Parallel' if parallel else 'Sequential'}")
        if parallel:
            print(f"Max Workers: {max_workers}")
        print(f"Model Config: {self.model_config or 'default'}")
        print(f"{'='*70}\n")
        
        self.results = []
        start_time = time.time()
        
        if parallel:
            return self._run_parallel(queries, max_workers, save_individual_results, start_time)
        else:
            return self._run_sequential(queries, delay_between_queries, save_individual_results, start_time)
    
    def _run_sequential(
        self,
        queries: List[Dict],
        delay_between_queries: float,
        save_individual_results: bool,
        start_time: float
    ) -> Dict:
        """Run evaluation sequentially (original implementation)"""
        for i, query_data in enumerate(queries, 1):
            query_id = query_data.get("id", f"query_{i}")
            query_text = query_data.get("query", "")
            category = query_data.get("category", "unknown")
            complexity = query_data.get("complexity", "unknown")
            
            print(f"[{i}/{len(queries)}] Running: {query_id} ({category}, {complexity})")
            print(f"   Query: {query_text[:80]}...")
            
            try:
                # Initialize agent
                agent_instance, _ = self.agent_service.initialize_agent()
                
                # Run workflow
                query_start = time.time()
                result = agent_instance.run_workflow(query_text)
                query_time = time.time() - query_start
                
                # Add metadata
                result["query_id"] = query_id
                result["query"] = query_text
                result["query_category"] = category
                result["query_complexity"] = complexity
                result["query_time_seconds"] = round(query_time, 2)
                result["success"] = bool(result.get("final_summary"))
                
                self.results.append(result)
                
                # Save individual result if requested
                if save_individual_results:
                    results_dir = self.project_root / "server" / "evaluation" / "results"
                    results_dir.mkdir(exist_ok=True)
                    result_file = results_dir / f"{query_id}_result.json"
                    with open(result_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                
                print(f"   ✅ Completed in {query_time:.2f}s")
                print(f"   Confidence: {result.get('analysis', {}).get('confidence', 0):.2f}")
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                error_result = {
                    "query_id": query_id,
                    "query": query_text,
                    "query_category": category,
                    "query_complexity": complexity,
                    "error": str(e),
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                }
                self.results.append(error_result)
                print()
            
            # Delay between queries to avoid rate limits
            if i < len(queries) and delay_between_queries > 0:
                time.sleep(delay_between_queries)
        
        total_time = time.time() - start_time
        return self._finalize_evaluation(queries, total_time)
    
    def _run_parallel(
        self,
        queries: List[Dict],
        max_workers: int,
        save_individual_results: bool,
        start_time: float
    ) -> Dict:
        """Run evaluation in parallel using ThreadPoolExecutor"""
        # Rate limiting semaphore (max concurrent API calls)
        rate_limiter = threading.Semaphore(max_workers)
        results_lock = threading.Lock()
        
        def evaluate_single_query(query_data: Dict, index: int) -> Dict:
            """Worker function to evaluate a single query"""
            query_id = query_data.get("id", f"query_{index}")
            query_text = query_data.get("query", "")
            category = query_data.get("category", "unknown")
            complexity = query_data.get("complexity", "unknown")
            
            # Acquire rate limiter
            rate_limiter.acquire()
            try:
                print(f"[{index}/{len(queries)}] Running: {query_id} ({category}, {complexity})")
                print(f"   Query: {query_text[:80]}...")
                
                # Create fresh agent instance for this worker (no shared state)
                # Load data once (shared read-only)
                data_file = config.DATA_FILE
                if not Path(data_file).is_absolute():
                    data_file = self.project_root / data_file
                data_path = Path(data_file)
                
                if data_path.exists():
                    with open(data_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    # Generate data if needed (shouldn't happen in parallel mode)
                    from data_generator import MockXDataGenerator
                    generator = MockXDataGenerator(seed=42)
                    data = generator.generate_dataset(
                        num_posts=config.MOCK_DATA_SIZE,
                        include_threads=True
                    )
                
                # Create agent with this data
                agent_instance = AgenticResearchAgent(data)
                
                # Apply model config if needed
                if self.model_config:
                    for key, value in self.model_config.items():
                        if hasattr(config.ModelConfig, key):
                            setattr(config.ModelConfig, key, value)
                
                # Run workflow
                query_start = time.time()
                result = agent_instance.run_workflow(query_text)
                query_time = time.time() - query_start
                
                # Add metadata
                result["query_id"] = query_id
                result["query"] = query_text
                result["query_category"] = category
                result["query_complexity"] = complexity
                result["query_time_seconds"] = round(query_time, 2)
                result["success"] = bool(result.get("final_summary"))
                
                # Save individual result if requested
                if save_individual_results:
                    results_dir = self.project_root / "server" / "evaluation" / "results"
                    results_dir.mkdir(exist_ok=True)
                    result_file = results_dir / f"{query_id}_result.json"
                    with open(result_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                
                print(f"   ✅ Completed in {query_time:.2f}s")
                print(f"   Confidence: {result.get('analysis', {}).get('confidence', 0):.2f}")
                
                return result
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                error_result = {
                    "query_id": query_id,
                    "query": query_text,
                    "query_category": category,
                    "query_complexity": complexity,
                    "error": str(e),
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                }
                return error_result
            finally:
                rate_limiter.release()
        
        # Execute queries in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_query = {
                executor.submit(evaluate_single_query, query_data, i+1): query_data
                for i, query_data in enumerate(queries)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_query):
                result = future.result()
                with results_lock:
                    self.results.append(result)
        
        total_time = time.time() - start_time
        return self._finalize_evaluation(queries, total_time)
    
    def _finalize_evaluation(self, queries: List[Dict], total_time: float) -> Dict:
        """Calculate metrics and return final evaluation results"""
        # Calculate metrics
        query_metadata = {
            q.get("id"): {
                "category": q.get("category", "unknown"),
                "complexity": q.get("complexity", "unknown")
            }
            for q in queries
        }
        
        metrics = MetricsCalculator.calculate_all_metrics(self.results, query_metadata)
        metrics["evaluation_metadata"] = {
            "total_time_seconds": round(total_time, 2),
            "avg_time_per_query": round(total_time / len(queries), 2),
            "model_config": self.model_config or "default",
            "queries_run": len(queries),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "results": self.results,
            "metrics": metrics
        }
    
    def save_evaluation(self, evaluation_data: Dict, output_file: str = None):
        """
        Save evaluation results to file
        
        Args:
            evaluation_data: Dict with results and metrics
            output_file: Output file path (default: evaluation/results/evaluation_TIMESTAMP.json)
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_suffix = ""
            if self.model_config:
                model_name = self.model_config.get("PLANNER_MODEL", "custom")
                model_suffix = f"_{model_name.replace('-', '_')}"
            output_file = self.project_root / "server" / "evaluation" / "results" / f"evaluation{model_suffix}_{timestamp}.json"
        else:
            output_file = Path(output_file)
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Evaluation saved to: {output_file}")
        return output_file


def main():
    """CLI entry point for batch evaluation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch evaluation runner for agentic research workflow")
    parser.add_argument(
        "--queries",
        type=str,
        default=None,
        help="Path to test queries JSON file (default: server/evaluation/test_queries.json)"
    )
    parser.add_argument(
        "--max-queries",
        type=int,
        default=None,
        help="Maximum number of queries to run (default: all)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between queries in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: auto-generated)"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Use parallel execution (faster but may hit rate limits)"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=3,
        help="Maximum concurrent workers for parallel mode (default: 3)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name to use (e.g., 'grok-4-fast-reasoning'). Overrides all model configs."
    )
    parser.add_argument(
        "--no-individual",
        action="store_true",
        help="Don't save individual result files"
    )
    
    args = parser.parse_args()
    
    # Get project root (evaluation -> server -> project_root)
    project_root = Path(__file__).parent.parent.parent.resolve()
    
    # Setup model config if specified
    model_config = None
    if args.model:
        model_config = {
            "PLANNER_MODEL": args.model,
            "ANALYZER_MODEL": args.model,
            "REFINER_MODEL": args.model,
            "SUMMARIZER_MODEL": args.model
        }
    
    # Run evaluation
    evaluator = BatchEvaluator(project_root, model_config=model_config)
    
    try:
        queries = evaluator.load_test_queries(args.queries)
        evaluation_data = evaluator.run_evaluation(
            queries,
            max_queries=args.max_queries,
            delay_between_queries=args.delay,
            save_individual_results=not args.no_individual,
            parallel=args.parallel,
            max_workers=args.max_workers
        )
        
        # Print metrics summary
        MetricsCalculator.print_summary(evaluation_data["metrics"])
        
        # Save evaluation
        output_file = evaluator.save_evaluation(evaluation_data, args.output)
        
        print(f"\n✅ Evaluation complete!")
        print(f"   Results: {len(evaluation_data['results'])} queries")
        print(f"   Completion Rate: {evaluation_data['metrics']['completion_rate']['completion_rate']:.1%}")
        print(f"   Output: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
