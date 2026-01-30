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
from utils.truncation import create_concise_data_summary, truncate_results_for_llm, truncate_text

class WorkflowState(Enum):
    """States in the agent workflow state machine"""
    PLAN = "plan"
    EXECUTE = "execute"
    VALIDATE_RESULTS = "validate_results"  # Validate results quality before analysis
    ANALYZE = "analyze"
    EVALUATE = "evaluate"  # Evaluate if replan needed
    REFINE = "refine"
    CRITIQUE = "critique"
    SUMMARIZE = "summarize"
    COMPLETE = "complete"


class AgenticResearchAgent:
    """Main agentic research agent using Grok with state machine orchestration"""
    
    def __init__(self, data: List[Dict], api_key: Optional[str] = None, progress_callback=None, model_config: Optional[Dict] = None):
        """
        Initialize agent
        
        Args:
            data: Dataset to search (list of posts/documents)
            api_key: Optional Grok API key
            progress_callback: Optional callback function(event_type, data) for progress updates
            model_config: Optional dict overriding model config (e.g. {"PLANNER_MODEL": "grok-3", ...})
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
        self.model_config = model_config or {}
    
    def _get_model(self, model_type: str) -> str:
        """Get model name for a given type, using override if provided"""
        return self.model_config.get(model_type, getattr(config.ModelConfig, model_type))
    
    def _emit_progress(self, event_type: str, data: Dict):
        """Emit progress event if callback is set"""
        if self.progress_callback:
            self.progress_callback(event_type, data)
    
    def plan(self, query: str) -> Dict:
        """
        Step 1: Plan - Decompose query into actionable steps
        
        Uses grok-4-fast-reasoning for complex reasoning
        """
        system_prompt = """Research planner. Break queries into steps.

Modes:
1. Plan-based: Exact steps (straightforward queries) - FASTER
2. Tool-calling: Dynamic tool selection (complex/exploratory queries) - SLOWER

Return JSON:
{
    "query_type": "trend_analysis|info_extraction|comparison|sentiment|temporal|other",
    "use_tool_calling": true/false,
    "steps": [
        {"step_number": 1, "action": "search", "description": "...", "tools": ["hybrid_search"]},
        {"step_number": 2, "action": "filter", "description": "...", "filters": {...}}
    ],
    "success_criteria": ["criterion1"],
    "expected_complexity": "low|medium|high"
}

Use tool_calling=true ONLY for: very complex multi-step queries requiring iterative tool selection.
Prefer plan-based (use_tool_calling=false) for: simple searches, single-step queries, straightforward info extraction."""
        
        user_prompt = f"""Query: "{query}"

