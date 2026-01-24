"""
Response utilities
"""
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional


def create_error_response(message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None) -> JSONResponse:
    """
    Create a standardized error response
    
    Args:
        message: Error message
        status_code: HTTP status code
        details: Optional additional details
    
    Returns:
        JSONResponse with error details
    """
    response = {
        "error": message,
        "success": False
    }
    if details:
        response["details"] = details
    
    return JSONResponse(status_code=status_code, content=response)


def create_success_response(data: Dict[str, Any], status_code: int = 200) -> Dict[str, Any]:
    """
    Create a standardized success response
    
    Args:
        data: Response data
        status_code: HTTP status code
    
    Returns:
        Dictionary with success response
    """
    return {
        "success": True,
        "data": data
    }
