"""
Model Comparison Script
Compares performance across different Grok model variants
"""
import json
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Add server directory to path
server_dir = Path(__file__).parent.parent
sys.path.insert(0, str(server_dir))

from evaluation.evaluator import BatchEvaluator
from evaluation.metrics import MetricsCalculator
import config


# Define model configurations to compare
# Selected models most applicable for agent analysis:
# 1. grok-4-fast-reasoning: Fast reasoning, 2M context, cost-effective ($0.20/$0.50)
# 2. grok-4-0709: Higher quality reasoning, 256K context, premium ($3.00/$15.00)
# 3. grok-3-mini: Smaller/cheaper option, 131K context, budget-friendly ($0.30/$0.50)
MODEL_CONFIGS = {
    "grok-4-fast-reasoning": {
        "PLANNER_MODEL": "grok-4-fast-reasoning",
        "ANALYZER_MODEL": "grok-4-fast-reasoning",
        "REFINER_MODEL": "grok-4-fast-reasoning",
        "SUMMARIZER_MODEL": "grok-4-fast-reasoning"
    },
    "grok-4-0709": {
        "PLANNER_MODEL": "grok-4-0709",
        "ANALYZER_MODEL": "grok-4-0709",
        "REFINER_MODEL": "grok-4-0709",
        "SUMMARIZER_MODEL": "grok-4-0709"
    },
    "grok-3-mini": {
        "PLANNER_MODEL": "grok-3-mini",
        "ANALYZER_MODEL": "grok-3-mini",
        "REFINER_MODEL": "grok-3-mini",
        "SUMMARIZER_MODEL": "grok-3-mini"
    }
}


def compare_models(
    project_root: Path,
    queries: List[Dict],
    model_configs: Dict[str, Dict] = None,
    max_queries: int = None,
    delay_between_queries: float = 1.0
) -> Dict:
    """
    Compare multiple model configurations
    
    Args:
        project_root: Project root directory
        queries: List of test queries
        model_configs: Dict of model_name -> model_config (default: MODEL_CONFIGS)
        max_queries: Maximum queries per model (for faster comparison)
        delay_between_queries: Delay between queries
        
    Returns:
        Dict with comparison results
    """
    if model_configs is None:
        model_configs = MODEL_CONFIGS
    
    print(f"\n{'='*70}")
    print(f"🔬 MODEL COMPARISON")
    print(f"{'='*70}")
    print(f"Models to compare: {', '.join(model_configs.keys())}")
    print(f"Queries per model: {max_queries or len(queries)}")
    print(f"{'='*70}\n")
    
    comparison_results = {}
    
    for model_name, model_config in model_configs.items():
        print(f"\n{'─'*70}")
        print(f"Testing Model: {model_name}")
        print(f"{'─'*70}\n")
        
        try:
            evaluator = BatchEvaluator(project_root, model_config=model_config)
            evaluation_data = evaluator.run_evaluation(
                queries,
                max_queries=max_queries,
                delay_between_queries=delay_between_queries,
                save_individual_results=False  # Don't save individual files for comparison
            )
            
            comparison_results[model_name] = {
                "model_config": model_config,
                "metrics": evaluation_data["metrics"],
                "results_count": len(evaluation_data["results"])
            }
            
            # Print quick summary
            metrics = evaluation_data["metrics"]
            print(f"\n📊 {model_name} Summary:")
            print(f"   Completion Rate: {metrics['completion_rate']['completion_rate']:.1%}")
            print(f"   Avg Confidence: {metrics['summary_quality']['avg_confidence']:.3f}")
            print(f"   Avg Steps: {metrics['step_efficiency']['avg_execution_steps']:.1f}")
            print(f"   Avg Tokens: {metrics['step_efficiency']['avg_tokens_per_query']:.0f}")
            
        except Exception as e:
            print(f"❌ Error testing {model_name}: {e}")
            comparison_results[model_name] = {
                "error": str(e),
                "metrics": None
            }
    
    # Generate comparison summary
    comparison_summary = generate_comparison_summary(comparison_results)
    
    return {
        "comparison_results": comparison_results,
        "comparison_summary": comparison_summary,
        "timestamp": datetime.now().isoformat()
    }


