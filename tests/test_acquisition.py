"""
Unit tests for Playwright Research Acquisition Subsystem.
Covers SourceRouter, HttpAcquirer, PdfAcquirer, and PlaywrightAgent with full mocking.
"""

from unittest.mock import MagicMock, patch, PropertyMock
import pytest
from src.acquisition.evidence_document import EvidenceDocument, ScrapedDocument
from src.acquisition.http_acquirer import HttpAcquirer, extract_html_tables
from src.acquisition.pdf_acquirer import PdfAcquirer
from src.acquisition.playwright_agent import PlaywrightAgent
from src.acquisition.source_router import SourceRouter, is_supported_url
from src.config import (
    PLAYWRIGHT_ENABLED,
    PLAYWRIGHT_HEADLESS,
    PLAYWRIGHT_MAX_PAGES,
    PLAYWRIGHT_MAX_SCROLLS,
    PLAYWRIGHT_TIMEOUT_MS,
)
from bs4 import BeautifulSoup


# 1. SourceRouter chooses HTTP for static pages
def test_router_chooses_http_for_static():
    mock_http = MagicMock()
    mock_pdf = MagicMock()
    mock_pw = MagicMock()

    doc = EvidenceDocument(
        url="https://example.com/article",
        title="Static Article",
        content="This is static text with sufficient informative length for research analysis. " * 5,
        acquisition_method="http",
    )
    mock_http.acquire.return_value = (doc, False, "")

    router = SourceRouter(http_acquirer=mock_http, pdf_acquirer=mock_pdf, playwright_agent=mock_pw)
    source = {"url": "https://example.com/article", "title": "Static Article"}
    result_doc, method = router.route_source(source)

    assert result_doc is not None
    assert method == "http"
    assert result_doc.acquisition_method == "http"
    mock_pw.acquire.assert_not_called()
    mock_pdf.acquire.assert_not_called()


# 2. SourceRouter chooses PDF for PDF sources
def test_router_chooses_pdf_for_pdf_sources():
    mock_http = MagicMock()
    mock_pdf = MagicMock()
    mock_pw = MagicMock()

    pdf_doc = EvidenceDocument(
        url="https://arxiv.org/pdf/2301.0001.pdf",
        title="PDF Paper",
        content="Academic PDF content with deep empirical evidence and methodology. " * 6,
        acquisition_method="pdf",
    )
    mock_pdf.acquire.return_value = pdf_doc

    router = SourceRouter(http_acquirer=mock_http, pdf_acquirer=mock_pdf, playwright_agent=mock_pw)
    source = {"url": "https://arxiv.org/pdf/2301.0001.pdf", "title": "PDF Paper"}
    result_doc, method = router.route_source(source)

    assert result_doc is not None
    assert method == "pdf"
    assert result_doc.acquisition_method == "pdf"
    mock_pdf.acquire.assert_called_once()
    mock_http.acquire.assert_not_called()


# 3. SourceRouter chooses Playwright for dynamic / low-text SPA pages
def test_router_chooses_playwright_for_dynamic():
    mock_http = MagicMock()
    mock_pdf = MagicMock()
    mock_pw = MagicMock()

    mock_http.acquire.return_value = (None, True, "Empty SPA mounting container detected")

    pw_doc = EvidenceDocument(
        url="https://dashboard.org/live-stats",
        title="Live Dashboard",
        content="Client-side rendered evidence rendered after JavaScript hydration. " * 6,
        acquisition_method="playwright",
    )
    mock_pw.acquire.return_value = pw_doc

    router = SourceRouter(http_acquirer=mock_http, pdf_acquirer=mock_pdf, playwright_agent=mock_pw)
    source = {"url": "https://dashboard.org/live-stats", "title": "Live Dashboard"}
    result_doc, method = router.route_source(source)

    assert result_doc is not None
    assert method == "playwright"
    assert result_doc.acquisition_method == "playwright"
    mock_pw.acquire.assert_called_once()


# 4. Playwright agent extracts visible text
def test_playwright_extracts_visible_text():
    agent = PlaywrightAgent(headless=True)

    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()

    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    sample_text = "Solid-state electrolyte materials demonstrate high ionic conductivity at room temperature. " * 5
    mock_page.content.return_value = "<html><body><article>" + sample_text + "</article></body></html>"
    mock_page.title.return_value = "Electrolyte Discovery"

    mock_locator = MagicMock()
    mock_locator.count.return_value = 1
    mock_locator.first.is_visible.return_value = True
    mock_locator.first.inner_text.return_value = sample_text
    mock_page.locator.return_value = mock_locator
    mock_page.evaluate.return_value = []

    with patch.object(agent, "_ensure_browser", return_value=mock_browser):
        source = {"url": "https://batteryresearch.org/study", "title": "Electrolyte Discovery"}
        doc = agent.acquire(source)

        assert doc is not None
        assert doc.acquisition_method == "playwright"
        assert "Solid-state electrolyte" in doc.content
        assert doc.title == "Electrolyte Discovery"
        mock_page.goto.assert_called_once()


