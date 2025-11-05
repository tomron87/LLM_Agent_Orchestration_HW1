# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a local AI chat application that connects a Streamlit UI to a FastAPI backend, which communicates with a local Ollama server running LLM models. The project is an educational assignment for the "LLMs and MultiAgent Orchestration" course.

## Development Commands

### Prerequisites Check
```bash
# Run preflight checks (Python version, dependencies, Ollama server, env vars)
make preflight
python scripts/preflight.py
```

### Installation
```bash
# Install dependencies from requirements.txt
make install
pip install -r requirements.txt
```

### Running Services
```bash
# Ensure Ollama server is running (starts if not running)
make ollama

# Start FastAPI backend (default: http://127.0.0.1:8000)
make api
# or with custom host/port:
make api HOST=0.0.0.0 PORT=8000
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Start Streamlit UI (default: http://127.0.0.1:8501)
make ui
# or with custom port:
make ui STREAMLIT_PORT=8501
streamlit run ui/streamlit_app.py --server.port 8501

# Run everything (preflight -> install -> ollama -> api in bg -> ui in fg)
make all
```

### Testing
```bash
# Run all tests
make test
pytest -q

# Run only unit tests (excludes integration tests)
make test-unit
pytest -m "not integration" -q

# Run only integration tests (requires running Ollama server)
make test-integration
pytest -q -k "integration"

# Run specific test file
pytest tests/test_auth_api.py -v

# Run specific test function
pytest tests/test_chat_validation_api.py::test_empty_messages -v
```

### Cleanup
```bash
# Remove Python cache files
make clean
```

## Architecture Overview

### Three-Layer Architecture

1. **API Layer** (`app/api/routers/chat.py`)
   - HTTP routing and request/response handling
   - Pydantic schemas for validation (`ChatMessage`, `ChatRequest`, `ChatResponse`)
   - Bearer token authentication via `app/api/deps.py`
   - Maps business exceptions to HTTP status codes

2. **Business Logic Layer** (`app/services/chat_service.py`)
   - Model selection and validation
   - Message processing
   - Response formatting with notices for edge cases
   - Session ID generation
   - Returns structured responses with `session_id`, `answer`, `model`, and optional `notice`

3. **Infrastructure Layer** (`app/services/ollama_client.py`)
   - HTTP communication with Ollama server
   - Functions: `ping()`, `has_model(model_name)`, `chat(messages, model, ...)`
   - Error handling for network/timeout/HTTP issues
   - All exceptions raised as `RuntimeError` for consistency with tests

### Request Flow

```
User/UI → FastAPI Router → Bearer Auth → ChatService → OllamaClient → Ollama Server
                                                                          ↓
User/UI ← JSON Response  ← HTTP Layer   ← Business Logic ← HTTP Client ←
```

### Configuration Management

