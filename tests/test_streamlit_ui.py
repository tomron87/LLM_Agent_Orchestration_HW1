import json
from pathlib import Path

import requests

from streamlit.testing.v1 import AppTest

APP_FILE = Path(__file__).resolve().parents[1] / "ui" / "streamlit_app.py"
DEFAULT_HEALTH = {"status": "ok", "ollama": True, "default_model": "phi"}


class DummyResponse:
    def __init__(self, payload=None, status=200):
        self._payload = payload or {}
        self.status_code = status
        self.text = json.dumps(self._payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


def _app_test(
    monkeypatch,
    *,
    health_payload=None,
    health_exception=None,
    post_payload=None,
    post_status=200,
    post_exception=None,
):
    monkeypatch.setenv("API_URL", "http://example.com/api/chat")
    monkeypatch.setenv("APP_API_KEY", "test-key")
    monkeypatch.setenv("OLLAMA_MODEL", "phi")

    def fake_get(url, timeout=5):
        if health_exception:
            raise health_exception
        payload = health_payload if health_payload is not None else DEFAULT_HEALTH
        return DummyResponse(payload)

    captured = {}

    def fake_post(url, json=None, headers=None, timeout=None):
        captured["payload"] = json
        if post_exception:
            raise post_exception
        payload = post_payload or {"answer": "test-answer", "notice": None}
        return DummyResponse(payload, status=post_status)

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(requests, "post", fake_post)

    app = AppTest.from_file(str(APP_FILE))
    app.captured_post = captured
    return app


def _submit_message(app, text="בדיקת הודעה"):
    app.text_area[0].input(text).run()
    app.button(key="FormSubmitter:chat_form-שלח").click().run()


def test_streamlit_app_renders_without_errors(monkeypatch):
    app = _app_test(monkeypatch).run()
    assert app.title[0].value == "Local Ollama Chat"
    assert not app.exception  # no runtime exceptions captured
    assert not app.error  # no st.error components rendered


def test_streamlit_chat_submission_updates_history(monkeypatch):
    expected_answer = "שלום מהמודל"
    app = _app_test(monkeypatch, post_payload={"answer": expected_answer, "notice": None}).run()

    user_message = "בדיקת הודעה"
    _submit_message(app, user_message)

    history = app.session_state["history"]
    assert history[0]["text"] == user_message
    assert history[-1]["text"] == expected_answer
    assert history[-1]["role"] == "bot"


def test_streamlit_api_check_button_success(monkeypatch):
    app = _app_test(monkeypatch).run()
    app.button(key="api_check_btn").click().run()
    assert any("API OK" in toast.value for toast in app.toast)


def test_streamlit_api_check_button_failure(monkeypatch):
    app = _app_test(monkeypatch, health_exception=RuntimeError("boom")).run()
    app.button(key="api_check_btn").click().run()
    assert any("API health failed" in toast.value for toast in app.toast)


def test_streamlit_chat_warns_when_api_down(monkeypatch):
    app = _app_test(monkeypatch, health_exception=RuntimeError("offline")).run()
    _submit_message(app)
    assert any("API לא זמין" in warn.value for warn in app.warning)


def test_streamlit_chat_warns_when_ollama_down(monkeypatch):
    app = _app_test(monkeypatch, health_payload={"status": "ok", "ollama": False}).run()
    _submit_message(app)
    assert any("שרת Ollama" in warn.value for warn in app.warning)


def test_streamlit_chat_warns_on_http_error(monkeypatch):
    app = _app_test(monkeypatch, post_status=503, post_payload={"detail": "failed"}).run()
    _submit_message(app)
    assert any("failed" in warn.value for warn in app.warning)


def test_streamlit_chat_warns_on_notice(monkeypatch):
    notice = "מודל לא מותקן"
    app = _app_test(monkeypatch, post_payload={"answer": "", "notice": notice}).run()
    _submit_message(app)
    assert any(notice in warn.value for warn in app.warning)


def test_streamlit_chat_warns_on_empty_answer(monkeypatch):
    app = _app_test(monkeypatch, post_payload={"answer": "", "notice": None}).run()
    _submit_message(app)
    assert any("לא החזיר תשובה" in warn.value for warn in app.warning)


def test_streamlit_chat_handles_timeout(monkeypatch):
    app = _app_test(monkeypatch, post_exception=requests.exceptions.ReadTimeout()).run()
    _submit_message(app)
    assert any("timeout" in err.value for err in app.error)


def test_temperature_slider_updates_payload(monkeypatch):
    app = _app_test(monkeypatch).run()
    # emulate user moving the slider by tweaking session_state before submit
    app.session_state["temperature"] = 0.65
    app.session_state["temperature_slider"] = 0.65
    _submit_message(app)
    sent_temp = app.captured_post.get("payload", {}).get("temperature")
    assert sent_temp == 0.65
