"""LLM provider settings (BYOK) — catalog aligned with Cursor models (minus Composer)."""

from __future__ import annotations

import contextlib
import json
import ssl
import urllib.error
import urllib.request
from typing import Any, Literal, cast

Provider = Literal["openrouter", "xai", "anthropic", "openai", "google", "local"]

PROVIDERS: list[Provider] = ["openrouter", "xai", "anthropic", "openai", "google", "local"]

PROVIDER_LABELS: dict[Provider, str] = {
    "openrouter": "OpenRouter",
    "xai": "xAI (Grok)",
    "anthropic": "Anthropic (Claude)",
    "openai": "OpenAI",
    "google": "Google (Gemini)",
    "local": "Local LLM (Ollama / LM Studio)",
}

# Cursor catalog: https://cursor.com/docs/models-and-pricing (Composer excluded)
MODEL_GROUPS: dict[Provider, list[dict[str, Any]]] = {
    "openai": [
        {
            "label": "Cursor — GPT-5.5",
            "models": ["gpt-5.5", "gpt-5.5-fast", "gpt-5.5-medium"],
        },
        {
            "label": "Cursor — GPT-5.4",
            "models": ["gpt-5.4", "gpt-5.4-mini", "gpt-5.4-nano", "gpt-5.4-low"],
        },
        {
            "label": "Cursor — GPT-5.3 Codex",
            "models": ["gpt-5.3-codex", "gpt-5.3-codex-high", "gpt-5.3-codex-low"],
        },
        {
            "label": "Cursor — GPT-5.2",
            "models": ["gpt-5.2", "gpt-5.2-high", "gpt-5.2-codex"],
        },
        {
            "label": "Cursor — GPT-5.1 Codex",
            "models": ["gpt-5.1-codex", "gpt-5.1-codex-max", "gpt-5.1-codex-mini"],
        },
        {
            "label": "Cursor — GPT-5",
            "models": [
                "gpt-5",
                "gpt-5-fast",
                "gpt-5-high",
                "gpt-5-high-fast",
                "gpt-5-low-fast",
                "gpt-5-mini",
                "gpt-5-codex",
            ],
        },
        {
            "label": "More OpenAI",
            "models": [
                "gpt-5-nano",
                "gpt-4.1",
                "gpt-4.1-mini",
                "gpt-4.1-nano",
                "gpt-4o",
                "gpt-4o-mini",
                "o3",
                "o3-mini",
                "o1",
                "o1-mini",
            ],
        },
    ],
    "anthropic": [
        {
            "label": "Cursor — Opus 4.8",
            "models": [
                "claude-opus-4-8",
                "claude-opus-4-8-fast",
                "claude-opus-4-8-thinking-low",
            ],
        },
        {
            "label": "Cursor — Opus 4.7",
            "models": ["claude-opus-4-7", "claude-opus-4-7-fast"],
        },
        {
            "label": "Cursor — Claude 4.6",
            "models": [
                "claude-opus-4-6",
                "claude-opus-4-6-fast",
                "claude-sonnet-4-6",
                "claude-4.6-sonnet-low-thinking",
            ],
        },
        {
            "label": "Cursor — Claude 4.5",
            "models": ["claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-4-5"],
        },
        {
            "label": "Cursor — Claude 4",
            "models": ["claude-sonnet-4", "claude-sonnet-4-1m"],
        },
        {
            "label": "More Anthropic",
            "models": [
                "claude-opus-4",
                "claude-sonnet-4-5-20250929",
                "claude-3-7-sonnet-latest",
                "claude-3-5-sonnet-latest",
                "claude-3-5-haiku-latest",
            ],
        },
    ],
    "google": [
        {
            "label": "Cursor — Gemini 3.5",
            "models": ["gemini-3.5-flash"],
        },
        {
            "label": "Cursor — Gemini 3.1",
            "models": ["gemini-3.1-pro"],
        },
        {
            "label": "Cursor — Gemini 3",
            "models": ["gemini-3-pro", "gemini-3-flash"],
        },
        {
            "label": "Cursor — Gemini 2.5",
            "models": ["gemini-2.5-flash"],
        },
        {
            "label": "More Google",
            "models": [
                "gemini-2.5-pro",
                "gemini-2.5-flash-lite",
                "gemini-2.0-pro",
                "gemini-2.0-flash",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
            ],
        },
    ],
    "xai": [
        {
            "label": "Cursor — Grok",
            "models": ["grok-4.3", "grok-4-20", "grok-build-0.1"],
        },
        {
            "label": "More xAI",
            "models": [
                "grok-4",
                "grok-4-fast",
                "grok-4-mini",
                "grok-3",
                "grok-3-fast",
                "grok-3-mini",
            ],
        },
    ],
    "openrouter": [
        {
            "label": "Cursor — OpenAI",
            "models": [
                "openai/gpt-5.5",
                "openai/gpt-5.4",
                "openai/gpt-5.3-codex",
                "openai/gpt-5.2",
                "openai/gpt-5.2-codex",
                "openai/gpt-5.1-codex",
                "openai/gpt-5",
                "openai/gpt-5-mini",
            ],
        },
        {
            "label": "Cursor — Anthropic",
            "models": [
                "anthropic/claude-opus-4.8",
                "anthropic/claude-opus-4.7",
                "anthropic/claude-opus-4.6",
                "anthropic/claude-sonnet-4.6",
                "anthropic/claude-opus-4.5",
                "anthropic/claude-sonnet-4.5",
                "anthropic/claude-haiku-4.5",
                "anthropic/claude-sonnet-4",
            ],
        },
        {
            "label": "Cursor — Google",
            "models": [
                "google/gemini-3.5-flash",
                "google/gemini-3.1-pro",
                "google/gemini-3-pro",
                "google/gemini-3-flash",
                "google/gemini-2.5-flash",
            ],
        },
        {
            "label": "Cursor — xAI",
            "models": ["x-ai/grok-4.3", "x-ai/grok-4.20"],
        },
        {
            "label": "Cursor — Moonshot",
            "models": ["moonshotai/kimi-k2.5"],
        },
        {
            "label": "More — Meta Llama",
            "models": [
                "meta-llama/llama-3.3-70b-instruct",
                "meta-llama/llama-3.1-405b-instruct",
                "meta-llama/llama-3.1-70b-instruct",
            ],
        },
        {
            "label": "More — DeepSeek / Qwen / Mistral",
            "models": [
                "deepseek/deepseek-r1",
                "deepseek/deepseek-v3",
                "qwen/qwen-2.5-72b-instruct",
                "qwen/qwq-32b",
                "mistralai/mistral-large",
            ],
        },
    ],
    "local": [
        {"label": "Llama", "models": ["llama3.3", "llama3.2", "llama3.1", "llama3.1:70b", "llama3.1:8b"]},
        {
            "label": "Qwen",
            "models": [
                "qwen2.5",
                "qwen2.5:32b",
                "qwen2.5:72b",
                "qwen2.5-coder",
                "qwen2.5-coder:32b",
                "qwq",
            ],
        },
        {
            "label": "DeepSeek",
            "models": ["deepseek-r1", "deepseek-r1:32b", "deepseek-r1:70b", "deepseek-coder-v2"],
        },
        {"label": "Mistral / Mixtral", "models": ["mistral", "mistral-nemo", "mixtral", "mixtral:8x22b"]},
        {"label": "Microsoft / Google", "models": ["phi3", "phi3:14b", "phi4", "gemma2", "gemma2:27b"]},
        {"label": "Code-focused", "models": ["codellama", "codellama:34b", "codestral", "starcoder2"]},
    ],
}

