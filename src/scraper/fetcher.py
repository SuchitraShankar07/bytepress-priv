"""
fetcher.py — Fetch recent (daily) articles per topic using NewsAPI + RSS fallback
"""

import requests
import feedparser
from datetime import datetime, timedelta, timezone
from src.utils import config

def fetch_articles(topic: str, max_results: int = 5, semantic_rerank=False):
    """
    Fetch recent English articles for a topic (daily digest).
    Uses NewsAPI by default, with fallback RSS feeds if needed.
    """
    api_key = getattr(config, "NEWS_API_KEY", None)
    if not api_key:
        raise ValueError("NEWS_API_KEY not found in utils/config.py")

    # 📅 Date range: last 24 hours
    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(days=1)

    url = (
        "https://newsapi.org/v2/everything?"
        f"q={topic}&from={from_date.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        f"&to={to_date.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        "&language=en"
        f"&sortBy=popularity&pageSize={max_results}&apiKey={api_key}"
    )

    print(
        f"[fetcher] Fetching top {max_results} '{topic}' articles "
        f"from {from_date.strftime('%Y-%m-%d %H:%M')} → {to_date.strftime('%Y-%m-%d %H:%M')}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        if articles:
            return [
                {
                    "title": art.get("title"),
                    "url": art.get("url"),
                    "source": art.get("source", {}).get("name"),
                    "publishedAt": art.get("publishedAt"),
                    "description": art.get("description"),
                }
                for art in articles
            ]

    except Exception as e:
        print(f"[fetcher] NewsAPI failed for '{topic}': {e}")

    # 📰 Fallback to RSS (if NewsAPI fails)
    print(f"[fetcher] Falling back to RSS for topic '{topic}'")
    feeds = [
        f"https://news.google.com/rss/search?q={topic}+when:1d&hl=en-US&gl=US&ceid=US:en",
        f"https://www.bing.com/news/search?q={topic}&format=RSS",
    ]

    all_items = []
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:max_results]:
                all_items.append(
                    {
                        "title": entry.get("title"),
                        "url": entry.get("link"),
                        "source": entry.get("source", {}).get("title") or "RSS",
                        "publishedAt": entry.get("published") or entry.get("updated"),
                        "description": entry.get("summary", ""),
                    }
                )
        except Exception as e:
            print(f"[fetcher] RSS fetch error for '{topic}': {e}")

    return all_items[:max_results]

