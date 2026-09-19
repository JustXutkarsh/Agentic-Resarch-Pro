"""
EvidenceDocument / ScrapedDocument definitions for Agentic Research PRO acquisition subsystem.
Provides 100% backward compatibility with legacy ScrapedDocument while preserving
granular provenance, acquisition methods (http, pdf, playwright), and structured tables.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List


@dataclass
class ScrapedDocument:
    """
    Normalized research evidence document acquired across HTTP, PDF, or Playwright.
    Fully backward-compatible with legacy scraper representations.
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

    def __post_init__(self):
        if self.content and not self.char_count:
            self.char_count = len(self.content)

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
        }


# Alias for explicit semantic clarity in new acquisition components
EvidenceDocument = ScrapedDocument
