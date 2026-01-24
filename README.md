# Grok Agentic Research Workflow

An autonomous multi-step agentic workflow using Grok as the central reasoner for complex research on simulated X (Twitter) data.

> 📖 **New to this project?** Check out the [Complete Beginner Guide](BEGINNER_GUIDE.md) for detailed explanations of data flow, optimizations, and step-by-step processes.

## 🎯 Overview

This system implements a fully autonomous research agent that can:
- **Plan**: Break down complex queries into actionable steps
- **Execute**: Retrieve relevant data using hybrid search (semantic + keyword)
- **Analyze**: Deep analysis of retrieved information
- **Refine**: Iteratively improve results when confidence is low
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

See [Deployment Guide](DEPLOYMENT.md#docker-deployment) for detailed Docker instructions.

## 📚 Documentation

- **[Beginner Guide](BEGINNER_GUIDE.md)**: Complete step-by-step walkthrough with data flow, optimizations, and detailed explanations
- **[Architecture](ARCHITECTURE.md)**: System architecture, design decisions, and component details
- **[API Documentation](API.md)**: API endpoints and usage examples
- **[Deployment Guide](DEPLOYMENT.md)**: Configuration, deployment, and troubleshooting

## 🔍 How It Works

1. **Planning**: Grok analyzes the query and creates a structured plan
2. **Execution**: Hybrid retrieval system searches through posts (semantic + keyword)
3. **Analysis**: Deep analysis identifies themes, sentiment, and confidence
4. **Evaluation**: Decides if replanning or refinement is needed
5. **Refinement**: Iteratively improves results when confidence is low
6. **Critique**: Checks for hallucinations and quality issues
7. **Summarization**: Generates final comprehensive summary

See [Beginner Guide](BEGINNER_GUIDE.md) for detailed explanations of each step.

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

See [Architecture](ARCHITECTURE.md) for more details on the evaluation framework.

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

See [Deployment Guide](DEPLOYMENT.md) for more troubleshooting tips.

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

See [Architecture](ARCHITECTURE.md) for detailed project structure.

## 🔐 Security Notes

- Never commit `.env` file with API keys
- Use environment variables in production
- Rotate API keys regularly
- Monitor token usage to avoid unexpected costs

---

**Built with ❤️ using Grok by xAI**
