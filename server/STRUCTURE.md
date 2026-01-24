# Server Module Structure

The server has been refactored into a modular architecture for better maintainability and testability.

## Directory Structure

```
server/
├── __init__.py              # Package marker
├── app.py                   # Flask application factory
├── api_server.py            # Entry point (runs the server)
│
├── routes/                  # API route handlers (Blueprints)
│   ├── __init__.py         # Blueprint registration
│   ├── main.py             # Main routes (/, /api/health, /api/examples)
│   └── query.py            # Query endpoint (/api/query)
│
├── services/                # Business logic layer
│   ├── __init__.py
│   └── agent_service.py    # Agent initialization and management
│
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── errors.py           # Error handlers
│   └── response.py        # Response utilities
│
├── agent.py                 # Agentic workflow logic
├── config.py                # Configuration
├── context_manager.py       # Context management
├── data_generator.py        # Mock data generation
├── grok_client.py          # Grok API client
└── retrieval.py            # Hybrid retrieval system
```

## Architecture

### Application Factory Pattern (`app.py`)

The `create_app()` function creates and configures the Flask application:
- Initializes services
- Registers blueprints
- Sets up error handlers
- Configures CORS

### Routes (Blueprints)

Routes are organized into blueprints for better separation of concerns:

- **`routes/main.py`**: 
  - `GET /` - Serve web UI
  - `GET /api/health` - Health check
  - `GET /api/examples` - Example queries

- **`routes/query.py`**:
  - `POST /api/query` - Research query with SSE streaming

### Services Layer

Business logic is separated into services:

- **`services/agent_service.py`**: 
  - Manages agent lifecycle
  - Handles data loading/generation
  - Provides singleton pattern for agent instance

### Utilities

Helper functions and error handling:

- **`utils/errors.py`**: Centralized error handlers
- **`utils/response.py`**: Standardized response helpers

## Benefits

1. **Separation of Concerns**: Routes, business logic, and utilities are clearly separated
2. **Testability**: Each module can be tested independently
3. **Maintainability**: Changes to one module don't affect others
4. **Scalability**: Easy to add new routes, services, or utilities
5. **Reusability**: Services can be reused across different routes

## Usage

The entry point remains `api_server.py`:

```bash
python server/api_server.py
```

Or import the app factory for testing:

```python
from server.app import create_app
app = create_app()
```
