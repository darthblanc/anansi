import json
import os
import re
from pathlib import Path
from langchain_core.language_models.chat_models import BaseChatModel

_CONFIG_PATH = Path(__file__).parent.parent / "agent_config.json"

_DEFAULT_KEY_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
}

# Cloud-only providers exposed to the deployed frontend/backend (the CLI's
# file-based config may still use "ollama"). Users supply their own key, so
# the deployed path picks one fixed preset model per provider rather than
# letting the model string be chosen.
CLOUD_LLM_PROVIDERS = ("anthropic", "openai")

LLM_PRESETS = {
    "anthropic": {
        "standard": {"model": "claude-sonnet-4-6", "params": {}},
        "thinking": {"model": "claude-sonnet-4-6", "thinking": True, "params": {}},
    },
    "openai": {
        "standard": {"model": "gpt-4.1", "params": {}},
        "thinking": {"model": "gpt-4.1", "params": {}},
    },
}


def extract_text(content) -> str:
    if isinstance(content, list):
        text = next(block["text"] for block in content if block.get("type") == "text")
        return re.sub(r"^```(?:json)?\s*|\s*```$", "", text).strip()
    return content


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


def create_llm(with_thinking: bool = False, override: dict | None = None) -> BaseChatModel:
    if override is not None:
        provider = override["provider"]
        if provider not in CLOUD_LLM_PROVIDERS:
            raise ValueError(
                f"Unsupported LLM provider {provider!r} for the deployed path. "
                f"Supported: {CLOUD_LLM_PROVIDERS}"
            )
        profile = LLM_PRESETS[provider]["thinking" if with_thinking else "standard"]
        model = profile["model"]
        params = profile.get("params", {})
        thinking_enabled = profile.get("thinking", False)
        api_key = override["api_key"]
    else:
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
