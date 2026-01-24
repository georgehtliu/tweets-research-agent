# Evaluation Framework

Comprehensive evaluation framework for testing the agentic research workflow with multiple queries and comparing different Grok model variants.

## Overview

This evaluation framework provides:
- **Batch Evaluation**: Run agent on 20-40 test queries
- **Metrics Collection**: Completion rate, step efficiency, summary quality, autonomy metrics
- **Model Comparison**: Compare performance across different Grok models
- **Category Breakdown**: Metrics broken down by query category and complexity

## Quick Start

### Run Batch Evaluation

Evaluate agent on all test queries:
```bash
cd server/evaluation
python evaluator.py
```

Evaluate on subset of queries:
```bash
python evaluator.py --max-queries 10
```

Use custom queries file:
```bash
python evaluator.py --queries path/to/queries.json
```

### Compare Models

Compare different Grok models:
```bash
python compare_models.py
```

Compare specific models:
```bash
python compare_models.py --models grok-4-fast-reasoning grok-3
```

Compare on subset of queries (faster):
```bash
python compare_models.py --max-queries 5
```

## Test Queries

The `test_queries.json` file contains 40 diverse queries covering:

- **Categories**: trend_analysis, info_extraction, comparison, temporal, sentiment, complex, edge_case, multilingual, specific, broad, filtering, synthesis, etc.
- **Complexity Levels**: low, medium, high
- **Edge Cases**: sarcasm, ambiguity, conflicting sources, threaded discussions

## Metrics Calculated

### Completion Rate
- Percentage of queries successfully completed
- Total vs completed vs failed

### Step Efficiency
- Average execution steps per query
- Average refinement iterations
- Average replan count
- Average tokens per query
- Min/max steps and tokens

### Summary Quality
- Average confidence score
- High confidence rate (>= 0.8)
- Average summary length
- Quality distribution (high/medium/low)

### Autonomy Metrics
- Replan rate (how often strategy needs revision)
- Refinement rate (how often additional searches needed)
- Critique pass rate (how often critique finds issues)
- Overall autonomy score (higher = more autonomous)

### Category Breakdown
- Metrics broken down by query category
- Metrics broken down by complexity level

## Output Files

### Individual Results
- `results/{query_id}_result.json` - Individual query results (if `--no-individual` not used)

### Evaluation Results
- `results/evaluation_{model}_{timestamp}.json` - Full evaluation with metrics

### Model Comparison
- `results/model_comparison_{timestamp}.json` - Comparison across models

## Example Usage

### Evaluate Default Model
```bash
python evaluator.py --max-queries 20 --delay 2.0
```

### Compare Models
```bash
python compare_models.py --max-queries 10 --models grok-4-fast-reasoning grok-3
```

### Custom Output
```bash
python evaluator.py --output results/my_evaluation.json
```

## Interpreting Results

### Good Metrics
- **Completion Rate**: > 90%
- **Avg Confidence**: > 0.7
- **Avg Steps**: < 10
- **Autonomy Score**: > 0.7

### Areas for Improvement
- Low completion rate → Check error handling, API issues
- Low confidence → Improve retrieval or analysis prompts
- High step count → Optimize workflow, reduce unnecessary steps
- Low autonomy → Agent needs more refinement/replanning

## Adding New Models

Edit `compare_models.py` and add to `MODEL_CONFIGS`:

```python
MODEL_CONFIGS = {
    "grok-4-fast-reasoning": {...},
    "your-new-model": {
        "PLANNER_MODEL": "your-new-model",
        "ANALYZER_MODEL": "your-new-model",
        "REFINER_MODEL": "your-new-model",
        "SUMMARIZER_MODEL": "your-new-model"
    }
}
```

## Adding New Test Queries

Edit `test_queries.json` and add to the `queries` array:

```json
{
  "id": "new_query_001",
  "category": "your_category",
  "complexity": "medium",
  "query": "Your test query here",
  "expected_themes": ["theme1", "theme2"],
  "description": "What this query tests"
}
```

## Command Line Options

### evaluator.py
- `--queries`: Path to test queries JSON file
- `--max-queries`: Maximum number of queries to run
- `--delay`: Delay between queries in seconds (default: 1.0)
- `--output`: Output file path
- `--model`: Model name to use (overrides all model configs)
- `--no-individual`: Don't save individual result files

### compare_models.py
- `--queries`: Path to test queries JSON file
- `--max-queries`: Maximum queries per model
- `--delay`: Delay between queries in seconds
- `--output`: Output file path
- `--models`: Specific models to compare (space-separated)
