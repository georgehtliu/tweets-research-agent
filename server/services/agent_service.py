"""
Agent Service - Manages agent initialization and lifecycle
"""
import json
import sys
from pathlib import Path
from typing import Tuple, Optional, Dict

# Add server directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_generator import MockXDataGenerator
from agent import AgenticResearchAgent
import config


class AgentService:
    """Service for managing agent instances and data"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self._agent: Optional[AgenticResearchAgent] = None
        self._data: Optional[list] = None
    
    def initialize_agent(self, model_config: Optional[Dict] = None) -> Tuple[AgenticResearchAgent, list]:
        """
        Initialize the agent and load data
        
        Args:
            model_config: Optional model config override (creates new agent instance)
        
        Returns:
            Tuple of (agent_instance, data)
        """
        # Load or generate data (only once)
        if self._data is None:
            data_file = config.DATA_FILE
            if not Path(data_file).is_absolute():
                data_file = self.project_root / data_file
            data_path = Path(data_file)
            
            if data_path.exists():
                print(f"📂 Loading data from {data_file}...")
                with open(data_path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                print(f"   ✅ Loaded {len(self._data)} posts")
            else:
                print(f"📝 Generating mock dataset...")
                generator = MockXDataGenerator(seed=42)
                self._data = generator.generate_dataset(
                    num_posts=config.MOCK_DATA_SIZE,
                    include_threads=True
                )
                generator.save_to_file(data_file)
                print(f"   ✅ Generated {len(self._data)} posts")
        
        # If model_config provided, create new agent (for comparison)
        if model_config is not None:
            try:
                agent = AgenticResearchAgent(self._data, model_config=model_config)
                return agent, self._data
            except ValueError as e:
                print(f"❌ Error initializing agent with model_config: {e}")
                raise
        
        # Otherwise use cached agent
        if self._agent is None:
            try:
                self._agent = AgenticResearchAgent(self._data)
                print("✅ Agent initialized")
            except ValueError as e:
                print(f"❌ Error initializing agent: {e}")
                raise
        
        return self._agent, self._data
    
    def get_agent(self) -> Optional[AgenticResearchAgent]:
        """Get the current agent instance"""
        return self._agent
    
    def get_data(self) -> Optional[list]:
        """Get the current data"""
        return self._data
    
    def is_initialized(self) -> bool:
        """Check if agent is initialized"""
        return self._agent is not None
    
    def reset(self):
        """Reset agent and data (useful for testing)"""
        self._agent = None
        self._data = None
