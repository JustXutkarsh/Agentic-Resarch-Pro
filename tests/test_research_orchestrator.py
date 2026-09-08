"""Unit tests for src/research_orchestrator.py"""
from unittest.mock import MagicMock
import pytest
from src.research_planner import ResearchPlan
from src.scraper import ScrapedDocument
from src.claim_verifier import ClaimVerification
from src.research_orchestrator import ResearchOrchestrator, ResearchResult


def test_orchestrator_execution_flow_with_mocks():
    # 1. Setup Mock Sub-agents
    mock_planner = MagicMock()
    mock_planner.plan_research.return_value = ResearchPlan(
        main_question="What are the latest advances in solid-state batteries?",
        sub_questions=["What electrolytes are used?", "When will commercial adoption happen?"],
        search_queries=["solid-state battery electrolytes", "commercial solid state battery timeline"],
        research_dimensions=["Electrolytes", "Commercialization"],
    )

    mock_searcher = MagicMock()
    mock_searcher.search_multiple.return_value = [
        {
            "url": "https://nature.com/articles/solid-battery",
            "title": "Solid State Electrolytes",
            "snippet": "Sulfides and oxides show 25% ionic conductivity improvements.",
            "published_date": "2026-01-10",
            "search_query": "solid-state battery electrolytes",
            "research_iteration": 1,
        }
    ]

    mock_gap_detector = MagicMock()
    mock_gap_detector.detect_gaps.return_value = []

    mock_summarizer = MagicMock()
    mock_summarizer.summarize.return_value = (
        "# Research Report: Solid State Batteries\n\n"
        "## Executive Summary\nSolid state batteries are progressing rapidly.\n\n"
        "## Key Findings & Strategic Insights\n- **Electrolytes**: Sulfides demonstrate high conductivity.\n\n"
        "## Trade-offs & Comparative Analysis\n### Strengths & Opportunities (Pros)\n- High safety.\n\n"
        "### Limitations & Risks (Cons)\n- Manufacturing costs remain elevated.\n\n"
        "## Source Citations & References\n- https://nature.com/articles/solid-battery"
    )

    mock_claim_verifier = MagicMock()
    mock_claim_verifier.extract_claims.return_value = ["Sulfides demonstrate high ionic conductivity."]
    mock_claim_verifier.verify_claims_against_evidence.return_value = [
        ClaimVerification(
            claim="Sulfides demonstrate high ionic conductivity.",
            support_label="Strongly Supported",
            support_score=1.0,
            reasoning="Directly stated in laboratory tests.",
            evidence_chunks=["Sulfides and oxides show 25% ionic conductivity improvements."],
            source_urls=["https://nature.com/articles/solid-battery"],
            source_count=1,
        )
    ]

    mock_contra_detector = MagicMock()
    mock_contra_detector.detect_contradictions.return_value = []

    orchestrator = ResearchOrchestrator(
        planner=mock_planner,
        searcher=mock_searcher,
        gap_detector=mock_gap_detector,
        summarizer=mock_summarizer,
        claim_verifier=mock_claim_verifier,
        contradiction_detector=mock_contra_detector,
    )

    progress_steps = []
    def record_progress(step, pct, details):
        progress_steps.append((step, pct))

    # Execute research
    result = orchestrator.run_research(
        topic="Solid State Batteries",
        depth="QUICK",
        progress_callback=record_progress,
    )

    assert isinstance(result, ResearchResult)
    assert result.topic == "Solid State Batteries"
    assert result.depth == "QUICK"
    assert result.session_id.startswith("research_")
    assert len(result.report) > 0
    assert len(result.claims) == 1
    assert result.claims[0].support_label == "Strongly Supported"
    assert result.confidence is not None
    assert 0.0 <= result.confidence.overall_score <= 100.0

    # Verify metrics
    metrics = result.metrics
    assert metrics is not None
    assert metrics.generated_queries >= 2
    assert metrics.total_sources_found >= 1
    assert metrics.execution_time_seconds >= 0.0

    # Verify progress callback was triggered across lifecycle
    assert len(progress_steps) >= 5
    assert progress_steps[-1][0] == "COMPLETE"
    assert progress_steps[-1][1] == 1.0
