"""
SourceRouter Module for Agentic Research PRO.
Intelligently routes candidate URLs between HTTP, PDF, and Playwright acquisition
based on URL heuristics, response headers, and dynamic DOM signals.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from src.acquisition.evidence_document import EvidenceDocument
from src.acquisition.http_acquirer import HttpAcquirer
from src.acquisition.pdf_acquirer import PdfAcquirer
from src.acquisition.playwright_agent import PlaywrightAgent
from src.config import PLAYWRIGHT_ENABLED

logger = logging.getLogger(__name__)

BLOCKED_DOMAINS = [
    "youtube.com", "youtu.be", "twitter.com", "x.com",
    "instagram.com", "tiktok.com", "facebook.com", "linkedin.com"
]


def is_supported_url(url: str) -> bool:
    """Check if URL is supported for acquisition."""
    if not url:
        return False
    lower = url.lower()
    for domain in BLOCKED_DOMAINS:
        if domain in lower:
            return False
    return lower.startswith("http://") or lower.startswith("https://")


class SourceRouter:
    """
    Intelligently routes candidate research sources to the optimal acquisition engine:
    - PDF documents -> PdfAcquirer
    - Static HTML -> HttpAcquirer
    - Dynamic/JS-rendered/Interactive -> PlaywrightAgent
    Includes automatic fallback between engines.
    """

    def __init__(
        self,
        http_acquirer: Optional[HttpAcquirer] = None,
        pdf_acquirer: Optional[PdfAcquirer] = None,
        playwright_agent: Optional[PlaywrightAgent] = None,
    ):
        self.http_acquirer = http_acquirer or HttpAcquirer()
        self.pdf_acquirer = pdf_acquirer or PdfAcquirer()
        self.playwright_agent = playwright_agent or PlaywrightAgent()

    def route_source(
        self,
        source: Dict[str, Any],
        research_objective: str = "",
        max_chars: int = 8000,
        progress_callback: Optional[Any] = None,
    ) -> Tuple[Optional[EvidenceDocument], str]:
        """
        Acquires a single source using the appropriate engine.
        Returns:
            (EvidenceDocument or None, acquisition_method: "http"|"pdf"|"playwright"|"failed")
        """
        if isinstance(source, str):
            source = {"url": source, "title": "", "search_query": "", "research_iteration": 1, "source_score": 0.5}

        url = source.get("url", "").strip()

        if not is_supported_url(url):
            logger.info(f"Skipping unsupported URL domain: {url}")
            return None, "unsupported"

        # 1. Check for explicit PDF URL
        if url.lower().endswith(".pdf") or "/pdf/" in url.lower():
            if progress_callback:
                progress_callback("ACQUISITION_PDF", 0.33, f"Acquiring academic PDF: {url[:50]}...")
            doc = self.pdf_acquirer.acquire(source, max_chars=max_chars)
            if doc:
                return doc, "pdf"
            return None, "failed_pdf"

        # 2. Attempt Static HTTP Acquisition
        http_doc, requires_playwright, reason = self.http_acquirer.acquire(source, max_chars=max_chars)

        # If HTTP says it's a PDF by content-type
        if reason == "application/pdf":
            doc = self.pdf_acquirer.acquire(source, max_chars=max_chars)
            if doc:
                return doc, "pdf"
            return None, "failed_pdf"

        # If HTTP produced a clean, complete document without dynamic signals, accept it!
        if http_doc is not None and not requires_playwright:
            return http_doc, "http"

        # 3. Dynamic escalation to Playwright Agent
        if PLAYWRIGHT_ENABLED and requires_playwright:
            if progress_callback:
                progress_callback(
                    "PLAYWRIGHT_DETECT",
                    0.33,
                    f"Dynamic content detected ({reason[:35]}); deploying Playwright agent..."
                )
            logger.info(f"Escalating {url} to Playwright agent: {reason}")
            pw_doc = self.playwright_agent.acquire(
                source,
                research_objective=research_objective,
                max_chars=max_chars,
                progress_callback=progress_callback,
            )

            if pw_doc:
                return pw_doc, "playwright"
            else:
                logger.info(f"Playwright acquisition returned None for {url}; attempting HTTP fallback")

        # 4. Fallback: if Playwright failed or was disabled, use HTTP doc if available
        if http_doc is not None:
            return http_doc, "http"

        return None, "failed"

    def acquire_sources(
        self,
        sources: List[Dict[str, Any]],
        research_objective: str = "",
        max_chars: int = 8000,
        progress_callback: Optional[Any] = None,
    ) -> Tuple[List[EvidenceDocument], List[Dict[str, Any]], Dict[str, int]]:
        """
        Process a batch of sources through the routing pipeline.
        Returns:
            (successful_documents, failed_sources, metrics_summary)
        """
        documents: List[EvidenceDocument] = []
        failures: List[Dict[str, Any]] = []

        metrics = {
            "http_acquisitions": 0,
            "pdf_acquisitions": 0,
            "playwright_acquisitions": 0,
            "successful_playwright": 0,
            "failed_playwright": 0,
            "pages_visited": 0,
        }

        try:
            for idx, src in enumerate(sources):
                doc, method = self.route_source(
                    src,
                    research_objective=research_objective,
                    max_chars=max_chars,
                    progress_callback=progress_callback,
                )

                if doc is not None:
                    documents.append(doc)
                    if method == "http":
                        metrics["http_acquisitions"] += 1
                    elif method == "pdf":
                        metrics["pdf_acquisitions"] += 1
                    elif method == "playwright":
                        metrics["playwright_acquisitions"] += 1
                        metrics["successful_playwright"] += 1
                        metrics["pages_visited"] += doc.metadata.get("pages_visited", 1)
                else:
                    failures.append(src)
                    if "playwright" in method or "dynamic" in method:
                        metrics["failed_playwright"] += 1

        finally:
            # Clean up browser runtime after batch completes
            self.playwright_agent.close()

        return documents, failures, metrics
