"""
Main Agentic Research Agent
Implements the full workflow: plan → execute → analyze → refine → summarize
"""
import json
from typing import Dict, List, Optional
from datetime import datetime
import config
from grok_client import GrokClient
from context_manager import ContextManager, ExecutionStep
from retrieval import HybridRetriever

class AgenticResearchAgent:
    """Main agentic research agent using Grok"""
    
    def __init__(self, data: List[Dict], api_key: Optional[str] = None):
        """
        Initialize agent
        
        Args:
            data: Dataset to search (list of posts/documents)
            api_key: Optional Grok API key
        """
        self.grok = GrokClient(api_key)
        self.context = ContextManager()
        self.retriever = HybridRetriever(data)
        self.data = data
        self.iteration_count = 0
    
    def plan(self, query: str) -> Dict:
        """
        Step 1: Plan - Decompose query into actionable steps
        
        Uses grok-4-fast-reasoning for complex reasoning
        """
        system_prompt = """You are an expert research planner. Break down complex queries into 
        clear, sequential steps. Think step-by-step about what information is needed and how to obtain it.
        
        Return your plan as JSON with this structure:
        {
            "query_type": "trend_analysis|info_extraction|comparison|sentiment|temporal|other",
            "steps": [
                {"step_number": 1, "action": "search", "description": "...", "tools": ["semantic_search", "keyword_search"]},
                {"step_number": 2, "action": "filter", "description": "...", "filters": {...}},
                {"step_number": 3, "action": "analyze", "description": "..."}
            ],
            "success_criteria": ["criterion1", "criterion2"],
            "expected_complexity": "low|medium|high"
        }"""
        
        user_prompt = f"""Analyze this research query and create a detailed plan:

Query: "{query}"

Consider:
- What type of query is this?
- What information needs to be retrieved?
- What analysis is required?
- What filters or constraints apply?
- How will we know if we've succeeded?

Create a comprehensive plan."""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self.grok.call(
            model=config.ModelConfig.PLANNER_MODEL,
            messages=messages,
            system_prompt=system_prompt,
            response_format={"type": "json_object"}
        )
        
        if not response.get("success", False):
            # Fallback plan if API fails
            plan = {
                "query_type": "other",
                "steps": [
                    {"step_number": 1, "action": "search", "description": "Search for relevant posts", "tools": ["hybrid_search"]},
                    {"step_number": 2, "action": "analyze", "description": "Analyze retrieved results"}
                ],
                "success_criteria": ["Relevant results found", "Analysis completed"],
                "expected_complexity": "medium"
            }
            plan_content = json.dumps(plan)
        else:
            plan_content = response["content"]
            plan = self.grok.parse_json_response(plan_content)
            
            # Validate plan structure
            if not isinstance(plan, dict) or "steps" not in plan:
                # Fallback to basic plan
                plan = {
                    "query_type": plan.get("query_type", "other"),
                    "steps": [
                        {"step_number": 1, "action": "search", "description": "Search for relevant posts", "tools": ["hybrid_search"]},
                        {"step_number": 2, "action": "analyze", "description": "Analyze retrieved results"}
                    ],
                    "success_criteria": ["Relevant results found"],
                    "expected_complexity": "medium"
                }
        
        # Store plan
        step = ExecutionStep(
            step_name="Planning",
            step_type="plan",
            input_data={"query": query},
            output_data=plan,
            reasoning=plan_content,
            timestamp=datetime.now().isoformat(),
            model_used=config.ModelConfig.PLANNER_MODEL,
            tokens_used=response.get("total_tokens", 0)
        )
        self.context.add_step(step)
        self.context.store_intermediate_result("plan", plan)
        
        return plan
    
    def execute(self, plan: Dict, query: str) -> List[Dict]:
        """
        Step 2: Execute - Retrieve data using hybrid search
        
        Uses retrieval tools based on plan
        """
        steps = plan.get("steps", [])
        all_results = []
        
        for step in steps:
            action = step.get("action", "").lower()
            
            if action == "search":
                # Perform hybrid search
                search_query = query  # Could be refined based on step description
                tools = step.get("tools", ["hybrid_search"])
                
                if "hybrid_search" in tools or "semantic_search" in tools:
                    results = self.retriever.hybrid_search(search_query)
                elif "keyword_search" in tools:
                    results = self.retriever.keyword_search(search_query)
                    results = [post for post, _ in results]
                else:
                    results = self.retriever.hybrid_search(search_query)
                
                all_results.extend(results)
            
            elif action == "filter":
                # Apply filters
                filters = step.get("filters", {})
                if filters:
                    all_results = self.retriever.filter_by_metadata(all_results, filters)
        
        # Remove duplicates
        seen_ids = set()
        unique_results = []
        for result in all_results:
            if result["id"] not in seen_ids:
                seen_ids.add(result["id"])
                unique_results.append(result)
        
        # Limit results
        max_results = 20
        unique_results = unique_results[:max_results]
        
        step = ExecutionStep(
            step_name="Execution",
            step_type="execute",
            input_data={"plan": plan},
            output_data={"results_count": len(unique_results), "sample_results": unique_results[:3]},
            reasoning=f"Retrieved {len(unique_results)} relevant items",
            timestamp=datetime.now().isoformat(),
            model_used="retrieval_system",
            tokens_used=0
        )
        self.context.add_step(step)
        self.context.store_intermediate_result("execution_results", unique_results)
        
        return unique_results
    
    def analyze(self, query: str, results: List[Dict], plan: Dict) -> Dict:
        """
        Step 3: Analyze - Deep analysis of retrieved data
        
        Uses grok-4-fast-reasoning for complex reasoning
        """
        system_prompt = """You are a research analyst. Analyze the provided data deeply.
        Identify patterns, themes, insights, and anomalies. Think critically and provide detailed analysis.
        
        Return analysis as JSON:
        {
            "main_themes": ["theme1", "theme2"],
            "key_insights": ["insight1", "insight2"],
            "sentiment_analysis": {"positive": count, "negative": count, "neutral": count},
            "engagement_patterns": {...},
            "notable_findings": ["finding1", "finding2"],
            "data_quality": "high|medium|low",
            "confidence": 0.0-1.0,
            "gaps_or_limitations": ["gap1", "gap2"]
        }"""
        
        # Prepare data summary
        data_summary = f"Query: {query}\n\n"
        data_summary += f"Retrieved {len(results)} items:\n\n"
        
        for i, item in enumerate(results[:10], 1):  # Show first 10
            data_summary += f"{i}. {item.get('text', '')[:200]}\n"
            data_summary += f"   Author: {item.get('author', {}).get('display_name', 'Unknown')}\n"
            data_summary += f"   Engagement: {sum(item.get('engagement', {}).values())} total\n"
            data_summary += f"   Sentiment: {item.get('sentiment', 'unknown')}\n\n"
        
        user_prompt = f"""{data_summary}

Analyze this data according to the plan:
{json.dumps(plan.get('steps', []), indent=2)}

Provide comprehensive analysis."""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self.grok.call(
            model=config.ModelConfig.ANALYZER_MODEL,
            messages=messages,
            system_prompt=system_prompt,
            response_format={"type": "json_object"}
        )
        
        if not response.get("success", False):
            # Fallback analysis if API fails
            analysis = {
                "main_themes": ["Unable to analyze - API error"],
                "key_insights": [f"Retrieved {len(results)} items"],
                "sentiment_analysis": {"positive": 0, "negative": 0, "neutral": 0},
                "confidence": 0.3,
                "data_quality": "unknown",
                "gaps_or_limitations": ["API error prevented full analysis"]
            }
            analysis_content = json.dumps(analysis)
        else:
            analysis_content = response["content"]
            analysis = self.grok.parse_json_response(analysis_content)
            
            # Ensure required fields exist
            if "confidence" not in analysis:
                analysis["confidence"] = 0.5
            if "main_themes" not in analysis:
                analysis["main_themes"] = []
        
        step = ExecutionStep(
            step_name="Analysis",
            step_type="analyze",
            input_data={"results_count": len(results)},
            output_data=analysis,
            reasoning=analysis_content,
            timestamp=datetime.now().isoformat(),
            model_used=config.ModelConfig.ANALYZER_MODEL,
            tokens_used=response.get("total_tokens", 0)
        )
        self.context.add_step(step)
        self.context.store_intermediate_result("analysis", analysis)
        
        return analysis
    
    def refine(self, query: str, analysis: Dict, plan: Dict) -> Dict:
        """
        Step 4: Refine - Determine if refinement is needed
        
        Uses grok-4-fast-reasoning for decision making
        """
        confidence = analysis.get("confidence", 0.5)
        
        # If confidence is high, skip refinement
        if confidence > 0.8:
            refinement = {
                "refinement_needed": False,
                "reason": "High confidence achieved",
                "next_steps": []
            }
            
            step = ExecutionStep(
                step_name="Refinement Check",
                step_type="refine",
                input_data={"confidence": confidence},
                output_data=refinement,
                reasoning="High confidence - no refinement needed",
                timestamp=datetime.now().isoformat(),
                model_used="decision_logic",
                tokens_used=0
            )
            self.context.add_step(step)
            return refinement
        
        system_prompt = """You are a research refinement specialist. Evaluate if the current 
        analysis is sufficient or if additional steps are needed.
        
        Return JSON:
        {
            "refinement_needed": true|false,
            "reason": "explanation",
            "next_steps": [
                {"action": "...", "description": "..."}
            ],
            "confidence_improvement_expected": 0.0-1.0
        }"""
        
        user_prompt = f"""Original Query: {query}

Current Analysis:
{json.dumps(analysis, indent=2)}

Plan:
{json.dumps(plan, indent=2)}

Evaluate if refinement is needed. Consider:
- Are there gaps in the data?
- Is the analysis complete?
- Would additional searches help?
- Is the confidence sufficient?"""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self.grok.call(
            model=config.ModelConfig.REFINER_MODEL,
            messages=messages,
            system_prompt=system_prompt,
            response_format={"type": "json_object"}
        )
        
        refinement_content = response["content"]
        refinement = self.grok.parse_json_response(refinement_content)
        
        step = ExecutionStep(
            step_name="Refinement",
            step_type="refine",
            input_data={"analysis": analysis},
            output_data=refinement,
            reasoning=refinement_content,
            timestamp=datetime.now().isoformat(),
            model_used=config.ModelConfig.REFINER_MODEL,
            tokens_used=response.get("total_tokens", 0)
        )
        self.context.add_step(step)
        
        return refinement
    
    def summarize(self, query: str, analysis: Dict, plan: Dict) -> str:
        """
        Step 5: Summarize - Generate final comprehensive summary
        
        Uses grok-4-fast-reasoning for high-quality summaries
        """
        system_prompt = """You are a research summarization expert. Create clear, actionable, 
        and comprehensive summaries of research findings.
        
        Structure your summary with:
        1. Executive Summary (2-3 sentences)
        2. Key Findings (bullet points)
        3. Detailed Analysis
        4. Limitations and Confidence
        5. Recommendations or Next Steps"""
        
        user_prompt = f"""Research Query: {query}

Plan Executed:
{json.dumps(plan, indent=2)}

Analysis Results:
{json.dumps(analysis, indent=2)}

Create a comprehensive final summary that answers the original query."""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self.grok.call(
            model=config.ModelConfig.SUMMARIZER_MODEL,
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=2000
        )
        
        summary = response["content"]
        
        step = ExecutionStep(
            step_name="Summarization",
            step_type="summarize",
            input_data={"analysis": analysis},
            output_data={"summary": summary},
            reasoning=summary,
            timestamp=datetime.now().isoformat(),
            model_used=config.ModelConfig.SUMMARIZER_MODEL,
            tokens_used=response.get("total_tokens", 0)
        )
        self.context.add_step(step)
        
        return summary
    
    def run_workflow(self, query: str, max_iterations: int = None) -> Dict:
        """
        Main workflow orchestrator
        
        Implements: Plan → Execute → Analyze → Refine → Summarize loop
        """
        if max_iterations is None:
            max_iterations = config.MAX_ITERATIONS
        
        self.iteration_count = 0
        print(f"\n{'='*70}")
        print(f"🚀 Starting Agentic Research Workflow")
        print(f"{'='*70}")
        print(f"Query: {query}\n")
        
        # Step 1: Plan
        print("📋 [1/5] Planning...")
        plan = self.plan(query)
        print(f"   Query Type: {plan.get('query_type', 'unknown')}")
        print(f"   Steps Planned: {len(plan.get('steps', []))}")
        print(f"   Complexity: {plan.get('expected_complexity', 'unknown')}\n")
        
        # Step 2: Execute
        print("⚙️  [2/5] Executing retrieval...")
        results = self.execute(plan, query)
        print(f"   Retrieved: {len(results)} items\n")
        
        # Step 3: Analyze
        print("🔍 [3/5] Analyzing results...")
        analysis = self.analyze(query, results, plan)
        confidence = analysis.get("confidence", 0.5)
        print(f"   Confidence: {confidence:.2f}")
        print(f"   Main Themes: {', '.join(analysis.get('main_themes', [])[:3])}\n")
        
        # Step 4: Refine (iterative loop)
        refinement_needed = True
        iteration = 0
        
        while refinement_needed and iteration < max_iterations:
            iteration += 1
            self.iteration_count = iteration
            
            print(f"🔄 [4/5] Refinement Check (Iteration {iteration})...")
            refinement = self.refine(query, analysis, plan)
            refinement_needed = refinement.get("refinement_needed", False)
            
            if refinement_needed:
                print(f"   Refinement needed: {refinement.get('reason', '')}")
                print(f"   Next steps: {len(refinement.get('next_steps', []))}")
                
                # Execute refinement steps
                refinement_plan = {
                    "steps": refinement.get("next_steps", []),
                    "query_type": plan.get("query_type")
                }
                additional_results = self.execute(refinement_plan, query)
                results.extend(additional_results)
                
                # Re-analyze with new data
                analysis = self.analyze(query, results, plan)
                confidence = analysis.get("confidence", 0.5)
                print(f"   Updated Confidence: {confidence:.2f}\n")
            else:
                print(f"   No refinement needed: {refinement.get('reason', '')}\n")
        
        # Step 5: Summarize
        print("📝 [5/5] Generating final summary...")
        summary = self.summarize(query, analysis, plan)
        print("   ✅ Summary complete\n")
        
        # Compile results
        total_tokens = sum(step.tokens_used or 0 for step in self.context.execution_steps)
        
        result = {
            "query": query,
            "plan": plan,
            "results_count": len(results),
            "analysis": analysis,
            "refinement_iterations": self.iteration_count,
            "final_summary": summary,
            "execution_steps": len(self.context.execution_steps),
            "total_tokens_used": total_tokens,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"{'='*70}")
        print("✅ Workflow Complete!")
        print(f"{'='*70}")
        print(f"Total Steps: {len(self.context.execution_steps)}")
        print(f"Refinement Iterations: {self.iteration_count}")
        print(f"Total Tokens Used: {total_tokens}")
        print(f"Final Confidence: {confidence:.2f}")
        print(f"{'='*70}\n")
        
        return result
