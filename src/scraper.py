"""
Robust Web and PDF Scraping Pipeline for Agentic Research PRO.
Integrates deep text cleaning, timeout enforcement, domain filtering,
and fault-tolerant per-source error recovery via the Acquisition Subsystem.
"""

import logging
import re
from typing import List, Dict, Any, Tuple, Optional
import requests
from bs4 import BeautifulSoup
from src.cleaner import clean_text
from src.acquisition.evidence_document import ScrapedDocument, EvidenceDocument
from src.acquisition.source_router import is_supported_url, BLOCKED_DOMAINS

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
    progress_callback: Optional[Any] = None,
) -> Optional[ScrapedDocument]:
    """
    Scrape a single source dictionary using the SourceRouter.
    Returns ScrapedDocument on success, or None on failure.
    """
    from src.acquisition.source_router import SourceRouter
    from src.acquisition.http_acquirer import HttpAcquirer
    from src.acquisition.pdf_acquirer import PdfAcquirer
    from src.acquisition.playwright_agent import PlaywrightAgent

    http_acq = HttpAcquirer(timeout=timeout, requests_get=requests.get)
    pdf_acq = PdfAcquirer(timeout=timeout)
    pw_agent = PlaywrightAgent()
    router = SourceRouter(http_acquirer=http_acq, pdf_acquirer=pdf_acq, playwright_agent=pw_agent)
    
    doc, _ = router.route_source(source, max_chars=max_chars, progress_callback=progress_callback)
    return doc


def scrape_sources(
    sources: List[Dict[str, Any]],
    timeout: int = 12,
    max_chars: int = 8000,
    progress_callback: Optional[Any] = None,
) -> Tuple[List[ScrapedDocument], List[Dict[str, Any]]]:
    """
    Scrapes all accepted sources in sequence using the SourceRouter.
    Returns:
      (successful_documents, failed_sources)
    Guarantees non-blocking execution: individual errors do not stop remaining sources.
    """
    from src.acquisition.source_router import SourceRouter
    from src.acquisition.http_acquirer import HttpAcquirer
    from src.acquisition.pdf_acquirer import PdfAcquirer
    from src.acquisition.playwright_agent import PlaywrightAgent

    http_acq = HttpAcquirer(timeout=timeout, requests_get=requests.get)
    pdf_acq = PdfAcquirer(timeout=timeout)
    pw_agent = PlaywrightAgent()
    router = SourceRouter(http_acquirer=http_acq, pdf_acquirer=pdf_acq, playwright_agent=pw_agent)

    docs, failures, _ = router.acquire_sources(sources, max_chars=max_chars, progress_callback=progress_callback)
    return docs, failures


def scrape_urls(urls: List[str], timeout: int = 12) -> List[str]:
    """
    Backward-compatible scraper helper that takes a list of URLs and returns raw text strings.
    """
    fake_sources = [{"url": u, "title": u} for u in urls]
    docs, _ = scrape_sources(fake_sources, timeout=timeout)
    return [d.content for d in docs]
