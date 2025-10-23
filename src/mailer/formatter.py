# src/mailer/formatter.py

from datetime import datetime

def format_digest(articles_by_topic: dict) -> str:
    """
    Formats the scraped articles into an HTML digest.
    """
    today = datetime.now().strftime("%B %d, %Y")
    html = [f"<h2>📰 Daily Digest - {today}</h2>"]

    for topic, articles in articles_by_topic.items():
        html.append(f"<h3>{topic}</h3>")
        if not articles:
            html.append("<p>No articles found today.</p>")
            continue

        for art in articles:
            html.append(f"""
                <p>
                    <strong>{art['title']}</strong><br>
                    {art['description'] or ''}<br>
                    <a href="{art['url']}">Read more</a>
                </p>
                <hr>
            """)

    return "\n".join(html)

