# Complete Beginner Guide: Grok Agentic Research Workflow

## 📚 Table of Contents
1. [What is This Project?](#what-is-this-project)
2. [Specialties & Strengths](#specialties--strengths)
3. [Limitations](#limitations)
4. [Complete Data Flow](#complete-data-flow)
5. [Detailed Step-by-Step Process](#detailed-step-by-step-process)
6. [Tool Calling Deep Dive](#tool-calling-deep-dive)
7. [Optimizations Explained](#optimizations-explained)
8. [How Each Component Works](#how-each-component-works)
9. [Understanding the State Machine](#understanding-the-state-machine)
10. [Performance Tips](#performance-tips)

---

## What is This Project?

This is an **autonomous AI research agent** that can answer complex questions about social media data (simulated X/Twitter posts). Think of it as a smart assistant that:

1. **Understands** your question
2. **Plans** how to answer it
3. **Searches** through thousands of posts
4. **Validates** that results match your query (prevents analyzing irrelevant data)
5. **Analyzes** what it finds
6. **Evaluates** if the strategy needs to change
7. **Refines** its search if needed (with confidence tracking to prevent loops)
8. **Critiques** the analysis for quality issues
9. **Summarizes** everything into a clear answer

### Key Features:
- **Autonomous**: Makes decisions on its own (when to search more, when to stop)
- **Multi-step**: Breaks complex questions into smaller steps
- **Self-correcting**: Can replan if the first approach doesn't work
- **Real-time**: Shows progress as it works
- **Fast**: Optimized for speed without sacrificing quality

---

## Specialties & Strengths

### What This System Excels At:

#### 1. **Sentiment Analysis** ⭐⭐⭐⭐⭐
The agent is excellent at analyzing sentiment across posts:
- **Positive/Negative/Neutral Detection**: Accurately categorizes sentiment
- **Sentiment Distribution**: Provides percentages of each sentiment type
- **Sentiment Trends**: Can track sentiment changes over time
- **Example Queries**:
  - "What's the sentiment on JavaScript?"
  - "Compare positive vs negative opinions on AI"
  - "How has sentiment about remote work changed?"

#### 2. **Time Range Queries** ⭐⭐⭐⭐⭐
Strong temporal analysis capabilities:
- **Date Filtering**: Can filter posts by specific date ranges
- **Trend Analysis**: Identifies trends over days, weeks, or months
- **Temporal Patterns**: Detects spikes, dips, and patterns over time
- **Example Queries**:
  - "What were the most discussed topics this week?"
  - "Show trends in fashion discussions over the last 7 days"
  - "How has sentiment changed in the past month?"

#### 3. **Multi-Language Support** ⭐⭐⭐⭐
Handles multiple languages effectively:
- **Supported Languages**: English, Spanish, French, Portuguese, German, Japanese
- **Language Filtering**: Can filter posts by language
- **Cross-Language Analysis**: Can compare discussions across languages
- **Example Queries**:
  - "What are Spanish speakers saying about fashion?"
  - "Compare French and English opinions on art"
  - "Summarize Portuguese posts about sports"

#### 4. **Author-Based Analysis** ⭐⭐⭐⭐
Excellent at analyzing posts by specific authors:
- **Verified Account Filtering**: Can filter by verified status
- **Author Comparison**: Compares perspectives between different authors
- **Celebrity vs Regular Users**: Distinguishes between account types
- **Example Queries**:
  - "What do verified accounts say about sports?"
  - "Compare Scorsese vs regular users on entertainment"
  - "What do celebrities think about fashion?"

#### 5. **Category-Specific Queries** ⭐⭐⭐⭐⭐
Strong performance on category-based searches:
- **Categories**: Tech, Sports, Politics, Fashion, Art, Entertainment
- **Category Filtering**: Can filter by specific categories
- **Cross-Category Comparison**: Compares discussions across categories
- **Example Queries**:
  - "What are people discussing in tech?"
  - "Compare fashion vs art discussions"
  - "What topics are trending in politics?"

#### 6. **Complex Multi-Step Queries** ⭐⭐⭐⭐
Excels at breaking down complex queries:
- **Multi-Step Planning**: Automatically decomposes complex questions
- **Iterative Refinement**: Can refine searches based on initial results
- **Tool Selection**: Dynamically chooses appropriate tools
- **Example Queries**:
  - "Compare JavaScript vs Python, then filter by verified accounts, then show 7-day trends"
  - "Find fashion trends this week, then filter for negative sentiment"
  - "What do verified accounts say about sports? Filter by high engagement"

#### 7. **Comparative Analysis** ⭐⭐⭐⭐
Strong at comparing different topics, authors, or time periods:
- **Topic Comparison**: Compares discussions about different topics
- **Sentiment Comparison**: Compares sentiment between topics
- **Temporal Comparison**: Compares trends across time periods
- **Example Queries**:
  - "Compare sentiment about crypto vs traditional finance"
  - "How do discussions about AI differ from discussions about blockchain?"
  - "Compare celebrity vs regular user opinions"

#### 8. **Engagement-Based Filtering** ⭐⭐⭐⭐
Can filter and analyze by engagement metrics:
- **High Engagement Posts**: Finds most liked/retweeted posts
- **Engagement Thresholds**: Filters by minimum engagement
- **Engagement Trends**: Tracks engagement patterns
- **Example Queries**:
  - "Find high-engagement posts about AI"
  - "What topics have the most engagement this week?"
  - "Show verified accounts with high engagement on sports"

---

## Limitations

### What This System Cannot Do or Struggles With:

#### 1. **Real-Time Data** ❌
- **Limitation**: Works with static mock data, not live social media feeds
- **Impact**: Cannot answer questions about current events or real-time trends
- **Workaround**: Update mock data file with recent posts

#### 2. **Very Large Datasets** ⚠️
- **Limitation**: Performance degrades with very large datasets (>10,000 posts)
- **Impact**: Slower retrieval and analysis times
- **Workaround**: Use smaller datasets or increase retrieval limits

#### 3. **Image/Media Analysis** ❌
- **Limitation**: Cannot analyze images, videos, or other media content
- **Impact**: Only analyzes text content of posts
- **Workaround**: None - text-only analysis

#### 4. **Thread Context** ⚠️
- **Limitation**: Limited understanding of reply threads and conversation context
- **Impact**: May miss nuanced discussions in threaded conversations
- **Workaround**: Posts include `is_reply` and `reply_to` fields, but full thread analysis is limited

#### 5. **Sarcasm Detection** ⚠️
- **Limitation**: May struggle with sarcasm and irony detection
- **Impact**: Could misclassify sarcastic posts as serious
- **Workaround**: System includes sarcasm detection in evaluation, but accuracy varies

#### 6. **Very Specific Technical Queries** ⚠️
- **Limitation**: May struggle with highly technical or domain-specific queries
- **Impact**: Lower confidence scores for niche topics
- **Workaround**: Use broader queries or add more domain-specific data

#### 7. **Ambiguous Queries** ⚠️
- **Limitation**: May need clarification for ambiguous queries
- **Impact**: Could produce lower confidence results
- **Workaround**: Be specific in queries, use example queries as templates

#### 8. **Cost Constraints** ⚠️
- **Limitation**: API costs increase with more complex queries and longer workflows
- **Impact**: Very complex queries can be expensive
- **Workaround**: Use fast mode, reduce max iterations, monitor token usage

#### 9. **Language Coverage** ⚠️
- **Limitation**: Best performance on English; other languages have limited data
- **Impact**: Lower quality results for non-English queries
- **Workaround**: Add more data in target languages

#### 10. **No User Authentication** ❌
- **Limitation**: Cannot access private accounts or protected content
- **Impact**: Only analyzes public posts in the dataset
- **Workaround**: None - public data only

#### 11. **Limited Historical Context** ⚠️
- **Limitation**: Mock data has limited historical range (typically 30 days)
- **Impact**: Cannot analyze long-term trends (months/years)
- **Workaround**: Generate more historical data or extend date ranges

#### 12. **No External Data Sources** ❌
- **Limitation**: Cannot fetch data from external APIs or databases
- **Impact**: Limited to the provided mock dataset
- **Workaround**: Add more data to the mock dataset

### When to Use This System:
✅ **Good For**:
- Analyzing sentiment and trends in social media discussions
- Comparing topics, authors, or time periods
- Multi-step research queries requiring iterative refinement
- Exploring patterns in categorized data (tech, sports, fashion, etc.)
- Multilingual analysis (with sufficient data)

❌ **Not Ideal For**:
- Real-time social media monitoring
- Image or media analysis
- Very large-scale datasets (>10K posts)
- Highly technical domain-specific queries
- Long-term historical analysis (years of data)

---

## Complete Data Flow

### High-Level Flow Diagram

```
User Types Query
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. WEB UI (Frontend)                                        │
│    - User enters query in browser                            │
│    - Clicks "Submit"                                         │
│    - JavaScript sends HTTP POST request                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTP POST /api/query
                        │ { "query": "What are people saying about AI?" }
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. FASTAPI SERVER (Backend)                                 │
│    - Receives request at routes/query.py                    │
│    - Creates background thread                              │
│    - Sets up progress callback queue                        │
│    - Starts Server-Sent Events (SSE) stream                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Creates Agent Instance
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. AGENTIC RESEARCH AGENT (agent.py)                        │
│    - State Machine Orchestrator                              │
│    - Runs workflow: PLAN → EXECUTE → VALIDATE → ANALYZE → ...│
│    - Emits progress events via callback                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   PLAN      │ │   EXECUTE    │ │ VALIDATE_    │
│             │ │              │ │   RESULTS    │
│ Calls Grok  │ │ Calls        │ │              │
│ API to     │ │ Hybrid       │ │ Checks       │
│ create plan│ │ Retriever    │ │ relevance    │
└──────┬──────┘ └──────┬───────┘ └──────┬───────┘
       │               │                 │
       │               └────────┬────────┘
       │                        │
       │                        ▼
       │            ┌───────────────────────┐
       │            │     ANALYZE          │
       │            │                       │
       │            │ Calls Grok API to     │
       │            │ analyze results       │
       │            └───────────┬───────────┘
       │                        │
       └────────────────────────┼─────────────┐
                                │             │
                                ▼             │
                    ┌───────────────────────┐ │
                    │   EVALUATE            │ │
                    │   (Should we replan?) │ │
                    └───────────┬───────────┘ │
                        │
            ┌───────────┴───────────┐
            │                       │
        Replan?                  No
            │                       │
            ▼                       ▼
    ┌──────────────┐      ┌──────────────┐
    │   REFINE     │      │   CRITIQUE   │
    │   (Search    │      │   (Check     │
    │    more)     │      │    quality)  │
    └──────┬───────┘      └──────┬───────┘
           │                     │
           └──────────┬──────────┘
                      │
                      ▼
            ┌───────────────────────┐
            │   SUMMARIZE           │
            │   (Final answer)      │
            └───────────┬───────────┘
                        │
                        │ Returns Result Dict
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. RESULT STREAMING                                        │
│    - Progress events sent via SSE                          │
│    - Frontend receives: "planning", "executing", etc.      │
│    - UI updates in real-time                                │
│    - Final result sent as last SSE event                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ SSE: data: {"type": "complete", "result": {...}}
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. WEB UI DISPLAY                                          │
│    - Shows logs in real-time                               │
│    - Displays final summary                                │
│    - Renders markdown beautifully                          │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Data Flow with Code Paths

#### Step 1: User Input → API Request
**File**: `client/static/script.js` (function `submitQuery()`)

```javascript
// User clicks submit button
const query = queryInput.value;  // "What are people saying about AI?"

// Create HTTP request
const response = await fetch(`${API_BASE}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: query })
});

// Open SSE stream to receive real-time updates
const reader = response.body.getReader();
```

**What happens:**
- User types query in browser
- JavaScript sends POST request to `/api/query`
- Server responds with Server-Sent Events (SSE) stream
- Frontend reads stream line-by-line

---

#### Step 2: API Route → Agent Creation
**File**: `server/routes/query.py` (function `query()`)

```python
@query_router.post("/query")
def query(request: QueryRequest):
    # Get agent service (singleton pattern)
    agent_service = get_agent_service()
    
    # Initialize agent (loads data, creates retriever)
    agent_instance, _ = agent_service.initialize_agent()
    
    # Create queue for progress events
    progress_queue = queue.Queue()
    
    # Set up callback to capture progress
    def progress_handler(event_type, data):
        event_data = {'type': event_type, 'timestamp': time.time(), **data}
        progress_queue.put(event_data)
    
    agent_instance.progress_callback = progress_handler
    
    # Start workflow in background thread
    workflow_thread = threading.Thread(target=run_workflow)
    workflow_thread.start()
    
    # Stream events from queue
    while not done:
        event = progress_queue.get(timeout=0.5)
        yield f"data: {json.dumps(event)}\n\n"
```

**What happens:**
- FastAPI receives POST request
- Creates agent instance (loads mock data, builds embeddings)
- Sets up progress callback system
- Starts workflow in background thread
- Streams progress events via SSE

---

#### Step 3: State Machine Execution
**File**: `server/agent.py` (function `run_workflow()`)

```python
def run_workflow(self, query: str, fast_mode: bool = None):
    # Initialize state
    self.current_state = WorkflowState.PLAN
    plan = None
    results = []
    analysis = None
    
    # State machine loop
    while self.current_state != WorkflowState.COMPLETE:
        
        if self.current_state == WorkflowState.PLAN:
            plan = self.plan(query)  # Step 3a
            self.current_state = WorkflowState.EXECUTE
            
        elif self.current_state == WorkflowState.EXECUTE:
            results = self.execute(plan, query)  # Step 3b
            self.current_state = WorkflowState.VALIDATE_RESULTS
        
        elif self.current_state == WorkflowState.VALIDATE_RESULTS:
            validation = self.validate_results(query, results, plan)  # Step 3c
            if validation.get("action") == "replan":
                self.current_state = WorkflowState.PLAN
            elif validation.get("action") == "refine":
                self.current_state = WorkflowState.REFINE
            else:
                self.current_state = WorkflowState.ANALYZE
        
        elif self.current_state == WorkflowState.ANALYZE:
            analysis = self.analyze(query, results, plan)  # Step 3d
            self.current_state = WorkflowState.EVALUATE
            
        # ... more states ...
    
    return result  # Final summary
```

**What happens:**
- Agent runs state machine loop
- Each state performs specific task
- State transitions based on results
- Progress events emitted at each step

---

## Detailed Step-by-Step Process

### Step 3a: PLAN State

**Purpose**: Break down the query into actionable steps

**File**: `server/agent.py` (function `plan()`)

**What happens:**

1. **Grok API Call**:
   ```python
   system_prompt = """Research planner. Break queries into steps.
   
   Return JSON:
   {
       "query_type": "trend_analysis|info_extraction|comparison|...",
       "use_tool_calling": true/false,
       "steps": [
           {"step_number": 1, "action": "search", "description": "...", "tools": ["hybrid_search"]}
       ],
       "expected_complexity": "low|medium|high"
   }
   """
   
   response = self.grok.call(
       model="grok-4-fast-reasoning",
       messages=[{"role": "user", "content": user_prompt}],
       system_prompt=system_prompt,
       response_format={"type": "json_object"}
   )
   ```

2. **Parse Response**:
   ```python
   plan = self.grok.parse_json_response(response["content"])
   # Example result:
   # {
   #     "query_type": "trend_analysis",
   #     "use_tool_calling": False,
   #     "steps": [
   #         {"step_number": 1, "action": "search", "description": "Search for AI-related posts", "tools": ["hybrid_search"]}
   #     ],
   #     "expected_complexity": "medium"
   # }
   ```

3. **Optimization Check**:
   ```python
   # If query is simple, disable tool calling for speed
   is_simple = (
       complexity == "low" or
       steps_count <= 2 or
       query_type in ["info_extraction", "sentiment"]
   )
   if is_simple and plan.get("use_tool_calling", False):
       plan["use_tool_calling"] = False  # Faster execution
   ```

4. **Emit Progress**:
   ```python
   self._emit_progress('planning', {
       'status': 'completed',
       'query_type': plan.get('query_type'),
       'steps_count': len(plan.get('steps', [])),
       'summary': 'Created plan with 2 steps'
   })
   ```

**Example Plan Output**:
```json
{
    "query_type": "trend_analysis",
    "use_tool_calling": false,
    "steps": [
        {
            "step_number": 1,
            "action": "search",
            "description": "Search for posts about AI",
            "tools": ["hybrid_search"]
        }
    ],
    "expected_complexity": "medium"
}
```

---

### Step 3b: EXECUTE State

**Purpose**: Retrieve relevant posts from the dataset

**File**: `server/agent.py` (function `execute()`)

**Two Execution Modes:**

#### Mode 1: Plan-Based Execution (Default, Faster)

```python
def execute(self, plan: Dict, query: str) -> List[Dict]:
    use_tool_calling = plan.get("use_tool_calling", False)
    
    if use_tool_calling:
        # Mode 2: Dynamic tool calling (see below)
        return self.execute_with_tool_calling(search_query)
    
    # Mode 1: Plan-based (direct retriever calls)
    steps = plan.get("steps", [])
    all_results = []
    
    for step in steps:
        action = step.get("action", "search")
        tools = step.get("tools", ["hybrid_search"])
        search_query = step.get("description") or query
        
        if action == "search":
            if "hybrid_search" in tools:
                # Call HybridRetriever directly
                results = self.retriever.hybrid_search(search_query)
                all_results.extend(results)
    
    # Remove duplicates and limit
    unique_results = deduplicate(all_results)[:MAX_RETRIEVAL_RESULTS]
    return unique_results
```

**What happens:**
1. Loop through plan steps
2. For each "search" step, call `hybrid_search()`
3. Combine all results
4. Remove duplicates
5. Limit to top 15 results (configurable)

#### Mode 2: Dynamic Tool Calling (For Complex Queries)

```python
def execute_with_tool_calling(self, query: str, max_tool_calls: int = 5):
    tools = self.tool_registry.get_tool_definitions()  # Get tool schemas
    
    messages = [{"role": "user", "content": f"Research query: {query}"}]
    
    while tool_call_count < max_tool_calls:
        # Call Grok with tools
        response = self.grok.call(
            model="grok-4-fast-reasoning",
            messages=messages,
            tools=tools,  # Provide tool definitions
            tool_choice="auto"  # Let Grok decide which tools to use
        )
        
        tool_calls = response.get("tool_calls", [])
        if not tool_calls:
            break  # Grok is done
        
        # Execute each tool call
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            arguments = json.loads(tool_call["function"]["arguments"])
            
            # Run tool via ToolRegistry
            tool_result = self.tool_registry.run_tool(function_name, arguments)
            
            # Add result to conversation
            messages.append({
                "role": "tool",
                "content": json.dumps(tool_result),
                "tool_call_id": tool_call["id"]
            })
    
    return all_results
```

**What happens:**
1. Grok receives query + tool definitions
2. Grok decides which tools to call (e.g., `hybrid_search`, `temporal_trend_analyzer`)
3. Agent executes tools via `ToolRegistry`
4. Tool results added back to conversation
5. Grok sees results, decides if more tools needed
6. Repeats until Grok says "done" or max iterations reached

**Hybrid Search Details** (`server/retrieval.py`):

```python
def hybrid_search(self, query: str) -> List[Dict]:
    # 1. Semantic Search (embeddings)
    query_embedding = self.embedder.encode(query)
    semantic_scores = cosine_similarity([query_embedding], self.embeddings)[0]
    
    # 2. Keyword Search (TF-IDF)
    keyword_scores = self.tfidf_vectorizer.transform([query])
    keyword_similarities = cosine_similarity(keyword_scores, self.tfidf_matrix)[0]
    
    # 3. Combine (60% semantic, 40% keyword)
    hybrid_scores = (
        0.6 * semantic_scores +  # Semantic weight
        0.4 * keyword_similarities  # Keyword weight
    )
    
    # 4. Get top K results
    top_indices = np.argsort(hybrid_scores)[::-1][:SEMANTIC_SEARCH_TOP_K]
    return [self.data[i] for i in top_indices]
```

**Optimizations:**
- **Embedding Caching**: Embeddings computed once, cached on disk
- **Reduced Top-K**: Only return top 8 results (was 10)
- **Early Termination**: Stop if confidence high enough

---

### Step 3c: ANALYZE State

**Purpose**: Deep analysis of retrieved posts

**File**: `server/agent.py` (function `analyze()`)

**What happens:**

1. **Prepare Data**:
   ```python
   # Limit sample size for analysis (optimization)
   sample_results = results[:ANALYZE_SAMPLE_SIZE]  # Only 6 items
   
   # Truncate text length (optimization)
   for item in sample_results:
       item["text"] = item["text"][:ANALYZE_TEXT_LENGTH]  # Max 150 chars
   ```

2. **Call Grok API**:
   ```python
   system_prompt = """Research analyst. Analyze data for patterns, themes, insights.
   
   Return JSON:
   {
       "main_themes": ["theme1", "theme2"],
       "sentiment_analysis": {"positive": 5, "negative": 2, "neutral": 3},
       "key_insights": ["insight1", "insight2"],
       "confidence": 0.0-1.0,
       "data_quality": "high|medium|low",
       "gaps_or_limitations": ["gap1"]
   }
   """
   
   response = self.grok.call(
       model="grok-4-fast-reasoning",
       messages=[{"role": "user", "content": analysis_prompt}],
       system_prompt=system_prompt,
       response_format={"type": "json_object"},
       max_tokens=MAX_TOKENS_RESPONSE  # 1500 tokens (optimization)
   )
   ```

3. **Parse Analysis**:
   ```python
   analysis = self.grok.parse_json_response(response["content"])
   # Example:
   # {
   #     "main_themes": ["AI safety", "Machine learning"],
   #     "sentiment_analysis": {"positive": 8, "negative": 3, "neutral": 4},
   #     "confidence": 0.75,
   #     "data_quality": "high"
   # }
   ```

4. **Emit Progress**:
   ```python
   self._emit_progress('analyzing', {
       'status': 'completed',
       'confidence': analysis.get('confidence', 0.5),
       'main_themes': analysis.get('main_themes', [])[:3],
       'summary': f'Analysis completed with 75% confidence'
   })
   ```

**Optimizations:**
- **Sample Size**: Only analyze 6 items (was 10)
- **Text Truncation**: Max 150 chars per item (was 200)
- **Token Limit**: Max 1500 tokens per response (was 2000)

---

### Step 3e: EVALUATE State

**Purpose**: Decide if we need to replan (start over) or refine (search more)

**File**: `server/agent.py` (function `evaluate_for_replan()`)

**What happens:**

1. **Check if Skipped** (Optimization - Improved Logic):
   ```python
   confidence = analysis.get("confidence", 0.5)
   data_quality = analysis.get("data_quality", "medium")
   
   # Only skip if BOTH high confidence AND good data quality
   skip_evaluate = (
       use_fast_mode or  # Fast mode enabled
       (SKIP_EVALUATE_IF_HIGH_CONFIDENCE and confidence > 0.85 and data_quality == "high")
   )
   
   if skip_evaluate:
       return {"replan_needed": False}  # Skip for speed
   ```
   
   **Improvement**: Now checks both confidence AND data quality. Previously, high confidence alone could skip evaluation even with poor data quality.

2. **Call Grok API**:
   ```python
   system_prompt = """Strategy evaluator. Determine if plan needs complete revision.
   
   Replan if: confidence < 0.7 (70%) AND (data wrong, strategy misaligned).
   Don't replan if: just need more data, or confidence >= 0.7 with sound strategy.
   """
   
   response = self.grok.call(
       model="grok-4-fast-reasoning",
       messages=[{"role": "user", "content": evaluation_prompt}],
       system_prompt=system_prompt,
       response_format={"type": "json_object"}
   )
   ```

3. **Parse Decision**:
   ```python
   evaluation = self.grok.parse_json_response(response["content"])
   # Example:
   # {
   #     "replan_needed": False,
   #     "reason": "Strategy is sound, just need more data",
   #     "suggested_strategy": None
   # }
   ```

4. **State Transition**:
   ```python
   if evaluation.get("replan_needed") and self.replan_count < max_replans:
       self.replan_count += 1
       self.current_state = WorkflowState.PLAN  # Start over
   else:
       self.current_state = WorkflowState.REFINE  # Continue
   ```

**Optimizations:**
- **Skip if High Confidence**: If confidence > 85%, skip evaluation
- **Fast Mode**: Skip entirely if fast_mode=True
- **Replan Threshold**: Lowered to 70% (was 80%)

---

### Step 3e: REFINE State

**Purpose**: Improve results by searching more or filtering

**File**: `server/agent.py` (function `refine()`)

**What happens:**

1. **Check if Skipped** (Optimization):
   ```python
   confidence = analysis.get("confidence", 0.5)
   if confidence > 0.75:  # High confidence threshold
       return {"refinement_needed": False}  # Skip refinement
   ```

2. **Call Grok API**:
   ```python
   system_prompt = """Refinement planner. Decide if more data needed.
   
   Return JSON:
   {
       "refinement_needed": true|false,
       "next_steps": [
           {"action": "search", "description": "Search for X", "tools": ["hybrid_search"]}
       ],
       "confidence_improvement_expected": 0.0-1.0
   }
   """
   ```

3. **Execute Refinement Steps**:
   ```python
   if refinement.get("refinement_needed"):
       for step in refinement.get("next_steps", []):
           if step.get("action") == "search":
               new_results = self.retriever.hybrid_search(step.get("description"))
               results.extend(new_results)
       
       # Re-analyze with new results
       self.current_state = WorkflowState.ANALYZE
   else:
       self.current_state = WorkflowState.CRITIQUE
   ```

**Optimizations:**
- **Confidence Threshold**: Skip if confidence > 75%
- **Max Iterations**: Limited to 2 refinement loops (was 3)
- **Early Exit**: Stop if confidence improves enough

---

### Step 3f: CRITIQUE State

**Purpose**: Check final summary for hallucinations or bias

**File**: `server/agent.py` (function `critique()`)

**What happens:**

1. **Check if Skipped** (Optimization):
   ```python
   confidence = analysis.get("confidence", 0.5)
   skip_critique = (
       use_fast_mode or
       (SKIP_CRITIQUE_IF_HIGH_CONFIDENCE and confidence > 0.85)
   )
   ```

2. **Call Grok API**:
   ```python
   system_prompt = """Quality critic. Check for hallucinations, bias, errors.
   
   Return JSON:
   {
       "issues_found": true|false,
       "issues": ["issue1", "issue2"],
       "revised_summary": "corrected summary" or null
   }
   """
   ```

3. **Handle Issues**:
   ```python
   if critique_result.get("issues_found"):
       if critique_refine_loop_count < max_critique_refine_loops:
           # Go back to refine
           self.current_state = WorkflowState.REFINE
       else:
           # Max loops reached, proceed anyway
           self.current_state = WorkflowState.SUMMARIZE
   else:
       self.current_state = WorkflowState.SUMMARIZE
   ```

**Optimizations:**
- **Skip if High Confidence**: Skip if confidence > 85%
- **Loop Limit**: Max 2 critique-refine loops to prevent infinite loops

---

### Step 3h: SUMMARIZE State

**Purpose**: Generate final comprehensive summary

**File**: `server/agent.py` (function `summarize()`)

**What happens:**

1. **Call Grok API**:
   ```python
   system_prompt = """Research summarizer. Generate comprehensive summary.
   
   Return JSON:
   {
       "executive_summary": "Brief overview",
       "key_findings": ["finding1", "finding2"],
       "detailed_analysis": "Full analysis",
       "limitations": ["limitation1"],
       "recommendations": ["rec1"]
   }
   """
   
   response = self.grok.call(
       model="grok-4-fast-reasoning",
       messages=[{"role": "user", "content": summary_prompt}],
       system_prompt=system_prompt,
       response_format={"type": "json_object"},
       max_tokens=MAX_TOKENS_SUMMARY  # 1200 tokens (optimization)
   )
   ```

2. **Return Final Result**:
   ```python
   result = {
       "query": query,
       "plan": plan,
       "results_count": len(results),
       "analysis": analysis,
       "final_summary": summary,
       "confidence": analysis.get("confidence", 0.5),
       "execution_steps": len(self.context.execution_steps),
       "total_tokens_used": total_tokens
   }
   return result
   ```

**Optimizations:**
- **Token Limit**: Max 1200 tokens for summary (shorter = faster)

---

## Tool Calling Deep Dive

### When Tool Calling is Used

Tool calling is **only** used when:
1. The planner sets `use_tool_calling: true` in the plan
2. The query is **not** simplified (complexity is medium/high, >2 steps, not simple query types)

**Most queries use plan-based execution** (faster, simpler). Tool calling is reserved for complex, multi-step queries.

### Available Tools

#### 1. `keyword_search`
**Purpose**: Exact keyword/phrase matching  
**Best For**: Hashtags, specific terms, exact phrases  
**Example**:
```json
{
  "name": "keyword_search",
  "arguments": {
    "query": "#Python #AI",
    "top_k": 10
  }
}
```

#### 2. `semantic_search`
**Purpose**: Meaning-based search using embeddings  
**Best For**: Conceptual queries, paraphrases, related topics  
**Example**:
```json
{
  "name": "semantic_search",
  "arguments": {
    "query": "artificial intelligence safety concerns",
    "top_k": 10
  }
}
```

#### 3. `hybrid_search` ⭐ (Recommended)
**Purpose**: Combines keyword + semantic search  
**Best For**: Most queries (default in tool-calling mode)  
**Example**:
```json
{
  "name": "hybrid_search",
  "arguments": {
    "query": "JavaScript frameworks",
    "top_k": 10
  }
}
```

#### 4. `user_profile_lookup`
**Purpose**: Find posts by specific authors  
**Best For**: Author-specific analysis, verified account filtering  
**Example**:
```json
{
  "name": "user_profile_lookup",
  "arguments": {
    "author_name": "Scorsese",
    "verified_only": true
  }
}
```

#### 5. `temporal_trend_analyzer`
**Purpose**: Analyze trends over time periods  
**Best For**: Time-based queries, trend detection  
**Example**:
```json
{
  "name": "temporal_trend_analyzer",
  "arguments": {
    "days_back": 7,
    "category": "tech"
  }
}
```

#### 6. `filter_by_metadata`
**Purpose**: Filter results by various criteria  
**Best For**: Post-execution filtering, refinement  
**Example**:
```json
{
  "name": "filter_by_metadata",
  "arguments": {
    "posts": ["post_1", "post_2", "post_3"],
    "sentiment": "positive",
    "min_engagement": 1000,
    "verified_only": true,
    "category": "tech"
  }
}
```

### Tool Calling Flow Example

**Query**: "Compare JavaScript vs Python, then filter by verified accounts, then show 7-day trends"

**Step 1**: Grok receives query + tool definitions
```python
messages = [{"role": "user", "content": "Compare JavaScript vs Python..."}]
tools = [keyword_search, semantic_search, hybrid_search, ...]
```

**Step 2**: Grok decides to call tools
```json
{
  "tool_calls": [
    {
      "id": "call_1",
      "function": {
        "name": "hybrid_search",
        "arguments": "{\"query\": \"JavaScript\", \"top_k\": 10}"
      }
    },
    {
      "id": "call_2",
      "function": {
        "name": "hybrid_search",
        "arguments": "{\"query\": \"Python\", \"top_k\": 10}"
      }
    }
  ]
}
```

**Step 3**: Agent executes tools
```python
js_results = tool_registry.run_tool("hybrid_search", {"query": "JavaScript"})
python_results = tool_registry.run_tool("hybrid_search", {"query": "Python"})
```

**Step 4**: Results added to conversation
```python
messages.append({
    "role": "tool",
    "content": json.dumps({"results": js_results}),
    "tool_call_id": "call_1"
})
messages.append({
    "role": "tool",
    "content": json.dumps({"results": python_results}),
    "tool_call_id": "call_2"
})
```

**Step 5**: Grok sees results, decides next action
```json
{
  "tool_calls": [
    {
      "function": {
        "name": "filter_by_metadata",
        "arguments": "{\"posts\": [...], \"verified_only\": true}"
      }
    },
    {
      "function": {
        "name": "temporal_trend_analyzer",
        "arguments": "{\"days_back\": 7}"
      }
    }
  ]
}
```

**Step 6**: Process repeats until Grok says "done" or max iterations reached

### Why Tool Calling vs Plan-Based?

| Aspect | Plan-Based | Tool Calling |
|--------|-----------|--------------|
| **Speed** | Faster (direct retriever calls) | Slower (multiple API calls) |
| **Flexibility** | Fixed plan steps | Dynamic tool selection |
| **Best For** | Simple queries, single searches | Complex queries, iterative refinement |
| **API Calls** | 0 (no Grok API for execution) | 1-5 (Grok decides tools) |
| **When Used** | Default (most queries) | Only for complex queries |

### How to Trigger Tool Calling

To see tool calling in action, use **complex, multi-step queries**:

✅ **Will Use Tool Calling**:
- "Compare JavaScript vs Python, then filter by verified accounts, then show 7-day trends"
- "What do verified accounts say about sports? Filter by high engagement, then analyze sentiment"
- "Find fashion trends this week, then filter for negative sentiment, then compare with last week"

❌ **Will Use Plan-Based** (faster):
- "What are people saying about AI?"
- "Summarize sentiment on JavaScript"
- "Find posts about Python"

### Viewing Tool Calls in UI

When tool calling is active, you'll see in the Logs tab:

```
📋 Planning...
   Query Type: comparison
   Steps Planned: 3

⚙️ Executing...
   Starting dynamic tool calling...
   Calling tool: hybrid_search...
   ✓ Tool: hybrid_search (success)
   Calling tool: filter_by_metadata...
   ✓ Tool: filter_by_metadata (success)
   Completed 2 tool call(s). Total results: 15
   Tool calling finished. Retrieved 15 results
```

Look for:
- `tool_calling_mode: true` in logs
- "Tools Used" section showing tool names and results
- "Calling tool: X" messages

---

## Optimizations Explained

### 1. **Model Selection Optimization**

**What**: Use `grok-4-fast-reasoning` for all tasks instead of more expensive models

**Why**:
- **45x cheaper**: $0.20/$0.50 vs $3/$15 per 1M tokens
- **15x larger context**: 2M vs 131K tokens
- **Faster**: 4M tokens per minute throughput

**Impact**: Saves ~$2.80 per 1M tokens, enables better context management

**Code**: `server/config.py` lines 21-37

---

### 2. **Fast Mode**

**What**: Skip EVALUATE and CRITIQUE steps entirely

**Why**: These steps add latency but aren't always necessary

**Impact**: Reduces execution time by ~30-40%

**Code**: `server/config.py` line 49, `server/agent.py` lines 1003-1007, 1137-1140

---

### 3. **High Confidence Skip (Improved)**

**What**: Skip EVALUATE if confidence > 85% AND data_quality == "high", skip CRITIQUE if confidence > 85% AND data_quality == "high"

**Why**: If we're already confident AND data quality is good, no need to evaluate further. Previously only checked confidence, which could skip quality checks even with poor data.

**Impact**: Saves 1-2 API calls per query when confidence is high AND data quality is good, while preserving accuracy checks when data quality is poor

**Code**: `server/config.py` lines 47-48, `server/agent.py` lines 1006-1008, 1137-1141

**Improvement**: Now considers both confidence and data quality signals, preventing premature skipping when data quality is poor.

---

### 4. **Reduced Sample Sizes**

**What**: 
- Analyze only 6 items (was 10)
- Show only 4 items in critique (was 5)
- Truncate text to 150 chars (was 200)

**Why**: Less data = faster API calls, lower token usage

**Impact**: Reduces token usage by ~40% in analysis step

**Code**: `server/config.py` lines 61-63

---

### 5. **Token Limits**

**What**:
- Max 1500 tokens per response (was 2000)
- Max 1200 tokens for summary (was longer)

**Why**: Shorter responses = faster generation, lower cost

**Impact**: Reduces response time by ~20-30%

**Code**: `server/config.py` lines 43-44

---

### 6. **Retrieval Optimization**

**What**:
- Top-K reduced from 10 to 8
- Max results reduced from 20 to 15
- Early termination if confidence high

**Why**: Fewer results = faster processing

**Impact**: Reduces retrieval time by ~20%

**Code**: `server/config.py` lines 57-60

---

### 7. **Embedding Caching**

**What**: Compute embeddings once, cache on disk

**Why**: Embedding computation is expensive (takes seconds)

**Impact**: Subsequent runs are ~5-10x faster

**Code**: `server/retrieval.py` lines 80-120

**How it works**:
```python
# Compute hash of data
data_hash = hashlib.md5(json.dumps(data).encode()).hexdigest()
cache_file = f"data/.embeddings_cache/embeddings_{data_hash}.npy"

if cache_file.exists():
    embeddings = np.load(cache_file)  # Load from cache
else:
    embeddings = embedder.encode(data)  # Compute
    np.save(cache_file, embeddings)  # Save to cache
```

---

### 8. **Max Iterations Reduction**

**What**: Max refinement loops reduced from 3 to 2

**Why**: Most improvements happen in first 2 iterations

**Impact**: Prevents long-running queries, saves tokens

**Code**: `server/config.py` line 40

---

### 9. **Simple Query Detection**

**What**: Automatically disable tool calling for simple queries

**Why**: Tool calling adds overhead (extra API calls)

**Impact**: Simple queries are ~50% faster

**Code**: `server/agent.py` lines 144-152

---

### 10. **Parallel Model Comparison**

**What**: Run multiple models simultaneously using ThreadPoolExecutor

**Why**: Sequential execution would be slow

**Impact**: Comparison of 3 models takes same time as 1 model

**Code**: `server/routes/query.py` lines 222-224

---

### 11. **Replan Threshold Lowered**

**What**: Changed from 80% to 70% confidence threshold

**Why**: More aggressive replanning when confidence is low

**Impact**: Better results for difficult queries

**Code**: `server/agent.py` lines 688-689, 719

---

### 12. **Result Validation (New)**

**What**: Validate result relevance before analysis using LLM evaluation

**Why**: Prevents analyzing irrelevant data with high confidence, catches data quality issues early

**Impact**: Improves accuracy by ensuring only relevant results are analyzed, triggers refinement/replanning early when results don't match query intent

**Code**: `server/agent.py` lines 459-541

**How it works**:
```python
# After EXECUTE, validate results before ANALYZE
validation = self.validate_results(query, results, plan)

if validation.get("action") == "replan":
    # Results don't match query - need new strategy
    self.current_state = WorkflowState.PLAN
elif validation.get("action") == "refine" or relevance_score < 0.6:
    # Low relevance - trigger refinement
    self.current_state = WorkflowState.REFINE
else:
    # Results validated - proceed to analysis
    self.current_state = WorkflowState.ANALYZE
```

**Benefits**:
- Early detection of irrelevant results
- Prevents false confidence from analyzing wrong data
- Automatic refinement/replanning triggers

---

### 13. **Confidence Tracking and Stagnation Detection (New)**

**What**: Track confidence across iterations and detect when refinement isn't improving results

**Why**: Prevents infinite refinement loops when confidence plateaus

**Impact**: Stops wasted iterations, improves efficiency, shows confidence deltas in logs

**Code**: `server/agent.py` lines 543-665, 1120-1128

**How it works**:
```python
# Track confidence history
confidence_history.append(confidence)
previous_confidence = confidence_history[-2] if len(confidence_history) > 1 else None

# In refine(), check for stagnation
if previous_confidence is not None:
    confidence_delta = confidence - previous_confidence
    if confidence_delta < 0.05 and self.iteration_count > 0:
        # Confidence not improving - stop refinement
        return {"refinement_needed": False, "confidence_stagnant": True}
```

**Benefits**:
- Prevents infinite loops
- Saves tokens and time
- Transparent confidence tracking in logs

---

### 14. **Improved Refinement Threshold (New)**

**What**: Increased refinement skip threshold from 75% to 85%

**Why**: Catch more cases that need refinement, improve accuracy

**Impact**: More queries will go through refinement when needed, improving result quality

**Code**: `server/agent.py` line 552

---

### 12. **Result Validation (New)**

**What**: Validate result relevance before analysis using LLM evaluation

**Why**: Prevents analyzing irrelevant data with high confidence, catches data quality issues early

**Impact**: Improves accuracy by ensuring only relevant results are analyzed, triggers refinement/replanning early when results don't match query intent

**Code**: `server/agent.py` lines 459-541

**How it works**:
```python
# After EXECUTE, validate results before ANALYZE
validation = self.validate_results(query, results, plan)

if validation.get("action") == "replan":
    # Results don't match query - need new strategy
    self.current_state = WorkflowState.PLAN
elif validation.get("action") == "refine" or relevance_score < 0.6:
    # Low relevance - trigger refinement
    self.current_state = WorkflowState.REFINE
else:
    # Results validated - proceed to analysis
    self.current_state = WorkflowState.ANALYZE
```

**Benefits**:
- Early detection of irrelevant results
- Prevents false confidence from analyzing wrong data
- Automatic refinement/replanning triggers

---

### 13. **Confidence Tracking and Stagnation Detection (New)**

**What**: Track confidence across iterations and detect when refinement isn't improving results

**Why**: Prevents infinite refinement loops when confidence plateaus

**Impact**: Stops wasted iterations, improves efficiency, shows confidence deltas in logs

**Code**: `server/agent.py` lines 543-665, 1120-1128

**How it works**:
```python
# Track confidence history
confidence_history.append(confidence)
previous_confidence = confidence_history[-2] if len(confidence_history) > 1 else None

# In refine(), check for stagnation
if previous_confidence is not None:
    confidence_delta = confidence - previous_confidence
    if confidence_delta < 0.05 and self.iteration_count > 0:
        # Confidence not improving - stop refinement
        return {"refinement_needed": False, "confidence_stagnant": True}
```

**Benefits**:
- Prevents infinite loops
- Saves tokens and time
- Transparent confidence tracking in logs

---

### 14. **Improved Refinement Threshold (New)**

**What**: Increased refinement skip threshold from 75% to 85%

**Why**: Catch more cases that need refinement, improve accuracy

**Impact**: More queries will go through refinement when needed, improving result quality

**Code**: `server/agent.py` line 552

---

### 15. **Context Management**

**What**: Truncate old steps when context gets too large

**Why**: Prevents context overflow, reduces token usage

**Impact**: Enables longer workflows without hitting limits

**Code**: `server/context_manager.py` lines 80-120

---

## How Each Component Works

### 1. HybridRetriever (`server/retrieval.py`)

**Purpose**: Search through posts using semantic + keyword search

**Key Methods**:
- `hybrid_search(query)`: Combines semantic and keyword search
- `keyword_search(query)`: Traditional keyword matching
- `filter_by_metadata(posts, filters)`: Filter by sentiment, engagement, etc.

**How Semantic Search Works**:
1. Convert query to embedding (vector) using SentenceTransformer
2. Compare with all post embeddings using cosine similarity
3. Return top K most similar posts

**How Keyword Search Works**:
1. Convert query and posts to TF-IDF vectors
2. Compute cosine similarity
3. Return top K most similar posts

**How Hybrid Works**:
```python
hybrid_score = 0.6 * semantic_score + 0.4 * keyword_score
```

---

### 2. ToolRegistry (`server/tools.py`)

**Purpose**: Execute tools that Grok can call dynamically

**Available Tools**:
- `keyword_search`: Exact keyword matching
- `semantic_search`: Embedding-based search
- `hybrid_search`: Combined search (default)
- `user_profile_lookup`: Find posts by author
- `temporal_trend_analyzer`: Analyze trends over time
- `filter_by_metadata`: Filter by various criteria

**How Tool Calling Works**:
1. Grok receives tool definitions (OpenAI function-calling format)
2. Grok decides which tools to call
3. Agent executes tools via `ToolRegistry.run_tool()`
4. Results sent back to Grok
5. Grok decides if more tools needed

---

### 3. ContextManager (`server/context_manager.py`)

**Purpose**: Track execution history and manage context size

**Key Features**:
- Stores all execution steps
- Tracks token usage
- Truncates old steps when context too large
- Creates concise summaries of old steps

**How Context Truncation Works**:
```python
if total_tokens > MAX_CONTEXT_TOKENS:
    # Remove oldest steps
    while total_tokens > MAX_CONTEXT_TOKENS * 0.8:
        removed_step = steps.pop(0)
        total_tokens -= removed_step.tokens_used
    
    # Create summary of removed steps
    summary = create_concise_data_summary(removed_steps)
```

---

### 4. GrokClient (`server/grok_client.py`)

**Purpose**: Interface to Grok API

**Key Methods**:
- `call()`: Make API call with messages, system prompt, tools
- `parse_json_response()`: Parse JSON from response
- `stream()`: Stream responses (for future use)

**How API Calls Work**:
```python
response = requests.post(
    f"{GROK_BASE_URL}/chat/completions",
    headers={"Authorization": f"Bearer {GROK_API_KEY}"},
    json={
        "model": model_name,
        "messages": messages,
        "system": system_prompt,
        "tools": tools,  # Optional
        "tool_choice": "auto",  # Optional
        "response_format": {"type": "json_object"},  # Optional
        "max_tokens": max_tokens
    }
)
```

---

## Understanding the State Machine

**Recent Improvements**: The state machine now includes result validation, confidence tracking with stagnation detection, and improved skip logic that considers both confidence and data quality. These improvements prevent analyzing irrelevant data and infinite refinement loops.

The state machine is visualized in the UI using a Mermaid diagram that updates in real-time, showing which models are at each state and how they progress through the workflow.

### State Transitions

```
PLAN
  │
  ▼
EXECUTE
  │
  ▼
VALIDATE_RESULTS
  │
  ├─[action="replan"]──► PLAN (start over)
  │
  ├─[action="refine"]──► REFINE
  │
  └─[action="proceed"]──► ANALYZE
                          │
                          ▼
                      EVALUATE
                          │
                          ├─[replan_needed=True]──► PLAN (start over)
                          │
                          └─[replan_needed=False]──► REFINE
                                                      │
                                                      ├─[refinement_needed=True]──► VALIDATE_RESULTS (validate new results)
                                                      │                                 │
                                                      │                                 └─► ANALYZE (re-analyze)
                                                      │
                                                      └─[refinement_needed=False]──► CRITIQUE
                                                                                      │
                                                                                      ├─[issues_found=True]──► REFINE
                                                                                      │
                                                                                      └─[issues_found=False]──► SUMMARIZE
                                                                                                                │
                                                                                                                ▼
                                                                                                            COMPLETE
```

### Detailed State Explanations

#### 1. **PLAN State** 📋

**Purpose**: Break down the user's query into actionable steps and decide on execution strategy.

**What It Does**:
- Analyzes the query to determine its type (trend_analysis, sentiment, comparison, etc.)
- Creates a step-by-step execution plan
- Decides between two execution modes:
  - **Plan-based execution** (default, faster): Direct retrieval using predefined steps
  - **Tool-calling execution** (complex queries): Dynamic tool selection by the LLM

**Key Decisions**:
- `query_type`: Categorizes the query (trend_analysis, info_extraction, comparison, sentiment, temporal, other)
- `use_tool_calling`: Whether to use dynamic tool calling (true) or plan-based execution (false)
- `steps`: Array of execution steps with actions, descriptions, and tools
- `expected_complexity`: low, medium, or high

**Model Used**: `PLANNER_MODEL` (typically `grok-4-fast-reasoning`)

**Can Skip?**: **No** - This is always the first state

**Example Output**:
```json
{
  "query_type": "comparison",
  "use_tool_calling": false,
  "steps": [
    {"step_number": 1, "action": "search", "description": "Search for JavaScript posts", "tools": ["hybrid_search"]},
    {"step_number": 2, "action": "search", "description": "Search for Python posts", "tools": ["hybrid_search"]}
  ],
  "expected_complexity": "medium"
}
```

**Transitions**: Always → `EXECUTE`

---

#### 2. **EXECUTE State** ⚙️

**Purpose**: Retrieve relevant data from the dataset based on the plan.

**What It Does**:
- Executes the plan steps sequentially
- Uses either:
  - **Plan-based mode**: Direct calls to `HybridRetriever` based on plan steps
  - **Tool-calling mode**: LLM dynamically selects and calls tools iteratively
- Combines results from multiple steps
- Deduplicates posts by ID

**Key Features**:
- Supports multiple search strategies (keyword, semantic, hybrid)
- Can filter by metadata (sentiment, engagement, verification status)
- Can analyze temporal trends
- Can look up posts by specific authors

**Model Used**: 
- Plan-based: Direct retrieval (no LLM)
- Tool-calling: `PLANNER_MODEL` for tool selection

**Can Skip?**: **No** - Data retrieval is essential

**Example**: For query "Compare JavaScript vs Python sentiment", executes:
1. Search for JavaScript posts → 50 results
2. Search for Python posts → 45 results
3. Combine and deduplicate → 90 unique results

**Transitions**: Always → `VALIDATE_RESULTS`

---

#### 3. **VALIDATE_RESULTS State** ✅

**Purpose**: Validate that retrieved results are relevant to the query before analysis.

**What It Does**:
- Checks if results match the query intent
- Calculates a relevance score (0.0-1.0)
- Recommends next action: `proceed`, `refine`, or `replan`

**Key Decisions**:
- `validation_passed`: Whether results are good enough
- `relevance_score`: How relevant results are (0.0-1.0)
- `action`: What to do next:
  - `proceed`: Results are relevant → go to ANALYZE
  - `refine`: Results need improvement → go to REFINE (only if relevance_score < 0.4)
  - `replan`: Results don't match query → start over at PLAN (only if relevance_score < 0.3)

**Special Cases**:
- If `len(results) == 0`: Automatically triggers `replan` (no results found)
- System is lenient: Prefers `proceed` unless results are clearly wrong

**Model Used**: `ANALYZER_MODEL` (typically `grok-3-mini`)

**Can Skip?**: **No** - Critical quality gate to prevent analyzing irrelevant data

**Example**: 
- Query: "What are people saying about AI?"
- Results: 30 posts about JavaScript (not AI)
- Validation: `relevance_score: 0.2`, `action: "replan"` → Start over with better search terms

**Transitions**:
- `action="replan"` → `PLAN` (start over)
- `action="refine"` → `REFINE`
- `action="proceed"` → `ANALYZE`

---

#### 4. **ANALYZE State** 🔍

**Purpose**: Analyze retrieved results to extract patterns, themes, and insights.

**What It Does**:
- Examines a sample of results (typically 6 items)
- Identifies key themes, patterns, and insights
- Calculates confidence score (0.0-1.0)
- Assesses data quality (high, medium, low)
- Extracts key insights, sentiment distribution, and trends

**Key Outputs**:
- `confidence`: How confident the analysis is (0.0-1.0)
- `data_quality`: Quality of retrieved data (high, medium, low)
- `key_insights`: Array of main findings
- `sentiment_distribution`: Breakdown of positive/negative/neutral
- `themes`: Main topics identified

**Optimizations**:
- Only analyzes 6 sample items (not all results) for speed
- Truncates text to 150 characters per item
- Uses concise data summaries

**Model Used**: `ANALYZER_MODEL` (typically `grok-3-mini`)

**Can Skip?**: **No** - Analysis is essential for generating insights

**Example Output**:
```json
{
  "confidence": 0.85,
  "data_quality": "high",
  "key_insights": [
    "JavaScript discussions focus on frameworks and performance",
    "Python discussions emphasize data science and AI"
  ],
  "sentiment_distribution": {"positive": 0.6, "negative": 0.2, "neutral": 0.2}
}
```

**Transitions**: Always → `EVALUATE`

---

#### 5. **EVALUATE State** 🔎

**Purpose**: Evaluate whether the current strategy needs to be completely replanned.

**What It Does**:
- Reviews the analysis and plan
- Determines if the strategy is fundamentally wrong
- Decides between:
  - **Replan**: Strategy is wrong, need to start over
  - **Refine**: Strategy is good, just need more/better data

**Key Decisions**:
- `replan_needed`: Whether to start over from PLAN
- `reason`: Explanation for the decision
- `suggested_strategy`: Optional new strategy if replanning

**Skip Conditions**:
- **Fast mode enabled**: Always skipped
- **High confidence + high quality**: If `confidence > 0.85` AND `data_quality == "high"`, skip evaluation

**Replan Triggers**:
- Confidence < 0.7 (70%) AND strategy is misaligned
- Data doesn't match query intent
- Fundamental approach is wrong

**Model Used**: `REFINER_MODEL` (typically `grok-3-mini`)

**Can Skip?**: **Yes** - Skipped in fast mode or when confidence is high

**Example**:
- Analysis shows low confidence (0.6) and data about wrong topic
- Evaluation: `replan_needed: true`, `reason: "Results don't match query intent"` → Go back to PLAN

**Transitions**:
- `replan_needed=True` → `PLAN` (start over)
- `replan_needed=False` → `REFINE`

---

#### 6. **REFINE State** 🔄

**Purpose**: Improve results by gathering more or better data without changing the overall strategy.

**What It Does**:
- Decides if refinement is needed
- Creates refinement steps (e.g., "search with different keywords", "filter by date range")
- Executes refinement steps
- Re-analyzes with new results

**Key Decisions**:
- `refinement_needed`: Whether more data is needed
- `next_steps`: Array of refinement actions to take
- `reason`: Why refinement is needed

**Skip Conditions**:
- **High confidence**: If `confidence > 0.85`, skip refinement
- **Confidence stagnation**: If confidence isn't improving across iterations, stop refining

**Stagnation Detection**:
- Tracks `confidence_history` across refinement loops
- If `confidence_delta < 0.05` (confidence not improving), stops refinement
- Prevents infinite refinement loops

**Refinement Steps**:
- Can search with different keywords
- Can apply additional filters
- Can expand date ranges
- Can search by different authors

**Model Used**: `REFINER_MODEL` (typically `grok-3-mini`)

**Can Skip?**: **Yes** - Skipped when confidence is high or stagnating

**Example**:
- Initial results: 20 posts
- Refinement: "Search with synonyms and expand date range"
- New results: 35 posts (includes original 20)
- Re-analyze with combined results

**Transitions**:
- `refinement_needed=True` → `VALIDATE_RESULTS` (validate new results) → `ANALYZE` (re-analyze)
- `refinement_needed=False` → `CRITIQUE`

---

#### 7. **CRITIQUE State** 🔬

**Purpose**: Review the analysis and summary for hallucinations, bias, and factual errors.

**What It Does**:
- Checks if claims are supported by retrieved data
- Identifies hallucinations (made-up facts)
- Detects selection bias
- Ensures analysis is balanced
- Adjusts confidence if issues found

**Key Decisions**:
- `critique_passed`: Whether analysis passes quality checks
- `hallucinations`: Array of unsupported claims
- `biases`: Array of detected biases
- `corrections`: Suggested corrections
- `confidence_adjustment`: Adjustment to confidence score (-0.1 to 0.1)

**Skip Conditions**:
- **Fast mode enabled**: Always skipped
- **High confidence + high quality**: If `confidence > 0.85` AND `data_quality == "high"`, skip critique

**Issue Handling**:
- If `issues_found=True`: Go back to REFINE to fix issues
- If `issues_found=False`: Proceed to SUMMARIZE

**Model Used**: `REFINER_MODEL` (typically `grok-3-mini`)

**Can Skip?**: **Yes** - Skipped in fast mode or when confidence is high

**Example**:
- Analysis claims "80% positive sentiment"
- Critique: "Only 60% positive based on data" → `hallucinations: ["Inflated sentiment percentage"]`
- Action: Go back to REFINE to correct analysis

**Transitions**:
- `issues_found=True` → `REFINE` (fix issues)
- `issues_found=False` → `SUMMARIZE`

---

#### 8. **SUMMARIZE State** 📝

**Purpose**: Generate the final comprehensive summary answer for the user.

**What It Does**:
- Combines all analysis, insights, and findings
- Creates a comprehensive summary
- Formats the answer clearly
- Includes key insights, patterns, and conclusions

**Key Outputs**:
- `final_summary`: The complete answer text
- `key_findings`: Main conclusions
- `supporting_data`: Evidence from retrieved results

**Model Used**: `SUMMARIZER_MODEL` (typically `grok-3-mini`)

**Can Skip?**: **No** - Final summary is always generated

**Example Output**:
```
Based on analysis of 90 posts comparing JavaScript and Python:

**Key Findings:**
- JavaScript discussions focus on frameworks (React, Vue) and performance optimization
- Python discussions emphasize data science, AI/ML, and ease of use
- Sentiment: JavaScript 65% positive, Python 70% positive

**Trends:**
- JavaScript: Growing interest in performance and modern frameworks
- Python: Strong focus on AI/ML applications and data analysis
```

**Transitions**: Always → `COMPLETE`

---

### State Summary Table

| State | Purpose | Can Skip? | When Skipped | Model Used |
|-------|---------|-----------|--------------|------------|
| **PLAN** | Create execution plan | No | Never | `PLANNER_MODEL` |
| **EXECUTE** | Retrieve data | No | Never | Direct retrieval or `PLANNER_MODEL` |
| **VALIDATE_RESULTS** | Validate result relevance | No | Never (critical quality gate) | `ANALYZER_MODEL` |
| **ANALYZE** | Analyze results | No | Never | `ANALYZER_MODEL` |
| **EVALUATE** | Check if replan needed | Yes | Fast mode OR (confidence > 85% AND data_quality == "high") | `REFINER_MODEL` |
| **REFINE** | Improve results | Yes | Confidence > 85% OR confidence stagnating | `REFINER_MODEL` |
| **CRITIQUE** | Check quality | Yes | Fast mode OR (confidence > 85% AND data_quality == "high") | `REFINER_MODEL` |
| **SUMMARIZE** | Generate final answer | No | Never | `SUMMARIZER_MODEL` |

### Understanding State Transitions

**Forward Flow (Normal Path)**:
1. `PLAN` → `EXECUTE` → `VALIDATE_RESULTS` → `ANALYZE` → `EVALUATE` → `REFINE` → `CRITIQUE` → `SUMMARIZE` → `COMPLETE`

**Cycles (Self-Correction)**:
- **Replan Cycle**: `VALIDATE_RESULTS` or `EVALUATE` → `PLAN` (start over with new strategy)
- **Refinement Cycle**: `REFINE` → `VALIDATE_RESULTS` → `ANALYZE` (improve results iteratively)
- **Critique Cycle**: `CRITIQUE` → `REFINE` → `CRITIQUE` (fix quality issues)

**Skip Paths (Fast Mode)**:
- `ANALYZE` → `REFINE` (skips `EVALUATE` and `CRITIQUE`)

### Visual Representation

The state machine is visualized in the UI using a Mermaid diagram that:
- Shows all states as nodes with icons
- Displays transition arrows with labels (e.g., "if validated", "if replan needed")
- Highlights active states (where models currently are) in blue
- Shows completed states in green
- Shows pending states in gray
- Displays model indicators on active states (e.g., "g4fr", "g4", "g3mini")
- Updates in real-time as models progress through the workflow

This visualization helps you understand:
- Where each model is in the workflow
- What transitions are being taken
- Which states have been completed
- The overall progress of the research process

---

## Performance Tips

### For Faster Queries:
1. **Enable Fast Mode**: Set `fast_mode=True` in UI or config
2. **Use Simple Queries**: Avoid complex multi-step queries when possible
3. **Reduce Data Size**: Use smaller mock dataset for testing
4. **Clear Embedding Cache**: If data changed, delete cache to rebuild

### For Better Results:
1. **Disable Fast Mode**: Get full evaluation and critique
2. **Use Complex Queries**: Multi-step queries trigger tool calling
3. **Increase Max Iterations**: Allow more refinement loops
4. **Increase Sample Sizes**: Analyze more items
5. **Result Validation**: The system now validates results before analysis (automatic)
6. **Confidence Tracking**: System tracks confidence improvement to prevent loops (automatic)

### For Lower Costs:
1. **Use Fast Mode**: Fewer API calls = lower cost
2. **Reduce Token Limits**: Shorter responses = fewer tokens
3. **Use Simple Queries**: Avoid tool calling overhead
4. **Monitor Token Usage**: Check `total_tokens_used` in results

---

## Common Questions

### Q: Why does it take so long?
**A**: The agent makes multiple API calls (plan, execute, analyze, evaluate, refine, critique, summarize). Each call takes 1-3 seconds. Fast mode reduces this significantly.

### Q: Why doesn't it use tool calling?
**A**: Tool calling is only used for complex queries. Simple queries use plan-based execution (faster). Try a complex query like "Compare JavaScript vs Python, then filter by verified accounts, then show 7-day trends."

### Q: How do I see what tools are being used?
**A**: Check the Logs tab in the UI. Tool calls appear when `tool_calling_mode: true` is present in the logs.

### Q: Why is confidence low?
**A**: Confidence depends on data quality and query match. Try queries that match topics in the dataset (AI, JavaScript, fashion, sports, etc.).

### Q: How do I add more data?
**A**: Edit `data/mock_x_data.json` or run `python server/data_generator.py` to regenerate.

---

## Next Steps

1. **Try Example Queries**: Use the examples in the UI
2. **Check Logs**: See what the agent is doing in real-time
3. **Compare Models**: Select multiple models to compare performance
4. **Read Code**: Explore `server/agent.py` to understand the workflow
5. **Experiment**: Try different queries and see how the agent responds

---

**Happy Researching! 🚀**
