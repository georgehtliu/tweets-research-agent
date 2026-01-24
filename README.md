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

## 🏗️ Architecture Overview

### System Architecture

The system follows a **state machine pattern** with autonomous decision-making capabilities:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Query Input                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │   State Machine       │
            │   Orchestrator        │
            └───────────┬───────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   PLAN       │ │   EXECUTE    │ │   ANALYZE    │
│              │ │              │ │              │
│ - Decompose  │ │ - Tool Call  │ │ - Extract    │
│ - Classify   │ │ - Hybrid     │ │   Themes     │
│ - Select     │ │   Search     │ │ - Sentiment  │
│   Tools      │ │ - Filter     │ │ - Confidence │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                 │
       └────────────────┼─────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │     EVALUATE          │
            │  (Replan Decision)    │
            └───────────┬───────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
        Replan?                  No
            │                       │
            ▼                       ▼
    ┌──────────────┐      ┌──────────────┐
    │   REFINE     │      │   CRITIQUE   │
    │              │      │              │
    │ - Iterative  │      │ - Hallucin.  │
    │   Improve    │      │   Check      │
    │ - Expand     │      │ - Bias Check │
    │   Search     │      │ - Quality    │
    └──────┬───────┘      └──────┬───────┘
           │                     │
           └──────────┬──────────┘
                      │
                      ▼
            ┌───────────────────────┐
            │    SUMMARIZE          │
            │                       │
            │ - Executive Summary   │
            │ - Key Findings        │
            │ - Detailed Analysis   │
            └───────────────────────┘
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Web UI)                      │
│  - React-like vanilla JS                                    │
│  - Server-Sent Events (SSE) for real-time updates           │
│  - Model comparison interface                               │
│  - Tweets browsing page                                     │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/SSE
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Server                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Query Routes │  │ Eval Routes  │  │ Main Routes  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │              │
│         └─────────────────┼──────────────────┘              │
│                           │                                  │
│                           ▼                                  │
│              ┌───────────────────────┐                      │
│              │   Agent Service       │                      │
│              │  (Singleton Pattern)  │                      │
│              └───────────┬───────────┘                      │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              AgenticResearchAgent (State Machine)            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Context      │  │ Hybrid       │  │ Tool        │     │
│  │ Manager      │  │ Retriever    │  │ Registry    │     │
│  │              │  │              │  │             │     │
│  │ - History    │  │ - Semantic   │  │ - Keyword   │     │
│  │ - Steps      │  │   Search     │  │   Search    │     │
│  │ - Tokens     │  │ - Keyword    │  │ - Temporal   │     │
│  └──────────────┘  │   Search     │  │ - Profile    │     │
│                    │ - Hybrid     │  │ - Filter     │     │
│                    └──────┬───────┘  └──────┬───────┘     │
│                           │                 │              │
│                           └────────┬────────┘              │
│                                    │                       │
│                                    ▼                       │
│                          ┌──────────────┐                 │
│                          │ Grok Client  │                 │
│                          │              │                 │
│                          │ - API Calls  │                 │
│                          │ - Streaming  │                 │
│                          │ - Tool Call  │                 │
│                          └──────┬───────┘                 │
└─────────────────────────────────┼──────────────────────────┘
                                  │
                                  ▼
                        ┌──────────────────┐
                        │   Grok API      │
                        │  (xAI Console)   │
                        └──────────────────┘
