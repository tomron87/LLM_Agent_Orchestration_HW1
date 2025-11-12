import os, sys, shutil, importlib
from dotenv import load_dotenv

fail = False

def ok(label, cond, extra=""):
    global fail
    print(f"[OK] {label}" + (f"  {extra}" if extra else "")) if cond else print(f"[FAIL] {label}" + (f"  {extra}" if extra else ""))
    if not cond:
        fail = True
    return bool(cond)

def require(label, cond, hint=""):
    # כמו ok, אבל מדגיש שזה תנאי חובה
    msg = f"{label}" + (f" | hint: {hint}" if (not cond and hint) else "")
    return ok(msg, cond)

def load_env():
    # מנסה לטעון .env אם קיים; לא נכשל אם אין
    loaded = load_dotenv()
    if loaded:
        print("[OK] .env loaded")
    else:
        print("[INFO] .env not found (reading environment only)")

def valid_http_url(u: str) -> bool:
    return isinstance(u, str) and u.startswith(("http://", "https://")) and "://" in u

def main():
    # 0) .env
    load_env()

    # 1) Python
    require("Python >= 3.10", sys.version_info >= (3, 10), hint="Use Python 3.10+ environment")

    # 2) tools on PATH (אופציונלי)
    ok("ollama on PATH", shutil.which("ollama") is not None, shutil.which("ollama") or "")
    # curl כבר לא חובה — עברנו ל-requests בפייתון

    # 3) packages (בדיקה קלה באמצעות import)
    def can_import(mod):
        try:
            importlib.import_module(mod)
            return True
        except Exception:
            return False

    # מיפוי שם-מודול → שם-חבילה להתקנה (כשצריך להדפיס hint)
    pkg_hint = {
        "dotenv": "python-dotenv",
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "requests": "requests",
        "pydantic": "pydantic",
        "pytest": "pytest",
        "streamlit": "streamlit",
    }

    for mod in ("fastapi", "uvicorn", "requests", "dotenv", "pydantic", "pytest", "streamlit"):
        require(
            f"python package import: {mod}",
            can_import(mod),
            hint=f"pip install {pkg_hint[mod]}"
        )
    # 4) env keys exist (ושפויים)
    app_api_key = os.getenv("APP_API_KEY")
    ollama_host = os.getenv("OLLAMA_HOST")
    ollama_model = os.getenv("OLLAMA_MODEL")
    api_url = os.getenv("API_URL")

    require("env var present: APP_API_KEY", bool(app_api_key), hint="Set APP_API_KEY in .env")
    # אל תאפשר ערך דמי
    ok("APP_API_KEY not default placeholder", app_api_key not in (None, "", "change-me"))
    require(
        "APP_API_KEY length >= 32 characters",
        len(app_api_key or "") >= 32,
        hint='Generate one via: python -c "import secrets; print(secrets.token_hex(32))"'
    )
    require(
        "APP_API_KEY has sufficient entropy (>=10 unique characters)",
        len(set(app_api_key or "")) >= 10,
        hint="Use a freshly generated token; avoid repeating the same few characters"
    )

    require("env var present: OLLAMA_HOST", bool(ollama_host), hint="Set OLLAMA_HOST in .env (e.g., http://127.0.0.1:11434)")
    ok("OLLAMA_HOST looks like URL", valid_http_url(ollama_host or ""))

    require("env var present: OLLAMA_MODEL", bool(ollama_model), hint="Set OLLAMA_MODEL in .env (e.g., phi or mistral)")

    require("env var present: API_URL", bool(api_url), hint="Set API_URL in .env (e.g., http://127.0.0.1:8000/api/chat)")
    ok("API_URL looks like URL", valid_http_url(api_url or ""))

    # 5) Ollama reachable (אופציונלי; לא נכשל אם לא)
    # עדיף להשתמש ב-requests כדי להיות חוצה פלטפורמות
    reachable = False
    if valid_http_url(ollama_host or ""):
        try:
            import requests
            r = requests.get(f"{ollama_host}/api/tags", timeout=3)
            reachable = r.ok and r.text.strip().startswith("{")
            ok(f"Ollama reachable at {ollama_host}", reachable, (r.text or "")[:60].replace("\n"," "))
        except Exception as e:
            ok(f"Ollama reachable at {ollama_host}", False, str(e))
    else:
        ok("Ollama reachable", False, "Invalid OLLAMA_HOST URL")

    print("\nPreflight done.")
    sys.exit(1 if fail else 0)

if __name__ == "__main__":
    main()
