import json
import os
import re

from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_ollama import ChatOllama

from storage.memory_store import get_recent_memory
from writing.llm_utils import invoke_with_retries

load_dotenv()

llm = ChatNVIDIA(
  model="upstage/solar-10.7b-instruct",
  api_key=os.getenv("NVIDIA_API_KEY"),
  max_tokens=300,
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


def _short_text(value, limit=280):
    text = str(value or "").strip()

    if len(text) <= limit:
        return text

    return text[:limit].rsplit(" ", 1)[0] + "..."


def _compact_trend(item):
    return {
        "title": _short_text(item.get("title"), 160),
        "source": item.get("source", ""),
        "source_type": item.get("source_type", ""),
        "url": item.get("url", ""),
        "summary": _short_text(item.get("summary"), 320),
        "ranking_score": item.get("ranking_score", 0),
    }


def _compact_memory_item(item):
    return {
        "title": _short_text(item.get("title"), 160),
        "source": item.get("source", ""),
    }


def _find_exact_item(parsed, trends):
    parsed_url, parsed_title = _topic_key(parsed)

    for item in trends:
        item_url, item_title = _topic_key(item)

        if parsed_url and parsed_url == item_url:
            return item

        if parsed_title and parsed_title == item_title:
            return item

    return None


def select_topic(trends, user_topic=""):
    if not trends:
        return {
            "title": user_topic or "AI engineering update",
            "source": "No source",
            "url": "",
            "summary": "No matching source items were found during this run.",
            "reason": "Fallback topic because source fetching returned no usable items.",
        }

    recent_memory = get_recent_memory()
    filtered_trends = filter_repeated_topics(
    trends,
    recent_memory
)
    if not filtered_trends:
        filtered_trends = trends

    candidates = filtered_trends[:6]

    trends_text = json.dumps(
        [_compact_trend(item) for item in candidates],
        separators=(",", ":")
    )
    memory_text = json.dumps(
        [_compact_memory_item(item) for item in recent_memory[:8]],
        separators=(",", ":")
    )

    topic_instruction = ""
    if user_topic:
        topic_instruction = f"""
User requested topic:
{user_topic}

Extra rules:
- Select an item that is clearly related to the requested topic
- Prefer the freshest concrete news, repository, paper, or discussion about that topic
- Use the requested topic as direction, but ground the post in one available item
"""

    prompt = f"""
You are selecting EXACTLY ONE topic for a LinkedIn post.

You must avoid repetitive content.

{topic_instruction}

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
- Copy title, source, url, and summary exactly from the selected available item
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

    raw = invoke_with_retries(llm, prompt)

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
