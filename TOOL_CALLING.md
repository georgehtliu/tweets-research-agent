# Dynamic Tool Calling Implementation

## Overview

The agent now supports **dynamic tool calling**, where Grok can iteratively select and use tools based on intermediate results. This enables true autonomous tool selection as specified in the requirements.

## How It Works

### 1. **Tool Definitions**

Tools are defined in `server/tools.py` (`ToolRegistry` class) in OpenAI function-calling format:

- `keyword_search` - Keyword-based search
- `semantic_search` - Semantic similarity search  
- `hybrid_search` - Combined keyword + semantic search
- `user_profile_lookup` - Find posts by author
- `temporal_trend_analyzer` - Analyze trends over time
- `filter_by_metadata` - Filter by sentiment, engagement, etc.

### 2. **Execution Modes**

The agent supports two execution modes:

#### **Plan-Based Execution** (Default)
- Planner specifies exact steps with tools
- Agent executes steps sequentially
- Good for straightforward queries

#### **Tool-Calling Execution** (Dynamic)
- Planner sets `use_tool_calling: true` for complex queries
- Grok dynamically selects tools iteratively
- Can call multiple tools per turn
- Sees tool results and decides if more information is needed
- Good for exploratory, ambiguous, or multi-step queries

### 3. **Implementation Details**

#### **GrokClient Updates** (`server/grok_client.py`)
- Added `tools` parameter to `call()` method
- Added `tool_choice` parameter (defaults to "auto")
- Parses `tool_calls` from API response
- Returns `tool_calls` array in response dict

#### **Agent Updates** (`server/agent.py`)

**`execute_with_tool_calling()`**:
- Iterative loop: Call Grok → Parse tool calls → Execute tools → Add results → Repeat
- Maximum `max_tool_calls` iterations (default: 5)
- Deduplicates results across tool calls
- Returns aggregated results

**`execute()`**:
- Checks plan for `use_tool_calling` flag
- Routes to `execute_with_tool_calling()` if enabled
- Otherwise uses plan-based execution

**`plan()`**:
- Updated prompt to suggest tool calling for complex queries
- Planner decides when to use `use_tool_calling: true`
- Criteria: multiple tool types needed, exploratory queries, iterative refinement

## Usage

### Automatic (Recommended)
The planner automatically decides when to use tool calling based on query complexity:

```python
plan = agent.plan("What are people saying about AI safety, and how has sentiment changed over the past week?")
# Planner may set use_tool_calling: true for this complex query
results = agent.execute(plan, query)
```

### Manual Override
You can force tool calling by modifying the plan:

```python
plan = agent.plan(query)
plan["use_tool_calling"] = True  # Force tool calling
results = agent.execute(plan, query)
```

### Direct Tool Calling
Call `execute_with_tool_calling()` directly:

```python
results = agent.execute_with_tool_calling(query, max_tool_calls=5)
```

## Example Flow

1. **Query**: "Find posts about AI from verified researchers in the last 7 days, then analyze sentiment trends"

2. **Planner** decides this needs tool calling (`use_tool_calling: true`)

3. **Tool Calling Loop**:
   - **Turn 1**: Grok calls `temporal_trend_analyzer(days_back=7, query="AI")`
   - **Turn 2**: Grok sees results, calls `filter_by_metadata(verified_only=true, author_type="researcher")`
   - **Turn 3**: Grok analyzes results, decides no more tools needed
   - **Done**: Returns filtered, deduplicated results

4. **Analysis** proceeds with the retrieved results

## Benefits

✅ **True Autonomy**: Agent selects tools dynamically based on context  
✅ **Iterative Refinement**: Can refine searches based on intermediate results  
✅ **Multi-Tool Coordination**: Can combine multiple tools in one turn  
✅ **Adaptive**: Handles ambiguous or exploratory queries better  
✅ **Backward Compatible**: Plan-based execution still works for simple queries

## Configuration

- **Max Tool Calls**: Default 5 iterations (configurable in `execute_with_tool_calling()`)
- **Tool Selection**: Grok decides which tools to use (guided by system prompt)
- **Result Limits**: Respects `config.MAX_RETRIEVAL_RESULTS`

## Testing

To test tool calling:

1. Use a complex query that benefits from multiple tools:
   ```python
   query = "Find verified researchers discussing neural networks, analyze sentiment trends over the past month, and identify the most engaged posts"
   ```

2. Check the plan - it should have `use_tool_calling: true`

3. Watch console output for tool calls:
   ```
   🔧 Calling tool: temporal_trend_analyzer with args: {...}
   🔧 Calling tool: filter_by_metadata with args: {...}
   ```

4. Verify results include data from multiple tools

## Future Enhancements

- [ ] Add tool call cost tracking
- [ ] Add tool call success/failure metrics
- [ ] Support parallel tool execution
- [ ] Add tool call retry logic
- [ ] Visualize tool calling flow in UI
