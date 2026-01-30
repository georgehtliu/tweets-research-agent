# Demo Script: Grok Agentic Research Agent

**Total Time**: ~5 minutes

---

## Part 1: UI Overview (1 minute)

**Screen Actions**:
- Point to query input box
- Scroll through example queries (simple, complex, languages, edge cases)
- Show fast mode toggle
- Show model selection checkboxes
- Click on Logs tab
- Click on Summary tab
- Point to state machine visualization area below progress bars

**Script Points**:
- Welcome to autonomous AI research agent built with Grok
- Main interface: query input, example queries organized by complexity
- Fast mode toggle skips some quality checks for speed
- Model selection: compare multiple Grok models side-by-side
- Two tabs: Logs (real-time progress) and Summary (final results)
- State machine visualization shows 8 states in real-time
- States: Plan, Execute, Validate, Analyze, Evaluate, Refine, Critique, Summarize
- Active states highlighted in blue with model indicators
- Completed states turn green
- Transitions visible with labels

---

## Part 2: What Queries Can the Agent Handle? (30 seconds)

**Script Points**:
- Wide variety of queries about social media data
- **Simple queries**: sentiment analysis, trend analysis, category searches, language-specific
- **Complex queries**: comparisons, filtered searches, temporal analysis, combined operations
- **What makes a query complex**: multiple steps, comparisons, filtering, temporal analysis
- Complex queries trigger dynamic tool calling where Grok decides which tools to use
- Let me demonstrate with a simple query first, then a complex one

**Screen**: Scroll through example queries, point out simple vs complex

---

## Part 3: Simple Query Demo (1 minute)

### Setup (10 seconds)

**Action**: 
- Click example: **"What's the sentiment on JavaScript?"**
- Or type: `What's the sentiment on JavaScript?`
- Click Submit

**Script**: "Starting with a simple sentiment analysis query about JavaScript"

---

### Execution (30 seconds)

**Script Points** (as states appear):
- **PLAN State**: Agent analyzes query, creates simple plan
- Identified as sentiment analysis with low complexity
- Using plan-based execution - no tool calling needed (faster)
- **EXECUTE State**: Searching dataset using hybrid search
- Combines semantic and keyword matching
- Fast because following predefined plan
- **VALIDATE_RESULTS State**: Validating retrieved results are relevant
- Quality gate to prevent analyzing irrelevant data
- **ANALYZE State**: Analyzing posts, calculating sentiment distribution
- Identifying key themes
- Calculating confidence score
- **EVALUATE State**: Skipped because confidence is high (optimization)
- **REFINE State**: Skipped because confidence is high
- **CRITIQUE State**: Skipped for speed since confidence is high
- **SUMMARIZE State**: Generating comprehensive summary
- Notice how quickly this completed - plan-based execution is optimized for speed

**Screen**: 
- Show Logs tab with real-time updates
- Point to state machine showing: PLAN → EXECUTE → VALIDATE → ANALYZE → SUMMARIZE
- Highlight plan-based execution (no tool calls in logs)
- Show skipped states (EVALUATE, REFINE, CRITIQUE)

**Key Points**:
- ✅ State machine visualization shows real-time progress
- ✅ Plan-based execution (fast)
- ✅ Quality gates (VALIDATE_RESULTS)
- ✅ Smart skipping when confidence is high

---

### Results (20 seconds)

**Script Points**:
- Final result: found relevant JavaScript posts
- Analyzed sentiment distribution: positive, negative, neutral percentages
- Key insights and themes identified
- Confidence score shows certainty level
- Fast because used plan-based execution - followed simple predefined plan

**Action**: 
- Switch to Summary tab
- Scroll through results
- Point out: executive summary, sentiment breakdown, key insights, confidence score

---

## Part 4: Complex Query Demo with State Machine Explanation (2 minutes)

### Setup (15 seconds)

**Action**: 
- Click complex example: **"Compare sentiment about JavaScript vs Python, then filter by verified accounts, then show how it changed over the last 7 days."**
- Or type: `Compare sentiment about JavaScript vs Python, then filter by verified accounts, then show how it changed over the last 7 days.`
- Click Submit

**Script**: "Now a complex multi-step query - will trigger dynamic tool calling and show full state machine workflow"

---

### Execution with State Machine Walkthrough (1 minute 30 seconds)

**Script Points** (as states appear):

- **PLAN State**: 
  - Recognized as complex comparison query with multiple steps
  - Decided to use tool calling mode
  - Grok will dynamically choose tools based on intermediate results
  - Different from simple query

