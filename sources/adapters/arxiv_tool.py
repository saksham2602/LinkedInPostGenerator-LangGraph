import feedparser


def fetch_arxiv_ai():

    url = (
        "http://export.arxiv.org/api/query?"
        "search_query=cat:cs.AI"
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