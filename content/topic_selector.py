from langchain_ollama import ChatOllama
import json
import re
from storage.memory_store import get_recent_memory

llm = ChatOllama(model="mistral", temperature=0)


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


def select_topic(trends):
    recent_memory = get_recent_memory()
    filtered_trends = filter_repeated_topics(
    trends,
    recent_memory
)
    trends_text = json.dumps(
    filtered_trends,
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
- Prefer fresh engineering insights
- Prefer AI agents, edge AI, robotics, RAG, evaluation, inference, infrastructure
- Pick ONE item only
- Use exact URL from the item
- Do not invent links

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
        return parsed

    # fallback: first usable item
    for item in filtered_trends:
        if item.get("url"):
            return item

    return filtered_trends[0]
