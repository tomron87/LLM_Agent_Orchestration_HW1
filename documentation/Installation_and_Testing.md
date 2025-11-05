# 📦 Installation and Testing — HW1_ai_chat_bot

This document explains **step-by-step** how to set up environment, run tests (including expected results and troubleshooting), perform LangChain↔️Ollama integration testing, and run the system (API + UI).

---

---

## 🧭 Before You Start — Verify Correct Directory Location
All commands in this guide should be run from **project root directory**:
`HW1_ai_chat_bot/`

You should copy the commands and run them in **terminal** when you are in this directory.
You can verify this using command:
```bash
pwd   # macOS/Linux
# or
cd    # Windows
```
Output should end with:
.../HW1_ai_chat_bot

---

## ✅ Prerequisites

1. **Operating system**: macOS / Linux / Windows 10+
2. **Python**: Version 3.10 and above (recommended 3.10.x).
3. **Ollama**: Installed and accessible in PATH.
   - Download and installation: <https://ollama.com>
   - Running: `ollama serve`
   - Example model pull: `ollama pull phi` or `ollama pull mistral`
4. **Git** (recommended): For code and version management.
5. **Port** available for Ollama (default: `127.0.0.1:11434`).

> **Tip**: If you're on Apple Silicon, ensure xcode-tools/Command Line Tools are installed (`xcode-select --install`).

---

## 🧰 Installation Instructions

### 1) Create and activate virtual environment
```bash
# In same project directory (repo root)
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1
```

### 2) Install packages
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Configure .env file
Create `.env` (or copy from `.env.example`) and configure:
```
APP_API_KEY=my-local-token-123       # Required – your own access key (matching what's sent in request)
OLLAMA_HOST=http://127.0.0.1:11434   # Required – Ollama server address, usually not changed
OLLAMA_MODEL=phi                     # Required – model name installed in Ollama (phi/mistral)
API_URL=http://127.0.0.1:8000/api/chat   # Required for client – your FastAPI address (including /api/chat)

```
> **Important**: Don't leave `APP_API_KEY=change-me`. Set some real value.
---

## 🧪 Tests — Recommended Execution Order

Project includes two types of tests:
- **Unit** – Run without dependency on external server (Ollama mocked/faked).
- **Integration** – Run against real Ollama server (optional).

Additionally there is **Preflight** (threshold condition check) and optional **LangChain check**.

> **Configuration files**:
> - `pytest.ini` — Defines `@pytest.mark.integration` marker and test paths.
> - `tests/conftest.py` — Creates readable output: file name → test name → `PASSED/FAILED` → `EXPECTED` (+ `ACTUAL` in case of failure).

### 0) Preflight (required before everything)
```bash
python ./scripts/preflight.py
```
Success criteria:
- No `[FAIL]` lines in output.
- `APP_API_KEY` is not placeholder.
- `OLLAMA_HOST` looks like valid URL.
- (Optional) "Ollama reachable …" — healthy if server is running.
- **(For UI)** `API_URL` defined in `.env` file — otherwise `streamlit_app.py` stops with appropriate error message.


If failed: fix according to printed instructions (Hints) and run again.

### 1) Unit Tests — Without External Dependency
```bash
pytest -m "not integration" -q
```

> Output displays status for each file, for each test `PASSED/FAILED`, and below:
> `EXPECTED: …` (always) and `ACTUAL: …` (only on failure).
> At end of each file: `>>> FILE STATUS: ALL PASSED` if all tests passed.

**Unit Tests Details:**

Following table details all unit tests in project, by file, each test's purpose, expected result and what to check in case of failure.