All configuration is loaded from environment variables via `app/core/config.py`:
- `APP_API_KEY` - Bearer token for API authentication
- `OLLAMA_HOST` - Ollama server URL (default: http://127.0.0.1:11434)
- `OLLAMA_MODEL` - Default model name (e.g., "phi", "mistral")
- `API_URL` - API endpoint URL for UI (e.g., http://127.0.0.1:8000/api/chat)

**Critical**: All env vars are required. The app fails fast at startup if any are missing. Never commit secrets to git.

### Test Architecture

- **conftest.py**: Shared fixtures including `client` (TestClient), `auth_header`, `settings`, `sample_msg`, and `DummyResp` for mocking HTTP responses
- **pytest.ini**: Defines the `integration` marker for separating unit vs integration tests
- **Test Categories**:
  - Unit tests: No external dependencies, use mocking (default, run with `-m "not integration"`)
  - Integration tests: Require running Ollama server (marked with `@pytest.mark.integration`)

### Important Conventions

1. **Error Handling**:
   - `ollama_client.py` raises `RuntimeError` for all failures (network, timeout, HTTP, response shape)
   - `chat_service.py` catches Ollama errors and re-raises for API layer to convert to HTTPException
   - API layer maps exceptions to appropriate HTTP status codes (401, 404, 500, 503)

2. **Model Validation**:
   - ChatService checks if model is installed before calling Ollama
   - If model missing, returns response with `notice` field explaining how to install (Hebrew message)
   - Empty responses also include helpful `notice` field

3. **Response Format**:
   All `/api/chat` responses include:
   ```json
   {
     "session_id": "sess-xxxxxxxx",
     "answer": "model response text",
     "model": "phi",
     "notice": null | "informational message in Hebrew"
   }
   ```

4. **Authentication**:
   - All `/api/chat` requests require `Authorization: Bearer <APP_API_KEY>` header
   - Validation in `app/api/deps.py` via `require_api_key` dependency
   - Returns 401 if missing or invalid

5. **Hebrew Text**:
   - Documentation files contain Hebrew (RTL) text
   - User-facing notices in responses are in Hebrew
   - Code comments and docstrings are in English

## File Structure

```
app/
├── main.py                      # FastAPI app initialization, CORS, router registration
├── core/config.py               # Environment variable loading and validation
├── api/
│   ├── deps.py                  # Authentication dependency (require_api_key)
│   └── routers/chat.py          # Chat endpoint routing and HTTP layer
└── services/
    ├── chat_service.py          # Business logic (ChatService class)
    └── ollama_client.py         # Ollama HTTP client (ping, has_model, chat)

ui/
└── streamlit_app.py             # Streamlit chat interface

tests/
├── conftest.py                  # Shared fixtures and test formatting hooks
├── pytest.ini                   # Pytest configuration (markers, etc.)
├── test_auth_api.py             # Bearer token authentication tests
├── test_health_api.py           # Health endpoint tests
├── test_chat_validation_api.py  # Request validation tests
├── test_chat_happy_errors_api.py # Error handling and edge cases
├── test_config_settings.py      # Configuration loading tests
├── test_ollama_client_unit.py   # Unit tests for OllamaClient (mocked)
└── test_ollama_models_integration.py # Integration tests (requires Ollama)

scripts/
├── preflight.py                 # Environment validation script
└── check_langchain.py           # LangChain dependency checker

documentation/                    # Detailed documentation in Hebrew
├── PRD.md                       # Product requirements
├── Architecture.md              # Architecture details
├── Installation_and_Testing.md  # Setup and testing guide
├── Prompting_and_Developing.md  # Development process documentation
└── Screenshots_and_Demonstrations.md # UI screenshots
```

## Development Workflow

1. **Making Changes to Business Logic**:
   - Modify `chat_service.py` for business rule changes
   - Update unit tests in `test_chat_validation_api.py` or `test_chat_happy_errors_api.py`
   - Run `make test-unit` to verify without needing Ollama

2. **Modifying Ollama Communication**:
   - Update `ollama_client.py` for protocol changes
   - Mock responses in `test_ollama_client_unit.py` using `DummyResp` fixture
   - Test real integration with `make test-integration` (requires Ollama running)

3. **Adding API Endpoints**:
   - Add routes in `app/api/routers/chat.py` or create new router file
   - Register router in `app/main.py` using `app.include_router()`
   - Add corresponding test file in `tests/`

4. **Environment Variable Changes**:
   - Update `app/core/config.py` Settings class
   - Update `.env.example` with new variable
   - Update this CLAUDE.md under "Configuration Management"

## Common Issues

- **Ollama Connection Failures**: Ensure Ollama server is running (`make ollama`) and accessible at `OLLAMA_HOST`
- **Model Not Found**: Install model with `ollama pull <model_name>` (e.g., `ollama pull phi`)
- **Authentication Errors**: Verify `APP_API_KEY` is set in `.env` and matches the Bearer token in requests
- **Test Failures**: Unit tests should never require external services; if they do, mark with `@pytest.mark.integration`

## Documentation

Comprehensive documentation is in the `documentation/` directory (mostly in Hebrew). Key files:
- **Architecture.md**: Detailed system architecture, data flow, security, and future extensions
- **Installation_and_Testing.md**: Complete setup instructions and testing procedures
- **PRD.md**: Product requirements and system goals
