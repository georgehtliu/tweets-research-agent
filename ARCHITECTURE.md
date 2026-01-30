# Architecture & Design Decisions

> 📖 **New to this project?** Start with the [Beginner Guide](BEGINNER_GUIDE.md) for a step-by-step walkthrough.

## 🏗️ System Architecture

### State Machine Pattern

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
│   PLAN       │ │   EXECUTE    │ │ VALIDATE_    │
│              │ │              │ │   RESULTS     │
│ - Decompose  │ │ - Tool Call  │ │              │
│ - Classify   │ │ - Hybrid     │ │ - Relevance   │
│ - Select     │ │   Search     │ │   Check      │
│   Tools      │ │ - Filter     │ │ - Quality    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                 │
       │                └────────┬────────┘
       │                         │
       │                         ▼
       │            ┌───────────────────────┐
       │            │     ANALYZE           │
       │            │                       │
       │            │ - Extract Themes       │
       │            │ - Sentiment Analysis   │
       │            │ - Confidence Score    │
       │            └───────────┬───────────┘
       │                        │
       └────────────────────────┼───────────────┐
                                │               │
                                ▼               │
                    ┌───────────────────────┐   │
                    │     EVALUATE          │   │
                    │  (Replan Decision)    │   │
                    └───────────┬───────────┘   │
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
- **Extensibility**: Easy to add new states (e.g., `VALIDATE_RESULTS` for quality checks, `CRITIQUE` for hallucination detection)

**State Transitions**:
- `PLAN → EXECUTE`: Initial planning complete
- `EXECUTE → VALIDATE_RESULTS`: Results retrieved, validate quality before analysis
- `VALIDATE_RESULTS → ANALYZE`: Results validated, proceed to analysis
- `VALIDATE_RESULTS → REFINE/REPLAN`: Low relevance detected, refine or replan
- `ANALYZE → EVALUATE`: Analysis complete, evaluate if replan needed
- `EVALUATE → PLAN`: Strategy misaligned, replan needed
- `EVALUATE → REFINE`: Strategy sound, check if refinement needed
- `REFINE → VALIDATE_RESULTS`: Refinement executed, validate new results
- `REFINE → CRITIQUE`: No refinement needed, proceed to critique
- `CRITIQUE → REFINE`: Issues found, refine to address
- `CRITIQUE → SUMMARIZE`: Critique passed, generate summary
- `SUMMARIZE → COMPLETE`: Workflow complete

**Implementation**: `WorkflowState` enum with state transition logic in `run_workflow()` method. Includes confidence tracking and stagnation detection to prevent infinite loops.

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

### 13. **Result Validation and Quality Gates**

**Decision**: Added `VALIDATE_RESULTS` state to check result relevance before analysis, preventing analysis of irrelevant data.

**Rationale**:
- **Accuracy**: Prevents analyzing irrelevant results with high confidence
- **Early Detection**: Catches data quality issues before expensive analysis steps
- **Efficiency**: Triggers refinement/replanning early when results don't match query intent
- **Confidence Calibration**: Provides relevance scores to inform downstream decisions

**Implementation**: `validate_results()` method checks relevance using LLM evaluation; transitions to `REFINE` or `REPLAN` if relevance < 0.6; validates again after refinement.

### 14. **Confidence Tracking and Stagnation Detection**

**Decision**: Track confidence across iterations and detect when refinement isn't improving results.

**Rationale**:
- **Prevent Loops**: Stops infinite refinement loops when confidence plateaus
- **Efficiency**: Avoids wasted iterations when no improvement is possible
- **Transparency**: Shows confidence deltas in logs for debugging

**Implementation**: `confidence_history` tracks confidence over iterations; `refine()` checks if delta < 0.05 after first iteration; stops refinement if stagnating.

### 15. **Improved Skip Logic for EVALUATE and CRITIQUE**

**Decision**: Only skip `EVALUATE` and `CRITIQUE` when both high confidence (>0.85) AND good data quality ("high").

**Rationale**:
- **Accuracy**: Prevents skipping quality checks when data quality is poor
- **Balanced**: Maintains speed optimization while preserving accuracy
- **Context-Aware**: Considers both confidence and data quality signals

**Implementation**: Updated skip conditions in `EVALUATE` and `CRITIQUE` states to check `data_quality == "high"` in addition to confidence threshold.

## 📐 Data Flow and Tool Calls

See [Beginner Guide - Data Flow](BEGINNER_GUIDE.md#complete-data-flow) for detailed data flow explanations.

### Two Execution Modes

| **Aspect** | **Plan-based execution** | **Dynamic tool calling** |
|---|---|---|
| **When** | Default. Used when `use_tool_calling=false` or when the plan is "simple" (e.g. low complexity, ≤2 steps, info_extraction/sentiment). | Used only when the planner sets `use_tool_calling=true` *and* the plan is not overridden as simple. |
| **Who drives** | The plan's `steps` (from `plan()`). The agent loops over steps and calls the retriever directly. | Grok API. The model chooses tools per turn; the agent runs them and appends results to the conversation. |
| **Tools** | `hybrid_search`, `keyword_search`, `filter_by_metadata` via `HybridRetriever` / `retrieval` (no Grok tool-calling). | All tools in `ToolRegistry`: see below. |
| **Progress** | `executing` events with `status: started | completed`, `results_count`. No `tool_calls` / `tool_calling_mode`. | Same, plus `tool_calling_mode: true`, `tool_calls` (list of `{name, args, success, ...}`), and per-call "Calling tool: X" / "Completed N tool call(s)" messages. |
| **Logs** | "Retrieving relevant data…" → "Retrieved N items". No "Tools used" section. | "Starting dynamic tool calling…" → "Calling tool: X" / "Completed N tool call(s)" → "Tool calling finished. Retrieved N results". "Tools used" appears in the Logs tab when `tool_calls` is present. |

### Available Tools (`tools.py`)

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

### Tool-calling Loop (dynamic mode only)

1. Agent sends the research query to Grok with `tools` and `tool_choice="auto"`.
2. Grok returns either a text reply or `tool_calls` (or both).
3. If there are no `tool_calls`, the loop ends; aggregated results are passed to **Analyze**.
4. Otherwise, for each `tool_call`:
   - `ToolRegistry.run_tool(name, arguments)` is invoked.
   - Results are appended to the conversation as tool messages.
   - Progress is emitted (`tool_calling`, `tool_calls` history) so the UI can show "Calling tool: X" and "Tools used".
5. The updated `messages` are sent back to Grok; repeat until no more `tool_calls` or `max_tool_calls` is reached.

After the loop, the final flattened result list is fed into **Analyze** → **Evaluate** → **Refine** / **Critique** → **Summarize** exactly as in plan-based execution.

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