DEFAULT_LOCAL_BASE_URL = "http://localhost:11434/v1"
DEFAULT_PROVIDER: Provider = "openai"


def _resolve_provider(provider: str) -> Provider:
    if provider in PROVIDERS:
        return cast(Provider, provider)
    return DEFAULT_PROVIDER


def flatten_models(provider: str) -> list[str]:
    groups = MODEL_GROUPS[_resolve_provider(provider)]
    models: list[str] = []
    for group in groups:
        models.extend(group["models"])
    return models


def default_model(provider: str) -> str:
    models = flatten_models(provider)
    return models[0] if models else ""


def provider_choices() -> list[tuple[str, str]]:
    return [(PROVIDER_LABELS[p], p) for p in PROVIDERS]


def key_required(provider: str) -> bool:
    return provider != "local"


def _friendly_status(status: int) -> str:
    if status in {401, 403}:
        return "Invalid or unauthorized API key."
    if status == 404:
        return "Model not found for this provider."
    if status == 429:
        return "Rate limited — slow down or check your plan."
    if status >= 500:
        return "Provider is having issues right now."
    return f"Request failed (HTTP {status})."


def _endpoint(provider: str, base_url: str) -> str:
    if provider == "openrouter":
        return "https://openrouter.ai/api/v1/chat/completions"
    if provider == "xai":
        return "https://api.x.ai/v1/chat/completions"
    if provider == "openai":
        return "https://api.openai.com/v1/chat/completions"
    if provider == "anthropic":
        return "https://api.anthropic.com/v1/messages"
    if provider == "google":
        return "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    base = (base_url.strip() or DEFAULT_LOCAL_BASE_URL).rstrip("/")
    return f"{base}/chat/completions"