def generate_comparison_summary(comparison_results: Dict) -> Dict:
    """
    Generate comparison summary across models
    
    Args:
        comparison_results: Dict of model_name -> results
        
    Returns:
        Comparison summary dict
    """
    summary = {
        "models_tested": list(comparison_results.keys()),
        "best_completion_rate": None,
        "best_confidence": None,
        "most_efficient": None,
        "most_autonomous": None
    }
    
    best_completion = {"model": None, "rate": 0.0}
    best_confidence = {"model": None, "confidence": 0.0}
    most_efficient = {"model": None, "steps": float('inf')}
    most_autonomous = {"model": None, "score": 0.0}
    
    for model_name, results in comparison_results.items():
        if "error" in results or not results.get("metrics"):
            continue
        
        metrics = results["metrics"]
        
        # Completion rate
        cr = metrics.get("completion_rate", {}).get("completion_rate", 0)
        if cr > best_completion["rate"]:
            best_completion = {"model": model_name, "rate": cr}
        
        # Confidence
        conf = metrics.get("summary_quality", {}).get("avg_confidence", 0)
        if conf > best_confidence["confidence"]:
            best_confidence = {"model": model_name, "confidence": conf}
        
        # Efficiency (fewer steps is better)
        steps = metrics.get("step_efficiency", {}).get("avg_execution_steps", float('inf'))
        if steps < most_efficient["steps"]:
            most_efficient = {"model": model_name, "steps": steps}
        
        # Autonomy
        autonomy = metrics.get("autonomy_metrics", {}).get("avg_autonomy_score", 0)
        if autonomy > most_autonomous["score"]:
            most_autonomous = {"model": model_name, "score": autonomy}
    
    summary["best_completion_rate"] = best_completion
    summary["best_confidence"] = best_confidence
    summary["most_efficient"] = most_efficient
    summary["most_autonomous"] = most_autonomous
    
    return summary


def print_comparison_table(comparison_results: Dict):
    """Print a comparison table"""
    print(f"\n{'='*70}")
    print("📊 MODEL COMPARISON TABLE")
    print(f"{'='*70}\n")
    
    # Header
    print(f"{'Model':<25} {'Completion':<12} {'Confidence':<12} {'Avg Steps':<12} {'Avg Tokens':<12} {'Autonomy':<12}")
    print("-" * 85)
    
    # Rows
    for model_name, results in comparison_results.items():
        if "error" in results or not results.get("metrics"):
            print(f"{model_name:<25} {'ERROR':<12}")
            continue
        
        metrics = results["metrics"]
        cr = metrics.get("completion_rate", {}).get("completion_rate", 0)
        conf = metrics.get("summary_quality", {}).get("avg_confidence", 0)
        steps = metrics.get("step_efficiency", {}).get("avg_execution_steps", 0)
        tokens = metrics.get("step_efficiency", {}).get("avg_tokens_per_query", 0)
        autonomy = metrics.get("autonomy_metrics", {}).get("avg_autonomy_score", 0)
        
        print(f"{model_name:<25} {cr:>10.1%}  {conf:>10.3f}  {steps:>10.1f}  {tokens:>10.0f}  {autonomy:>10.3f}")
    
    print()


def main():
    """CLI entry point for model comparison"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare different Grok models")
    parser.add_argument(
        "--queries",
        type=str,
        default=None,
        help="Path to test queries JSON file"
    )
    parser.add_argument(
        "--max-queries",
        type=int,
        default=None,
        help="Maximum queries per model (for faster comparison)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between queries in seconds"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path"
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=None,
        help="Specific models to compare (default: all in MODEL_CONFIGS)"
    )
    
    args = parser.parse_args()
    
    # Get project root (evaluation -> server -> project_root)
    project_root = Path(__file__).parent.parent.parent.resolve()
    
    # Filter models if specified
    model_configs = MODEL_CONFIGS
    if args.models:
        model_configs = {name: MODEL_CONFIGS[name] for name in args.models if name in MODEL_CONFIGS}
        if not model_configs:
            print(f"❌ No valid models found. Available: {list(MODEL_CONFIGS.keys())}")
            sys.exit(1)
    
    # Load queries
    evaluator = BatchEvaluator(project_root)
    try:
        queries = evaluator.load_test_queries(args.queries)
    except Exception as e:
        print(f"❌ Failed to load queries: {e}")
        sys.exit(1)
    
    # Run comparison
    try:
        comparison = compare_models(
            project_root,
            queries,
            model_configs=model_configs,
            max_queries=args.max_queries,
            delay_between_queries=args.delay
        )
        
        # Print comparison table
        print_comparison_table(comparison["comparison_results"])
        
        # Print summary
        summary = comparison["comparison_summary"]
        print(f"\n🏆 BEST PERFORMERS:")
        print(f"   Completion Rate: {summary['best_completion_rate']['model']} ({summary['best_completion_rate']['rate']:.1%})")
        print(f"   Confidence: {summary['best_confidence']['model']} ({summary['best_confidence']['confidence']:.3f})")
        print(f"   Efficiency: {summary['most_efficient']['model']} ({summary['most_efficient']['steps']:.1f} steps)")
        print(f"   Autonomy: {summary['most_autonomous']['model']} ({summary['most_autonomous']['score']:.3f})")
        
        # Save comparison
        if args.output:
            output_file = Path(args.output)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = project_root / "server" / "evaluation" / "results" / f"model_comparison_{timestamp}.json"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Comparison saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Comparison failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
