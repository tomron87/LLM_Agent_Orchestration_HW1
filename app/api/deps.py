"""
API Dependencies

This module contains FastAPI dependencies used across API endpoints,
primarily for authentication and authorization.

"""

from fastapi import Header, HTTPException, status
from app.core.config import settings


def require_api_key(authorization: str = Header(default="")) -> str:
    """
    FastAPI dependency for API key authentication.

    Validates that requests include a valid Bearer token in the
    Authorization header. The token must match APP_API_KEY from .env.

    Args:
        authorization: Authorization header value (automatically injected by FastAPI)

    Returns:
        The validated API key/token

    Raises:
        HTTPException: 401 Unauthorized if:
            - Authorization header is missing
            - Header doesn't start with "Bearer "
            - Token doesn't match configured APP_API_KEY

    Example:
        >>> @router.post("/chat", dependencies=[Depends(require_api_key)])
        >>> def chat_endpoint():
        ...     # This only runs if auth succeeds
        ...     pass

    Usage in request:
        >>> curl -H "Authorization: Bearer your-secret-key" \\
        ...      http://localhost:8000/api/chat
    """
    # Check if header starts with "Bearer "
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token. Use header: Authorization: Bearer <key>"
        )

    # Extract token (everything after "Bearer ")
    token = authorization.split(" ", 1)[1].strip()

    # Validate token matches configured key
    if token != settings.app_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return token