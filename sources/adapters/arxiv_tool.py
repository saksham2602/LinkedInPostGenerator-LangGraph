import feedparser
from urllib.parse import quote


def fetch_arxiv_ai(query=None):
    search_query = (
        f'all:"{query}"'
        if query
        else "cat:cs.AI"
    )

    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query={quote(search_query)}"
        "&start=0&max_results=5"
    )

    feed = feedparser.parse(url)

    papers = []

    for entry in feed.entries:

        papers.append({
            "source": "arxiv",
            "title": entry.title,
            "summary": entry.summary,
            "url": entry.link
        })

    return papers
