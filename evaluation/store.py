import json
import os

from psycopg.types.json import Jsonb

from evaluation.metrics import evaluate_post, summarize_evaluations
from storage.db import database_enabled, ensure_schema, get_connection


EVALUATION_FILE = "data/evaluations.json"


def load_evaluations():
    if database_enabled():
        ensure_schema()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT record
                    FROM evaluations
                    ORDER BY created_at ASC, id ASC
                    """
                )

                return [row[0] for row in cur.fetchall()]

    if not os.path.exists(EVALUATION_FILE):
        return []

    with open(EVALUATION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_evaluation(state):
    topic = state.get("topic", {})
    post = state.get("final_post", "")
    metrics = evaluate_post(post, topic)

    record = {
        **metrics,
        "title": topic.get("title", "") if isinstance(topic, dict) else str(topic),
        "source": topic.get("source", "") if isinstance(topic, dict) else "",
        "content_type": state.get("content_type", ""),
        "quality_score": state.get("score", 0),
        "retry_count": state.get("retry_count", 0),
        "needs_image": state.get("needs_image", False),
    }

    if database_enabled():
        ensure_schema()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO evaluations (record) VALUES (%s)",
                    (Jsonb(record),)
                )

        return {
            "evaluation": record
        }

    os.makedirs("data", exist_ok=True)

    evaluations = load_evaluations()
    evaluations.append(record)

    with open(EVALUATION_FILE, "w", encoding="utf-8") as f:
        json.dump(evaluations, f, indent=2, ensure_ascii=False)

    return {
        "evaluation": record
    }


def get_evaluation_summary():
    return summarize_evaluations(load_evaluations())
