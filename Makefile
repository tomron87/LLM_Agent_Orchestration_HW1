.PHONY: help preflight install ollama api ui test test-unit test-integration all clean

# ============================================================
# Makefile for HW1
# Flow according to documentation/Installation_and_Testing.md
# Execution order: preflight -> install -> ollama -> api -> ui
# ============================================================

HOST ?= 127.0.0.1
PORT ?= 8000
STREAMLIT_PORT ?= 8501
PY ?= python

# === עזרה כללית ===
help:
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets (בהתאם ל-Installation_and_Testing.md):"
	@echo "  preflight         1) בדיקת תקינות סביבה (Python, חבילות, Ollama, משתני סביבה)"
	@echo "  install           2) התקנת תלויות מ-requirements.txt (אם קיים)"
	@echo "  ollama            3) הבטחת הרצת שרת Ollama (יפעיל אם לא רץ)"
	@echo "  api               4) הרצת שרת FastAPI עם Uvicorn (HOST=$(HOST), PORT=$(PORT))"
	@echo "  ui                5) הרצת ממשק Streamlit (PORT=$(STREAMLIT_PORT))"
	@echo "  test              בדיקות (pytest)"
	@echo "  test-unit         בדיקות“בדיקות יחידה (not integration)”"
	@echo "  test-integration  בדיקות אינטגרציה בלבד"
	@echo "  coverage          pytest --cov=app --cov=ui --cov-report=term-missing --cov-report=html"
	@echo "  all               הפעלה מלאה: preflight -> install -> ollama -> api(bg) -> ui(fg)"
	@echo "  clean             ניקוי קבצי cache של Python"
	@echo ""
	@echo "Examples:"
	@echo "  make preflight"
	@echo "  make install"
	@echo "  make ollama"
	@echo "  make api HOST=0.0.0.0 PORT=8000"
	@echo "  make ui STREAMLIT_PORT=8501"
	@echo "  make all"
	@echo ""

# === 1) PRE-FLIGHT: אימות סביבה ===
preflight:
	$(PY) scripts/preflight.py

# === 2) התקנת תלויות ===
install:
	@if [ -f requirements.txt ]; then \
		echo 'Installing from requirements.txt...'; \
		$(PY) -m pip install -r requirements.txt; \
	else \
		echo 'requirements.txt not found. Skipping install.'; \
	fi

# === 3) הבטחת הרצת שרת Ollama (יפעיל רק אם לא רץ) ===
ollama:
	@echo "Ensuring Ollama server is running on http://127.0.0.1:11434 ..."
	@curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && \
	  echo "Ollama already running." || \
	  ( echo "Starting Ollama server..."; \
	    (ollama serve &) && sleep 3; \
	    curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && \
	      echo "Ollama server started." || \
	      (echo "ERROR: Failed to reach Ollama after start attempt." && exit 1) )

# === 4) הרצת API ===
api:
	uvicorn app.main:app --host $(HOST) --port $(PORT) --reload

# === 5) הרצת UI ===
ui:
	streamlit run ui/streamlit_app.py --server.port $(STREAMLIT_PORT)

# === בדיקות ===
test:
	pytest -q

test-unit:
	pytest -m "not integration" -q

test-integration:
	pytest -q -k "integration"

coverage:
	pytest --cov=app --cov=ui --cov-report=term-missing --cov-report=html

# === הפעלה מקצה לקצה: Preflight -> Install -> Ollama -> API(bg) -> UI(fg) ===
all: preflight install ollama
	@echo "Starting API in background on $(HOST):$(PORT) ..."
	@uvicorn app.main:app --host $(HOST) --port $(PORT) --reload &
	@echo "Starting UI in foreground on port $(STREAMLIT_PORT) ..."
	streamlit run ui/streamlit_app.py --server.port $(STREAMLIT_PORT)

# === ניקוי קבצי ביניים ===
clean:
	@echo "Cleaning Python cache and build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
