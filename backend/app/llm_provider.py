"""
Provider-agnostic LLM factory.

Set LLM_PROVIDER in .env to one of: groq | openrouter | ollama
Each returns a LangChain BaseChatModel with the same .invoke() interface,
so graph nodes never need to know which provider is active.
"""
import os
from functools import lru_cache
from langchain_core.language_models.chat_models import BaseChatModel


def _build_groq() -> BaseChatModel:
    from langchain_groq import ChatGroq
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set. Get one free at https://console.groq.com/keys")
    return ChatGroq(
        model=os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
        api_key=api_key,
        temperature=0.2,
    )


def _build_openrouter() -> BaseChatModel:
    # Prefer the dedicated package; fall back to ChatOpenAI + base_url override
    # since OpenRouter exposes an OpenAI-compatible endpoint either way.
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set. Get one at https://openrouter.ai/keys")
    model = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
    try:
        from langchain_openrouter import ChatOpenRouter
        return ChatOpenRouter(model=model, api_key=api_key, temperature=0.2)
    except ImportError:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.2,
        )


def _build_ollama() -> BaseChatModel:
    from langchain_ollama import ChatOllama
    return ChatOllama(
        model=os.environ.get("OLLAMA_MODEL", "qwen3:4b-q4_K_M"),
        base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.2,
    )


_BUILDERS = {
    "groq": _build_groq,
    "openrouter": _build_openrouter,
    "ollama": _build_ollama,
}


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    """Return the configured LLM, cached for the process lifetime."""
    provider = os.environ.get("LLM_PROVIDER", "groq").lower()
    if provider not in _BUILDERS:
        raise RuntimeError(f"Unknown LLM_PROVIDER '{provider}'. Choose from: {list(_BUILDERS)}")
    return _BUILDERS[provider]()


def get_llm_for_provider(provider: str) -> BaseChatModel:
    """Build an LLM for a specific provider, bypassing the cached default.
    Useful if the frontend lets the user switch provider per-session."""
    if provider not in _BUILDERS:
        raise RuntimeError(f"Unknown provider '{provider}'. Choose from: {list(_BUILDERS)}")
    return _BUILDERS[provider]()
