import pytest
import app.services.ollama_client as oc
from app.core.config import settings

class DummyResp:
    def __init__(self, status=200, data=None):
        self.status_code = status
        self._data = data or {}
        self.ok = (status == 200)
    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")
    def json(self):
        return self._data

def test_ollama_client_end_to_end_unit(monkeypatch, exp):
    def fake_get_ok(url, timeout=5):
        assert url == f"{settings.ollama_host}/api/tags"
        return DummyResp(200, {"models": []})
    monkeypatch.setattr(oc.requests, "get", fake_get_ok)
    assert oc.ping() is True

    def fake_get_fail(url, timeout=5):
        raise OSError("connection refused")
    monkeypatch.setattr(oc.requests, "get", fake_get_fail)
    assert oc.ping() is False

    captured = {}
    def fake_post_ok(url, json=None, timeout=60):
        captured["url"] = url
        captured["json"] = json
        return DummyResp(200, {"message": {"role": "assistant", "content": "OK"}})
    monkeypatch.setattr(oc.requests, "post", fake_post_ok)

    answer = oc.chat(
        messages=[{"role": "user", "content": "hi"}],
        model="mistral",
        temperature=0.1,
        stream=False,
    )
    assert answer == "OK"
    assert captured["url"].startswith(settings.ollama_host)
    assert captured["url"].endswith("/api/chat")
    payload = captured["json"]
    assert payload["model"] == "mistral"
    assert payload["messages"] == [{"role": "user", "content": "hi"}]
    assert payload["stream"] is False
    assert "options" in payload and payload["options"].get("temperature") == 0.1
    exp.expect("ping True/False toggles; chat returns 'OK' with correct URL/payload")
    exp.actual(f"url={captured['url']} payload_ok={payload['model']=='mistral'}")

    def fake_post_500(url, json=None, timeout=60):
        return DummyResp(500, {"error": "boom"})
    monkeypatch.setattr(oc.requests, "post", fake_post_500)

    raised = False
    try:
        oc.chat([{"role": "user", "content": "x"}])
    except RuntimeError:
        raised = True
    assert raised, "chat() must raise when HTTP status >= 400"
    # עדכון ה-ACTUAL של אותו טסט (אפשר לשנות/להחליף את השורה הקודמת)
    exp.actual("HTTP >= 400 raised RuntimeError as expected")

def test_has_model_handles_missing_models_key(monkeypatch, exp):
    def fake_get(url, timeout=5):
        return DummyResp(200, {})  # ללא "models"
    monkeypatch.setattr(oc.requests, "get", fake_get)
    exp.expect("has_model returns False when /api/tags lacks 'models' key")
    result = oc.has_model("phi")
    exp.actual(f"result={result}")
    assert result is False

def test_chat_timeout_raises_runtimeerror(monkeypatch, exp):
    def fake_post(*a, **k):
        raise OSError("timeout")
    monkeypatch.setattr(oc.requests, "post", fake_post)
    exp.expect("chat() raises RuntimeError on timeout/connection error")
    with pytest.raises(RuntimeError):
        oc.chat([{"role": "user", "content": "x"}])
    exp.actual("raised RuntimeError as expected")