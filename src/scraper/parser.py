"""
parser.py
Fetches an article page and extracts metadata like title, publication date, etc.
"""

import requests
from bs4 import BeautifulSoup

def parse_article(url: str):
    """
    Fetches a single article URL and extracts its metadata.
    Returns a dict with extracted fields or None if failed.
    """
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        title = soup.find("title").get_text().strip() if soup.find("title") else None
        date_meta = soup.find("meta", {"property": "article:published_time"})
        published = date_meta["content"] if date_meta and "content" in date_meta.attrs else None

        return {"url": url, "title": title, "published": published}

    except Exception as e:
        print(f"[parser] Failed to parse {url}: {e}")
        return None

