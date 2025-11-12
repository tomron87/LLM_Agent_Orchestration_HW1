# 🔌 Extensibility Guide

## Purpose

This guide explains how to extend the Local AI Chat System with new capabilities without modifying core architecture. The system was designed with extensibility in mind, using clean separation of concerns and well-defined extension points.

**Target Audience**: Developers who want to add features, integrate new services, or customize behavior.

---

## 🎯 Extension Points (Hooks)

The system provides several well-defined extension points where you can add functionality without breaking existing code.

---

### 1. Adding New Model Providers

**Current State**: System only supports Ollama as the LLM provider.

**Extension Point**: `app/services/ollama_client.py` defines the interface for LLM communication.

**How to Extend**:

#### Step 1: Create a New Client Module

Create `app/services/openai_client.py` (or any other provider):

```python
"""
OpenAI Client - Alternative LLM Provider
Implements the same interface as ollama_client.py
"""

import os
import openai
from typing import List, Dict
from app.core.config import settings

def ping() -> bool:
    """
    Check if OpenAI API is accessible.

    Returns:
        True if API key is valid and service reachable
    """
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        # Simple API call to verify connectivity
        openai.Model.list()
        return True
    except Exception:
        return False


def has_model(model_name: str) -> bool:
    """
    Check if model is available.

    Args:
        model_name: e.g., "gpt-4", "gpt-3.5-turbo"

    Returns:
        True if model accessible
    """
    try:
        models = openai.Model.list()
        return any(m.id == model_name for m in models.data)
    except Exception:
        return False


def chat(messages: List[Dict[str, str]], model: str, **kwargs) -> str:
    """
    Generate chat completion via OpenAI API.

    Args:
        messages: List of {"role": "user/assistant", "content": "..."}
        model: Model name (e.g., "gpt-4")
        **kwargs: Optional parameters (temperature, max_tokens, etc.)

    Returns:
        Generated response text

    Raises:
        RuntimeError: If API call fails
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1000)
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}")
```

#### Step 2: Create Provider Selector in ChatService

Modify `app/services/chat_service.py`:

```python
import app.services.ollama_client as ollama_client
import app.services.openai_client as openai_client

class ChatService:
    def __init__(self, default_model: str, provider: str = "ollama"):
        """
        Initialize chat service with provider selection.

        Args:
            default_model: Default model name
            provider: "ollama" or "openai" (extensible to more)
        """
        self.default_model = default_model
        self.provider = provider

        # Select client based on provider
        if provider == "ollama":
            self.client = ollama_client
        elif provider == "openai":
            self.client = openai_client
        else:
            raise ValueError(f"Unknown provider: {provider}")

        logger.info(f"ChatService initialized with provider: {provider}")

    def process_chat(self, messages, model=None, session_id=None):
        # Now uses self.client instead of self.ollama_client
        selected_model = self._resolve_model(model)

        if not self.client.has_model(selected_model):
            return self._build_model_not_found_response(selected_model, session_id)

        sid = session_id or self._generate_session_id()
        answer = self.client.chat(messages, model=selected_model)

        return self._build_success_response(answer, selected_model, sid)
```

#### Step 3: Update Configuration

Add to `.env`:

```bash
# Provider selection
LLM_PROVIDER=ollama  # or "openai"

# OpenAI configuration (if using OpenAI)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

Add to `app/core/config.py`:

```python
class Settings(BaseSettings):
    # Existing fields...

    # Provider settings
    llm_provider: str = Field(default="ollama", env="LLM_PROVIDER")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: Optional[str] = Field(default="gpt-4", env="OPENAI_MODEL")
