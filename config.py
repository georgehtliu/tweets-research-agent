"""
Configuration for Grok Agentic Research Framework
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GROK_API_KEY = os.getenv("GROK_API_KEY")
# xAI API endpoint - check https://docs.x.ai for latest endpoint
# Common formats: "https://api.x.ai/v1" or "https://api.x.ai/openai/v1"
GROK_BASE_URL = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")

# Model Selection Strategy
# Based on Grok model capabilities:
# - grok-beta: General purpose, good reasoning (use for planning, analysis, refinement)
# - grok-beta: Can also be used for faster tasks (classification)
# Note: Adjust model names based on actual available models from xAI

class ModelConfig:
    """Model selection for different agent tasks"""
    
    # Primary reasoning model - best for complex planning and analysis
    PLANNER_MODEL = "grok-beta"  # Use strongest model for planning
    
    # Analysis model - needs deep reasoning
    ANALYZER_MODEL = "grok-beta"  # Use strongest model for analysis
    
    # Classification model - can use faster/cheaper model
    CLASSIFIER_MODEL = "grok-beta"  # Can use lighter model if available
    
    # Refinement model - needs reasoning
    REFINER_MODEL = "grok-beta"  # Use strong model for refinement
    
    # Summarization model - needs good reasoning
    SUMMARIZER_MODEL = "grok-beta"  # Use strong model for summaries

# Agent Configuration
MAX_ITERATIONS = 5  # Maximum refinement loops
MAX_CONTEXT_TOKENS = 8000  # Context window limit
TEMPERATURE = 0.7  # Default temperature for creativity
MAX_TOKENS_RESPONSE = 2000  # Max tokens per response

# Data Configuration
MOCK_DATA_SIZE = 100  # Number of mock posts to generate
DATA_FILE = "data/mock_x_data.json"

# Retrieval Configuration
SEMANTIC_SEARCH_TOP_K = 10  # Top K results for semantic search
KEYWORD_SEARCH_TOP_K = 10  # Top K results for keyword search
HYBRID_ALPHA = 0.6  # Weight for semantic vs keyword (0.6 = 60% semantic, 40% keyword)

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/agent_execution.log"
