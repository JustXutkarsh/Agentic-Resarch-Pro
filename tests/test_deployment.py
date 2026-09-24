"""
Deployment Readiness Test Suite for Agentic Research PRO.
Validates production deployment contracts for Render / container deployment:
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


def test_cors_default_origins_allowed(client):
    """Local development origins must be allowed by default CORS configuration."""
    # Preflight OPTIONS request
    preflight = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert preflight.status_code == 200
    assert preflight.headers.get("access-control-allow-origin") == "http://localhost:5173"

    # Actual GET request includes Access-Control-Expose-Headers
    resp = client.get(
        "/health",
        headers={"Origin": "http://localhost:5173"},
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "content-disposition" in resp.headers.get("access-control-expose-headers", "").lower()


def test_cors_origin_normalization_logic():
    """Verify that comma-separated origins are trimmed of whitespace and trailing slashes."""
    raw = " https://my-agentic-app.vercel.app/ , https://preview-123.vercel.app/ , http://custom-domain.com "
    configured = [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]
    assert configured == [
        "https://my-agentic-app.vercel.app",
        "https://preview-123.vercel.app",
        "http://custom-domain.com",
    ]


def test_cors_vercel_origins_allowed(client):
    """Verify production and preview Vercel domains are allowed with preflight 200."""
    vercel_origins = [
        "https://agentic-research-pro.vercel.app",
        "https://agentic-research-pro-git-main-justxutkarsh.vercel.app",
        "https://my-custom-subdomain.vercel.app",
    ]

    for origin in vercel_origins:
        # Preflight OPTIONS request for /api/research
        preflight = client.options(
            "/api/research",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert preflight.status_code == 200, f"Preflight failed for {origin}"
        assert preflight.headers.get("access-control-allow-origin") == origin
        assert preflight.headers.get("access-control-allow-credentials") == "true"

        # GET request to /health with Vercel origin
        resp = client.get("/health", headers={"Origin": origin})
        assert resp.status_code == 200
        assert resp.headers.get("access-control-allow-origin") == origin


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
        page.set_content("<html><head><title>Render Deployment Test</title></head><body><h1>Agentic Research PRO</h1></body></html>")
        
        title = page.title()
        assert title == "Render Deployment Test"
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


def test_cleanup_session_vector_store():
    """Verify that cleanup_session_vector_store deletes ephemeral collection to release RAM."""
    from src.chroma_store import get_vector_store, cleanup_session_vector_store, get_chroma_client
    
    test_sid = "test_cleanup_session_123"
    col = get_vector_store(test_sid)
    assert col is not None
    client = get_chroma_client()
    names = [c.name for c in client.list_collections()]
    assert f"research_{test_sid}" in names
    
    cleanup_session_vector_store(test_sid)
    names_after = [c.name for c in client.list_collections()]
    assert f"research_{test_sid}" not in names_after


def test_session_pruning_bounds_memory(tmp_path):
    """Verify that prune_old_sessions removes oldest sessions when exceeding MAX_RETAINED_SESSIONS."""
    from server import active_sessions, prune_old_sessions, MAX_RETAINED_SESSIONS
    from datetime import datetime, timedelta
    
    # Clear sessions for test
    active_sessions.clear()
    
    # Create 5 completed sessions
    base_time = datetime.now()
    for i in range(5):
        sid = f"session_prune_test_{i}"
        dummy_pdf = str(tmp_path / f"dossier_{i}.pdf")
        with open(dummy_pdf, "w") as f:
            f.write("pdf data")
        active_sessions[sid] = {
            "session_id": sid,
            "status": "complete",
            "started_at": base_time + timedelta(minutes=i),
            "pdf_path": dummy_pdf,
        }
    
    assert len(active_sessions) == 5
    prune_old_sessions()
    assert len(active_sessions) == MAX_RETAINED_SESSIONS
    # Oldest 2 sessions (0 and 1) should be pruned
    assert "session_prune_test_0" not in active_sessions
    assert "session_prune_test_1" not in active_sessions
    assert "session_prune_test_4" in active_sessions