```

**Benefits**:
- ✅ Keeps same interface - no changes to API layer
- ✅ Easy to add more providers (Claude, Cohere, etc.)
- ✅ Provider-specific logic isolated in separate modules

---

### 2. Custom Middleware

**Current State**: Only CORS middleware is configured.

**Extension Point**: `app/main.py` - middleware registration section

**How to Add Custom Middleware**:

#### Example: Request Logging Middleware

Add to `app/main.py`:

```python
from fastapi import Request
import time
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests with timing information.

    Logs: method, path, duration, status code
    """
    start_time = time.time()

    # Log incoming request
    logger.info(f"➡️  {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log response
    logger.info(
        f"⬅️  {request.method} {request.url.path} "
        f"→ {response.status_code} ({duration:.3f}s)"
    )

    # Add custom header with timing
    response.headers["X-Process-Time"] = str(duration)

    return response
```

#### Example: Rate Limiting Middleware

```python
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import HTTPException, status

# Simple in-memory rate limiter (use Redis for production)
request_counts = defaultdict(list)
RATE_LIMIT = 10  # requests per minute
RATE_WINDOW = 60  # seconds

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """
    Rate limit requests by IP address.

    Limits: 10 requests per minute per IP
    """
    client_ip = request.client.host
    now = datetime.now()

    # Clean old requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if now - req_time < timedelta(seconds=RATE_WINDOW)
    ]

    # Check rate limit
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {RATE_LIMIT} requests per minute"
        )

    # Record this request
    request_counts[client_ip].append(now)

    return await call_next(request)
```

#### Example: Custom Authentication Header Middleware

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Add security headers to all responses.
    """
    response = await call_next(request)

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"

    return response
```

**Order Matters**: Middleware is executed in registration order. Place logging first, then auth, then rate limiting.

---

### 3. Response Post-Processing Hooks

**Current State**: Responses are built in `ChatService._build_success_response()` without extensibility.

**Extension Point**: Add processor chain to `ChatService`

**How to Extend**:

#### Step 1: Define Processor Interface

Create `app/services/processors.py`:

```python
"""
Response processors - Chain of Responsibility pattern
"""

from typing import Dict, Callable

ResponseProcessor = Callable[[Dict[str, str]], Dict[str, str]]


def markdown_formatter(response: Dict[str, str]) -> Dict[str, str]:
    """
    Format code blocks in response as markdown.

    Detects code and wraps with ```language``` blocks.
    """
    answer = response["answer"]

    # Simple detection: if contains common code patterns
    if any(keyword in answer for keyword in ["def ", "class ", "import ", "function "]):
        # Wrap in code block if not already wrapped
        if not answer.startswith("```"):
            # Try to detect language
            lang = "python" if "def " in answer or "import " in answer else ""
            response["answer"] = f"```{lang}\n{answer}\n```"

    return response


def profanity_filter(response: Dict[str, str]) -> Dict[str, str]:
    """
    Filter inappropriate content from responses.

    In production, use proper content moderation API.
    """
    answer = response["answer"]

    # Simple word list (extend as needed)
    inappropriate_words = ["badword1", "badword2"]  # Add actual words

    for word in inappropriate_words:
        if word.lower() in answer.lower():
            response["notice"] = "Response filtered for inappropriate content"
            response["answer"] = "[Content filtered]"
            break

    return response


def token_counter(response: Dict[str, str]) -> Dict[str, str]:
    """
    Add token count to response metadata.
    """
    answer = response["answer"]

    # Simple approximation: ~4 chars per token
    estimated_tokens = len(answer) // 4

    response["metadata"] = response.get("metadata", {})
    response["metadata"]["estimated_tokens"] = estimated_tokens

    return response


def add_timestamp(response: Dict[str, str]) -> Dict[str, str]:
    """
    Add ISO timestamp to response.
    """
    from datetime import datetime

    response["timestamp"] = datetime.utcnow().isoformat() + "Z"

    return response
```

#### Step 2: Modify ChatService to Use Processors

Update `app/services/chat_service.py`:

```python
from typing import List
from app.services.processors import ResponseProcessor

