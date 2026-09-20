# src/cleaner.py
import re
import unicodedata
import html

CONTROL_CHAR_PATTERN = re.compile(
    "[" 
    "\u0000-\u0008"
    "\u000B-\u000C"
    "\u000E-\u001F"
    "\u007F"
    "\u0080-\u009F"
    "]"
)

def remove_all_control_chars(text: str) -> str:
    return CONTROL_CHAR_PATTERN.sub("", text)

def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKD", text)

# Boilerplate and noise patterns
BOILERPLATE_PATTERNS = [
    re.compile(r"(?i)\b(?:accept|manage|reject)\s+(?:all\s+)?cookies\b[^\n]*"),
    re.compile(r"(?i)\bwe\s+use\s+cookies\s+to\s+enhance\b[^\n]*"),
    re.compile(r"(?i)\bsign\s+up\s+for\s+(?:our\s+)?newsletter\b[^\n]*"),
    re.compile(r"(?i)\ball\s+rights\s+reserved\.?\b"),
    re.compile(r"(?i)\bterms\s+of\s+service\s+\|\s+privacy\s+policy\b"),
    re.compile(r"(?i)\benable\s+javascript\s+to\s+run\s+this\s+app\b"),
]


def clean_text(raw: str, preserve_paragraphs: bool = False) -> str:
    """
    Cleans raw text by removing HTML tags, control chars, and normalizing whitespace.
    If preserve_paragraphs=True, maintains double newlines between paragraphs and tables.
    """
    if not raw:
        return ""

    text = html.unescape(raw)
    text = re.sub(r"<script.*?>.*?</script>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<style.*?>.*?</style>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = normalize_unicode(text)
    text = remove_all_control_chars(text)
    text = text.replace("\u2028", " ").replace("\u2029", " ")

    if preserve_paragraphs:
        # Normalize multiple spaces on single lines, but keep line breaks
        lines = [re.sub(r"[^\S\r\n]+", " ", line).strip() for line in text.splitlines()]
        # Remove repeated blank lines
        text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
        return text.strip()
    else:
        text = re.sub(r"\s+", " ", text)
        return text.strip()


def clean_structured_content(raw: str) -> str:
    """
    Cleans extracted article/document content while preserving markdown headings (#, ##),
    markdown tables (| col |), bullet points, and paragraph boundaries.
    Strips cookie notices, subscription banners, and navigational boilerplate.
    """
    if not raw:
        return ""

    text = html.unescape(raw)
    # Remove scripts and styles
    text = re.sub(r"<script.*?>.*?</script>", "\n", text, flags=re.DOTALL)
    text = re.sub(r"<style.*?>.*?</style>", "\n", text, flags=re.DOTALL)

    # Convert common HTML break/paragraph tags to newlines before stripping other tags
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(?:p|div|h[1-6]|tr|li)>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)

    text = normalize_unicode(text)
    text = remove_all_control_chars(text)

    # Strip boilerplate lines
    cleaned_lines = []
    for line in text.splitlines():
        line_str = line.strip()
        if not line_str:
            cleaned_lines.append("")
            continue
        is_boilerplate = any(p.search(line_str) for p in BOILERPLATE_PATTERNS)
        if not is_boilerplate:
            cleaned_lines.append(re.sub(r"[^\S\r\n]+", " ", line_str))

    content = "\n".join(cleaned_lines)
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip()

