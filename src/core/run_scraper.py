from src.scraper.fetcher import fetch_articles
from src.mailer.formatter import format_digest
from src.mailer.sender import send_email


def run_scraper(topics, max_articles=5, semantic_rerank=False):
    """
    Fetch top articles for a list of topics, segregated by topic.

    Args:
        topics (list[str]): List of topic strings
        max_articles (int): Number of articles per topic
        semantic_rerank (bool): Whether to apply semantic re-ranking

    Returns:
        dict: { topic1: [articles], topic2: [articles], ... }
    """
    all_articles = {}

    for topic in topics:
        print(f"[1] Fetching articles for topic: {topic}")
        articles = fetch_articles(
            topic, max_results=max_articles, semantic_rerank=semantic_rerank
        )
        print(f"✅ Fetched {len(articles)} articles for '{topic}'\n")
        all_articles[topic] = articles

    return all_articles


if __name__ == "__main__":
    # Example topic list
    topics_list = ["gut health", "football", "AI"]

    # Run scraper
    all_results = run_scraper(topics_list, max_articles=5, semantic_rerank=True)

    # --- Format Digest ---
    print("[2] Formatting digest for email...\n")
    digest_html = format_digest(all_results)

    # --- Send Email ---
    print("[3] Sending email...\n")
    recipient = "recipient@example.com"  # will later come from DB
    subject = "🗞️ Your Daily BytePress Digest"
    send_email(recipient, subject, digest_html)

    print("\n✅ Digest email sent successfully!")

