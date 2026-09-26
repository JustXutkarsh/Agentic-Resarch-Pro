"""
Contradiction & Divergence Detector for Agentic Research PRO.
Identifies genuine empirical disagreements, trade-offs, and conflicting perspectives
across research dimensions during DEEP research mode.
Uses dimension-based evidence clustering before invoking GPT-4o.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from openai import OpenAI
from src.config import ResearchConfig, LLM_MODEL
from src.research_planner import ResearchPlan
from src.embedder import embed_text, embed_query
from src.hallucination import cosine_similarity

from src.llm import LLMProvider, get_llm_provider, OpenAICompatibleClientAdapter

logger = logging.getLogger(__name__)


@dataclass
class Contradiction:
    """Represents a validated divergence or contradiction between research sources."""
    topic: str
    perspective_a: str
    perspective_b: str
    supporting_sources_a: List[str] = field(default_factory=list)
    supporting_sources_b: List[str] = field(default_factory=list)
    resolution: str = ""
    divergence_type: str = "DIRECT_CONTRADICTION"  # DIRECT_CONTRADICTION, PARTIAL_TENSION, DIFFERENT_SCOPE, DIFFERENT_TIMEFRAME, DIFFERENT_DEFINITION
    scope_difference: str = ""
    timeframe_a: str = ""
    timeframe_b: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "perspective_a": self.perspective_a,
            "perspective_b": self.perspective_b,
            "supporting_sources_a": self.supporting_sources_a,
            "supporting_sources_b": self.supporting_sources_b,
            "resolution": self.resolution,
            "divergence_type": self.divergence_type,
            "scope_difference": self.scope_difference,
            "timeframe_a": self.timeframe_a,
            "timeframe_b": self.timeframe_b,
        }


def _group_chunks_by_dimension(
    dimensions: List[str],
    chunks: List[Dict[str, Any]],
    similarity_threshold: float = 0.30,
) -> Dict[str, List[Dict[str, Any]]]:
    """Group evidence chunks into dimension clusters using embeddings."""
    grouped: Dict[str, List[Dict[str, Any]]] = {dim: [] for dim in dimensions}

    dim_embeddings = {dim: embed_query(dim) for dim in dimensions}

    for chunk_dict in chunks:
        text = chunk_dict.get("text", "")
        if not text:
            continue

        chunk_emb = embed_text(text, is_query=False)

        # Assign to best matching dimension above threshold
        best_dim = None
        best_sim = -1.0

        for dim, dim_emb in dim_embeddings.items():
            sim = cosine_similarity(dim_emb, chunk_emb)
            if sim > best_sim:
                best_sim = sim
                best_dim = dim

        if best_dim and best_sim >= similarity_threshold:
            grouped[best_dim].append(chunk_dict)

    return grouped


class ContradictionDetector:
    """Identifies nuanced disagreements and opposing evidence across research dimensions."""

    def __init__(
        self,
        client: Optional[Any] = None,
        llm_provider: Optional[LLMProvider] = None,
        session_id: Optional[str] = None,
    ):
        self.client = client
        self._provider = llm_provider
        self.session_id = session_id

    def _get_provider(self) -> LLMProvider:
        if self._provider is not None:
            return self._provider
        if self.client is not None:
            self._provider = OpenAICompatibleClientAdapter(self.client, model=LLM_MODEL)
            return self._provider
        self._provider = get_llm_provider(session_id=self.session_id)
        return self._provider

    def _get_client(self) -> Any:
        if self.client is None:
            self.client = OpenAI()
        return self.client

    def detect_contradictions(
        self,
        topic: str,
        plan: ResearchPlan,
        evidence_chunks: List[Dict[str, Any]],
        config: ResearchConfig,
        max_contradiction_pairs: int = 5,
    ) -> List[Contradiction]:
        """
        Detect contradictions across evidence dimensions with scope awareness.
        Distinguishes between direct factual contradictions and different operational regimes.
        """
        if not config.enable_contradiction_detection:
            logger.info("Contradiction detection is disabled for this research depth.")
            return []

        if len(evidence_chunks) < 4:
            logger.info("Insufficient evidence chunks to perform meaningful contradiction analysis.")
            return []

        dimensions = plan.research_dimensions or ["Core Findings", "Market Outlook"]
        grouped = _group_chunks_by_dimension(dimensions, evidence_chunks)

        # Select dimensions with at least 2 distinct chunks for comparison
        candidate_dimensions = [
            dim for dim, chunks in grouped.items() if len(chunks) >= 2
        ][:max_contradiction_pairs]

        if not candidate_dimensions:
            if len(evidence_chunks) >= 2:
                candidate_dimensions = ["Cross-Dimensional Analysis"]
                grouped["Cross-Dimensional Analysis"] = evidence_chunks[:4]
            else:
                return []

        # Prepare payload for batched analysis preserving up to 1200 chars per snippet
        analysis_payload = []
        for dim in candidate_dimensions:
            chunks = grouped[dim][:4]
            snippets = [
                {
                    "text": c.get("text", "")[:1200],
                    "url": c.get("metadata", {}).get("source_url", "source"),
                    "domain": c.get("metadata", {}).get("source_domain", ""),
                    "tier": c.get("metadata", {}).get("authority_tier", 3),
                }
                for c in chunks
            ]
            analysis_payload.append({
                "dimension": dim,
                "evidence": snippets,
            })

        prompt = f"""