Create a plan. Consider: query type, information needed, analysis required, filters/constraints."""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self.grok.call(
            model=self._get_model("PLANNER_MODEL"),
            messages=messages,
            system_prompt=system_prompt,
            response_format={"type": "json_object"}
        )
        
        if not response.get("success", False):
            # Fallback plan if API fails
            plan = {
                "query_type": "other",
                "use_tool_calling": False,
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
                    "use_tool_calling": False,
                    "steps": [
                        {"step_number": 1, "action": "search", "description": "Search for relevant posts", "tools": ["hybrid_search"]},
                        {"step_number": 2, "action": "analyze", "description": "Analyze retrieved results"}
                    ],
                    "success_criteria": ["Relevant results found"],
                    "expected_complexity": "medium"
                }
            
            # Ensure use_tool_calling is set (default to False for speed)
            if "use_tool_calling" not in plan:
                plan["use_tool_calling"] = False
            
            # Override: Disable tool calling for simple queries (performance optimization)
            complexity = plan.get("expected_complexity", "medium").lower()
            query_type = plan.get("query_type", "other").lower()
            steps_count = len(plan.get("steps", []))
            
            # Simple query heuristics: disable tool calling for faster execution
            is_simple = (
                complexity == "low" or
                steps_count <= 2 or
                query_type in ["info_extraction", "sentiment"]  # Usually straightforward
            )
            
            if is_simple and plan.get("use_tool_calling", False):
                plan["use_tool_calling"] = False
                print(f"   ⚡ Simplified workflow: disabled tool calling for faster execution")
        
        # Store plan
        step = ExecutionStep(
            step_name="Planning",
            step_type="plan",
            input_data={"query": query},
            output_data=plan,
            reasoning=plan_content,
            timestamp=datetime.now().isoformat(),
            model_used=self._get_model("PLANNER_MODEL"),
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
        
        Args:
            query: Research query
            max_tool_calls: Maximum number of tool call iterations allowed
            
        Returns:
            List of retrieved posts
        """
        # Get tool definitions
        tools = self.tool_registry.get_tool_definitions()
        
        # Initial system prompt
        system_prompt = """You are a research assistant that uses tools to find information.
        
Available tools:
- keyword_search: Search posts using keyword matching (good for exact terms, hashtags)
- semantic_search: Search posts using semantic similarity (good for concepts, meaning)
- hybrid_search: Combines keyword and semantic search (recommended for most queries)
- user_profile_lookup: Find posts by specific authors
- temporal_trend_analyzer: Analyze trends over time periods
- filter_by_metadata: Filter results by sentiment, engagement, verification status

Use tools iteratively to gather comprehensive information. You can call multiple tools in one turn.
After seeing tool results, decide if you need more information or can proceed."""
        
        # Conversation history
        messages = [
            {
                "role": "user",
                "content": f"Research query: {query}\n\nUse tools to find relevant information. You can call multiple tools."
            }
        ]
        
        all_results = []
        seen_post_ids = set()
        tool_call_count = 0
        total_tokens = 0
        tool_calls_history = []
        
        # Emit initial tool calling start
        self._emit_progress('executing', {
            'status': 'started',
            'message': 'Starting dynamic tool calling...',
            'tool_calling_mode': True,
            'tool_calls': []
        })
        
        while tool_call_count < max_tool_calls:
            # Call Grok with tools
            response = self.grok.call(
                model=self._get_model("PLANNER_MODEL"),  # Use planner model for tool selection
                messages=messages,
                system_prompt=system_prompt,
                tools=tools,
                tool_choice="auto",
                max_tokens=500,
                temperature=0.7
            )
            
            if not response.get("success"):
                print(f"⚠️ Tool calling API error: {response.get('error', 'Unknown error')}")
                total_tokens += response.get("total_tokens", 0)
                break
            
            total_tokens += response.get("total_tokens", 0)
            
            # Add assistant message to conversation
            assistant_message = {"role": "assistant", "content": response.get("content", "")}
            messages.append(assistant_message)
            
            # Check for tool calls
            tool_calls = response.get("tool_calls", [])
            
            if not tool_calls:
                # No more tool calls - Grok is done
                self._emit_progress('executing', {
                    'status': 'completed',
                    'message': f'Tool calling completed. Retrieved {len(all_results)} results',
                    'tool_calling_mode': True,
                    'tool_calls': tool_calls_history,
                    'total_results': len(all_results),
                    'total_tool_calls': tool_call_count
                })
                break
            
            # Execute each tool call
            tool_results = []
            iteration_tool_calls = []
            
            for tool_call in tool_calls:
                tool_call_count += 1
                function_name = tool_call["function"]["name"]
                function_args_str = tool_call["function"]["arguments"]
                
                # Parse arguments
                try:
                    function_args = json.loads(function_args_str)
                except json.JSONDecodeError:
                    function_args = {}
                
                print(f"🔧 Calling tool: {function_name} with args: {function_args}")
                
                # Emit tool call start
                self._emit_progress('executing', {
                    'status': 'tool_calling',
                    'message': f'Calling tool: {function_name}...',
                    'tool_calling_mode': True,
                    'current_tool': {
                        'name': function_name,
                        'arguments': function_args,
                        'status': 'executing'
                    }
                })
                
                # Execute tool
                tool_result = self.tool_registry.call_tool(function_name, function_args)
                
                # Collect results
                results_count = 0
                if tool_result.get("success"):
                    results = tool_result.get("results", [])
                    results_count = len(results)
                    for result in results:
                        post_id = result.get("id")
                        if post_id and post_id not in seen_post_ids:
                            seen_post_ids.add(post_id)
                            all_results.append(result)
                    
                    tool_results.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps({
                            "success": True,
                            "message": tool_result.get("message", ""),
                            "results_count": len(results),
                            "sample_results": results[:3] if results else []
                        })
                    })
                else:
                    tool_results.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps({
                            "success": False,
                            "message": tool_result.get("message", "Tool execution failed")
                        })
                    })
                
                # Track tool call for history
                iteration_tool_calls.append({
                    'name': function_name,
                    'arguments': function_args,
                    'success': tool_result.get("success", False),
                    'results_count': results_count,
                    'message': tool_result.get("message", "")
                })
            
            # Emit tool calls completion for this iteration
            tool_calls_history.extend(iteration_tool_calls)
            self._emit_progress('executing', {
                'status': 'tool_calling',
                'message': f'Completed {len(iteration_tool_calls)} tool call(s). Total results: {len(all_results)}',
                'tool_calling_mode': True,
                'tool_calls': tool_calls_history,
                'total_results': len(all_results),
                'iteration': len(tool_calls_history)
            })
            
            # Add tool results to conversation
            messages.extend(tool_results)
            
            # Limit total results
            if len(all_results) >= config.MAX_RETRIEVAL_RESULTS:
                break
        
        # Limit and deduplicate final results
        final_results = all_results[:config.MAX_RETRIEVAL_RESULTS]
        
        # Emit final completion
        self._emit_progress('executing', {
            'status': 'completed',
            'message': f'Tool calling finished. Retrieved {len(final_results)} results',
            'tool_calling_mode': True,
            'tool_calls': tool_calls_history,
            'total_results': len(final_results),
            'total_tool_calls': tool_call_count,
            'results_count': len(final_results)
        })
        
        # Log execution step
        step = ExecutionStep(
            step_name="Tool-Calling Execution",
            step_type="execute",
            input_data={"query": query, "max_tool_calls": max_tool_calls},
            output_data={"results_count": len(final_results), "tool_calls_made": tool_call_count, "tool_calls": tool_calls_history},
            reasoning=f"Used {tool_call_count} tool calls to retrieve {len(final_results)} results",
            timestamp=datetime.now().isoformat(),
            model_used=self._get_model("PLANNER_MODEL"),
            tokens_used=total_tokens
        )
        self.context.add_step(step)
        self.context.store_intermediate_result("execution_results", final_results)
        
        return final_results
    
    def validate_results(self, query: str, results: List[Dict], plan: Dict) -> Dict:
        """
        Validate that retrieved results match query intent before analysis
        
        Returns:
            Dict with "validation_passed", "relevance_score", "recommendations", "action"
        """
        if not results:
            validation = {
                "validation_passed": False,
                "relevance_score": 0.0,
                "recommendations": ["No results retrieved - need to expand search"],
                "action": "replan"  # No results = fundamental issue
            }
            step = ExecutionStep(
                step_name="Result Validation",
                step_type="validate",
                input_data={"results_count": 0},
                output_data=validation,
                reasoning="No results retrieved - validation failed",
                timestamp=datetime.now().isoformat(),
                model_used="validation_logic",
                tokens_used=0
            )
            self.context.add_step(step)
            return validation
        
        # Check result count - only trigger refinement if no results at all
        # Even 1-2 results might be sufficient for analysis
        if len(results) == 0:
            validation = {
                "validation_passed": False,
                "relevance_score": 0.0,
                "recommendations": ["No results retrieved - need to expand search"],
                "action": "replan"
            }
            step = ExecutionStep(
                step_name="Result Validation",
                step_type="validate",
                input_data={"results_count": 0},
                output_data=validation,
                reasoning="No results retrieved - need to replan",
                timestamp=datetime.now().isoformat(),
                model_used="validation_logic",
                tokens_used=0
            )
            self.context.add_step(step)
            return validation
        
        system_prompt = """Result validator. Check if retrieved results match query intent.
        
Return JSON:
{
    "validation_passed": true|false,
    "relevance_score": 0.0-1.0,
    "recommendations": ["action1", "action2"],
    "action": "proceed|refine|replan"
}

Actions:
- "proceed": Results are relevant enough to analyze (default - prefer this unless results are clearly wrong)
- "refine": Results are somewhat relevant but need more/better data (only if relevance_score < 0.4)
- "replan": Results don't match query at all, need completely new strategy (only if relevance_score < 0.3)

Be lenient: Only recommend "refine" or "replan" if results are clearly irrelevant or insufficient. If results are somewhat related to the query, prefer "proceed" to allow analysis."""
        
        # Sample results for validation
        sample_size = min(5, len(results))
        sample_results = results[:sample_size]
        
        data_summary = create_concise_data_summary(
            sample_results,
            query,
            max_items=sample_size,
            max_text_length=100
        )
        
        user_prompt = f"""Query: {query}
Plan: {json.dumps({'query_type': plan.get('query_type'), 'steps_count': len(plan.get('steps', []))}, separators=(',', ':'))}
Retrieved Results ({len(results)} total): {data_summary}

Validate: Do these results match the query intent? Are they relevant?"""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self.grok.call(
            model=self._get_model("ANALYZER_MODEL"),
            messages=messages,
            system_prompt=system_prompt,
            response_format={"type": "json_object"}
        )
        
        if not response.get("success", False):
            # Default to proceed on error, but with moderate relevance score
            validation = {
                "validation_passed": True,
                "relevance_score": 0.6,
                "recommendations": [],
                "action": "proceed"
            }
            validation_content = json.dumps(validation)
        else:
            validation_content = response["content"]
            validation = self.grok.parse_json_response(validation_content)
            if not isinstance(validation, dict):
                validation = {"validation_passed": True, "relevance_score": 0.6, "action": "proceed"}
            if "action" not in validation:
                validation["action"] = "proceed" if validation.get("validation_passed") else "refine"
            if "relevance_score" not in validation:
                validation["relevance_score"] = 0.7 if validation.get("validation_passed") else 0.4
        
        step = ExecutionStep(
            step_name="Result Validation",
            step_type="validate",
            input_data={"results_count": len(results)},
            output_data=validation,
            reasoning=validation_content,
            timestamp=datetime.now().isoformat(),
            model_used=self._get_model("ANALYZER_MODEL"),
            tokens_used=response.get("total_tokens", 0)
        )
        self.context.add_step(step)
        
        return validation
    
    def execute(self, plan: Dict, query: str) -> List[Dict]:
        """
        Step 2: Execute - Retrieve data using hybrid search or dynamic tool calling
        
        Uses retrieval tools based on plan. If plan specifies use_tool_calling=True,
        uses dynamic tool calling where Grok selects tools iteratively. Otherwise,
        uses plan-based execution with specified tools.
        
        Search steps use step["description"] as the search query when present
        (plan or refinement); otherwise fall back to the original query.
        """
        # Check if plan requests tool calling
        use_tool_calling = plan.get("use_tool_calling", False)
        
        if use_tool_calling:
            # Use dynamic tool calling
            search_query = query
            # If plan has a search step with description, use that as the query
            steps = plan.get("steps", [])
            for step in steps:
                if step.get("action") == "search" and step.get("description"):
                    search_query = step.get("description")
                    break
            
            return self.execute_with_tool_calling(search_query, max_tool_calls=5)
        
        # Plan-based execution (original approach)
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
        system_prompt = """Research analyst. Analyze data for patterns, themes, insights.

Return JSON:
{
    "main_themes": ["theme1", "theme2"],
    "key_insights": ["insight1", "insight2"],
    "sentiment_analysis": {"positive": count, "negative": count, "neutral": count},
    "engagement_patterns": {...},
    "notable_findings": ["finding1"],
    "data_quality": "high|medium|low",
    "confidence": 0.0-1.0,
    "gaps_or_limitations": ["gap1"]
}"""
        
        # Use optimized truncation utility
        data_summary = create_concise_data_summary(
            results,
            query,
            max_items=config.ANALYZE_SAMPLE_SIZE,
            max_text_length=config.ANALYZE_TEXT_LENGTH
        )
        
        # Truncate plan steps for prompt
        plan_steps = plan.get('steps', [])[:3]  # Only include first 3 steps
        
        user_prompt = f"""{data_summary}

Plan steps: {json.dumps(plan_steps, separators=(',', ':'))}

Analyze and return JSON."""
        
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
            model_used=self._get_model("ANALYZER_MODEL"),
            tokens_used=response.get("total_tokens", 0)
        )
        self.context.add_step(step)
        self.context.store_intermediate_result("analysis", analysis)
        
        return analysis
    
    def refine(self, query: str, analysis: Dict, plan: Dict, previous_confidence: Optional[float] = None) -> Dict:
        """
        Step 4: Refine - Determine if refinement is needed
        
        Uses grok-4-fast-reasoning for decision making
        
        Args:
            query: Research query
            analysis: Current analysis results
            plan: Original plan
            previous_confidence: Confidence from previous iteration (for stagnation detection)
        """
        confidence = analysis.get("confidence", 0.5)
        
        # Check if confidence improved from previous iteration
        if previous_confidence is not None:
            confidence_delta = confidence - previous_confidence
            if confidence_delta < 0.05 and self.iteration_count > 0:
                # Confidence not improving - might be stuck
                refinement = {
                    "refinement_needed": False,
                    "reason": f"Confidence not improving (delta: {confidence_delta:.2f}) - proceeding to avoid loops",
                    "next_steps": [],
                    "confidence_stagnant": True
                }
                step = ExecutionStep(
                    step_name="Refinement Check",
                    step_type="refine",
                    input_data={"confidence": confidence, "previous_confidence": previous_confidence},
                    output_data=refinement,
                    reasoning=f"Confidence stagnation detected: {previous_confidence:.2f} -> {confidence:.2f}",
                    timestamp=datetime.now().isoformat(),
                    model_used="decision_logic",
                    tokens_used=0
                )
                self.context.add_step(step)
                return refinement
        
        # If confidence is high, skip refinement (optimized threshold)
        if confidence > 0.85:  # Increased from 0.75 to catch more cases needing refinement
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
            model=self._get_model("REFINER_MODEL"),
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
        system_prompt = """Strategy evaluator. Determine if plan needs complete revision (not just refinement).

Return JSON:
{
    "replan_needed": true|false,
    "reason": "brief explanation",
    "suggested_strategy": "new approach if replan needed"
}

Replan if: confidence < 0.7 (70%) AND (data fundamentally wrong, strategy misaligned, quality issues require different approach).
Don't replan if: just need more data, need filters, or confidence >= 0.7 with sound strategy."""
        
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
        gaps = analysis.get("gaps_or_limitations", [])[:2]  # Limit gaps
        
        # Truncate plan and analysis
        plan_summary = {"steps_count": len(plan.get("steps", [])), "query_type": plan.get("query_type", "other")}
        analysis_summary = {
            "confidence": confidence,
            "data_quality": data_quality,
            "gaps": gaps,
            "sentiment_dist": sentiment_dist
        }
        
        user_prompt = f"""Query: {query}
Plan: {json.dumps(plan_summary, separators=(',', ':'))}
Analysis: {json.dumps(analysis_summary, separators=(',', ':'))}
Results: {len(results)} items, sarcasm_ratio: {sarcasm_ratio:.2f}

Evaluate: replan needed (fundamental strategy wrong) or refine (more data needed)?
Consider replanning if confidence < 0.7 (70%) and strategy appears misaligned."""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self.grok.call(
            model=self._get_model("REFINER_MODEL"),  # Reuse refiner model for evaluation
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
        system_prompt = """Critique specialist. Review for hallucinations, bias, factual errors.

Return JSON:
{
    "critique_passed": true|false,
    "hallucinations": ["claim1 not supported"],
    "biases": ["selection bias: only positive"],
    "corrections": ["correction1"],
    "confidence_adjustment": -0.1 to 0.1,
    "revised_summary": null or "corrected summary"
}

Flag unsupported claims."""
        
        # Use truncation utility
        data_sample = create_concise_data_summary(
            results,
            query,
            max_items=config.CRITIQUE_SAMPLE_SIZE,
            max_text_length=100
        )
        
        # Truncate analysis and summary
        analysis_summary = {
            "main_themes": analysis.get("main_themes", [])[:3],
            "key_insights": analysis.get("key_insights", [])[:2],
            "confidence": analysis.get("confidence", 0)
        }
        summary_truncated = truncate_text(summary, max_chars=500)
        
        user_prompt = f"""Query: {query}
Data: {data_sample}
Analysis: {json.dumps(analysis_summary, separators=(',', ':'))}
Summary: {summary_truncated}

Check: claims supported? hallucinations? bias? balanced?"""
        
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
            model_used=self._get_model("ANALYZER_MODEL"),
            tokens_used=response.get("total_tokens", 0)
        )
        self.context.add_step(step)
        
        return critique
    
    def summarize(self, query: str, analysis: Dict, plan: Dict) -> str:
        """
        Step 5: Summarize - Generate final comprehensive summary
        
        Uses grok-4-fast-reasoning for high-quality summaries
        """
        system_prompt = """Summarization expert. Create clear, concise summaries.

Structure: Executive Summary, Key Findings, Analysis, Limitations, Recommendations"""
        
        # Truncate for summary prompt
        analysis_summary = {
            "main_themes": analysis.get("main_themes", [])[:5],
            "key_insights": analysis.get("key_insights", [])[:3],
            "sentiment_analysis": analysis.get("sentiment_analysis", {}),
            "confidence": analysis.get("confidence", 0)
        }
        plan_summary = {"steps_count": len(plan.get("steps", [])), "query_type": plan.get("query_type", "other")}
        
        user_prompt = f"""Query: {query}
Plan: {json.dumps(plan_summary, separators=(',', ':'))}
Analysis: {json.dumps(analysis_summary, separators=(',', ':'))}

Create concise summary answering the query."""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self.grok.call(
            model=self._get_model("SUMMARIZER_MODEL"),
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
            model_used=self._get_model("SUMMARIZER_MODEL"),
            tokens_used=response.get("total_tokens", 0)
        )
        self.context.add_step(step)
        
        return summary
    
    def run_workflow(self, query: str, max_iterations: int = None, max_replans: int = 2, fast_mode: bool = None) -> Dict:
        """
        Main workflow orchestrator using state machine pattern
        
        State transitions:
        - PLAN → EXECUTE
        - EXECUTE → VALIDATE_RESULTS (validate result quality)
        - VALIDATE_RESULTS → ANALYZE (if validated) OR → REFINE/REPLAN (if low quality)
        - ANALYZE → EVALUATE (check if replan needed)
        - EVALUATE → PLAN (if replan needed) OR → REFINE
        - REFINE → ANALYZE (if refinement executed) OR → CRITIQUE
        - CRITIQUE → SUMMARIZE (or back to REFINE if major issues)
        - SUMMARIZE → COMPLETE
        
        Args:
            query: Research query
            max_iterations: Max refinement iterations
            max_replans: Max replanning cycles (default: 2)
            fast_mode: Override config - skip evaluate/critique when True; None = use config
        """
        if max_iterations is None:
            max_iterations = config.MAX_ITERATIONS
        
        use_fast_mode = fast_mode if fast_mode is not None else config.ENABLE_FAST_MODE
        
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
        critique_refine_loop_count = 0  # Prevent CRITIQUE → REFINE → CRITIQUE infinite loop
        max_critique_refine_loops = 2
        previous_confidence = None  # Track confidence for improvement detection
        confidence_history = []  # Track confidence over iterations
        
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
                
                self.current_state = WorkflowState.VALIDATE_RESULTS
            
            elif self.current_state == WorkflowState.VALIDATE_RESULTS:
                print(f"✅ [{self.current_state.value.upper()}] Validating result quality...")
                self._emit_progress('validating', {'status': 'started', 'message': 'Validating result relevance...'})
                validation = self.validate_results(query, results, plan)
                
                action = validation.get("action", "proceed")
                relevance_score = validation.get("relevance_score", 0.5)
                validation_passed = validation.get("validation_passed", True)
                
                validation_summary = f"Validation {'passed' if validation_passed else 'failed'} (relevance: {relevance_score:.2f})"
                self._emit_progress('validating', {
                    'status': 'completed',
                    'validation_passed': validation_passed,
                    'relevance_score': relevance_score,
                    'action': action,
                    'summary': validation_summary
                })
                
                if action == "replan" and self.replan_count < max_replans:
                    # Only replan if relevance is very low (< 0.3)
                    if relevance_score < 0.3:
                        self.replan_count += 1
                        print(f"   ⚠️  Very low relevance ({relevance_score:.2f}) - replanning needed")
                        print(f"   Reason: {validation.get('recommendations', ['Low relevance'])}")
                        results = []
                        analysis = None
                        previous_confidence = None
                        confidence_history = []
                        self.current_state = WorkflowState.PLAN
                    else:
                        # Relevance not low enough for replan - proceed to analyze
                        print(f"   ✅ Results validated (relevance: {relevance_score:.2f}) - proceeding to analyze")
                        self.current_state = WorkflowState.ANALYZE
                elif action == "refine" and relevance_score < 0.4:
                    # Only refine if explicitly requested AND relevance is low (but not terrible)
                    print(f"   ⚠️  Low relevance ({relevance_score:.2f}) - triggering refinement")
                    recommendations = validation.get("recommendations", ["Expand search"])
                    # Create refinement plan from validation recommendations
                    refinement = {
                        "refinement_needed": True,
                        "reason": f"Low result relevance ({relevance_score:.2f}): {', '.join(recommendations)}",
                        "next_steps": [{"action": "search", "description": rec, "tools": ["hybrid_search"]} 
                                      for rec in recommendations[:2]]  # Limit to 2 steps
                    }
                    # Store refinement for REFINE state
                    self.context.store_intermediate_result("pending_refinement", refinement)
                    self.current_state = WorkflowState.REFINE
                else:
                    # Default: proceed to analyze (even if relevance is moderate)
                    print(f"   ✅ Results validated (relevance: {relevance_score:.2f})")
                    self.current_state = WorkflowState.ANALYZE
            
            elif self.current_state == WorkflowState.ANALYZE:
                print(f"🔍 [{self.current_state.value.upper()}] Analyzing results...")
                self._emit_progress('analyzing', {'status': 'started', 'message': 'Analyzing retrieved data...'})
                analysis = self.analyze(query, results, plan)
                confidence = analysis.get("confidence", 0.5)
                
                # Track confidence history
                confidence_history.append(confidence)
                previous_confidence = confidence_history[-2] if len(confidence_history) > 1 else None
                
                analyze_summary = f"Analysis completed with {confidence:.0%} confidence."
                self._emit_progress('analyzing', {
                    'status': 'completed',
                    'confidence': confidence,
                    'main_themes': analysis.get('main_themes', [])[:3],
                    'summary': analyze_summary
                })
                print(f"   Confidence: {confidence:.2f}")
                if previous_confidence is not None:
                    delta = confidence - previous_confidence
                    print(f"   Confidence Change: {delta:+.2f} (from {previous_confidence:.2f})")
                print(f"   Main Themes: {', '.join(analysis.get('main_themes', [])[:3])}\n")
                
                self.current_state = WorkflowState.EVALUATE
            
            elif self.current_state == WorkflowState.EVALUATE:
                # Skip evaluate if fast mode OR (high confidence AND good data quality)
                confidence = analysis.get("confidence", 0.5) if analysis else 0.5
                data_quality = analysis.get("data_quality", "medium") if analysis else "medium"
                
                # Only skip if BOTH high confidence AND good data quality
                skip_evaluate = (
                    use_fast_mode or 
                    (config.SKIP_EVALUATE_IF_HIGH_CONFIDENCE and confidence > 0.85 and data_quality == "high")
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
                
                # Check if there's a pending refinement from VALIDATE_RESULTS
                pending_refinement = self.context.get_intermediate_result("pending_refinement")
                if pending_refinement:
                    refinement = pending_refinement
                    self.context.clear_intermediate_result("pending_refinement")
                else:
                    refinement = self.refine(query, analysis, plan, previous_confidence)
                
                refinement_needed = refinement.get("refinement_needed", False)
                
                # Force refinement when critique found issues (we came from CRITIQUE)
                if critique_result and not critique_result.get("critique_passed", True):
                    if critique_refine_loop_count >= max_critique_refine_loops:
                        # Already looped too many times; proceed to summarize instead of going back to critique
                        print(f"   Max critique-refine loops ({max_critique_refine_loops}) reached, proceeding to summarize\n")
                        revised = critique_result.get("revised_summary")
                        if revised:
                            summary = revised
                        self.current_state = WorkflowState.SUMMARIZE
                        continue
                    refinement_needed = True
                    refinement["reason"] = f"Critique found issues: {len(critique_result.get('hallucinations', []))} hallucinations, {len(critique_result.get('biases', []))} biases"
                    default_steps = [{"action": "search", "description": "Expand search to address critique issues", "tools": ["hybrid_search"]}]
                    refinement.setdefault("next_steps", default_steps)
                
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
                    new_confidence = analysis.get("confidence", 0.5)
                    
                    # Track confidence improvement
                    confidence_history.append(new_confidence)
                    if previous_confidence is not None:
                        improvement = new_confidence - previous_confidence
                        if improvement < 0.05 and len(confidence_history) > 1:
                            print(f"   ⚠️  Confidence stagnating (improvement: {improvement:.2f}) - stopping refinement")
                            self.current_state = WorkflowState.CRITIQUE
                            previous_confidence = new_confidence
                            continue
                    
                    print(f"   Updated Confidence: {new_confidence:.2f}")
                    if previous_confidence is not None:
                        print(f"   Improvement: {improvement:+.2f}\n")
                    else:
                        print()
                    
                    previous_confidence = new_confidence
                    critique_result = None  # Clear so we don't force refinement again
                    critique_refine_loop_count = 0  # Reset after successful refinement
                    # Loop back to validate (to ensure new results are still relevant)
                    self.current_state = WorkflowState.VALIDATE_RESULTS
                else:
                    print(f"   No refinement needed: {refinement.get('reason', '')}\n")
                    # If we came from critique with issues, we'd have forced refinement above.
                    # Here we're on the normal path (REFINE → CRITIQUE).
                    self.current_state = WorkflowState.CRITIQUE
            
            elif self.current_state == WorkflowState.CRITIQUE:
                # Skip critique if fast mode OR (high confidence AND good data quality)
                confidence = analysis.get("confidence", 0.5) if analysis else 0.5
                data_quality = analysis.get("data_quality", "medium") if analysis else "medium"
                
                # Only skip if BOTH high confidence AND good data quality
                skip_critique = (
                    use_fast_mode or 
                    (config.SKIP_CRITIQUE_IF_HIGH_CONFIDENCE and confidence > 0.85 and data_quality == "high")
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
                    
                    # If major issues, try to refine once more (cap loops to avoid CRITIQUE↔REFINE infinite loop)
                    if hallucinations and self.iteration_count < max_iterations and critique_refine_loop_count < max_critique_refine_loops:
                        critique_refine_loop_count += 1
                        print(f"   Attempting refinement to address issues (loop {critique_refine_loop_count}/{max_critique_refine_loops})...\n")
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
                    critique_refine_loop_count = 0  # Reset on pass
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
