from sources.adapters.arxiv_tool import fetch_arxiv_ai
from sources.adapters.currents_news import fetch_currents_news
from sources.adapters.github_trending_tool import fetch_github_trending
from sources.adapters.google_news_tool import fetch_google_news
from sources.adapters.hackernews_tool import fetch_hn_ai
from sources.adapters.reddit_tool import fetch_reddit_ai
from sources.adapters.tavily_search import fetch_tavily_search


def aggregate_content(query=None):
    data = []

    for fetcher in [
        fetch_tavily_search,
        fetch_google_news,
        fetch_currents_news,
        fetch_reddit_ai,
        fetch_github_trending,
        fetch_arxiv_ai,
        fetch_hn_ai,
    ]:
        try:
            items = fetcher(query)
            print(f"{fetcher.__name__}: {len(items)} items")
            data.extend(items)
        except Exception as e:
            print(f"Fetcher failed: {fetcher.__name__} -> {e}")

    print(f"Total aggregated items: {len(data)}")
    return data
