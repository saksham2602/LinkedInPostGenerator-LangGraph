import feedparser
from urllib.parse import quote_plus


def fetch_reddit_ai(query=None):
    if query:
        feed_url = f"https://www.reddit.com/search.rss?q={quote_plus(query)}"
    else:
        feed_url = "https://www.reddit.com/r/artificial/.rss"

    feed = feedparser.parse(
        feed_url
    )

    results = []

    for entry in feed.entries[:5]:

        results.append({
            "source": "reddit",
            "title": entry.title,
            "summary": entry.summary,
            "url": entry.link
        })

    return results
