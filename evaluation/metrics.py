import re
from datetime import datetime


GENERIC_CTA_PATTERNS = [
    r"what are your thoughts",
    r"let'?s discuss",
    r"curious to know",
    r"how do you manage",
    r"how do you handle",
    r"how do you ensure",
]

BANNED_PHRASES = [
    "in ai development",
    "rapidly evolving",
    "future of ai",
    "game-changing",
    "revolutionary",
    "transformative",
    "cutting-edge",
    "delve",
    "robust systems",
    "unseen scenarios",
    "striking the right balance",
    "promising guarantees",
    "practical implications",
    "my takeaway:",
]

TECH_TERMS = [
    "agent",
    "algorithm",
    "api",
    "benchmark",
    "data",
    "dataset",
    "deployment",
    "evaluation",
    "fallback",
    "inference",
    "latency",
    "model",
    "routing",
    "selector",
    "solver",
    "training",
]


def _count_matches(patterns, text):
    lower_text = text.lower()
    return sum(
        len(re.findall(pattern, lower_text))
        for pattern in patterns
    )


def _score_from_penalties(base, *penalties):
    return max(0, min(10, base - sum(penalties)))


def _word_count(text):
    return len(re.findall(r"\b[\w'-]+\b", text))


def _sentence_count(text):
    sentences = re.findall(r"[^.!?]+[.!?]", text)
    return max(1, len(sentences))


def _source_line(post, expected_source):
    lines = [
        line.strip()
        for line in post.strip().splitlines()
        if line.strip()
    ]

    if not lines:
        return {
            "source_present": False,
            "source_line_valid": False,
        }

    last_line = lines[-1]
    expected = f"Source: {expected_source}".lower()

    return {
        "source_present": last_line.lower().startswith("source:"),
        "source_line_valid": last_line.lower() == expected if expected_source else last_line.lower().startswith("source:"),
    }


def evaluate_post(post, topic=None):
    topic = topic or {}
    expected_source = topic.get("source", "") if isinstance(topic, dict) else ""

    words = _word_count(post)
    sentences = _sentence_count(post)
    avg_sentence_words = round(words / sentences, 2)
    question_count = post.count("?")
    raw_url_count = len(re.findall(r"https?://", post))
    hashtag_count = len(re.findall(r"(^|\s)#\w+", post))
    generic_cta_count = _count_matches(GENERIC_CTA_PATTERNS, post)
    banned_phrase_count = _count_matches(
        [re.escape(phrase) for phrase in BANNED_PHRASES],
        post
    )
    tech_term_count = _count_matches(
        [fr"\b{re.escape(term)}\b" for term in TECH_TERMS],
        post
    )
    source_metrics = _source_line(post, expected_source)

    readability_penalty = 0
    if avg_sentence_words > 28:
        readability_penalty += 2
    if words < 90 or words > 230:
        readability_penalty += 2

    clarity_score = _score_from_penalties(
        10,
        readability_penalty,
        banned_phrase_count,
        raw_url_count,
        hashtag_count,
    )

    human_tone_score = _score_from_penalties(
        10,
        banned_phrase_count * 2,
        generic_cta_count * 3,
        2 if question_count > 1 else 0,
    )

    specificity_score = min(
        10,
        3 + tech_term_count + (2 if re.search(r"\d", post) else 0)
    )

    source_score = 10
    if not source_metrics["source_present"]:
        source_score = 0
    elif not source_metrics["source_line_valid"]:
        source_score = 5

    cta_score = 10 if generic_cta_count == 0 else 3

    evaluation_score = round(
        (
            clarity_score
            + human_tone_score
            + specificity_score
            + source_score
            + cta_score
        ) / 5,
        2
    )

    return {
        "evaluated_at": datetime.now().isoformat(),
        "evaluation_score": evaluation_score,
        "clarity_score": clarity_score,
        "human_tone_score": human_tone_score,
        "specificity_score": specificity_score,
        "source_faithfulness_score": source_score,
        "cta_quality_score": cta_score,
        "word_count": words,
        "sentence_count": sentences,
        "avg_sentence_words": avg_sentence_words,
        "question_count": question_count,
        "generic_cta_count": generic_cta_count,
        "banned_phrase_count": banned_phrase_count,
        "raw_url_count": raw_url_count,
        "hashtag_count": hashtag_count,
        "tech_term_count": tech_term_count,
        **source_metrics,
    }


def summarize_evaluations(records):
    if not records:
        return {}

    count = len(records)

    def avg(key):
        return round(
            sum(item.get(key, 0) for item in records) / count,
            2
        )

    return {
        "total_evaluated": count,
        "avg_evaluation_score": avg("evaluation_score"),
        "avg_clarity_score": avg("clarity_score"),
        "avg_human_tone_score": avg("human_tone_score"),
        "avg_specificity_score": avg("specificity_score"),
        "generic_cta_rate": round(
            sum(1 for item in records if item.get("generic_cta_count", 0) > 0) / count,
            2
        ),
        "source_validity_rate": round(
            sum(1 for item in records if item.get("source_line_valid")) / count,
            2
        ),
        "avg_word_count": avg("word_count"),
    }
