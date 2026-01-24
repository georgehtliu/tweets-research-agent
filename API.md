# API Documentation

## Endpoints

### Query Endpoints

#### `POST /api/query`

Submit a research query and receive results via Server-Sent Events (SSE).

**Request Body**:
```json
{
  "query": "What are people saying about AI?",
  "fast_mode": false
}
```

**Response**: Server-Sent Events stream with progress updates:
```
data: {"type": "planning", "status": "started", "message": "Analyzing query..."}
data: {"type": "planning", "status": "completed", "steps_count": 2}
data: {"type": "executing", "status": "started", "message": "Retrieving data..."}
data: {"type": "executing", "status": "completed", "results_count": 15}
data: {"type": "analyzing", "status": "started", "message": "Analyzing results..."}
data: {"type": "analyzing", "status": "completed", "confidence": 0.75}
...
data: {"type": "complete", "result": {...}}
```

**Event Types**:
- `planning`: Plan creation progress
- `executing`: Data retrieval progress
- `analyzing`: Analysis progress
- `evaluating`: Strategy evaluation progress
- `refining`: Refinement progress
- `critiquing`: Quality critique progress
- `summarizing`: Summary generation progress
- `complete`: Final result
- `error`: Error occurred

#### `POST /api/query/compare-models`

Compare multiple models on the same query in parallel.

**Request Body**:
```json
{
  "query": "What are people saying about AI?",
  "models": ["grok-4-fast-reasoning", "grok-4-0709", "grok-3-mini"],
  "fast_mode": false
}
```

**Response**: SSE stream with model-specific progress and final comparison:
```
data: {"type": "comparison_start", "models": [...], "query": "..."}
data: {"type": "model_log", "log": {"type": "planning", "model": "grok-4-fast-reasoning", ...}}
data: {"type": "model_complete", "model": "grok-4-fast-reasoning", "status": "success", "result": {...}}
data: {"type": "comparison_complete", "summary": {...}}
```

### Evaluation Endpoints

#### `GET /api/evaluation/models`

Get list of available models for comparison.

**Response**:
```json
{
  "models": [
    {
      "name": "grok-4-fast-reasoning",
      "description": "Fast reasoning model",
      "context_size": 2000000,
      "pricing": {"input": 0.20, "output": 0.50},
      "badge": "Recommended"
    },
    ...
  ]
}
```

#### `GET /api/tweets`

Get paginated and filtered tweets.

**Query Parameters**:
- `page` (int, default: 1): Page number
- `per_page` (int, default: 20): Items per page
- `category` (string, optional): Filter by category (tech, sports, politics, fashion, art, entertainment)
- `language` (string, optional): Filter by language (en, es, fr, pt, de, ja)

**Response**:
```json
{
  "posts": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 238,
    "total_pages": 12
  }
}
```

### Utility Endpoints

#### `GET /api/health`

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-23T12:00:00Z"
}
```

#### `GET /api/examples`

Get example queries.

**Response**:
```json
{
  "examples": [
    "What are people saying about AI?",
    "Summarize sentiment on JavaScript",
    ...
  ]
}
```

## Web UI Routes

#### `GET /`

Main query interface.

#### `GET /tweets`

Tweets browsing page with pagination and filters.

## Interactive API Documentation

When the server is running, visit:
- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`
