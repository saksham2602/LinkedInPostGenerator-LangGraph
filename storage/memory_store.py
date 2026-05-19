import json
import os
from datetime import datetime, timedelta

from psycopg.types.json import Jsonb

from storage.db import database_enabled, ensure_schema, get_connection

MEMORY_FILE = "data/post_memory.json"
DEFAULT_MEMORY_RETENTION_DAYS = 30


def _memory_retention_days():
    raw_value = os.getenv("MEMORY_RETENTION_DAYS", str(DEFAULT_MEMORY_RETENTION_DAYS))

    try:
        return max(1, int(raw_value))
    except ValueError:
        return DEFAULT_MEMORY_RETENTION_DAYS


def prune_memory():
    retention_days = _memory_retention_days()

    if database_enabled():
        ensure_schema()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM post_memory
                    WHERE created_at < NOW() - (%s * INTERVAL '1 day')
                    """,
                    (retention_days,)
                )

        return

    if not os.path.exists(MEMORY_FILE):
        return

    cutoff = datetime.now() - timedelta(days=retention_days)

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        memory = json.load(f)

    fresh_memory = []
    for item in memory:
        try:
            item_date = datetime.fromisoformat(item.get("date", ""))
        except ValueError:
            fresh_memory.append(item)
            continue

        if item_date >= cutoff:
            fresh_memory.append(item)

    if len(fresh_memory) != len(memory):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(fresh_memory, f, indent=2, ensure_ascii=False)


def load_memory():
    prune_memory()

    if database_enabled():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT record
                    FROM post_memory
                    ORDER BY created_at ASC, id ASC
                    """
                )

                return [row[0] for row in cur.fetchall()]

    if not os.path.exists(MEMORY_FILE):
        return []

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_to_memory(state):
    topic = state.get("topic", {})

    record = {
        "date": datetime.now().isoformat(),
        "title": topic.get("title", "") if isinstance(topic, dict) else str(topic),
        "source": topic.get("source", "") if isinstance(topic, dict) else "",
        "url": topic.get("url", "") if isinstance(topic, dict) else "",
        "content_type": state.get("content_type", ""),
        "final_post": state.get("final_post", ""),
        "needs_image": state.get("needs_image", False),
        "score": state.get("score", 0),
        "evaluation": state.get("evaluation", {})
    }

    if database_enabled():
        ensure_schema()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO post_memory (record) VALUES (%s)",
                    (Jsonb(record),)
                )

        return {
            "memory_saved": True
        }

    os.makedirs("data", exist_ok=True)

    memory = load_memory()
    memory.append(record)

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

    return {
        "memory_saved": True
    }


def get_recent_memory(limit=10):
    memory = load_memory()
    return memory[-limit:]
