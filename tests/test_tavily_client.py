"""Unit tests for src/tavily_client.py"""
from unittest.mock import MagicMock
import pytest
from src.tavily_client import (
    normalize_url,
    deduplicate_sources,
    TavilySearch,
)


def test_normalize_url():
    url1 = "https://Example.COM/articles/battery-tech/?utm_source=twitter&ref=newsletter#section2"
    url2 = "https://example.com/articles/battery-tech"
    assert normalize_url(url1) == "https://example.com/articles/battery-tech"
    assert normalize_url(url2) == "https://example.com/articles/battery-tech"


def test_deduplicate_sources():
    sources = [
        {"title": "Doc 1", "url": "https://nature.com/articles/123?utm_medium=email"},
        {"title": "Doc 1 Duplicate", "url": "https://nature.com/articles/123/"},
        {"title": "Doc 2", "url": "https://science.org/articles/456"},
    ]
    unique = deduplicate_sources(sources)
    assert len(unique) == 2
    assert unique[0]["title"] == "Doc 1"
    assert unique[1]["title"] == "Doc 2"


def test_tavily_search_query_with_mock():
    mock_tavily = MagicMock()
    mock_tavily.search.return_value = {
        "results": [
            {
                "title": "Quantum Leap in AI",
                "url": "https://technologyreview.com/quantum-ai",
                "content": "Researchers have demonstrated a quantum algorithm for AI...",
                "published_date": "2026-03-01",
            }
        ]
    }

    searcher = TavilySearch(api_key="test_dummy_key")
    searcher.client = mock_tavily

    results = searcher.search_query("quantum computing in AI", max_results=3, iteration=1)
    assert len(results) == 1
    assert results[0]["title"] == "Quantum Leap in AI"
    assert results[0]["search_query"] == "quantum computing in AI"
    assert results[0]["research_iteration"] == 1


def test_query_caching_avoids_repeated_searches():
    mock_tavily = MagicMock()
    mock_tavily.search.return_value = {"results": [{"title": "Test", "url": "https://test.com"}]}

    searcher = TavilySearch(api_key="test_dummy_key")
    searcher.client = mock_tavily

    # First search
    res1 = searcher.search_query("Solid state batteries")
    assert len(res1) == 1
    assert mock_tavily.search.call_count == 1

    # Second search with slightly different whitespace / casing
    res2 = searcher.search_query("  solid state batteries  ")
    assert len(res2) == 0
    # Must still be 1 (second call was skipped due to query cache)
    assert mock_tavily.search.call_count == 1


def test_search_failure_does_not_crash():
    mock_tavily = MagicMock()
    mock_tavily.search.side_effect = Exception("Connection timeout to Tavily")

    searcher = TavilySearch(api_key="test_dummy_key")
    searcher.client = mock_tavily

    # Should catch error, log warning, and return empty list
    results = searcher.search_query("Failing query")
    assert results == []


def test_search_multiple_combines_and_deduplicates():
    mock_tavily = MagicMock()
    mock_tavily.search.side_effect = [
        {"results": [{"title": "A", "url": "https://shared.com/page"}]},
        {"results": [{"title": "A copy", "url": "https://shared.com/page?ref=site"}, {"title": "B", "url": "https://unique.com"}]},
    ]

    searcher = TavilySearch(api_key="test_dummy_key")
    searcher.client = mock_tavily

    combined = searcher.search_multiple(["Query 1", "Query 2"])
    assert len(combined) == 2
    assert combined[0]["url"] == "https://shared.com/page"
    assert combined[1]["url"] == "https://unique.com"
