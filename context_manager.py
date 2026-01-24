"""
Context Manager for Agentic Workflow
Tracks conversation history, execution steps, and manages context limits
"""
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import json
import config

@dataclass
class ExecutionStep:
    """Represents a single step in the agent workflow"""
    step_name: str
    step_type: str  # "plan", "execute", "analyze", "refine", "summarize"
    input_data: Dict
    output_data: Dict
    reasoning: str
    timestamp: str
    model_used: str
    tokens_used: Optional[int] = None
    
    def to_dict(self):
        return asdict(self)

class ContextManager:
    """Manages context and execution history for the agent"""
    
    def __init__(self, max_context_tokens: int = None):
        """
        Initialize context manager
        
        Args:
            max_context_tokens: Maximum tokens to keep in context
        """
        self.max_context_tokens = max_context_tokens or config.MAX_CONTEXT_TOKENS
        self.execution_steps: List[ExecutionStep] = []
        self.conversation_history: List[Dict] = []
        self.intermediate_results: Dict = {}
        self.total_tokens_used = 0
    
    def add_step(self, step: ExecutionStep):
        """Add an execution step to history"""
        self.execution_steps.append(step)
        if step.tokens_used:
            self.total_tokens_used += step.tokens_used
    
    def add_conversation(self, role: str, content: str):
        """Add a conversation turn"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def store_intermediate_result(self, key: str, value: any):
        """Store intermediate result for later use"""
        self.intermediate_results[key] = value
    
    def get_intermediate_result(self, key: str, default=None):
        """Retrieve intermediate result"""
        return self.intermediate_results.get(key, default)
    
    def get_recent_steps(self, n: int = 5) -> List[ExecutionStep]:
        """Get the most recent n execution steps"""
        return self.execution_steps[-n:]
    
    def get_steps_by_type(self, step_type: str) -> List[ExecutionStep]:
        """Get all steps of a specific type"""
        return [step for step in self.execution_steps if step.step_type == step_type]
    
    def build_context_summary(self) -> str:
        """Build a summary of context for Grok"""
        summary_parts = []
        
        # Add execution summary
        if self.execution_steps:
            summary_parts.append("Execution History:")
            for step in self.execution_steps[-5:]:  # Last 5 steps
                summary_parts.append(
                    f"- {step.step_name} ({step.step_type}): {step.reasoning[:100]}..."
                )
        
        # Add intermediate results summary
        if self.intermediate_results:
            summary_parts.append("\nIntermediate Results:")
            for key, value in list(self.intermediate_results.items())[-3:]:
                if isinstance(value, (str, int, float, bool)):
                    summary_parts.append(f"- {key}: {value}")
                elif isinstance(value, list):
                    summary_parts.append(f"- {key}: {len(value)} items")
                else:
                    summary_parts.append(f"- {key}: {type(value).__name__}")
        
        return "\n".join(summary_parts)
    
    def get_conversation_context(self, max_turns: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        return self.conversation_history[-max_turns:]
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 characters)"""
        return len(text) // 4
    
    def should_summarize_context(self) -> bool:
        """Check if context should be summarized to save tokens"""
        estimated_tokens = sum(
            self.estimate_tokens(step.reasoning)
            for step in self.execution_steps
        )
        return estimated_tokens > self.max_context_tokens * 0.8
    
    def create_summarized_context(self) -> str:
        """Create a summarized version of context"""
        if not self.execution_steps:
            return "No execution history yet."
        
        summary = f"Total steps executed: {len(self.execution_steps)}\n"
        summary += f"Total tokens used: {self.total_tokens_used}\n\n"
        
        # Group by step type
        step_types = {}
        for step in self.execution_steps:
            if step.step_type not in step_types:
                step_types[step.step_type] = []
            step_types[step.step_type].append(step)
        
        summary += "Step Summary:\n"
        for step_type, steps in step_types.items():
            summary += f"- {step_type}: {len(steps)} steps\n"
        
        # Add most recent reasoning
        if self.execution_steps:
            latest = self.execution_steps[-1]
            summary += f"\nLatest step ({latest.step_name}): {latest.reasoning[:200]}..."
        
        return summary
    
    def export_to_dict(self) -> Dict:
        """Export full context to dictionary"""
        return {
            "execution_steps": [step.to_dict() for step in self.execution_steps],
            "conversation_history": self.conversation_history,
            "intermediate_results": self.intermediate_results,
            "total_tokens_used": self.total_tokens_used,
            "export_timestamp": datetime.now().isoformat()
        }
    
    def save_to_file(self, filepath: str):
        """Save context to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.export_to_dict(), f, indent=2, ensure_ascii=False, default=str)
    
    def load_from_file(self, filepath: str):
        """Load context from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.execution_steps = [
            ExecutionStep(**step) for step in data.get("execution_steps", [])
        ]
        self.conversation_history = data.get("conversation_history", [])
        self.intermediate_results = data.get("intermediate_results", {})
        self.total_tokens_used = data.get("total_tokens_used", 0)
    
    def clear(self):
        """Clear all context (use with caution)"""
        self.execution_steps = []
        self.conversation_history = []
        self.intermediate_results = {}
        self.total_tokens_used = 0
