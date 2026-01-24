"""
API Server Entry Point
Creates and runs the FastAPI application using Uvicorn
"""
import os
import uvicorn
from pathlib import Path
from app import create_app, get_client_dir, get_project_root

# Create the FastAPI app
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 8080))
    
    project_root = get_project_root()
    client_dir = get_client_dir()
    
    print("\n" + "="*70)
    print("🚀 Starting Grok Agentic Research API Server (FastAPI)")
    print("="*70)
    print("\nAPI Endpoints:")
    print("  GET  /              - Web UI")
    print("  POST /api/query     - Submit research query")
    print("  GET  /api/health    - Health check")
    print("  GET  /api/examples  - Get example queries")
    print("  GET  /docs          - Swagger UI documentation")
    print("  GET  /redoc         - ReDoc documentation")
    print(f"\nClient directory: {client_dir}")
    print(f"Project root: {project_root}")
    print(f"\n🌐 Server running on: http://localhost:{port}")
    print(f"📚 API docs available at: http://localhost:{port}/docs")
    print("\n" + "="*70 + "\n")
    
    # Disable reload in Docker/production environments
    reload_enabled = os.getenv("ENVIRONMENT", "development") == "development" and not os.path.exists("/.dockerenv")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=reload_enabled,
        log_level="info"
    )
