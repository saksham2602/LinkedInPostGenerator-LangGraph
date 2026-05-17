import json
import os
from datetime import datetime

from psycopg.types.json import Jsonb

from storage.db import database_enabled, ensure_schema, get_connection

MEMORY_FILE = "data/post_memory.json"


def load_memory():
    if database_enabled():
        ensure_schema()

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
