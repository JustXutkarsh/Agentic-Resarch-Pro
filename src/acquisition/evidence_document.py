"""
EvidenceDocument / ScrapedDocument definitions for Agentic Research PRO acquisition subsystem.
Provides 100% backward compatibility with legacy ScrapedDocument while preserving
granular provenance, acquisition methods (http, pdf, playwright), and structured tables.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List


import hashlib
from urllib.parse import urlparse

@dataclass
class ScrapedDocument:
    """
    Normalized research evidence document acquired across HTTP, PDF, or Playwright.
    Fully backward-compatible with legacy scraper representations while providing
    granular provenance tracking for research sessions and authority tiers.
    """
    url: str
    title: str
    content: str
    search_query: str = ""
    research_iteration: int = 1
    source_score: float = 0.5
    char_count: int = 0
    acquisition_method: str = "http"  # "http" | "pdf" | "playwright"
    retrieval_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tables: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    research_session_id: str = ""
    document_id: str = ""
    source_domain: str = ""
    source_type: str = "web"  # "peer_reviewed" | "government" | "standards" | "preprint" | "corporate_technical" | "technical_journalism" | "commercial_blog"
    authority_tier: int = 3
    publisher: str = ""

    def __post_init__(self):
        if self.content and not self.char_count:
            self.char_count = len(self.content)
        if not self.document_id:
            if self.url:
                url_hash = hashlib.md5(self.url.encode("utf-8")).hexdigest()[:12]
                self.document_id = f"doc_{url_hash}"
            else:
                self.document_id = f"doc_{hashlib.md5((self.title + self.content[:100]).encode('utf-8')).hexdigest()[:12]}"
        if not self.source_domain and self.url:
            try:
                parsed = urlparse(self.url)
                self.source_domain = parsed.netloc.lower()
            except Exception:
                self.source_domain = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "search_query": self.search_query,
            "research_iteration": self.research_iteration,
            "source_score": self.source_score,
            "char_count": self.char_count,
            "acquisition_method": self.acquisition_method,
            "retrieval_timestamp": self.retrieval_timestamp,
            "tables": self.tables,
            "metadata": self.metadata,
            "research_session_id": self.research_session_id,
            "document_id": self.document_id,
            "source_domain": self.source_domain,
            "source_type": self.source_type,
            "authority_tier": self.authority_tier,
            "publisher": self.publisher,
        }


# Alias for explicit semantic clarity in new acquisition components
EvidenceDocument = ScrapedDocument