def _headers(provider: str, api_key: str) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if provider == "anthropic":
        headers["x-api-key"] = api_key
        headers["anthropic-version"] = "2023-06-01"
        return headers
    if provider == "local":
        if api_key.strip():
            headers["Authorization"] = f"Bearer {api_key.strip()}"
        return headers
    headers["Authorization"] = f"Bearer {api_key.strip()}"
    if provider == "openrouter":
        headers["HTTP-Referer"] = "https://biodex.local"
        headers["X-Title"] = "BioDex"
    return headers


def _token_limit_key(provider: str, model: str) -> str:
    """Newer OpenAI models reject max_tokens; they want max_completion_tokens."""
    slug = model.lower().split("/")[-1]
    if provider in ("openai", "openrouter") and slug.startswith(("gpt-5", "o1", "o3", "o4")):
        return "max_completion_tokens"
    return "max_tokens"


def _build_payload(provider: str, model: str, token_key: str) -> dict[str, Any]:
    if provider == "anthropic":
        return {
            "model": model,
            "max_tokens": 16,
            "system": "Reply with the single word: pong.",
            "messages": [{"role": "user", "content": "ping"}],
        }
    return {
        "model": model,
        token_key: 16,
        "messages": [
            {"role": "system", "content": "Reply with the single word: pong."},
            {"role": "user", "content": "ping"},
        ],
    }


def _post_json(
    provider: str,
    api_key: str,
    model: str,
    base_url: str,
    payload: dict[str, Any],
    *,
    timeout: int = 30,
) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        _endpoint(provider, base_url),
        data=data,
        headers=_headers(provider, api_key),
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as res:
        body = res.read().decode("utf-8", errors="replace")
        if res.status >= 400:
            raise urllib.error.HTTPError(req.full_url, res.status, _friendly_status(res.status), res.headers, None)
    if not body:
        return {}
    try:
        return cast(dict[str, Any], json.loads(body))
    except json.JSONDecodeError:
        return {}


def _request(provider: str, api_key: str, model: str, base_url: str) -> None:
    token_key = _token_limit_key(provider, model)
    payload = _build_payload(provider, model, token_key)
    try:
        _post_json(provider, api_key, model, base_url, payload)
    except urllib.error.HTTPError as exc:
        if exc.code != 400 or token_key == "max_completion_tokens":
            raise
        detail = ""
        with contextlib.suppress(OSError):
            detail = exc.read().decode("utf-8", errors="replace")
        if "max_completion_tokens" not in detail:
            raise
        _post_json(provider, api_key, model, base_url, _build_payload(provider, model, "max_completion_tokens"))


def test_connection(provider: str, api_key: str, model: str, base_url: str) -> str:
    provider = provider or DEFAULT_PROVIDER
    model = model.strip()
    if key_required(provider) and not api_key.strip():
        return "Enter an API key."
    if not model:
        return "Enter a model name."
    try:
        _request(provider, api_key, model, base_url)
        return "Connected."
    except urllib.error.HTTPError as exc:
        detail = ""
        with contextlib.suppress(OSError):
            detail = exc.read().decode("utf-8", errors="replace")[:200]
        msg = _friendly_status(exc.code)
        return f"{msg} {detail}".strip()
    except urllib.error.URLError as exc:
        return f"Connection failed: {exc.reason}"
    except Exception as exc:
        return str(exc)


