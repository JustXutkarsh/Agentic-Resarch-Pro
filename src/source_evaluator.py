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
from src.embedder import embed_text, embed_query, is_embedding_model_loaded
from src.hallucination import cosine_similarity


def compute_lexical_relevance(query: str, text: str) -> float:
    """
    Fast, zero-memory relevance scoring based on query term coverage and token overlap.
    Used during initial source filtering to avoid premature loading of heavy PyTorch models.
    """
    if not query or not text:
        return 0.5
    query_words = re.findall(r"\w+", query.lower())
    stop_words = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with", "is", "are", "was", "were", "by"}
    meaningful_query = [w for w in query_words if w not in stop_words] or query_words

    text_words = set(re.findall(r"\w+", text.lower()))
    if not meaningful_query:
        return 0.5

    matches = sum(1 for w in meaningful_query if w in text_words)
    overlap_ratio = matches / len(meaningful_query)

    phrase_bonus = 0.15 if query.lower().strip() in text.lower() else 0.0
    return max(0.0, min(1.0, 0.40 + (overlap_ratio * 0.45) + phrase_bonus))


@dataclass
class SourceEvaluation:
    """
    Multi-factor source quality evaluation.
    Treated as a calibrated source-quality signal rather than mathematical certainty.
    """
    authority_score: float
    relevance_score: float
    recency_score: float
    evidence_quality_score: float
    reputation_score: float
    overall_score: float
    recency_unknown: bool = False
    explanation: str = ""
    tier: int = 4  # 1: Peer-reviewed/Gov/Standards, 2: University/Preprint/Corp Tech, 3: Tech Journalism/Industry, 4: Commercial/Blog
    source_type: str = "commercial_blog"
    is_corporate_roadmap: bool = False
    signal_confidence: str = "Moderate"

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
            "tier": self.tier,
            "source_type": self.source_type,
            "is_corporate_roadmap": self.is_corporate_roadmap,
            "signal_confidence": self.signal_confidence,
        }


# ==============================================================================
# 4-TIER SOURCE AUTHORITY HIERARCHY (Source-Quality Signal)
# ==============================================================================

# Tier 1: Peer-reviewed academic literature, Government publications/labs, Official standards bodies
TIER_1_GOV_LABS = {
    ".gov", ".mil", ".gov.uk", ".gov.in", ".europa.eu", "nih.gov", "ncbi.nlm.nih.gov",
    "nist.gov", "energy.gov", "who.int", "cdc.gov", "lanl.gov", "ornl.gov", "sandia.gov"
}

TIER_1_PEER_REVIEWED = {
    "nature.com", "science.org", "sciencedirect.com", "ieee.org", "springer.com",
    "wiley.com", "cell.com", "pnas.org", "aps.org", "acm.org", "iop.org", "oup.com"
}

TIER_1_STANDARDS_BODIES = {
    "iso.org", "ietf.org", "w3.org", "itu.int", "bipm.org"
}

# Tier 2: University/research institution publications, High-quality preprints (arXiv), Official corporate technical research
TIER_2_UNIVERSITIES = {
    ".edu", ".ac.uk", "mit.edu", "stanford.edu", "harvard.edu", "ox.ac.uk",
    "cam.ac.uk", "caltech.edu", "princeton.edu", "uchicago.edu", "berkeley.edu"
}

TIER_2_PREPRINTS = {
    "arxiv.org", "biorxiv.org", "medrxiv.org", "chemrxiv.org", "techrxiv.org", "ssrn.com"
}

TIER_2_CORPORATE_TECHNICAL = {
    "research.ibm.com", "ibm.com", "research.google", "blog.google/technology",
    "microsoft.com/en-us/research", "meta.com/research", "amazon.science",
    "openai.com/research", "anthropic.com/research", "bell-labs.com", "intel.com/research"
}

# Tier 3: Reputable technical journalism, Established industry publications
TIER_3_TECH_JOURNALISM = {
    "technologyreview.com", "arstechnica.com", "ieeespectrum.org", "quantamagazine.org",
    "wired.com", "spectrum.ieee.org"
}

TIER_3_INDUSTRY_NEWS = {
    "reuters.com", "bloomberg.com", "apnews.com", "ft.com", "wsj.com",
    "bbc.com", "nytimes.com", "economist.com"
}


