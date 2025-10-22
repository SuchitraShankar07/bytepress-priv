"""
aggregator.py
Cleans, filters, deduplicates, and ranks fetched articles.
"""

from datetime import datetime

def clean_and_rank(articles: list):
    """
    Takes a list of articles (dicts) and:
    - Removes duplicates
    - Filters out missing titles or URLs
    - Sorts by publication date (newest first)
    """
    seen = set()
    cleaned = []

    for art in articles:
        if not art or not art.get("url") or art["url"] in seen:
            continue
        seen.add(art["url"])
        cleaned.append(art)

    def parse_date(date_str):
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return datetime.min

    cleaned.sort(key=lambda a: parse_date(a.get("publishedAt") or a.get("published")), reverse=True)
    return cleaned

