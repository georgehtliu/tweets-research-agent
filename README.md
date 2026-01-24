# Grok Agentic Research Workflow

An autonomous multi-step agentic workflow using Grok as the central reasoner for complex research on simulated X (Twitter) data.

## 🎯 Overview

This system implements a fully autonomous research agent that can:
- **Plan**: Break down complex queries into actionable steps
- **Execute**: Retrieve relevant data using hybrid search (semantic + keyword)
- **Analyze**: Deep analysis of retrieved information
- **Refine**: Iteratively improve results when confidence is low
- **Summarize**: Generate comprehensive final summaries

The agent handles various query types:
- Trend analysis
- Information extraction
- Comparative analysis
- Temporal analysis
- Sentiment analysis
- And more...

## 🏗️ Architecture

```
User Query
    ↓
┌─────────────────┐
│  Grok Planner   │ ← Uses grok-4-fast-reasoning for complex reasoning
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Query Classifier│ ← Classifies query type
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Hybrid Retriever│ ← Semantic + Keyword search
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Grok Analyzer  │ ← Deep analysis with grok-4-fast-reasoning
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Refiner       │ ← Decides if refinement needed
└────────┬────────┘
         │
    ┌────┴────┐
    │ Refine? │
    └────┬────┘
    Yes  │  No
    └────┴────┐
         │
         ▼
┌─────────────────┐
│  Summarizer     │ ← Final summary with grok-4-fast-reasoning
└─────────────────┘
```

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
cd server
python api_server.py
```

Or from project root:
```bash
python server/api_server.py
```

Then open your browser to:
```
http://localhost:8080
```

**Important**: Always access the UI through the server URL (`http://localhost:8080`), not by opening the HTML file directly. The server serves the frontend and handles API requests.

(You can change the port by setting the `PORT` environment variable)

The web interface provides:
- Simple query input with submit button
- Example queries to try
- Real-time results display
- Beautiful, responsive UI

#### CLI Mode

**Interactive Mode:**
```bash
cd server
python main.py
```

Or from project root:
```bash
python server/main.py
```

Then enter your query when prompted:
```
💬 Enter your research query: What are people saying about AI safety?
```

**Single Query Mode:**
```bash
cd server
python main.py --query "What are the main trends in tech discussions?"
```

**With Custom Data:**
```bash
cd server
python main.py --query "Your question" --data path/to/data.json
```

#### API Endpoints

The API server provides REST endpoints:

- `GET /` - Web UI
- `POST /api/query` - Submit research query
  ```json
  {
    "query": "What are people saying about AI?"
  }
  ```
- `GET /api/health` - Health check
- `GET /api/examples` - Get example queries

## 📁 Project Structure

```
Grok-takehome/
├── server/                 # Server-side code
│   ├── api_server.py       # Flask API server
│   ├── main.py             # CLI entry point
│   ├── agent.py            # Core agentic workflow
│   ├── grok_client.py      # Grok API client
│   ├── retrieval.py        # Hybrid retrieval system
│   ├── context_manager.py  # Context and execution tracking
│   ├── data_generator.py   # Mock X data generator
│   └── config.py           # Configuration settings
├── client/                 # Client-side code
│   └── static/            # Web UI files
│       ├── index.html      # Main HTML page
│       ├── style.css       # Styles
│       └── script.js       # Frontend JavaScript
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── README.md               # This file
├── data/                   # Generated mock data
│   └── mock_x_data.json
└── output/                 # Research results
    └── research_result.json
```

## 🔧 Configuration

Edit `config.py` to customize:

- **Model Selection**: Choose which Grok models to use for each task
- **Retrieval Settings**: Adjust hybrid search weights, top-k results
- **Agent Settings**: Max iterations, context limits, temperature
- **Data Settings**: Mock data size, file paths

### Model Selection Strategy

The framework uses different Grok models for different tasks:

- **Planning & Analysis**: `grok-4-fast-reasoning` (fast reasoning, 2M context, $0.20/$0.50)
- **Classification**: `grok-4-fast-reasoning` (consistent model)
- **Refinement**: `grok-4-fast-reasoning` (fast reasoning)
- **Summarization**: `grok-4-fast-reasoning` (high-quality summaries)

*Note: Adjust model names in `config.py` based on available models from xAI*

## 📊 Example Queries

The agent can handle diverse query types:

### Trend Analysis
```
"What are people saying about AI safety?"
"What topics are trending in tech discussions?"
```

### Information Extraction
```
"Find all posts mentioning GPT-4 from verified accounts"
"What are the most liked posts about climate change?"
```

