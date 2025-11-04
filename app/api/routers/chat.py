"""
Chat API Router

FastAPI endpoints for chat operations.
This module handles HTTP routing only - business logic is in ChatService.

"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, conlist, confloat, constr
from typing import Optional, Literal, List, Dict, Any
import logging

from app.core.config import settings
from app.api.deps import require_api_key
from app.services.chat_service import ChatService, ModelNotFoundError
import app.services.ollama_client as ollama_client

logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    """
    Individual message in a conversation.

    Attributes:
        role: Message role (system, user, or assistant)
        content: Message text content
    """
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, description="Message content (non-empty)")


class ChatRequest(BaseModel):
    """
    Request payload for chat endpoint.

    Attributes:
        session_id: Optional session identifier for tracking conversations
        messages: List of conversation messages
        stream: Whether to stream response (not implemented yet)
        model: Optional model override (defaults to OLLAMA_MODEL from .env)
    """
    session_id: Optional[str] = Field(None, description="Session identifier")
    messages: List[ChatMessage] = Field(
        ..., min_length=1, description="Conversation messages"
    )
    stream: bool = Field(False, description="Enable streaming (not yet supported)")
    model: Optional[str] = Field(None, description="Model name override")
    temperature: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Decoding temperature in [0.0, 1.0]"
    )

class ChatResponse(BaseModel):
    """
    Response from chat endpoint.

    Attributes:
        session_id: Session identifier
        answer: Generated response text
        model: Model name used
        notice: Optional user-friendly warning/notice (not an error)
    """
    session_id: str
    answer: str
    model: str
    notice: Optional[str] = Field(None, description="User-friendly notice or warning")


# Initialize router
router = APIRouter(prefix="/api", tags=["chat"])

# Initialize chat service (singleton for this module)
chat_service = ChatService(
    ollama_client=ollama_client,
    default_model=settings.ollama_model
)


def get_chat_service() -> ChatService:
    """
    Dependency for injecting ChatService.

    Returns:
        Configured ChatService instance
    """
    return chat_service


@router.get("/health")
def health() -> Dict[str, Any]:
    """
    Health check endpoint.

    Checks if Ollama is reachable and returns system status.

    Returns:
        Dictionary with:
            - status: "ok" if system is healthy
            - ollama: boolean indicating Ollama availability
            - default_model: configured default model name

    Example:
        >>> GET /api/health
        {
            "status": "ok",
            "ollama": true,
            "default_model": "phi"
        }
    """
    available = ollama_client.ping()
    return {
        "status": "ok",
        "ollama": available,
        "default_model": settings.ollama_model,
    }


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(require_api_key)])
def chat_endpoint(
        req: ChatRequest,
        service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    """
    Process chat request with LLM.

    This endpoint:
    1. Validates authentication (via dependency)
    2. Delegates to ChatService for business logic
    3. Returns formatted response or raises HTTPException

    Args:
        req: Chat request with messages and optional model override
        service: Injected ChatService instance

    Returns:
        ChatResponse with answer and metadata

    Raises:
        HTTPException:
            - 401 if authentication fails (handled by dependency)
            - 404 if model not found
            - 502 if Ollama communication fails
    """
    logger.info(
        f"Chat request: session={req.session_id}, model={req.model}, "
        f"messages={len(req.messages)}"
    )

    try:
        # Convert Pydantic models to dicts for service layer
        messages_dict = [msg.model_dump() for msg in req.messages]

        # Delegate to service layer for all business logic
        result = service.process_chat(
            messages=messages_dict,
            model=req.model,
            session_id=req.session_id
        )

        # Return response (service already formatted it correctly)
        return ChatResponse(**result)

    except ModelNotFoundError as e:
        # Business logic exception - model not available
        logger.warning(f"Model not found: {e.model}")
        raise HTTPException(
            status_code=404,
            detail=f"Model '{e.model}' not found. Install with: ollama pull {e.model}"
        )

    except Exception as e:
        # Infrastructure or unexpected error
        logger.exception("Unexpected error in chat endpoint")
        raise HTTPException(
            status_code=502,
            detail=f"Error communicating with Ollama: {str(e)}"
        )