- **EXECUTE State - Tool Calling Mode**:
  - Watch logs - "Tools Used" section appearing
  - Grok making autonomous decisions:
    - First: `hybrid_search` to find JavaScript posts
    - Then: `hybrid_search` again for Python posts
    - Next: `filter_by_metadata` to filter by verified accounts
    - Finally: `temporal_trend_analyzer` to analyze 7-day trends
  - Each tool call visible in logs with arguments and results
  - Iterative tool selection makes complex queries powerful

- **VALIDATE_RESULTS State**:
  - Validating combined results are relevant
  - Checking if they match comparison query intent
  - More complex validation since multiple searches combined

- **ANALYZE State**:
  - Analyzing combined results
  - Comparing sentiment between JavaScript and Python
  - Looking at verified accounts specifically
  - Identifying trends over time
  - More complex than simple query

- **EVALUATE State**:
  - Evaluating if strategy worked
  - Checking if comparison is meaningful
  - Verifying temporal analysis makes sense

- **REFINE State** (if needed):
  - If confidence moderate, might refine
  - Could search with different keywords or expand date range
  - Watch for loop back to VALIDATE_RESULTS and ANALYZE
  - State machine shows cycles

- **CRITIQUE State**:
  - Quality check: claims supported?
  - Is comparison fair?
  - Any bias in analysis?

- **SUMMARIZE State**:
  - Generating comprehensive summary
  - Combines: comparison, verified filter, temporal trends

- **State Machine Cycles**:
  - Notice visualization shows cycles
  - REFINE can loop back to VALIDATE_RESULTS if refinement needed
  - This is self-correction mechanism

**Screen**: 
- Show Logs tab
- **CRITICAL**: Point out `tool_calling_mode: true` in logs
- Show "Tools Used" section expanding with each tool call
- Point to state machine visualization showing:
  - State transitions
  - Active states (blue) with model indicators
  - Transition labels ("if validated", "if refine needed")
  - Any cycles (REFINE → VALIDATE_RESULTS → ANALYZE)
- Highlight each tool call in logs

**Key Points**:
- ✅ Tool calling mode activated (different from simple query)
- ✅ State machine shows all transitions and cycles
- ✅ Grok autonomously decides which tools to use
- ✅ Self-correction through refinement cycles
- ✅ Quality gates at multiple stages

---

### Results (15 seconds)

**Script Points**:
- Comprehensive result successfully generated
- Compared sentiment between JavaScript and Python
- Filtered to only verified accounts
- Analyzed how sentiment changed over 7 days
- Detailed comparison summary provided
- Demonstrates ability to handle complex multi-step queries autonomously

**Action**: 
- Switch to Summary tab
- Show comparison results
- Point out: comparison between topics, verified filter applied, temporal analysis, comprehensive summary

---

## Part 5: Compare Results (30 seconds)

**Script Points**:

**Simple Query**:
- Used plan-based execution (faster)
- Single search operation
- Completed in ~30 seconds
- High confidence result
- Skipped EVALUATE, REFINE, CRITIQUE for speed

**Complex Query**:
- Used tool calling mode (more flexible)
- Multiple tool calls: hybrid_search (twice), filter_by_metadata, temporal_trend_analyzer
- Took longer (~1.5 minutes) but handled multi-step operations
- Went through full state machine workflow
- More comprehensive analysis

**Key Differences**:
- Simple queries optimized for speed with plan-based execution
- Complex queries use dynamic tool calling for flexibility
- State machine adapts: simple queries skip optional states, complex queries use full workflow
- Both use quality gates (VALIDATE_RESULTS) to ensure relevant results
- Agent autonomously decides which approach to use based on query complexity

**Screen**: 
- Switch between the two summary tabs
- Or show side-by-side if possible
- Highlight differences: execution mode, number of operations, time taken, states visited

---

## Conclusion (30 seconds)

**Script Points**:
- **Autonomous Decision-Making**: Agent decides execution mode, which tools to use, when to refine
- **State Machine Workflow**: 8 states with quality gates and self-correction cycles, visualized in real-time
- **Two Execution Modes**: Fast plan-based for simple queries, flexible tool calling for complex queries
- **Real-Time Visibility**: State machine visualization and detailed logs show exactly what's happening
- **Quality Assurance**: Validation, evaluation, critique, and refinement ensure high-quality results
- **Balanced System**: Simple queries are fast, complex queries are comprehensive
- Thank you for watching!

**Screen**: 
- Show final state machine visualization
- Maybe show architecture overview
- End screen

---

## Example Queries (Highly Relevant to Data)

### Simple Query (Plan-Based, Fast):
```
What's the sentiment on JavaScript?
```

