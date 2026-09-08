"""Unit tests for src/research_metrics.py"""
import time
import pytest
from src.research_metrics import ResearchMetrics, APP_VERSION


def test_research_metrics_initialization_and_finalization():
    metrics = ResearchMetrics(
        session_id="test_sess_001",
        topic="Solid State Batteries",
        depth="STANDARD",
    )
    assert metrics.session_id == "test_sess_001"
    assert metrics.generated_queries == 0
    assert metrics.app_version == APP_VERSION

    time.sleep(0.05)
    metrics.generated_queries += 3
    metrics.sources_accepted += 8
    metrics.finalize()

    assert metrics.end_time != ""
    assert metrics.execution_time_seconds >= 0.04
    data = metrics.to_dict()
    assert data["generated_queries"] == 3
    assert data["sources_accepted"] == 8
    assert data["depth"] == "STANDARD"
