"""Unit tests for src/research_planner.py"""
import json
from unittest.mock import MagicMock
import pytest
from src.config import get_research_config
from src.research_planner import ResearchPlanner, ResearchPlan, _create_fallback_plan


def test_quick_planning_disabled_no_llm_call():
    mock_client = MagicMock()
    planner = ResearchPlanner(client=mock_client)
    config = get_research_config("QUICK")

    plan = planner.plan_research("Electric Vehicles in India", config=config)

    # When enable_planning is False, OpenAI must NOT be called
    mock_client.chat.completions.create.assert_not_called()
    assert isinstance(plan, ResearchPlan)
    assert len(plan.search_queries) == 1
    assert "Electric Vehicles in India" in plan.search_queries[0]


def test_standard_planning_with_mock_llm():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps({
                    "main_question": "What is the technological and market state of AI in Healthcare?",
                    "sub_questions": [
                        "How is AI being used in diagnostics?",
                        "What are the regulatory hurdles?",
                        "What is the market growth rate?",
                    ],
                    "research_dimensions": [
                        "Clinical Applications",
                        "Regulatory & Ethics",
                        "Market Dynamics",
                    ],
                    "search_queries": [
                        "AI clinical diagnostic adoption 2026",
                        "FDA regulatory framework for healthcare AI",
                        "AI healthcare market size forecast",
                    ],
                })
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_response

    planner = ResearchPlanner(client=mock_client)
    config = get_research_config("STANDARD")

    plan = planner.plan_research("AI in Healthcare", config=config)

    mock_client.chat.completions.create.assert_called_once()
    assert plan.main_question.startswith("What is the technological")
    assert len(plan.sub_questions) == 3
    assert len(plan.research_dimensions) == 3
    assert len(plan.search_queries) == 3
    assert "AI clinical diagnostic adoption 2026" in plan.search_queries


def test_planner_fallback_on_llm_exception():
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("OpenAI API rate limit")

    planner = ResearchPlanner(client=mock_client)
    config = get_research_config("STANDARD")

    plan = planner.plan_research("Quantum Computing", config=config)

    assert isinstance(plan, ResearchPlan)
    assert len(plan.search_queries) <= config.max_queries
    assert len(plan.search_queries) > 0
    assert "Quantum Computing" in plan.main_question


def test_fallback_plan_query_limits():
    plan_quick = _create_fallback_plan("Robotics", max_queries=1)
    assert len(plan_quick.search_queries) == 1

    plan_standard = _create_fallback_plan("Robotics", max_queries=3)
    assert len(plan_standard.search_queries) == 3

    plan_deep = _create_fallback_plan("Robotics", max_queries=6)
    assert len(plan_deep.search_queries) == 6