class ChatService:
    def __init__(
        self,
        ollama_client,
        default_model: str,
        response_processors: List[ResponseProcessor] = None
    ):
        """
        Initialize chat service with optional response processors.

        Args:
            ollama_client: LLM client
            default_model: Default model name
            response_processors: List of processor functions to apply to responses
        """
        self.ollama_client = ollama_client
        self.default_model = default_model
        self.response_processors = response_processors or []
        logger.info(
            f"ChatService initialized with {len(self.response_processors)} processors"
        )

    def _build_success_response(
        self,
        answer: str,
        model: str,
        session_id: str
    ) -> Dict[str, str]:
        """
        Build success response and apply processor chain.
        """
        response = {
            "session_id": session_id,
            "answer": answer,
            "model": model,
            "notice": None
        }

        # Apply all processors in order
        for processor in self.response_processors:
            try:
                response = processor(response)
            except Exception as e:
                logger.error(f"Processor {processor.__name__} failed: {e}")
                # Continue with other processors

        return response
```

#### Step 3: Configure Processors

Update `app/api/routers/chat.py`:

```python
from app.services.processors import (
    markdown_formatter,
    profanity_filter,
    token_counter,
    add_timestamp
)

# Initialize service with processors
chat_service = ChatService(
    ollama_client=ollama_client,
    default_model=settings.ollama_model,
    response_processors=[
        add_timestamp,        # Add timestamp first
        markdown_formatter,   # Format code blocks
        token_counter,        # Count tokens
        # profanity_filter,   # Uncomment if needed
    ]
)
```

**Benefits**:
- ✅ Add/remove processors without changing core logic
- ✅ Processors are composable and testable
- ✅ Failed processors don't break the response

---

### 4. Custom Pydantic Validators

**Current State**: Basic validation in `ChatRequest` model.

**Extension Point**: `app/api/routers/chat.py` - Pydantic schemas

**How to Extend**:

```python
from pydantic import BaseModel, Field, validator, root_validator
import re

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_length=1)
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)

    @validator('messages')
    def validate_message_count(cls, v):
        """
        Ensure conversation isn't too long.

        Long conversations can cause context overflow.
        """
        if len(v) > 50:
            raise ValueError(
                "Conversation too long (max 50 messages). "
                "Start a new session."
            )
        return v

    @validator('messages')
    def validate_message_content(cls, v):
        """
        Ensure messages aren't empty or just whitespace.
        """
        for msg in v:
            if not msg.content or not msg.content.strip():
                raise ValueError("Message content cannot be empty")
        return v

    @validator('messages')
    def validate_message_length(cls, v):
        """
        Ensure individual messages aren't too long.
        """
        for msg in v:
            if len(msg.content) > 10000:  # ~2500 tokens
                raise ValueError(
                    f"Message too long ({len(msg.content)} chars). "
                    f"Maximum 10000 characters per message."
                )
        return v

    @validator('model')
    def validate_model_name(cls, v):
        """
        Ensure model name follows valid format.
        """
        if v is not None:
            # Model names should be alphanumeric with optional hyphens
            if not re.match(r'^[a-z0-9][a-z0-9-]*$', v):
                raise ValueError(
                    "Invalid model name format. "
                    "Use lowercase letters, numbers, and hyphens only."
                )
        return v

    @validator('temperature')
    def warn_high_temperature(cls, v):
        """
        Log warning for high temperature values.
        """
        if v is not None and v > 0.8:
            logger.warning(
                f"High temperature ({v}) may cause inconsistent responses"
            )
        return v

    @root_validator
    def validate_request_combination(cls, values):
        """
        Validate combinations of fields.

        Example: Certain models may not support temperature.
        """
        model = values.get('model')
        temp = values.get('temperature')

        # Example rule: Some models might have fixed temperature
        if model == "phi:latest" and temp is not None and temp != 0.2:
            logger.info(
                f"Model {model} works best with temperature=0.2, "
                f"but {temp} was requested"
            )

        return values
```

**Custom Validator for Hebrew Text**:

```python
@validator('messages')
def support_hebrew_content(cls, v):
    """
    Ensure Hebrew text is properly handled.

    Hebrew uses UTF-8, so verify encoding.
    """
    for msg in v:
        try:
            # Verify UTF-8 encoding works
            msg.content.encode('utf-8')
        except UnicodeEncodeError:
            raise ValueError("Message contains invalid characters")
    return v
