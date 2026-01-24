"""
FastAPI Application Factory
Creates and configures the FastAPI app with modular components
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import sys

# Add server directory to path for imports
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

# Import routers
from routes import main_router, query_router
from utils.errors import register_error_handlers
from services import AgentService

# Global instances (initialized in create_app)
_agent_service: AgentService = None
_project_root: Path = None
_client_dir: Path = None


def create_app(project_root: Path = None, client_dir: Path = None) -> FastAPI:
    """
    Create and configure FastAPI application
    
    Args:
        project_root: Path to project root directory
        client_dir: Path to client directory
    
    Returns:
        Configured FastAPI application
    """
    global _agent_service, _project_root, _client_dir
    
    # Set defaults
    if project_root is None:
        _project_root = Path(__file__).parent.parent
    else:
        _project_root = Path(project_root)
    
    if client_dir is None:
        _client_dir = _project_root / 'client'
    else:
        _client_dir = Path(client_dir)
    
    # Create FastAPI app
    app = FastAPI(
        title="Grok Agentic Research API",
        description="API for agentic research workflow using Grok models",
        version="1.0.0"
    )
    
    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify actual origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize services
    _agent_service = AgentService(_project_root)
    
    # Include routers (must be before static file mounting for route precedence)
    app.include_router(main_router)
    app.include_router(query_router)
    
    # Mount static files (after routers to avoid conflicts)
    static_dir = _client_dir / 'static'
    if static_dir.exists():
        # Mount static files at /static prefix
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def get_agent_service() -> AgentService:
    """Get the agent service instance"""
    if _agent_service is None:
        raise RuntimeError("Agent service not initialized. Call create_app() first.")
    return _agent_service


def get_project_root() -> Path:
    """Get the project root path"""
    if _project_root is None:
        raise RuntimeError("Project root not initialized. Call create_app() first.")
    return _project_root


def get_client_dir() -> Path:
    """Get the client directory path"""
    if _client_dir is None:
        raise RuntimeError("Client directory not initialized. Call create_app() first.")
    return _client_dir