```

## 🎨 Major Design Decisions

### 1. **State Machine Pattern for Workflow Orchestration**

**Decision**: Implemented a state machine with explicit state transitions rather than a linear pipeline.

**Rationale**:
- **Autonomy**: Enables the agent to make dynamic decisions (e.g., replanning when analysis reveals insufficient data)
- **Flexibility**: Supports conditional state transitions (e.g., `ANALYZE → EVALUATE → PLAN` if replan needed)
- **Clarity**: Makes the workflow explicit and debuggable
- **Extensibility**: Easy to add new states (e.g., `CRITIQUE` state for quality checks)

**Implementation**: `WorkflowState` enum with state transition logic in `run_workflow()` method.

### 2. **Hybrid Retrieval System**

**Decision**: Combined semantic search (embeddings) with keyword search rather than using either alone.

**Rationale**:
- **Robustness**: Semantic search handles conceptual queries; keyword search handles exact matches
- **Performance**: Keyword search is fast for specific terms; semantic search finds related content
- **Coverage**: Handles both "find posts about AI safety" (semantic) and "find posts with #Python" (keyword)
- **Fallback**: If embeddings fail, keyword search still works

**Implementation**: `HybridRetriever` combines cosine similarity (semantic) with TF-IDF-like scoring (keyword), weighted by `config.HYBRID_SEMANTIC_WEIGHT`.

### 3. **Dynamic Tool Calling**

**Decision**: Implemented OpenAI-style function calling for iterative tool selection, with a fallback to plan-based execution.

**Rationale**:
- **Adaptability**: Complex queries benefit from iterative tool selection based on intermediate results
- **Efficiency**: Simple queries use faster plan-based execution (no tool-calling overhead)
- **Autonomy**: Agent decides which tools to use based on context, not hardcoded logic
- **Extensibility**: Easy to add new tools without changing core workflow

**Implementation**: `ToolRegistry` provides tool definitions; planner decides `use_tool_calling` flag; `execute_with_tool_calling()` implements iterative loop.

### 4. **Context Management with Token Limits**

**Decision**: Implemented `ContextManager` to track execution history and manage context size.

**Rationale**:
- **Memory Efficiency**: Prevents context overflow by truncating old steps
- **Traceability**: Maintains execution history for debugging and analysis
- **Cost Control**: Tracks token usage to monitor API costs
- **Quality**: Preserves recent context while summarizing older steps

**Implementation**: `ContextManager` tracks `ExecutionStep` objects, truncates when approaching `MAX_CONTEXT_TOKENS`, uses `create_concise_data_summary()` for compression.

### 5. **Model Selection Strategy**

**Decision**: Use `grok-4-fast-reasoning` for all reasoning tasks rather than mixing models.

**Rationale**:
- **Cost Efficiency**: 45x cheaper than `grok-3` ($0.20/$0.50 vs $3/$15 per 1M tokens)
- **Large Context**: 2M token context window (vs 131K) enables better context management
- **Consistency**: Same model ensures consistent behavior across stages
- **Simplicity**: Easier configuration and maintenance

**Trade-off**: Could use lighter models for classification, but current approach prioritizes quality and simplicity.

**Implementation**: `ModelConfig` in `config.py` with `model_config` override support for model comparison.

### 6. **Fast Mode for Latency Reduction**

**Decision**: Added `fast_mode` flag to skip `EVALUATE` and `CRITIQUE` states for faster execution.

**Rationale**:
- **User Control**: Users can choose speed vs. quality trade-off
- **Use Cases**: Fast mode suitable for exploratory queries; full mode for production
- **Flexibility**: Can be enabled per-query or globally via config

**Implementation**: `fast_mode` parameter in `run_workflow()` skips `evaluate()` and `critique()` calls.

### 7. **Progress Callback System**

**Decision**: Implemented callback-based progress reporting for real-time UI updates.

**Rationale**:
- **User Experience**: Provides real-time feedback during long-running queries
- **Debugging**: Helps identify bottlenecks in the workflow
- **Flexibility**: Works for both CLI (print) and Web UI (SSE streaming)

**Implementation**: `progress_callback(event_type, data)` called at each workflow step; Web UI uses Server-Sent Events (SSE) for streaming.

### 8. **Modular Router Architecture**

**Decision**: Separated routes into `query_router`, `evaluation_router`, and `main_router`.

**Rationale**:
- **Separation of Concerns**: Each router handles a specific domain
- **Maintainability**: Easy to find and modify route handlers
- **Scalability**: Can add new routers without cluttering main app
- **Testing**: Each router can be tested independently

**Implementation**: FastAPI routers with prefixes (`/api` for query/eval, `/` for main).

### 9. **Embedding Caching**

**Decision**: Cache embeddings on disk to avoid recomputing for the same dataset.

**Rationale**:
- **Performance**: Embeddings are expensive to compute; caching saves time on subsequent runs
- **Cost**: Reduces CPU usage
- **Stability**: Uses data hash to detect dataset changes

**Implementation**: `HybridRetriever._load_or_build_embeddings()` checks cache directory; invalidates on data change.

### 10. **Parallel Model Comparison**

**Decision**: Run multiple models in parallel for comparison rather than sequentially.

**Rationale**:
- **Speed**: Parallel execution reduces total time
- **Fairness**: All models see the same query simultaneously
- **User Experience**: Faster results for comparison

**Implementation**: `ThreadPoolExecutor` in `/api/query/compare-models` endpoint; progress events streamed via queues.

### 11. **Error Handling and Resilience**

**Decision**: Comprehensive error handling with graceful degradation.

**Rationale**:
- **Reliability**: System continues operating even if components fail
- **User Experience**: Clear error messages instead of crashes
- **Debugging**: Detailed error logging for troubleshooting

**Implementation**: Try-catch blocks at critical points; fallback to keyword-only search if embeddings fail; division-by-zero guards in calculations.

### 12. **Mock Data Generation**

**Decision**: Generate diverse, realistic mock X data with multiple categories, languages, and edge cases.

**Rationale**:
- **Testing**: Enables testing without real API access
- **Diversity**: Covers various query types (trends, sentiment, multilingual, etc.)
- **Realism**: Includes verified accounts, engagement metrics, threads, etc.

**Implementation**: `MockXDataGenerator` with category-specific templates, foreign language support, and celebrity names.

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

The API server provides REST endpoints (FastAPI):

- `GET /` - Web UI
- `POST /api/query` - Submit research query (returns SSE stream)
  ```json
  {
    "query": "What are people saying about AI?"
  }
  ```
- `GET /api/health` - Health check
- `GET /api/examples` - Get example queries
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## 📁 Project Structure

```
Grok-takehome/
├── server/                      # Server-side code
│   ├── api_server.py            # FastAPI server entry point
│   ├── main.py                  # CLI entry point
│   ├── app.py                   # FastAPI app factory
│   ├── agent.py                 # Core agentic workflow (state machine)
│   ├── grok_client.py           # Grok API client with tool calling
│   ├── retrieval.py             # Hybrid retrieval system (semantic + keyword)
│   ├── context_manager.py       # Context and execution tracking
│   ├── data_generator.py        # Mock X data generator
│   ├── config.py                # Configuration settings
│   ├── tools.py                 # Tool registry and definitions
│   ├── routes/                  # API route handlers
│   │   ├── __init__.py          # Router definitions
│   │   ├── main.py              # Main routes (health, static files)
│   │   ├── query.py             # Query endpoints (single, compare-models)
│   │   └── evaluation.py        # Evaluation endpoints
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   └── agent_service.py     # Agent lifecycle management
│   ├── utils/                   # Utility modules
│   │   ├── __init__.py
│   │   ├── errors.py            # Error handling
│   │   ├── response.py          # Response formatting
│   │   └── truncation.py        # Text truncation utilities
│   └── evaluation/              # Evaluation framework
│       ├── evaluator.py         # Batch evaluation runner
│       ├── compare_models.py    # Model comparison script
│       ├── metrics.py           # Metrics collection
│       ├── test_queries.json    # Test query suite (40 queries)
│       └── results/             # Evaluation results output
├── client/                      # Client-side code
│   └── static/                  # Web UI files
│       ├── index.html           # Main query interface
│       ├── tweets.html         # Tweets browsing page
│       ├── style.css            # Styles
│       └── script.js            # Frontend JavaScript
├── data/                        # Generated mock data
│   ├── mock_x_data.json        # Main dataset (~3800 posts)
│   └── .embeddings_cache/      # Cached embeddings
├── output/                      # Research results
│   └── research_result.json
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose configuration
└── README.md                    # This file
```

### Key Components

- **`agent.py`**: Implements the state machine workflow with autonomous decision-making
- **`retrieval.py`**: Hybrid search combining semantic (embeddings) and keyword matching
- **`tools.py`**: Dynamic tool calling system (keyword_search, semantic_search, hybrid_search, user_profile_lookup, temporal_trend_analyzer, filter_by_metadata)
- **`context_manager.py`**: Manages conversation history and token limits
- **`grok_client.py`**: Handles Grok API calls with streaming and tool calling support
- **`routes/query.py`**: API endpoints for single queries and parallel model comparison
- **`client/static/`**: Web UI with real-time progress updates via Server-Sent Events

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

## 📐 Data Flow and Tool Calls

### End-to-end data flow

```
┌─────────────┐     POST /api/query      ┌─────────────────┐     progress_callback     ┌──────────────┐
│   Web UI    │ ───────────────────────► │  FastAPI        │ ◄──────────────────────── │   Agent      │
│  (script.js)│                          │  routes/query   │      (event_type, data)   │  (agent.py)  │
└─────────────┘                          └────────┬────────┘                           └──────┬───────┘
       │                                           │                                            │
       │  SSE stream (data: {...}\n\n)              │  run_workflow(query)                      │
       │ ◄─────────────────────────────────────────┤                                            │
       │                                           │  AgentService.get_agent()                 │
       │                                           └──────────────────────────────────────────►│
       │                                                                                       │
       │                                                                     ┌─────────────────┴─────────────────┐
       │                                                                     │  State machine: PLAN → EXECUTE →   │
       │                                                                     │  ANALYZE → EVALUATE → REFINE /     │
       │                                                                     │  CRITIQUE → SUMMARIZE → COMPLETE   │
       │                                                                     └─────────────────┬─────────────────┘
       │                                                                                       │
       │                                                                     Plan-based        │ Dynamic tool
       │                                                                     (retriever only)  │ calling (Grok API
       │                                                                           │          │ + ToolRegistry)
       │                                                                           ▼          ▼
       │                                                                     ┌──────────┐  ┌──────────────┐
       │                                                                     │Hybrid    │  │ Grok API     │
       │                                                                     │Retriever │  │ (tools=...)  │
       │                                                                     │tools.py  │  │ tools.py     │
       │                                                                     └──────────┘  └──────────────┘