**Why this works well**:
- JavaScript is a major topic in the tech category
- Lots of posts about JavaScript in the dataset
- Simple sentiment analysis query
- Will use plan-based execution (fast)
- Should get high confidence results

**Alternative Simple Queries**:
- `What are people saying about AI?`
- `Summarize sentiment on Python`
- `What's the sentiment on Premier League?`
- `What are people discussing about sustainable fashion?`

---

### Complex Query (Tool Calling, Multi-Step):
```
Compare sentiment about JavaScript vs Python, then filter by verified accounts, then show how it changed over the last 7 days.
```

**Why this works well**:
- JavaScript and Python are both major topics in tech category
- Dataset has verified accounts (like Scorsese, developers)
- Has temporal data (created_at timestamps)
- Multiple steps trigger tool calling
- Will demonstrate full state machine workflow

**Alternative Complex Queries**:
- `What do verified accounts say about sports? Filter by high engagement, then analyze sentiment.`
- `Compare discussions about AI vs Machine Learning in tech, then filter for negative sentiment, then show trends over the last week.`
- `Find posts about fashion from verified accounts, then filter by high engagement, then compare sentiment on sustainable fashion vs runway shows.`

---

## Timing Breakdown

| Section | Time | Notes |
|---------|------|-------|
| Part 1: UI Overview | 1:00 | Interface walkthrough |
| Part 2: Query Types | 0:30 | What queries are supported |
| Part 3: Simple Query | 1:00 | Fast plan-based execution (30s execution) |
| Part 4: Complex Query | 2:00 | Tool calling with state machine walkthrough (1:30 execution) |
| Part 5: Compare Results | 0:30 | Side-by-side comparison |
| Conclusion | 0:30 | Summary and wrap-up |
| **Total** | **5:30** | Can trim to fit 5 minutes |

---

## Key Visual Elements to Highlight

### UI Overview:
- ✅ Query input and example queries
- ✅ Fast mode toggle
- ✅ Model selection
- ✅ Logs and Summary tabs
- ✅ State machine visualization area

### Simple Query:
- ✅ State machine: PLAN → EXECUTE → VALIDATE → ANALYZE → SUMMARIZE
- ✅ Plan-based execution (no tool calls)
- ✅ Skipped states (EVALUATE, REFINE, CRITIQUE)
- ✅ Fast completion

### Complex Query:
- ✅ State machine showing full workflow with cycles
- ✅ Tool calling mode activation (`tool_calling_mode: true`)
- ✅ "Tools Used" section in logs
- ✅ Multiple tool calls visible
- ✅ Refinement cycles (if they occur)
- ✅ Transition labels on state machine

### Comparison:
- ✅ Execution mode difference
- ✅ Time difference
- ✅ States visited difference
- ✅ Result complexity difference

---

## Tips for Recording

### Before Recording:
- Test both queries once to ensure they work well
- Check state machine visualization appears and updates correctly
- Prepare comparison: have both query results ready
- Clear browser: use fresh session or clear cache
- Check API key: verify API key is set and has credits

### During Recording:
- Point to UI elements: use cursor to highlight important parts
- Explain state machine: walk through states as they appear
- Show tool calls: point out each tool call in complex query
- Compare clearly: make differences between simple and complex obvious
- Speak clearly: explain what's happening in real-time

### What to Speed Up:
- Execution phases: can speed up the actual running parts
- Keep normal: UI overview, state explanations, results viewing, comparison

### Key Moments:
1. ✅ State machine visualization appearing and updating
2. ✅ Tool calling mode activation (`tool_calling_mode: true`)
3. ✅ Tools Used section expanding
4. ✅ State transitions with labels
5. ✅ Refinement cycles (if they occur)
6. ✅ Comparison between simple and complex

### Backup Plans:
- If tool calling doesn't trigger: use exact complex query from examples
- If state machine doesn't show: mention it's loading and continue with logs
- If query is slow: speed up execution phase
- If API error: skip to comparison using prepared results

---

## Screen Layout Recommendations

```
┌─────────────────────────────────────────────┐
│  Browser (Full Screen)                     │
│  ┌───────────────────────────────────────┐ │
│  │  Query Input + Examples              │ │
│  │  [Fast Mode] [Model Selection]        │ │
│  │                                       │ │
│  │  ┌──────────┐ ┌──────────┐          │ │
│  │  │ Summary  │ │ Logs ✓   │          │ │
│  │  └──────────┘ └──────────┘          │ │
│  │                                       │ │
│  │  [Logs Display]                      │ │
│  │  [State Machine Visualization]        │ │
│  │                                       │ │
│  │  [Summary Display]                   │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

---

**Good luck with your demo! 🚀**