| File                                  | What test checks | Expected results | If failed – what to check / what to fix |
|---------------------------------------|---|---|---|
| `tests/test_auth_api.py`              | `test_missing_token_returns_401` — `/api/chat` request without Authorization header | Status `401` and text containing "Missing bearer token" | Is header actually not sent? `require_api_key` implementation returns 401 and correct message string; `APP_API_KEY` shouldn't affect here |
|  `tests/test_auth_api.py`             | `test_invalid_token_returns_401` — header with wrong token | Status `401` and text containing "Invalid API key" | Check token differs from `.env`; comparison logic in `require_api_key`; don't "swallow" errors |
| `tests/test_auth_api.py`              | `test_auth_wrong_scheme_returns_401` — using wrong scheme (`Token` instead of `Bearer`) | Status `401` | Check in `require_api_key` that `Bearer` scheme is verified (case-sensitive/insensitive per policy) |
| `tests/test_auth_api.py`              | `test_auth_empty_bearer_returns_401` — correct scheme but empty value | Status `401` | Verify empty value not accepted; header parsing; appropriate message return |
| `tests/test_auth_api.py`              | `test_auth_lowercase_bearer_policy` — checking lowercase/uppercase policy | If defined as case-insensitive → `200`; otherwise `401` | Clarify policy in code/document; if want to pass this test as 200, compare scheme with case lowering |
| `tests/test_chat_validation_api.py`   | `test_chat_empty_messages_returns_422` — `messages` is `[]` | Status `400/422` | Schema constraints: `messages` not empty; Pydantic validations in `ChatRequest` |
| `tests/test_chat_validation_api.py`   | `test_chat_missing_messages_key_returns_422` — missing `messages` key | Status `400/422` | Required field in schema; field names match; correct use of `Field(...)` |
| `tests/test_chat_validation_api.py`   | `test_chat_message_missing_fields_returns_422` — item in `messages` without valid `content` | Status `400/422` | `ChatMessage.content` with `min_length=1`; check `""` not accepted |
| `tests/test_chat_validation_api.py`   | `test_chat_model_wrong_type_returns_422` — `model` not string type | Status `400/422` | Field types in schema; if field optional — check it's string when value provided |
| `tests/test_chat_validation_api.py`   | `test_chat_temperature_out_of_range_returns_422` — temperature outside range [0,1] | Status `400/422` | Add `temperature` field to schema with constraints; or update test if no support |
| `tests/test_chat_happy_errors_api.py` | `test_valid_token_with_mock` — Happy path: mocking `ollama_client.has_model=True` and `chat="MOCK-ANSWER"` | Status `200` and body `{"answer":"MOCK-ANSWER"}` | Ensure both `has_model` mocked to `True` (to not fall to `notice`), and `chat` mock returned; check endpoint returns answer |
| `tests/test_chat_happy_errors_api.py` | `test_chat_when_client_raises_returns_5xx` — mocking exception from `ollama_client.chat` | Status `500/502` and body with `detail`/`error` | Mock `has_model=True` also to reach branch calling `chat`; in endpoint catch exceptions and map to `HTTPException(5xx)` |
| `tests/test_chat_happy_errors_api.py` | `test_chat_endpoint_handles_missing_model` — model doesn't exist (`has_model=False`) | Status `200` with friendly `notice` field ("not installed…") and empty `answer` | That service/endpoint returns `notice` not error; message wording; don't try calling `chat` when no model |
| `tests/test_health_api.py`            | `test_health_endpoint` — basic `/api/health` | Status `200` and JSON with keys `status`, `ollama` (and possibly `default_model`) | Function returns consistent structure whether server available/not; no Ollama dependency for basic 200 status |
| `tests/test_health_api.py`            | `test_health_when_ping_fails_returns_structured_json` — `ping()` fails | Status `200` (or `503` per policy) with consistent JSON | Keep consistent body (fixed keys/message) even on failure; if chose 503 — update documentation/test |
| `tests/test_config_settings.py`       | `test_settings_defaults_when_env_missing` — defaults when no ENV | Valid types/defaults: API key string, host starts `http`, model string | `config.py` loads dotenv; default values match document; no crash when `.env` missing |
| `tests/test_config_settings.py`       | `test_settings_env_override` — values from ENV override default | Values changed to test values (e.g. `XYZ`, `http://x:1234`, `mistral`) | Use of `os.getenv`/dotenv loading at time; reload option in fixture if needed |
| `tests/test_ollama_client_unit.py`    | `test_ollama_client_end_to_end_unit` — mocked unit: `ping()` success/fail, `chat()` URL/payload, 5xx → raise | `ping` returns `True/False` per mock; `chat` returns `"OK"` from `{"message":{"content":"OK"}}`; 5xx → exception | Ensure `requests.get/post` mocked; URL built from `OLLAMA_HOST` ending `/api/chat`; payload includes `model/messages/stream/options.temperature` |
| `tests/test_ollama_client_unit.py`    | `test_has_model_handles_missing_models_key` — `/api/tags` missing `models` | Function returns `False` without exception | Robust handling when key missing; return `False` as default |
| `tests/test_ollama_client_unit.py`    | `test_chat_timeout_raises_runtimeerror` — timeout/connection fails | Raise `RuntimeError` (or agreed exception) | In `chat()` catch `requests.Timeout/ConnectionError` and raise uniform `RuntimeError`; update test if exception name differs |

