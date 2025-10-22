"""
digest.py
Main orchestrator — calls fetcher, parser, aggregator to build a clean digest.
"""

from scraper.fetcher import fetch_articles
from scraper.parser import parse_article
from scraper.aggregator import clean_and_rank

def generate_digest(topic: str, max_results: int = 10):
    """
    Generates a digest of recent articles for the given topic.
    Returns a cleaned list of article dicts with titles and URLs.
    """
    print(f"[digest] Generating digest for topic: {topic}")
    raw_articles = fetch_articles(topic, max_results=max_results)
    print(f"[digest] Fetched {len(raw_articles)} articles.")

    # Optionally enrich metadata by parsing each link
    parsed_articles = []
    for art in raw_articles:
        parsed = parse_article(art["url"])
        if parsed:
            art.update(parsed)
        parsed_articles.append(art)

    digest = clean_and_rank(parsed_articles)
    print(f"[digest] Final digest contains {len(digest)} articles.")
    return digest

