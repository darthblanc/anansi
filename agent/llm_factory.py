import json
import os
from pathlib import Path
from langchain_core.language_models.chat_models import BaseChatModel

_CONFIG_PATH = Path(__file__).parent.parent / "agent_config.json"

_DEFAULT_KEY_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
}


def _load_config() -> dict:
    with open(_CONFIG_PATH) as f:
        return json.load(f)


def _resolve_api_key(cfg: dict) -> str | None:
    provider = cfg["provider"]
    if provider == "ollama":
        return None
    env_var = cfg.get("api_key_env", _DEFAULT_KEY_ENV.get(provider))
    if not env_var:
        return None
    key = os.environ.get(env_var)
    if not key:
        raise EnvironmentError(
            f"API key env var '{env_var}' is not set. Add it to your .env file."
        )
    return key


def create_llm(with_thinking: bool = False) -> BaseChatModel:
    cfg = _load_config()
    provider = cfg["provider"]
    profile = cfg["thinking"] if with_thinking else cfg["standard"]
    model = profile["model"]
    params = profile.get("params", {})
    thinking_enabled = profile.get("thinking", False)
    api_key = _resolve_api_key(cfg)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        kwargs = {"model": model, "api_key": api_key, **params}
        if thinking_enabled:
            kwargs["thinking"] = {"type": "adaptive"}
        return ChatAnthropic(**kwargs)

    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=model, **params)

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model, api_key=api_key, **params)

    else:
        raise ValueError(
            f"Unknown provider {provider!r}. Supported: 'anthropic', 'ollama', 'openai'"
        )
