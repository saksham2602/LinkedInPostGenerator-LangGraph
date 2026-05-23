from sources.aggregator import aggregate_content

TECH_KEYWORDS = [
    "ai",
    "llm",
    "agent",
    "rag",
    "robotics",
    "inference",
    "gpu",
    "transformer",
    "open source",
    "developer",
    "coding",
    "software engineering",
    "machine learning",
    "deep learning",
    "model",
    "benchmark",
    "deployment",
    "infrastructure",
    "automation",
]
def normalize_item(item):
    if isinstance(item, dict):
        normalized = {
            "source": item.get("source", "unknown"),
            "title": str(item.get("title", "")).strip(),
            "summary": str(item.get("summary", "")).strip(),
            "url": item.get("url", "")
        }

        for key in [
            "source_type",
            "published_at",
            "language",
            "stars",
            "ranking_score",
        ]:
            if key in item:
                normalized[key] = item.get(key)

        return normalized

    if isinstance(item, str):
        return {
            "source": "unknown",
            "title": item.strip(),
            "summary": "",
            "url": ""
        }

    return None
def is_tech_relevant(item):
    source_type = item.get("source_type", "").lower()
    source = item.get("source", "").lower()

    text = (
        item.get("title", "")
        + " "
        + item.get("summary", "")
    ).lower()

    matches = sum(
        keyword in text
        for keyword in TECH_KEYWORDS
    )

    if source_type == "github" or source == "github":
        return matches >= 1

    return matches >= 2

def _query_terms(query):
    stop_words = {
        "a",
        "an",
        "and",
        "for",
        "in",
        "of",
        "on",
        "or",
        "the",
        "to",
        "with",
    }

    return [
        word.strip().lower()
        for word in str(query or "").replace("-", " ").split()
        if len(word.strip()) > 2 and word.strip().lower() not in stop_words
    ]


def _matches_query(item, query):
    terms = _query_terms(query)

    if not terms:
        return True

    text = (
        item.get("title", "")
        + " "
        + item.get("summary", "")
        + " "
        + item.get("source", "")
    ).lower()

    matches = sum(term in text for term in terms)

    return matches >= 1


def get_trends(query=None):
    raw_items = aggregate_content(query)

    seen = set()
    cleaned = []

    for raw_item in raw_items:
        item = normalize_item(raw_item)

        if not item:
            continue

        title = item["title"]

        if not title:
            continue

        if query and not _matches_query(item, query):
            continue

        if not query and not is_tech_relevant(item):
            continue

        key = title.lower()[:80]

        if key in seen:
            continue

        seen.add(key)
        cleaned.append(item)

    return cleaned[:20]