# 5. Playwright agent extracts relevant targeted sections
def test_playwright_extracts_relevant_sections():
    agent = PlaywrightAgent()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()

    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    mock_page.content.return_value = "<html><body><div>Nav</div><main>Target Research Section Content with key metrics. " * 8 + "</main></body></html>"
    mock_page.title.return_value = "Target Section"

    article_locator = MagicMock()
    article_locator.count.return_value = 1
    article_locator.first.is_visible.return_value = True
    article_locator.first.inner_text.return_value = "Target Research Section Content with key metrics. " * 8
    mock_page.locator.return_value = article_locator
    mock_page.evaluate.return_value = []

    with patch.object(agent, "_ensure_browser", return_value=mock_browser):
        doc = agent.acquire({"url": "https://research.org/paper", "title": "Paper"})
        assert doc is not None
        assert "Target Research Section" in doc.content


# 6. Playwright agent handles expandable content
def test_playwright_handles_expandable_content():
    agent = PlaywrightAgent()
    mock_page = MagicMock()

    btn1 = MagicMock()
    btn1.is_visible.return_value = True
    btn2 = MagicMock()
    btn2.is_visible.return_value = False

    mock_locator = MagicMock()
    mock_locator.all.return_value = [btn1, btn2]
    mock_page.locator.return_value = mock_locator

    expanded = agent._expand_interactive_sections(mock_page)
    assert expanded == 3
    assert btn1.click.call_count == 3
    btn2.click.assert_not_called()


# 7. Playwright agent handles bounded pagination
def test_playwright_handles_bounded_pagination():
    agent = PlaywrightAgent(max_pages=2)
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()

    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    mock_page.content.return_value = "<html><body>Page 1 Content with adequate text. " * 10 + "</body></html>"
    mock_page.title.return_value = "Paginated Source"

    body_locator = MagicMock()
    body_locator.inner_text.side_effect = [
        "Page 1 Content with adequate text. " * 10,
        "Page 2 Content with subsequent evidence. " * 10,
    ]
    mock_page.locator.return_value = body_locator
    mock_page.evaluate.return_value = []

    with patch.object(agent, "_ensure_browser", return_value=mock_browser):
        doc = agent.acquire({"url": "https://multi-page.org/reports", "title": "Multi Page"})
        assert doc is not None
        assert doc.metadata.get("pages_visited", 1) <= 2


# 8. Playwright agent handles bounded scrolling
def test_playwright_handles_bounded_scrolling():
    agent = PlaywrightAgent(max_scrolls=3)
    mock_page = MagicMock()

    call_counts = {"count": 0}

    def mock_eval(script):
        call_counts["count"] += 1
        # Iteration 1: prev=1000, scrollBy, curr=1500
        # Iteration 2: prev=1500, scrollBy, curr=1500 (stops)
        if call_counts["count"] <= 2:
            return 1000
        return 1500

    mock_page.evaluate.side_effect = mock_eval
    scrolls = agent._perform_bounded_scroll(mock_page)

    assert scrolls == 2


# 9. Playwright agent extracts tables without losing relationships
def test_playwright_extracts_tables_preserving_relationships():
    agent = PlaywrightAgent()
    mock_page = MagicMock()

    table_eval_data = [
        {
            "headers": ["Year", "Production (GWh)", "Region"],
            "rows": [
                ["2024", "45", "North America"],
                ["2025", "85", "Asia Pacific"],
                ["2026", "160", "Europe"],
            ],
        }
    ]
    mock_page.evaluate.return_value = table_eval_data

    md_table, records = agent._extract_tables_from_page(mock_page)

    assert "| Year | Production (GWh) | Region |" in md_table
    assert "| 2026 | 160 | Europe |" in md_table
    assert len(records) == 1
    assert records[0]["headers"] == ["Year", "Production (GWh)", "Region"]
    assert records[0]["rows"][2] == ["2026", "160", "Europe"]


# 10. Duplicate evidence removal and URL filtering
def test_is_supported_url():
    assert is_supported_url("https://nature.com/articles/s41586") is True
    assert is_supported_url("http://arxiv.org/abs/2401.0001") is True
    assert is_supported_url("https://youtube.com/watch?v=123") is False
    assert is_supported_url("https://twitter.com/post") is False
    assert is_supported_url("") is False


