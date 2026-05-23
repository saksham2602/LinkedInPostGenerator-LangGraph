import os
import requests
from dotenv import load_dotenv

load_dotenv()

CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY")


def fetch_currents_news(query=None):
    if not CURRENTS_API_KEY:
        raise ValueError("CURRENTS_API_KEY not found in .env")

    url = "https://api.currentsapi.services/v1/search"

    params = {
        "apiKey": CURRENTS_API_KEY,
        "keywords": query or "artificial intelligence",
        "language": "en",
        "page_size": 10,
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    

    articles = data.get("news", [])
    print(f"Currents fetched: {len(articles)} articles")

    results = []

    for article in articles:
        results.append({
            "source": article.get("author") or "Currents",
            "source_type": "currents",
            "title": article.get("title", ""),
            "summary": article.get("description", "") or "",
            "url": article.get("url", ""),
            "published_at": article.get("published"),
        })

    return results[:5]
