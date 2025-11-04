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