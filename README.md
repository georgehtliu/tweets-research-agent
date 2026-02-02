# Grok Agentic Research Workflow

An autonomous multi-step agentic workflow using Grok as the central reasoner for complex research on simulated X (Twitter) data.

![Grok Research Agent demo](grok-research.gif)

## 🎯 Overview

This system implements a fully autonomous research agent that can:
- **Plan**: Break down complex queries into actionable steps
- **Execute**: Retrieve relevant data using hybrid search (semantic + keyword)
- **Validate**: Check result relevance and quality before analysis
- **Analyze**: Deep analysis of retrieved information
- **Evaluate**: Determine if replanning or refinement is needed
- **Refine**: Iteratively improve results when confidence is low (with stagnation detection)
- **Critique**: Check for hallucinations and quality issues
- **Summarize**: Generate comprehensive final summaries

The agent handles various query types: trend analysis, information extraction, comparative analysis, temporal analysis, sentiment analysis, and more.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Grok API key from [console.x.ai](https://console.x.ai)
- Use promo code: `grok_eng_b4d86a51` for $20 free credits

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Grok-takehome
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your GROK_API_KEY
```

4. **Generate mock data** (optional - will auto-generate on first run)
```bash
cd server
python data_generator.py
```

### Usage

#### Web UI (Recommended)
Start the API server:
```bash
python server/api_server.py
```

Then open your browser to:
```
http://localhost:8080
```

The web interface provides:
- Simple query input with submit button
- Example queries to try
- Real-time results display
- Model comparison interface
- Tweets browsing page

#### CLI Mode

**Interactive Mode:**
```bash
python server/main.py
```

**Single Query Mode:**
```bash
python server/main.py --query "What are people saying about AI?"
```

#### Docker Deployment

**Quick Start:**
```bash
# Create .env file with your GROK_API_KEY
cp .env.example .env

# Start with Docker Compose
docker-compose up
```

## 📚 Documentation

### Architecture
The system uses a state machine pattern with autonomous decision-making. Components include a FastAPI server, AgenticResearchAgent (state machine orchestrator), HybridRetriever (semantic + keyword search), ToolRegistry (dynamic tool calling), ContextManager (execution tracking), and GrokClient (API interface). The workflow progresses through states: PLAN → EXECUTE → VALIDATE_RESULTS → ANALYZE → EVALUATE → REFINE → CRITIQUE → SUMMARIZE.

### Beginner Guide
The system excels at sentiment analysis, time range queries, multi-language support, author-based analysis, category-specific queries, and complex multi-step queries. It uses hybrid retrieval (semantic + keyword search), supports both plan-based and dynamic tool-calling execution modes, and includes optimizations like embedding caching, confidence tracking with stagnation detection, and result validation gates.

### API
Main endpoints: `POST /api/query` (submit query, receive SSE stream), `POST /api/query/compare-models` (parallel model comparison), `GET /api/tweets` (paginated tweet browsing), `GET /api/health` (health check). The query endpoint streams progress events (planning, executing, analyzing, etc.) via Server-Sent Events. Interactive API docs available at `/docs` (Swagger) and `/redoc` (ReDoc).

### Deployment
Configure via `server/config.py` (model selection, retrieval settings, agent parameters). Docker deployment: create `.env` with `GROK_API_KEY`, run `docker-compose up`. Supports volume mounts for data persistence, health checks, and production considerations (security, scaling, monitoring). Uses `grok-4-fast-reasoning` model for optimal cost/performance balance (45x cheaper than grok-3 with 2M token context).

## 🔍 How It Works

1. **Planning**: Grok analyzes the query and creates a structured plan
2. **Execution**: Hybrid retrieval system searches through posts (semantic + keyword)
3. **Validation**: Validates result relevance and quality before analysis (prevents analyzing irrelevant data)
4. **Analysis**: Deep analysis identifies themes, sentiment, and confidence
5. **Evaluation**: Decides if replanning or refinement is needed (checks both confidence and data quality)
6. **Refinement**: Iteratively improves results when confidence is low (tracks confidence improvement to prevent loops)
7. **Critique**: Checks for hallucinations and quality issues (skipped only when high confidence AND good data quality)
8. **Summarization**: Generates final comprehensive summary

**Accuracy Improvements**: The system includes result validation gates, confidence tracking with stagnation detection, and improved skip logic to ensure high-quality results while maintaining efficiency.

## 📊 Example Queries

- **Trend Analysis**: "What are people saying about AI safety?"
- **Information Extraction**: "Find all posts mentioning GPT-4 from verified accounts"
- **Comparative Analysis**: "Compare discussions about Python vs JavaScript"
- **Temporal Analysis**: "How has sentiment about remote work changed over time?"

## 🧪 Testing & Evaluation

### Run Example Queries
```bash
python server/main.py --query "What are people saying about AI?"
```

### Batch Evaluation
```bash
cd server/evaluation
python evaluator.py --max-queries 10
```

### Model Comparison
```bash
python server/evaluation/compare_models.py --max-queries 5
```


## 🐛 Troubleshooting

### API Key Issues
Set `GROK_API_KEY` in `.env` file or environment variable

### API Errors
- Check your API key is valid
- Verify you have credits in your xAI account
- Check rate limits
- Verify model names match available models

### No Results Found
- Check your mock data file exists
- Verify data format matches expected structure
- Try broader search terms


## 📁 Project Structure

```
Grok-takehome/
├── server/              # Server-side code
│   ├── agent.py         # Core agentic workflow (state machine)
│   ├── retrieval.py     # Hybrid retrieval system
│   ├── tools.py         # Tool registry and definitions
│   ├── routes/          # API route handlers
│   └── evaluation/      # Evaluation framework
├── client/              # Client-side code
│   └── static/          # Web UI files
├── data/                # Generated mock data
└── docs/                # Documentation files
```


## 🔐 Security Notes

- Never commit `.env` file with API keys
- Use environment variables in production
- Rotate API keys regularly
- Monitor token usage to avoid unexpected costs

---

**Built with ❤️ using Grok by xAI**
