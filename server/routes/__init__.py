"""
Routes module - API endpoints
"""
from fastapi import APIRouter

# Create routers
main_router = APIRouter()
query_router = APIRouter(prefix="/api", tags=["query"])
evaluation_router = APIRouter(prefix="/api", tags=["evaluation"])

# Import routes to register them
from . import main, query, evaluation
