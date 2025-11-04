"""
PyTest setup:
- Integration tests must be marked with @pytest.mark.integration
- Unit tests are unmarked by design; run them with: pytest -m "not integration"
- Make targets:
    make test            # all tests
    make test-unit       # -m "not integration"
    make test-integration# -m integration
"""


import os
import sys
import importlib
import pytest
from fastapi.testclient import TestClient

# נטען כאן את האפליקציה והקונפיג פעם אחת
from app.main import app
from app.core import config as config_module


# ---------- Fixtures כלליים ----------

@pytest.fixture(scope="session")
def settings():
    """
    מחזיר את אובייקט ה-Settings (כמו app.core.config.settings).
    אם תרצה לשנות משתני סביבה לטסט מסוים, אפשר להשתמש ב-monkeypatch
    ואז לעשות reload למודול config (ראה settings_reload בהמשך).
    """
    return config_module.settings


@pytest.fixture(scope="function")
def settings_reload(monkeypatch):
    """
    מאפשר לבצע reload ל-settings אחרי שינוי משתני סביבה.
    שימוש:
        monkeypatch.setenv("APP_API_KEY", "XYZ")
        s = settings_reload()
        assert s.app_api_key == "XYZ"
    """
    def _reload():
        importlib.reload(config_module)
        return config_module.settings
    return _reload


@pytest.fixture(scope="function")
def client():
    """
    TestClient של FastAPI – מוכן לשימוש בכל טסט API.
    """
    return TestClient(app)


@pytest.fixture(scope="session")
def auth_header(settings):
    """
    Authorization תקין כפי שמוגדר ב-.env/Settings.
    שימוש:
        def test_x(client, auth_header):
            r = client.post("/api/chat", headers=auth_header, json=...)
    """
    return {"Authorization": f"Bearer {settings.app_api_key}"}


@pytest.fixture(scope="session")
def sample_msg():
    """
    הודעת דוגמה סטנדרטית לשימוש נפוץ בבדיקות /api/chat.
    """
    return [{"role": "user", "content": "hi"}]


# ---------- כלי עזר לשכבת ה-HTTP (ollama_client) ----------

class _DummyResp:
    """
    אובייקט תגובה דמה בסגנון requests.Response שמספיק לבדיקות שלנו.
    """
    def __init__(self, status=200, data=None):
        self.status_code = status
        self._data = data or {}
        self.ok = (status == 200)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._data


@pytest.fixture(scope="session")
def DummyResp():
    """
    מחזיר את מחלקת DummyResp כדי שניתן יהיה להשתמש בה בקלות בכל טסט,
    ללא צורך להגדיר אותה שוב בכל קובץ.

    שימוש:
        def test_something(DummyResp, monkeypatch):
            def fake_post(*a, **k): return DummyResp(200, {"x":1})
            monkeypatch.setattr(oc.requests, "post", fake_post)
    """
    return _DummyResp

@pytest.fixture
def exp(request):
    """
    שימוש:
        exp.expect("401 with 'Missing bearer token'")
        exp.actual(f"status={r.status_code} body={r.text[:120]}")
    """
    class _Exp:
        def expect(self, msg: str):
            request.node._expected = msg
        def actual(self, msg: str):
            request.node._actual = msg
    return _Exp()

# ---------- hook: פורמט פלט: קובץ → טסטים → סטטוס + EXPECTED/ACTUAL + תקציר קובץ ----------

_last_file = None
_current_failed = False
_current_count = 0

def _normalize_path(item):
    # משתמשים ב-fspath וממירים ל-relpath יציב לתיקיית הריצה הנוכחית
    p = str(item.fspath)
    try:
        rel = os.path.relpath(p, start=os.getcwd())
    except Exception:
        rel = p
    return rel.replace("\\", "/")

def _flush_file_status():
    """מדפיס בסוף קובץ אם כל הטסטים בו עברו (ואז מציג 'ALL PASSED')."""
    global _last_file, _current_failed, _current_count
    if _last_file is not None and _current_count > 0 and not _current_failed:
        print("  >>> FILE STATUS: ALL PASSED")
        sys.stdout.flush()

def pytest_runtest_makereport(item, call):
    global _last_file, _current_failed, _current_count
    if call.when != "call":
        return

    file_path = _normalize_path(item)
    test_name = item.name

    # אם עברנו לקובץ חדש – קודם מסכמים את הקודם, ואחר כך פותחים כותרת חדשה
    if file_path != _last_file:
        _flush_file_status()
        print(f"\n{file_path}")
        sys.stdout.flush()
        _last_file = file_path
        _current_failed = False
        _current_count = 0

    expected = getattr(item, "_expected", None)
    actual = getattr(item, "_actual", None)
    passed = (call.excinfo is None)

    _current_count += 1
    if not passed:
        _current_failed = True

    status_str = "PASSED" if passed else "FAILED"
    print(f"  {test_name} ... {status_str}")
    if expected:
        print(f"    EXPECTED: {expected}")
    if not passed and actual:
        print(f"    ACTUAL:   {actual}")
    sys.stdout.flush()

def pytest_sessionfinish(session, exitstatus):
    _flush_file_status()
    sys.stdout.flush()