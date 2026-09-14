"""
Research Gap Detector for Agentic Research PRO.
Identifies unexplored or low-coverage research dimensions using a two-tier approach:
1. Deterministic semantic embedding coverage scoring (zero LLM cost)
2. Targeted GPT-4o follow-up query formulation for genuinely missing dimensions
"""

import json
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from openai import OpenAI
from src.config import ResearchConfig, LLM_MODEL
from src.research_planner import ResearchPlan
from src.embedder import embed_text
from src.hallucination import cosine_similarity
from src.llm import LLMProvider, get_llm_provider, OpenAICompatibleClientAdapter

logger = logging.getLogger(__name__)


@dataclass
class ResearchGap:
    """Represents an identified coverage gap with an actionable query."""
    missing_dimension: str
    reason: str
    priority: str  # "High", "Medium", "Low"
    suggested_query: str
    coverage_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "missing_dimension": self.missing_dimension,
            "reason": self.reason,
            "priority": self.priority,
            "suggested_query": self.suggested_query,
            "coverage_score": round(self.coverage_score, 2),
        }


def compute_dimension_coverage(
    dimensions: List[str],
    evidence_chunks: List[str],
    coverage_threshold: float = 0.45,
) -> Dict[str, float]:
    """
    Deterministically score semantic coverage for each research dimension
    against retrieved evidence chunks using Hugging Face embeddings.
    Returns mapping: {dimension: coverage_score}
    """
    if not dimensions:
        return {}

    if not evidence_chunks:
        return {dim: 0.0 for dim in dimensions}

    # Embed evidence chunks
    chunk_embeddings = [embed_text(c[:500]) for c in evidence_chunks[:30]]

    coverage_map: Dict[str, float] = {}

    for dim in dimensions:
        dim_vec = embed_text(dim)
        similarities = [cosine_similarity(dim_vec, c_vec) for c_vec in chunk_embeddings]
        
        # Take the top 3 highest matches and average them
        similarities.sort(reverse=True)
        top_sims = similarities[:3]
        avg_sim = sum(top_sims) / len(top_sims) if top_sims else 0.0
        
        # Normalize score into [0.0, 1.0]
        normalized_score = max(0.0, min(1.0, (avg_sim + 1.0) / 2.0))
        coverage_map[dim] = normalized_score

    return coverage_map


class ResearchGapDetector:
    """Detects missing dimensions and formulates targeted follow-up research queries."""

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

    def detect_gaps(
        self,
        topic: str,
        plan: ResearchPlan,
        evidence_chunks: List[str],
        config: ResearchConfig,
        current_iteration: int = 1,
        coverage_threshold: float = 0.45,
    ) -> List[ResearchGap]:
        """
        Detect research gaps.
        Returns list of ResearchGap items.
        """
        # If gap detection is disabled in config, return empty list
        if not config.enable_gap_detection:
            logger.info("Gap detection is disabled for this research depth.")
            return []

        # If we have reached or exceeded max iterations, do not generate more gaps
        if current_iteration >= config.max_iterations:
            logger.info("Maximum research iterations reached. Halting gap detection.")
            return []

        dimensions = plan.research_dimensions or ["Key Aspects"]
        coverage_scores = compute_dimension_coverage(dimensions, evidence_chunks, coverage_threshold)

        low_coverage_dims = [
            dim for dim, score in coverage_scores.items() if score < coverage_threshold
        ]

        if not low_coverage_dims:
            logger.info("All research dimensions met the coverage threshold.")
            return []

        logger.info(f"Identified {len(low_coverage_dims)} low-coverage dimensions: {low_coverage_dims}")

        # If LLM calls are budgeted for gap analysis, use GPT-4o to formulate sharp queries
        if config.max_follow_up_gap_analyses > 0:
            return self._formulate_gaps_with_llm(topic, low_coverage_dims, coverage_scores)
        else:
            return self._formulate_gaps_deterministically(topic, low_coverage_dims, coverage_scores)

    def _formulate_gaps_deterministically(
        self,
        topic: str,
        low_coverage_dims: List[str],
        coverage_scores: Dict[str, float],
    ) -> List[ResearchGap]:
        """Formulate follow-up queries deterministically without LLM calls."""
        gaps = []
        for dim in low_coverage_dims:
            score = coverage_scores.get(dim, 0.0)
            priority = "High" if score < 0.30 else "Medium"
            query = f"{topic} {dim} details statistics"
            gaps.append(
                ResearchGap(
                    missing_dimension=dim,
                    reason=f"Dimension '{dim}' had low semantic coverage ({int(score*100)}%).",
                    priority=priority,
                    suggested_query=query,
                    coverage_score=score,
                )
            )
        return gaps

    def _formulate_gaps_with_llm(
        self,
        topic: str,
        low_coverage_dims: List[str],
        coverage_scores: Dict[str, float],
    ) -> List[ResearchGap]:
        """Formulate follow-up queries using a single batched GPT-4o call."""
        prompt = f"""
We are conducting research on: '{topic}'.
Our evidence retrieval found insufficient information for these specific dimensions:
{json.dumps(low_coverage_dims)}

For EACH low-coverage dimension, provide:
1. "reason": Brief 1-sentence explanation of what critical aspect is missing.
2. "priority": "High" or "Medium"
3. "suggested_query": One highly specific, search-engine-ready query to find facts for this dimension.

Return JSON strictly in this format:
{{
  "gaps": [
    {{
      "dimension": "Name of dimension",
      "reason": "Why it is missing or needed",
      "priority": "High",
      "suggested_query": "specific search query"
    }}
  ]
}}
"""
        try:
            provider = self._get_provider()
            data = provider.generate_structured(
                messages=[
                    {"role": "system", "content": "You are a research analyst identifying gaps in collected evidence."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                operation="gap_detection",
            )
            items = data.get("gaps", [])

            results = []
            for item in items:
                dim_name = item.get("dimension", low_coverage_dims[0])
                score = coverage_scores.get(dim_name, 0.35)
                results.append(
                    ResearchGap(
                        missing_dimension=dim_name,
                        reason=item.get("reason", "Dimension lacked sufficient evidence."),
                        priority=item.get("priority", "High"),
                        suggested_query=item.get("suggested_query", f"{topic} {dim_name}"),
                        coverage_score=score,
                    )
                )
            return results if results else self._formulate_gaps_deterministically(topic, low_coverage_dims, coverage_scores)

        except Exception as e:
            logger.warning(f"GPT-4o gap formulation failed: {e}. Using deterministic queries.")
            return self._formulate_gaps_deterministically(topic, low_coverage_dims, coverage_scores)
