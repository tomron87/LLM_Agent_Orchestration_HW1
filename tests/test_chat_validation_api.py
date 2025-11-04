from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)
AUTH = {"Authorization": f"Bearer {settings.app_api_key}"}
SAMPLE_MSG = [{"role": "user", "content": "hi"}]

def test_chat_empty_messages_returns_422(exp):
    r = client.post("/api/chat", headers=AUTH, json={"messages": []})
    exp.expect("400/422 on messages=[] (min_length=1)")
    exp.actual(f"status={r.status_code} body={r.text[:140]}")
    assert r.status_code in (400, 422)

def test_chat_missing_messages_key_returns_422(exp):
    r = client.post("/api/chat", headers=AUTH, json={"model": settings.ollama_model})
    exp.expect("400/422 when 'messages' key is missing")
    exp.actual(f"status={r.status_code} body={r.text[:140]}")
    assert r.status_code in (400, 422)

def test_chat_message_missing_fields_returns_422(exp):
    r = client.post("/api/chat", headers=AUTH,
                    json={"messages":[{"role":"user"}]})
    exp.expect("400/422 when message.content is missing/empty")
    exp.actual(f"status={r.status_code} body={r.text[:140]}")
    assert r.status_code in (400, 422)

def test_chat_model_wrong_type_returns_422(exp):
    r = client.post("/api/chat", headers=AUTH,
                    json={"messages": SAMPLE_MSG, "model": 123})
    exp.expect("400/422 when model is not a string")
    exp.actual(f"status={r.status_code} body={r.text[:140]}")
    assert r.status_code in (400, 422)

def test_chat_temperature_out_of_range_returns_422(exp):
    r = client.post("/api/chat", headers=AUTH,
                    json={"messages": SAMPLE_MSG, "temperature": 9.99})
    exp.expect("400/422 when temperature is out of [0.0, 1.0]")
    exp.actual(f"status={r.status_code} body={r.text[:140]}")
    assert r.status_code in (400, 422)