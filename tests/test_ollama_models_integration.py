import pytest
from app.services import ollama_client
from app.core.config import settings

@pytest.mark.integration
def test_ping_reachable(exp):
    ok = ollama_client.ping()
    exp.expect("ping returns bool; test skipped if False (server not running)")
    exp.actual(f"ok={ok}")
    assert isinstance(ok, bool)
    if not ok:
        pytest.skip("⚠️ Ollama server לא זמין (ollama serve לא רץ במחשב הזה)")

@pytest.mark.integration
def test_has_model_checks_local(exp):
    if not ollama_client.ping():
        pytest.skip("Ollama server לא רץ — מדלגים על הבדיקה")

    default_model = settings.ollama_model
    exists = ollama_client.has_model(default_model)
    fake_model = "model_that_does_not_exist_xyz"
    fake_exists = ollama_client.has_model(fake_model)

    exp.expect(f"has_model(default='{default_model}') returns bool; fake model returns False")
    exp.actual(f"default_exists={exists} fake_exists={fake_exists}")

    assert isinstance(exists, bool)
    assert fake_exists is False