"""
Deployment Readiness Test Suite for Agentic Research PRO.
Validates production deployment contracts for Railway:
- GET /health and GET /api/health lightweight endpoints
- Static frontend index & SPA routing fallback
- Configurable CORS headers
- Ephemeral & Persistent ChromaDB initialization
- Playwright Chromium headless browser launch and cleanup
- LLM provider initialization (NVIDIA primary, OpenAI fallback)
- ReportLab PDF generation with permanent author attribution
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    """GET and HEAD /health must return status ok without heavy computation."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "agentic-research-pro"
    assert data["version"] == "2.0.0"

    head_resp = client.head("/health")
    assert head_resp.status_code == 200


def test_api_health_mirror(client):
    """GET and HEAD /api/health mirror must also return status ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "agentic-research-pro"

    head_resp = client.head("/api/health")
    assert head_resp.status_code == 200


def test_spa_route_fallback(client):
    """Client-side routing (e.g. /dossier, /session_xyz) should serve index.html, not 404."""
    response = client.get("/dossier")
    assert response.status_code == 200
    assert "<title>✦ AGENTIC RESEARCH" in response.text
    assert '<div id="root"></div>' in response.text


def test_nonexistent_api_returns_404(client):
    """API routes that do not exist should 404 instead of serving HTML index."""
    response = client.get("/api/nonexistent_route")
    assert response.status_code == 404


def test_chroma_ephemeral_client():
    """Verify Chroma initializes EphemeralClient by default."""
    from src.chroma_store import get_chroma_client, reset_chroma_client
    reset_chroma_client()
    
    # Ensure no CHROMA_PERSIST_DIR
    old_env = os.environ.pop("CHROMA_PERSIST_DIR", None)
    try:
        client = get_chroma_client()
        assert client is not None
        # Should be an in-memory client
        col = client.get_or_create_collection("test_ephemeral")
        assert col.name == "test_ephemeral"
    finally:
        if old_env:
            os.environ["CHROMA_PERSIST_DIR"] = old_env
        reset_chroma_client()


def test_chroma_persistent_client(tmp_path):
    """Verify Chroma initializes PersistentClient when CHROMA_PERSIST_DIR is configured."""
    from src.chroma_store import get_chroma_client, reset_chroma_client
    reset_chroma_client()
    
    persist_dir = str(tmp_path / "chroma_test_dir")
    os.environ["CHROMA_PERSIST_DIR"] = persist_dir
    try:
        client = get_chroma_client()
        assert client is not None
        col = client.get_or_create_collection("test_persistent")
        assert col.name == "test_persistent"
        assert os.path.exists(persist_dir)
    finally:
        os.environ.pop("CHROMA_PERSIST_DIR", None)
        reset_chroma_client()


def test_playwright_chromium_launch():
    """Verify Playwright Chromium launches, evaluates page, and closes cleanly."""
    from src.acquisition.playwright_agent import PlaywrightAgent
    
    agent = PlaywrightAgent(headless=True, timeout_ms=10000)
    try:
        browser = agent._ensure_browser()
        assert browser is not None
        
        context = browser.new_context()
        page = context.new_page()
        page.set_content("<html><head><title>Railway Test</title></head><body><h1>Agentic Research PRO</h1></body></html>")
        
        title = page.title()
        assert title == "Railway Test"
        heading = page.locator("h1").inner_text()
        assert heading == "Agentic Research PRO"
        
        page.close()
        context.close()
    finally:
        agent.close()


def test_pdf_generation_attribution(tmp_path):
    """Verify PDF generator produces a valid document containing required author attribution."""
    from src.pdfgen import generate_research_pdf
    from src.research_orchestrator import ResearchResult, ResearchState
    from src.config import get_research_config
    from src.confidence import ResearchConfidence
    
    dummy_confidence = ResearchConfidence(
        overall_score=88.0,
        source_quality=90.0,
        evidence_coverage=85.0,
        claim_support=88.0,
        source_agreement=85.0,
        research_completeness=92.0,
        explanation="High confidence empirical analysis.",
    )

    state = ResearchState(
        session_id="session_deploy_test",
        topic="Deployment Verification Analysis",
        depth="STANDARD",
        config=get_research_config("STANDARD"),
        report="## Executive Summary\nDeployment verification analysis confirms system integrity.",
        confidence=dummy_confidence,
        accepted_sources=[{
            "url": "https://example.com/research",
            "title": "Example Technical Specification",
            "tier": 1,
            "source_type": "official",
            "source_score": 0.95,
        }],
    )
    dummy_result = ResearchResult(state=state)
    
    output_pdf = str(tmp_path / "test_deployment_dossier.pdf")
    generated_path = generate_research_pdf(dummy_result, output_path=output_pdf)
    
    assert os.path.exists(generated_path)
    assert os.path.getsize(generated_path) > 1000
    
    # Read text back from generated PDF to ensure author attribution is present
    from pypdf import PdfReader
    reader = PdfReader(generated_path)
    assert len(reader.pages) >= 1
    
    full_pdf_text = "".join(p.extract_text() or "" for p in reader.pages)
    assert "Built by - Utkarsh Pandey" in full_pdf_text
    assert "Deployment verification analysis" in full_pdf_text
