"""
Centralized Configuration System for Agentic Research PRO.
Defines parameters for QUICK, STANDARD, and DEEP research depth modes,
along with model constants and resource/cost budget limits.
"""

import os
from dataclasses import dataclass
from typing import Dict

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "nvidia").strip().lower()
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

LLM_MODEL = NVIDIA_MODEL if LLM_PROVIDER == "nvidia" else OPENAI_MODEL

# Embedding Configuration: "local" (sentence-transformers) or "nvidia" (remote NIM API)
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local").strip().lower()
NVIDIA_EMBEDDING_MODEL = os.getenv("NVIDIA_EMBEDDING_MODEL", "nvidia/nemotron-3-embed-1b").strip()
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "16"))


def get_embedding_provider_name() -> str:
    """Return the active embedding provider name ('local' or 'nvidia')."""
    return os.getenv("EMBEDDING_PROVIDER", "local").strip().lower()


def get_embedding_model() -> str:
    """Return the active model identifier based on current provider."""
    provider = get_embedding_provider_name()
    if provider == "nvidia":
        return os.getenv("NVIDIA_EMBEDDING_MODEL", "nvidia/nemotron-3-embed-1b").strip()
    return "sentence-transformers/all-MiniLM-L6-v2"


def get_embedding_dimension() -> int:
    """Return vector dimension for the active provider (2048 for NVIDIA, 384 for MiniLM)."""
    provider = get_embedding_provider_name()
    if provider == "nvidia":
        return 2048
    return 384


EMBEDDING_MODEL = get_embedding_model()
EMBEDDING_DIMENSION = get_embedding_dimension()

# Playwright Browser Acquisition Configuration
PLAYWRIGHT_ENABLED = os.getenv("PLAYWRIGHT_ENABLED", "true").strip().lower() in ("true", "1", "yes")
PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true").strip().lower() in ("true", "1", "yes")
PLAYWRIGHT_MAX_PAGES = int(os.getenv("PLAYWRIGHT_MAX_PAGES", "3"))
PLAYWRIGHT_MAX_SCROLLS = int(os.getenv("PLAYWRIGHT_MAX_SCROLLS", "5"))
PLAYWRIGHT_TIMEOUT_MS = int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "15000"))


@dataclass(frozen=True)
class ResearchConfig:
    """Configuration parameters for a research session."""
    name: str
    max_queries: int
    max_sources: int
    max_iterations: int
    top_k: int
    verification_level: str
    source_quality_threshold: float
    enable_planning: bool
    enable_gap_detection: bool
    enable_contradiction_detection: bool
    # Cost-aware LLM control fields
    max_llm_calls: int
    max_claims_to_verify: int
    max_evidence_chunks_per_claim: int
    max_follow_up_gap_analyses: int


RESEARCH_CONFIGS: Dict[str, ResearchConfig] = {
    "QUICK": ResearchConfig(
        name="QUICK",
        max_queries=1,
        max_sources=5,
        max_iterations=1,
        top_k=10,
        verification_level="minimal",
        source_quality_threshold=0.35,
        enable_planning=False,
        enable_gap_detection=False,
        enable_contradiction_detection=False,
        max_llm_calls=3,
        max_claims_to_verify=5,
        max_evidence_chunks_per_claim=3,
        max_follow_up_gap_analyses=0,
    ),
    "STANDARD": ResearchConfig(
        name="STANDARD",
        max_queries=3,
        max_sources=10,
        max_iterations=2,
        top_k=20,
        verification_level="moderate",
        source_quality_threshold=0.45,
        enable_planning=True,
        enable_gap_detection=True,
        enable_contradiction_detection=False,
        max_llm_calls=8,
        max_claims_to_verify=10,
        max_evidence_chunks_per_claim=4,
        max_follow_up_gap_analyses=1,
    ),
    "DEEP": ResearchConfig(
        name="DEEP",
        max_queries=6,
        max_sources=20,
        max_iterations=3,
        top_k=30,
        verification_level="comprehensive",
        source_quality_threshold=0.50,
        enable_planning=True,
        enable_gap_detection=True,
        enable_contradiction_detection=True,
        max_llm_calls=16,
        max_claims_to_verify=20,
        max_evidence_chunks_per_claim=5,
        max_follow_up_gap_analyses=2,
    ),
}


def get_research_config(depth: str) -> ResearchConfig:
    """
    Retrieve research configuration for a given depth level.
    Defaults to STANDARD if depth is unrecognized.
    """
    normalized = depth.strip().upper() if depth else "STANDARD"
    return RESEARCH_CONFIGS.get(normalized, RESEARCH_CONFIGS["STANDARD"])