# --- Chat / vision generation -------------------------------------------------

# Providers (and OpenAI-compatible gateways) that accept image inputs.
_VISION_PROVIDERS = {"openai", "anthropic", "google", "openrouter", "xai"}

# Model slugs that cannot handle images even on a vision-capable provider.
_TEXT_ONLY_HINTS = ("o1-mini", "o3-mini", "gpt-4.1-nano", "haiku")


def is_vision_capable(provider: str, model: str) -> bool:
    """Best-effort guess at whether (provider, model) accepts image inputs."""
    if provider not in _VISION_PROVIDERS:
        return False
    slug = model.lower()
    return not any(hint in slug for hint in _TEXT_ONLY_HINTS)


def _split_data_uri(data_uri: str) -> tuple[str, str]:
    """Split a 'data:<media>;base64,<payload>' URI into (media_type, payload)."""
    try:
        header, payload = data_uri.split(",", 1)
        media = header[len("data:") : header.index(";")]
        return media or "image/jpeg", payload
    except ValueError:
        return "image/jpeg", ""


def _chat_payload(
    provider: str,
    model: str,
    token_key: str,
    system: str,
    user: str,
    image_uri: str | None,
    max_tokens: int,
    temperature: float,
) -> dict[str, Any]:
    if provider == "anthropic":
        content: list[dict[str, Any]] = []
        if image_uri:
            media, b64 = _split_data_uri(image_uri)
            content.append(
                {"type": "image", "source": {"type": "base64", "media_type": media, "data": b64}}
            )
        content.append({"type": "text", "text": user})
        return {
            "model": model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": content}],
        }

    user_content: list[dict[str, Any]] = [{"type": "text", "text": user}]
    if image_uri:
        user_content.append({"type": "image_url", "image_url": {"url": image_uri}})
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
        token_key: max_tokens,
    }
    # Newer reasoning models (gpt-5 / o-series) only allow the default temperature.
    if token_key == "max_tokens":
        payload["temperature"] = temperature
    return payload


def _extract_text(provider: str, resp: dict[str, Any]) -> str:
    if provider == "anthropic":
        blocks = resp.get("content") or []
        return "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
    choices = resp.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message", {})
    content = message.get("content")
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict)).strip()
    return (content or "").strip()


def generate(
    provider: str,
    api_key: str,
    model: str,
    base_url: str,
    *,
    system: str,
    user: str,
    image_uri: str | None = None,
    max_tokens: int = 700,
    temperature: float = 0.4,
) -> str:
    """Run one chat completion and return the assistant text.

    Raises on transport/HTTP errors; callers should surface a friendly message.
    """
    provider = provider or DEFAULT_PROVIDER
    model = model.strip()
    if key_required(provider) and not api_key.strip():
        raise ValueError("No API key configured.")
    if not model:
        raise ValueError("No model configured.")

    token_key = _token_limit_key(provider, model)
    payload = _chat_payload(provider, model, token_key, system, user, image_uri, max_tokens, temperature)
    try:
        resp = _post_json(provider, api_key, model, base_url, payload, timeout=90)
    except urllib.error.HTTPError as exc:
        if exc.code != 400 or token_key == "max_completion_tokens":
            raise
        detail = ""
        with contextlib.suppress(OSError):
            detail = exc.read().decode("utf-8", errors="replace")
        if "max_completion_tokens" not in detail:
            raise
        payload = _chat_payload(
            provider, model, "max_completion_tokens", system, user, image_uri, max_tokens, temperature
        )
        resp = _post_json(provider, api_key, model, base_url, payload, timeout=90)
    return _extract_text(provider, resp)


__all__ = [
    "DEFAULT_LOCAL_BASE_URL",
    "DEFAULT_PROVIDER",
    "MODEL_GROUPS",
    "PROVIDER_LABELS",
    "PROVIDERS",
    "default_model",
    "flatten_models",
    "generate",
    "is_vision_capable",
    "key_required",
    "provider_choices",
    "test_connection",
]
