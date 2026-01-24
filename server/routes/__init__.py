"""
Routes module - API endpoints
"""
from fastapi import APIRouter

# Create routers
main_router = APIRouter()
query_router = APIRouter(prefix="/api", tags=["query"])

# Import routes to register them
from . import main, query
