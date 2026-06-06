"""Strip HTML tags and optimize text for storage/labeling.

Uses BeautifulSoup when available, otherwise falls back to a regex tag-stripper
so the tool has no hard dependency on beautifulsoup4.
"""
import re

try:
    from bs4 import BeautifulSoup
    _HAS_BS4 = True
except ImportError:
    BeautifulSoup = None
    _HAS_BS4 = False


def clean_html(raw: str, max_chars: int = 280) -> str:
    """
    Strip HTML tags, collapse whitespace, truncate to max_chars.
    Returns clean plain text suitable for spam labeling.
    """
    if not raw:
        return ""
    if _HAS_BS4:
        text = BeautifulSoup(raw, "html.parser").get_text(separator=" ")
    else:
        text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]
