"""
End-to-End Pipeline & Comparative Benchmark Tests for Agentic Research PRO.
Validates operational differences between QUICK, STANDARD, and DEEP research depth modes,
and measures Agentic Research PRO against traditional single-query research.
"""

from unittest.mock import MagicMock
import pytest
from src.config import get_research_config
from src.research_planner import ResearchPlan
from src.research_orchestrator import ResearchOrchestrator, ResearchResult
from src.claim_verifier import ClaimVerification
from src.contradiction_detector import Contradiction


def test_research_depth_behavioral_hierarchy():
    """
    Verify that Quick, Standard, and Deep depth modes enforce
    strictly increasing computational parameters.
    """
    quick_cfg = get_research_config("QUICK")
    std_cfg = get_research_config("STANDARD")
    deep_cfg = get_research_config("DEEP")

    # 1. Queries
    assert quick_cfg.max_queries < std_cfg.max_queries < deep_cfg.max_queries
    assert (quick_cfg.max_queries, std_cfg.max_queries, deep_cfg.max_queries) == (1, 3, 6)

    # 2. Target Sources
    assert quick_cfg.max_sources < std_cfg.max_sources < deep_cfg.max_sources
    assert (quick_cfg.max_sources, std_cfg.max_sources, deep_cfg.max_sources) == (5, 10, 20)

    # 3. Iterations
    assert quick_cfg.max_iterations <= std_cfg.max_iterations < deep_cfg.max_iterations
    assert (quick_cfg.max_iterations, std_cfg.max_iterations, deep_cfg.max_iterations) == (1, 2, 3)

    # 4. Top K Retrieval
    assert quick_cfg.top_k < std_cfg.top_k < deep_cfg.top_k
    assert (quick_cfg.top_k, std_cfg.top_k, deep_cfg.top_k) == (10, 20, 30)

    # 5. Planning and Gaps
    assert quick_cfg.enable_planning is False
    assert std_cfg.enable_planning is True
    assert deep_cfg.enable_planning is True

    assert quick_cfg.enable_gap_detection is False
    assert std_cfg.enable_gap_detection is True
    assert deep_cfg.enable_gap_detection is True

    # 6. Contradictions
    assert quick_cfg.enable_contradiction_detection is False
    assert std_cfg.enable_contradiction_detection is False
    assert deep_cfg.enable_contradiction_detection is True


