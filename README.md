# 🤖 Local AI Chat Agent

> **Production-grade chat interface for local LLMs using Ollama + FastAPI + Streamlit**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green.svg)](https://ollama.ai/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-Educational-yellow.svg)](#)

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Course Information](#-course-information)
- [Key Features](#-key-features)
- [Architecture](#️-architecture)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Installation Guide](#-installation-guide)
- [Running the Application](#️-running-the-application)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Configuration](#️-configuration)
- [Performance & Monitoring](#-performance--monitoring)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)
- [Project Structure](#-project-structure)
- [Documentation](#-documentation)
- [Known Limitations](#-known-limitations)
- [Future Extensions](#-future-extensions)

---

## 🎯 Overview

This project is a **production-ready local AI chat system** that enables interactive conversations with Large Language Models (LLMs) running entirely on your machine using **Ollama**. The system features a modern three-layer architecture with complete separation of concerns, comprehensive testing, and enterprise-grade error handling.

**Why This Project?**
- **Privacy First** - All data stays on your machine, no cloud API calls
- **Cost Effective** - Zero API costs, unlimited usage
- **Educational** - Learn modern Python backend architecture, testing patterns, and LLM integration
- **Extensible** - Ready foundation for RAG, agents, and multi-model orchestration

**Key Characteristics:**
- ✅ **100% Local** - No cloud dependencies, complete privacy
- ✅ **Production-Ready** - Comprehensive testing (35 tests), error handling, and validation
- ✅ **Modular Architecture** - Clean separation: API → Business Logic → Infrastructure
- ✅ **Developer-Friendly** - Complete documentation, Makefile automation, preflight checks
- ✅ **Type-Safe** - Pydantic schemas throughout, catching errors at validation time
- ✅ **Well-Tested** - Unit tests (mocked) + Integration tests (real Ollama)
- ✅ **Extensible** - Ready for RAG, multi-model routing, and agent orchestration

---

## 🏫 Course Information
- **Assignment:** Assignment 1 – AI Chat Bot
- **Course:** LLMs and MultiAgent Orchestration
- **Instructor:** Dr. Yoram Gal
- **Students:** Igor Nazarenko, Tom Ron, and Roie Gilad
- **Submission Date:** November 2025
- **Repository:** [https://github.com/tomron87/LLM_Agent_Orchestration_HW1](https://github.com/tomron87/LLM_Agent_Orchestration_HW1)

---

## 🌟 Key Features

### Core Functionality
- **Real-time Chat** - Interactive conversation with local LLM models via WebSocket-ready architecture
- **Multi-Model Support** - Switch between Phi, Llama, Mistral, and other Ollama models dynamically
- **Bearer Token Authentication** - Secure API access control with environment-based secrets
- **Health Monitoring** - Real-time system and model availability checks via `/api/health`
- **Graceful Error Handling** - User-friendly error messages with detailed logging for debugging
- **Session Management** - Unique session IDs for conversation tracking
- **Decoding Controls** - Optional `temperature` parameter (0.0–1.0, default 0.2) respected end-to-end for deterministic vs. creative replies

### Developer Features
- **Comprehensive Testing** - 35 tests covering all layers (33 unit + 2 integration)
- **Automated Setup** - Single-command deployment via Makefile
- **Preflight Checks** - Environment validation catches issues before startup
- **Type Safety** - Pydantic schemas for request/response validation
- **Detailed Logging** - Structured logging with configurable levels
- **Interactive API Docs** - Auto-generated Swagger UI at `/docs`
- **Hot Reload** - Development server with automatic code reloading

---

## 🏗️ Architecture

The system follows a **three-layer architecture** with clear separation of concerns:

```
┌─────────────────┐
│  Streamlit UI   │  ← User Interface Layer
└────────┬────────┘    • Stateful session management
         │              • Real-time updates
         │ HTTP POST /api/chat
         │ Bearer Token
┌────────▼────────┐
│  FastAPI API    │  ← HTTP Layer (Presentation)
│  - Routing      │    • Request validation (Pydantic)
│  - Auth         │    • Bearer token authentication
│  - Validation   │    • Error mapping to HTTP codes
│  - CORS         │    • Swagger/OpenAPI documentation
└────────┬────────┘
         │
┌────────▼────────┐
│  Chat Service   │  ← Business Logic Layer (Domain)
│  - Model check  │    • Model existence validation
│  - Session mgmt │    • Response formatting
│  - Logic        │    • Notice generation
│  - Orchestration│    • Future: RAG, chains, agents
└────────┬────────┘
         │
┌────────▼────────┐
│ Ollama Client   │  ← Infrastructure Layer
│  - HTTP client  │    • Network communication
│  - Error        │    • Timeout handling (60s default)
│    handling     │    • Response parsing
│  - Retry logic  │    • Connection pooling
└────────┬────────┘
         │
┌────────▼────────┐
│  Ollama Server  │  ← Local LLM (External Service)
│  (phi/mistral)  │    • Model inference
│                 │    • Context management
└─────────────────┘
```

> **UI Composition:** Visual layout/events live in `ui/streamlit_app.py`, while non-visual helpers (health checks, payload builders, history rendering) live in `ui/components.py`. Keeping them separate satisfies the “single responsibility” rubric without changing behavior.

### Data Flow

1. **User** enters message in Streamlit UI
2. **UI** sends POST request to `/api/chat` with Bearer token
3. **FastAPI Router** validates authentication and request schema (Pydantic)
4. **Chat Service** checks if model exists via Ollama Client
   - If missing → returns friendly `notice` (not an error)
   - If exists → calls Ollama Client for inference
5. **Ollama Client** communicates with local Ollama server (HTTP)
6. **Response** flows back up the stack with structured JSON
7. **UI** displays response with metadata (model name, session ID, timestamp)

### Response Format
All `/api/chat` responses follow this schema:
```json
{
  "session_id": "sess-a1b2c3d4",       // Unique session identifier
  "answer": "Model's response text",   // LLM generated response
  "model": "phi",                      // Model used for this response
  "notice": null                       // Optional user-facing notice (e.g., model not found)
}
```

> **Decoding Parameters:** Requests may include `temperature` (0.0–1.0). When omitted, the backend defaults to `0.2`, matching the production configuration described in the Parameter Sensitivity Analysis.

### Error Handling Strategy
- **401** - Missing or invalid Bearer token
- **422** - Invalid request schema (Pydantic validation)
- **500** - Internal server error (logged with full traceback)
- **503** - Ollama service unavailable (with retry suggestion)
- **200 + notice** - Graceful degradation (e.g., model not installed)

---

## ✅ Prerequisites

### Required Software
- **Python 3.10+** (tested on 3.10.x, 3.11.x)
- **Ollama** - Download from [ollama.com](https://ollama.com)
- **Git** - For cloning repository

### System Requirements
- **Operating System:** macOS / Linux / Windows 10+ (WSL2 recommended for Windows)
- **RAM:** 8GB+ (16GB recommended for larger models like Llama2)
- **Disk Space:** 5GB+ free (for model storage)
- **CPU:** Multi-core recommended (inference can be CPU-intensive)
- **Network:** Ports 11434 (Ollama) and 8000 (FastAPI) available

### Supported Models
Any Ollama-compatible model:
- **Phi** (2.7GB) - Recommended for development, fast inference
- **Mistral** (4.1GB) - Good balance of speed and capability
- **Llama 2** (3.8GB) - Meta's foundation model
- **Code Llama** (7GB) - Optimized for code generation
- Full list: [https://ollama.com/library](https://ollama.com/library)

### Installation Check
```bash
python --version   # Should show 3.10 or higher
ollama --version   # Should show Ollama version
git --version      # Any recent version
```

---

## 🚀 Quick Start

For experienced users, here's the fastest path to running the application:

```bash
# 1. Clone repository
git clone https://github.com/tomron87/LLM_Agent_Orchestration_HW1.git
cd LLM_Agent_Orchestration_HW1

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
# Optional extras (LangChain, notebooks, torch, etc.)
# pip install -r requirements-optional.txt

# 4. Configure environment (IMPORTANT: Set your own API key!)
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"  # Copy the output (64 hex chars)
nano .env  # Paste value into APP_API_KEY (needs ≥32 chars w/ lots of unique characters)

# 5. Install Ollama model (if not already done)
ollama serve  # In separate terminal
ollama pull phi  # Small, fast model (recommended for testing)

# 6. Verify setup
python scripts/preflight.py

# 7. Run everything (one command)
make all
```

> Preflight will fail with actionable errors if `APP_API_KEY` is shorter than 32 characters or reuses the same few characters—generate a new value with the snippet above whenever that happens.

**Expected Result:**
- API server starts on http://127.0.0.1:8000
- UI opens automatically in browser at http://127.0.0.1:8501
- Health check at http://127.0.0.1:8000/api/health returns `{"status":"ok"}`

**First Steps After Launch:**
1. UI automatically reads `APP_API_KEY` (and `API_URL`) from `.env`; if they're missing you'll see a red error banner—update `.env` and restart.
2. Select model (e.g., "phi")
3. Use the temperature slider to choose determinism vs. creativity (0.0 = מדויק, 1.0 = יצירתי)
4. Click "Check API Connection" to verify setup
5. Start chatting!

---

## 📦 Installation Guide

### Step 1: Clone Repository
```bash
git clone https://github.com/tomron87/LLM_Agent_Orchestration_HW1.git
cd LLM_Agent_Orchestration_HW1
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv

# Activate on macOS/Linux:
source .venv/bin/activate

# Activate on Windows PowerShell:
.venv\Scripts\Activate.ps1

# Activate on Windows CMD:
.venv\Scripts\activate.bat
```

**Verification:** You should see `(.venv)` prefix in your terminal prompt.

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
# Optional extras (LangChain, notebooks, torch, etc.)
# pip install -r requirements-optional.txt
```

**Core packages (requirements.txt):**
- `fastapi`, `uvicorn` – API server
- `streamlit` – UI framework
- `pydantic`, `python-dotenv`, `requests` – validation & config
- `pytest`, `pytest-cov` – testing

**Optional extras (requirements-optional.txt):**
- LangChain/LangGraph stacks, transformers, vector DBs
- Torch + pandas/numpy/scikit-learn + JupyterLab
- Gradio experiments
- Formatting/tooling (`black`, `flake8`, `isort`, `pylint`)

### Step 4: Install and Configure Ollama

#### Install Ollama

**macOS:**
```bash
# Option 1: Download from website
# Visit https://ollama.com/download

# Option 2: Homebrew
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download installer from [ollama.com](https://ollama.com)

#### Pull Models

```bash
# Start Ollama server (keep running in separate terminal)
ollama serve

# Pull recommended model (in another terminal)
ollama pull phi        # 2.7GB - Recommended for development

# Optional: Pull additional models
ollama pull mistral    # 4.1GB - More capable
ollama pull llama2     # 3.8GB - Meta's foundation model
```

**Verify installation:**
```bash
ollama list
# Should show: phi:latest
```

### Step 5: Configure Environment Variables

**Create `.env` file:**
```bash
cp .env.example .env
```

**Edit `.env`** with your preferred editor:

```dotenv
# API Authentication (REQUIRED - CHANGE THIS!)
# Generate secure key (≥32 chars, high entropy):
#   python -c "import secrets; print(secrets.token_hex(32))"
APP_API_KEY=replace-with-64-char-hex-key

# Ollama Configuration (defaults usually work)
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=phi

# API URL for UI (change if running on different port)
API_URL=http://127.0.0.1:8000/api/chat
```

**Security Best Practices:**
- ⚠️ **Never commit `.env` to git** (already in `.gitignore`)
- ✅ Use a strong random API key (≥32 characters with at least ~10 unique symbols)
- ✅ Generate keys with: `python -c "import secrets; print(secrets.token_hex(32))"`
- ✅ Rotate keys periodically (preflight enforces the policy so weak keys fail fast)
- ✅ Different keys for dev/staging/production
- ⚠️ Don't use `change-me`, dictionary words, or short passwords

### Step 6: Run Preflight Check

**Validate environment:**
```bash
python scripts/preflight.py
```

**Expected output:**
```
[OK] Python version 3.10+
[OK] Required packages installed
[OK] Ollama server reachable at http://127.0.0.1:11434
[OK] Model 'phi' installed
[OK] Environment variables configured
[OK] APP_API_KEY is set (not default)
[OK] APP_API_KEY length >= 32 characters
[OK] APP_API_KEY has sufficient entropy (>=10 unique characters)
[OK] All ports available (8000, 8501, 11434)
```

**If any check fails:**
- Read the error message carefully
- Follow the suggested fix
- Re-run `python scripts/preflight.py`

---

## ▶️ Running the Application

### Method 1: Using Makefile (Recommended)

**See all available commands:**
```bash
make help
```

**Full startup (recommended for first run):**
```bash
make all
# This runs: preflight → install → ollama check → API (background) → UI (foreground)
```

**Run services individually:**
```bash
# Terminal 1: Start API only
make api

# Terminal 2: Start UI only
make ui

# Ensure Ollama is running
make ollama
```

**Common Makefile targets:**
```bash
make preflight           # Validate environment
make install            # Install/update dependencies
make test               # Run all tests
make test-unit          # Run unit tests only
make test-integration   # Run integration tests (requires Ollama)
make clean              # Remove Python cache files
```

### Method 2: Manual Execution

**Terminal 1: Start Ollama** (if not already running as service)
```bash
ollama serve
# Leave this running. You should see:
# time=... level=INFO msg="Ollama server listening on http://127.0.0.1:11434"
```

**Terminal 2: Start FastAPI Backend**
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process using StatReload
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Terminal 3: Start Streamlit UI**
```bash
streamlit run ui/streamlit_app.py --server.port 8501
```
> This launches the Streamlit layout (`ui/streamlit_app.py`) along with the shared helper module (`ui/components.py`) that handles health checks, payload building, and history rendering.

**Streamlit will:**
- Automatically open browser to http://localhost:8501
- Display local/network URLs in terminal

**If browser doesn't auto-open:**
- Manual URL: http://localhost:8501 or http://127.0.0.1:8501

### Verify Everything Works

#### 1. Check API Health Endpoint
```bash
curl http://127.0.0.1:8000/api/health
```

**Expected response:**
```json
{
  "status": "ok",
  "ollama": true,
  "default_model": "phi"
}
```

#### 2. Test Chat Endpoint
Replace `YOUR_API_KEY` with value from your `.env` file:

```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is 2+2?"}
    ]
  }'
```

**Expected response:**
```json
{
  "session_id": "sess-a1b2c3d4",
  "answer": "2 + 2 equals 4.",
  "model": "phi",
  "notice": null
}
```

#### 3. Access Interactive API Docs
Visit **http://127.0.0.1:8000/docs** in your browser for:
- Swagger UI with all endpoints
- Try-it-out functionality
- Schema documentation
- Example requests/responses

#### 4. Use the Streamlit UI

1. Open browser to http://localhost:8501
2. **Sidebar Overview:**
   - `APP_API_KEY` + `API_URL` are loaded directly from `.env`; if either is missing, the UI blocks usage with an error.
   - Select model (should show "phi" or whichever you installed)
   - Click "Check API Connection" → should show "✅ Connected"
3. **Start Chatting:**
   - Type message in input box
   - Click "Send" or press Enter
   - View response with timestamp and model info
4. **Additional Features:**
   - View conversation history
   - Copy responses to clipboard
   - Clear conversation
   - Switch models on the fly

---

## 📖 API Documentation

### Available Endpoints

#### `GET /`
**Root endpoint** - Service information

**Response:**
```json
{
  "ok": true,
  "service": "AI Chat Local Gateway",
  "docs": "/docs",
  "health": "/api/health"
}
```

#### `GET /api/health`
**Health check** - System and model availability

**Response:**
```json
{
  "status": "ok",
  "ollama": true,
  "default_model": "phi"
}
```

**Status Codes:**
- `200` - System healthy
- `503` - Ollama unavailable (still returns 200 but with `"ollama": false`)

#### `POST /api/chat`
**Chat completion** - Send message, receive LLM response

**Headers:**
```
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY
```

**Request Body:**
```json
{
  "messages": [
    {"role": "user", "content": "Your question here"}
  ],
  "model": "phi",          // Optional: override default model
  "temperature": 0.7,      // Optional: 0.0-1.0; honored end-to-end (defaults to 0.2)
  "stream": false          // Optional: streaming not yet implemented
}
```

**Response:**
```json
{
  "session_id": "sess-abc123",
  "answer": "LLM generated response",
  "model": "phi",
  "notice": null          // Or user-friendly message if issue
}
```

**Status Codes:**
- `200` - Success (even if model not found, check `notice` field)
- `401` - Missing or invalid Bearer token
- `422` - Invalid request schema
- `500` - Internal server error
- `503` - Ollama server unreachable (start `ollama serve` and retry)
- `503` - Ollama service unavailable

**Example with curl:**
```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain quantum computing in simple terms"}
    ],
    "temperature": 0.5
  }'
```

### Interactive Documentation

Visit **http://127.0.0.1:8000/docs** for:
- Full OpenAPI/Swagger UI
- Try all endpoints in browser
- See request/response schemas
- Download OpenAPI spec

Alternative: **http://127.0.0.1:8000/redoc** for ReDoc interface

---

## 🧪 Testing

The project includes **35 comprehensive tests** (33 unit + 2 integration) covering all architectural layers.

### Quick Test Commands

```bash
# Run ALL tests
make test
# or
pytest -q

# Run ONLY unit tests (fast, no external dependencies)
make test-unit
# or
pytest -m "not integration" -q

# Run ONLY integration tests (requires Ollama running)
make test-integration
# or
pytest -m integration -q

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth_api.py -v

# Run specific test function
pytest tests/test_auth_api.py::test_missing_token_returns_401 -v

# Run tests with coverage report
make coverage
# (Runs: pytest --cov=app --cov=ui --cov-report=term-missing --cov-report=html)
# Open htmlcov/index.html in browser for visual report
```

### Test Categories

#### Unit Tests (No External Dependencies)
These tests use mocking and **don't require Ollama** to be running:

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_auth_api.py` | 5 | Bearer token authentication (401 errors, schemes, validation) |
| `test_chat_validation_api.py` | 5 | Request validation (Pydantic schemas, empty messages, type errors) |
| `test_chat_happy_errors_api.py` | 5 | Happy path, error handling, temperature passthrough, Ollama offline (503) |
| `test_health_api.py` | 2 | Health endpoint consistency |
| `test_config_settings.py` | 2 | Configuration loading, env var overrides |
| `test_ollama_client_unit.py` | 3 | HTTP client behavior with mocked responses |
| `test_streamlit_ui.py` | 11 | Streamlit UI smoke tests (load, sidebar actions, guard-rails, notices, timeouts) via `AppTest` |

**Total Unit Tests:** 33

#### Integration Tests (Require Running Ollama)
These tests communicate with **real Ollama server**:

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_ollama_models_integration.py` | 2 | Real ping tests, model availability checks |

**Total Integration Tests:** 2

**Note:** Integration tests are automatically **SKIPPED** (not FAILED) if Ollama is not running.

#### Notebook Data Validation (Research Artifacts)

Validate that the committed CSVs powering `notebooks/Results_Analysis.ipynb` still match the documented schema:

```bash
python scripts/validate_notebooks.py
```

What it checks:
- `notebooks/data/temperature_experiment.csv` exists
- Column order matches the published schema
- Exactly five rows (temperatures 0.0–1.0) with numeric values
- Sample size stays consistent across rows
- Temperatures remain sorted (no accidental reordering)

> Graders can run this command (no Ollama needed) to confirm the notebook artifacts are reproducible without opening Jupyter.

### Understanding Test Output

Tests use custom formatting from `conftest.py` for clear, readable output:

**Passing tests:**
```
tests/test_auth_api.py
  test_missing_token_returns_401 ... PASSED
    EXPECTED: 401 with 'Missing bearer token'
  test_invalid_token_returns_401 ... PASSED
    EXPECTED: 401 with 'Invalid API key'
  >>> FILE STATUS: ALL PASSED
```

**Failing tests:**
```
tests/test_auth_api.py
  test_invalid_token_returns_401 ... FAILED
    EXPECTED: 401 with 'Invalid API key'
    ACTUAL:   status=200 body={'detail': 'unexpected error'}
```

### Test Coverage Metrics

Run coverage analysis:
```bash
make coverage
# Under the hood: pytest --cov=app --cov=ui --cov-report=term-missing --cov-report=html
```

**Latest measurement (2025-11-12, macOS, Python 3.11.10):**
- Overall: **89%** (315 statements / 34 missed) — reported by `make coverage`
- `app/api/routers/chat.py`: 96%
- `app/services/chat_service.py`: 87%
- `app/services/ollama_client.py`: 80%
- `ui/streamlit_app.py`: 91% (Streamlit `AppTest` covers sidebar actions, errors, and timeouts)
- `ui/components.py`: Exercised indirectly via the same AppTests (health helpers, payload builder, history renderer)
- HTML report location: `htmlcov/index.html` (auto-generated, already `.gitignore`d)

Integration tests in `tests/test_ollama_models_integration.py` automatically skip whenever `ollama serve` is not running locally; the latest run skipped both because `ping()` returned `False`.

### Testing Best Practices

1. **Run unit tests frequently** during development (fast feedback)
2. **Run integration tests** before committing (ensures real Ollama compatibility)
3. **Check coverage** when adding new features
4. **Use `-v` flag** when debugging failing tests
5. **Use `pytest.mark.skip`** for tests requiring external services
6. **Mock external dependencies** in unit tests for speed and reliability

---

## ⚙️ Configuration

### Environment Variables

All configuration managed through `.env` file:

| Variable | Type | Description | Default | Required |
|----------|------|-------------|---------|----------|
| `APP_API_KEY` | string | Secret key for Bearer token auth (≥32 chars, high entropy) | *None* | ✅ Yes |
| `OLLAMA_HOST` | URL | Ollama server endpoint | `http://127.0.0.1:11434` | ✅ Yes |
| `OLLAMA_MODEL` | string | Default model name | `phi` | ✅ Yes |
| `API_URL` | URL | FastAPI endpoint for UI | `http://127.0.0.1:8000/api/chat` | ✅ Yes |

**Environment Validation:**
- App **fails fast on startup** if any required variable is missing
- Validation performed in `app/core/config.py` using Pydantic
- Clear error messages indicate which variables need to be set

### Advanced Configuration

#### Running on Different Ports

**API on custom port:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
# Then update .env:
API_URL=http://127.0.0.1:8001/api/chat
```

**UI on custom port:**
```bash
streamlit run ui/streamlit_app.py --server.port 8502  # loads helper module from ui/components.py
```

**Using Makefile:**
```bash
make api PORT=8001
make ui STREAMLIT_PORT=8502
```

**Expose to network:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
# Then access from other devices: http://<your-ip>:8000
```

#### Using Different Models

1. **Pull the model:**
   ```bash
   ollama pull llama2
   # or
   ollama pull codellama
   # or
   ollama pull mistral
   ```

2. **Update `.env`:**
   ```dotenv
   OLLAMA_MODEL=llama2
   ```

3. **Restart services** (Ctrl+C and rerun)

4. **Or switch dynamically** via UI sidebar without restarting

**Available models:** [https://ollama.com/library](https://ollama.com/library)

#### Remote Ollama Server

Deploy Ollama on different machine and connect remotely:

```dotenv
OLLAMA_HOST=http://192.168.1.100:11434
```

**Security note:** Ollama has no built-in authentication. Use firewall rules or VPN for remote access.

#### Production Deployment

For production use, consider:

```bash
# Use production-grade ASGI server
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info \
  --access-log \
  --proxy-headers \
  --forwarded-allow-ips='*'

# Behind reverse proxy (nginx/Traefik)
# Set up HTTPS, rate limiting, and caching
```

**Environment-specific configs:**
- `.env.development`
- `.env.staging`
- `.env.production`

Load with: `export $(cat .env.production | xargs)`

---

## 📊 Performance & Monitoring

### Performance Characteristics

**Typical Response Times (on M1 Mac, 16GB RAM):**
- Health check: < 50ms
- Chat (Phi model, short response): 200-500ms
- Chat (Phi model, long response): 1-3s
- Chat (Mistral model): 2-5s
- First request (cold start): +500ms (model loading)

**Resource Usage:**
- API server: ~100MB RAM (idle)
- Streamlit UI: ~200MB RAM
- Ollama (Phi model loaded): ~2.5GB RAM
- Ollama (Mistral model loaded): ~4GB RAM

### Monitoring and Logging

**Log Locations:**
- FastAPI logs: stdout (uvicorn output)
- Streamlit logs: `~/.streamlit/logs/`
- Ollama logs: system logs (check `ollama serve` output)

**Log Levels:**
```python
# In app/main.py, adjust:
import logging
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG, INFO, WARNING, ERROR
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Enable verbose Uvicorn logs:**
```bash
uvicorn app.main:app --log-level debug --access-log
```

**Monitor Ollama:**
```bash
# Check running models
curl http://127.0.0.1:11434/api/tags | jq

# Check Ollama server status
curl http://127.0.0.1:11434/api/version
```

### Health Checks

**Kubernetes/Docker readiness probe:**
```yaml
readinessProbe:
  httpGet:
    path: /api/health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

**Monitoring Script:**
```bash
#!/bin/bash
while true; do
  curl -s http://127.0.0.1:8000/api/health | jq
  sleep 5
done
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. "401 Unauthorized" Error

**Symptom:** API returns 401 when calling `/api/chat`

**Diagnosis:**
```bash
# Check if API key is set
grep APP_API_KEY .env

# Test with curl
curl -H "Authorization: Bearer your-key" http://127.0.0.1:8000/api/chat
```

**Solutions:**
```bash
# 1. Ensure API key is not the placeholder
nano .env  # Change APP_API_KEY to actual value

# 2. Generate strong API key (preflight enforces ≥32 chars)
python -c "import secrets; print(secrets.token_hex(32))"

# 3. Verify header format (must be "Bearer <token>")
# Correct:   Authorization: Bearer abc123
# Incorrect: Authorization: abc123
# Incorrect: Authorization: Token abc123

# 4. Check for whitespace in .env file
cat -A .env  # Look for hidden spaces/newlines
```

#### 2. Preflight Fails: `APP_API_KEY length >= 32 characters` / `entropy`

**Symptom:** `python scripts/preflight.py` exits with one (or both) of the new APP_API_KEY checks.

**Solutions:**
```bash
# 1. Generate a compliant key (64 hex characters = 32 bytes of entropy)
python -c "import secrets; print(secrets.token_hex(32))"

# 2. Update .env with the new value
nano .env  # Paste value into APP_API_KEY

# 3. Re-run the preflight check
python scripts/preflight.py
```

> Tip: The entropy check simply counts unique characters. Any freshly generated `token_hex(32)` value will pass immediately. Rotate the key whenever you share screenshots/logs.

#### 3. "Connection Refused" to Ollama

**Symptom:** Can't reach Ollama server, API returns 503

**Diagnosis:**
```bash
# Test Ollama connectivity
curl http://127.0.0.1:11434/api/tags

# Check if Ollama process is running
ps aux | grep ollama

# Check port availability
lsof -i :11434  # macOS/Linux
netstat -ano | findstr :11434  # Windows
```

**Solutions:**
```bash
# 1. Start Ollama server
ollama serve

# 2. If fails, check Ollama installation
ollama --version

# 3. Reinstall if necessary
# macOS: brew reinstall ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# 4. Check firewall (macOS)
# System Preferences → Security & Privacy → Firewall → Allow ollama

# 5. Check firewall (Linux)
sudo ufw allow 11434
sudo ufw status
```

#### 3. Model Not Found

**Symptom:** Response has `notice` field: "Model not installed"

**Diagnosis:**
```bash
# List installed models
ollama list

# Check .env model name
grep OLLAMA_MODEL .env

# Test model directly
ollama run phi "test"
```

**Solutions:**
```bash
# 1. Pull the model
ollama pull phi

# 2. Verify model name matches .env
# Model names are case-sensitive: "phi" not "Phi"

# 3. For specific versions
ollama pull phi:2.7b
# Then update .env: OLLAMA_MODEL=phi:2.7b

# 4. List available models online
# Visit https://ollama.com/library
```

#### 4. Port Already in Use

**Symptom:** `Error: [Errno 48] Address already in use`

**Diagnosis:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Example output:
# COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
# python    1234 user   3u  IPv4  12345      0t0  TCP *:8000 (LISTEN)
```

**Solutions:**
```bash
# 1. Kill the process
kill 1234  # Replace with actual PID from lsof

# 2. Use different port
uvicorn app.main:app --port 8001
# Update .env: API_URL=http://127.0.0.1:8001/api/chat

# 3. Using Makefile
make api PORT=8001

# 4. Find all Python processes
ps aux | grep python
```

#### 5. Virtual Environment Not Activated

**Symptom:** `ModuleNotFoundError` despite running pip install

**Diagnosis:**
```bash
# Check which Python is being used
which python
# Should show: /path/to/project/.venv/bin/python
# NOT: /usr/bin/python or /usr/local/bin/python

# Check if venv exists
ls -la .venv
```

**Solutions:**
```bash
# 1. Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\Activate.ps1  # Windows PowerShell

# 2. Verify activation
which python  # Should point to .venv
python -m pip list  # Should show installed packages

# 3. If .venv missing, recreate
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Add to shell profile for convenience
# Add to ~/.bashrc or ~/.zshrc:
alias venv-activate='source .venv/bin/activate'
```

#### 6. Streamlit UI Won't Connect to API

**Symptoms:**
- UI shows connection errors
- "Check API Connection" button shows ❌

**Diagnosis:**
```bash
# 1. Check if API is running
curl http://127.0.0.1:8000/api/health

# 2. Check API_URL in .env
grep API_URL .env

# 3. Test from UI's perspective
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(grep APP_API_KEY .env | cut -d= -f2)" \
  -d '{"messages":[{"role":"user","content":"test"}]}'
```

**Solutions:**
```bash
# 1. Ensure API is running
# In separate terminal:
uvicorn app.main:app --reload

# 2. Verify API_URL is correct
nano .env
# Should be: API_URL=http://127.0.0.1:8000/api/chat
# NOT: http://127.0.0.1:8000 (missing /api/chat)

# 3. Check CORS settings (app/main.py)
# Ensure allow_origins includes UI origin

# 4. Restart Streamlit
# Ctrl+C and rerun (auto-imports helpers from ui/components.py):
streamlit run ui/streamlit_app.py

# 5. Clear Streamlit cache
streamlit cache clear
```

#### 7. Tests Failing

**Unit tests failing:**
```bash
# 1. Ensure virtual environment active
source .venv/bin/activate

# 2. Reinstall dependencies
pip install -r requirements.txt

# 3. Run with verbose output to see exact error
pytest tests/test_auth_api.py -v -s

# 4. Check if test fixtures are working
pytest tests/conftest.py -v

# 5. Isolate the failing test
pytest tests/test_auth_api.py::test_missing_token_returns_401 -vv
```

**Integration tests failing:**
```bash
# 1. Ensure Ollama is running
curl http://127.0.0.1:11434/api/tags

# 2. Start Ollama if not running
ollama serve &

# 3. Ensure model is installed
ollama pull phi

# 4. Run integration tests
pytest -m integration -v

# 5. If still fails, check Ollama logs
# Look at output of `ollama serve` terminal
```

#### 8. Slow Response Times

**Symptoms:**
- Chat responses take >5 seconds
- UI feels sluggish

**Diagnosis:**
```bash
# Check CPU/RAM usage
top -o cpu  # macOS/Linux
# or
htop

# Check Ollama resource usage
ps aux | grep ollama

# Test model directly (bypass API)
time ollama run phi "What is 2+2?"
```

**Solutions:**
```bash
# 1. Use smaller model
ollama pull phi  # Faster than mistral/llama2
# Update .env: OLLAMA_MODEL=phi

# 2. Close other applications

# 3. Check available RAM
free -h  # Linux
vm_stat  # macOS

# 4. Restart Ollama (clears model cache)
killall ollama
ollama serve

# 5. For persistent slow performance:
# Consider upgrading RAM or using quantized models
ollama pull phi:q4_0  # 4-bit quantized version
```

### Debug Mode

**Enable verbose logging:**

```bash
# 1. Set log level in code (app/main.py)
import logging
logging.basicConfig(level=logging.DEBUG)

# 2. Run Uvicorn with debug logs
uvicorn app.main:app --reload --log-level debug

# 3. Enable Streamlit debug mode (layout + helper module)
streamlit run ui/streamlit_app.py --logger.level=debug

# 4. Run tests with output
pytest -v -s  # -s shows print statements
```

### Getting Help

**If issues persist:**

1. ✅ Check [Installation_and_Testing.md](documentation/Installation_and_Testing.md)
2. ✅ Review [Architecture.md](documentation/Architecture.md)
3. ✅ Run preflight: `python scripts/preflight.py`
4. ✅ Check logs for errors
5. ✅ Search GitHub issues: [LLM_Agent_Orchestration_HW1/issues](https://github.com/tomron87/LLM_Agent_Orchestration_HW1/issues)
6. ✅ Open new issue with:
   - OS and Python version
   - Output of `python scripts/preflight.py`
   - Relevant error messages
   - Steps to reproduce

---

## 💻 Development

### Development Workflow

**1. Setup development environment:**
```bash
# Clone and setup
git clone https://github.com/tomron87/LLM_Agent_Orchestration_HW1.git
cd LLM_Agent_Orchestration_HW1
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional: tooling, notebooks, LangChain, etc.
# pip install -r requirements-optional.txt
```

**2. Make changes:**
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes to code
# ...

# Format code
black app/ tests/

# Lint
flake8 app/ tests/

# Type check
mypy app/
```

**3. Test changes:**
```bash
# Run tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Test specific component
pytest tests/test_auth_api.py -v
```

**4. Commit and push:**
```bash
git add .
git commit -m "feat: add feature description"
git push origin feature/your-feature-name
```

### Code Style Guidelines

**Follow PEP 8:**
- Use `black` for formatting
- Max line length: 88 characters
- Use type hints where possible

**Example:**
```python
from typing import List, Dict, Optional

def process_message(
    message: str,
    model: Optional[str] = None,
    temperature: float = 0.7
) -> Dict[str, str]:
    """
    Process user message through LLM.

    Args:
        message: User input text
        model: Optional model override
        temperature: Sampling temperature (0.0-1.0, defaults to 0.2 when omitted)

    Returns:
        Dictionary with session_id, answer, model, notice

    Raises:
        ValueError: If temperature out of range
    """
    ...
```

### Adding New Features

**⚠️ Important**: Before adding new features, review the [Extensibility Guide](documentation/Extensibility_Guide.md) for best practices and established extension points.

The system provides well-defined extension points for:
- Adding new LLM providers (OpenAI, Claude, etc.)
- Custom middleware (logging, rate limiting, metrics)
- Response post-processing hooks
- Custom Pydantic validators
- Authentication extensions

See **[documentation/Extensibility_Guide.md](documentation/Extensibility_Guide.md)** for detailed examples and complete implementation guides.

**Example: Add new API endpoint**

1. **Define schema** in `app/api/routers/chat.py`:
   ```python
   class NewFeatureRequest(BaseModel):
       field1: str
       field2: Optional[int] = None
   ```

2. **Add endpoint**:
   ```python
   @router.post("/new-feature")
   def new_feature(request: NewFeatureRequest):
       ...
   ```

3. **Add tests** in `tests/test_new_feature.py`:
   ```python
   def test_new_feature_success(client, auth_header):
       response = client.post("/api/new-feature", ...)
       assert response.status_code == 200
   ```

4. **Update documentation** in this README and docstrings

### Running Development Server

**With hot reload:**
```bash
uvicorn app.main:app --reload --log-level debug
```

**Watch for file changes:**
```bash
# Install watchdog
pip install watchdog

# Auto-run tests on change
pytest-watch
```

---

## 📁 Project Structure

```
LLM_Agent_Orchestration_HW1/
├── app/                          # FastAPI Application
│   ├── __init__.py
│   ├── main.py                   # Entry point, CORS, middleware
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py              # Dependencies (auth, etc.)
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── chat.py          # Chat endpoints + schemas
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py            # Configuration management
│   └── services/
│       ├── __init__.py
│       ├── chat_service.py      # Business logic
│       └── ollama_client.py     # Ollama HTTP client
│
├── ui/
│   ├── __init__.py              # Treats ui/ as a package for helper imports
│   ├── components.py            # Streamlit helper functions (health checks, payloads, renderers)
│   └── streamlit_app.py         # Streamlit UI layout + event wiring
│
├── tests/                        # Test Suite (35 tests)
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── pytest.ini               # Pytest config
│   ├── test_auth_api.py         # Auth tests (5)
│   ├── test_chat_validation_api.py    # Validation tests (5)
│   ├── test_chat_happy_errors_api.py  # Error handling (3)
│   ├── test_health_api.py       # Health endpoint (2)
│   ├── test_config_settings.py  # Config tests (2)
│   ├── test_ollama_client_unit.py     # Client unit tests (3)
│   ├── test_streamlit_ui.py     # Streamlit AppTest scenarios (11)
│   └── test_ollama_models_integration.py  # Integration (2)
│
├── scripts/
│   ├── preflight.py             # Environment validator
│   ├── check_langchain.py       # LangChain integration check (requires requirements-optional)
│   └── validate_notebooks.py    # Regression checks for notebook CSVs
│
├── documentation/                # Comprehensive docs
│   ├── PRD.md                   # Product requirements
│   ├── Architecture.md          # System architecture
│   ├── Installation_and_Testing.md  # Setup guide
│   ├── Prompting_and_Developing.md  # Development process
│   ├── Screenshots_and_Demonstrations.md  # Visual docs
│   ├── Parameter_Sensitivity_Analysis.md  # Experiment methodology
│   ├── Extensibility_Guide.md    # Extension hooks
│   └── screenshot_images/        # Referenced figures
│
├── notebooks/
│   ├── Results_Analysis.ipynb    # Research visualizations & stats
│   └── data/
│       └── temperature_experiment.csv
│
├── .env                         # Environment config (not in git)
├── .env.example                 # Template for .env
├── .gitignore                   # Git ignore rules
├── Makefile                     # Automation targets
├── requirements.txt             # Core Python dependencies
├── requirements-optional.txt    # Optional LangChain/notebook/tooling deps
├── CLAUDE.md                    # Claude Code AI guide
└── README.md                    # This file
```

### Key Design Patterns

1. **Dependency Injection** - FastAPI's dependency system for auth, services
2. **Repository Pattern** - `ollama_client.py` abstracts Ollama communication
3. **Service Layer** - `chat_service.py` contains business logic
4. **Schema Validation** - Pydantic models at API boundary
5. **Error Mapping** - Business exceptions → HTTP status codes
6. **Configuration Management** - Environment-based with validation
7. **Test Isolation** - Unit tests mock external dependencies

---

## 📚 Documentation

Use this documentation map as a master index—each link explains what it covers and the moment in the workflow when it helps most.

| Document | Purpose | When to read |
|----------|---------|--------------|
| [README.md](README.md) | Setup, run commands, validation checklist | First stop before cloning/running anything |
| [documentation/PRD.md](documentation/PRD.md) | Product goals, KPIs, assumptions, timeline | When confirming scope with stakeholders/grading rubric |
| [documentation/Architecture.md](documentation/Architecture.md) | System diagram, data flow, security posture | Before modifying services, infra, or integrations |
| [documentation/Installation_and_Testing.md](documentation/Installation_and_Testing.md) | Environment prep, pytest/coverage commands, troubleshooting | While setting up locally or validating submissions |
| [documentation/Prompting_and_Developing.md](documentation/Prompting_and_Developing.md) | Prompt engineering approach and dev guardrails | When iterating on agent prompts or dev workflow |
| [documentation/Screenshots_and_Demonstrations.md](documentation/Screenshots_and_Demonstrations.md) | UI walkthrough with annotated screenshots | When instructors need a visual verification |
| [documentation/Parameter_Sensitivity_Analysis.md](documentation/Parameter_Sensitivity_Analysis.md) | Temperature/model experiments, CSV references + link to `scripts/validate_notebooks.py` | While tuning LLM parameters or citing experimentation |
| [notebooks/Results_Analysis.ipynb](notebooks/Results_Analysis.ipynb) | Backing notebook for the parameter study *(needs `requirements-optional.txt`)* | After ingesting the analysis summary to reproduce figures |
| [documentation/Extensibility_Guide.md](documentation/Extensibility_Guide.md) | Future roadmap, extension hooks, effort estimates | When planning extra credit or capstone enhancements |
| [requirements-optional.txt](requirements-optional.txt) | Optional LangChain/notebook dependencies | Only when running notebooks or heavyweight tooling |
| [CLAUDE.md](CLAUDE.md) | Claude-specific usage guide for this repo | Whenever an AI assistant is pairing on this project |

---

## ⚠️ Known Limitations

### Current Limitations

1. **No Streaming** - Responses are not streamed token-by-token (planned for future)
2. **Single User** - No multi-user support or user management
3. **No Conversation History** - Sessions not persisted (in-memory only)
4. **No RAG** - No retrieval augmented generation yet
5. **Local Only** - Requires local Ollama installation (no cloud LLM support)
6. **No Rate Limiting** - API has no built-in rate limits (add reverse proxy for production)
7. **Basic Auth** - Simple Bearer token (consider OAuth2 for production)
8. **No Metrics** - No built-in Prometheus/Grafana integration
9. **macOS Optimized** - Some scripts may need adjustment for Windows

### Performance Constraints

- **Model Size** - Limited by available RAM
- **Concurrent Requests** - Not optimized for high concurrency (single-threaded Ollama)
- **Response Time** - Depends on model size and hardware (2-5s typical)

### Security Considerations

- **No HTTPS** - Local deployment only, no TLS
- **No Input Sanitization** - Relies on Ollama's safety (add for production)
- **Secrets in .env** - Ensure `.env` is not committed or exposed
- **No Audit Logs** - No tracking of API usage or requests

---

## 🚀 Future Extensions

The architecture is designed to support:

### Planned Features

**Streaming Responses** (High Priority)
- Server-Sent Events (SSE) for real-time token streaming
- WebSocket support for bidirectional communication
- Progress indicators in UI

**Conversation Management**
- Session persistence with SQLite or Redis
- Conversation history with pagination
- Export conversations to JSON/Markdown

**Multi-Model Routing**
- Dynamic model selection based on query type
- Model performance comparison
- Automatic fallback if model unavailable

**RAG (Retrieval Augmented Generation)**
- Vector database integration (FAISS, Chroma, Pinecone)
- Document upload and indexing
- Semantic search with embeddings
- Citation tracking

**LangChain/LangGraph Integration**
- Chain-of-thought prompting
- Agent workflows with tools
- Memory modules for long-term context

**Agent Orchestration**
- Multi-agent collaboration
- Specialized agents (researcher, coder, reviewer)
- Inter-agent communication protocols

### Observability Improvements

- **Structured Logging** - JSON logs with correlation IDs
- **Metrics** - Prometheus integration (response times, error rates)
- **Tracing** - OpenTelemetry for distributed tracing
- **Dashboards** - Grafana dashboards for real-time monitoring

### Security Enhancements

- **OAuth2/OIDC** - Industry-standard authentication
- **API Key Management** - Key rotation, expiry, scoping
- **Rate Limiting** - Per-user or per-IP limits
- **Input Validation** - SQL injection, XSS prevention
- **Audit Logs** - Track all API calls with user context
- **RBAC** - Role-based access control for different user tiers

### UI/UX Improvements

- **Conversation History UI** - Browse and search past conversations
- **File Upload** - PDF, DOCX support for RAG
- **Model Status Indicator** - Real-time availability in UI
- **Export Options** - Download chats as PDF/Markdown
- **Dark Mode** - Theme toggle
- **Keyboard Shortcuts** - Power user features
- **Mobile Responsive** - Better mobile experience

### DevOps

- **Docker Compose** - Single-command deployment
- **Kubernetes Manifests** - Cloud deployment ready
- **CI/CD Pipeline** - GitHub Actions for testing and deployment
- **Health Checks** - Kubernetes-compatible probes
- **Auto-scaling** - Based on request volume

---

## 🤝 Contributing

This project was developed as an academic assignment. However, contributions are welcome:

### How to Contribute

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** Pull Request

### Contribution Guidelines

- Follow existing code style (use `black` formatter)
- Add tests for new features
- Update documentation
- Ensure all tests pass: `make test`
- Keep PRs focused and atomic

### Areas for Contribution

- 🐛 Bug fixes
- 📝 Documentation improvements
- ✨ New features (see [Future Extensions](#-future-extensions))
- 🧪 Additional test coverage
- ⚡ Performance optimizations

---

## 📄 License

This project is provided **as-is for educational purposes** as part of the "LLMs and MultiAgent Orchestration" course at Reichman University.

**Usage Rights:**
- ✅ Use for learning and education
- ✅ Modify for personal projects
- ✅ Fork and adapt for your needs
- ⚠️ Not licensed for commercial use without permission

---

## 🙏 Acknowledgments

### Contributors
- **Igor Nazarenko** - Co-developer
- **Tom Ron** - Co-developer
- **Roie Gilad** - Co-developer

### Mentors & Instructors
- **Dr. Yoram Gal** - Course instructor and guidance

### Technologies & Tools
- **[Ollama Team](https://ollama.com)** - Excellent local LLM platform
- **[FastAPI](https://fastapi.tiangolo.com)** - Modern Python web framework
- **[Streamlit](https://streamlit.io)** - Intuitive UI framework
- **[Pydantic](https://docs.pydantic.dev)** - Data validation
- **[Pytest](https://pytest.org)** - Testing framework

### AI Assistants
- **ChatGPT** - Development assistance and code review
- **Claude** - Architecture design and documentation
- **Ollama (Phi, Mistral)** - Local LLM testing

---

## 📞 Support

### Getting Help

**For setup/installation issues:**
1. ✅ Run preflight check: `python scripts/preflight.py`
2. ✅ Check [Troubleshooting](#-troubleshooting) section
3. ✅ Review [Installation_and_Testing.md](documentation/Installation_and_Testing.md)

**For development questions:**
1. ✅ Check [Architecture.md](documentation/Architecture.md)
2. ✅ Review [CLAUDE.md](CLAUDE.md) for development patterns
3. ✅ Examine existing tests for examples

**For bugs or feature requests:**
1. ✅ Search [GitHub Issues](https://github.com/tomron87/LLM_Agent_Orchestration_HW1/issues)
2. ✅ Open new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (`python --version`, OS, etc.)

---

## 📈 Project Stats

- **Total Lines of Code**: ~2,500 (excluding tests)
- **Test Coverage**: 89% (make coverage on 2025-11-12; UI AppTest suite covers guard rails + errors)
- **Number of Tests**: 35 (33 unit + 2 integration)
- **Documentation Pages**: 7
- **Supported Models**: All Ollama models
- **Supported Platforms**: macOS, Linux, Windows (WSL)

---

**🎯 Built with ❤️ using AI-assisted development**

*This project demonstrates best practices in:*
- ✨ Clean architecture and separation of concerns
- 🧪 Comprehensive testing (unit + integration)
- 📚 Professional documentation
- ⚙️ DevOps automation (Makefile)
- 🔒 Security-first design
- 🎯 Type safety and validation
- 🚀 Production-ready error handling
- 📊 Observable and debuggable systems
