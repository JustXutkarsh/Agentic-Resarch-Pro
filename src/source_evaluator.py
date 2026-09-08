"""
Source Evaluator Module for Agentic Research PRO.
Evaluates and prioritizes web sources using a multi-factor heuristic:
- Authority (30%)
- Semantic Relevance (25%)
- Recency (20%)
- Evidence Quality (15%)
- Institutional Reputation (10%)

Uses neutral fallback for missing metadata and labels scores as
'Source Priority Score' rather than 'objective truth'.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from urllib.parse import urlparse
from src.embedder import embed_text
from src.hallucination import cosine_similarity


@dataclass
class SourceEvaluation:
    """Detailed multi-factor evaluation scores for a source."""
    authority_score: float
    relevance_score: float
    recency_score: float
    evidence_quality_score: float
    reputation_score: float
    overall_score: float
    recency_unknown: bool = False
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "authority_score": round(self.authority_score, 2),
            "relevance_score": round(self.relevance_score, 2),
            "recency_score": round(self.recency_score, 2),
            "evidence_quality_score": round(self.evidence_quality_score, 2),
            "reputation_score": round(self.reputation_score, 2),
            "overall_score": round(self.overall_score, 2),
            "recency_unknown": self.recency_unknown,
            "explanation": self.explanation,
        }


# Domain heuristic patterns
HIGH_AUTHORITY_DOMAINS = {
    ".gov", ".mil", ".edu", ".ac.uk", ".gov.uk", ".gov.in", ".europa.eu"
}

ESTABLISHED_ACADEMIC_ORGS = {
    "arxiv.org", "nature.com", "science.org", "sciencedirect.com",
    "ieee.org", "nih.gov", "ncbi.nlm.nih.gov", "who.int", "cdc.gov",
    "mit.edu", "stanford.edu", "harvard.edu", "ox.ac.uk", "cam.ac.uk",
    "springer.com", "wiley.com", "frontiersin.org", "cell.com"
}

REPUTABLE_NEWS_ORGS = {
    "reuters.com", "bloomberg.com", "apnews.com", "ft.com", "wsj.com",
    "bbc.com", "nytimes.com", "technologyreview.com", "economist.com"
}


def evaluate_authority_and_reputation(url: str) -> Tuple[float, float, str]:
    """
    Score authority and institutional reputation based on domain patterns.
    Returns (authority_score, reputation_score, label).
    """
    try:
        domain = urlparse(url).netloc.lower()
    except Exception:
        domain = ""

    # Check top-level domain
    for suffix in HIGH_AUTHORITY_DOMAINS:
        if domain.endswith(suffix):
            return 0.95, 0.95, "Official Government / Academic Domain"

    # Check known scientific/academic institutions
    for org in ESTABLISHED_ACADEMIC_ORGS:
        if org in domain:
            return 0.92, 0.95, "Peer-Reviewed / Academic Publication"

    # Check major news organizations
    for news in REPUTABLE_NEWS_ORGS:
        if news in domain:
            return 0.80, 0.85, "Recognized Journalism / News Organization"

    # Standard commercial / organization domain
    if domain.endswith(".org"):
        return 0.70, 0.70, "Established Non-Profit / Organization"

    # Default commercial domain
    return 0.55, 0.55, "General Web Publisher"


def evaluate_recency(published_date: Optional[str]) -> Tuple[float, bool]:
    """
    Score recency based on publication date.
    Returns (recency_score, recency_unknown).
    """
    if not published_date:
        # Neutral fallback score: 0.5 without heavy penalty
        return 0.50, True

    try:
        # Extract year
        year_match = re.search(r"\b(20\d{2}|19\d{2})\b", str(published_date))
        if not year_match:
            return 0.50, True

        year = int(year_match.group(1))
        current_year = datetime.now().year

        diff = current_year - year
        if diff <= 1:
            return 0.95, False
        elif diff <= 3:
            return 0.80, False
        elif diff <= 5:
            return 0.65, False
        else:
            return 0.45, False

    except Exception:
        return 0.50, True


def evaluate_evidence_quality(text: str) -> float:
    """
    Score quality of content heuristics:
    - Text length
    - Presence of numerical/statistical data
    - Presence of citations/technical terms
    """
    if not text:
        return 0.2

    length = len(text)
    length_score = min(1.0, length / 400.0)

    # Check for quantitative data (percentages, currencies, numbers)
    has_stats = 1.0 if re.search(r"(\d+[\.,]?\d*%)|(\$\d+)|(\b\d{2,}\b)", text) else 0.5

    # Check for structured indicators (studies, researchers, according to)
    indicators = ["study", "research", "percent", "report", "analysis", "data", "found", "according to"]
    matched = sum(1 for ind in indicators if ind in text.lower())
    struct_score = min(1.0, matched / 3.0)

    return 0.4 * length_score + 0.3 * has_stats + 0.3 * struct_score


def evaluate_source(
    source: Dict[str, Any],
    topic: str,
    topic_embedding: Optional[List[float]] = None,
) -> SourceEvaluation:
    """
    Compute comprehensive Source Priority Score for a single source.
    """
    url = source.get("url", "")
    title = source.get("title", "")
    snippet = source.get("snippet", "")
    published_date = source.get("published_date")

    # 1. Authority and Reputation
    auth_score, rep_score, label = evaluate_authority_and_reputation(url)

    # 2. Semantic Relevance (using Hugging Face embeddings)
    if topic_embedding is None:
        topic_embedding = embed_text(topic)

    text_to_compare = f"{title}. {snippet}"
    content_embedding = embed_text(text_to_compare)
    relevance_raw = cosine_similarity(topic_embedding, content_embedding)
    relevance_score = max(0.0, min(1.0, (relevance_raw + 1.0) / 2.0))

    # 3. Recency
    recency_score, recency_unknown = evaluate_recency(published_date)

    # 4. Evidence Quality
    evidence_quality = evaluate_evidence_quality(snippet)

    # Overall Weighted Priority Score:
    # 30% Authority + 25% Relevance + 20% Recency + 15% Evidence Quality + 10% Reputation
    overall_score = (
        0.30 * auth_score +
        0.25 * relevance_score +
        0.20 * recency_score +
        0.15 * evidence_quality +
        0.10 * rep_score
    )

    explanation = f"{label} (Relevance: {int(relevance_score*100)}%, Quality: {int(evidence_quality*100)}%)"

    return SourceEvaluation(
        authority_score=auth_score,
        relevance_score=relevance_score,
        recency_score=recency_score,
        evidence_quality_score=evidence_quality,
        reputation_score=rep_score,
        overall_score=overall_score,
        recency_unknown=recency_unknown,
        explanation=explanation,
    )


def evaluate_and_filter_sources(
    sources: List[Dict[str, Any]],
    topic: str,
    quality_threshold: float = 0.45,
    min_sources_to_retain: int = 3,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Evaluate all sources, attach evaluation data, and partition into accepted and rejected.
    Ensures at least `min_sources_to_retain` are accepted if available.
    """
    if not sources:
        return [], []

    topic_embedding = embed_text(topic)
    evaluated_sources = []

    for src in sources:
        evaluation = evaluate_source(src, topic, topic_embedding=topic_embedding)
        src_with_eval = dict(src)
        src_with_eval["evaluation"] = evaluation.to_dict()
        src_with_eval["source_score"] = evaluation.overall_score
        evaluated_sources.append(src_with_eval)

    # Sort descending by priority score
    evaluated_sources.sort(key=lambda s: s["source_score"], reverse=True)

    accepted = [s for s in evaluated_sources if s["source_score"] >= quality_threshold]
    rejected = [s for s in evaluated_sources if s["source_score"] < quality_threshold]

    # If too few sources passed the threshold, retain top sources so pipeline doesn't stall
    if len(accepted) < min_sources_to_retain and evaluated_sources:
        needed = min(min_sources_to_retain, len(evaluated_sources))
        accepted = evaluated_sources[:needed]
        rejected = evaluated_sources[needed:]

    return accepted, rejected
