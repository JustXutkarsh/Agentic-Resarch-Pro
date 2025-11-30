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

def clean_text(raw: str) -> str:
    if not raw:
        return ""

    text = html.unescape(raw)
    text = re.sub(r"<script.*?>.*?</script>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<style.*?>.*?</style>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = normalize_unicode(text)
    text = remove_all_control_chars(text)
    text = text.replace("\u2028", " ").replace("\u2029", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()
