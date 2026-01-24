"""
Main Agentic Research Agent
Implements state machine workflow: plan → execute → analyze → evaluate → refine → critique → summarize
Supports dynamic transitions including Analyzer → Replan
"""
import json
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import config
from grok_client import GrokClient
from context_manager import ContextManager, ExecutionStep
from retrieval import HybridRetriever
from tools import ToolRegistry

class WorkflowState(Enum):
    """States in the agent workflow state machine"""
    PLAN = "plan"
    EXECUTE = "execute"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"  # Evaluate if replan needed
    REFINE = "refine"
    CRITIQUE = "critique"
    SUMMARIZE = "summarize"
    COMPLETE = "complete"


class AgenticResearchAgent:
    """Main agentic research agent using Grok with state machine orchestration"""
    
    def __init__(self, data: List[Dict], api_key: Optional[str] = None, progress_callback=None):
        """
        Initialize agent
        
        Args:
            data: Dataset to search (list of posts/documents)
            api_key: Optional Grok API key
            progress_callback: Optional callback function(event_type, data) for progress updates
        """
        self.grok = GrokClient(api_key)
        self.context = ContextManager()
        self.retriever = HybridRetriever(data)
        self.tool_registry = ToolRegistry(self.retriever, data)
        self.data = data
        self.iteration_count = 0
        self.replan_count = 0
        self.progress_callback = progress_callback
        self.current_state = WorkflowState.PLAN
    
    def _emit_progress(self, event_type: str, data: Dict):
        """Emit progress event if callback is set"""
        if self.progress_callback:
            self.progress_callback(event_type, data)
    
    def plan(self, query: str) -> Dict:
        """
        Step 1: Plan - Decompose query into actionable steps
        
        Uses grok-4-fast-reasoning for complex reasoning
        """
        system_prompt = """You are an expert research planner. Break down queries into clear steps.
        
        Return JSON:
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
    
    def execute_with_tool_calling(self, query: str, max_tool_calls: int = 5) -> List[Dict]:
        """
        Execute using dynamic tool-calling loop where Grok chooses tools iteratively
        
        This is an alternative to plan-based execution where the LLM dynamically
        decides which tools to call based on intermediate results.
        
        NOTE: Full implementation requires GrokClient to support tools/function_calling.
        Currently falls back to hybrid_search. To enable:
        1. Add 'tools' parameter support to GrokClient.call()
        2. Parse tool_calls from API response
        3. Execute tools via tool_registry.call_tool()
        4. Add tool results back to conversation
        
        Args:
            query: Research query
            max_tool_calls: Maximum number of tool calls allowed
            
        Returns:
            List of retrieved posts
        """
        # TODO: Implement full tool-calling when GrokClient supports tools parameter
        # For now, use hybrid search as fallback
        # The tool_registry and tool definitions are ready for when API support is added
        results = self.retriever.hybrid_search(query)
        return results[:20]
    
    def execute(self, plan: Dict, query: str) -> List[Dict]:
        """
        Step 2: Execute - Retrieve data using hybrid search
        
        Uses retrieval tools based on plan. Search steps use step["description"]
        as the search query when present (plan or refinement); otherwise fall
        back to the original query.
        """
        steps = plan.get("steps", [])
        all_results = []
        
        for step in steps:
            action = (step.get("action") or "search").lower()
            tools = step.get("tools", ["hybrid_search"])
            if isinstance(tools, str):
                tools = [tools]
            
            if action == "search":
                search_query = step.get("description") or query
                if "hybrid_search" in tools or "semantic_search" in tools:
                    results = self.retriever.hybrid_search(search_query)
                elif "keyword_search" in tools:
                    results = self.retriever.keyword_search(search_query)
                    results = [post for post, _ in results]
                else:
                    results = self.retriever.hybrid_search(search_query)
                all_results.extend(results)
            
            elif action == "filter":
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
        max_results = config.MAX_RETRIEVAL_RESULTS
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
        system_prompt = """You are a research analyst. Analyze data and identify patterns, themes, insights.
        
        Return JSON:
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
        
        # Prepare data summary (optimized: fewer items, shorter text)
        data_summary = f"Query: {query}\n\n"
        data_summary += f"Retrieved {len(results)} items:\n\n"
        
        sample_size = min(config.ANALYZE_SAMPLE_SIZE, len(results))
        text_length = config.ANALYZE_TEXT_LENGTH
        for i, item in enumerate(results[:sample_size], 1):
            data_summary += f"{i}. {item.get('text', '')[:text_length]}\n"
            data_summary += f"   Author: {item.get('author', {}).get('display_name', 'Unknown')}\n"
            eng = item.get('engagement', {}) or {}
            eng_sum = sum(v for v in eng.values() if isinstance(v, (int, float))) if isinstance(eng, dict) else 0
            data_summary += f"   Engagement: {eng_sum} total\n"
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
        
        # If confidence is high, skip refinement (optimized threshold)
        if confidence > 0.75:  # Lowered from 0.8 to skip more often
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
                {"action": "search", "description": "exact search query to run for this step"}
            ],
            "confidence_improvement_expected": 0.0-1.0
        }
        
        For next_steps: use action "search" with a clear "description" that is the exact 
        search query to run (e.g. "negative sentiment posts about X", "high engagement 
        posts from verified users"). The description will be used as the search query."""
        
        user_prompt = f"""Query: {query}

Analysis: {json.dumps(analysis, indent=2)}
Plan: {json.dumps(plan, indent=2)}

Evaluate if refinement needed: gaps, completeness, need for more searches, confidence."""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self.grok.call(
            model=config.ModelConfig.REFINER_MODEL,
            messages=messages,
            system_prompt=system_prompt,
            response_format={"type": "json_object"}
        )
        
        if not response.get("success", False):
            refinement = {
                "refinement_needed": False,
                "reason": "API error - skipping refinement to avoid invalid state",
                "next_steps": []
            }
            step = ExecutionStep(
                step_name="Refinement",
                step_type="refine",
                input_data={"analysis": analysis},
                output_data=refinement,
                reasoning="Refinement API call failed; treating as no refinement needed",
                timestamp=datetime.now().isoformat(),
                model_used=config.ModelConfig.REFINER_MODEL,
                tokens_used=0
            )
            self.context.add_step(step)
            return refinement
        
        refinement_content = response["content"]
        refinement = self.grok.parse_json_response(refinement_content)
        
        # Validate structure
        if not isinstance(refinement, dict):
            refinement = {"refinement_needed": False, "reason": "Invalid refinement response", "next_steps": []}
        if "next_steps" not in refinement or not isinstance(refinement["next_steps"], list):
            refinement["next_steps"] = refinement.get("next_steps", []) or []
        if "refinement_needed" not in refinement:
            refinement["refinement_needed"] = bool(refinement["next_steps"])
        if "reason" not in refinement:
            refinement["reason"] = "Refinement check completed"
        
        # Normalize next_steps: ensure action + description for execute contract
        normalized = []
        for s in refinement["next_steps"]:
            if not isinstance(s, dict):
                continue
            action = (s.get("action") or "search").lower()
            desc = (s.get("description") or "").strip()
            if "search" in action:
                normalized.append({"action": "search", "description": desc or query, "tools": s.get("tools", ["hybrid_search"])})
            elif action == "filter" and s.get("filters"):
                normalized.append({"action": "filter", "filters": s["filters"]})
        refinement["next_steps"] = normalized
        if not normalized and refinement.get("refinement_needed"):
            refinement["refinement_needed"] = False
            refinement["reason"] = (refinement.get("reason") or "") + " (no executable steps after normalization)"

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
    
    def evaluate_for_replan(self, query: str, analysis: Dict, plan: Dict, results: List[Dict]) -> Dict:
        """
        Evaluate if the current plan/strategy needs to be completely revised
        
        Analyzer can request replanning if:
        - Data quality is poor (e.g., 90% sarcasm when looking for serious analysis)
        - Strategy is fundamentally wrong
        - Retrieved data doesn't match query intent
        
        Returns:
            Dict with "replan_needed" (bool), "reason", "suggested_strategy"
        """
        system_prompt = """You are a research strategy evaluator. Determine if the current 
        research plan needs to be completely revised (not just refined with more searches).
        
        Return JSON:
        {
            "replan_needed": true|false,
            "reason": "explanation",
            "suggested_strategy": "description of new approach if replan needed"
        }
        
        Replan if:
        - The retrieved data is fundamentally wrong (e.g., 90% sarcasm when query asks for serious analysis)
        - The search strategy is misaligned with query intent
        - Data quality issues require a completely different approach (not just more searches)
        
        Do NOT replan if:
        - Just need more data (use refinement instead)
        - Need to filter existing results (use refinement instead)
        - Confidence is low but strategy is sound (use refinement instead)"""
        
        # Analyze data quality signals
        sentiment_dist = analysis.get("sentiment_analysis", {}) or {}
        total_sentiment = sum(v for v in sentiment_dist.values() if isinstance(v, (int, float)))
        neg = sentiment_dist.get("negative", 0)
        neg = neg if isinstance(neg, (int, float)) else 0
        if total_sentiment > 0:
            sarcasm_ratio = neg / total_sentiment
        else:
            sarcasm_ratio = 0
        
        data_quality = analysis.get("data_quality", "medium")
        confidence = analysis.get("confidence", 0.5)
        gaps = analysis.get("gaps_or_limitations", [])
        
        user_prompt = f"""Original Query: {query}

Current Plan:
{json.dumps(plan, indent=2)}

Analysis Results:
{json.dumps(analysis, indent=2)}

Data Quality Signals:
- Sentiment distribution: {sentiment_dist}
- Data quality rating: {data_quality}
- Confidence: {confidence:.2f}
- Gaps/limitations: {gaps}
- Retrieved {len(results)} items

Evaluate if the PLAN/STRATEGY needs to be completely revised (replan) vs. just refined (more searches).
Consider: Is the fundamental approach wrong, or do we just need more/better data?"""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self.grok.call(
            model=config.ModelConfig.REFINER_MODEL,  # Reuse refiner model for evaluation
            messages=messages,
            system_prompt=system_prompt,
            response_format={"type": "json_object"}
        )
        
        if not response.get("success", False):
            evaluation = {
                "replan_needed": False,
                "reason": "API error - proceeding with current plan",
                "suggested_strategy": None
            }
        else:
            evaluation = self.grok.parse_json_response(response["content"])
            if not isinstance(evaluation, dict):
                evaluation = {"replan_needed": False, "reason": "Invalid response", "suggested_strategy": None}
            if "replan_needed" not in evaluation:
                evaluation["replan_needed"] = False
        
        step = ExecutionStep(
            step_name="Strategy Evaluation",
            step_type="evaluate",
            input_data={"analysis": analysis, "results_count": len(results)},
            output_data=evaluation,
            reasoning=response.get("content", json.dumps(evaluation)),
            timestamp=datetime.now().isoformat(),
            model_used=config.ModelConfig.REFINER_MODEL,
            tokens_used=response.get("total_tokens", 0)
        )
        self.context.add_step(step)
        
        return evaluation
    
    def critique(self, query: str, analysis: Dict, plan: Dict, results: List[Dict], summary: str) -> Dict:
        """
        Critique step: Review analysis and summary for hallucinations and bias
        
        Checks:
        - Are claims supported by retrieved data?
        - Is there selection bias?
        - Are there hallucinations (made-up facts)?
        - Is the analysis balanced?
        
        Returns:
            Dict with "critique_passed" (bool), "hallucinations", "biases", "corrections"
        """
        system_prompt = """You are a research critique specialist. Review the analysis and summary 
        for hallucinations (unsupported claims), bias, and factual errors.
        
        Return JSON:
        {
            "critique_passed": true|false,
            "hallucinations": ["claim1 not supported", "claim2 not in data"],
            "biases": ["selection bias: only positive posts", "temporal bias: only recent data"],
            "corrections": ["correction1", "correction2"],
            "confidence_adjustment": 0.0-1.0,
            "revised_summary": "corrected summary if critique failed"
        }
        
        Be strict: flag any claim that cannot be directly supported by the retrieved data."""
        
        # Prepare sample of retrieved data for verification (optimized: fewer items)
        data_sample = f"Retrieved {len(results)} items. Sample:\n\n"
        sample_size = min(config.CRITIQUE_SAMPLE_SIZE, len(results))
        for i, item in enumerate(results[:sample_size], 1):
            data_sample += f"{i}. {item.get('text', '')[:120]}\n"
            data_sample += f"   Sentiment: {item.get('sentiment', 'unknown')}\n"
            data_sample += f"   Author: {item.get('author', {}).get('display_name', 'Unknown')}\n\n"
        
        user_prompt = f"""Original Query: {query}

Retrieved Data Sample:
{data_sample}

Analysis:
{json.dumps(analysis, indent=2)}

Summary:
{summary}

Critique the analysis and summary:
1. Are all claims supported by the retrieved data?
2. Are there hallucinations (made-up facts)?
3. Is there bias (selection, temporal, sentiment)?
4. Is the analysis balanced and fair?"""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self.grok.call(
            model=config.ModelConfig.ANALYZER_MODEL,
            messages=messages,
            system_prompt=system_prompt,
            response_format={"type": "json_object"}
        )
        
        if not response.get("success", False):
            critique = {
                "critique_passed": True,  # Pass on error to avoid blocking
                "hallucinations": [],
                "biases": ["Could not complete critique due to API error"],
                "corrections": [],
                "confidence_adjustment": 0.0,
                "revised_summary": None
            }
        else:
            critique = self.grok.parse_json_response(response["content"])
            if not isinstance(critique, dict):
                critique = {"critique_passed": True, "hallucinations": [], "biases": [], "corrections": []}
            if "critique_passed" not in critique:
                critique["critique_passed"] = len(critique.get("hallucinations", [])) == 0
        
        step = ExecutionStep(
            step_name="Critique",
            step_type="critique",
            input_data={"results_count": len(results)},
            output_data=critique,
            reasoning=response.get("content", json.dumps(critique)),
            timestamp=datetime.now().isoformat(),
            model_used=config.ModelConfig.ANALYZER_MODEL,
            tokens_used=response.get("total_tokens", 0)
        )
        self.context.add_step(step)
        
        return critique
    
    def summarize(self, query: str, analysis: Dict, plan: Dict) -> str:
        """
        Step 5: Summarize - Generate final comprehensive summary
        
        Uses grok-4-fast-reasoning for high-quality summaries
        """
        system_prompt = """You are a research summarization expert. Create clear summaries.
        
        Structure: 1) Executive Summary (2-3 sentences), 2) Key Findings, 3) Analysis, 4) Limitations, 5) Recommendations"""
        
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
            max_tokens=config.MAX_TOKENS_SUMMARY
        )
        
        if not response.get("success", False):
            summary = (
                "Summary could not be generated due to an API error. "
                "Please try again. The analysis and retrieved results are still available."
            )
        else:
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
    
    def run_workflow(self, query: str, max_iterations: int = None, max_replans: int = 2) -> Dict:
        """
        Main workflow orchestrator using state machine pattern
        
        State transitions:
        - PLAN → EXECUTE
        - EXECUTE → ANALYZE
        - ANALYZE → EVALUATE (check if replan needed)
        - EVALUATE → PLAN (if replan needed) OR → REFINE
        - REFINE → ANALYZE (if refinement executed) OR → CRITIQUE
        - CRITIQUE → SUMMARIZE (or back to REFINE if major issues)
        - SUMMARIZE → COMPLETE
        
        Args:
            query: Research query
            max_iterations: Max refinement iterations
            max_replans: Max replanning cycles (default: 2)
        """
        if max_iterations is None:
            max_iterations = config.MAX_ITERATIONS
        
        self.context.clear()
        self.iteration_count = 0
        self.replan_count = 0
        self.current_state = WorkflowState.PLAN
        
        # State variables
        plan = None
        results = []
        analysis = None
        summary = None
        critique_result = None
        
        print(f"\n{'='*70}")
        print(f"🚀 Starting Agentic Research Workflow (State Machine)")
        print(f"{'='*70}")
        print(f"Query: {query}\n")
        
        # State machine loop
        while self.current_state != WorkflowState.COMPLETE:
            
            if self.current_state == WorkflowState.PLAN:
                print(f"📋 [{self.current_state.value.upper()}] Planning...")
                self._emit_progress('planning', {'status': 'started', 'message': 'Analyzing query and creating plan...'})
                plan = self.plan(query)
                
                plan_summary = f"Created a {plan.get('expected_complexity', 'medium')} complexity plan for a {plan.get('query_type', 'unknown')} query. "
                plan_summary += f"Identified {len(plan.get('steps', []))} execution steps."
                
                self._emit_progress('planning', {
                    'status': 'completed',
                    'query_type': plan.get('query_type', 'unknown'),
                    'steps_count': len(plan.get('steps', [])),
                    'complexity': plan.get('expected_complexity', 'unknown'),
                    'summary': plan_summary
                })
                print(f"   Query Type: {plan.get('query_type', 'unknown')}")
                print(f"   Steps Planned: {len(plan.get('steps', []))}\n")
                
                self.current_state = WorkflowState.EXECUTE
            
            elif self.current_state == WorkflowState.EXECUTE:
                print(f"⚙️  [{self.current_state.value.upper()}] Executing retrieval...")
                self._emit_progress('executing', {'status': 'started', 'message': 'Retrieving relevant data...'})
                results = self.execute(plan, query)
                
                execute_summary = f"Retrieved {len(results)} relevant items from the dataset."
                self._emit_progress('executing', {
                    'status': 'completed', 
                    'results_count': len(results),
                    'summary': execute_summary
                })
                print(f"   Retrieved: {len(results)} items\n")
                
                self.current_state = WorkflowState.ANALYZE
            
            elif self.current_state == WorkflowState.ANALYZE:
                print(f"🔍 [{self.current_state.value.upper()}] Analyzing results...")
                self._emit_progress('analyzing', {'status': 'started', 'message': 'Analyzing retrieved data...'})
                analysis = self.analyze(query, results, plan)
                confidence = analysis.get("confidence", 0.5)
                
                analyze_summary = f"Analysis completed with {confidence:.0%} confidence."
                self._emit_progress('analyzing', {
                    'status': 'completed',
                    'confidence': confidence,
                    'main_themes': analysis.get('main_themes', [])[:3],
                    'summary': analyze_summary
                })
                print(f"   Confidence: {confidence:.2f}")
                print(f"   Main Themes: {', '.join(analysis.get('main_themes', [])[:3])}\n")
                
                self.current_state = WorkflowState.EVALUATE
            
            elif self.current_state == WorkflowState.EVALUATE:
                # Skip evaluate if fast mode or high confidence (optimization)
                confidence = analysis.get("confidence", 0.5) if analysis else 0.5
                skip_evaluate = (
                    config.ENABLE_FAST_MODE or 
                    (config.SKIP_EVALUATE_IF_HIGH_CONFIDENCE and confidence > 0.85)
                )
                
                if skip_evaluate:
                    print(f"🔎 [{self.current_state.value.upper()}] Skipping evaluation (fast mode or high confidence)\n")
                    evaluation = {"replan_needed": False, "reason": "Skipped for performance", "suggested_strategy": None}
                    self._emit_progress('evaluating', {
                        'status': 'skipped',
                        'reason': 'High confidence or fast mode',
                        'summary': 'Evaluation skipped for performance'
                    })
                else:
                    print(f"🔎 [{self.current_state.value.upper()}] Evaluating strategy...")
                    self._emit_progress('evaluating', {'status': 'started', 'message': 'Evaluating if replan needed...'})
                    evaluation = self.evaluate_for_replan(query, analysis, plan, results)
                
                replan_needed = evaluation.get("replan_needed", False)
                
                # Emit evaluation completion
                eval_summary = "Strategy evaluation completed"
                if replan_needed:
                    eval_summary += f" - Replan needed: {evaluation.get('reason', '')}"
                else:
                    eval_summary += " - Strategy is sound"
                
                self._emit_progress('evaluating', {
                    'status': 'completed',
                    'replan_needed': replan_needed,
                    'reason': evaluation.get('reason', ''),
                    'summary': eval_summary
                })
                
                if replan_needed and self.replan_count < max_replans:
                    self.replan_count += 1
                    print(f"   ⚠️  Replan needed: {evaluation.get('reason', '')}")
                    print(f"   Suggested strategy: {evaluation.get('suggested_strategy', 'N/A')}")
                    print(f"   Replanning (attempt {self.replan_count}/{max_replans})...\n")
                    self._emit_progress('replanning', {
                        'status': 'replanning',
                        'reason': evaluation.get('reason', ''),
                        'attempt': self.replan_count,
                        'summary': f"Replanning due to: {evaluation.get('reason', '')}"
                    })
                    # Reset results/analysis for new plan
                    results = []
                    analysis = None
                    self.current_state = WorkflowState.PLAN
                else:
                    if replan_needed:
                        print(f"   Max replans reached ({max_replans}), proceeding with current plan\n")
                    else:
                        print(f"   Strategy is sound, proceeding to refinement\n")
                    self.current_state = WorkflowState.REFINE
            
            elif self.current_state == WorkflowState.REFINE:
                iteration = self.iteration_count + 1
                if iteration > max_iterations:
                    print(f"   Max refinement iterations reached ({max_iterations}), proceeding to critique\n")
                    self.current_state = WorkflowState.CRITIQUE
                    continue
                
                print(f"🔄 [{self.current_state.value.upper()}] Refinement Check (Iteration {iteration})...")
                self._emit_progress('refining', {
                    'status': 'checking',
                    'iteration': iteration,
                    'message': f'Checking if refinement needed (iteration {iteration})...'
                })
                refinement = self.refine(query, analysis, plan)
                refinement_needed = refinement.get("refinement_needed", False)
                
                if refinement_needed:
                    self.iteration_count = iteration
                    print(f"   Refinement needed: {refinement.get('reason', '')}")
                    
                    self._emit_progress('refining', {
                        'status': 'refining',
                        'iteration': iteration,
                        'reason': refinement.get('reason', ''),
                        'summary': f"Refinement iteration {iteration}: {refinement.get('reason', '')}"
                    })
                    
                    # Execute refinement steps
                    refinement_plan = {
                        "steps": refinement.get("next_steps", []),
                        "query_type": plan.get("query_type")
                    }
                    additional_results = self.execute(refinement_plan, query)
                    results.extend(additional_results)
                    
                    # Deduplicate
                    seen_ids = set()
                    deduped = []
                    for r in results:
                        if r["id"] not in seen_ids:
                            seen_ids.add(r["id"])
                            deduped.append(r)
                    results = deduped
                    
                    # Re-analyze
                    analysis = self.analyze(query, results, plan)
                    confidence = analysis.get("confidence", 0.5)
                    
                    print(f"   Updated Confidence: {confidence:.2f}\n")
                    # Loop back to analyze (which will go to evaluate)
                    self.current_state = WorkflowState.ANALYZE
                else:
                    print(f"   No refinement needed: {refinement.get('reason', '')}\n")
                    self.current_state = WorkflowState.CRITIQUE
            
            elif self.current_state == WorkflowState.CRITIQUE:
                # Skip critique if fast mode or high confidence (optimization)
                confidence = analysis.get("confidence", 0.5) if analysis else 0.5
                skip_critique = (
                    config.ENABLE_FAST_MODE or 
                    (config.SKIP_CRITIQUE_IF_HIGH_CONFIDENCE and confidence > 0.85)
                )
                
                if skip_critique:
                    print(f"🔬 [{self.current_state.value.upper()}] Skipping critique (fast mode or high confidence)\n")
                    critique_result = {
                        "critique_passed": True,
                        "hallucinations": [],
                        "biases": [],
                        "corrections": [],
                        "confidence_adjustment": 0.0,
                        "revised_summary": None
                    }
                    self._emit_progress('critiquing', {
                        'status': 'skipped',
                        'critique_passed': True,
                        'summary': 'Critique skipped for performance'
                    })
                    # Generate summary if not already done
                    if summary is None:
                        summary = self.summarize(query, analysis, plan)
                else:
                    print(f"🔬 [{self.current_state.value.upper()}] Critiquing analysis...")
                    self._emit_progress('critiquing', {'status': 'started', 'message': 'Reviewing for hallucinations and bias...'})
                    
                    # Generate summary first for critique
                    if summary is None:
                        summary = self.summarize(query, analysis, plan)
                    
                    critique_result = self.critique(query, analysis, plan, results, summary)
                critique_passed = critique_result.get("critique_passed", True)
                
                # Emit critique completion
                critique_summary = f"Critique {'passed' if critique_passed else 'found issues'}"
                if not critique_passed:
                    hallucinations = critique_result.get("hallucinations", [])
                    biases = critique_result.get("biases", [])
                    if hallucinations:
                        critique_summary += f" ({len(hallucinations)} hallucinations)"
                    if biases:
                        critique_summary += f" ({len(biases)} biases)"
                
                self._emit_progress('critiquing', {
                    'status': 'completed',
                    'critique_passed': critique_passed,
                    'hallucinations_count': len(critique_result.get("hallucinations", [])),
                    'biases_count': len(critique_result.get("biases", [])),
                    'summary': critique_summary
                })
                
                if not critique_passed:
                    hallucinations = critique_result.get("hallucinations", [])
                    biases = critique_result.get("biases", [])
                    print(f"   ⚠️  Critique found issues:")
                    if hallucinations:
                        print(f"      Hallucinations: {len(hallucinations)}")
                    if biases:
                        print(f"      Biases: {len(biases)}")
                    
                    # If major issues, try to refine once more
                    if hallucinations and self.iteration_count < max_iterations:
                        print(f"   Attempting refinement to address issues...\n")
                        self.current_state = WorkflowState.REFINE
                    else:
                        # Use revised summary if provided
                        revised = critique_result.get("revised_summary")
                        if revised:
                            summary = revised
                        print(f"   Proceeding with corrections applied\n")
                        self.current_state = WorkflowState.SUMMARIZE
                else:
                    print(f"   ✅ Critique passed - no major issues found\n")
                    self.current_state = WorkflowState.SUMMARIZE
            
            elif self.current_state == WorkflowState.SUMMARIZE:
                if summary is None:
                    print(f"📝 [{self.current_state.value.upper()}] Generating final summary...")
                    self._emit_progress('summarizing', {'status': 'started', 'message': 'Generating final summary...'})
                    summary = self.summarize(query, analysis, plan)
                    print("   ✅ Summary complete\n")
                
                self.current_state = WorkflowState.COMPLETE
        
        # Compile final results
        total_tokens = sum(step.tokens_used or 0 for step in self.context.execution_steps)
        confidence = analysis.get("confidence", 0.5) if analysis else 0.0
        
        result = {
            "query": query,
            "plan": plan,
            "results_count": len(results),
            "analysis": analysis,
            "refinement_iterations": self.iteration_count,
            "replan_count": self.replan_count,
            "critique": critique_result,
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
        print(f"Replan Cycles: {self.replan_count}")
        print(f"Total Tokens Used: {total_tokens}")
        print(f"Final Confidence: {confidence:.2f}")
        print(f"{'='*70}\n")
        
        return result
