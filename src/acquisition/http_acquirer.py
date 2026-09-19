"""
HTTP Acquisition Module for Agentic Research PRO.
Executes fast static HTML extraction and detects dynamic JavaScript signals
that require browser escalation.
"""

import logging
import re
from typing import Optional, Dict, Any, Tuple, List
import requests
from bs4 import BeautifulSoup
from src.cleaner import clean_text
from src.acquisition.evidence_document import EvidenceDocument

logger = logging.getLogger(__name__)

RESEARCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36 (AcademicResearchBot/2.0)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

SPA_EMPTY_PATTERNS = [
    re.compile(r'<div\s+id=["\'](?:root|app|__next)["\']\s*>\s*</div>', re.IGNORECASE),
    re.compile(r'<div\s+id=["\']main-content["\']\s*>\s*</div>', re.IGNORECASE),
    re.compile(r'<body[^>]*>\s*<noscript>[^<]*</noscript>\s*<script', re.IGNORECASE),
]

JS_REQUIRED_KEYWORDS = [
    "please enable javascript",
    "you need to enable javascript",
    "javascript is required",
    "enable javascript to run this app",
    "javascript is disabled",
    "browser does not support javascript",
]


def extract_html_tables(soup: BeautifulSoup) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extract meaningful HTML tables into markdown-compatible text and structured records.
    Preserves column and row relationships.
    """
    table_records: List[Dict[str, Any]] = []
    markdown_tables: List[str] = []

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows or len(rows) < 2:
            continue

        # Extract headers
        headers = []
        header_row = rows[0]
        th_tags = header_row.find_all(["th", "td"])
        if th_tags:
            headers = [clean_text(th.get_text()) for th in th_tags]
            headers = [h for h in headers if h]

        if not headers:
            continue

        # Extract data rows
        data_rows = []
        for r in rows[1:]:
            cells = [clean_text(td.get_text()) for td in r.find_all(["td", "th"])]
            if any(cells):
                # Align length
                padded = (cells + [""] * len(headers))[:len(headers)]
                data_rows.append(padded)

        if not data_rows:
            continue

        # Build markdown table string
        md_lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        for row in data_rows:
            md_lines.append("| " + " | ".join(row) + " |")

        md_table = "\n".join(md_lines)
        markdown_tables.append(md_table)
        table_records.append({
            "headers": headers,
            "rows": data_rows,
            "markdown": md_table,
        })

    return "\n\n".join(markdown_tables), table_records


class HttpAcquirer:
    """Acquires and evaluates static HTML web content."""

    def __init__(self, timeout: int = 12, requests_get: Optional[Any] = None):
        self.timeout = timeout
        self.requests_get = requests_get or requests.get

    def detect_dynamic_signals(
        self,
        html_raw: str,
        extracted_text: Optional[str],
    ) -> Tuple[bool, str]:
        """
        Detect whether a page requires client-side JavaScript rendering or interaction.
        Returns (is_dynamic, reason).
        """
        if not html_raw:
            return False, ""

        lower_html = html_raw.lower()
        text_len = len(extracted_text or "")

        # Signal 1: Explicit noscript / JS required warnings
        for kw in JS_REQUIRED_KEYWORDS:
            if kw in lower_html:
                return True, f"Explicit JS dependency detected: '{kw}'"

        # Signal 2: Empty SPA mounting containers
        for pattern in SPA_EMPTY_PATTERNS:
            if pattern.search(html_raw):
                return True, "Empty single-page application mounting container detected"

        # Signal 3: Disproportionately low readable text compared to raw payload
        if len(html_raw) > 5000 and text_len < 250:
            if "<script" in lower_html:
                return True, f"Low text yield ({text_len} chars) with heavy script assets ({len(html_raw)} bytes)"

        # Signal 4: Interactive/dynamic table or app shells without server-rendered rows
        if "react" in lower_html or "vue" in lower_html or "angular" in lower_html:
            if text_len < 300:
                return True, "Client-side web framework shell with sparse initial HTML"

        return False, ""

    def acquire(
        self,
        source: Dict[str, Any],
        max_chars: int = 8000,
    ) -> Tuple[Optional[EvidenceDocument], bool, str]:
        """
        Fetch HTML source via HTTP request.
        Returns:
            (EvidenceDocument or None, requires_playwright_bool, reason_string)
        """
        if isinstance(source, str):
            source = {"url": source, "title": "", "search_query": "", "research_iteration": 1, "source_score": 0.5}

        url = source.get("url", "").strip()
        title = source.get("title", "")
        query = source.get("search_query", "")
        iteration = source.get("research_iteration", 1)
        score = source.get("source_score", 0.5)

        try:
            resp = self.requests_get(url, timeout=self.timeout, headers=RESEARCH_HEADERS)
            if resp.status_code != 200:
                logger.info(f"HTTP GET returned status {resp.status_code} for {url}")
                # 403 or non-200 might still work in Playwright if bot detection blocks standard requests
                if resp.status_code in (403, 503):
                    return None, True, f"HTTP status {resp.status_code} (potential client verification required)"
                return None, False, f"HTTP status {resp.status_code}"

            content_type = resp.headers.get("Content-Type", "").lower()
            if "application/pdf" in content_type:
                return None, False, "application/pdf"

            raw_html = resp.text
            soup = BeautifulSoup(raw_html, "html.parser")

            # Extract structured tables before decomposing tags
            table_md, table_records = extract_html_tables(soup)

            # Strip script, style, nav, footer, header, aside, noscript
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                tag.decompose()

            # Extract body paragraphs
            paragraphs = [clean_text(p.get_text(" ", strip=True)) for p in soup.find_all("p")]
            paragraphs = [p for p in paragraphs if len(p) > 20]
            body_text = " ".join(paragraphs)

            if len(body_text) < 200:
                # Fallback to general visible text
                raw_text = clean_text(soup.get_text(" ", strip=True))
                body_text = raw_text if len(raw_text) > len(body_text) else body_text

            # Append structured table text if present
            if table_md:
                body_text = f"{body_text}\n\n### Extracted Data Tables:\n{table_md}"

            # Check dynamic signals
            is_dynamic, dynamic_reason = self.detect_dynamic_signals(raw_html, body_text)

            # If dynamic signals are present and text is insufficient or empty
            if is_dynamic and len(body_text) < 350:
                return None, True, dynamic_reason

            if len(body_text) >= 200:
                truncated = body_text[:max_chars]
                doc = EvidenceDocument(
                    url=url,
                    title=title or (soup.title.string.strip() if soup.title and soup.title.string else url),
                    content=truncated,
                    search_query=query,
                    research_iteration=iteration,
                    source_score=score,
                    char_count=len(truncated),
                    acquisition_method="http",
                    tables=table_records,
                    metadata=source,
                )
                return doc, is_dynamic, dynamic_reason

            # If text is too short, consider whether Playwright might extract more
            return None, True, f"Insufficient text ({len(body_text)} chars); escalating to dynamic browser"

        except Exception as e:
            logger.info(f"HTTP acquisition failed for {url}: {e}")
            return None, True, f"HTTP exception: {e}"
