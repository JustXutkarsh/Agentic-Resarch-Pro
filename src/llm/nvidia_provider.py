"""
NVIDIA NIM Primary LLM Provider.
Integrates with NVIDIA NIM OpenAI-compatible API using Nemotron models.
Provides reasoning isolation, JSON parsing with auto-repair, and bounded backoff.
"""

import os
import time
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI

from src.llm.provider import (
    LLMProvider,
    LLMResponse,
    clean_reasoning_and_fences,
    extract_json_from_text,
)

logger = logging.getLogger("NVIDIAProvider")

DEFAULT_NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_NVIDIA_MODEL = "nvidia/nemotron-3-super-120b-a12b"


class NVIDIAProvider(LLMProvider):
    """Primary LLM provider using NVIDIA NIM OpenAI-compatible endpoint."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        client: Optional[OpenAI] = None,
        max_retries: int = 2,
    ):
        self.api_key = api_key if api_key is not None else os.getenv("NVIDIA_API_KEY", "")
        self.base_url = base_url or os.getenv("NVIDIA_BASE_URL", DEFAULT_NVIDIA_BASE_URL)
        self.model = model or os.getenv("NVIDIA_MODEL", DEFAULT_NVIDIA_MODEL)
        self.max_retries = max_retries
        self._client = client

    @property
    def provider_name(self) -> str:
        return "NVIDIA"

    @property
    def model_name(self) -> str:
        return self.model

    def _get_client(self) -> OpenAI:
        """Lazy instantiation of OpenAI-compatible client for NVIDIA NIM."""
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    "NVIDIA_API_KEY is not configured. Please set NVIDIA_API_KEY in your environment or .env file."
                )
            self._client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=60.0,
            )
        return self._client

    def _execute_with_retry(self, operation: str, call_func):
        """Execute an API call with bounded exponential backoff for rate limits and 5xx errors."""
        retries = 0
        last_exception = None

        while retries <= self.max_retries:
            try:
                start_time = time.time()
                result = call_func()
                duration = round(time.time() - start_time, 2)
                logger.info(f"[LLM] Provider: NVIDIA | Model: {self.model} | Operation: {operation} | Success ({duration}s)")
                return result
            except Exception as e:
                last_exception = e
                err_str = str(e).lower()
                status_code = getattr(e, "status_code", None)

                # Check if retryable: 429 (rate limit), 500, 502, 503, 504, timeout, connection
                is_rate_limit = "429" in err_str or status_code == 429 or "rate limit" in err_str
                is_server_error = any(str(code) in err_str for code in [500, 502, 503, 504]) or (status_code and status_code >= 500)
                is_timeout = "timeout" in err_str or "timed out" in err_str
                is_connection = "connection" in err_str or "network" in err_str

                if (is_rate_limit or is_server_error or is_timeout or is_connection) and retries < self.max_retries:
                    wait_time = 2 ** retries  # 1s, 2s
                    logger.warning(
                        f"[LLM] NVIDIA request error ({e}) during {operation}. Retrying in {wait_time}s (Attempt {retries + 1}/{self.max_retries})..."
                    )
                    time.sleep(wait_time)
                    retries += 1
                else:
                    logger.error(f"[LLM] NVIDIA non-retryable or exhausted error during {operation}: {e}")
                    raise e

        raise last_exception

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        op_name = operation or "text_generation"
        client = self._get_client()

        create_kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            create_kwargs["max_tokens"] = max_tokens

        def _call():
            return client.chat.completions.create(**create_kwargs)

        raw_resp = self._execute_with_retry(op_name, _call)
        choice = raw_resp.choices[0]
        msg = choice.message

        # Separate reasoning content from visible final content
        reasoning = getattr(msg, "reasoning_content", None)
        raw_content = msg.content or ""
        
        # Clean any internal <think> tags if model embedded them in text
        final_content = clean_reasoning_and_fences(raw_content)

        usage = getattr(raw_resp, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
        completion_tokens = getattr(usage, "completion_tokens", 0) if usage else 0

        return LLMResponse(
            content=final_content,
            reasoning_content=reasoning,
            provider_used="NVIDIA",
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
        op_name = operation or "structured_generation"
        client = self._get_client()

        create_kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        if max_tokens:
            create_kwargs["max_tokens"] = max_tokens

        def _call():
            try:
                return client.chat.completions.create(**create_kwargs)
            except Exception as e:
                # If NVIDIA NIM returns error regarding response_format parameter, retry without it
                err_str = str(e).lower()
                if "response_format" in err_str or "unsupported" in err_str or "400" in err_str:
                    logger.info(f"[LLM] NVIDIA model does not support response_format param; retrying with strict JSON prompt.")
                    fallback_kwargs = dict(create_kwargs)
                    fallback_kwargs.pop("response_format", None)
                    return client.chat.completions.create(**fallback_kwargs)
                raise

        raw_resp = self._execute_with_retry(op_name, _call)
        raw_text = raw_resp.choices[0].message.content or "{}"

        # Parse JSON
        try:
            return extract_json_from_text(raw_text)
        except Exception as parse_err:
            logger.warning(f"[LLM] NVIDIA JSON parsing initial failure: {parse_err}. Attempting 1 corrective repair query...")
            
            # Corrective retry prompt
            repair_messages = list(messages) + [
                {"role": "assistant", "content": raw_text},
                {
                    "role": "user",
                    "content": "CRITICAL: Your previous output was not valid JSON. Return ONLY the raw JSON object without markdown fences, explanations, or commentary.",
                },
            ]
            repair_kwargs = {
                "model": self.model,
                "messages": repair_messages,
                "temperature": 0.0,
            }
            retry_resp = self._execute_with_retry(f"{op_name}_repair", lambda: client.chat.completions.create(**repair_kwargs))
            retry_text = retry_resp.choices[0].message.content or "{}"
            return extract_json_from_text(retry_text)

    def health_check(self) -> Dict[str, Any]:
        configured = bool(self.api_key and self.api_key.strip())
        reachable = False
        error_msg = None

        if configured:
            try:
                # Test reachability with a minimal non-intrusive call
                client = self._get_client()
                # Use models.list() or a 1-token probe with short timeout
                client.models.list(timeout=5.0)
                reachable = True
            except Exception as e:
                error_msg = str(e)
                reachable = False

        return {
            "provider": "NVIDIA",
            "model": self.model,
            "base_url": self.base_url,
            "configured": configured,
            "reachable": reachable,
            "error": error_msg,
        }
