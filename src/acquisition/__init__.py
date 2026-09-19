"""
Acquisition Package for Agentic Research PRO.
Provides unified, resilient evidence acquisition across static HTTP, PDF documents,
and task-oriented Playwright browser rendering.
"""

from src.acquisition.evidence_document import EvidenceDocument
from src.acquisition.http_acquirer import HttpAcquirer
from src.acquisition.pdf_acquirer import PdfAcquirer
from src.acquisition.playwright_agent import PlaywrightAgent
from src.acquisition.source_router import SourceRouter, is_supported_url

__all__ = [
    "EvidenceDocument",
    "HttpAcquirer",
    "PdfAcquirer",
    "PlaywrightAgent",
    "SourceRouter",
    "is_supported_url",
]
