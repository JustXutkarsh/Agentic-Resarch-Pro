"""
LLM Provider Package for Agentic Research PRO.
Exposes provider-agnostic interfaces, NVIDIA NIM primary provider,
OpenAI fallback provider, and factory helper.
"""

import os
from typing import Optional

from src.llm.provider import (
    LLMProvider,
    LLMResponse,
    FallbackLLMProvider,
    OpenAICompatibleClientAdapter,
    clean_reasoning_and_fences,
    extract_json_from_text,
)
from src.llm.nvidia_provider import NVIDIAProvider
from src.llm.openai_provider import OpenAIProvider


# In-memory registry for session-bound providers
_session_providers: dict = {}


def get_llm_provider(session_id: Optional[str] = None) -> LLMProvider:
    """
    Factory creating the configured LLM provider hierarchy.
    By default:
    - Primary: NVIDIA NIM (nvidia/nemotron-3-super-120b-a12b)
    - Fallback: Existing OpenAI implementation (gpt-4o)
    
    If LLM_PROVIDER=openai is explicitly set, uses OpenAI directly.
    When a session_id is provided, the provider instance is cached so
    that any provider failure marks the primary as unavailable for all
    subsequent calls within that session.
    """
    if session_id and session_id in _session_providers:
        return _session_providers[session_id]

    provider_pref = os.getenv("LLM_PROVIDER", "nvidia").strip().lower()

    if provider_pref == "openai":
        provider = OpenAIProvider()
        if session_id:
            _session_providers[session_id] = provider
        return provider

    # Primary: NVIDIA NIM
    primary = NVIDIAProvider()

    # Fallback: OpenAI if OPENAI_API_KEY is configured
    fallback = None
    if os.getenv("OPENAI_API_KEY"):
        fallback = OpenAIProvider()

    provider = FallbackLLMProvider(primary=primary, fallback=fallback, session_id=session_id)
    if session_id:
        _session_providers[session_id] = provider
    return provider


__all__ = [
    "LLMProvider",
    "LLMResponse",
    "NVIDIAProvider",
    "OpenAIProvider",
    "FallbackLLMProvider",
    "OpenAICompatibleClientAdapter",
    "get_llm_provider",
    "clean_reasoning_and_fences",
    "extract_json_from_text",
]
