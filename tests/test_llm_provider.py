"""
Unit tests for the provider-agnostic LLM Layer, NVIDIA NIM integration,
and automatic session-aware fallback to OpenAI.
"""

import json
from unittest.mock import MagicMock, patch
import pytest

from src.llm.provider import (
    LLMResponse,
    FallbackLLMProvider,
    clean_reasoning_and_fences,
    extract_json_from_text,
    OpenAICompatibleClientAdapter,
)
from src.llm.nvidia_provider import NVIDIAProvider
from src.llm.openai_provider import OpenAIProvider


# =========================================================================
# TEST 1: Normal Operation — NVIDIA Works (OpenAI NOT Called)
# =========================================================================
def test_nvidia_provider_success():
    """Verify that when NVIDIA succeeds, it returns clean content and does not invoke fallback."""
    mock_nvidia_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.choices = [
        MagicMock(
            message=MagicMock(
                content="Solid-state battery research summary",
                reasoning_content="Internal chain of thought: evaluating dendrite formation.",
            )
        )
    ]
    mock_nvidia_client.chat.completions.create.return_value = mock_resp

    nvidia_prov = NVIDIAProvider(api_key="nvapi-test", client=mock_nvidia_client)
    mock_openai_prov = MagicMock()

    composite = FallbackLLMProvider(primary=nvidia_prov, fallback=mock_openai_prov, session_id="test_s1")
    resp = composite.generate([{"role": "user", "content": "Analyze batteries"}], operation="test_op")

    assert resp.content == "Solid-state battery research summary"
    assert resp.reasoning_content == "Internal chain of thought: evaluating dendrite formation."
    assert resp.provider_used == "NVIDIA"
    assert composite.last_provider_used == "NVIDIA"

    # OpenAI MUST NOT be called
    mock_openai_prov.generate.assert_not_called()
    mock_openai_prov.generate_structured.assert_not_called()


# =========================================================================
# TEST 2: NVIDIA API Key is Invalid -> Automatic Fallback to OpenAI
# =========================================================================
def test_nvidia_auth_failure_falls_back_to_openai():
    """Verify that an auth failure on NVIDIA switches to OpenAI for that call and session."""
    mock_nvidia_client = MagicMock()
    mock_nvidia_client.chat.completions.create.side_effect = Exception("401 Unauthorized: Invalid NVIDIA API Key")

    nvidia_prov = NVIDIAProvider(api_key="nvapi-invalid", client=mock_nvidia_client)

    mock_openai_prov = MagicMock()
    mock_openai_prov.provider_name = "OpenAI"
    mock_openai_prov.generate.return_value = LLMResponse(
        content="OpenAI generated fallback report",
        provider_used="OpenAI",
        model_used="gpt-4o",
    )

    composite = FallbackLLMProvider(primary=nvidia_prov, fallback=mock_openai_prov, session_id="test_s2")
    resp = composite.generate([{"role": "user", "content": "Test"}], operation="planner")

    assert resp.content == "OpenAI generated fallback report"
    assert resp.provider_used == "OpenAI"
    assert composite.last_provider_used == "OpenAI"
    mock_openai_prov.generate.assert_called_once()

    # Subsequent call in the same session should directly use OpenAI without re-attempting failed NVIDIA
    mock_openai_prov.generate.reset_mock()
    mock_nvidia_client.chat.completions.create.reset_mock()

    resp2 = composite.generate([{"role": "user", "content": "Next step"}], operation="synthesis")
    assert resp2.provider_used == "OpenAI"
    mock_openai_prov.generate.assert_called_once()
    mock_nvidia_client.chat.completions.create.assert_not_called()


# =========================================================================
# TEST 3: NVIDIA Returns HTTP 429 Rate Limit -> Backoff & Fallback
# =========================================================================
def test_nvidia_429_rate_limit_backoff_and_fallback():
    """Verify that HTTP 429 triggers bounded retries then switches to OpenAI."""
    mock_nvidia_client = MagicMock()
    mock_nvidia_client.chat.completions.create.side_effect = Exception("429 Too Many Requests: Rate limit exceeded")

    nvidia_prov = NVIDIAProvider(api_key="nvapi-test", client=mock_nvidia_client, max_retries=1)

    mock_openai_prov = MagicMock()
    mock_openai_prov.provider_name = "OpenAI"
    mock_openai_prov.generate_structured.return_value = {"claims": ["Fallback claim"]}

    with patch("time.sleep", return_value=None):  # Fast execution in tests
        composite = FallbackLLMProvider(primary=nvidia_prov, fallback=mock_openai_prov, session_id="test_s3")
        result = composite.generate_structured([{"role": "user", "content": "Claims"}], operation="claims")

    assert result == {"claims": ["Fallback claim"]}
    assert mock_nvidia_client.chat.completions.create.call_count == 2  # Initial + 1 retry
    mock_openai_prov.generate_structured.assert_called_once()


