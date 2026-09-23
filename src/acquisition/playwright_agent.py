"""
Playwright Research Acquisition Agent for Agentic Research PRO.
Task-oriented, read-only browser agent for acquiring evidence from
JavaScript-rendered, dynamic, interactive, and multi-page web sources.
"""

import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from src.cleaner import clean_text
from src.acquisition.evidence_document import EvidenceDocument
from src.config import (
    PLAYWRIGHT_ENABLED,
    PLAYWRIGHT_HEADLESS,
    PLAYWRIGHT_MAX_PAGES,
    PLAYWRIGHT_MAX_SCROLLS,
    PLAYWRIGHT_TIMEOUT_MS,
)

logger = logging.getLogger(__name__)

RESEARCH_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 (AcademicResearchBot/2.0)"
)

# Blocked signals indicating security gates, paywalls, or authentication barriers
BLOCKED_PAGE_PATTERNS = [
    "verify you are human",
    "attention required! | cloudflare",
    "access denied",
    "pardon our interruption",
    "security check to continue",
    "please log in to continue",
    "sign in to continue",
    "subscribe to read this article",
]

EXPANDABLE_BUTTON_SELECTORS = [
    "button:has-text('Show more')",
    "button:has-text('Read more')",
    "button:has-text('View all')",
    "button:has-text('Expand')",
    "a:has-text('Read more')",
    "summary",
    "[aria-expanded='false']",
]

PAGINATION_SELECTORS = [
    "a[rel='next']",
    "button:has-text('Next')",
    "a:has-text('Next')",
    "a:has-text('Next page')",
    "a:has-text('›')",
    "button[aria-label*='Next']",
    "a[aria-label*='Next']",
]