You are an objective academic peer reviewer analyzing research evidence for nuanced conflicts, divergences, and trade-offs.

TOPIC: {topic}

EVIDENCE BY DIMENSION:
{json.dumps(analysis_payload, indent=2)}

CRITICAL PRINCIPLES FOR CONTRADICTION DETECTION:
1. SCOPE & REGIME SENSITIVITY:
   - Do NOT treat statements from different operational regimes as direct contradictions!
   - For example, a paper demonstrating synthetic sampling advantage on noisy qubits in 2023 (NISQ era) does NOT contradict a report concluding commercial advantage in chemistry requires fault-tolerant logical qubits in 2035-2040. They address DIFFERENT SCOPES and DIFFERENT TIMEFRAMES.
2. DIVERGENCE CLASSIFICATION:
   - "DIRECT_CONTRADICTION": Same subject, same timeframe, mutually exclusive claims (e.g., conflicting error thresholds under identical code parameters).
   - "PARTIAL_TENSION": Competing architectural trade-offs (e.g., high gate speed vs long coherence time).
   - "DIFFERENT_SCOPE": Different operational regimes (e.g., NISQ benchmark vs Fault-Tolerant production).
   - "DIFFERENT_TIMEFRAME": Short-term roadmap milestone (e.g. 2026-2029) vs long-term commercial maturity (e.g. 2035-2040).
   - "DIFFERENT_DEFINITION": Competing definitions of the term (e.g., computational advantage vs economic ROI advantage).
3. EXCLUSION:
   - If evidence passages are complementary, consistent, or simply discuss different aspects of the same topic, DO NOT force a contradiction. Only record meaningful divergences.

Return JSON strictly in this format:
{{
  "contradictions": [
    {{
      "topic": "Dimension name or sub-topic",
      "divergence_type": "DIRECT_CONTRADICTION | PARTIAL_TENSION | DIFFERENT_SCOPE | DIFFERENT_TIMEFRAME | DIFFERENT_DEFINITION",
      "perspective_a": "First distinct perspective or finding",
      "perspective_b": "Directly opposing or conflicting perspective",
      "supporting_sources_a": ["URL or source A"],
      "supporting_sources_b": ["URL or source B"],
      "scope_difference": "Explicit explanation of differing conditions, assumptions, or scopes (e.g. NISQ vs FTQC, 2026 vs 2040)",
      "timeframe_a": "Applicable timeframe for perspective A (or 'N/A')",
      "timeframe_b": "Applicable timeframe for perspective B (or 'N/A')",
      "resolution": "Synthesized reconciliation explaining how both findings relate or which is more empirically rigorous"
    }}
  ]
}}
"""

        try:
            provider = self._get_provider()
            data_dict = provider.generate_structured(
                messages=[
                    {"role": "system", "content": "You are an objective academic research reviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                operation="contradiction_detection",
            )
            data = data_dict.get("contradictions", [])

            results = []
            for item in data[:max_contradiction_pairs]:
                results.append(
                    Contradiction(
                        topic=item.get("topic", topic),
                        perspective_a=item.get("perspective_a", ""),
                        perspective_b=item.get("perspective_b", ""),
                        supporting_sources_a=item.get("supporting_sources_a", []),
                        supporting_sources_b=item.get("supporting_sources_b", []),
                        resolution=item.get("resolution", "Different analytical methodologies lead to diverging estimates."),
                        divergence_type=item.get("divergence_type", "DIRECT_CONTRADICTION"),
                        scope_difference=item.get("scope_difference", ""),
                        timeframe_a=item.get("timeframe_a", ""),
                        timeframe_b=item.get("timeframe_b", ""),
                    )
                )
            return results

        except Exception as e:
            logger.warning(f"Contradiction detection failed: {e}. Returning empty contradictions list.")
            return []
