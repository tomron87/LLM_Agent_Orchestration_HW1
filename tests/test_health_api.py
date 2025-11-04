from fastapi.testclient import TestClient
from app.main import app
import app.services.ollama_client as oc

client = TestClient(app)

def test_health_endpoint(exp):
    r = client.get("/api/health")
    exp.expect("200 with keys ['status','ollama']")
    exp.actual(f"status={r.status_code} json={r.json()}")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert "ollama" in data

def test_health_when_ping_fails_returns_structured_json(monkeypatch, exp):
    monkeypatch.setattr(oc, "ping", lambda: False)
    r = client.get("/api/health")
    exp.expect("200/503 with structured JSON even if ping() fails")
    exp.actual(f"status={r.status_code} json={r.json()}")
    assert r.status_code in (200, 503)
    data = r.json()
    assert "status" in data and "ollama" in data