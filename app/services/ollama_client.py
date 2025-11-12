"""
Ollama Client - Infrastructure Layer

This module provides a thin HTTP client for communicating with the Ollama REST API.
It handles all network communication with the local Ollama server.

"""

from typing import List, Dict, Optional
import requests
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_TEMPERATURE = 0.2

class OllamaConnectionError(Exception):
    """Raised when unable to connect to Ollama server."""
    pass


class OllamaUnavailableError(OllamaConnectionError):
    """Raised when Ollama cannot be reached during model checks."""
    pass


def ping() -> bool:
    """
    Check if Ollama server is reachable.

    Attempts to connect to Ollama's /api/tags endpoint to verify
    the server is running and responsive.

    Returns:
        True if Ollama is reachable, False otherwise

    """
    try:
        response = requests.get(
            f"{settings.ollama_host}/api/tags",
            timeout=5
        )
        is_ok = response.ok
        logger.debug(f"Ollama ping: {'success' if is_ok else 'failed'}")
        return is_ok
    except Exception as e:
        logger.warning(f"Ollama ping failed: {e}")
        return False


def has_model(model_name: str) -> bool:
    """
    Check if a specific model is installed in Ollama.

    Queries Ollama's /api/tags endpoint and checks if the specified
    model name exists in the list of installed models.

    Args:
        model_name: Name of model to check (e.g., "phi", "mistral", "llama2")

    Returns:
        True if model is installed, False otherwise

    Note:
        Model names are compared without tags (e.g., "phi:latest" -> "phi")

    Example:
        >>> if has_model("phi"):
        ...     print("phi is installed")
        ... else:
        ...     print("Run: ollama pull phi")
    """
    try:
        response = requests.get(
            f"{settings.ollama_host}/api/tags",
            timeout=5
        )
        response.raise_for_status()

        data = response.json()
        installed_models = data.get("models", [])

        # Extract model names (without tags like ":latest")
        model_names = {
            model.get("name", "").split(":")[0]
            for model in installed_models
        }

        # Check if requested model exists (also strip tag from request)
        requested_name = model_name.split(":")[0]
        exists = requested_name in model_names

        logger.debug(
            f"Model check: {model_name} -> "
            f"{'found' if exists else 'not found'} "
            f"(installed: {model_names})"
        )

        return exists

    except (requests.Timeout, requests.ConnectionError, OSError) as e:
        logger.error(f"Connectivity issue while checking model availability: {e}")
        raise OllamaUnavailableError(str(e)) from e
    except Exception as e:
        logger.error(f"Error checking model availability: {e}")
        return False


def chat(messages, model=None, temperature: Optional[float] = None, stream: bool = False, timeout=60):
    """
    Send chat request to Ollama and get response.

    Calls Ollama's /api/chat endpoint with the provided messages
    and returns the generated response text.

    Args:
        messages: List of message dicts with 'role' and 'content' keys
        model: Model name to use (defaults to OLLAMA_MODEL from .env)
        temperature: Optional sampling temperature; defaults to 0.2 if not provided
        stream: Whether to request streaming responses (not implemented server-side yet)
        timeout: HTTP timeout in seconds

    Returns:
        Generated response text from the model

    Raises:
        RuntimeError: On any network/HTTP/shape error (מותאם לטסטים הקיימים)
    """
    model = model or settings.ollama_model
    url = f"{settings.ollama_host}/api/chat"
    effective_temperature = temperature if temperature is not None else DEFAULT_TEMPERATURE

    payload = {
        "model": model or settings.ollama_model,
        "messages": messages,
        "stream": bool(stream),  # Streaming not yet implemented
        "options": {
            "temperature": effective_temperature
        }
    }

    logger.debug(
        f"Sending chat request: model={payload['model']}, "
        f"messages={len(messages)}, temp={temperature}"
    )

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=timeout  # LLM generation can take time
        )
        response.raise_for_status()
    except (requests.Timeout, requests.ConnectionError, OSError) as e:
        logger.error(f"Ollama request failed (network/timeout): {e}")
        raise RuntimeError(f"Ollama request failed: {e}") from e
    except requests.HTTPError as e:
        status = getattr(getattr(e, "response", None), "status_code", None)
        logger.error(f"Ollama HTTP error: {status} ({e})")
        raise RuntimeError(f"Ollama HTTP error: {status}") from e
    except Exception as e:
        logger.exception("Unexpected error in Ollama chat")
        raise RuntimeError("Unexpected error communicating with Ollama") from e

    try:
        data = response.json()
        # Expected format: {"message": {"role": "assistant", "content": "..."}}
        message = data.get("message", {})
        content = message.get("content")
        if not isinstance(content, str):
            raise KeyError("message.content missing or not a string")
    except Exception as e:
        logger.error(f"Unexpected Ollama response shape: {e}")
        raise RuntimeError("Unexpected Ollama response shape") from e

    logger.info(f"Received response: {len(content)} characters")
    return content
