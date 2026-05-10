import requests
from bs4 import BeautifulSoup


def fetch_github_trending():

    url = "https://github.com/trending"

    response = requests.get(url)

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    repos = []

    articles = soup.find_all("article")[:5]

    for article in articles:

        title = article.h2.text.strip()

        repos.append({
            "source": "github",
            "title": title,
            "summary": "Trending GitHub repository",
            "url": url
        })

    return repos