**General Notes:**
- All tests are true **unit tests (Unit)** — no dependency on real Ollama server; tests use `monkeypatch` to mock calls.
- If get surprising result (e.g. 200 with `notice` instead of 5xx), ensure `has_model` also mocked to `True`.
- If one of validation tests fails (422/400), check Pydantic schema in `chat.py` file.

---
### 2) Integration Tests — Against Real Ollama Server (Optional)
Run in another terminal:
```bash
ollama serve
```
```bash
ollama pull <MODEL>   # if model not installed
```
Then:
```bash
pytest -m integration -q
```
**Integration Tests Details:**

Tests in this file are **real integration tests**, meaning they depend on active connection to local Ollama server.
They test server availability (`ping`) and existence of locally installed models per settings in `.env` file.

| File | What test checks | Expected results | If failed – what to check / what to fix |
|---|---|---|---|
| `tests/test_ollama_models_integration.py` | `test_ping_reachable` — tests local Ollama server availability using `ping()` | Function returns `True` if server active, `False` otherwise; if server not active — test marked as SKIPPED | Ensure `ollama serve` command running in background; if on new computer — ensure Ollama installed and port (`127.0.0.1:11434`) open |
| `tests/test_ollama_models_integration.py` | `test_has_model_checks_local` — tests if default model from `.env` installed on local server | `has_model(default)` returns `True` if model exists and `False` if not; test for imaginary model always returns `False` | Ensure `.env` file contains valid `OLLAMA_MODEL` (e.g. `phi` or `mistral`); run `ollama pull <model>` to ensure model installed; server activation (`ollama serve`) required before running |

---

**General Notes:**
- If Ollama not active, tests appear as `SKIPPED` not `FAILED`, to prevent false failure.
- Recommended to verify required models installed first with:
  ```bash
  ollama pull phi
  ollama pull mistral
  ```

### 3) LangChain ↔️ Ollama Integration Test
Helper file: `scripts/check_langchain.py`.
Execution:
```bash
python ./scripts/check_langchain.py
```
Expected result: Printing short response from model. If fails — clear message received (e.g. about connection/model).

---

# ▶️ System Execution and Running — HW1_ai_chat_bot

Following section guides **step-by-step** how to run API and UI, and how to verify everything works using endpoint checks.
Assuming you're already in project root directory (`HW1_ai_chat_bot`) and virtual environment active.

---

## 1) Running API Server (FastAPI)

```bash
uvicorn app.main:app --reload
```
- Terminal should show: `Uvicorn running on http://127.0.0.1:8000`
- Keep this window open during work.

### Endpoint Checks

#### A. System Health (matches `test_health_api.py` tests)
```bash
curl http://127.0.0.1:8000/api/health
```
**Expected:** JSON with keys: `status`, `ollama`, `default_model`
Example:
```json
{"status":"ok","ollama":true,"default_model":"phi"}
```

#### B. Basic Chat Call (matches `test_auth_api.py` + `test_chat_*` tests)
> Replace `YOUR_APP_API_KEY` in line below with value from `.env` file (the `APP_API_KEY` variable).

```bash
curl -X POST "http://127.0.0.1:8000/api/chat"   -H "Content-Type: application/json"   -H "Authorization: Bearer YOUR_APP_API_KEY"   -d '{"messages":[{"role":"user","content":"Hello"}], "stream":false}'
```
**Expected:**
- If model installed in Ollama → status `200` with `answer` key.
- If model not installed → `200` with `notice` key explaining how to install (matches `test_chat_endpoint_handles_missing_model` test).
- If header missing/invalid → `401` (matches `test_auth_api.py` tests).
- If request body invalid (e.g. `messages` empty) → `400/422` (matches `test_chat_validation_api.py`).

