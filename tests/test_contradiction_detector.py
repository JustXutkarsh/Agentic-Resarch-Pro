"""Unit tests for src/contradiction_detector.py"""
from unittest.mock import MagicMock
import json
import pytest
from src.config import get_research_config
from src.research_planner import ResearchPlan
from src.contradiction_detector import (
    ContradictionDetector,
    Contradiction,
    _group_chunks_by_dimension,
)


def test_disabled_in_quick_and_standard():
    quick_cfg = get_research_config("QUICK")
    std_cfg = get_research_config("STANDARD")
    detector = ContradictionDetector()
    plan = ResearchPlan(main_question="Q", research_dimensions=["D1"], search_queries=["Q"])

    assert detector.detect_contradictions("Topic", plan, [{"text": "Sample text"}], quick_cfg) == []
    assert detector.detect_contradictions("Topic", plan, [{"text": "Sample text"}], std_cfg) == []


def test_group_chunks_by_dimension():
    dimensions = ["Solar Energy", "Ocean Marine Biology"]
    chunks = [
        {"text": "Photovoltaic cells absorb photons to generate electrical voltage.", "metadata": {}},
        {"text": "Coral reefs experience bleaching due to rising sea temperatures.", "metadata": {}},
    ]
    grouped = _group_chunks_by_dimension(dimensions, chunks)

    assert len(grouped["Solar Energy"]) >= 1
    assert "Photovoltaic" in grouped["Solar Energy"][0]["text"]
    assert len(grouped["Ocean Marine Biology"]) >= 1
    assert "Coral reefs" in grouped["Ocean Marine Biology"][0]["text"]


def test_detect_contradictions_with_mock_llm():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps({
                    "contradictions": [
                        {
                            "topic": "EV Battery Lifespan",
                            "perspective_a": "Lab studies report EV batteries degrade below 70% capacity after 5 years.",
                            "perspective_b": "Fleet real-world data demonstrates batteries retain over 85% capacity after 8 years.",
                            "supporting_sources_a": ["https://labstudy.org/battery"],
                            "supporting_sources_b": ["https://fleetdata.com/analytics"],
                            "resolution": "Accelerated laboratory thermal stress tests do not reflect mild real-world driving cycles.",
                        }
                    ]
                })
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_response

    detector = ContradictionDetector(client=mock_client)
    deep_cfg = get_research_config("DEEP")
    plan = ResearchPlan(
        main_question="EV Reliability",
        research_dimensions=["Battery Lifespan", "Manufacturing Costs"],
        search_queries=["EV battery life"],
    )
    chunks = [
        {"text": "Battery lifespan degrades rapidly in heat.", "metadata": {"source_url": "https://labstudy.org/battery"}},
        {"text": "Fleet data shows long battery retention.", "metadata": {"source_url": "https://fleetdata.com/analytics"}},
        {"text": "Manufacturing costs dropped significantly.", "metadata": {}},
        {"text": "Raw materials inflation increased costs.", "metadata": {}},
    ]

    contradictions = detector.detect_contradictions("EV Reliability", plan, chunks, deep_cfg)

    assert len(contradictions) == 1
    c = contradictions[0]
    assert isinstance(c, Contradiction)
    assert c.topic == "EV Battery Lifespan"
    assert "Lab studies" in c.perspective_a
    assert "Fleet" in c.perspective_b
    assert "https://labstudy.org/battery" in c.supporting_sources_a
