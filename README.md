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
│  Grok Planner   │ ← Uses grok-beta for complex reasoning
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
│  Grok Analyzer  │ ← Deep analysis with grok-beta
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
│  Summarizer     │ ← Final summary with grok-beta
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
python data_generator.py
```

### Usage

#### Interactive Mode
```bash
python main.py
```

Then enter your query when prompted:
```
💬 Enter your research query: What are people saying about AI safety?
```

#### Single Query Mode
```bash
python main.py --query "What are the main trends in tech discussions?"
```

#### With Custom Data
```bash
python main.py --query "Your question" --data path/to/data.json
```

## 📁 Project Structure

```
Grok-takehome/
├── main.py                 # Main entry point and CLI
├── agent.py                # Core agentic workflow
├── grok_client.py          # Grok API client
├── retrieval.py            # Hybrid retrieval system
├── context_manager.py      # Context and execution tracking
├── data_generator.py       # Mock X data generator
├── config.py               # Configuration settings
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

- **Planning & Analysis**: `grok-beta` (strongest reasoning)
- **Classification**: `grok-beta` (can use lighter model if available)
- **Refinement**: `grok-beta` (needs good reasoning)
- **Summarization**: `grok-beta` (high-quality summaries)

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

### Why grok-beta for Planning?
Planning requires complex reasoning to break down queries. The strongest model ensures high-quality plans.

### Why grok-beta for Analysis?
Deep analysis needs sophisticated reasoning to identify patterns and insights.

### Why grok-beta for Refinement?
Refinement decisions require understanding context and determining optimal next steps.

### Why grok-beta for Summarization?
High-quality summaries need strong language understanding and synthesis capabilities.

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
