import feedparser


def fetch_reddit_ai():

    feed = feedparser.parse(
        "https://www.reddit.com/r/artificial/.rss"
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