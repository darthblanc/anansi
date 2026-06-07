from unittest.mock import MagicMock

import pytest

from agent import llm_factory


def test_extract_text_passes_through_plain_string():
    assert llm_factory.extract_text("hello world") == "hello world"


def test_extract_text_strips_json_fences_from_content_blocks():
    content = [
        {"type": "thinking", "text": "pondering..."},
        {"type": "text", "text": "```json\n{\"a\": 1}\n```"},
    ]
    assert llm_factory.extract_text(content) == '{"a": 1}'


def test_extract_text_strips_plain_fences_without_json_tag():
    content = [{"type": "text", "text": "```\nplain text\n```"}]
    assert llm_factory.extract_text(content) == "plain text"


def test_resolve_api_key_returns_none_for_ollama():
    assert llm_factory._resolve_api_key({"provider": "ollama"}) is None


def test_resolve_api_key_returns_none_when_no_env_var_configured():
    assert llm_factory._resolve_api_key({"provider": "anthropic", "api_key_env": ""}) is None


def test_resolve_api_key_raises_when_env_var_not_set(monkeypatch):
    monkeypatch.delenv("MISSING_KEY_VAR", raising=False)
    with pytest.raises(EnvironmentError):
        llm_factory._resolve_api_key({"provider": "anthropic", "api_key_env": "MISSING_KEY_VAR"})


def test_resolve_api_key_returns_key_from_env(monkeypatch):
    monkeypatch.setenv("SOME_KEY_VAR", "secret-value")
    assert llm_factory._resolve_api_key({"provider": "anthropic", "api_key_env": "SOME_KEY_VAR"}) == "secret-value"


def test_resolve_api_key_uses_default_env_var_for_known_provider(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "default-anthropic-key")
    assert llm_factory._resolve_api_key({"provider": "anthropic"}) == "default-anthropic-key"


def _base_cfg(provider, **profile_overrides):
    profile = {"model": "some-model", "params": {}}
    profile.update(profile_overrides)
    return {
        "provider": provider,
        "api_key_env": "ANTHROPIC_API_KEY",
        "standard": profile,
        "thinking": {**profile, "thinking": True},
    }


def test_create_llm_builds_anthropic_chat_model(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    fake_chat_anthropic = MagicMock(return_value="anthropic-llm")
    monkeypatch.setattr(llm_factory, "_load_config", lambda: _base_cfg("anthropic"))
    monkeypatch.setitem(__import__("sys").modules, "langchain_anthropic", MagicMock(ChatAnthropic=fake_chat_anthropic))

    result = llm_factory.create_llm()

    assert result == "anthropic-llm"
    fake_chat_anthropic.assert_called_once_with(model="some-model", api_key="test-key")


def test_create_llm_enables_thinking_when_requested(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    fake_chat_anthropic = MagicMock(return_value="anthropic-llm")
    monkeypatch.setattr(llm_factory, "_load_config", lambda: _base_cfg("anthropic"))
    monkeypatch.setitem(__import__("sys").modules, "langchain_anthropic", MagicMock(ChatAnthropic=fake_chat_anthropic))

    llm_factory.create_llm(with_thinking=True)

    _, kwargs = fake_chat_anthropic.call_args
    assert kwargs["thinking"] == {"type": "adaptive"}


def test_create_llm_builds_ollama_chat_model_without_api_key(monkeypatch):
    fake_chat_ollama = MagicMock(return_value="ollama-llm")
    monkeypatch.setattr(llm_factory, "_load_config", lambda: _base_cfg("ollama"))
    monkeypatch.setitem(__import__("sys").modules, "langchain_ollama", MagicMock(ChatOllama=fake_chat_ollama))

    result = llm_factory.create_llm()

    assert result == "ollama-llm"
    fake_chat_ollama.assert_called_once_with(model="some-model")


def test_create_llm_builds_openai_chat_model(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    cfg = _base_cfg("openai")
    cfg["api_key_env"] = "OPENAI_API_KEY"
    fake_chat_openai = MagicMock(return_value="openai-llm")
    monkeypatch.setattr(llm_factory, "_load_config", lambda: cfg)
    monkeypatch.setitem(__import__("sys").modules, "langchain_openai", MagicMock(ChatOpenAI=fake_chat_openai))

    result = llm_factory.create_llm()

    assert result == "openai-llm"
    fake_chat_openai.assert_called_once_with(model="some-model", api_key="test-key")


def test_create_llm_raises_for_unknown_provider(monkeypatch):
    monkeypatch.setattr(llm_factory, "_load_config", lambda: _base_cfg("mystery-provider"))

    with pytest.raises(ValueError):
        llm_factory.create_llm()
