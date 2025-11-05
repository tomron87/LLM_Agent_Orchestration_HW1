# 🤖 Local AI Chat Agent

> **Interactive chat interface with local LLM using Ollama + FastAPI + Streamlit**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green.svg)](https://ollama.ai/)

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
- [Testing](#-testing)
- [Configuration](#️-configuration)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)
- [Documentation](#-documentation)
- [Future Extensions](#-future-extensions)

---

## 🎯 Overview

This project is a **local AI chat system** that enables interactive conversations with Large Language Models (LLMs) running entirely on your machine using **Ollama**. The system features a modern architecture separating concerns into three layers: a FastAPI backend, a Streamlit user interface, and an Ollama client service.

**Key Characteristics:**
- ✅ **100% Local** - No cloud dependencies, complete privacy
- ✅ **Production-Ready** - Comprehensive testing, error handling, and validation
- ✅ **Modular Architecture** - Clean separation between API, business logic, and infrastructure
- ✅ **Developer-Friendly** - Complete documentation, Makefile automation, and preflight checks
- ✅ **Extensible** - Ready for RAG, multi-model routing, and agent orchestration

---

## 🏫 Course Information
- **Assignment:** Assignment 1 – AI Chat Bot
- **Course:** LLMs and MultiAgent Orchestration
- **Instructor:** Dr. Yoram Gal
- **Students:** Igor Nazarenko and partner (if applicable)
- **Submission Date:** November 2025
- **Repository:** [GitHub Repository](../)

---

## 🌟 Key Features

### Core Functionality
- **Real-time Chat** - Interactive conversation with local LLM models
- **Multi-Model Support** - Switch between Phi, Llama, Mistral, and other Ollama models
- **Bearer Token Authentication** - Secure API access control
- **Health Monitoring** - Real-time system and model availability checks
- **Error Handling** - Graceful degradation with user-friendly error messages

### Developer Features
- **Comprehensive Testing** - Unit tests (mocked) and integration tests (real Ollama)
- **Automated Setup** - Makefile targets for one-command execution
- **Preflight Checks** - Environment validation before startup
- **Type Safety** - Pydantic schemas for request/response validation
- **Detailed Logging** - Debug and production-ready logging

---

## 🏗️ Architecture

The system follows a **three-layer architecture**:

```
┌─────────────────┐
│  Streamlit UI   │  ← User Interface Layer
└────────┬────────┘
         │ HTTP POST /api/chat
         │ Bearer Token
┌────────▼────────┐
│  FastAPI API    │  ← HTTP Layer
│  - Routing      │    • Request validation (Pydantic)
│  - Auth         │    • Bearer token authentication
│  - Validation   │    • Error mapping to HTTP codes
└────────┬────────┘
         │
┌────────▼────────┐
│  Chat Service   │  ← Business Logic Layer
│  - Model check  │    • Model existence validation
│  - Session mgmt │    • Response formatting
│  - Logic        │    • Notice generation
└────────┬────────┘
         │
┌────────▼────────┐
│ Ollama Client   │  ← Infrastructure Layer
│  - HTTP client  │    • Network communication
│  - Error        │    • Timeout handling
│    handling     │    • Response parsing
└────────┬────────┘
         │
┌────────▼────────┐
│  Ollama Server  │  ← Local LLM
│  (phi/mistral)  │
└─────────────────┘
```

### Data Flow

1. **User** enters message in Streamlit UI
2. **UI** sends POST request to `/api/chat` with Bearer token
3. **FastAPI Router** validates authentication and request schema
4. **Chat Service** checks if model exists
   - If missing → returns friendly notice
   - If exists → calls Ollama Client
5. **Ollama Client** communicates with local Ollama server
6. **Response** flows back up the stack with structured JSON

### Response Format
```json
{
  "session_id": "sess-xxxxxxxx",
  "answer": "Model's response text",
  "model": "phi",
  "notice": null
}
```

---

## ✅ Prerequisites

### Required
- **Python 3.10+** (recommended: Python 3.10.x)
- **Ollama** - Download from [ollama.com](https://ollama.com)
- **Git** (recommended) - For cloning repository

### System Requirements
- **Operating System:** macOS / Linux / Windows 10+ (with WSL)
- **RAM:** 8GB+ recommended (for running LLM models)
- **Disk Space:** 5GB+ for models
- **Network:** Port 11434 (Ollama) and 8000 (FastAPI) available

### Installation Check
```bash
python --version  # Should show 3.10 or higher
ollama --version  # Should show Ollama version
git --version     # Optional but recommended
```

---

## 🚀 Quick Start

For experienced users, here's the fastest path to running the application:

```bash
# 1. Clone and navigate
cd path/to/HW1_ai_chat_bot

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env: Set APP_API_KEY to any value (e.g., "my-secret-key-123")

# 5. Install Ollama model
ollama pull phi

# 6. Run everything (one command)
make all
```

The application will start:
- API: http://127.0.0.1:8000
- UI: http://127.0.0.1:8501 (opens automatically in browser)

---

## 📦 Installation Guide

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd HW1_ai_chat_bot
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

You should see `(.venv)` prefix in your terminal.

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (API server)
- Streamlit (UI)
- Pydantic (validation)
- python-dotenv (configuration)
- pytest (testing)
- requests (HTTP client)

### Step 4: Install and Configure Ollama

#### Install Ollama
Visit [ollama.com](https://ollama.com) and download for your OS.

**macOS:**
```bash
# Download from website or use Homebrew
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download installer from ollama.com

#### Pull Model
```bash
# Start Ollama server (keep running in separate terminal)
ollama serve

# Pull a model (in another terminal)
ollama pull phi        # Recommended: small, fast
# or
ollama pull mistral    # Alternative: larger, more capable
# or
ollama pull llama2     # Alternative: Meta's model
```

Verify model installed:
```bash
ollama list
```

### Step 5: Configure Environment Variables

Create `.env` file in project root:

```bash
cp .env.example .env
```

Edit `.env` with your preferred text editor and set these **required** values:

```dotenv
# API Authentication (REQUIRED - change to any secret value)
APP_API_KEY=my-secret-key-123

# Ollama Configuration (usually keep defaults)
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=phi

# API URL for UI (usually keep default)
API_URL=http://127.0.0.1:8000/api/chat
```

**Important Notes:**
- `APP_API_KEY`: Must be changed from placeholder. Use any secret string.
- `OLLAMA_HOST`: Only change if Ollama runs on different port/host
- `OLLAMA_MODEL`: Must match a model you've pulled with `ollama pull`
- `API_URL`: Only change if running API on different port

### Step 6: Run Preflight Check

Verify everything is configured correctly:

```bash
python scripts/preflight.py
```

Expected output:
```
[OK] Python version 3.10+
[OK] Required packages installed
[OK] Ollama server reachable
[OK] Model 'phi' installed
[OK] Environment variables set
```

If any `[FAIL]` appears, follow the hints to fix issues.

---

## ▶️ Running the Application

### Method 1: Using Makefile (Recommended)

The Makefile provides convenient commands for all operations:

```bash
# See all available commands
make help

# Run complete startup (preflight -> install -> ollama -> api -> ui)
make all

# Or run services individually in separate terminals:

# Terminal 1: Start API
make api

# Terminal 2: Start UI
make ui
```

### Method 2: Manual Execution

If you prefer running services manually:

#### Terminal 1: Start Ollama (if not already running)
```bash
ollama serve
```
Leave this running.

#### Terminal 2: Start FastAPI Backend
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

#### Terminal 3: Start Streamlit UI
```bash
streamlit run ui/streamlit_app.py --server.port 8501
```

Streamlit will automatically open your browser to `http://localhost:8501`.

If browser doesn't open, manually navigate to:
- http://localhost:8501
- http://127.0.0.1:8501

### Verify Everything Works

#### 1. Check API Health
```bash
curl http://127.0.0.1:8000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "ollama": true,
  "default_model": "phi"
}
```

#### 2. Test Chat Endpoint
Replace `YOUR_API_KEY` with the value from your `.env` file:

```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"messages":[{"role":"user","content":"Hello!"}]}'
```

Expected response:
```json
{
  "session_id": "sess-a1b2c3d4",
  "answer": "Hello! How can I help you today?",
  "model": "phi",
  "notice": null
}
```

#### 3. Use the UI

1. Open browser to http://localhost:8501
2. Enter your API key in the sidebar (same as `.env` APP_API_KEY)
3. Select model (should show "phi" or whichever model you installed)
4. Click "Check API Connection" to verify
5. Type a message and click "Send"

---

## 🧪 Testing

The project includes comprehensive test suite with both unit and integration tests.

### Quick Test Commands

```bash
# Run ALL tests
make test
# or
pytest -q

# Run ONLY unit tests (no Ollama required)
make test-unit
# or
pytest -m "not integration" -q

# Run ONLY integration tests (requires Ollama running)
make test-integration
# or
pytest -m integration -q

# Run specific test file
pytest tests/test_auth_api.py -v

# Run specific test function
pytest tests/test_auth_api.py::test_missing_token_returns_401 -v
```

### Test Categories

#### Unit Tests (No External Dependencies)
These tests use mocking and don't require Ollama to be running:

- `test_auth_api.py` - Bearer token authentication (401 errors, valid/invalid tokens)
- `test_chat_validation_api.py` - Request validation (empty messages, missing fields, type errors)
- `test_chat_happy_errors_api.py` - Happy path and error handling (mocked responses, 5xx errors, missing models)
- `test_health_api.py` - Health endpoint consistency
- `test_config_settings.py` - Configuration loading and defaults
- `test_ollama_client_unit.py` - Ollama client with mocked HTTP requests

#### Integration Tests (Require Ollama)
These tests communicate with real Ollama server:

- `test_ollama_models_integration.py` - Real ping tests, model availability checks

**Note:** Integration tests are automatically **SKIPPED** if Ollama is not running (not marked as FAILED).

### Understanding Test Output

Tests use custom formatting from `conftest.py`:

```
tests/test_auth_api.py
  test_missing_token_returns_401 ... PASSED
    EXPECTED: 401 with 'Missing bearer token'
  test_invalid_token_returns_401 ... PASSED
    EXPECTED: 401 with 'Invalid API key'
  >>> FILE STATUS: ALL PASSED
```

If a test fails:
```
tests/test_auth_api.py
  test_invalid_token_returns_401 ... FAILED
    EXPECTED: 401 with 'Invalid API key'
    ACTUAL:   status=200 body={...}
```

### Test Coverage Summary

| Test File | Tests | Purpose |
|-----------|-------|---------|
| `test_auth_api.py` | 5 | Authentication and authorization |
| `test_chat_validation_api.py` | 5 | Request schema validation |
| `test_chat_happy_errors_api.py` | 3 | Happy path and error scenarios |
| `test_health_api.py` | 2 | Health endpoint reliability |
| `test_config_settings.py` | 2 | Configuration management |
| `test_ollama_client_unit.py` | 3 | HTTP client behavior |
| `test_ollama_models_integration.py` | 2 | Real Ollama integration |

**Total:** 22 tests ensuring reliability across all layers

---

## ⚙️ Configuration

### Environment Variables

All configuration is managed through `.env` file:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_API_KEY` | Secret key for Bearer token authentication | No default | ✅ Yes |
| `OLLAMA_HOST` | Ollama server URL | `http://127.0.0.1:11434` | ✅ Yes |
| `OLLAMA_MODEL` | Default model name | `phi` | ✅ Yes |
| `API_URL` | FastAPI endpoint for UI | `http://127.0.0.1:8000/api/chat` | ✅ Yes |

### Advanced Configuration

#### Running on Different Ports

**API on different port:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
# Update API_URL in .env to match
```

**UI on different port:**
```bash
streamlit run ui/streamlit_app.py --server.port 8502
```

**Using Makefile:**
```bash
make api PORT=8001
make ui STREAMLIT_PORT=8502
```

#### Using Different Models

1. Pull the model:
   ```bash
   ollama pull llama2
   ```

2. Update `.env`:
   ```dotenv
   OLLAMA_MODEL=llama2
   ```

3. Restart services

Available models: https://ollama.com/library

#### Remote Ollama Server

If Ollama runs on different machine:

```dotenv
OLLAMA_HOST=http://192.168.1.100:11434
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. "401 Unauthorized" Error

**Symptom:** API returns 401 when calling `/api/chat`

**Causes & Solutions:**
- `APP_API_KEY` is still placeholder `change-me`:
  ```bash
  # Edit .env and set real value
  APP_API_KEY=my-actual-secret-key
  ```

- Missing Authorization header:
  ```bash
  # Include header in requests:
  -H "Authorization: Bearer YOUR_KEY_HERE"
  ```

- Key mismatch between `.env` and request:
  ```bash
  # Verify they match exactly:
  echo $APP_API_KEY  # Should match what you send in requests
  ```

#### 2. "Connection Refused" to Ollama

**Symptom:** Can't reach Ollama server

**Solutions:**
```bash
# 1. Check if Ollama is running:
curl http://127.0.0.1:11434/api/tags

# 2. If not, start it:
ollama serve

# 3. If still fails, check firewall:
# macOS: System Preferences → Security & Privacy → Firewall
# Linux: sudo ufw allow 11434
```

#### 3. Model Not Found

**Symptom:** Response has `notice` field saying model not installed

**Solution:**
```bash
# 1. Check installed models:
ollama list

# 2. If model missing, pull it:
ollama pull phi

# 3. Verify .env has correct model name:
grep OLLAMA_MODEL .env
```

#### 4. Port Already in Use

**Symptom:** `Address already in use` error

**Solutions:**
```bash
# Find process using port:
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port:
make api PORT=8001
```

#### 5. Virtual Environment Not Activated

**Symptom:** `ModuleNotFoundError` when running commands

**Solution:**
```bash
# Activate virtual environment:
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Verify:
which python  # Should show .venv/bin/python
```

#### 6. Streamlit UI Won't Connect to API

**Symptoms:**
- UI shows connection errors
- Can't send messages

**Solutions:**
```bash
# 1. Verify API_URL in .env:
grep API_URL .env
# Should be: http://127.0.0.1:8000/api/chat

# 2. Check API is running:
curl http://127.0.0.1:8000/api/health

# 3. Restart Streamlit:
# Ctrl+C to stop, then:
streamlit run ui/streamlit_app.py
```

#### 7. Tests Failing

**Unit tests failing:**
```bash
# Ensure virtual environment active and dependencies installed:
source .venv/bin/activate
pip install -r requirements.txt

# Run with verbose output:
pytest tests/test_auth_api.py -v
```

**Integration tests failing:**
```bash
# Ensure Ollama running:
ollama serve

# Ensure model installed:
ollama pull phi

# Run integration tests:
pytest -m integration -v
```

### Debug Mode

Enable detailed logging:

```bash
# Set log level in code (app/main.py)
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with verbose output:
uvicorn app.main:app --reload --log-level debug
```

### Getting Help

If issues persist:

1. Check [Installation_and_Testing.md](documentation/Installation_and_Testing.md) for detailed troubleshooting
2. Review [Architecture.md](documentation/Architecture.md) for system design
3. Run preflight check: `python scripts/preflight.py`
4. Check application logs for error messages

---

## 📁 Project Structure

```
HW1_ai_chat_bot/
├── app/                          # FastAPI Backend
│   ├── main.py                   # Application entry point, CORS config
│   ├── api/
│   │   ├── deps.py              # Authentication dependency (Bearer token)
│   │   └── routers/
│   │       └── chat.py          # Chat endpoint, Pydantic schemas
│   ├── core/
│   │   └── config.py            # Environment variable loading
│   └── services/
│       ├── chat_service.py      # Business logic layer
│       └── ollama_client.py     # Ollama HTTP client
│
├── ui/
│   └── streamlit_app.py         # Streamlit user interface
│
├── tests/                        # Test Suite
│   ├── conftest.py              # Shared fixtures, test formatting
│   ├── pytest.ini               # Pytest configuration
│   ├── test_auth_api.py         # Authentication tests
│   ├── test_chat_validation_api.py    # Validation tests
│   ├── test_chat_happy_errors_api.py  # Error handling tests
│   ├── test_health_api.py       # Health endpoint tests
│   ├── test_config_settings.py  # Configuration tests
│   ├── test_ollama_client_unit.py     # Unit tests (mocked)
│   └── test_ollama_models_integration.py  # Integration tests
│
├── scripts/
│   ├── preflight.py             # Environment validation
│   └── check_langchain.py       # LangChain integration check
│
├── documentation/                # Comprehensive Documentation
│   ├── PRD.md                   # Product Requirements
│   ├── Architecture.md          # System architecture details
│   ├── Installation_and_Testing.md  # Setup and testing guide
│   ├── Prompting_and_Developing.md  # Development process
│   └── Screenshots_and_Demonstrations.md  # Visual documentation
│
├── .env                         # Environment configuration (create from .env.example)
├── .env.example                 # Example environment file
├── requirements.txt             # Python dependencies
├── Makefile                     # Automation commands
├── CLAUDE.md                    # Guide for Claude Code AI assistant
└── README.md                    # This file
```

### Key Files Explained

**Backend (app/):**
- `main.py` - FastAPI app initialization, middleware, route registration
- `api/deps.py` - Security: Bearer token verification
- `api/routers/chat.py` - HTTP layer: routing, validation, error mapping
- `services/chat_service.py` - Business layer: model checking, session management
- `services/ollama_client.py` - Infrastructure: HTTP communication with Ollama
- `core/config.py` - Configuration management with Pydantic

**Frontend (ui/):**
- `streamlit_app.py` - Complete UI implementation with state management

**Tests (tests/):**
- `conftest.py` - Shared fixtures (`client`, `auth_header`, `DummyResp`)
- `pytest.ini` - Test configuration and markers
- `test_*.py` - Comprehensive test coverage for all layers

**Automation:**
- `Makefile` - One-command execution for all operations
- `scripts/preflight.py` - Pre-flight environment validation

---

## 📚 Documentation

This project includes extensive documentation:

| Document | Description |
|----------|-------------|
| [README.md](README.md) | **This file** - Complete guide to installation and usage |
| [CLAUDE.md](CLAUDE.md) | Guide for Claude Code AI assistant when working with this repo |
| [Architecture.md](documentation/Architecture.md) | System architecture, data flow, security, future extensions |
| [Installation_and_Testing.md](documentation/Installation_and_Testing.md) | Detailed setup instructions, test explanations, troubleshooting |
| [PRD.md](documentation/PRD.md) | Product requirements document |
| [Prompting_and_Developing.md](documentation/Prompting_and_Developing.md) | Development process and AI tool usage |
| [Screenshots_and_Demonstrations.md](documentation/Screenshots_and_Demonstrations.md) | Visual demonstrations of the system |

---

## 🚀 Future Extensions

The architecture is designed to support future enhancements:

### Planned Features
- **Streaming Responses** - Server-Sent Events (SSE) or WebSocket for real-time token streaming
- **Conversation History** - Session persistence with Redis or simple database
- **Multi-Model Routing** - Dynamic model selection based on query complexity
- **RAG (Retrieval Augmented Generation)** - Integration with vector databases (FAISS, Chroma)
- **LangChain Integration** - Advanced prompting and chain-of-thought
- **Agent Orchestration** - Multi-agent workflows with specialized capabilities

### Observability
- **Structured Logging** - JSON logs for better parsing
- **Metrics** - Prometheus integration for monitoring
- **Tracing** - OpenTelemetry for distributed tracing

### Security Enhancements
- **Rate Limiting** - Prevent abuse
- **Role-Based Access** - Multiple user tiers
- **Request Size Limits** - Prevent large payload attacks
- **Input Sanitization** - Additional validation layers

### UI Improvements
- **Conversation History** - View past chats
- **File Uploads** - Document-based Q&A
- **Model Status** - Real-time availability indicator
- **Export Conversations** - Save chats to files

---

## 🤝 Contributing

This project was developed as part of an academic assignment. While it's not actively maintained, you're welcome to:

- Fork the repository
- Use it as a learning resource
- Adapt it for your own projects
- Report issues (though they may not be addressed)

---

## 📄 License

This project is provided as-is for educational purposes as part of the "LLMs and MultiAgent Orchestration" course.

---

## 🙏 Acknowledgments

- **Dr. Yoram Gal** - Course instructor
- **Ollama Team** - For the excellent local LLM platform
- **FastAPI & Streamlit** - For powerful, developer-friendly frameworks
- **AI Tools** - ChatGPT, Claude, and Ollama for development assistance

---

## 📞 Support

For questions or issues:

1. Check the [Documentation](#-documentation)
2. Run `python scripts/preflight.py` for environment issues
3. Review [Troubleshooting](#-troubleshooting) section
4. Check test output for specific errors: `pytest -v`

---

**Built with ❤️ using AI-assisted development**

*This project demonstrates best practices in:*
- Clean architecture and separation of concerns
- Comprehensive testing (unit + integration)
- Professional documentation
- DevOps automation (Makefile)
- Security-first design
- Type safety and validation
