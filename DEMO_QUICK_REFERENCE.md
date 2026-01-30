# Demo Quick Reference Card

## Timing (4-5 minutes total)

| Section | Time | Action |
|---------|------|--------|
| Intro | 30s | Explain what the system does |
| Simple Query 1 | 1:00 | "Summarize sentiment on JavaScript" |
| Simple Query 2 | 0:45 | "What are people saying about AI?" |
| Complex Query | 2:00 | "Compare JS vs Python → verified → 7-day" |
| Conclusion | 0:30 | Wrap up |

---

## Key Points to Mention

### Introduction
- ✅ Autonomous AI research agent
- ✅ State machine: Plan → Execute → Analyze → Evaluate → Refine → Critique → Summarize
- ✅ Makes decisions on its own

### Simple Queries
- ✅ Fast execution (plan-based)
- ✅ Real-time progress visible
- ✅ High confidence results
- ✅ No tool calling (optimized for speed)

### Complex Query
- ✅ **Tool calling activated** (`tool_calling_mode: true`)
- ✅ Grok decides which tools to use
- ✅ Shows "Tools Used" section
- ✅ Multiple tools: hybrid_search, filter_by_metadata, temporal_trend_analyzer
- ✅ More flexible but slower

### Conclusion
- ✅ Autonomous decision-making
- ✅ Two execution modes
- ✅ Real-time visibility
- ✅ Self-correcting
- ✅ Optimized for speed

---

## Exact Queries to Use

### Simple 1:
```
Summarize sentiment on JavaScript
```

### Simple 2:
```
What are people saying about AI?
```

### Complex (MUST trigger tool calling):
```
Compare sentiment about JavaScript vs Python, then filter by verified accounts, then show how it changed over the last 7 days.
```

---

## What to Show in UI

### During Execution:
1. **Logs Tab** (default) - Show real-time updates
2. **State transitions** - Planning → Executing → Analyzing → etc.
3. **Tool calls** - For complex query, show "Tools Used" section
4. **Progress bars** - If comparing models

### In Results:
1. **Summary Tab** - Show formatted results
2. **Confidence score** - Highlight this
3. **Sentiment breakdown** - For sentiment queries
4. **Themes/Findings** - For trend queries
5. **Comparison** - For complex queries

---

## Troubleshooting

**If tool calling doesn't trigger:**
- Use the exact complex query from examples
- Check logs for `use_tool_calling: true` in planning

**If query is slow:**
- Say "Let me speed this up" and fast-forward
- Or use fast mode checkbox

**If confidence is low:**
- Mention "The agent identified lower confidence and could refine if needed"

**If API error:**
- Skip to next query
- Say "Let me try another example"

---

## Screen Layout

```
┌─────────────────────────────────────┐
│  Browser Window (Full Screen)      │
│                                     │
│  [Query Input] [Submit]             │
│                                     │
│  ┌──────────┐ ┌──────────┐         │
│  │ Summary  │ │ Logs ✓   │         │
│  └──────────┘ └──────────┘         │
│                                     │
│  [Logs/Results Display]             │
│                                     │
└─────────────────────────────────────┘
```

---

## Key Phrases

- "As you can see in the logs..."
- "Notice how the agent..."
- "This demonstrates..."
- "The agent autonomously decided to..."
- "Unlike the simple queries, this one uses..."
- "Here's the comprehensive result..."

---

**Keep this open while recording! 📝**
