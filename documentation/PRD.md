# 📘 Product Requirements Document (PRD)

## 1. Background and System Purpose
The project's goal is to build an interactive chat system that operates with local Artificial Intelligence models (LLMs) using **Ollama**, including a graphical user interface (Streamlit) and an independent API (FastAPI).
The system enables sending requests to a local model, conversation management, environment health checks, and end-to-end execution — with emphasis on modular architecture, readable code, and future extensibility.

The system was developed as part of the "LLMs and MultiAgent Orchestration" course instructed by Dr. Yoram Gal, as part of Assignment 1.

---

## 2. Main Objectives
- **Establish complete communication interface** between user and local AI model through Ollama server.
- **Develop standard API** using FastAPI with access controls, business logic and request management.
- **Develop graphical user interface (UI)** using Streamlit, for displaying real-time communication.
- **Ensure complete portability** (works locally without dependency on global installations).
- **Implement unit and integration tests**, according to industry standards.
- **Professional documentation** at every stage (PRD, architecture, installation and testing, Prompting).

---

## 3. System Content
The system includes three core components:

| Component | Description |
|------|--------|
| **API Backend (FastAPI)** | Server for managing chat requests, connection to Ollama model, authentication using API key. |
| **Ollama Client** | Service component for managing communication with local Ollama server, including sending prompt and receiving response. |
| **Streamlit UI** | Interactive graphical user interface displaying real-time conversation between user and model. |

The system is built modularly so each component can be replaced or extended (for example: model replacement, agent logic addition, future Plugins addition).

---

## 4. Functional Requirements

| Category | Requirement |
|----------|--------|
| **Real-time chat** | User enters text in interface, system sends request to model and returns response in real-time. |
| **Error and exception handling** | Handling failure situations in Ollama connection, displaying error message to user. |
| **Secured API** | Required use of access key (`APP_API_KEY`) for authentication and usage control. |
| **Preflight Check** | Automatic check script verifying system is ready to run (Python, packages, Ollama, variables). |
| **Tests** | Unit and integration tests available in `tests/` directory. |

---

## 5. Non-Functional Requirements
- **Performance:** Initial response within ≤2 seconds with local model.
- **Reliability:** System supports repeated running without crashes or memory leaks.
- **Security:** Use of environment keys and not hardcoded fields in code.
- **Portability:** Complete operation from any computer with Ollama installed.
- **Accessibility:** Simple and clear graphical interface, suitable for local operation without CLI.
- **Maintainability:** Readable code, separated into modules, supported by complete documentation.

---

## 6. System Requirements and Installation
The system operates in **Python 3.10+** environment, with local **Ollama** installation.
Installation is performed according to steps detailed in [Installation_and_Testing.md](Installation_and_Testing.md) document.

Required components:
- Operating system: macOS / Linux / Windows (with WSL)
- Dependencies: `fastapi`, `requests`, `streamlit`, `python-dotenv`, `pydantic`
- Local connection to Ollama server available at `http://127.0.0.1:11434`

---

## 7. System Structure and Architecture
Project structure is described in detail in [Architecture.md](Architecture.md) document.

**General diagram:**
```
User → Streamlit UI → FastAPI (Chat Router) → Ollama Client → Ollama Server (Local Model)
```

**Main directory structure:**
```
HW1/
├── app/
│   ├── api/
│   │   ├── routers/chat.py
│   │   └── deps.py
│   ├── core/config.py
│   ├── services/
│   │   ├── ollama_client.py
│   │   └── chat_service.py
│   └── main.py
├── ui/streamlit_app.py
├── tests/
├── scripts/
├── documentation/
├── README.md
├── Makefile
├── .env.example
├── .env
├── requirements.txt
└── .gitignore
```

---

## 8. Testing and QA

| Type | Purpose | Location |
|------|--------|--------|
| **Unit Tests** | Unit tests for API components, ChatService and OllamaClient | `/tests/test_*_api.py`, `/tests/test_ollama_client_unit.py` |
| **Integration Tests** | Real communication tests against local Ollama server | `/tests/test_ollama_models_integration.py` |
| **Preflight Script** | Validates environment (Python, packages, Ollama, environment variables) | `/scripts/preflight.py` |

Tests are implemented using **pytest**, with use of **single marker**:
- `@pytest.mark.integration` for integration tests.
- Any test not marked is considered Unit type and run using `pytest -m "not integration"`.

The entire execution and testing process is managed through **Makefile**, defining complete flow:
> `preflight → install → ollama → api → ui → tests`

For complete details of Makefile commands, execution instructions and testing environment –
see [**Installation_and_Testing.md**](Installation_and_Testing.md) document.

These tests are designed to ensure **reliability, health and complete execution ability** before submission,
and to ensure the system operates consistently in any testing environment.

---

## 9. Future Extensions
- Support for multiple models (for example: Llama 3, Phi 3, Mistral).
- Addition of **Agent Logic** – internal agent with context management and long-term memory storage.
- Support for conversation history and Session storage.
- Connection to vector database (Vector DB) for contextual retrieval.
- Integration of Speech-to-Text / Text-to-Speech.
- User management interface.

---

## 10. Summary
This document defines all requirements and specifications for the Ollama-based local chat project.
The system was developed according to course requirements and submission guidelines (public GitHub, complete README, unit tests and documentation).
For technical depth, refer to accompanying documents:
- 📘 **[Architecture.md](Architecture.md)** – Structure details, data flow and system diagrams
- 🧪 **[Installation_and_Testing.md](Installation_and_Testing.md)** – Installation, execution and testing instructions
- 🤖 **[Prompting_and_Developing.md](Prompting_and_Developing.md)** – Development process documentation using AI
- 🖼️ **[Screenshots_and_Demonstrations.md](Screenshots_and_Demonstrations.md)** – System in action documentation including screenshots
