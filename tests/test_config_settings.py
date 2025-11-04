import importlib
from app.core import config as config_module

def test_settings_defaults_when_env_missing(monkeypatch, exp):
    for k in ("APP_API_KEY","OLLAMA_HOST","OLLAMA_MODEL"):
        monkeypatch.delenv(k, raising=False)
    importlib.reload(config_module)
    s = config_module.settings
    exp.expect("defaults loaded (api_key str, host startswith http, model str)")
    exp.actual(f"api_key={type(s.app_api_key).__name__} host={s.ollama_host} model={type(s.ollama_model).__name__}")
    assert isinstance(s.app_api_key, str)
    assert s.ollama_host.startswith("http")
    assert isinstance(s.ollama_model, str)

def test_settings_env_override(monkeypatch, exp):
    monkeypatch.setenv("APP_API_KEY","XYZ")
    monkeypatch.setenv("OLLAMA_HOST","http://x:1234")
    monkeypatch.setenv("OLLAMA_MODEL","mistral")
    importlib.reload(config_module)
    s = config_module.settings
    exp.expect("env overrides are applied (XYZ, http://x:1234, mistral)")
    exp.actual(f"api_key={s.app_api_key} host={s.ollama_host} model={s.ollama_model}")
    assert s.app_api_key == "XYZ"
    assert s.ollama_host == "http://x:1234"
    assert s.ollama_model == "mistral"