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
        return {
            "source": item.get("source", "unknown"),
            "title": str(item.get("title", "")).strip(),
            "summary": str(item.get("summary", "")).strip(),
            "url": item.get("url", "")
        }

    if isinstance(item, str):
        return {
            "source": "unknown",
            "title": item.strip(),
            "summary": "",
            "url": ""
        }

    return None
def is_tech_relevant(item):

    text = (
        item.get("title", "")
        + " "
        + item.get("summary", "")
    ).lower()

    matches = sum(
        keyword in text
        for keyword in TECH_KEYWORDS
    )

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
