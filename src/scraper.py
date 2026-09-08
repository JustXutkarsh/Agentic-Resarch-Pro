"""
Robust Web and PDF Scraping Pipeline for Agentic Research PRO.
Integrates deep text cleaning, timeout enforcement, domain filtering,
and fault-tolerant per-source error recovery.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
import requests
from bs4 import BeautifulSoup
from src.cleaner import clean_text

logger = logging.getLogger(__name__)

# User-Agent mimicking a modern academic research client
RESEARCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36 (AcademicResearchBot/2.0)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Domains to skip because they require login walls, complex JS renderers, or are video-only
BLOCKED_DOMAINS = [
    "youtube.com", "youtu.be", "twitter.com", "x.com",
    "instagram.com", "tiktok.com", "facebook.com", "linkedin.com"
]


@dataclass
class ScrapedDocument:
    """Represents a successfully scraped and sanitized document."""
    url: str
    title: str
    content: str
    search_query: str = ""
    research_iteration: int = 1
    source_score: float = 0.5
    char_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.content and not self.char_count:
            self.char_count = len(self.content)


def is_supported_url(url: str) -> bool:
    """Check if URL is supported for scraping."""
    if not url:
        return False
    lower = url.lower()
    for domain in BLOCKED_DOMAINS:
        if domain in lower:
            return False
    return lower.startswith("http://") or lower.startswith("https://")


def scrape_pdf_content(url: str, timeout: int = 12) -> Optional[str]:
    """Download and extract text from a PDF URL using PyMuPDF."""
    try:
        import pymupdf
        resp = requests.get(url, timeout=timeout, headers=RESEARCH_HEADERS, stream=True)
        if resp.status_code != 200:
            return None

        # Guard against excessively large downloads (>20MB)
        content_length = resp.headers.get("Content-Length")
        if content_length and int(content_length) > 20 * 1024 * 1024:
            logger.warning(f"PDF exceeds size limit: {url}")
            return None

        doc = pymupdf.open(stream=resp.content, filetype="pdf")
        extracted_pages = []
        # Limit to first 25 pages to avoid memory spikes
        for page_idx in range(min(len(doc), 25)):
            page_text = doc[page_idx].get_text()
            if page_text:
                extracted_pages.append(page_text)

        full_raw = "\n".join(extracted_pages)
        sanitized = clean_text(full_raw)
        return sanitized if len(sanitized) > 200 else None

    except Exception as e:
        logger.warning(f"PDF scraping failed for {url}: {e}")
        return None


def scrape_html_content(html: str) -> Optional[str]:
    """Parse HTML and extract readable text using BeautifulSoup and cleaner."""
    if not html:
        return None

    try:
        soup = BeautifulSoup(html, "html.parser")

        # Remove irrelevant elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            tag.decompose()

        # Extract main article/body paragraphs first
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        body_text = " ".join(paragraphs)

        if len(body_text) > 300:
            return clean_text(body_text)

        # Fallback to general visible text
        raw_text = soup.get_text(" ", strip=True)
        if len(raw_text) > 300:
            return clean_text(raw_text)

        return None
    except Exception as e:
        logger.warning(f"HTML parsing failed: {e}")
        return None


def scrape_single_source(
    source: Dict[str, Any],
    timeout: int = 12,
    max_chars: int = 8000,
) -> Optional[ScrapedDocument]:
    """
    Scrape a single source dictionary.
    Returns ScrapedDocument on success, or None on failure.
    """
    url = source.get("url", "").strip()
    title = source.get("title", "")
    query = source.get("search_query", "")
    iteration = source.get("research_iteration", 1)
    score = source.get("source_score", 0.5)

    if not is_supported_url(url):
        logger.info(f"Skipping unsupported URL domain: {url}")
        return None

    try:
        content: Optional[str] = None

        if url.lower().endswith(".pdf") or "/pdf/" in url.lower():
            content = scrape_pdf_content(url, timeout=timeout)
        else:
            resp = requests.get(url, timeout=timeout, headers=RESEARCH_HEADERS)
            if resp.status_code == 200:
                # If the Content-Type header indicates PDF
                if "application/pdf" in resp.headers.get("Content-Type", "").lower():
                    content = scrape_pdf_content(url, timeout=timeout)
                else:
                    content = scrape_html_content(resp.text)

        if content and len(content) >= 200:
            truncated = content[:max_chars]
            return ScrapedDocument(
                url=url,
                title=title,
                content=truncated,
                search_query=query,
                research_iteration=iteration,
                source_score=score,
                char_count=len(truncated),
                metadata=source,
            )

        return None

    except Exception as e:
        logger.warning(f"Scraping failed for {url}: {e}")
        return None


def scrape_sources(
    sources: List[Dict[str, Any]],
    timeout: int = 12,
    max_chars: int = 8000,
) -> Tuple[List[ScrapedDocument], List[Dict[str, Any]]]:
    """
    Scrapes all accepted sources in sequence.
    Returns:
      (successful_documents, failed_sources)
    Guarantees non-blocking execution: individual errors do not stop remaining sources.
    """
    documents: List[ScrapedDocument] = []
    failures: List[Dict[str, Any]] = []

    for src in sources:
        doc = scrape_single_source(src, timeout=timeout, max_chars=max_chars)
        if doc is not None:
            documents.append(doc)
        else:
            failures.append(src)

    return documents, failures


def scrape_urls(urls: List[str], timeout: int = 12) -> List[str]:
    """
    Backward-compatible scraper helper that takes a list of URLs and returns raw text strings.
    """
    fake_sources = [{"url": u, "title": u} for u in urls]
    docs, _ = scrape_sources(fake_sources, timeout=timeout)
    return [d.content for d in docs]
