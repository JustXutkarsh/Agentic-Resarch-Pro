"""Unit tests for src/config.py"""
import pytest
from src.config import (
    ResearchConfig,
    RESEARCH_CONFIGS,
    get_research_config,
    LLM_MODEL,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
)


def test_model_constants():
    assert LLM_MODEL == "gpt-4o"
    assert EMBEDDING_MODEL == "sentence-transformers/all-MiniLM-L6-v2"
    assert EMBEDDING_DIMENSION == 384


def test_get_research_config_presets():
    quick = get_research_config("QUICK")
    assert quick.name == "QUICK"
    assert quick.max_queries == 1
    assert quick.max_sources == 5
    assert quick.max_iterations == 1
    assert quick.enable_planning is False
    assert quick.enable_gap_detection is False
    assert quick.enable_contradiction_detection is False

    standard = get_research_config("STANDARD")
    assert standard.name == "STANDARD"
    assert standard.max_queries == 3
    assert standard.max_sources == 10
    assert standard.max_iterations == 2
    assert standard.enable_planning is True
    assert standard.enable_gap_detection is True
    assert standard.enable_contradiction_detection is False

    deep = get_research_config("DEEP")
    assert deep.name == "DEEP"
    assert deep.max_queries == 6
    assert deep.max_sources == 20
    assert deep.max_iterations == 3
    assert deep.enable_planning is True
    assert deep.enable_gap_detection is True
    assert deep.enable_contradiction_detection is True


def test_get_research_config_case_insensitivity_and_fallback():
    assert get_research_config("quick").name == "QUICK"
    assert get_research_config("standard").name == "STANDARD"
    assert get_research_config("deep").name == "DEEP"
    assert get_research_config("unknown_mode").name == "STANDARD"
    assert get_research_config("").name == "STANDARD"


def test_research_config_hierarchy():
    q = get_research_config("QUICK")
    s = get_research_config("STANDARD")
    d = get_research_config("DEEP")

    assert q.max_queries < s.max_queries < d.max_queries
    assert q.max_sources < s.max_sources < d.max_sources
    assert q.max_iterations <= s.max_iterations < d.max_iterations
    assert q.max_llm_calls < s.max_llm_calls < d.max_llm_calls
    assert q.max_claims_to_verify < s.max_claims_to_verify < d.max_claims_to_verify
