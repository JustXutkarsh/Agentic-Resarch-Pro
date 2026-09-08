"""Unit tests for src/pdfgen.py"""
import os
import pytest
from src.pdfgen import generate_research_pdf, generate_pdf
from src.research_orchestrator import ResearchResult, ResearchState
from src.config import get_research_config
from src.claim_verifier import ClaimVerification
from src.contradiction_detector import Contradiction
from src.confidence import ResearchConfidence
from src.research_metrics import ResearchMetrics


def test_generate_research_pdf_success(tmp_path):
    output_pdf = str(tmp_path / "test_research.pdf")
    config = get_research_config("DEEP")

    metrics = ResearchMetrics(
        session_id="test_sess_pdf",
        topic="AI in Medicine & Diagnostics",
        depth="DEEP",
    )
    metrics.generated_queries = 6
    metrics.total_sources_found = 18
    metrics.sources_accepted = 12
    metrics.total_chunks = 45
    metrics.retrieved_evidence_chunks = 30
    metrics.execution_time_seconds = 18.5
    metrics.finalize()

    claims = [
        ClaimVerification(
            claim="Deep neural networks achieved 96% AUC in diagnostic imaging trials.",
            support_label="Strongly Supported",
            support_score=1.0,
            reasoning="Directly evidenced in clinical trials.",
            evidence_chunks=["Evidence text"],
            source_urls=["https://nature.com/medicine"],
            source_count=1,
        )
    ]

    contradictions = [
        Contradiction(
            topic="Clinical Deployment Timeline",
            perspective_a="Hospitals predict widespread deployment by 2026.",
            perspective_b="Regulatory audits report compliance hurdles delaying rollout to 2029.",
            supporting_sources_a=["https://hospital.org"],
            supporting_sources_b=["https://fda.gov"],
            resolution="Differences reflect variance between private clinics and federally regulated centers.",
        )
    ]

    confidence = ResearchConfidence(
        overall_score=86.5,
        source_quality=90.0,
        evidence_coverage=85.0,
        claim_support=92.0,
        source_agreement=85.0,
        research_completeness=90.0,
        explanation="High confidence (86/100). Strong grounding across medical sources.",
    )

    state = ResearchState(
        session_id="test_sess_pdf",
        topic="AI in Medicine & Diagnostics",
        depth="DEEP",
        config=config,
        report=(
            "# Research Report: AI in Medicine\n\n"
            "## Executive Summary\n"
            "AI diagnostics have seen extensive progress in radiology & pathology.\n\n"
            "## Key Findings & Strategic Insights\n"
            "- **Accuracy**: Model sensitivity exceeded 95%.\n\n"
            "## Trade-offs & Comparative Analysis\n"
            "### Strengths & Opportunities (Pros)\n"
            "- Fast triage.\n\n"
            "### Limitations & Risks (Cons)\n"
            "- Liability concerns.\n\n"
            "## Source Citations & References\n"
            "- https://nature.com/medicine"
        ),
        accepted_sources=[
            {
                "url": "https://nature.com/medicine",
                "title": "Nature Medicine AI Study",
                "source_score": 0.94,
            }
        ],
        claims=claims,
        contradictions=contradictions,
        confidence=confidence,
        metrics=metrics,
    )

    result = ResearchResult(state=state)

    path = generate_research_pdf(result, output_path=output_pdf)
    assert os.path.exists(path)
    assert os.path.getsize(path) > 2000


def test_legacy_generate_pdf_wrapper(tmp_path):
    output_pdf = str(tmp_path / "test_legacy.pdf")
    path = generate_pdf(
        summary="Test summary",
        insights=["Insight 1"],
        pros_cons={"pros": ["Pro 1"], "cons": ["Con 1"]},
        citations=["https://example.com"],
        output_path=output_pdf,
    )
    assert os.path.exists(path)
    assert os.path.getsize(path) > 1000
