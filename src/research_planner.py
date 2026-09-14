"""
Research Planner Agent for Agentic Research PRO.
Converts a broad user research topic into a structured ResearchPlan with
focused sub-questions, key research dimensions, and targeted search queries.
Uses GPT-4o with strict budget limits and deterministic fallback.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional, Any
from openai import OpenAI
from src.config import ResearchConfig, get_research_config, LLM_MODEL

logger = logging.getLogger(__name__)


@dataclass
class ResearchPlan:
    """Structured plan for guiding the research process."""
    main_question: str
    sub_questions: List[str] = field(default_factory=list)
    search_queries: List[str] = field(default_factory=list)
    research_dimensions: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "main_question": self.main_question,
            "sub_questions": self.sub_questions,
            "search_queries": self.search_queries,
            "research_dimensions": self.research_dimensions,
        }


def _create_fallback_plan(topic: str, max_queries: int) -> ResearchPlan:
    """Deterministic fallback plan when LLM is disabled or unavailable."""
    queries = [topic]
    if max_queries >= 3:
        queries.extend([f"{topic} key developments", f"{topic} challenges and outlook"])
    if max_queries >= 6:
        queries.extend([
            f"{topic} market analysis",
            f"{topic} regulations and policies",
            f"{topic} future projections",
        ])
    queries = queries[:max_queries]

    return ResearchPlan(
        main_question=f"What is the current status and future outlook of {topic}?",
        sub_questions=[
            f"What are the core fundamentals and recent trends in {topic}?",
            f"What are the primary challenges and opportunities associated with {topic}?",
            f"What are the future projections for {topic}?",
        ],
        search_queries=queries,
        research_dimensions=["Fundamentals", "Trends & Challenges", "Future Outlook"],
    )


from src.llm import LLMProvider, get_llm_provider, OpenAICompatibleClientAdapter


class ResearchPlanner:
    """Agent that plans research scope and generates optimized search queries."""

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
        """Retain for legacy test inspections."""
        if self.client is None:
            self.client = OpenAI()
        return self.client

    def plan_research(self, topic: str, config: Optional[ResearchConfig] = None) -> ResearchPlan:
        """
        Generate a structured ResearchPlan.
        For QUICK depth (planning disabled), uses deterministic plan to save LLM budget.
        For STANDARD/DEEP, uses primary reasoning LLM to decompose topic.
        """
        if config is None:
            config = get_research_config("STANDARD")

        clean_topic = topic.strip()
        if not clean_topic:
            return _create_fallback_plan("Research Topic", config.max_queries)

        # Cost-aware optimization: if planning is disabled, skip LLM call entirely
        if not config.enable_planning:
            logger.info(f"Planning disabled in config ({config.name}). Using minimal deterministic plan.")
            return _create_fallback_plan(clean_topic, config.max_queries)

        query_count = min(config.max_queries, 8)

        prompt = f"""
You are a senior research analyst. Decompose the following research topic into a rigorous research plan.

TOPIC: {clean_topic}
TARGET QUERY COUNT: Exactly {query_count} distinct, highly specific search queries.

Generate a JSON object with EXACTLY these keys:
{{
  "main_question": "One comprehensive overarching research question",
  "sub_questions": [
    "Sub-question 1",
    "Sub-question 2",
    "Sub-question 3"
  ],
  "research_dimensions": [
    "Dimension 1 (e.g., Technological Innovation)",
    "Dimension 2 (e.g., Economic & Market Impact)",
    "Dimension 3 (e.g., Regulatory & Policy Landscape)"
  ],
  "search_queries": [
    "Query 1 (focused for search engine)",
    "Query 2",
    ... exactly {query_count} queries
  ]
}}

Guidelines:
- Search queries must be distinct, factual, search-engine-friendly, without boolean operators.
- No duplicate or overlapping queries.
- Return ONLY valid JSON.
"""

        try:
            provider = self._get_provider()
            data = provider.generate_structured(
                messages=[
                    {"role": "system", "content": "You are a research planning agent that responds strictly in valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                operation="research_planning",
            )

            main_q = data.get("main_question", f"Comprehensive analysis of {clean_topic}")
            sub_qs = data.get("sub_questions", [])
            dims = data.get("research_dimensions", [])
            queries = data.get("search_queries", [])

            # Enforce non-empty and bounded queries
            if not queries:
                queries = [clean_topic]
            queries = queries[:config.max_queries]

            # Deduplicate while preserving order
            unique_queries = []
            seen = set()
            for q in queries:
                q_norm = q.strip().lower()
                if q_norm and q_norm not in seen:
                    seen.add(q_norm)
                    unique_queries.append(q.strip())

            return ResearchPlan(
                main_question=main_q,
                sub_questions=sub_qs or [f"What are key aspects of {clean_topic}?"],
                search_queries=unique_queries or [clean_topic],
                research_dimensions=dims or ["Overview", "Key Factors", "Outlook"],
            )

        except Exception as e:
            logger.warning(f"Research planner LLM call failed: {e}. Falling back to deterministic plan.")
            return _create_fallback_plan(clean_topic, config.max_queries)