```

---

### 5. Authentication Extensions

**Current State**: Simple Bearer token authentication in `app/api/deps.py`.

**Extension Point**: Replace `require_api_key` dependency

**How to Extend**:

#### Option A: API Key with Database

Create `app/api/auth.py`:

```python
"""
Enhanced authentication with database-backed API keys
"""

from fastapi import Header, HTTPException, status
from typing import Optional
import hashlib

# In production, use actual database (PostgreSQL, MongoDB, etc.)
API_KEYS_DB = {
    "user1_hashed_key": {"user_id": "user1", "permissions": ["read", "write"]},
    "user2_hashed_key": {"user_id": "user2", "permissions": ["read"]},
}

def hash_api_key(key: str) -> str:
    """Hash API key for storage."""
    return hashlib.sha256(key.encode()).hexdigest()


async def require_api_key_with_permissions(
    authorization: str = Header(default=""),
    required_permission: str = "read"
) -> dict:
    """
    Validate API key and check permissions.

    Returns:
        User info dict with user_id and permissions
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token"
        )

    token = authorization.split(" ", 1)[1].strip()
    hashed = hash_api_key(token)

    # Check if key exists
    user_info = API_KEYS_DB.get(hashed)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    # Check permissions
    if required_permission not in user_info["permissions"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {required_permission} required"
        )

    return user_info
```

Use in routes:

```python
from app.api.auth import require_api_key_with_permissions

@router.post("/chat")
async def chat(
    request: ChatRequest,
    user_info: dict = Depends(require_api_key_with_permissions)
):
    # Now you have user_info with user_id
    logger.info(f"Chat request from user: {user_info['user_id']}")
    ...
```

#### Option B: JWT Token Authentication

```python
"""
JWT-based authentication
"""

import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Header

SECRET_KEY = "your-secret-key-here"  # Load from settings
ALGORITHM = "HS256"

def create_jwt_token(user_id: str, expires_delta: timedelta = None) -> str:
    """Create JWT token for user."""
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    payload = {
        "user_id": user_id,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def require_jwt_token(authorization: str = Header(default="")) -> dict:
    """Validate JWT token."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token"
        )

    token = authorization.split(" ", 1)[1].strip()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

---

## 🚀 Recommended Future Extensions

These are well-scoped extensions that build on the current architecture:

---

### 1. RAG (Retrieval Augmented Generation) 🌟 **High Priority**

**Purpose**: Enable chat with your documents (PDFs, docs, websites)

**Effort**: Medium (2-3 days)

**Architecture**:

```
app/services/rag_service.py         # Document loading, chunking, embedding
app/services/vector_store.py        # ChromaDB/FAISS integration
app/api/routers/documents.py        # Upload/manage documents
```

**Extension Points**:
- Modify `ChatService.process_chat()` to inject retrieved context
- Add document upload endpoint
- Add vector database initialization

**Implementation Sketch**:

```python
# app/services/rag_service.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma

class RAGService:
    def __init__(self, persist_directory="./chroma_db"):
        self.embeddings = OllamaEmbeddings(model="phi")
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )

    def add_documents(self, texts: List[str]):
        """Add documents to vector store."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = splitter.split_text("\n\n".join(texts))
        self.vectorstore.add_texts(chunks)

    def retrieve_context(self, query: str, k: int = 3) -> str:
        """Retrieve relevant context for query."""
        docs = self.vectorstore.similarity_search(query, k=k)
        return "\n\n".join([doc.page_content for doc in docs])


# Modify ChatService
class ChatService:
    def __init__(self, ollama_client, default_model, rag_service=None):
        self.rag_service = rag_service
        ...

    def process_chat(self, messages, model=None, session_id=None, use_rag=False):
        if use_rag and self.rag_service:
            # Get user's last message
            last_message = messages[-1]["content"]

            # Retrieve relevant context
            context = self.rag_service.retrieve_context(last_message)

            # Inject context as system message
            messages_with_context = [
                {"role": "system", "content": f"Context:\n{context}"}
            ] + messages

            return self._process_with_context(messages_with_context, model, session_id)

        return self._process_normal(messages, model, session_id)
```