# =========================================================================
# TEST 4: NVIDIA Times Out -> Bounded Retry & Fallback
# =========================================================================
def test_nvidia_timeout_retry_and_fallback():
    """Verify that a timeout on NVIDIA retries and switches to OpenAI."""
    mock_nvidia_client = MagicMock()
    mock_nvidia_client.chat.completions.create.side_effect = Exception("Connection timed out after 60s")

    nvidia_prov = NVIDIAProvider(api_key="nvapi-test", client=mock_nvidia_client, max_retries=1)

    mock_openai_prov = MagicMock()
    mock_openai_prov.provider_name = "OpenAI"
    mock_openai_prov.generate.return_value = LLMResponse(
        content="OpenAI timeout rescue",
        provider_used="OpenAI",
        model_used="gpt-4o",
    )

    with patch("time.sleep", return_value=None):
        composite = FallbackLLMProvider(primary=nvidia_prov, fallback=mock_openai_prov, session_id="test_s4")
        resp = composite.generate([{"role": "user", "content": "Topic"}], operation="gap_detection")

    assert resp.content == "OpenAI timeout rescue"
    assert mock_nvidia_client.chat.completions.create.call_count == 2
    mock_openai_prov.generate.assert_called_once()


# =========================================================================
# TEST 5: NVIDIA Malformed Structured Output -> Recovery / Fallback
# =========================================================================
def test_nvidia_malformed_json_recovery_success():
    """Verify that markdown-fenced or leading conversational JSON is parsed cleanly."""
    raw_markdown_json = """Here is the research plan you requested:
```json
{
  "main_question": "What are the bottlenecks of solid-state cells?",
  "sub_questions": ["Electrolyte interface", "Manufacturing scale"]
}
```
Hope this helps!"""

    parsed = extract_json_from_text(raw_markdown_json)
    assert parsed["main_question"] == "What are the bottlenecks of solid-state cells?"
    assert len(parsed["sub_questions"]) == 2


def test_nvidia_completely_broken_json_falls_back_to_openai():
    """Verify that unrecoverable malformed JSON on NVIDIA falls back to OpenAI."""
    mock_nvidia_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content="I am unable to generate JSON today."))]
    mock_nvidia_client.chat.completions.create.return_value = mock_resp

    nvidia_prov = NVIDIAProvider(api_key="nvapi-test", client=mock_nvidia_client, max_retries=0)

    mock_openai_prov = MagicMock()
    mock_openai_prov.provider_name = "OpenAI"
    mock_openai_prov.generate_structured.return_value = {"status": "rescued_by_openai"}

    composite = FallbackLLMProvider(primary=nvidia_prov, fallback=mock_openai_prov, session_id="test_s5")
    result = composite.generate_structured([{"role": "user", "content": "Decompose"}], operation="planner")

    assert result == {"status": "rescued_by_openai"}
    mock_openai_prov.generate_structured.assert_called_once()


# =========================================================================
# TEST 6: NVIDIA Completely Unavailable -> Research Works Through OpenAI
# =========================================================================
def test_nvidia_unavailable_from_start():
    """Verify that if NVIDIA_API_KEY is not configured, FallbackLLMProvider seamlessly uses OpenAI."""
    nvidia_prov = NVIDIAProvider(api_key="", client=None)  # Unconfigured
    mock_openai_prov = MagicMock()
    mock_openai_prov.provider_name = "OpenAI"
    mock_openai_prov.generate.return_value = LLMResponse(
        content="Clean report via OpenAI",
        provider_used="OpenAI",
        model_used="gpt-4o",
    )

    composite = FallbackLLMProvider(primary=nvidia_prov, fallback=mock_openai_prov, session_id="test_s6")
    resp = composite.generate([{"role": "user", "content": "Topic"}], operation="synthesis")

    assert resp.content == "Clean report via OpenAI"
    assert resp.provider_used == "OpenAI"
    mock_openai_prov.generate.assert_called_once()


# =========================================================================
# TEST 7: Reasoning Model Handling (Nemotron Reasoning Isolation)
# =========================================================================
def test_reasoning_isolation_and_tag_stripping():
    """Verify that <think>...</think> tags are stripped from visible content."""
    raw_with_think = "<think>We should evaluate battery dendrites carefully.</think>The primary limitation is dendrite growth."
    cleaned = clean_reasoning_and_fences(raw_with_think)

    assert "<think>" not in cleaned
    assert "</think>" not in cleaned
    assert cleaned == "The primary limitation is dendrite growth."


# =========================================================================
# TEST 8: Health Check Verification (No Secrets Leaked)
# =========================================================================
def test_health_check_no_secrets():
    """Verify that health check reports metadata without leaking secret keys."""
    nvidia_prov = NVIDIAProvider(api_key="nvapi-super-secret-key-12345")
    health = nvidia_prov.health_check()

    assert health["provider"] == "NVIDIA"
    assert health["model"] == "nvidia/nemotron-3-super-120b-a12b"
    assert health["configured"] is True
    # Verify API key is NOT in health report
    assert "super-secret" not in str(health)
    assert "api_key" not in health
