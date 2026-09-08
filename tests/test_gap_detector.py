"""Unit tests for src/gap_detector.py"""
from unittest.mock import MagicMock
import json
import pytest
from src.config import get_research_config
from src.research_planner import ResearchPlan
from src.gap_detector import (
    ResearchGap,
    ResearchGapDetector,
    compute_dimension_coverage,
)


def test_compute_dimension_coverage():
    dimensions = ["Battery Chemistry", "Ancient Rome Architecture"]
    evidence = [
        "Lithium iron phosphate and nickel cobalt aluminum battery chemistry cells show distinct thermal runaway resistance.",
    ]

    scores = compute_dimension_coverage(dimensions, evidence)
    assert scores["Battery Chemistry"] > scores["Ancient Rome Architecture"]


def test_detect_gaps_disabled_in_quick_mode():
    config = get_research_config("QUICK")
    plan = ResearchPlan(
        main_question="Q?",
        research_dimensions=["Cost", "Safety"],
        search_queries=["Q"],
    )
    detector = ResearchGapDetector()
    gaps = detector.detect_gaps("Batteries", plan, ["Some evidence"], config=config, current_iteration=1)
    assert gaps == []


def test_detect_gaps_halts_at_max_iterations():
    config = get_research_config("STANDARD")  # max_iterations = 2
    plan = ResearchPlan(
        main_question="Q?",
        research_dimensions=["Infrastructure", "Cost"],
        search_queries=["Q"],
    )
    detector = ResearchGapDetector()
    # If current_iteration is already 2, it must not generate more gaps
    gaps = detector.detect_gaps("EVs", plan, [], config=config, current_iteration=2)
    assert gaps == []


def test_detect_gaps_deterministic_formulation():
    config = get_research_config("STANDARD")
    # Force max_follow_up_gap_analyses = 0 for pure deterministic test
    custom_config = pytest.importorskip("dataclasses").replace(config, max_follow_up_gap_analyses=0)

    plan = ResearchPlan(
        main_question="AI in Hospitals",
        research_dimensions=["Diagnostic Accuracy", "Ethical and Legal Frameworks"],
        search_queries=["AI diagnostics"],
    )
    # Evidence only mentions diagnostics
    evidence = ["High accuracy convolutional networks in radiology diagnostics."]

    detector = ResearchGapDetector()
    gaps = detector.detect_gaps(
        "AI in Hospitals",
        plan,
        evidence,
        config=custom_config,
        current_iteration=1,
        coverage_threshold=0.55,
    )

    # Ethical and Legal should be flagged as a gap
    missing_dims = [g.missing_dimension for g in gaps]
    assert "Ethical and Legal Frameworks" in missing_dims
    for g in gaps:
        assert isinstance(g, ResearchGap)
        assert len(g.suggested_query) > 0


def test_detect_gaps_with_mock_llm():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps({
                    "gaps": [
                        {
                            "dimension": "Ethical and Legal Frameworks",
                            "reason": "No evidence discussing malpractice liability was retrieved.",
                            "priority": "High",
                            "suggested_query": "AI healthcare malpractice legal liability framework",
                        }
                    ]
                })
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_response

    detector = ResearchGapDetector(client=mock_client)
    config = get_research_config("STANDARD")

    plan = ResearchPlan(
        main_question="AI in Hospitals",
        research_dimensions=["Diagnostic Accuracy", "Ethical and Legal Frameworks"],
        search_queries=["AI diagnostics"],
    )
    evidence = ["Diagnostic models achieved 95% sensitivity in clinical imaging."]

    gaps = detector.detect_gaps(
        "AI in Hospitals",
        plan,
        evidence,
        config=config,
        current_iteration=1,
        coverage_threshold=0.55,
    )

    assert len(gaps) >= 1
    assert gaps[0].missing_dimension == "Ethical and Legal Frameworks"
    assert "liability" in gaps[0].reason
    assert "liability" in gaps[0].suggested_query