**Benefits**:
- ✅ Chat with your own documents
- ✅ Reduces hallucinations
- ✅ Enables domain-specific knowledge

---

### 2. Streaming Responses 🌟 **High Priority**

**Purpose**: Stream LLM responses token-by-token for better UX

**Effort**: Medium (2 days)

**Extension Points**:
- Add streaming endpoint in `chat.py`
- Modify `ollama_client.chat()` to support streaming
- Update Streamlit UI to handle Server-Sent Events

**Implementation**:

```python
# app/services/ollama_client.py
def chat_stream(messages: List[Dict], model: str):
    """
    Stream chat response token by token.

    Yields:
        str: Individual tokens as they arrive
    """
    url = f"{settings.ollama_host}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": True  # Enable streaming
    }

    with requests.post(url, json=payload, stream=True, timeout=120) as response:
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "message" in data and "content" in data["message"]:
                    yield data["message"]["content"]


# app/api/routers/chat.py
from fastapi.responses import StreamingResponse

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat response using Server-Sent Events.
    """
    async def generate():
        for token in ollama_client.chat_stream(
            request.messages,
            model=request.model or settings.ollama_model
        ):
            yield f"data: {json.dumps({'token': token})}\n\n"

        # Send completion signal
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

**UI Integration** (Streamlit):

> **Note:** Layout lives in `ui/streamlit_app.py`, while reusable helpers (health checks, payload builders, history renderers) live in `ui/components.py`. Add new non-visual logic there to keep the UI file focused on layout.

```python
# ui/streamlit_app.py
def stream_chat_response(api_url, messages):
    """Handle streaming response from API."""
    response_placeholder = st.empty()
    accumulated_text = ""

    with requests.post(
        f"{api_url}/stream",
        json={"messages": messages},
        stream=True
    ) as resp:
        for line in resp.iter_lines():
            if line.startswith(b"data: "):
                data = json.loads(line[6:])
                if "token" in data:
                    accumulated_text += data["token"]
                    response_placeholder.markdown(accumulated_text)

    return accumulated_text
```

---

### 3. Conversation History Persistence 🌟 **Medium Priority**

**Purpose**: Save conversations to database for later retrieval

**Effort**: Low-Medium (1-2 days)

**Architecture**:

```
app/services/session_store.py       # SQLite/Redis backend
app/models/conversation.py          # Pydantic models for DB
```

**Implementation**:

```python
# app/services/session_store.py
import sqlite3
from datetime import datetime
import json