```

1. **Request**: User submits a query via the Web UI → `POST /api/query` (or `/api/query/compare-models` for multi-model).
2. **Orchestration**: The route starts `run_workflow` in a background thread and sets `agent.progress_callback` to push events into a queue.
3. **Streaming**: A generator consumes the queue and emits Server-Sent Events (`data: {"type": "...", ...}\n\n`) to the client. The UI updates logs and progress in real time from these events.
4. **Execution**: The agent runs the state machine. **Execute** either uses **plan-based** retrieval (see below) or **dynamic tool calling** (Grok selects tools iteratively).
5. **Response**: When the workflow reaches `COMPLETE`, the final result (summary, findings, etc.) is sent as the last SSE payload (or in the compare-models response). The UI displays it in the Summary tab.

### Two execution modes

| **Aspect** | **Plan-based execution** | **Dynamic tool calling** |
|---|---|---|
| **When** | Default. Used when `use_tool_calling=false` or when the plan is “simple” (e.g. low complexity, ≤2 steps, info_extraction/sentiment). | Used only when the planner sets `use_tool_calling=true` *and* the plan is not overridden as simple. |
| **Who drives** | The plan’s `steps` (from `plan()`). The agent loops over steps and calls the retriever directly. | Grok API. The model chooses tools per turn; the agent runs them and appends results to the conversation. |
| **Tools** | `hybrid_search`, `keyword_search`, `filter_by_metadata` via `HybridRetriever` / `retrieval` (no Grok tool-calling). | All tools in `ToolRegistry`: see below. |
| **Progress** | `executing` events with `status: started | completed`, `results_count`. No `tool_calls` / `tool_calling_mode`. | Same, plus `tool_calling_mode: true`, `tool_calls` (list of `{name, args, success, ...}`), and per-call “Calling tool: X” / “Completed N tool call(s)” messages. |
| **Logs** | “Retrieving relevant data…” → “Retrieved N items”. No “Tools used” section. | “Starting dynamic tool calling…” → “Calling tool: X” / “Completed N tool call(s)” → “Tool calling finished. Retrieved N results”. “Tools used” appears in the Logs tab when `tool_calls` is present. |

Simple multi-step queries (e.g. “Summarize sentiment on crypto”) typically use **plan-based** execution, so you will not see tool-call entries in the logs. To see **tool calling** in the UI, use **complex, multi-step** prompts (e.g. “Compare sentiment about crypto vs traditional finance, then filter by verified accounts, then show how it changed over the last 7 days” or “What do verified accounts say about sports? Filter by high engagement.”).

### Available tools (`tools.py`)

Used in **dynamic tool calling**; in **plan-based** mode, only the retriever-based logic (hybrid/keyword/filter) is used.

| Tool | Purpose |
|------|--------|
| `keyword_search` | Keyword/phrase matching. Good for exact terms, hashtags. |
| `semantic_search` | Embedding-based similarity. Good for concepts and paraphrases. |
| `hybrid_search` | Combines keyword + semantic. Default search in tool-calling mode. |
| `user_profile_lookup` | Posts by author (name/id). Optional `verified_only`. |
| `temporal_trend_analyzer` | Time-windowed analysis (e.g. `days_back`, date range). |
| `filter_by_metadata` | Filter by sentiment, `min_engagement`, `verified_only`, category, language, etc. |

`ToolRegistry` holds tool definitions (OpenAI-style function schema), implements `run_tool(name, arguments)`, and uses `HybridRetriever` and the full dataset for search/filter operations.

### Tool-calling loop (dynamic mode only)

1. Agent sends the research query to Grok with `tools` and `tool_choice="auto"`.
2. Grok returns either a text reply or `tool_calls` (or both).
3. If there are no `tool_calls`, the loop ends; aggregated results are passed to **Analyze**.
4. Otherwise, for each `tool_call`:
   - `ToolRegistry.run_tool(name, arguments)` is invoked.
   - Results are appended to the conversation as tool messages.
   - Progress is emitted (`tool_calling`, `tool_calls` history) so the UI can show “Calling tool: X” and “Tools used”.
5. The updated `messages` are sent back to Grok; repeat until no more `tool_calls` or `max_tool_calls` is reached.

After the loop, the final flattened result list is fed into **Analyze** → **Evaluate** → **Refine** / **Critique** → **Summarize** exactly as in plan-based execution.

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

## 📈 Evaluation Framework

The system includes a comprehensive evaluation framework for testing agent performance across multiple queries and comparing different Grok models.

### Quick Start

**Run batch evaluation:**
```bash
cd server/evaluation
python evaluator.py --max-queries 10
```

**Compare models:**
```bash
python compare_models.py --max-queries 5
```

### Features

- **40 Test Queries**: Diverse queries covering trend analysis, info extraction, comparison, temporal analysis, sentiment, edge cases, and more
- **Metrics Collection**: 
  - Completion rate (% successfully completed)
  - Step efficiency (avg steps, refinement iterations, replan count)
  - Summary quality (confidence scores, summary length)
  - Autonomy metrics (replan rate, refinement rate, critique pass rate)
- **Model Comparison**: Compare performance across different Grok model variants
- **Category Breakdown**: Metrics broken down by query category and complexity level

### Test Query Suite

The `server/evaluation/test_queries.json` contains 40 queries:
- **Categories**: trend_analysis, info_extraction, comparison, temporal, sentiment, complex, edge_case, multilingual, specific, broad, filtering, synthesis, etc.
- **Complexity**: low (4), medium (18), high (18)
- **Edge Cases**: sarcasm detection, ambiguity resolution, conflicting sources, threaded discussions

### Metrics Tracked

- **Completion Rate**: % of queries successfully completed
- **Step Efficiency**: Number of steps per query, refinement iterations, replan cycles
- **Confidence Scores**: Final confidence in results, high confidence rate
- **Token Usage**: Total tokens consumed per query
- **Autonomy Score**: How well agent handles queries independently (0-1 scale)

Results are saved to `server/evaluation/results/` with detailed metrics and individual query results.

See `server/evaluation/README.md` for detailed documentation.

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