# 11. Navigation timeout is handled cleanly
def test_navigation_timeout_handled():
    agent = PlaywrightAgent(timeout_ms=500)
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()

    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    mock_page.goto.side_effect = Exception("Navigation timeout of 500ms exceeded")

    with patch.object(agent, "_ensure_browser", return_value=mock_browser):
        doc = agent.acquire({"url": "https://slow-failing-site.org"})
        assert doc is None
        mock_page.close.assert_called_once()
        mock_context.close.assert_called_once()


# 12. Browser crash / process termination handled
def test_browser_crash_handled():
    agent = PlaywrightAgent()
    with patch.object(agent, "_ensure_browser", side_effect=Exception("Browser process died unexpectedly")):
        doc = agent.acquire({"url": "https://crashing-site.com"})
        assert doc is None


# 13. Blocked / paywall / CAPTCHA source handled
def test_blocked_source_handled():
    agent = PlaywrightAgent()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()

    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    mock_page.content.return_value = "<html><head><title>Access Denied</title></head><body>Verify you are human | Cloudflare security check to continue</body></html>"

    with patch.object(agent, "_ensure_browser", return_value=mock_browser):
        doc = agent.acquire({"url": "https://protected-paywall.com"})
        assert doc is None


# 14. Playwright failure falls back to HTTP acquisition
def test_playwright_failure_falls_back_to_http():
    mock_http = MagicMock()
    mock_pdf = MagicMock()
    mock_pw = MagicMock()

    partial_http_doc = EvidenceDocument(
        url="https://dynamic-site.org",
        title="Fallback HTML",
        content="Partial server-side rendered text available as a fallback for research. " * 5,
        acquisition_method="http",
    )
    mock_http.acquire.return_value = (partial_http_doc, True, "Dynamic SPA indicators present")
    mock_pw.acquire.return_value = None  # Browser acquisition fails

    router = SourceRouter(http_acquirer=mock_http, pdf_acquirer=mock_pdf, playwright_agent=mock_pw)
    source = {"url": "https://dynamic-site.org", "title": "Fallback HTML"}
    doc, method = router.route_source(source)

    assert doc is not None
    assert method == "http"
    assert doc.title == "Fallback HTML"


# 15. Acquisition metadata preserved in EvidenceDocument
def test_acquisition_metadata_preserved():
    doc = EvidenceDocument(
        url="https://energy.gov/report",
        title="Energy Grid Review",
        content="Grid modernization findings and transmission network metrics. " * 6,
        acquisition_method="playwright",
        tables=[{"headers": ["Metric", "Value"], "rows": [["Loss", "4%"]]}],
        metadata={"pages_visited": 2, "tables_found": 1},
    )

    d = doc.to_dict()
    assert d["acquisition_method"] == "playwright"
    assert d["metadata"]["pages_visited"] == 2
    assert len(d["tables"]) == 1
    assert "retrieval_timestamp" in d


# 16. SSE research progress events emitted correctly
def test_sse_events_emitted_correctly():
    mock_http = MagicMock()
    mock_http.acquire.return_value = (None, True, "Dynamic SPA framework detected")

    mock_pw = MagicMock()
    mock_pw.acquire.return_value = EvidenceDocument(
        url="https://dashboard.org",
        title="Dynamic",
        content="Extracted dynamic evidence text with sufficient length. " * 6,
        acquisition_method="playwright",
    )

    router = SourceRouter(http_acquirer=mock_http, playwright_agent=mock_pw)
    events = []

    def callback(step, pct, msg):
        events.append((step, msg))

    sources = [{"url": "https://dashboard.org", "title": "Dynamic"}]
    docs, failures, metrics = router.acquire_sources(sources, progress_callback=callback)

    assert len(docs) == 1
    assert metrics["playwright_acquisitions"] == 1
    assert any("PLAYWRIGHT_DETECT" in e[0] for e in events)


# 17. Browser resources cleaned up on close
def test_browser_resources_cleaned_up():
    agent = PlaywrightAgent()
    mock_browser = MagicMock()
    mock_playwright = MagicMock()
    agent._browser = mock_browser
    agent._playwright = mock_playwright

    agent.close()

    mock_browser.close.assert_called_once()
    mock_playwright.stop.assert_called_once()
    assert agent._browser is None
    assert agent._playwright is None


# 18. Configuration parameters load correctly
def test_configuration_loaded():
    assert isinstance(PLAYWRIGHT_ENABLED, bool)
    assert isinstance(PLAYWRIGHT_HEADLESS, bool)
    assert isinstance(PLAYWRIGHT_MAX_PAGES, int)
    assert isinstance(PLAYWRIGHT_MAX_SCROLLS, int)
    assert isinstance(PLAYWRIGHT_TIMEOUT_MS, int)
    assert PLAYWRIGHT_MAX_PAGES >= 1
    assert PLAYWRIGHT_MAX_SCROLLS >= 1
    assert PLAYWRIGHT_TIMEOUT_MS >= 1000
