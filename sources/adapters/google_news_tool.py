import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def fetch_google_news():
    if not NEWS_API_KEY:
        raise ValueError("NEWS_API_KEY not found in .env")

    url = "https://newsdata.io/api/1/latest"

    params = {
        "apikey": NEWS_API_KEY,
        "q": "AI OR artificial intelligence OR LLM OR machine learning",
        "language": "en",
        "category": "technology",
        "size": 10,   # important
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    

    articles = data.get("results", [])
    print(f"NewsData fetched: {len(articles)} articles")

    results = []

    for article in articles:
        results.append({
            "source": article.get("source_name", "Unknown"),
            "source_type": "newsdata",
            "title": article.get("title", ""),
            "summary": article.get("description", "") or "",
            "url": article.get("link", ""),
        })

    return results[:5]