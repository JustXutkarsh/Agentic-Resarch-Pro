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
from src.embedder import embed_text
from src.hallucination import cosine_similarity

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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "perspective_a": self.perspective_a,
            "perspective_b": self.perspective_b,
            "supporting_sources_a": self.supporting_sources_a,
            "supporting_sources_b": self.supporting_sources_b,
            "resolution": self.resolution,
        }


def _group_chunks_by_dimension(
    dimensions: List[str],
    evidence_chunks: List[Dict[str, Any]],
    similarity_threshold: float = 0.30,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Cluster evidence chunks into research dimensions based on semantic similarity.
    """
    grouped: Dict[str, List[Dict[str, Any]]] = {dim: [] for dim in dimensions}
    if not dimensions or not evidence_chunks:
        return grouped

    dim_vectors = {dim: embed_text(dim) for dim in dimensions}

    for chunk_dict in evidence_chunks:
        text = chunk_dict.get("text", "")
        if not text:
            continue
        chunk_vec = embed_text(text[:300])

        for dim, dim_vec in dim_vectors.items():
            sim = cosine_similarity(dim_vec, chunk_vec)
            if sim >= similarity_threshold:
                grouped[dim].append(chunk_dict)

    return grouped


class ContradictionDetector:
    """Identifies nuanced disagreements and opposing evidence across research dimensions."""

    def __init__(self, client: Optional[OpenAI] = None):
        self.client = client

    def _get_client(self) -> OpenAI:
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
        Detect contradictions across evidence dimensions.
        Only runs when enable_contradiction_detection is True (typically DEEP mode).
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
            return []

        # Prepare payload for batched GPT-4o analysis
        analysis_payload = []
        for dim in candidate_dimensions:
            chunks = grouped[dim][:4]
            snippets = [
                {
                    "text": c.get("text", "")[:350],
                    "url": c.get("metadata", {}).get("source_url", "source"),
                }
                for c in chunks
            ]
            analysis_payload.append({
                "dimension": dim,
                "evidence": snippets,
            })

        prompt = f"""
You are an objective academic peer reviewer. Analyze whether the following evidence clusters contain GENUINE empirical contradictions, conflicting estimates, or competing viewpoints.

TOPIC: {topic}

EVIDENCE BY DIMENSION:
{json.dumps(analysis_payload, indent=2)}

INSTRUCTIONS:
- Do NOT force contradictions if the evidence is broadly in consensus or merely complementary.
- Only identify REAL divergences (e.g. conflicting dates/costs, positive vs negative environmental impact, optimistic vs pessimistic forecasts).
- If no genuine contradiction exists for a dimension, DO NOT include it.
- Return JSON strictly in this format:
{{
  "contradictions": [
    {{
      "topic": "Dimension name or sub-topic",
      "perspective_a": "First distinct perspective or finding",
      "perspective_b": "Directly opposing or conflicting perspective",
      "supporting_sources_a": ["URL or source A"],
      "supporting_sources_b": ["URL or source B"],
      "resolution": "Synthesized reconciliation or explanation of why estimates differ (e.g., methodology differences, different study years)"
    }}
  ]
}}
"""

        try:
            client = self._get_client()
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an objective academic research reviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content or "{}"
            data = json.loads(raw).get("contradictions", [])

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
                    )
                )
            return results

        except Exception as e:
            logger.warning(f"Contradiction detection failed: {e}. Returning empty contradictions list.")
            return []
