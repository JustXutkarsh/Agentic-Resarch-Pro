"""
PDF Acquisition Module for Agentic Research PRO.
Extracts clean textual evidence from remote PDF documents using PyMuPDF.
"""

import logging
from typing import Optional, Dict, Any
import requests
from src.cleaner import clean_text
from src.acquisition.evidence_document import EvidenceDocument

logger = logging.getLogger(__name__)

RESEARCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36 (AcademicResearchBot/2.0)"
    ),
    "Accept": "application/pdf,*/*;q=0.8",
}


class PdfAcquirer:
    """Acquires and sanitizes evidence from PDF documents."""

    def __init__(self, timeout: int = 12, max_pages: int = 25, max_bytes: int = 20 * 1024 * 1024):
        self.timeout = timeout
        self.max_pages = max_pages
        self.max_bytes = max_bytes

    def acquire(self, source: Dict[str, Any], max_chars: int = 8000) -> Optional[EvidenceDocument]:
        """
        Download and parse PDF document, returning normalized EvidenceDocument.
        """
        if isinstance(source, str):
            source = {"url": source, "title": "", "search_query": "", "research_iteration": 1, "source_score": 0.5}

        url = source.get("url", "").strip()
        title = source.get("title", "")
        query = source.get("search_query", "")
        iteration = source.get("research_iteration", 1)
        score = source.get("source_score", 0.5)

        try:
            import pymupdf
            resp = requests.get(url, timeout=self.timeout, headers=RESEARCH_HEADERS, stream=True)
            if resp.status_code != 200:
                logger.warning(f"PDF acquisition returned HTTP {resp.status_code} for {url}")
                return None

            content_length = resp.headers.get("Content-Length")
            if content_length and int(content_length) > self.max_bytes:
                logger.warning(f"PDF exceeds size limit ({content_length} bytes): {url}")
                return None

            doc = pymupdf.open(stream=resp.content, filetype="pdf")
            extracted_pages = []
            page_limit = min(len(doc), self.max_pages)
            for page_idx in range(page_limit):
                page_text = doc[page_idx].get_text()
                if page_text:
                    extracted_pages.append(page_text)

            full_raw = "\n".join(extracted_pages)
            sanitized = clean_text(full_raw)

            if len(sanitized) < 200:
                return None

            truncated = sanitized[:max_chars]
            return EvidenceDocument(
                url=url,
                title=title or (f"PDF Document: {url.split('/')[-1]}"),
                content=truncated,
                search_query=query,
                research_iteration=iteration,
                source_score=score,
                char_count=len(truncated),
                acquisition_method="pdf",
                metadata=source,
            )

        except Exception as e:
            logger.warning(f"PDF acquisition failed for {url}: {e}")
            return None
