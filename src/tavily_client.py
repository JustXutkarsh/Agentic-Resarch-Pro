"""
Multi-Query Web Search Client powered by Tavily API.
Includes query caching, URL normalization, source deduplication,
and error-tolerant multi-query execution.
"""

import logging
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from tavily import TavilyClient

logger = logging.getLogger(__name__)

# Common tracking parameters to strip during URL normalization
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "fbclid", "gclid", "msclkid", "_ga", "mc_cid", "mc_eid"
}


def normalize_url(url: str) -> str:
    """
    Normalize a URL for reliable deduplication:
    - Lowercase scheme and domain
    - Strip trailing slashes
    - Strip URL fragments (#...)
    - Strip tracking query parameters (utm_*, ref, etc.)
    """
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip("/")

        # Filter query params
        query_dict = parse_qs(parsed.query, keep_blank_values=False)
        filtered_query = {
            k: v for k, v in query_dict.items() if k.lower() not in TRACKING_PARAMS
        }
        clean_query = urlencode(filtered_query, doseq=True)

        return urlunparse((scheme, netloc, path, "", clean_query, ""))
    except Exception:
        return url.strip().rstrip("/")


def deduplicate_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate sources based on normalized URL while preserving initial order.
    """
    seen_urls: Set[str] = set()
    unique_sources: List[Dict[str, Any]] = []

    for src in sources:
        url = src.get("url", "")
        norm_url = normalize_url(url)
        if norm_url and norm_url not in seen_urls:
            seen_urls.add(norm_url)
            # Store normalized URL in the record
            src_copy = dict(src)
            src_copy["normalized_url"] = norm_url
            unique_sources.append(src_copy)

    return unique_sources


class TavilySearch:
    """Multi-query search client with query caching and error tolerance."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.client: Optional[TavilyClient] = None
        if self.api_key:
            try:
                self.client = TavilyClient(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize TavilyClient: {e}")
        # Cache of normalized queries that have already been executed
        self.searched_queries: Dict[str, Dict[str, Any]] = {}

    def _normalize_query(self, query: str) -> str:
        """Normalize query string: lowercase, strip, collapse multiple spaces."""
        return re.sub(r"\s+", " ", query.strip().lower())

    def search_query(
        self,
        query: str,
        max_results: int = 5,
        iteration: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Execute a single search query with caching.
        Returns list of source dicts with metadata.
        """
        norm_query = self._normalize_query(query)
        if not norm_query:
            return []

        # Check search query cache
        if norm_query in self.searched_queries:
            logger.info(f"Query already searched in this session, skipping: '{query}'")
            return []

        self.searched_queries[norm_query] = {
            "query": query,
            "iteration": iteration,
            "timestamp": datetime.now().isoformat(),
        }

        if not self.client:
            logger.warning("Tavily API key is missing or client is not initialized.")
            return []

        try:
            resp = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",
                include_raw_content=False,
            )
            raw_results = resp.get("results", []) if isinstance(resp, dict) else []

            out = []
            for r in raw_results:
                out.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content") or r.get("snippet", ""),
                    "published_date": r.get("published_date"),
                    "search_query": query,
                    "research_iteration": iteration,
                })
            return out

        except Exception as e:
            logger.warning(f"Tavily search failed for query '{query}': {e}")
            return []

    def search_multiple(
        self,
        queries: List[str],
        max_results_per_query: int = 5,
        iteration: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Execute search across multiple queries and return combined, deduplicated sources.
        """
        all_sources: List[Dict[str, Any]] = []

        for q in queries:
            results = self.search_query(
                query=q,
                max_results=max_results_per_query,
                iteration=iteration,
            )
            all_sources.extend(results)

        return deduplicate_sources(all_sources)