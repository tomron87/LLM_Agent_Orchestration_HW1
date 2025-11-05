# 🏗️ Architecture — HW1_ai_chat_bot

This document presents the system architecture — **Backend** and **Frontend** — highlighting roles, data flow, security, environment variables, and testing.
The document focuses on architecture and does not include detailed installation instructions.

---

## ⚙️ Complete Directory Structure

```
HW1_ai_chat_bot/
├── app/
│   ├── api/routers/chat.py
│   ├── core/config.py
│   ├── services/ollama_client.py
│   ├── services/chat_service.py
│   └── main.py
├── ui/
│   └── streamlit_app.py
├── tests/
│   ├── test_auth_api.py
│   ├── test_chat_happy_errors_api.py
│   ├── test_chat_validation_api.py
│   ├── test_config_settings.py
│   ├── test_health_api.py
│   ├── test_ollama_client_unit.py
│   ├── test_ollama_models_integration.py
│   ├── conftest.py
│   └── pytest.ini
├── scripts/
│   ├── preflight.py
│   └── check_langchain.py
├── documentation/
│   ├── PRD.md
│   ├── Architecture.md
│   ├── Installation_and_Testing.md
│   ├── Prompting_and_Developing.md
│   └── Screenshots_and_Demonstrations.md
├── README.md
├── Makefile
├── .env.example
├── .env
├── requirements.txt
└──  .gitignore
```

---

## 🧩 System Components and Roles

### 🖥️ Backend (FastAPI)

| Component | Role |
|------|--------|
| `app/main.py` | Entry point; creates FastAPI instance and registers routes (`/api/health`, `/api/chat`). |
| `app/api/routers/chat.py` | HTTP layer: Pydantic schemas (`ChatMessage`, `ChatRequest`, `ChatResponse`), routing, error handling to HTTP. |
| `app/api/deps.py` | Bearer Token-based access authentication (`require_api_key`). |
| `app/services/chat_service.py` | Business logic: model existence checking, calling `ollama_client`, collecting/unifying results into a unified format (answer/notice). |
| `app/services/ollama_client.py` | HTTP communication layer to Ollama (`ping`, `has_model`, `chat`) with error/timeout handling. |
| `app/core/config.py` | Configuration management and loading `.env` to environment variables. |

#### Main Flow Logic:
1. **User sends request** → `/api/chat`
2. **API** authenticates entry (`require_api_key`), checks request structure (`ChatRequest`).
3. **ChatService**:
   - Checks if model exists (`has_model`)
   - If not — returns notice (model not installed)
   - If yes — calls `ollama_client.chat()` to get response
4. **OllamaClient** communicates with local server (`OLLAMA_HOST/api/chat`)
5. **API** returns structured response (JSON with `answer`, `model`, `session_id`, and `notice` if needed).

---

### 💬 Frontend (Streamlit)

| Component | Role |
|------|--------|
| `ui/streamlit_app.py` | Chat window; HTTP calls to `API_URL`; displays model response/`notice`. |
| `.env → API_URL` | API call destination (`http://127.0.0.1:8000/api/chat` by default). |

#### UI Workflow:
1. User types message and clicks "Send"
2. Streamlit sends POST request to API_URL
3. Response is displayed on right/left side according to role
4. If model is not installed, appropriate `notice` message is displayed to the user

---
## 🔁 Data Flow Diagram

```text
[User / Streamlit UI]
       │  (HTTP POST /api/chat, Bearer)
       ▼
[FastAPI Router (chat.py)]  — Validation + error mapping
       │
       ▼
[ChatService]  — Model checking, model selection, call to client
       │
       ▼
[OllamaClient] — HTTP to {OLLAMA_HOST}/api/chat
       │
       ▼
[Ollama Server]  — Text generation
       │
       ▼
[API JSON]  — {session_id, answer, model, notice?}
```

---

## 🌱 Environment Variables

| Key | Usage | Default/Example |
|------|-------|-------------------|
| `APP_API_KEY` | Bearer token for `/api/chat` | No valid default (must set a real value) |
| `OLLAMA_HOST` | Ollama server base URL | `http://127.0.0.1:11434` |
| `OLLAMA_MODEL` | Local model name to use | `phi` (or `mistral`/other) |
| `API_URL` | UI's API call destination | `http://127.0.0.1:8000/api/chat` |

> Keys are loaded in `app/core/config.py`; do not store secrets in code/git.

> The system will not start if any variable is missing.

---

## 🧪 Testing (QA) — Architectural Summary

| File / Component | Main Role |
|--------------|--------------|
| `tests/` | Includes unit and integration tests for all system layers. |
| `tests/test_*.py` | API tests, validation, settings and configuration. |
| `tests/test_ollama_client_unit.py` | Unit tests for communication layer (OllamaClient) — without real server. |
| `tests/test_ollama_models_integration.py` | Integration tests against local Ollama server (`ping`, model existence). |
| `tests/conftest.py` | Shared fixtures, unified output format, expected/actual management. |
| `pytest.ini` | Defines single `integration` marker and global run parameters. |
| `scripts/preflight.py` | Validates environment health (Python, packages, Ollama, environment variables). |

#### Development and Testing Tools
- **Makefile** – Centralizes the entire startup and testing process (including `preflight`, `install`, `ollama`, `api`, `ui`, and `test`) and ensures consistent execution in any environment.
- **Pytest markers** – Enable filtering between test types:
  - `pytest -m "not integration"` — Run unit tests only.
  - `pytest -m integration` — Run integration tests against real server.
- **Preflight Script** – Part of QA process; ensures healthy environment before startup or testing.

> The testing layer and Makefile are integral parts of the architecture, ensuring a stable, consistent, and reproducible QA process in any execution environment.
---

## 🔐 Security

- **Authentication**: Every `/api/chat` call requires `Authorization: Bearer <APP_API_KEY>`; verification performed in `require_api_key`.
- **Secrets in code**: No hardcoded values; key values loaded from `.env` through `app/core/config.py`.
- **Errors/logs**: Mapping exceptions to HTTP errors (401/404/5xx); logs in `ollama_client` and `chat.py` without leaking secrets.
- **Validation**: Pydantic schemas enforce structure/types; protect against bad input.
- **Possible hardening (future)**: rate limiting, precise CORS, request size limiting, sanitization, and audit logs.

---

## 🚀 Future Extensions

- **Streaming** responses (SSE/WebSocket) and partial tokens.
- **Conversation management**: Memory/storage of session history (simple DB/Redis).
- **Multi-Model Routing**: Dynamic model selection based on state/cost/latency.
- **Robustness**: retry/backoff mechanism, circuit breaker, per-layer timeouts.
- **Observability**: Structured logging, metrics (Prometheus), tracing (OTEL).
- **Security**: rate limiting, permission cohorts, CORS, message size limiting.
- **Caching**: Identical/similar responses (embeddings+cache).
- **Optional RAG**: Document indexing, semantic search (FAISS/Chroma), connection to LangChain/LangGraph.
- **UI**: Conversation history, file uploads, model status indication.

---


## ⚡ Summary
- **Clear separation** between HTTP, business logic, and external communication.
- **External dependencies isolated** in unit tests using mocking.
- **Clean configuration** through `.env` without secrets in code.
- **Ready foundation for extensions** (Streaming, RAG, observability, and more).
