from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
import app.services.ollama_client as oc

client = TestClient(app)
AUTH = {"Authorization": f"Bearer {settings.app_api_key}"}
SAMPLE_MSG = [{"role": "user", "content": "hi"}]

def test_valid_token_with_mock(monkeypatch, exp):
    import app.services.ollama_client as oc
    monkeypatch.setattr(oc, "has_model", lambda name: True)
    monkeypatch.setattr(oc, "chat", lambda *a, **k: "MOCK-ANSWER")

    r = client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {settings.app_api_key}"},
        json={"messages": [{"role": "user", "content": "hi"}]}
    )

    exp.expect("200 with body {'answer': 'MOCK-ANSWER'}")
    exp.actual(f"status={r.status_code} json={r.json()}")
    assert r.status_code == 200
    assert r.json()["answer"] == "MOCK-ANSWER"

def test_chat_when_client_raises_returns_5xx(monkeypatch, exp):
    import app.services.ollama_client as oc
    monkeypatch.setattr(oc, "has_model", lambda name: True)

    def boom(*a, **k):
        raise RuntimeError("boom")
    monkeypatch.setattr(oc, "chat", boom)

    r = client.post("/api/chat", headers=AUTH, json={"messages": SAMPLE_MSG})

    exp.expect("500/502 with JSON error/detail when service raises")
    try:
        data = r.json()
    except Exception:
        data = r.text[:160]
    exp.actual(f"status={r.status_code} body={data}")

    assert r.status_code in (500, 502)
    assert isinstance(data, (dict, str))
    if isinstance(data, dict):
        assert any(k in data for k in ("error", "detail"))

def test_chat_endpoint_handles_missing_model(monkeypatch, exp):
    """בודקת שבמקרה שמודל לא קיים, מוחזרת הודעת notice מתאימה"""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.services import ollama_client

    client_local = TestClient(app)
    fake_model = "model_that_does_not_exist_xyz"
    monkeypatch.setattr(ollama_client, "has_model", lambda name: False)

    headers = {"Authorization": f"Bearer {settings.app_api_key}"}
    payload = {"messages": [{"role": "user", "content": "שלום!"}], "model": fake_model}

    r = client_local.post("/api/chat", headers=headers, json=payload)
    data = r.json()
    exp.expect("200 with 'notice' telling model is not installed")
    exp.actual(f"status={r.status_code} json={data}")
    assert r.status_code == 200
    assert "notice" in data
    assert "לא מותקן" in data["notice"]

def test_temperature_parameter_passes_through(monkeypatch, exp):
    """Ensures user-provided temperature reaches the Ollama client."""
    import app.services.ollama_client as oc

    monkeypatch.setattr(oc, "has_model", lambda name: True)
    captured = {}

    def fake_chat(messages, model=None, temperature=None, stream=False, timeout=60):
        captured["temperature"] = temperature
        return "TEMP-ANSWER"

    monkeypatch.setattr(oc, "chat", fake_chat)

    r = client.post(
        "/api/chat",
        headers=AUTH,
        json={"messages": SAMPLE_MSG, "temperature": 0.65}
    )
    exp.expect("temperature parameter propagates to client and response succeeds")
    exp.actual(f"status={r.status_code} temp={captured.get('temperature')}")
    assert r.status_code == 200
    assert captured["temperature"] == 0.65

def test_ollama_unavailable_returns_503(monkeypatch, exp):
    import app.services.ollama_client as oc

    def fake_has_model(name):
        raise oc.OllamaUnavailableError("connection refused")

    monkeypatch.setattr(oc, "has_model", fake_has_model)

    r = client.post("/api/chat", headers=AUTH, json={"messages": SAMPLE_MSG})
    exp.expect("503 when Ollama unreachable instead of model-not-found notice")
    exp.actual(f"status={r.status_code} body={r.json() if r.headers.get('content-type','').startswith('application/json') else r.text}")
    assert r.status_code == 503
    assert "Ollama" in r.json().get("detail", "")
