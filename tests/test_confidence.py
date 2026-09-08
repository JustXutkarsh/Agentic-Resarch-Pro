"""Unit tests for src/confidence.py"""
import pytest
from src.confidence import (
    calculate_research_confidence,
    ResearchConfidence,
    LIMITATIONS_DISCLAIMER,
)
from src.claim_verifier import ClaimVerification
from src.contradiction_detector import Contradiction


def test_calculate_research_confidence_weights_and_bounds():
    accepted_sources = [
        {"url": "https://nature.com/article1", "source_score": 0.90},
        {"url": "https://energy.gov/article2", "source_score": 0.80},
    ]
    dimension_coverage = {"Technology": 0.80, "Economics": 0.70}
    claims = [
        ClaimVerification(
            claim="Claim 1",
            support_label="Strongly Supported",
            support_score=1.0,
            reasoning="Exact match",
        ),
        ClaimVerification(
            claim="Claim 2",
            support_label="Supported",
            support_score=0.85,
            reasoning="Supported",
        ),
    ]
    contradictions = []

    conf = calculate_research_confidence(
        accepted_sources=accepted_sources,
        dimension_coverage=dimension_coverage,
        claims=claims,
        contradictions=contradictions,
        iterations_completed=2,
        max_iterations=2,
        target_sources=2,
    )

    assert isinstance(conf, ResearchConfidence)
    assert 0.0 <= conf.overall_score <= 100.0
    assert conf.source_quality == 85.0
    assert conf.evidence_coverage == 75.0
    assert conf.claim_support == 92.5
    assert conf.source_agreement == 100.0
    assert conf.research_completeness == 100.0
    assert conf.limitations == LIMITATIONS_DISCLAIMER
    assert len(conf.explanation) > 0


def test_contradictions_lower_agreement():
    accepted_sources = [{"source_score": 0.80}]
    dimension_coverage = {"A": 0.80}
    claims = []

    conf_clean = calculate_research_confidence(
        accepted_sources, dimension_coverage, claims, contradictions=[],
        iterations_completed=1, max_iterations=1,
    )
    conf_with_contra = calculate_research_confidence(
        accepted_sources, dimension_coverage, claims,
        contradictions=[
            Contradiction(topic="T", perspective_a="A", perspective_b="B"),
            Contradiction(topic="T2", perspective_a="A2", perspective_b="B2"),
        ],
        iterations_completed=1, max_iterations=1,
    )

    assert conf_clean.source_agreement > conf_with_contra.source_agreement
    assert conf_clean.overall_score > conf_with_contra.overall_score


def test_confidence_explanation_identifies_weaknesses():
    accepted_sources = [{"source_score": 0.30}]  # low source quality
    dimension_coverage = {"A": 0.20}  # low coverage
    claims = [ClaimVerification(claim="C", support_label="Unsupported", support_score=0.1, reasoning="None")]

    conf = calculate_research_confidence(
        accepted_sources, dimension_coverage, claims, contradictions=[],
        iterations_completed=1, max_iterations=3, target_sources=10,
    )

    assert "constrained by" in conf.explanation
