# Project Structure

This document explains the reorganized project structure with separate `client/` and `server/` folders.

## Directory Layout

```
Grok-takehome/
├── server/                    # Backend/server-side code
│   ├── __init__.py           # Package marker
│   ├── api_server.py         # Flask API server (main entry point for web UI)
│   ├── main.py               # CLI entry point
│   ├── agent.py              # Core agentic workflow
│   ├── grok_client.py        # Grok API client
│   ├── retrieval.py          # Hybrid retrieval system
│   ├── context_manager.py   # Context and execution tracking
│   ├── data_generator.py    # Mock X data generator
│   ├── config.py            # Configuration settings
│   └── test_setup.py        # Setup verification script
│
├── client/                   # Frontend/client-side code
│   └── static/              # Static web files
│       ├── index.html       # Main HTML page
│       ├── style.css        # CSS styles
│       └── script.js        # Frontend JavaScript
│
├── data/                     # Generated mock data
│   └── mock_x_data.json
│
├── output/                   # Research results
│   └── research_result.json
│
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
└── README.md                 # Main documentation
```

## Running the Application

### Web UI (Recommended)
```bash
# From project root
python server/api_server.py

# Or from server directory
cd server
python api_server.py
```

Then open: `http://localhost:5000`

### CLI Mode
```bash
# From project root
python server/main.py

# Or from server directory
cd server
python main.py
```

## Path Handling

All server code uses relative paths that are resolved relative to the project root:
- Data files: `data/mock_x_data.json` (resolved to project root)
- Output files: `output/research_result.json` (resolved to project root)
- Client files: `client/static/` (served by Flask)

The API server automatically:
- Sets up paths relative to project root
- Serves static files from `client/static/`
- Initializes the agent with correct data paths

## Development

### Adding New Server Files
Place all server-side Python files in the `server/` directory. They can import from each other directly since they're in the same package.

### Adding New Client Files
Place all frontend files (HTML, CSS, JS) in `client/static/`. The Flask server automatically serves them.

### Testing
```bash
cd server
python test_setup.py
```

## Benefits of This Structure

1. **Clear Separation**: Client and server code are clearly separated
2. **Easy Deployment**: Can deploy client and server separately if needed
3. **Better Organization**: Related files are grouped together
4. **Scalability**: Easy to add more client or server components
