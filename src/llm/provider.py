"""
Provider-agnostic LLM Layer for Agentic Research PRO.
Defines LLMProvider base interface, LLMResponse, and FallbackLLMProvider
orchestrating primary (NVIDIA NIM) and fallback (OpenAI) execution.
"""

import os
import re
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger("LLMProvider")


@dataclass
class LLMResponse:
    """Normalized response returned by all LLM providers."""
    content: str
    reasoning_content: Optional[str] = None
    provider_used: str = "unknown"
    model_used: str = "unknown"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    raw_response: Any = None


def clean_reasoning_and_fences(raw_text: str) -> str:
    """
    Remove reasoning blocks like <think>...</think> and strip markdown fences
    if pure JSON or clean text is needed.
    """
    if not raw_text:
        return ""

    # Strip <think>...</think> tags if reasoning model embedded them in content
    cleaned = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()
    return cleaned


def extract_json_from_text(raw_text: str) -> Dict[str, Any]:
    """
    Extract and parse valid JSON from LLM output, handling markdown code blocks,
    preceding conversational text, or trailing content.
    """
    cleaned = clean_reasoning_and_fences(raw_text)

    # 1. Try direct json.loads
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 2. Try extracting from ```json ... ``` code block
    json_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if json_block_match:
        try:
            return json.loads(json_block_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3. Try finding first { or [ to last } or ]
    start_brace = cleaned.find("{")
    end_brace = cleaned.rfind("}")
    if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
        try:
            return json.loads(cleaned[start_brace : end_brace + 1])
        except json.JSONDecodeError:
            pass

    start_bracket = cleaned.find("[")
    end_bracket = cleaned.rfind("]")
    if start_bracket != -1 and end_bracket != -1 and end_bracket > start_bracket:
        try:
            return json.loads(cleaned[start_bracket : end_bracket + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Failed to parse valid JSON from LLM response: {raw_text[:200]}...")


class LLMProvider(ABC):
    """Abstract interface for language model providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g., 'NVIDIA', 'OpenAI')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the model being called."""
        pass

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text completion from prompt messages."""
        pass

    @abstractmethod
    def generate_structured(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate and parse structured JSON output from prompt messages."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Verify configuration and API reachability."""
        pass


class FallbackLLMProvider(LLMProvider):
    """
    Composite provider orchestrating primary (NVIDIA NIM) with automatic
    real-time fallback to existing OpenAI provider.
    
    Session-aware: If primary fails during a research session, it switches to
    fallback for that operation and marks primary as temporarily unavailable for
    the remainder of the session to prevent repeated delay.
    """

    def __init__(
        self,
        primary: LLMProvider,
        fallback: Optional[LLMProvider] = None,
        session_id: Optional[str] = None,
    ):
        self.primary = primary
        self.fallback = fallback
        self.session_id = session_id or "default"
        self._primary_available = True
        self.last_provider_used = self.primary.provider_name

    @property
    def provider_name(self) -> str:
        return f"{self.primary.provider_name} (Fallback: {self.fallback.provider_name if self.fallback else 'None'})"

    @property
    def model_name(self) -> str:
        if self._primary_available:
            return self.primary.model_name
        return self.fallback.model_name if self.fallback else self.primary.model_name

    def mark_primary_unavailable(self, reason: str):
        """Mark primary as unavailable for this session."""
        if self._primary_available:
            logger.warning(
                f"[LLM] Primary provider ({self.primary.provider_name}) marked unavailable for session '{self.session_id}': {reason}"
            )
            self._primary_available = False
            if self.fallback:
                logger.info(f"[LLM] Fallback provider active: {self.fallback.provider_name}")

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        op_desc = operation or "generation"

        # Attempt Primary (NVIDIA) first if available
        if self._primary_available:
            try:
                logger.info(f"[LLM] Primary provider: {self.primary.provider_name} | Operation: {op_desc}")
                response = self.primary.generate(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    operation=op_desc,
                    **kwargs,
                )
                self.last_provider_used = self.primary.provider_name
                return response
            except Exception as e:
                logger.error(f"[LLM] Primary provider ({self.primary.provider_name}) request failed during {op_desc}: {e}")
                self.mark_primary_unavailable(str(e))
                if not self.fallback:
                    raise

        # Fallback to OpenAI if primary failed or was already unavailable
        if self.fallback:
            logger.info(f"[LLM] Falling back to existing {self.fallback.provider_name} provider | Operation: {op_desc}")
            response = self.fallback.generate(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                operation=op_desc,
                **kwargs,
            )
            self.last_provider_used = self.fallback.provider_name
            return response

        raise RuntimeError(f"All LLM providers unavailable for operation: {op_desc}")

    def generate_structured(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        op_desc = operation or "structured_generation"

        # Attempt Primary (NVIDIA) first if available
        if self._primary_available:
            try:
                logger.info(f"[LLM] Primary provider: {self.primary.provider_name} | Operation: {op_desc}")
                result = self.primary.generate_structured(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    operation=op_desc,
                    **kwargs,
                )
                self.last_provider_used = self.primary.provider_name
                return result
            except Exception as e:
                logger.error(f"[LLM] Primary provider ({self.primary.provider_name}) structured request failed during {op_desc}: {e}")
                self.mark_primary_unavailable(str(e))
                if not self.fallback:
                    raise

        # Fallback to OpenAI
        if self.fallback:
            logger.info(f"[LLM] Falling back to existing {self.fallback.provider_name} provider | Operation: {op_desc}")
            result = self.fallback.generate_structured(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                operation=op_desc,
                **kwargs,
            )
            self.last_provider_used = self.fallback.provider_name
            return result

        raise RuntimeError(f"All LLM providers unavailable for structured operation: {op_desc}")

    def health_check(self) -> Dict[str, Any]:
        primary_health = self.primary.health_check()
        fallback_health = self.fallback.health_check() if self.fallback else None

        return {
            "primary": primary_health,
            "fallback": fallback_health,
            "active_provider": self.primary.provider_name if self._primary_available else (self.fallback.provider_name if self.fallback else "none"),
            "session_id": self.session_id,
        }


class OpenAICompatibleClientAdapter(LLMProvider):
    """
    Adapter allowing legacy OpenAI mock objects or custom clients
    (e.g., in unit tests) to satisfy the LLMProvider interface transparently.
    """

    def __init__(self, client: Any, model: str = "gpt-4o"):
        self.client = client
        self._model = model

    @property
    def provider_name(self) -> str:
        return "LegacyClientAdapter"

    @property
    def model_name(self) -> str:
        return self._model

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        create_kwargs: Dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            create_kwargs["max_tokens"] = max_tokens

        resp = self.client.chat.completions.create(**create_kwargs)
        content = resp.choices[0].message.content or ""
        reasoning = getattr(resp.choices[0].message, "reasoning_content", None)

        return LLMResponse(
            content=content,
            reasoning_content=reasoning,
            provider_used="LegacyClientAdapter",
            model_used=self._model,
            raw_response=resp,
        )

    def generate_structured(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        create_kwargs: Dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        if max_tokens:
            create_kwargs["max_tokens"] = max_tokens

        try:
            resp = self.client.chat.completions.create(**create_kwargs)
        except Exception:
            # Retry without response_format if client doesn't support it
            create_kwargs.pop("response_format", None)
            resp = self.client.chat.completions.create(**create_kwargs)

        raw = resp.choices[0].message.content or "{}"
        return extract_json_from_text(raw)

    def health_check(self) -> Dict[str, Any]:
        return {
            "provider": "LegacyClientAdapter",
            "model": self._model,
            "configured": True,
            "reachable": True,
        }
