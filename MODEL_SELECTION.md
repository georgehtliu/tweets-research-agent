# Model Selection Strategy

This document explains the rationale for selecting different Grok models for different components of the agentic workflow.

## Overview

The framework uses **grok-4-fast-reasoning** as the primary model for all reasoning tasks. This is because:

1. **Cost Efficiency**: 45x cheaper than grok-3 ($0.20/$0.50 vs $3/$15 per 1M tokens)
2. **Large Context**: 15x larger context window (2M vs 131K tokens) for better context management
3. **Fast Reasoning**: Maintains strong reasoning capabilities while being much faster
4. **Consistency**: Using the same model ensures consistent behavior across all stages
5. **Simplicity**: Easier to configure and maintain

However, the architecture is designed to allow easy switching to different models for different tasks if needed.

## Model Assignment by Component

### 1. Planner (`PLANNER_MODEL`)
- **Model**: `grok-4-fast-reasoning`
- **Why**: Planning requires complex reasoning to break down queries into actionable steps
- **Requirements**: 
  - Understanding query intent
  - Decomposing complex problems
  - Selecting appropriate tools
  - Defining success criteria
- **Alternative**: Could use a lighter model if available, but quality may suffer

### 2. Analyzer (`ANALYZER_MODEL`)
- **Model**: `grok-4-fast-reasoning`
- **Why**: Deep analysis needs sophisticated reasoning to identify patterns and insights
- **Requirements**:
  - Pattern recognition
  - Sentiment analysis
  - Theme extraction
  - Confidence assessment
- **Alternative**: This is critical - keep strong model here

### 3. Classifier (`CLASSIFIER_MODEL`)
- **Model**: `grok-4-fast-reasoning`
- **Why**: Currently using same model, but this could use a lighter/faster model
- **Requirements**:
  - Quick query type classification
  - Low latency preferred
- **Alternative**: If `grok-fast` or similar exists, use it here to reduce costs

### 4. Refiner (`REFINER_MODEL`)
- **Model**: `grok-4-fast-reasoning`
- **Why**: Refinement decisions require understanding context and determining optimal next steps
- **Requirements**:
  - Evaluating analysis quality
  - Deciding if refinement needed
  - Suggesting improvement steps
- **Alternative**: Keep strong model - critical for autonomous operation

### 5. Summarizer (`SUMMARIZER_MODEL`)
- **Model**: `grok-4-fast-reasoning`
- **Why**: High-quality summaries need strong language understanding and synthesis
- **Requirements**:
  - Synthesizing information
  - Creating coherent narratives
  - Highlighting key points
- **Alternative**: Keep strong model for best results

## Cost Optimization Strategy

If you want to optimize costs while maintaining quality:

1. **Use lighter model for classification**: Query classification is simpler, so a faster/cheaper model could work
2. **Cache common queries**: Store plans for similar queries
3. **Limit refinement iterations**: Set lower `MAX_ITERATIONS` to reduce API calls
4. **Batch processing**: Process multiple queries together if possible

## Model Availability

**Important**: The actual model names may differ based on what's available in your xAI API plan. Common model names might be:

- `grok-4-fast-reasoning` (current - recommended for cost/performance)
- `grok-4-1-fast-reasoning` (newer variant)
- `grok-3` (higher quality but 45x more expensive)
- `grok-3-mini` (cheaper but weaker reasoning)
- `grok-code-fast-1` (for code-specific tasks)

Check the [xAI documentation](https://docs.x.ai) for available models and update `config.py` accordingly.

## Updating Model Configuration

To change models, edit `config.py`:

```python
class ModelConfig:
    PLANNER_MODEL = "grok-4-fast-reasoning"      # Fast reasoning, 2M context, $0.20/$0.50
    ANALYZER_MODEL = "grok-4-fast-reasoning"     # Fast reasoning for analysis
    CLASSIFIER_MODEL = "grok-4-fast-reasoning"   # Or use grok-3-mini for cost savings
    REFINER_MODEL = "grok-4-fast-reasoning"      # Fast reasoning for refinement
    SUMMARIZER_MODEL = "grok-4-fast-reasoning"   # Fast reasoning for summaries
```

## Performance Considerations

- **Latency**: Stronger models may be slower but produce better results
- **Cost**: Stronger models cost more per token
- **Quality**: Stronger models produce more reliable plans and analysis
- **Trade-off**: Balance quality vs cost based on your needs

## Testing Different Models

To test different model configurations:

1. Update `config.py` with different model names
2. Run test queries: `python main.py --query "Your test query"`
3. Compare results quality and token usage
4. Adjust based on your requirements

## Recommendations

For the assessment:
- **Use strongest available model** for all components to demonstrate best capabilities
- **Document your choices** in your submission
- **Explain trade-offs** if you choose different models

For production:
- **Use strongest model** for planning, analysis, refinement, summarization
- **Consider lighter model** for classification if available
- **Monitor costs** and adjust based on usage patterns
