import os

import requests
from dotenv import load_dotenv


load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def fetch_tavily_search(query=None):
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY not found in .env")

    search_query = query or "latest AI engineering news open source LLM agents"

    response = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": TAVILY_API_KEY,
            "query": search_query,
            "search_depth": "advanced",
            "topic": "news",
            "max_results": 8,
            "include_answer": False,
            "include_raw_content": False,
        },
        timeout=15,
    )
    response.raise_for_status()

    data = response.json()
    results = []

    for item in data.get("results", []):
        title = item.get("title", "")
        url = item.get("url", "")

        if not title or not url:
            continue

        results.append({
            "source": "Tavily",
            "source_type": "web_search",
            "title": title,
            "summary": item.get("content", "") or "",
            "url": url,
            "published_at": item.get("published_date", ""),
        })

    return results
