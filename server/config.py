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
# - grok-4-fast-reasoning: Fast reasoning model with 2M context, $0.20/$0.50 per 1M tokens
# - Much cheaper than grok-3 ($3/$15) while maintaining strong reasoning capabilities
# - 15x larger context window (2M vs 131K) and faster throughput (4M tpm)

class ModelConfig:
    """Model selection for different agent tasks"""
    
    # Primary reasoning model - best for complex planning and analysis
    PLANNER_MODEL = "grok-4-fast-reasoning"  # Fast reasoning model for planning
    
    # Analysis model - needs deep reasoning
    ANALYZER_MODEL = "grok-4-fast-reasoning"  # Fast reasoning model for analysis
    
    # Classification model - can use faster/cheaper model
    CLASSIFIER_MODEL = "grok-4-fast-reasoning"  # Using same model for consistency
    
    # Refinement model - needs reasoning
    REFINER_MODEL = "grok-4-fast-reasoning"  # Fast reasoning model for refinement
    
    # Summarization model - needs good reasoning
    SUMMARIZER_MODEL = "grok-4-fast-reasoning"  # Fast reasoning model for summaries

# Agent Configuration
MAX_ITERATIONS = 2  # Maximum refinement loops (reduced from 3 for faster runs)
MAX_CONTEXT_TOKENS = 8000  # Context window limit
TEMPERATURE = 0.7  # Default temperature for creativity
MAX_TOKENS_RESPONSE = 1500  # Max tokens per response (reduced from 2000 for faster responses)
MAX_TOKENS_SUMMARY = 1200  # Max tokens for summary (shorter summaries = faster)

# Performance Optimization Flags
SKIP_EVALUATE_IF_HIGH_CONFIDENCE = True  # Skip evaluate step if confidence > 0.85
SKIP_CRITIQUE_IF_HIGH_CONFIDENCE = True  # Skip critique if confidence > 0.85 and no obvious issues
ENABLE_FAST_MODE = True  # Fast mode: skip evaluate and critique entirely (enabled for speed)

# Data Configuration
MOCK_DATA_SIZE = 100  # Number of mock posts to generate
# Data file path relative to project root
DATA_FILE = "data/mock_x_data.json"

# Retrieval Configuration
SEMANTIC_SEARCH_TOP_K = 8  # Top K results for semantic search (reduced from 10)
KEYWORD_SEARCH_TOP_K = 8  # Top K results for keyword search (reduced from 10)
HYBRID_ALPHA = 0.6  # Weight for semantic vs keyword (0.6 = 60% semantic, 40% keyword)
MAX_RETRIEVAL_RESULTS = 15  # Max results to return (reduced from 20)
ANALYZE_SAMPLE_SIZE = 6  # Number of items to show in analyze step (reduced from 10)
ANALYZE_TEXT_LENGTH = 150  # Max text length per item in analyze (reduced from 200)
CRITIQUE_SAMPLE_SIZE = 4  # Number of items to show in critique (reduced from 5)

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/agent_execution.log"
