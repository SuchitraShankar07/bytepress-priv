# src/core/run_scraper.py

from src.scraper.fetcher import fetch_articles
from src.mailer.formatter import format_digest
from src.mailer.sender import send_email
from src.utils.logger import logger  # ✅ Logging system

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
    logger.info(f"Starting digest generation for topics: {topics}")
    all_articles = {}

    for topic in topics:
        try:
            logger.info(f"Fetching articles for topic: {topic}")
            articles = fetch_articles(
                topic, max_results=max_articles, semantic_rerank=semantic_rerank
            )
            logger.info(f"✅ Fetched {len(articles)} articles for '{topic}'")
            all_articles[topic] = articles
        except Exception as e:
            logger.error(f"❌ Error fetching articles for '{topic}': {e}")

    return all_articles


if __name__ == "__main__":
    topics_list = ["gut health", "football", "AI"]

    try:
        logger.info("🧠 Digest job started.")

        # --- Fetch and organize articles ---
        all_results = run_scraper(topics_list, max_articles=5, semantic_rerank=True)
        logger.info("✅ Articles fetched successfully for all topics.")

        # --- Format Digest ---
        logger.info("🧩 Formatting digest for email...")
        digest_html = format_digest(all_results)
        logger.info("✅ Digest formatted successfully.")

        # --- Send Email ---
        logger.info("📧 Sending email...")
        recipient = "recipient@example.com"  # Placeholder (will later come from DB)
        subject = "🗞️ Your Daily BytePress Digest"

        send_email(recipient, subject, digest_html)
        logger.info(f"✅ Email sent successfully to {recipient}")

        logger.info("🎉 Digest job completed successfully.")
        print("\n✅ Digest email sent successfully!")

    except Exception as e:
        logger.exception(f"❌ Digest job failed: {e}")
        print("\n❌ Digest job failed. Check logs for details.")

