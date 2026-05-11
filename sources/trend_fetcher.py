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

def get_trends():
    raw_items = aggregate_content()

    seen = set()
    cleaned = []

    for raw_item in raw_items:
        item = normalize_item(raw_item)

        if not item:
            continue

        title = item["title"]

        if not title:
            continue

        if not is_tech_relevant(item):
            continue

        key = title.lower()[:80]

        if key in seen:
            continue

        seen.add(key)
        cleaned.append(item)

    return cleaned[:20]
