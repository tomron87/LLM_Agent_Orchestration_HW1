"""
Configuration Management

This module handles loading and validating all application configuration
from environment variables (.env file).

"""

from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

# Load .env file into environment variables
load_dotenv()


def _require_env(name: str) -> str:
    """
    Get required environment variable or raise error.

    Args:
        name: Environment variable name

    Returns:
        Value of the environment variable

    Raises:
        RuntimeError: If environment variable is not set
    """
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Create a .env file based on .env.example and set {name}."
        )
    return value


class Settings(BaseModel):
    """
    Application settings loaded from environment variables.

    All settings are required and must be defined in .env file.
    See .env.example for a template.

    Attributes:
        app_api_key: Secret key for API authentication (Bearer token)
        ollama_host: URL of Ollama server (e.g., http://127.0.0.1:11434)
        ollama_model: Default model name to use (e.g., "phi", "mistral")
        api_url: Base URL for API endpoints (used by UI)

    Example .env:
        APP_API_KEY=your-secret-key-here
        OLLAMA_HOST=http://127.0.0.1:11434
        OLLAMA_MODEL=phi
        API_URL=http://127.0.0.1:8000/api
    """
    app_api_key: str = Field(..., description="API authentication key")
    ollama_host: str = Field(..., description="Ollama server URL")
    ollama_model: str = Field(..., description="Default LLM model name")
    api_url: str = Field(..., description="API base URL for UI")


# Global settings instance (singleton)
# Fails fast at startup if required env vars are missing
settings = Settings(
    app_api_key=_require_env("APP_API_KEY"),
    ollama_host=_require_env("OLLAMA_HOST"),
    ollama_model=_require_env("OLLAMA_MODEL"),
    api_url=_require_env("API_URL"),
)