class PlaywrightAgent:
    """
    Task-oriented, bounded, read-only Playwright browser acquisition agent.
    Safely navigates, renders JavaScript, extracts tables, and handles dynamic content.
    """

    def __init__(
        self,
        headless: bool = PLAYWRIGHT_HEADLESS,
        timeout_ms: int = PLAYWRIGHT_TIMEOUT_MS,
        max_scrolls: int = PLAYWRIGHT_MAX_SCROLLS,
        max_pages: int = PLAYWRIGHT_MAX_PAGES,
    ):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.max_scrolls = max_scrolls
        self.max_pages = max_pages
        self._playwright = None
        self._browser = None

    def _ensure_browser(self):
        """Lazy-initialize a shared Playwright Chromium browser instance."""
        if self._browser is None:
            from playwright.sync_api import sync_playwright
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-gpu",
                    "--disable-extensions",
                    "--mute-audio",
                    "--js-flags=--max-old-space-size=256",
                ],
            )
        return self._browser

    def close(self):
        """Clean up browser and Playwright runtime without leaving orphan processes."""
        try:
            if self._browser:
                self._browser.close()
                self._browser = None
        except Exception as e:
            logger.debug(f"Error closing browser: {e}")
        try:
            if self._playwright:
                self._playwright.stop()
                self._playwright = None
        except Exception as e:
            logger.debug(f"Error stopping playwright: {e}")

    def __enter__(self):
        self._ensure_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _check_blocked_page(self, page_content: str) -> bool:
        """Check if page is blocked by authentication, CAPTCHA, or paywall."""
        lower = page_content.lower()
        for pattern in BLOCKED_PAGE_PATTERNS:
            if pattern in lower:
                return True
        return False

    def _extract_tables_from_page(self, page) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Extract meaningful HTML tables via DOM evaluation preserving column/row relationships.
        Converts extracted tables to Markdown.
        """
        try:
            raw_tables = page.evaluate("""() => {
                const results = [];
                const tables = document.querySelectorAll('table');
                for (const table of tables) {
                    const rows = Array.from(table.querySelectorAll('tr'));
                    if (rows.length < 2) continue;
                    const headers = Array.from(rows[0].querySelectorAll('th, td'))
                        .map(c => c.innerText.trim())
                        .filter(Boolean);
                    const dataRows = [];
                    for (let i = 1; i < rows.length; i++) {
                        const cells = Array.from(rows[i].querySelectorAll('td, th'))
                            .map(c => c.innerText.trim());
                        if (cells.some(Boolean)) {
                            dataRows.push(cells);
                        }
                    }
                    if (headers.length > 0 && dataRows.length > 0) {
                        results.push({ headers, rows: dataRows });
                    }
                }
                return results;
            }""")

            markdown_tables = []
            table_records = []

            for tbl in (raw_tables or []):
                headers = tbl.get("headers", [])
                rows = tbl.get("rows", [])
                if not headers or not rows:
                    continue

                md_lines = [
                    "| " + " | ".join(headers) + " |",
                    "| " + " | ".join(["---"] * len(headers)) + " |",
                ]
                for row in rows:
                    padded = (row + [""] * len(headers))[:len(headers)]
                    md_lines.append("| " + " | ".join(padded) + " |")

                md_table = "\n".join(md_lines)
                markdown_tables.append(md_table)
                table_records.append({
                    "headers": headers,
                    "rows": rows,
                    "markdown": md_table,
                })

            return "\n\n".join(markdown_tables), table_records
        except Exception as e:
            logger.debug(f"Table extraction failed: {e}")
            return "", []

    def _expand_interactive_sections(self, page) -> int:
        """Expand accordions, 'read more', and 'show more' controls bounded to max 3 clicks."""
        expanded_count = 0
        for selector in EXPANDABLE_BUTTON_SELECTORS:
            if expanded_count >= 3:
                break
            try:
                elements = page.locator(selector).all()
                for el in elements[:2]:
                    if expanded_count >= 3:
                        break
                    if el.is_visible():
                        el.click(timeout=1000)
                        page.wait_for_timeout(300)
                        expanded_count += 1
            except Exception:
                continue
        return expanded_count

    def _perform_bounded_scroll(self, page) -> int:
        """Perform bounded scrolling to trigger lazy-loaded dynamic content."""
        scroll_count = 0
        for _ in range(self.max_scrolls):
            try:
                prev_height = page.evaluate("document.body.scrollHeight")
                page.evaluate("window.scrollBy(0, window.innerHeight * 1.5)")
                page.wait_for_timeout(400)
                curr_height = page.evaluate("document.body.scrollHeight")
                scroll_count += 1
                if curr_height <= prev_height:
                    break
            except Exception:
                break
        return scroll_count

    def acquire(
        self,
        source: Dict[str, Any],
        research_objective: str = "",
        max_chars: int = 8000,
        progress_callback: Optional[Any] = None,
    ) -> Optional[EvidenceDocument]:
        """
        Execute bounded, read-only browser acquisition for a single source.
        Returns EvidenceDocument on success or None on failure.
        """
        if not PLAYWRIGHT_ENABLED:
            logger.info("Playwright acquisition is disabled via configuration.")
            return None

        if isinstance(source, str):
            source = {"url": source, "title": "", "search_query": "", "research_iteration": 1, "source_score": 0.5}

        url = source.get("url", "").strip()
        title = source.get("title", "")
        query = source.get("search_query", "")
        iteration = source.get("research_iteration", 1)
        score = source.get("source_score", 0.5)

        browser = None
        context = None
        page = None

        try:
            if progress_callback:
                progress_callback("PLAYWRIGHT_INIT", 0.33, f"Opening interactive browser for: {url[:50]}...")

            browser = self._ensure_browser()
            context = browser.new_context(
                user_agent=RESEARCH_USER_AGENT,
                viewport={"width": 1280, "height": 800},
                java_script_enabled=True,
                ignore_https_errors=True,
            )
            page = context.new_page()
            page.set_default_timeout(self.timeout_ms)

            # Step 1: Navigate to target URL
            page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)

            # Allow brief network stabilization if active
            try:
                page.wait_for_load_state("networkidle", timeout=3000)
            except Exception:
                pass

            # Step 2: Check for safety and access barriers
            page_raw_content = page.content()
            if self._check_blocked_page(page_raw_content):
                logger.warning(f"Playwright encountered blocked/paywalled page: {url}")
                return None

            page_title = page.title() or title or url

            # Step 3: Handle interactive expansion
            if progress_callback:
                progress_callback("PLAYWRIGHT_EXPAND", 0.34, "Inspecting interactive sections & tables...")
            self._expand_interactive_sections(page)

            # Step 4: Perform bounded scrolling for dynamic views
            self._perform_bounded_scroll(page)

            # Step 5: Extract structured tables
            table_md, table_records = self._extract_tables_from_page(page)

            # Step 6: Extract main page text
            # Prefer article / main content containers first
            extracted_text = ""
            for content_sel in ["article", "main", "[role='main']", "#content", ".content"]:
                try:
                    locator = page.locator(content_sel)
                    if locator.count() > 0 and locator.first.is_visible():
                        extracted_text = locator.first.inner_text()
                        if len(extracted_text) > 300:
                            break
                except Exception:
                    continue

            if len(extracted_text) < 250:
                try:
                    extracted_text = page.locator("body").inner_text()
                except Exception:
                    extracted_text = ""

            accumulated_pages = [clean_text(extracted_text)]

            # Step 7: Bounded Pagination (if available and beneficial)
            page_idx = 1
            while page_idx < self.max_pages:
                next_found = False
                for p_sel in PAGINATION_SELECTORS:
                    try:
                        next_btn = page.locator(p_sel).first
                        if next_btn.is_visible():
                            if progress_callback:
                                progress_callback("PLAYWRIGHT_PAGE", 0.345, f"Following pagination to page {page_idx + 1}...")
                            next_btn.click(timeout=2000)
                            page.wait_for_load_state("domcontentloaded", timeout=4000)
                            page.wait_for_timeout(800)
                            next_text = clean_text(page.locator("body").inner_text())
                            if len(next_text) > 200 and next_text not in accumulated_pages:
                                accumulated_pages.append(next_text)
                                page_idx += 1
                                next_found = True
                                break
                    except Exception:
                        continue
                if not next_found:
                    break

            full_extracted_content = "\n\n".join(p for p in accumulated_pages if p)

            # Append structured tables if present
            if table_md:
                full_extracted_content = f"{full_extracted_content}\n\n### Extracted Data Tables:\n{table_md}"

            sanitized_content = clean_text(full_extracted_content)

            if len(sanitized_content) < 200:
                logger.info(f"Playwright acquisition yielded insufficient text ({len(sanitized_content)} chars) for {url}")
                return None

            truncated = sanitized_content[:max_chars]

            if progress_callback:
                progress_callback("PLAYWRIGHT_SUCCESS", 0.35, f"Acquired {len(truncated)} chars via browser agent.")

            return EvidenceDocument(
                url=url,
                title=page_title,
                content=truncated,
                search_query=query,
                research_iteration=iteration,
                source_score=score,
                char_count=len(truncated),
                acquisition_method="playwright",
                tables=table_records,
                metadata={
                    **source,
                    "pages_visited": len(accumulated_pages),
                    "tables_found": len(table_records),
                    "timestamp": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            logger.warning(f"Playwright acquisition encountered error for {url}: {e}")
            return None

        finally:
            if page:
                try:
                    page.close()
                except Exception:
                    pass
            if context:
                try:
                    context.close()
                except Exception:
                    pass
