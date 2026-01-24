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

### Prerequisites

- Docker installed ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (usually included with Docker Desktop)
- Grok API key

### Quick Start with Docker Compose (Recommended)

1. **Create `.env` file**:
```bash
cp .env.example .env
```

2. **Edit `.env` and add your API key**:
```bash
GROK_API_KEY=your_api_key_here
GROK_BASE_URL=https://api.x.ai/v1
PORT=8080
```

3. **Start the container**:
```bash
docker-compose up
```

4. **Access the application**:
   - Web UI: http://localhost:8080
   - API Docs: http://localhost:8080/docs

5. **Stop the container**:
```bash
docker-compose down
```

### Docker Compose Options

**Run in detached mode (background)**:
```bash
docker-compose up -d
```

**View logs**:
```bash
docker-compose logs -f
```

**Rebuild after code changes**:
```bash
docker-compose up --build
```

**Stop and remove containers**:
```bash
docker-compose down
```

**Stop and remove containers + volumes**:
```bash
docker-compose down -v
```

### Docker Compose Configuration

Edit `docker-compose.yml` to customize:

- **Port mapping**: Change `${PORT:-8080}:8080` to use a different host port
- **Environment variables**: Add more variables in the `environment` section
- **Volume mounts**: Adjust paths for data, output, and logs persistence
- **Resource limits**: Add `deploy.resources` section for CPU/memory limits

Example with custom port and resource limits:
```yaml
services:
  grok-agent:
    ports:
      - "9000:8080"  # Host port 9000 -> Container port 8080
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Manual Docker Build

#### Build Image

```bash
docker build -t grok-agent .
```

#### Run Container

**Basic run**:
```bash
docker run -p 8080:8080 \
  -e GROK_API_KEY=your_api_key \
  grok-agent
```

**With volumes for data persistence**:
```bash
docker run -p 8080:8080 \
  -e GROK_API_KEY=your_api_key \
  -e GROK_BASE_URL=https://api.x.ai/v1 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  grok-agent
```

**With custom port**:
```bash
docker run -p 9000:8080 \
  -e GROK_API_KEY=your_api_key \
  -e PORT=8080 \
  grok-agent
```

**Run in detached mode**:
```bash
docker run -d \
  --name grok-agent \
  -p 8080:8080 \
  -e GROK_API_KEY=your_api_key \
  grok-agent
```

**View logs**:
```bash
docker logs -f grok-agent
```

**Stop container**:
```bash
docker stop grok-agent
docker rm grok-agent
```

### Dockerfile Details

The Dockerfile:
- Uses Python 3.11 slim base image
- Installs system dependencies (gcc for some Python packages)
- Copies requirements and installs Python dependencies
- Copies application code
- Creates necessary directories
- Exposes port 8080
- Includes health check
- Runs the API server

### Volume Mounts

The following directories are mounted as volumes for data persistence:

- `./data` → `/app/data`: Mock data and embedding cache
- `./output` → `/app/output`: Research results
- `./logs` → `/app/logs`: Application logs
- `./server/evaluation/results` → `/app/server/evaluation/results`: Evaluation results

**Important**: Without volume mounts, data will be lost when the container stops.

### Environment Variables

Required:
- `GROK_API_KEY`: Your Grok API key (required)

Optional:
- `GROK_BASE_URL`: API base URL (default: `https://api.x.ai/v1`)
- `PORT`: Server port (default: `8080`)
- `PYTHONUNBUFFERED`: Set to `1` for immediate log output

### Health Check

The container includes a health check that:
- Checks `/api/health` endpoint every 30 seconds
- Times out after 10 seconds
- Retries 3 times before marking unhealthy
- Starts checking after 10 seconds

View health status:
```bash
docker ps  # Shows health status
docker inspect grok-agent | grep Health
```

### Troubleshooting Docker

#### Container won't start
```bash
# Check logs
docker-compose logs

# Check if port is already in use
lsof -i :8080

# Try rebuilding
docker-compose up --build
```

#### API key not working
```bash
# Verify environment variable is set
docker-compose exec grok-agent env | grep GROK_API_KEY

# Or check in running container
docker exec grok-agent env | grep GROK_API_KEY
```

#### Data not persisting
- Ensure volumes are mounted correctly in `docker-compose.yml`
- Check volume paths exist on host
- Verify write permissions

#### Container keeps restarting
```bash
# Check logs for errors
docker-compose logs -f

# Check health status
docker ps
```

#### Out of memory
- Reduce dataset size
- Add memory limits in `docker-compose.yml`
- Use smaller base image or optimize Dockerfile

### Production Docker Deployment

For production, consider:

1. **Use specific image tags** instead of `latest`
2. **Add resource limits** in docker-compose.yml
3. **Use secrets management** for API keys (Docker secrets, AWS Secrets Manager, etc.)
4. **Set up reverse proxy** (nginx, Traefik) for HTTPS
5. **Use Docker Swarm or Kubernetes** for orchestration
6. **Set up logging aggregation** (ELK stack, CloudWatch, etc.)
7. **Monitor container health** and set up alerts
8. **Use multi-stage builds** to reduce image size
9. **Scan images** for vulnerabilities
10. **Use read-only filesystem** where possible

Example production docker-compose.yml additions:
```yaml
services:
  grok-agent:
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    security_opt:
      - no-new-privileges:true
    read_only: false  # Set to true if possible
```

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
