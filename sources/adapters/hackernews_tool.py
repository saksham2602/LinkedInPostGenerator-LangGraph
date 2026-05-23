import requests


AI_KEYWORDS = [
    "ai",
    "llm",
    "agent",
    "rag",
    "transformer",
    "inference",
    "openai",
    "anthropic",
    "robotics",
    "deep learning",
    "machine learning",
    "gpu",
    "neural",
]


def fetch_hn_ai(query=None):
    keywords = [
        word.lower()
        for word in str(query or "").split()
        if len(word) > 2
    ] or AI_KEYWORDS

    top = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json"
    ).json()[:20]

    results = []

    for story_id in top:

        item = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        ).json()

        title = item.get("title", "")

        title_lower = title.lower()

        if any(keyword in title_lower for keyword in keywords):

            results.append({
                "source": "hackernews",
                "title": title,
                "summary": "Trending Hacker News AI discussion",
                "url": item.get("url", "")
            })

    return results[:5]
