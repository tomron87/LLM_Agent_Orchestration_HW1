# 🖼️ Screenshots and Demonstrations

## 🎯 Document Purpose
This document presents screenshots and demonstrations of the chat system built as part of the project.
The goal is to illustrate the system's functioning in real-time — from starting the servers to routine use of the graphical interface.
The images accompany the main stages of work according to specifications and architecture described in other documents.

---

## 🧭 Stage 1 – Opening Screen and Settings

When opening the application, the user is presented with an opening screen including model selection, server connection health check, and API key entry.

📸 [UI_interface_welcome.png](screenshot_images/UI_interface_welcome.png)

> The screenshot shows input fields, "Check API" button.

---

## 💬 Stage 2 – Conversation with Bot

Demonstration of chat interface in action – user sends message, system returns response, and shows response time indication and "copy" button.

📸 [UI_chat_interface.png](screenshot_images/UI_chat_interface.png)

> The screenshot shows consistent and clear design between user messages and system responses.

### 🎚️ Temperature Control Highlight

After wiring the decoding controls end-to-end, the UI now exposes a temperature slider so users can choose between deterministic (0.0) and creative (1.0) responses directly from the chat screen.

📸 [temperature_value_setup.png](screenshot_images/temperature_value_setup.png)

> The slider caption explains the trade-off: low values favor accuracy and repeatability, high values add creativity at the cost of consistency.

---

## ⚙️ Stage 3 – Model Management and API Connection

Screenshot demonstrating changing active model through interface (for example moving from Phi to Mistral), and connection health check result to Ollama using API Health Check.

📸 [api_health.png](screenshot_images/api_health.png)

📸 [model_selection.png](screenshot_images/model_selection.png)
> The image shows model selection interface and connection check result.

---

## 🧪 Stage 4 – Tests and Error Messages

### ⚠️ Server or Model Problems
Screenshots showing cases where Ollama server is not active or desired model is not installed.

📸 [error_ollama_server_off.png](screenshot_images/error_ollama_server_off.png)
📸 [error_ollama_model_installation.png](screenshot_images/error_ollama_model_installation.png)

> Screenshots show warning messages when server is not active or model is not installed.

### 🔑 API Key or Address Problems
Illustration for situations where API key is missing, wrong, or server address is incorrect.

📸 [error_api_key_missing.png](screenshot_images/error_api_key_missing.png)
📸 [error_api_url_wrong.png](screenshot_images/error_api_url_wrong.png)

> Screenshots show error messages in interface (for example: "API key invalid" or "Model not found").

### 💭 Empty Response Problems
Scenario where request succeeds but model returns empty response.

📸 [error_.empty_answer.png](screenshot_images/error_.empty_answer.png)

> Screenshot shows alert about empty response — without execution or connection error occurring.

### 📊 Automated Coverage Report (`make coverage`)

Demonstration of the CLI workflow that generates the official coverage numbers cited in README/PRD. The `make coverage` target runs:

```bash
pytest --cov=app --cov=ui --cov-report=term-missing --cov-report=html
```

📸 [make_coverage_test.png](screenshot_images/make_coverage_test.png)

> The screenshot shows the terminal summary produced by `make coverage`, confirming the 35-test suite (33 unit + 2 integration) and the generation of the HTML report under `htmlcov/index.html`.

---

## 🧰 Stage 5 – Logs and Console Display

This section shows screenshots from development environment (terminal) demonstrating server and UI execution.

### 🚀 Running Ollama Server
Screenshot of Ollama execution using `make ollama` command.

📸 [ollama_server_initiation.png](screenshot_images/ollama_server_initiation.png)

> Shows Ollama server starting up and its local host address.

### 🌐 Running FastAPI Server
Screenshot of API server execution during system loading and request execution.

📸 [api_logs.png](screenshot_images/api_logs.png)
📸 [api_logs_chat.png](screenshot_images/api_logs_chat.png)

> Shows API calls and real-time responses from server.

### 💻 Running User Interface (UI)
Screenshot of UI interface execution using `make ui` command.

📸 [ui_logs_initiation.png](screenshot_images/ui_logs_initiation.png)

> Shows interface activation, browser opening, and link to UI's local address.

---

## 🧾 Summary

The document presents main scenarios for system activation and illustrates its stability and communication process between Frontend (Streamlit), Backend (FastAPI) and language model (Ollama).
The images reflect main stages in work, and demonstrate design principles — simplicity, clarity, and future extensibility possibility.

> All images are stored in `documentation/screenshot_images/` directory.
