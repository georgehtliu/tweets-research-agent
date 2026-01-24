"""
Metrics Calculation for Agent Evaluation
Calculates completion rate, step efficiency, summary quality, and other metrics
"""
from typing import Dict, List, Optional
from datetime import datetime
import json


class MetricsCalculator:
    """Calculate evaluation metrics from agent results"""
    
    @staticmethod
    def calculate_completion_rate(results: List[Dict]) -> Dict:
        """
        Calculate completion rate: % of queries successfully completed
        
        Args:
            results: List of result dictionaries from agent runs
            
        Returns:
            Dict with completion_rate, total, completed, failed
        """
        total = len(results)
        completed = sum(1 for r in results if r.get("final_summary") and not r.get("error"))
        failed = total - completed
        
        return {
            "completion_rate": completed / total if total > 0 else 0.0,
            "total_queries": total,
            "completed": completed,
            "failed": failed
        }
    
    @staticmethod
    def calculate_step_efficiency(results: List[Dict]) -> Dict:
        """
        Calculate step efficiency metrics
        
        Args:
            results: List of result dictionaries
            
        Returns:
            Dict with avg_steps, avg_refinement_iterations, avg_replan_count, etc.
        """
        if not results:
            return {
                "avg_execution_steps": 0,
                "avg_refinement_iterations": 0,
                "avg_replan_count": 0,
                "avg_tokens_per_query": 0
            }
        
        completed_results = [r for r in results if r.get("final_summary")]
        
        if not completed_results:
            return {
                "avg_execution_steps": 0,
                "avg_refinement_iterations": 0,
                "avg_replan_count": 0,
                "avg_tokens_per_query": 0
            }
        
        avg_steps = sum(r.get("execution_steps", 0) for r in completed_results) / len(completed_results)
        avg_refinement = sum(r.get("refinement_iterations", 0) for r in completed_results) / len(completed_results)
        avg_replan = sum(r.get("replan_count", 0) for r in completed_results) / len(completed_results)
        avg_tokens = sum(r.get("total_tokens_used", 0) for r in completed_results) / len(completed_results)
        
        return {
            "avg_execution_steps": round(avg_steps, 2),
            "avg_refinement_iterations": round(avg_refinement, 2),
            "avg_replan_count": round(avg_replan, 2),
            "avg_tokens_per_query": round(avg_tokens, 0),
            "min_steps": min((r.get("execution_steps", 0) for r in completed_results), default=0),
            "max_steps": max((r.get("execution_steps", 0) for r in completed_results), default=0),
            "min_tokens": min((r.get("total_tokens_used", 0) for r in completed_results), default=0),
            "max_tokens": max((r.get("total_tokens_used", 0) for r in completed_results), default=0)
        }
    
    @staticmethod
    def calculate_summary_quality(results: List[Dict]) -> Dict:
        """
        Calculate summary quality metrics
        
        Args:
            results: List of result dictionaries
            
        Returns:
            Dict with avg_confidence, avg_summary_length, quality_distribution
        """
        if not results:
            return {
                "avg_confidence": 0.0,
                "avg_summary_length": 0,
                "high_confidence_rate": 0.0,
                "quality_distribution": {}
            }
        
        completed_results = [r for r in results if r.get("final_summary") and r.get("analysis")]
        
        if not completed_results:
            return {
                "avg_confidence": 0.0,
                "avg_summary_length": 0,
                "high_confidence_rate": 0.0,
                "quality_distribution": {}
            }
        
        confidences = []
        summary_lengths = []
        
        for r in completed_results:
            analysis = r.get("analysis", {})
            confidence = analysis.get("confidence", 0.0)
            if isinstance(confidence, (int, float)):
                confidences.append(confidence)
            
            summary = r.get("final_summary", "")
            if summary:
                summary_lengths.append(len(summary))
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        avg_length = sum(summary_lengths) / len(summary_lengths) if summary_lengths else 0
        
        high_confidence = sum(1 for c in confidences if c >= 0.8)
        high_confidence_rate = high_confidence / len(confidences) if confidences else 0.0
        
        # Quality distribution
        quality_dist = {
            "high": sum(1 for c in confidences if c >= 0.8),
            "medium": sum(1 for c in confidences if 0.5 <= c < 0.8),
            "low": sum(1 for c in confidences if c < 0.5)
        }
        
        return {
            "avg_confidence": round(avg_confidence, 3),
            "avg_summary_length": round(avg_length, 0),
            "high_confidence_rate": round(high_confidence_rate, 3),
            "quality_distribution": quality_dist,
            "min_confidence": round(min(confidences), 3) if confidences else 0.0,
            "max_confidence": round(max(confidences), 3) if confidences else 0.0
        }
    
    @staticmethod
    def calculate_autonomy_metrics(results: List[Dict]) -> Dict:
        """
        Calculate autonomy metrics: how well the agent handles queries independently
        
        Args:
            results: List of result dictionaries
            
        Returns:
            Dict with replan_rate, refinement_rate, critique_pass_rate, etc.
        """
        if not results:
            return {
                "replan_rate": 0.0,
                "refinement_rate": 0.0,
                "critique_pass_rate": 0.0,
                "avg_autonomy_score": 0.0
            }
        
        completed_results = [r for r in results if r.get("final_summary")]
        
        if not completed_results:
            return {
                "replan_rate": 0.0,
                "refinement_rate": 0.0,
                "critique_pass_rate": 0.0,
                "avg_autonomy_score": 0.0
            }
        
        replan_count = sum(1 for r in completed_results if r.get("replan_count", 0) > 0)
        refinement_count = sum(1 for r in completed_results if r.get("refinement_iterations", 0) > 0)
        
        critique_passed = 0
        critique_total = 0
        for r in completed_results:
            critique = r.get("critique")
            if critique:
                critique_total += 1
                if critique.get("critique_passed", False):
                    critique_passed += 1
        
        replan_rate = replan_count / len(completed_results) if completed_results else 0.0
        refinement_rate = refinement_count / len(completed_results) if completed_results else 0.0
        critique_pass_rate = critique_passed / critique_total if critique_total > 0 else 1.0
        
        # Autonomy score: higher is better (fewer interventions needed)
        # Formula: 1.0 - (replan_rate * 0.3 + refinement_rate * 0.2 + (1 - critique_pass_rate) * 0.5)
        autonomy_score = 1.0 - (
            replan_rate * 0.3 + 
            refinement_rate * 0.2 + 
            (1 - critique_pass_rate) * 0.5
        )
        autonomy_score = max(0.0, min(1.0, autonomy_score))  # Clamp to [0, 1]
        
        return {
            "replan_rate": round(replan_rate, 3),
            "refinement_rate": round(refinement_rate, 3),
            "critique_pass_rate": round(critique_pass_rate, 3),
            "avg_autonomy_score": round(autonomy_score, 3),
            "queries_with_replan": replan_count,
            "queries_with_refinement": refinement_count,
            "queries_critiqued": critique_total
        }
    
    @staticmethod
    def calculate_category_metrics(results: List[Dict], query_metadata: Dict) -> Dict:
        """
        Calculate metrics broken down by query category and complexity
        
        Args:
            results: List of result dictionaries (should have query_id)
            query_metadata: Dict mapping query_id to category/complexity
            
        Returns:
            Dict with metrics per category and complexity level
        """
        category_metrics = {}
        complexity_metrics = {}
        
        # Group results by category and complexity
        for result in results:
            query_id = result.get("query_id")
            if not query_id or query_id not in query_metadata:
                continue
            
            metadata = query_metadata[query_id]
            category = metadata.get("category", "unknown")
            complexity = metadata.get("complexity", "unknown")
            
            if category not in category_metrics:
                category_metrics[category] = []
            category_metrics[category].append(result)
            
            if complexity not in complexity_metrics:
                complexity_metrics[complexity] = []
            complexity_metrics[complexity].append(result)
        
        # Calculate metrics per category
        category_stats = {}
        for category, cat_results in category_metrics.items():
            category_stats[category] = {
                "completion_rate": MetricsCalculator.calculate_completion_rate(cat_results),
                "step_efficiency": MetricsCalculator.calculate_step_efficiency(cat_results),
                "summary_quality": MetricsCalculator.calculate_summary_quality(cat_results),
                "count": len(cat_results)
            }
        
        # Calculate metrics per complexity
        complexity_stats = {}
        for complexity, comp_results in complexity_metrics.items():
            complexity_stats[complexity] = {
                "completion_rate": MetricsCalculator.calculate_completion_rate(comp_results),
                "step_efficiency": MetricsCalculator.calculate_step_efficiency(comp_results),
                "summary_quality": MetricsCalculator.calculate_summary_quality(comp_results),
                "count": len(comp_results)
            }
        
        return {
            "by_category": category_stats,
            "by_complexity": complexity_stats
        }
    
    @staticmethod
    def calculate_all_metrics(results: List[Dict], query_metadata: Optional[Dict] = None) -> Dict:
        """
        Calculate all metrics
        
        Args:
            results: List of result dictionaries
            query_metadata: Optional dict mapping query_id to metadata
            
        Returns:
            Comprehensive metrics dictionary
        """
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(results),
            "completion_rate": MetricsCalculator.calculate_completion_rate(results),
            "step_efficiency": MetricsCalculator.calculate_step_efficiency(results),
            "summary_quality": MetricsCalculator.calculate_summary_quality(results),
            "autonomy_metrics": MetricsCalculator.calculate_autonomy_metrics(results)
        }
        
        if query_metadata:
            metrics["category_breakdown"] = MetricsCalculator.calculate_category_metrics(
                results, query_metadata
            )
        
        return metrics
    
    @staticmethod
    def export_metrics(metrics: Dict, output_path: str):
        """Export metrics to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False, default=str)
    
    @staticmethod
    def print_summary(metrics: Dict):
        """Print a human-readable summary of metrics"""
        print("\n" + "="*70)
        print("📊 EVALUATION METRICS SUMMARY")
        print("="*70)
        
        # Completion Rate
        cr = metrics.get("completion_rate", {})
        print(f"\n✅ Completion Rate: {cr.get('completion_rate', 0):.1%}")
        print(f"   Completed: {cr.get('completed', 0)}/{cr.get('total_queries', 0)}")
        
        # Step Efficiency
        se = metrics.get("step_efficiency", {})
        print(f"\n⚙️  Step Efficiency:")
        print(f"   Avg Steps: {se.get('avg_execution_steps', 0)}")
        print(f"   Avg Refinement Iterations: {se.get('avg_refinement_iterations', 0)}")
        print(f"   Avg Replan Count: {se.get('avg_replan_count', 0)}")
        print(f"   Avg Tokens/Query: {se.get('avg_tokens_per_query', 0):.0f}")
        
        # Summary Quality
        sq = metrics.get("summary_quality", {})
        print(f"\n📝 Summary Quality:")
        print(f"   Avg Confidence: {sq.get('avg_confidence', 0):.3f}")
        print(f"   High Confidence Rate: {sq.get('high_confidence_rate', 0):.1%}")
        print(f"   Avg Summary Length: {sq.get('avg_summary_length', 0):.0f} chars")
        
        # Autonomy
        am = metrics.get("autonomy_metrics", {})
        print(f"\n🤖 Autonomy Metrics:")
        print(f"   Autonomy Score: {am.get('avg_autonomy_score', 0):.3f}")
        print(f"   Replan Rate: {am.get('replan_rate', 0):.1%}")
        print(f"   Refinement Rate: {am.get('refinement_rate', 0):.1%}")
        print(f"   Critique Pass Rate: {am.get('critique_pass_rate', 0):.1%}")
        
        # Category breakdown if available
        if "category_breakdown" in metrics:
            print(f"\n📂 Category Breakdown:")
            cb = metrics["category_breakdown"]
            for category, stats in cb.get("by_category", {}).items():
                cr_cat = stats.get("completion_rate", {}).get("completion_rate", 0)
                print(f"   {category}: {cr_cat:.1%} completion ({stats.get('count', 0)} queries)")
        
        print("\n" + "="*70 + "\n")
