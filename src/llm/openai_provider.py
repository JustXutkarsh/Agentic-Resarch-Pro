"""
OpenAI Fallback LLM Provider.
Preserves the existing OpenAI gpt-4o implementation as an authentic fallback safety net.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI

from src.llm.provider import LLMProvider, LLMResponse, extract_json_from_text

logger = logging.getLogger("OpenAIProvider")

DEFAULT_OPENAI_MODEL = "gpt-4o"


class OpenAIProvider(LLMProvider):
    """Fallback LLM provider using the existing OpenAI implementation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        client: Optional[OpenAI] = None,
    ):
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
        self._client = client

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    @property
    def model_name(self) -> str:
        return self.model

    def _get_client(self) -> OpenAI:
        if self._client is None:
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY is not configured in environment or .env.")
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        client = self._get_client()
        op_name = operation or "text_generation"

        create_kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            create_kwargs["max_tokens"] = max_tokens

        logger.info(f"[LLM] Provider: OpenAI | Model: {self.model} | Operation: {op_name}")
        raw_resp = client.chat.completions.create(**create_kwargs)
        content = raw_resp.choices[0].message.content or ""

        usage = getattr(raw_resp, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
        completion_tokens = getattr(usage, "completion_tokens", 0) if usage else 0

        return LLMResponse(
            content=content,
            provider_used="OpenAI",
            model_used=self.model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            raw_response=raw_resp,
        )

    def generate_structured(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        client = self._get_client()
        op_name = operation or "structured_generation"

        create_kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        if max_tokens:
            create_kwargs["max_tokens"] = max_tokens

        logger.info(f"[LLM] Provider: OpenAI | Model: {self.model} | Operation: {op_name}")
        raw_resp = client.chat.completions.create(**create_kwargs)
        raw_text = raw_resp.choices[0].message.content or "{}"
        return extract_json_from_text(raw_text)

    def health_check(self) -> Dict[str, Any]:
        configured = bool(self.api_key and self.api_key.strip())
        reachable = False
        error_msg = None

        if configured:
            try:
                client = self._get_client()
                client.models.list(timeout=5.0)
                reachable = True
            except Exception as e:
                error_msg = str(e)
                reachable = False

        return {
            "provider": "OpenAI",
            "model": self.model,
            "configured": configured,
            "reachable": reachable,
            "error": error_msg,
        }