### Comparative Analysis
```
"Compare discussions about Python vs JavaScript"
"What's the difference in sentiment between crypto and traditional finance?"
```

### Temporal Analysis
```
"How has sentiment about remote work changed over time?"
"What were the peak discussion topics last week?"
```

## 🔍 How It Works

### 1. Planning Phase
Grok analyzes the query and creates a structured plan:
- Classifies query type
- Identifies required tools
- Defines success criteria
- Estimates complexity

### 2. Execution Phase
Hybrid retrieval system:
- **Semantic Search**: Uses sentence transformers for meaning-based search
- **Keyword Search**: Traditional keyword matching with TF-IDF-like scoring
- **Hybrid**: Combines both methods with configurable weights

### 3. Analysis Phase
Grok performs deep analysis:
- Identifies main themes
- Extracts key insights
- Analyzes sentiment distribution
- Evaluates data quality
- Assigns confidence score

### 4. Refinement Phase
If confidence is low (< 0.8), Grok decides:
- Whether refinement is needed
- What additional steps to take
- Expected confidence improvement

The agent iteratively refines until confidence is sufficient or max iterations reached.

### 5. Summarization Phase
Grok generates final comprehensive summary:
- Executive summary
- Key findings
- Detailed analysis
- Limitations
- Recommendations

## 🧪 Testing

Run example queries:
```bash
# Test trend analysis
python main.py --query "What are people saying about AI?"

# Test information extraction
python main.py --query "Find posts about Python from verified accounts"

# Test comparison
python main.py --query "Compare sentiment about crypto vs stocks"
```

## 📈 Evaluation Metrics

The system tracks:
- **Completion Rate**: % of queries successfully completed
- **Step Efficiency**: Number of steps per query
- **Confidence Scores**: Final confidence in results
- **Token Usage**: Total tokens consumed
- **Refinement Iterations**: How many refinement loops needed

Results are saved to `output/research_result.json` with full execution details.

## 🐛 Troubleshooting

### API Key Issues
```
Error: GROK_API_KEY not found
```
**Solution**: Set `GROK_API_KEY` in `.env` file or environment variable

### API Errors
```
❌ Grok API Error: ...
```
**Solutions**:
- Check your API key is valid
- Verify you have credits in your xAI account
- Check rate limits
- Verify model names match available models

### No Results Found
If retrieval returns no results:
- Check your mock data file exists
- Verify data format matches expected structure
- Try broader search terms

### Low Confidence
If confidence scores are consistently low:
- Increase mock data size
- Adjust hybrid search weights
- Increase max refinement iterations
- Check data quality

## 🔐 Security Notes

- Never commit `.env` file with API keys
- Use environment variables in production
- Rotate API keys regularly
- Monitor token usage to avoid unexpected costs

## 📝 Model Selection Rationale

### Why grok-4-fast-reasoning for Planning?
Planning requires complex reasoning to break down queries. `grok-4-fast-reasoning` provides strong reasoning at 45x lower cost than `grok-3` ($0.20/$0.50 vs $3/$15 per 1M tokens) with a 15x larger context window (2M vs 131K tokens).

### Why grok-4-fast-reasoning for Analysis?
Deep analysis needs sophisticated reasoning to identify patterns and insights. The fast reasoning model maintains quality while significantly reducing costs.

### Why grok-4-fast-reasoning for Refinement?
Refinement decisions require understanding context and determining optimal next steps. The larger context window (2M tokens) allows for better context management.

### Why grok-4-fast-reasoning for Summarization?
High-quality summaries need strong language understanding and synthesis capabilities. The fast reasoning model provides excellent quality at a fraction of the cost.

**Note**: The framework uses `grok-4-fast-reasoning` for optimal cost/performance balance. It's 45x cheaper than `grok-3` while maintaining strong reasoning capabilities.

*Note: If lighter/faster models are available, you can use them for classification tasks to reduce costs.*

## 🚢 Deployment

### Docker (Coming Soon)
```bash
docker build -t grok-agent .
docker run -e GROK_API_KEY=your_key grok-agent
```

### Docker Compose (Coming Soon)
```bash
docker-compose up
```

## 📄 License

This project is created for the Grok engineering assessment.

## 🤝 Contributing

This is an assessment project. For questions or issues, contact the assessment team.

## 📧 Contact

For questions about this assessment:
- Payton: payton@x.ai
- Ideshpande: ideshpande@x.ai

---

**Built with ❤️ using Grok by xAI**
