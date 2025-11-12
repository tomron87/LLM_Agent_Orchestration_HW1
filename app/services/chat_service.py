"""
Chat Service - Business Logic Layer

This module contains the core business logic for processing chat requests.
It is separated from the API layer (routing) and infrastructure layer (Ollama client).

Responsibilities:
- Model selection and validation
- Message processing
- Response formatting
- Business rule enforcement
"""

from typing import List, Dict, Optional
import logging
import uuid

logger = logging.getLogger(__name__)


class ModelNotFoundError(Exception):
    """Raised when requested model is not available in Ollama."""

    def __init__(self, model: str):
        self.model = model
        super().__init__(f"Model '{model}' is not installed in Ollama")


class ChatService:
    """
    Business logic service for chat operations.

    This service handles all chat-related business logic:
    - Resolving which model to use (default or user-specified)
    - Validating model availability
    - Calling the LLM provider (Ollama)
    - Formatting responses with notices for edge cases

    Attributes:
        ollama_client: Client for communicating with Ollama
        default_model: Default model to use when not specified
    """

    def __init__(self, ollama_client, default_model: str):
        """
        Initialize the chat service.

        Args:
            ollama_client: Instance of OllamaClient for model communication
            default_model: Default model name to use (e.g., "phi", "mistral")
        """
        self.ollama_client = ollama_client
        self.default_model = default_model
        logger.info(f"ChatService initialized with default model: {default_model}")

    def process_chat(
            self,
            messages: List[Dict[str, str]],
            model: Optional[str] = None,
            session_id: Optional[str] = None,
            temperature: Optional[float] = None,
            stream: bool = False
    ) -> Dict[str, str]:
        """
        Process a chat request through the complete business logic flow.

        Flow:
        1. Resolve which model to use (explicit or default)
        2. Validate model is installed in Ollama
        3. Call Ollama to generate response
        4. Format and return response with notices if needed

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Optional model name override
            session_id: Optional session identifier

        Returns:
            Dictionary containing:
                - session_id: Session identifier
                - answer: Generated response text
                - model: Model name used
                - notice: Optional warning/notice message
                - temperature: Applied decoding temperature (implicit through Ollama client)

        Raises:
            ModelNotFoundError: If specified model is not installed

        Example:
            >>> service = ChatService(ollama_client, "phi")
            >>> result = service.process_chat(
            ...     messages=[{"role": "user", "content": "Hello"}],
            ...     model="phi"
            ... )
            >>> print(result["answer"])
            "Hi there! How can I help you?"
        """
        # Step 1: Resolve model
        selected_model = self._resolve_model(model)
        logger.info(f"Processing chat with model: {selected_model}, messages: {len(messages)}")

        # Step 2: Validate model availability
        try:
            available = self._is_model_available(selected_model)
        except self.ollama_client.OllamaUnavailableError:
            logger.exception("Ollama unreachable while checking model availability")
            raise

        if not available:
            logger.warning(f"Model not found: {selected_model}")
            return self._build_model_not_found_response(selected_model, session_id)

        # Step 3: Generate session ID if needed
        sid = session_id or self._generate_session_id()

        # Step 4: Call LLM
        try:
            answer = self.ollama_client.chat(
                messages,
                model=selected_model,
                temperature=temperature,
                stream=stream
            )
            logger.info(f"Received answer of length: {len(answer) if answer else 0}")
        except self.ollama_client.OllamaUnavailableError:
            logger.exception("Ollama unreachable during chat call")
            raise
        except Exception as e:
            logger.exception("Error calling Ollama")
            raise  # Re-raise for API layer to handle as HTTPException

        # Step 5: Handle empty response
        if not answer or not answer.strip():
            logger.warning("Model returned empty response")
            return self._build_empty_response(selected_model, sid)

        # Step 6: Success - return formatted response
        return self._build_success_response(answer, selected_model, sid)

    def _resolve_model(self, model: Optional[str]) -> str:
        """
        Determine which model to use.

        Business rule: Use explicit model if provided, otherwise default.

        Args:
            model: Optional model name from request

        Returns:
            Model name to use (stripped of whitespace)
        """
        selected = (model or self.default_model).strip()
        logger.debug(f"Resolved model: {selected}")
        return selected

    def _is_model_available(self, model: str) -> bool:
        """
        Check if model is installed in Ollama.

        Args:
            model: Model name to check

        Returns:
            True if model is available, False otherwise
        """
        return self.ollama_client.has_model(model)

    def _generate_session_id(self) -> str:
        """
        Generate a unique session identifier.

        Returns:
            Session ID in format "sess-{random_hex}"
        """
        return f"sess-{uuid.uuid4().hex[:8]}"

    def _build_model_not_found_response(
            self,
            model: str,
            session_id: Optional[str]
    ) -> Dict[str, str]:
        """
        Build response when requested model is not installed.

        Args:
            model: Name of missing model
            session_id: Optional session ID

        Returns:
            Response dict with notice about missing model
        """
        return {
            "session_id": session_id or self._generate_session_id(),
            "answer": "",
            "model": model,
            "notice": (
                f"המודל '{model}' לא מותקן ב-Ollama. "
                f"התקן עם: ollama pull {model}, או בחר מודל אחר."
            )
        }

    def _build_empty_response(self, model: str, session_id: str) -> Dict[str, str]:
        """
        Build response when model returns empty answer.

        Args:
            model: Model name used
            session_id: Session identifier

        Returns:
            Response dict with notice about empty response
        """
        return {
            "session_id": session_id,
            "answer": "",
            "model": model,
            "notice": "לא התקבלה תשובה תוכנית מהמודל. נסו לנסח אחרת או לשלוח שוב."
        }

    def _build_success_response(
            self,
            answer: str,
            model: str,
            session_id: str
    ) -> Dict[str, str]:
        """
        Build successful response with model answer.

        Args:
            answer: Generated text from model
            model: Model name used
            session_id: Session identifier

        Returns:
            Response dict with answer and metadata
        """
        return {
            "session_id": session_id,
            "answer": answer,
            "model": model,
            "notice": None
        }
