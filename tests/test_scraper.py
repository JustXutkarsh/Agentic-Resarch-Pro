"""Unit tests for src/scraper.py"""
from unittest.mock import MagicMock, patch
import pytest
from src.scraper import (
    is_supported_url,
    scrape_html_content,
    scrape_single_source,
    scrape_sources,
    ScrapedDocument,
)


def test_is_supported_url():
    assert is_supported_url("https://nature.com/article1") is True
    assert is_supported_url("http://arxiv.org/abs/2301.0001") is True
    assert is_supported_url("https://www.youtube.com/watch?v=123") is False
    assert is_supported_url("https://x.com/tech_news") is False
    assert is_supported_url("ftp://unsupported.com") is False
    assert is_supported_url("") is False


def test_scrape_html_content_strips_scripts_and_extracts():
    sample_html = """
    <html>
      <head><script>var ad = 123;</script><style>body { color: red; }</style></head>
      <body>
        <nav>Navigation links</nav>
        <p>Artificial intelligence in modern clinical healthcare offers significant advancements in diagnostics.</p>
        <p>Clinicians are utilizing deep neural networks to recognize radiographic patterns faster than manual inspection.</p>
        <p>Furthermore, medical centers report increased throughput and reduced wait times across multiple hospital departments.</p>
        <footer>Copyright 2026</footer>
      </body>
    </html>
    """
    text = scrape_html_content(sample_html)
    assert text is not None
    assert "ad = 123" not in text
    assert "Navigation links" not in text
    assert "Copyright 2026" not in text
    assert "Artificial intelligence in modern clinical healthcare" in text


@patch("src.scraper.requests.get")
def test_scrape_single_source_success(mock_get):
    sample_html = "<p>" + ("Solid-state electrolyte research continues to show promise. " * 15) + "</p>"
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "text/html"}
    mock_resp.text = sample_html
    mock_get.return_value = mock_resp

    source = {
        "url": "https://batterytech.org/report",
        "title": "Solid State Report",
        "search_query": "battery breakthroughs",
        "research_iteration": 1,
        "source_score": 0.88,
    }
    doc = scrape_single_source(source)

    assert doc is not None
    assert isinstance(doc, ScrapedDocument)
    assert doc.url == "https://batterytech.org/report"
    assert doc.source_score == 0.88
    assert "Solid-state electrolyte" in doc.content


@patch("src.scraper.requests.get")
def test_scrape_sources_fault_tolerance(mock_get):
    # First source succeeds, second source raises exception
    good_html = "<p>" + ("Quantum computers operate using qubits with superposition properties. " * 15) + "</p>"
    good_resp = MagicMock()
    good_resp.status_code = 200
    good_resp.headers = {"Content-Type": "text/html"}
    good_resp.text = good_html

    mock_get.side_effect = [good_resp, Exception("Connection refused")]

    sources = [
        {"url": "https://science.org/quantum", "title": "Quantum Science"},
        {"url": "https://failing-domain.com/broken", "title": "Failing Link"},
    ]

    docs, failures = scrape_sources(sources)

    assert len(docs) == 1
    assert len(failures) == 1
    assert docs[0].url == "https://science.org/quantum"
    assert failures[0]["url"] == "https://failing-domain.com/broken"
