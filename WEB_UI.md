# Web UI Guide

## Quick Start

1. **Start the API server:**
   ```bash
   cd server
   python api_server.py
   ```
   
   Or from project root:
   ```bash
   python server/api_server.py
   ```

2. **Open your browser:**
   Navigate to: `http://localhost:5000`

3. **Ask a question:**
   - Type your query in the input box
   - Click "Ask" or press Enter
   - Wait for results (usually 10-30 seconds)

## Features

### Simple Interface
- Clean, modern design
- Responsive layout (works on mobile)
- Real-time loading indicators

### Example Queries
Click any example button to quickly try:
- "What are people saying about AI safety?"
- "Find the most discussed topics this week"
- "Compare sentiment about crypto vs traditional finance"

### Results Display
The results show:
- **Query Type**: Classification of your query
- **Results Found**: Number of posts analyzed
- **Refinement Iterations**: How many refinement loops were needed
- **Total Steps**: Number of execution steps
- **Confidence**: Confidence score (0-100%)
- **Final Summary**: Comprehensive answer to your query
- **Analysis**: Detailed analysis with themes and insights
- **Execution Plan**: Steps the agent took

## API Endpoints

### POST /api/query
Submit a research query.

**Request:**
```json
{
  "query": "What are people saying about AI?"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "query": "...",
    "plan": {...},
    "analysis": {...},
    "final_summary": "...",
    ...
  }
}
```

### GET /api/health
Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "data_loaded": true
}
```

### GET /api/examples
Get example queries.

**Response:**
```json
{
  "examples": [
    "What are people saying about AI safety?",
    "Find the most discussed topics this week",
    ...
  ]
}
```

## Troubleshooting

### Server won't start
- Check if port 5000 is already in use
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify your `.env` file has `GROK_API_KEY` set

### API errors
- Check the browser console (F12) for error messages
- Verify the API server is running
- Check server logs for detailed error information

### No results
- Make sure mock data exists in `data/mock_x_data.json`
- Check that the agent initialized successfully (see `/api/health`)

## Development

### Running in Debug Mode
The server runs in debug mode by default. To disable:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

### Custom Port
Change the port in `api_server.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Static Files
Static files (HTML, CSS, JS) are served from the `static/` directory.

## Architecture

```
Browser (Frontend)
    ↓ HTTP Request
Flask API Server (api_server.py)
    ↓
AgenticResearchAgent (agent.py)
    ↓
Grok API (grok-4-fast-reasoning)
    ↓
Results → JSON Response → Browser
```

The frontend makes AJAX requests to the Flask API, which processes queries through the agentic workflow and returns JSON results that are displayed in the UI.
