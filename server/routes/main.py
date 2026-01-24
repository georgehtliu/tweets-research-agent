"""
Main routes - Health check, examples, and static file serving
"""
from fastapi import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pathlib import Path
from . import main_router


@main_router.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main HTML page"""
    from app import get_client_dir
    
    index_path = get_client_dir() / 'static' / 'index.html'
    if not index_path.exists():
        raise HTTPException(
            status_code=404,
            detail={
                "error": "HTML file not found",
                "path": str(index_path),
                "exists": index_path.exists()
            }
        )
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "path": str(index_path)})


@main_router.get("/api/health")
async def health():
    """Health check endpoint"""
    from app import get_agent_service
    
    try:
        agent_service = get_agent_service()
        agent_instance, data_instance = agent_service.initialize_agent()
        return {
            "status": "healthy",
            "agent_initialized": agent_instance is not None,
            "data_loaded": data_instance is not None and len(data_instance) > 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@main_router.get("/api/examples")
async def examples():
    """Get example queries"""
    return {
        "examples": [
            "What are people saying about AI safety?",
            "Find the most discussed topics this week",
            "Compare sentiment about crypto vs traditional finance",
            "What are the main concerns about machine learning?",
            "Find posts from verified accounts about Python"
        ]
    }


# This catch-all route must be LAST to avoid intercepting API routes
# It only serves files with specific extensions
@main_router.get("/{filename:path}")
async def serve_static_files(filename: str):
    """Serve static files (CSS, JS) from root path for backward compatibility"""
    from app import get_client_dir
    
    # Only serve specific file types to avoid conflicts with API routes
    if not filename.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf')):
        raise HTTPException(status_code=404, detail="File not found")
    
    static_dir = get_client_dir() / 'static'
    file_path = static_dir / filename
    
    if file_path.exists() and file_path.is_file():
        # Determine content type
        content_type = "text/css" if filename.endswith('.css') else "application/javascript" if filename.endswith('.js') else None
        return FileResponse(str(file_path), media_type=content_type)
    
    raise HTTPException(status_code=404, detail="File not found")
