from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_missing_token_returns_401(exp):
    r = client.post("/api/chat", json={"messages":[{"role":"user","content":"hi"}]})
    exp.expect("401 with message 'Missing bearer token'")
    exp.actual(f"status={r.status_code} body={r.text[:120]}")
    assert r.status_code == 401
    assert "Missing bearer token" in r.text

def test_invalid_token_returns_401(exp):
    r = client.post("/api/chat",
        headers={"Authorization":"Bearer WRONG"},
        json={"messages":[{"role":"user","content":"hi"}]}
    )
    exp.expect("401 with message 'Invalid API key'")
    exp.actual(f"status={r.status_code} body={r.text[:120]}")
    assert r.status_code == 401
    assert "Invalid API key" in r.text

def test_auth_wrong_scheme_returns_401(exp):
    r = client.post("/api/chat",
        headers={"Authorization": f"Token {settings.app_api_key}"},
        json={"messages":[{"role":"user","content":"hi"}]})
    exp.expect("401 due to wrong auth scheme (Token instead of Bearer)")
    exp.actual(f"status={r.status_code}")
    assert r.status_code == 401

def test_auth_empty_bearer_returns_401(exp):
    r = client.post("/api/chat",
        headers={"Authorization": "Bearer "},
        json={"messages":[{"role":"user","content":"hi"}]})
    exp.expect("401 due to empty Bearer token")
    exp.actual(f"status={r.status_code}")
    assert r.status_code == 401

def test_auth_lowercase_bearer_policy(exp):
    r = client.post("/api/chat",
        headers={"Authorization": f"bearer {settings.app_api_key}"},
        json={"messages":[{"role":"user","content":"hi"}]})
    exp.expect("200 if case-insensitive supported; else 401")
    exp.actual(f"status={r.status_code}")
    assert r.status_code in (200, 401)