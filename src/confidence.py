"""
Research Confidence Engine for Agentic Research PRO.
Computes an explainable, multi-component confidence heuristic (0-100) combining:
- Source Quality (25%)
- Evidence Coverage (20%)
- Claim Support (25%)
- Source Agreement (15%)
- Research Completeness (15%)

Generates algorithmic plain-English explanations without additional LLM API overhead,
and explicitly attaches scientific limitations disclaimer.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from src.claim_verifier import ClaimVerification
from src.contradiction_detector import Contradiction

LIMITATIONS_DISCLAIMER = (
    "Research Confidence is a system-generated heuristic based on evidence coverage, "
    "source prioritization, claim support, source agreement, and research completeness. "
    "It does not represent objective scientific certainty or independently verified truth."
)


@dataclass
class ResearchConfidence:
    """Detailed confidence breakdown and explainability report."""
    overall_score: float
    source_quality: float
    evidence_coverage: float
    claim_support: float
    source_agreement: float
    research_completeness: float
    explanation: str
    limitations: str = LIMITATIONS_DISCLAIMER

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": round(self.overall_score, 1),
            "source_quality": round(self.source_quality, 1),
            "evidence_coverage": round(self.evidence_coverage, 1),
            "claim_support": round(self.claim_support, 1),
            "source_agreement": round(self.source_agreement, 1),
            "research_completeness": round(self.research_completeness, 1),
            "explanation": self.explanation,
            "limitations": self.limitations,
        }


def _generate_explanation(
    scores: Dict[str, float],
    weaknesses: List[str],
    strengths: List[str],
) -> str:
    """Algorithmically produce a coherent summary of why the score was assigned."""
    overall = scores["overall"]
    if overall >= 85:
        tier = "High confidence"
    elif overall >= 70:
        tier = "Moderate-to-high confidence"
    elif overall >= 55:
        tier = "Moderate confidence"
    else:
        tier = "Preliminary confidence"

    strength_str = f"Strong grounding in {', '.join(strengths)}." if strengths else ""
    weakness_str = f"The score is primarily constrained by {', '.join(weaknesses)}." if weaknesses else "No major constraints detected across evaluation factors."

    return f"{tier} ({int(overall)}/100). {strength_str} {weakness_str}".strip()


def calculate_research_confidence(
    accepted_sources: List[Dict[str, Any]],
    dimension_coverage: Dict[str, float],
    claims: List[ClaimVerification],
    contradictions: List[Contradiction],
    iterations_completed: int,
    max_iterations: int,
    target_sources: int = 10,
) -> ResearchConfidence:
    """
    Synthesize research metrics into an explainable ResearchConfidence instance.
    All component scores are normalized to 0 - 100.
    """
    # 1. Source Quality (25%)
    if accepted_sources:
        avg_source_score = sum(s.get("source_score", 0.5) for s in accepted_sources) / len(accepted_sources)
        source_quality = min(100.0, max(10.0, avg_source_score * 100.0))
    else:
        source_quality = 30.0

    # 2. Evidence Coverage (20%)
    if dimension_coverage:
        avg_cov = sum(dimension_coverage.values()) / len(dimension_coverage)
        evidence_coverage = min(100.0, max(10.0, avg_cov * 100.0))
    else:
        evidence_coverage = 40.0

    # 3. Claim Support (25%)
    if claims:
        avg_claim = sum(c.support_score for c in claims) / len(claims)
        claim_support = min(100.0, max(10.0, avg_claim * 100.0))
    else:
        claim_support = 70.0

    # 4. Source Agreement (15%)
    # Deduct 12 points per contradiction, bounded between 40.0 and 100.0
    contradiction_count = len(contradictions)
    source_agreement = max(40.0, 100.0 - (contradiction_count * 12.0))

    # 5. Research Completeness (15%)
    iter_ratio = min(1.0, iterations_completed / max(1, max_iterations))
    source_ratio = min(1.0, len(accepted_sources) / max(1, target_sources))
    research_completeness = (0.5 * iter_ratio + 0.5 * source_ratio) * 100.0

    # Overall Weighted Formula:
    # 25% Source Quality + 20% Evidence Coverage + 25% Claim Support + 15% Agreement + 15% Completeness
    overall_score = round(
        0.25 * source_quality +
        0.20 * evidence_coverage +
        0.25 * claim_support +
        0.15 * source_agreement +
        0.15 * research_completeness,
        2
    )

    source_quality = round(source_quality, 2)
    evidence_coverage = round(evidence_coverage, 2)
    claim_support = round(claim_support, 2)
    source_agreement = round(source_agreement, 2)
    research_completeness = round(research_completeness, 2)

    component_scores = {
        "Source Quality": source_quality,
        "Evidence Coverage": evidence_coverage,
        "Claim Support": claim_support,
        "Source Agreement": source_agreement,
        "Research Completeness": research_completeness,
    }

    strengths = [name.lower() for name, val in component_scores.items() if val >= 80]
    weaknesses = [name.lower() for name, val in component_scores.items() if val < 65]

    explanation = _generate_explanation({"overall": overall_score}, weaknesses, strengths)

    return ResearchConfidence(
        overall_score=overall_score,
        source_quality=source_quality,
        evidence_coverage=evidence_coverage,
        claim_support=claim_support,
        source_agreement=source_agreement,
        research_completeness=research_completeness,
        explanation=explanation,
        limitations=LIMITATIONS_DISCLAIMER,
    )
