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
# UI layout is in ui/streamlit_app.py; helper logic (health checks, payload builder, history renderer) lives in ui/components.py

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

1. **UI Layer** (`ui/streamlit_app.py` + `ui/components.py`)
   - Streamlit layout/events live in `streamlit_app.py`
   - Non-visual helpers (health checks, payload builder, history renderer) live in `components.py`
   - Keeps Streamlit under the single-responsibility rubric while sharing code with tests

2. **API Layer** (`app/api/routers/chat.py`)
   - HTTP routing and request/response handling
   - Pydantic schemas for validation (`ChatMessage`, `ChatRequest`, `ChatResponse`)
   - Bearer token authentication via `app/api/deps.py`
   - Maps business exceptions to HTTP status codes

3. **Business Logic Layer** (`app/services/chat_service.py`)
   - Model selection and validation
   - Message processing
   - Response formatting with notices for edge cases
   - Session ID generation
   - Returns structured responses with `session_id`, `answer`, `model`, and optional `notice`

4. **Infrastructure Layer** (`app/services/ollama_client.py`)
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
LLM_Agent_Orchestration_HW1/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── deps.py
│   │   └── routers/chat.py
│   ├── core/config.py
│   └── services/
│       ├── chat_service.py
│       └── ollama_client.py
│
├── ui/
│   ├── __init__.py
│   ├── components.py
│   └── streamlit_app.py
│
├── tests/
│   ├── conftest.py
│   ├── pytest.ini
│   ├── test_auth_api.py
│   ├── test_chat_validation_api.py
│   ├── test_chat_happy_errors_api.py
│   ├── test_health_api.py
│   ├── test_config_settings.py
│   ├── test_ollama_client_unit.py
│   ├── test_streamlit_ui.py
│   └── test_ollama_models_integration.py
│
├── scripts/
│   ├── preflight.py
│   ├── check_langchain.py
│   └── validate_notebooks.py
│
├── documentation/
│   ├── PRD.md
│   ├── Architecture.md
│   ├── Installation_and_Testing.md
│   ├── Prompting_and_Developing.md
│   ├── Screenshots_and_Demonstrations.md
│   ├── Parameter_Sensitivity_Analysis.md
│   ├── Extensibility_Guide.md
│   └── screenshot_images/
│
├── notebooks/
│   ├── Results_Analysis.ipynb
│   └── data/
│       └── temperature_experiment.csv
│
├── requirements.txt
├── requirements-optional.txt
├── .env / .env.example
├── Makefile
└── README.md
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

## Recent Enhancements (November 2025)

The following documentation and analysis components were added to meet academic requirements and demonstrate professional software engineering practices:

### Research & Analysis Components (Mission 1)
- **Parameter_Sensitivity_Analysis.md**: Comprehensive analysis of temperature, model selection, and timeout parameters with experimental results and recommendations
- **notebooks/Results_Analysis.ipynb**: Jupyter notebook with visualizations (matplotlib/seaborn), statistical analysis, and LaTeX formulas demonstrating data-driven decision making

### PRD Enhancements (Mission 2)
- **KPIs & Success Metrics (Section 2.1)**: Technical, UX, and development KPIs with actual status tracking (all ✅ achieved)
- **Stakeholders Analysis (Section 1.1)**: Identified 5 key stakeholder groups with their interests
- **User Stories (Section 1.2)**: 6 complete user stories with acceptance criteria, priorities, and implementation status
- **Use Cases (Section 1.3)**: 5 detailed use case workflows covering happy path, error recovery, and setup scenarios

### Architecture Decision Records (Mission 3)
Added to **Architecture.md**:
- **ADR-001**: Three-Layer Architecture Pattern
- **ADR-002**: Bearer Token Authentication
- **ADR-003**: Local-Only LLM with Ollama
- **ADR-004**: Pydantic for Request/Response Validation
- **ADR-005**: pytest with Mocking for Unit Tests
- **ADR-006**: Environment Variables for Configuration
- **ADR-007**: Streamlit for UI (Not Custom React/Vue)

### C4 Model Diagrams (Mission 4)
Added to **Architecture.md**:
- **Level 1: System Context Diagram** - Big picture view with user, system, and Ollama
- **Level 2: Container Diagram** - Shows Streamlit UI, FastAPI Backend, Configuration, and Ollama
- **Level 3: Component Diagram** - Internal structure of FastAPI backend (6 components with file paths)
- **Level 4: Deployment Diagram** - Physical deployment on local machine with all processes
- **Bonus: Data Flow Through Layers** - 8-step request/response flow with error handling

### Extensibility Guide (Mission 5)
Created **Extensibility_Guide.md** with:
- **5 Extension Points**: New model providers, custom middleware, response processors, Pydantic validators, auth extensions
- **5 Future Extensions**: RAG, streaming responses, conversation history, multi-model routing, observability
- **Complete Code Examples**: Ready-to-use implementations for each extension point
- **Maintenance Guidelines**: Best practices for extending the system

### Cross-References Updated
- **README.md**: Updated "Adding New Features" section to reference Extensibility Guide, updated Documentation table with 3 new files
- **PRD.md**: Updated Future Extensions with detailed feature list and reference to Extensibility Guide, updated Summary with complete documentation suite (10 files)

**Total Documentation**: 10 comprehensive files covering requirements, architecture, testing, research, analysis, and extensibility.

---

## Documentation

Comprehensive documentation is in the `documentation/` directory. Key files:

**Core Documentation:**
- **Architecture.md**: System architecture, C4 diagrams (4 levels), ADRs, data flow, security, cost analysis
- **Installation_and_Testing.md**: Complete setup instructions and testing procedures
- **PRD.md**: Product requirements, KPIs, stakeholders, user stories, acceptance criteria
- **Prompting_and_Developing.md**: AI-assisted development process documentation
- **Screenshots_and_Demonstrations.md**: Visual walkthrough with UI screenshots

**Research & Analysis:**
- **Parameter_Sensitivity_Analysis.md**: Temperature, model, timeout experiments with recommendations
- **Results_Analysis.ipynb** (in `notebooks/`): Jupyter notebook with visualizations and statistical analysis

**Extensibility:**
- **Extensibility_Guide.md**: Extension points, hooks, and complete implementation guides for adding features
