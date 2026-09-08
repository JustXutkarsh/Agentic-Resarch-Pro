"""
Research Metrics Tracker for Agentic Research PRO.
Records real execution counters, timestamps, throughput metrics,
and reproducibility metadata across the end-to-end pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from src.config import LLM_MODEL, EMBEDDING_MODEL

APP_VERSION = "2.0.0"


@dataclass
class ResearchMetrics:
    """Exact computational metrics and provenance for a research run."""
    session_id: str
    topic: str
    depth: str
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: str = ""
    execution_time_seconds: float = 0.0

    # Counters from actual pipeline execution
    generated_queries: int = 0
    total_sources_found: int = 0
    duplicate_sources_removed: int = 0
    sources_accepted: int = 0
    sources_rejected: int = 0
    scraping_failures: int = 0
    research_iterations: int = 0
    total_documents: int = 0
    total_chunks: int = 0
    retrieved_evidence_chunks: int = 0
    research_gaps: int = 0
    claims_analyzed: int = 0
    supported_claims: int = 0
    weakly_supported_claims: int = 0
    contradictions_detected: int = 0
    llm_calls_made: int = 0

    # Reproducibility metadata
    llm_model: str = LLM_MODEL
    embedding_model: str = EMBEDDING_MODEL
    app_version: str = APP_VERSION

    def finalize(self) -> None:
        """Mark end time and calculate total elapsed duration in seconds."""
        self.end_time = datetime.now().isoformat()
        try:
            start_dt = datetime.fromisoformat(self.start_time)
            end_dt = datetime.fromisoformat(self.end_time)
            self.execution_time_seconds = round((end_dt - start_dt).total_seconds(), 2)
        except Exception:
            self.execution_time_seconds = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "topic": self.topic,
            "depth": self.depth,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time_seconds": self.execution_time_seconds,
            "generated_queries": self.generated_queries,
            "total_sources_found": self.total_sources_found,
            "duplicate_sources_removed": self.duplicate_sources_removed,
            "sources_accepted": self.sources_accepted,
            "sources_rejected": self.sources_rejected,
            "scraping_failures": self.scraping_failures,
            "research_iterations": self.research_iterations,
            "total_documents": self.total_documents,
            "total_chunks": self.total_chunks,
            "retrieved_evidence_chunks": self.retrieved_evidence_chunks,
            "research_gaps": self.research_gaps,
            "claims_analyzed": self.claims_analyzed,
            "supported_claims": self.supported_claims,
            "weakly_supported_claims": self.weakly_supported_claims,
            "contradictions_detected": self.contradictions_detected,
            "llm_calls_made": self.llm_calls_made,
            "llm_model": self.llm_model,
            "embedding_model": self.embedding_model,
            "app_version": self.app_version,
        }
