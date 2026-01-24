# Evaluation Framework Quick Start

## Run Evaluation on 10 Queries

```bash
cd server/evaluation
python evaluator.py --max-queries 10
```

## Run Full Evaluation (40 Queries)

```bash
cd server/evaluation
python evaluator.py
```

## Compare Models

```bash
cd server/evaluation
python compare_models.py --max-queries 5
```

## View Results

Results are saved to `server/evaluation/results/`:
- `evaluation_{model}_{timestamp}.json` - Full evaluation with metrics
- `model_comparison_{timestamp}.json` - Model comparison results
- `{query_id}_result.json` - Individual query results

## Example Output

```
📊 EVALUATION METRICS SUMMARY
======================================================================

✅ Completion Rate: 95.0%
   Completed: 38/40

⚙️  Step Efficiency:
   Avg Steps: 8.5
   Avg Refinement Iterations: 1.2
   Avg Replan Count: 0.1
   Avg Tokens/Query: 12500

📝 Summary Quality:
   Avg Confidence: 0.782
   High Confidence Rate: 65.0%
   Avg Summary Length: 850 chars

🤖 Autonomy Metrics:
   Autonomy Score: 0.745
   Replan Rate: 10.0%
   Refinement Rate: 35.0%
   Critique Pass Rate: 90.0%
```