> **Tip:** If got `401` – verify `Authorization` header valid and `APP_API_KEY` exactly matches value in `.env`.

---

## 2) Running User Interface (Streamlit)

```bash
streamlit run ./ui/streamlit_app.py
```
- Default: Streamlit tries to open browser automatically.
- If it **doesn't open automatically**, enter manually to address:
  - `http://127.0.0.1:8501` or `http://localhost:8501`

### Important Configuration Before Running
In `.env` should have:
```dotenv
API_URL=http://127.0.0.1:8000/api/chat
```
This is API endpoint that UI calls. Also ensure API server (Uvicorn) running in parallel.

### How to Verify UI Communicates with API
- In message field in UI write: "Hello" and click Send/Submit.
- **Expected:** Response from model (if installed), or `notice` message if not installed.
- If get `401` error → update `APP_API_KEY` and check UI sends matching Bearer.
- If no communication → ensure `API_URL` points to `http://127.0.0.1:8000/api/chat` and API server running.

---
## Running Using Makefile
Makefile wraps startup stages in order: **preflight → install → ollama → api → ui**.

| Target | What it does | Usage notes |
|---|---|---|
| `make help` | Display available commands and explanation for each | Prints command list from Makefile |
| `make preflight` | Check Python/packages/Ollama/ENV | Runs `scripts/preflight.py` |
| `make install` | Install dependencies | Reads `requirements.txt` if exists |
| `make ollama` | Ensure Ollama server running | Runs `ollama serve` if needed, checks `/api/tags` |
| `make api` | Run FastAPI with Uvicorn | Parameters: `HOST`, `PORT` |
| `make ui` | Run Streamlit | Parameter: `STREAMLIT_PORT` |
| `make test` | Run all tests | Respects `pytest.ini` |
| `make test-unit` | Unit tests | Equivalent to `pytest -m "not integration"` |
| `make test-integration` | Run integration tests | Requires `@pytest.mark.integration` |
| `make all` | End-to-end execution | API in background, UI in foreground |
| `make clean` | Clean Python cache | Optional |

### Running Tests by Markers
In this project exists one marker:
```ini
[pytest]
markers = integration: tests that require a running local Ollama server
```

---

## ❓ Common Troubles and Quick Fix

| Symptom | Common Cause | Solution |
|---|---|---|
| 401 on `/api/chat` | `APP_API_KEY` placeholder / Authorization header missing/invalid | Update `.env` (real value in `APP_API_KEY`); send `Authorization: Bearer <APP_API_KEY>` |
| 422 / 400 on `/api/chat` | Invalid request schema | Ensure `messages` non-empty list; each message has non-empty `role` and `content` |
| 200 with `notice` instead of answer | Model not installed in Ollama | Run `ollama serve` then `ollama pull <model>` (e.g. `phi`/`mistral`) |
| Timeouts / Connection Errors | Ollama not running / wrong address | Run `ollama serve`; check `OLLAMA_HOST` in `.env`; run `python scripts/preflight.py` |
| Port already in use | Another server running on same port | Stop previous processes or run with different port: `uvicorn app.main:app --reload --port 8001` |
| UI doesn't open automatically | Browser doesn't open automatically / firewall | Open manually: `http://127.0.0.1:8501`; check firewall not blocking |
| PytestUnknownMarkWarning | `pytest` doesn't recognize `integration` | Ensure in `pytest.ini` defined: `markers =\n    integration: tests that require a running local Ollama server` |

---

## 📝 Notes on Test Files (Link to Operation Logic)

- **System health** – matches `tests/test_health_api.py` (checks consistent JSON even if `ping()` fails).
- **Access authentication (401/200)** – matches `tests/test_auth_api.py` (Bearer Token valid/wrong/missing/wrong scheme).
- **Request body validation** – matches `tests/test_chat_validation_api.py` (empty/missing fields/invalid types).
- **Happy path + exceptions** – matches `tests/test_chat_happy_errors_api.py` (mocking for response, 5xx on exceptions, notice).
- **Ollama layer (mocked unit)** – `tests/test_ollama_client_unit.py` (URL/payload/timeout/errors) – **does not** require real server.
- **Integration tests against Ollama** – `tests/test_ollama_models_integration.py` (requires `ollama serve`; SKIPPED when not running).