class SessionStore:
    def __init__(self, db_path="./conversations.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                session_id TEXT PRIMARY KEY,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TEXT,
                FOREIGN KEY (session_id) REFERENCES conversations(session_id)
            )
        """)
        self.conn.commit()

    def save_message(self, session_id: str, role: str, content: str):
        """Save message to conversation history."""
        now = datetime.utcnow().isoformat()

        # Create conversation if doesn't exist
        self.conn.execute("""
            INSERT OR IGNORE INTO conversations (session_id, created_at, updated_at)
            VALUES (?, ?, ?)
        """, (session_id, now, now))

        # Save message
        self.conn.execute("""
            INSERT INTO messages (session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        """, (session_id, role, content, now))

        # Update conversation timestamp
        self.conn.execute("""
            UPDATE conversations SET updated_at = ? WHERE session_id = ?
        """, (now, session_id))

        self.conn.commit()

    def get_conversation(self, session_id: str) -> List[Dict]:
        """Retrieve full conversation history."""
        cursor = self.conn.execute("""
            SELECT role, content, timestamp
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """, (session_id,))

        return [
            {"role": row[0], "content": row[1], "timestamp": row[2]}
            for row in cursor.fetchall()
        ]
```

**Integration**:

```python
# Modify ChatService
class ChatService:
    def __init__(self, ollama_client, default_model, session_store=None):
        self.session_store = session_store
        ...

    def process_chat(self, messages, model=None, session_id=None):
        result = self._process_normal(messages, model, session_id)

        # Save to history if store available
        if self.session_store:
            # Save user message
            last_user_msg = messages[-1]
            self.session_store.save_message(
                result["session_id"],
                last_user_msg["role"],
                last_user_msg["content"]
            )

            # Save assistant response
            self.session_store.save_message(
                result["session_id"],
                "assistant",
                result["answer"]
            )

        return result
```

---

### 4. Multi-Model Routing 🌟 **Medium Priority**

**Purpose**: Automatically select best model based on query type

**Effort**: Low (1 day)

**Implementation**:

```python
# app/services/model_router.py
import re

class ModelRouter:
    """
    Route queries to appropriate models based on content.
    """

    def select_model(self, query: str) -> str:
        """
        Select optimal model for query.

        Rules:
        - Code-related: Use codellama
        - Math/logic: Use phi (fast, accurate)
        - Creative writing: Use mistral (more creative)
        - General: Use phi (default)
        """
        query_lower = query.lower()

        # Code detection
        if any(keyword in query_lower for keyword in [
            "code", "python", "javascript", "function", "class", "debug"
        ]):
            return "codellama"

        # Math detection
        if any(keyword in query_lower for keyword in [
            "calculate", "math", "equation", "solve", "compute"
        ]):
            return "phi"

        # Creative detection
        if any(keyword in query_lower for keyword in [
            "write a story", "poem", "creative", "imagine"
        ]):
            return "mistral"

        # Default
        return "phi"


# Use in ChatService
class ChatService:
    def __init__(self, ollama_client, default_model, use_smart_routing=False):
        self.model_router = ModelRouter() if use_smart_routing else None
        ...

    def process_chat(self, messages, model=None, session_id=None):
        if not model and self.model_router:
            # Auto-select model based on last user message
            last_message = messages[-1]["content"]
            model = self.model_router.select_model(last_message)
            logger.info(f"Auto-selected model: {model}")

        return self._process_normal(messages, model, session_id)
```

---

### 5. Observability & Monitoring 🌟 **Low Priority**

**Purpose**: Add Prometheus metrics and structured logging

**Effort**: Low-Medium (1-2 days)

**Implementation**:

```python
# app/middleware/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Request
import time

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

llm_request_duration = Histogram(
    'llm_request_duration_seconds',
    'LLM request duration',
    ['model']
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Collect Prometheus metrics."""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type="text/plain")
```

---

## 🛠️ Maintenance Guidelines

### When Adding Extensions:

1. **✅ Document**: Update this guide with new extension points
2. **✅ Test**: Add unit tests for new functionality (maintain 80%+ coverage)
3. **✅ Backward Compatibility**: Don't break existing APIs without major version bump
4. **✅ Configuration**: Add new settings to `.env.example` with documentation
5. **✅ Architecture**: Update `Architecture.md` if structure changes significantly
6. **✅ PRD**: Update acceptance criteria in `PRD.md` if adding user-facing features

### Coding Conventions:

- **Follow existing three-layer pattern**: API → Business Logic → Infrastructure
- **Keep separation of concerns**: Each module has single responsibility
- **Add type hints**: Use Python typing for all function signatures
- **Write docstrings**: Google-style docstrings for all public functions
- **Write tests alongside code**: TDD or tests-first approach
- **Update README**: If user-facing changes, document in README.md

### Testing New Extensions:

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific extension tests
pytest tests/test_your_extension.py -v
```

---

## 📚 Further Reading

- **FastAPI Middleware**: https://fastapi.tiangolo.com/tutorial/middleware/
- **Pydantic Validators**: https://docs.pydantic.dev/latest/usage/validators/
- **LangChain**: https://python.langchain.com/docs/get_started/introduction
- **Ollama API**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **Prometheus Python Client**: https://github.com/prometheus/client_python

---

**Questions or suggestions?** Open an issue on GitHub or contribute to this guide!
