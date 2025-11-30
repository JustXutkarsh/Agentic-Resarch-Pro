# src/scraper.py
import requests
from bs4 import BeautifulSoup
import re

def clean_text(t):
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def scrape_pdf(url):
    try:
        import fitz  # PyMuPDF
        r = requests.get(url, timeout=12)
        if r.status_code != 200:
            return None
        
        doc = fitz.open(stream=r.content, filetype="pdf")
        out = ""
        for page in doc:
            out += page.get_text()
        return clean_text(out)
    except:
        return None


def scrape_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # Extract paragraphs
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = " ".join(paragraphs)

    if len(text) > 300:
        return clean_text(text)

    # fallback: extract all visible text
    raw = soup.get_text(" ", strip=True)
    if len(raw) > 300:
        return clean_text(raw)

    return None


def scrape_urls(urls):
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (ResearchAgentBot)"
    }

    for url in urls:
        try:
            lower = url.lower()

            # Skip YouTube and X
            if "youtube.com/watch" in lower or "youtu.be/" in lower or "x.com/" in lower:
                continue

            # PDF links
            if lower.endswith(".pdf"):
                text = scrape_pdf(url)
                if text and len(text) > 300:
                    results.append(text[:8000])
                continue

            # normal page
            r = requests.get(url, timeout=12, headers=headers)
            if r.status_code != 200:
                continue

            extracted = scrape_html(r.text)
            if extracted and len(extracted) > 300:
                results.append(extracted[:8000])

        except Exception:
            continue

    return results