def evaluate_authority_and_reputation(url: str, detailed: bool = False):
    """
    Evaluates authority and institutional reputation based on 4-tier hierarchy.
    Treats authority as a source-quality signal, not an immutable truth.
    If detailed=True, returns: (authority_score, reputation_score, label, tier, source_type, is_corporate_roadmap)
    If detailed=False (default for backward-compatibility): returns: (authority_score, reputation_score, label)
    """
    try:
        domain = urlparse(url).netloc.lower()
        path = urlparse(url).path.lower()
    except Exception:
        domain = ""
        path = ""

    # Flag corporate roadmaps / announcements
    is_roadmap = any(kw in f"{domain}{path}" for kw in ["roadmap", "announcement", "press-release", "newsroom"])

    def _pack(auth, rep, lbl, tr, st, rm):
        if detailed:
            return auth, rep, lbl, tr, st, rm
        return auth, rep, lbl

    # -------------------------------------------------------------
    # TIER 1: Peer-reviewed literature, Government labs, Standards
    # -------------------------------------------------------------
    for gov in TIER_1_GOV_LABS:
        if domain.endswith(gov) or gov in domain:
            return _pack(0.95, 0.95, "Tier 1: Government Lab / Official Body", 1, "government_lab", False)

    for peer in TIER_1_PEER_REVIEWED:
        if peer in domain:
            return _pack(0.95, 0.95, "Tier 1: Peer-Reviewed Academic Literature", 1, "peer_reviewed_literature", False)

    for std in TIER_1_STANDARDS_BODIES:
        if std in domain:
            return _pack(0.95, 0.95, "Tier 1: Official Standards Body", 1, "standards_body", False)

    # -------------------------------------------------------------
    # TIER 2: Universities, High-Quality Preprints (arXiv), Corporate Tech
    # -------------------------------------------------------------
    for edu in TIER_2_UNIVERSITIES:
        if domain.endswith(edu) or edu in domain:
            return _pack(0.90, 0.92, "Tier 2: University / Research Institution", 2, "university_research", False)

    for prep in TIER_2_PREPRINTS:
        if prep in domain:
            return _pack(0.85, 0.88, "Tier 2: High-Quality Preprint (arXiv/bioRxiv)", 2, "academic_preprint", False)

    for corp in TIER_2_CORPORATE_TECHNICAL:
        if corp in domain:
            label = "Tier 2: Corporate Technical Roadmap" if is_roadmap else "Tier 2: Official Corporate Technical Research"
            return _pack(0.82, 0.85, label, 2, "corporate_technical_publication", is_roadmap)

    # -------------------------------------------------------------
    # TIER 3: Technical Journalism & Established Industry Publications
    # -------------------------------------------------------------
    for tech_j in TIER_3_TECH_JOURNALISM:
        if tech_j in domain:
            return _pack(0.80, 0.85, "Tier 3: Reputable Technical Journalism", 3, "technical_journalism", False)

    for news in TIER_3_INDUSTRY_NEWS:
        if news in domain:
            return _pack(0.80, 0.85, "Tier 3: Established Industry Publication", 3, "industry_publication", False)

    if domain.endswith(".org"):
        return _pack(0.70, 0.72, "Tier 3: Established Non-Profit Organization", 3, "industry_publication", False)

    # -------------------------------------------------------------
    # TIER 4: Commercial Blogs, Marketing Content, Low-Authority Secondary
    # -------------------------------------------------------------
    return _pack(0.50, 0.50, "Tier 4: Commercial / Secondary Source", 4, "commercial_blog", is_roadmap)



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

    # 1. Authority and Reputation with 4-tier calibration
    auth_score, rep_score, label, tier, source_type, is_roadmap = evaluate_authority_and_reputation(url, detailed=True)

    # 2. Semantic Relevance (uses embeddings if already in memory; zero-memory lexical scoring during pre-acquisition)
    text_to_compare = f"{title}. {snippet}"
    if topic_embedding is not None:
        content_embedding = embed_text(text_to_compare, is_query=False)
        relevance_raw = cosine_similarity(topic_embedding, content_embedding)
        relevance_score = max(0.0, min(1.0, (relevance_raw + 1.0) / 2.0))
    elif is_embedding_model_loaded():
        topic_embedding = embed_query(topic)
        content_embedding = embed_text(text_to_compare, is_query=False)
        relevance_raw = cosine_similarity(topic_embedding, content_embedding)
        relevance_score = max(0.0, min(1.0, (relevance_raw + 1.0) / 2.0))
    else:
        relevance_score = compute_lexical_relevance(topic, text_to_compare)

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

    signal_confidence = (
        "Tier 1: High Signal (Peer-Reviewed / Gov / Standards)" if tier == 1 else
        "Tier 2: High Signal (University / Preprint / Corp Tech)" if tier == 2 else
        "Tier 3: Moderate Signal (Tech Journalism / Industry)" if tier == 3 else
        "Tier 4: Secondary Signal (Commercial / Blog)"
    )

    return SourceEvaluation(
        authority_score=auth_score,
        relevance_score=relevance_score,
        recency_score=recency_score,
        evidence_quality_score=evidence_quality,
        reputation_score=rep_score,
        overall_score=overall_score,
        recency_unknown=recency_unknown,
        explanation=explanation,
        tier=tier,
        source_type=source_type,
        is_corporate_roadmap=is_roadmap,
        signal_confidence=signal_confidence,
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

    topic_embedding = embed_query(topic) if is_embedding_model_loaded() else None
    evaluated_sources = []

    for src in sources:
        evaluation = evaluate_source(src, topic, topic_embedding=topic_embedding)
        src_with_eval = dict(src)
        src_with_eval["evaluation"] = evaluation.to_dict()
        src_with_eval["source_score"] = evaluation.overall_score
        src_with_eval["tier"] = evaluation.tier
        src_with_eval["source_type"] = evaluation.source_type
        src_with_eval["is_corporate_roadmap"] = evaluation.is_corporate_roadmap
        src_with_eval["signal_confidence"] = evaluation.signal_confidence
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
