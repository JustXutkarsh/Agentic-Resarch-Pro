"""
Unit tests for FastAPI Server & SSE Bridge.
"""

import pytest
from fastapi.testclient import TestClient
from server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_index_serves_react_app(client):
    """Verify that root / serves the compiled React presentation layer."""
    response = client.get("/")
    assert response.status_code == 200
    # Should serve the HTML with title and root div
    assert "<title>✦ AGENTIC RESEARCH" in response.text
    assert '<div id="root"></div>' in response.text


def test_start_research_validation(client):
    """Verify that starting research validates empty topic."""
    response = client.post("/api/research", json={"topic": "   ", "depth": "QUICK"})
    assert response.status_code == 400
    assert "Topic must not be empty" in response.json()["detail"]


def test_start_research_success(client, monkeypatch):
    """Verify that starting research returns session metadata."""
    # Prevent background execution from actually making web calls during fast test
    monkeypatch.setattr("server.run_research_worker", lambda *args, **kwargs: None)

    response = client.post("/api/research", json={"topic": "Quantum Computing Viability", "depth": "QUICK"})
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["topic"] == "Quantum Computing Viability"
    assert data["depth"] == "QUICK"
    assert "/api/research/" in data["stream_url"]


def test_llm_health_endpoint(client):
    """Verify that /api/health/llm returns provider diagnostics without exposing secrets."""
    response = client.get("/api/health/llm")
    assert response.status_code == 200
    data = response.json()
    assert "primary" in data
    assert "active_provider" in data
    assert "api_key" not in str(data).lower() or data["primary"].get("configured") is not None
    # Ensure no secrets leak
    assert "sk-" not in str(data)
    assert "nvapi-" not in str(data)
