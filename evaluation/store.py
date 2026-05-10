import json
import os

from evaluation.metrics import evaluate_post, summarize_evaluations


EVALUATION_FILE = "data/evaluations.json"


def load_evaluations():
    if not os.path.exists(EVALUATION_FILE):
        return []

    with open(EVALUATION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_evaluation(state):
    os.makedirs("data", exist_ok=True)

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

    evaluations = load_evaluations()
    evaluations.append(record)

    with open(EVALUATION_FILE, "w", encoding="utf-8") as f:
        json.dump(evaluations, f, indent=2, ensure_ascii=False)

    return {
        "evaluation": record
    }


def get_evaluation_summary():
    return summarize_evaluations(load_evaluations())
