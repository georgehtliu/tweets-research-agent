# Deployment & Configuration Guide

## Configuration

Edit `server/config.py` to customize:

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

### Performance Optimization Flags

```python
# Skip evaluate step if confidence > 0.85
SKIP_EVALUATE_IF_HIGH_CONFIDENCE = True

# Skip critique if confidence > 0.85
SKIP_CRITIQUE_IF_HIGH_CONFIDENCE = True

# Fast mode: skip evaluate and critique entirely
ENABLE_FAST_MODE = True
```

### Retrieval Configuration

```python
SEMANTIC_SEARCH_TOP_K = 8  # Top K results for semantic search
KEYWORD_SEARCH_TOP_K = 8   # Top K results for keyword search
HYBRID_ALPHA = 0.6         # Weight for semantic vs keyword (60% semantic, 40% keyword)
MAX_RETRIEVAL_RESULTS = 15 # Max results to return
```

## Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
GROK_API_KEY=your_api_key_here
GROK_BASE_URL=https://api.x.ai/v1
PORT=8080
```

## Docker Deployment

### Build Image

```bash
docker build -t grok-agent .
```

### Run Container

```bash
docker run -p 8080:8080 \
  -e GROK_API_KEY=your_api_key \
  -e PORT=8080 \
  grok-agent
```

### Docker Compose

```bash
docker-compose up
```

Edit `docker-compose.yml` to customize:
- Port mapping
- Environment variables
- Volume mounts for data persistence

## Production Considerations

### Security

- Never commit `.env` file with API keys
- Use environment variables in production
- Rotate API keys regularly
- Monitor token usage to avoid unexpected costs
- Use HTTPS in production (set up reverse proxy)

### Performance

- Enable fast mode for lower latency
- Adjust retrieval settings based on dataset size
- Monitor token usage and API costs
- Use embedding caching (enabled by default)
- Consider using CDN for static assets

### Scaling

- Run multiple server instances behind a load balancer
- Use shared storage for embedding cache
- Consider database for storing results instead of JSON files
- Monitor API rate limits

## Troubleshooting

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

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Change `PORT` environment variable or stop the process using the port

## Monitoring

### Token Usage

Check token usage in results:
```python
result = agent.run_workflow(query)
print(f"Total tokens: {result['total_tokens_used']}")
```

### Performance Metrics

Monitor:
- Average query time
- Token usage per query
- API error rates
- Confidence scores distribution

## Model Selection Rationale

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
