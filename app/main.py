"""
FastAPI Application Entry Point

This module initializes and configures the FastAPI application,
including middleware, CORS, and API routers.

Authors: Igor Nazarenko, Tom Ron, and Roie Gilad
Course: LLMs and MultiAgent Orchestration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from app.api.routers.chat import router as chat_router

# Initialize FastAPI application
app = FastAPI(
    title="AI Chat Local Gateway",
    description="Local LLM chat API with Ollama backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
# Allows requests from any origin (suitable for local development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
def root() -> Dict[str, Any]:
    """
    Root endpoint - service information.

    Returns basic information about the service and links to documentation.

    Returns:
        Dictionary with:
            - ok: Health status
            - service: Service name
            - docs: Link to Swagger documentation
            - health: Link to health check endpoint

    Example:
        >>> GET /
        {
            "ok": true,
            "service": "AI Chat Local Gateway",
            "docs": "/docs",
            "health": "/api/health"
        }
    """
    return {
        "ok": True,
        "service": "AI Chat Local Gateway",
        "docs": "/docs",
        "health": "/api/health"
    }


# Include API routers
app.include_router(chat_router)