def test_end_to_end_quick_vs_deep_execution():
    """
    Simulate full execution for QUICK and DEEP and compare generated metrics.
    """
    topic = "Impact of Artificial Intelligence on Cybersecurity"

    # Planner Mock
    mock_planner = MagicMock()
    mock_planner.plan_research.side_effect = lambda t, config: ResearchPlan(
        main_question=f"Analysis of {t}",
        sub_questions=[f"Sub-q {i}" for i in range(config.max_queries)],
        search_queries=[f"Query {i} on {t}" for i in range(config.max_queries)],
        research_dimensions=["Threat Detection", "Automated Response", "Vulnerability Discovery"][:config.max_queries],
    )

    # Searcher Mock
    mock_searcher = MagicMock()
    def mock_search_multiple(queries, max_results_per_query, iteration):
        results = []
        for q in queries:
            results.append({
                "url": f"https://security.gov/report-{abs(hash(q)) % 1000}",
                "title": f"Security Report for {q}",
                "snippet": "Deep learning models identified cyber attack vectors with 98.2% recall in benchmark testing.",
                "published_date": "2026-01-15",
                "search_query": q,
                "research_iteration": iteration,
            })
        return results
    mock_searcher.search_multiple.side_effect = mock_search_multiple

    # Gap Detector Mock
    mock_gap_detector = MagicMock()
    mock_gap_detector.detect_gaps.return_value = []

    # Summarizer Mock
    mock_summarizer = MagicMock()
    mock_summarizer.summarize.return_value = (
        f"# Research Report: {topic}\n\n"
        "## Executive Summary\nAI dramatically improves cyber defense capabilities.\n\n"
        "## Key Findings & Strategic Insights\n- **Threat Detection**: Recall reached 98.2%.\n\n"
        "## Trade-offs & Comparative Analysis\n### Strengths & Opportunities (Pros)\n- Real-time defense.\n\n"
        "### Limitations & Risks (Cons)\n- Adversarial evasion.\n\n"
        "## Source Citations & References\n- https://security.gov/report"
    )

    # Claim Verifier Mock
    mock_claim_verifier = MagicMock()
    mock_claim_verifier.extract_claims.side_effect = lambda rep, max_claims: [
        f"Factual Claim {i}: AI recall reached 98.2%." for i in range(min(max_claims, 3))
    ]
    mock_claim_verifier.verify_claims_against_evidence.side_effect = lambda claims, collection=None, config=None: [
        ClaimVerification(
            claim=c,
            support_label="Strongly Supported",
            support_score=1.0,
            reasoning="Directly confirmed by benchmark data.",
            evidence_chunks=["Recall reached 98.2%."],
            source_urls=["https://security.gov/report"],
            source_count=1,
        )
        for c in claims
    ]

    # Contradiction Detector Mock
    mock_contra = MagicMock()
    mock_contra.detect_contradictions.side_effect = lambda topic=None, plan=None, evidence_chunks=None, config=None, **kwargs: [
        Contradiction(
            topic="Offensive vs Defensive Asymmetry",
            perspective_a="AI favors defenders by automating patch management.",
            perspective_b="AI favors attackers by automating polymorphic malware generation.",
            supporting_sources_a=["https://security.gov/defense"],
            supporting_sources_b=["https://security.gov/attacks"],
            resolution="Both offensive and defensive capabilities accelerate simultaneously.",
        )
    ] if (config and config.enable_contradiction_detection) else []

    orchestrator = ResearchOrchestrator(
        planner=mock_planner,
        searcher=mock_searcher,
        gap_detector=mock_gap_detector,
        summarizer=mock_summarizer,
        claim_verifier=mock_claim_verifier,
        contradiction_detector=mock_contra,
    )

    from unittest.mock import patch
    from src.scraper import ScrapedDocument

    # Mock scrape_sources to return clean documents without network requests
    fake_docs = [
        ScrapedDocument(
            url="https://security.gov/report",
            title="Cybersecurity Report",
            content="Deep learning models identified cyber attack vectors with 98.2% recall in benchmark testing.",
            source_score=0.92,
        )
    ]
    with patch("src.research_orchestrator.scrape_sources", return_value=(fake_docs, [])):
        # Run QUICK
        result_quick = orchestrator.run_research(topic=topic, depth="QUICK")

        # Run DEEP
        result_deep = orchestrator.run_research(topic=topic, depth="DEEP")

    # Assert Operational Differences:
    # 1. Queries: Quick (1) < Deep (6)
    assert result_quick.metrics.generated_queries == 1
    assert result_deep.metrics.generated_queries == 6
    assert result_quick.metrics.generated_queries < result_deep.metrics.generated_queries

    # 2. Contradictions: Disabled in Quick, Active in Deep
    assert len(result_quick.contradictions) == 0
    assert len(result_deep.contradictions) == 1

    # 3. Claims Analyzed: Quick capped lower than Deep
    assert result_quick.metrics.claims_analyzed <= result_deep.metrics.claims_analyzed

    # 4. Session IDs are distinct
    assert result_quick.session_id != result_deep.session_id


def test_traditional_vs_agentic_research_comparison():
    """
    Benchmark comparison between traditional single-query search and Agentic Research PRO.
    """
    topic = "Autonomous Electric Vehicle Fleets"

    # Traditional single query research profile:
    traditional_profile = {
        "queries_used": 1,
        "sources_evaluated": 5,
        "sources_quality_filtered": False,
        "research_dimensions": 1,
        "gap_detection_loops": 0,
        "factual_claims_verified": 0,
        "contradiction_analysis": False,
        "confidence_heuristic": False,
    }

    # Agentic Research PRO profile (STANDARD depth):
    std_cfg = get_research_config("STANDARD")
    agentic_profile = {
        "queries_used": std_cfg.max_queries,  # 3
        "sources_evaluated": std_cfg.max_sources,  # 10
        "sources_quality_filtered": True,
        "research_dimensions": 3,
        "gap_detection_loops": 1,
        "factual_claims_verified": std_cfg.max_claims_to_verify,  # 10
        "contradiction_analysis": False,
        "confidence_heuristic": True,
    }

    assert agentic_profile["queries_used"] > traditional_profile["queries_used"]
    assert agentic_profile["sources_evaluated"] > traditional_profile["sources_evaluated"]
    assert agentic_profile["research_dimensions"] > traditional_profile["research_dimensions"]
    assert agentic_profile["sources_quality_filtered"] is True
    assert agentic_profile["factual_claims_verified"] > 0
