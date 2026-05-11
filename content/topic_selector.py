from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_ollama import ChatOllama
import json
import re
from storage.memory_store import get_recent_memory

llm = ChatNVIDIA(
  model="upstage/solar-10.7b-instruct",
  api_key="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", 
)


def filter_repeated_topics(
    trends,
    recent_memory
):
    recent_titles = set()

    for item in recent_memory:

        title = (
            item.get("title", "")
            .lower()
            .strip()
        )

        if title:
            recent_titles.add(title)

    filtered = []

    for trend in trends:

        trend_title = (
            trend.get("title", "")
            .lower()
            .strip()
        )

        if trend_title not in recent_titles:
            filtered.append(trend)

    return filtered
def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        return None

    try:
        return json.loads(match.group())
    except:
        return None


def _topic_key(item):
    return (
        str(item.get("url", "")).strip().lower(),
        str(item.get("title", "")).strip().lower(),
    )


def _find_exact_item(parsed, trends):
    parsed_url, parsed_title = _topic_key(parsed)

    for item in trends:
        item_url, item_title = _topic_key(item)

        if parsed_url and parsed_url == item_url:
            return item

        if parsed_title and parsed_title == item_title:
            return item

    return None


def select_topic(trends):
    recent_memory = get_recent_memory()
    filtered_trends = filter_repeated_topics(
    trends,
    recent_memory
)
    if not filtered_trends:
        filtered_trends = trends

    candidates = filtered_trends[:10]

    trends_text = json.dumps(
    candidates,
    indent=2
)
    memory_text = json.dumps(
    recent_memory,
    indent=2
)

    prompt = f"""
You are selecting EXACTLY ONE topic for a LinkedIn post.

You must avoid repetitive content.

Recently covered topics:
{memory_text}

Rules:
- Avoid repeating the same topic
- Avoid repeatedly selecting the same source
- Avoid too many AI ethics posts
- Prefer the highest ranking_score unless a lower item is clearly more concrete
- Prefer fresh engineering insights over broad industry news
- Prefer AI agents, edge AI, robotics, RAG, evaluation, inference, infrastructure
- Prefer GitHub repositories only when the repo description is clearly technical or AI-adjacent
- Pick ONE item only
- Select only from Available items
- Copy title, source, url, and summary exactly from the selected item
- Use the exact URL from the item
- Do not invent source names or links

Return ONLY valid JSON:

{{
  "title": "...",
  "source": "...",
  "url": "...",
  "summary": "...",
  "reason": "..."
}}

Available items:
{trends_text}
"""

    raw = llm.invoke(prompt).content.strip()

    parsed = extract_json(raw)

    if parsed:
        exact_item = _find_exact_item(
            parsed,
            candidates
        )

        if exact_item:
            selected = dict(exact_item)
            selected["reason"] = parsed.get("reason", "")
            return selected

    # fallback: best ranked usable item
    for item in candidates:
        if item.get("url"):
            return item

    return candidates[0]
