from typing import TypedDict, List, Dict, Any, Optional

from dotenv import load_dotenv
from evaluation.store import save_evaluation
from langgraph.graph import StateGraph, END
from content.content_type_selector import select_content_type
from content.topic_selector import select_topic
from content.trend_ranker import rank_trends
from media.image_generator import generate_image
from media.image_prompt import generate_image_prompt
from media.visual_decider import decide_visual
from sources.trend_fetcher import get_trends
from storage.memory_store import save_to_memory
from storage.trend_cache import load_ranked_trend_cache, save_ranked_trend_cache
from writing.contrarian_insight import generate_contrarian_insight
from writing.insight_compressor import compress_insight
from writing.post_cleaner import clean_post
from writing.post_writer import generate_post
from writing.reviewer import review_post
from writing.scorer import score_post
load_dotenv()


class AgentState(TypedDict, total=False):
    trends: List[Dict[str, Any]]
    topic: str
    content_type: str
    contrarian_insight: str
    compressed_insight: str
    draft_post: str
    final_post: str
    score: int
    needs_image: bool
    visual_type: str
    image_prompt: str
    image_bytes: Any
    retry_count: int
    memory_saved: bool
    ranked_trends: list
    image_error: str
    evaluation: Dict[str, Any]
    trend_cache_hit: bool
    trend_cache_cached_at: str
    enable_image: bool


def fetch_trends_node(state):
    print("\n[Node] Fetching trends...")

    cached = load_ranked_trend_cache()

    if cached:
        print(
            f"Using cached ranked trends from {cached['cached_at']}"
        )

        return {
            "trends": cached["trends"],
            "ranked_trends": cached["ranked_trends"],
            "trend_cache_hit": True,
            "trend_cache_cached_at": cached["cached_at"],
        }

    trends = get_trends()

    print(f"Fetched {len(trends)} trends")

    return {
        "trends": trends,
        "trend_cache_hit": False
    }


def rank_trends_node(state):
    if state.get("trend_cache_hit") and state.get("ranked_trends"):
        print("\n[Node] Ranking trends...")
        print("Using cached ranking")

        return {
            "ranked_trends": state["ranked_trends"]
        }

    result = rank_trends(state)

    save_ranked_trend_cache(
        state.get("trends", []),
        result.get("ranked_trends", [])
    )

    return result


def select_topic_node(state):
    print("\n[Node] Selecting topic...")

    topic = select_topic(
        state["ranked_trends"]
    )

    print("\nSelected topic:")
    print(topic)

    return {
        "topic": topic
    }


def content_type_node(state):
    return select_content_type(state)


def contrarian_node(state):
    return generate_contrarian_insight(state)


def write_post_node(state):
    print("\n[Node] Writing draft...")

    retry_count = state.get("retry_count", 0)

    return {
        "draft_post": generate_post(state),
        "retry_count": retry_count + 1
    }

def review_post_node(state):
    print("\n[Node] Reviewing draft...")

    reviewed = review_post(
        state["draft_post"],
        state.get("topic", {})
    )

    cleaned = clean_post(
        reviewed,
        state.get("topic", {})
    )

    post_body = cleaned.split("Source:", 1)[0].strip()

    if len(post_body.split()) < 60:
        cleaned = build_fallback_post(state)

    return {
        "final_post": cleaned
    }


def build_fallback_post(state):
    topic = state.get("topic", {})

    if not isinstance(topic, dict):
        topic = {}

    title = topic.get("title", "This AI project")
    summary = topic.get("summary", "")
    source = topic.get("source", "Source")
    url = topic.get("url", "")
    content_type = state.get("content_type", "TECH_BREAKDOWN")
    insight = state.get("compressed_insight") or state.get("contrarian_insight") or ""

    source_line = (
        f"Source: [{source}]({url})"
        if url
        else f"Source: {source}"
    )

    summary_sentences = split_sentences(summary)
    concrete_detail = pick_grounded_detail(
        summary_sentences
    )
    second_detail = pick_grounded_detail(
        summary_sentences,
        skip=concrete_detail
    )

    opening = f"{title} points to a practical engineering tradeoff."
    details = concrete_detail or summary or "The source describes a technical system with a design choice that needs validation."
    takeaway = insight or second_detail or "The safer takeaway is to validate the system against future cases, not only the examples used while designing it."

    return "\n\n".join([
        opening,
        details,
        "The failure mode is trusting a result because it looks strong on the training examples, while missing how the same choice behaves on new inputs.",
        takeaway,
        "For builders, the useful question is not only whether the method works once, but how much evidence is enough before using it as a selection rule.",
        source_line,
    ])


def split_sentences(text):
    if not text:
        return []

    parts = [
        part.strip()
        for part in text.replace("\n", " ").split(".")
        if part.strip()
    ]

    return [
        part + "."
        for part in parts
    ]


def pick_grounded_detail(sentences, skip=""):
    useful_terms = [
        "overfitting",
        "training",
        "performance",
        "portfolio",
        "selector",
        "guarantee",
        "tradeoff",
        "parameter",
        "validation",
        "future",
    ]

    for sentence in sentences:
        if sentence == skip:
            continue

        lower = sentence.lower()

        if any(term in lower for term in useful_terms):
            return shorten_text(sentence, 260)

    for sentence in sentences:
        if sentence != skip:
            return shorten_text(sentence, 260)

    return ""


def shorten_text(text, limit):
    text = " ".join(str(text or "").split())

    if len(text) <= limit:
        return text

    return text[:limit].rsplit(" ", 1)[0] + "."


def score_node(state):
    print("\n[Node] Scoring post...")

    return {
        "score": score_post(
            state["final_post"]
        )
    }


def should_retry(state):
    print(f"\nQuality score: {state['score']}")

    if state["score"] < 7 and state.get("retry_count", 0) < 3:
        return "write"

    return "visual_decision"


def evaluate_node(state):
    print("\n[Node] Evaluating post...")

    return save_evaluation(state)


def image_prompt_node(state):
    print("\n[Node] Generating image prompt...")

    return {
        "image_prompt": generate_image_prompt(
            state["final_post"]
        )
    }


def image_node(state):

    print("\n[Node] Generating image...")

    try:

        image = generate_image(
            state["image_prompt"]
        )

        return {
            "image_bytes": image,
            "image_error": None
        }

    except Exception as e:

        print(
            "\n[Image Generation Failed]"
        )

        print(str(e))

        return {
            "image_bytes": None,
            "image_error": str(e)
        }


def route_visual(state):
    if state.get("enable_image") and state.get("needs_image"):
        return "image_prompt"

    return "evaluate"


builder = StateGraph(AgentState)

builder.add_node("fetch", fetch_trends_node)
builder.add_node("topic", select_topic_node)
builder.add_node("content_type", content_type_node)
builder.add_node("contrarian", contrarian_node)
builder.add_node("write", write_post_node)
builder.add_node("review", review_post_node)
builder.add_node("score", score_node)
builder.add_node("evaluate", evaluate_node)
builder.add_node("visual_decision", decide_visual)
builder.add_node("image_prompt", image_prompt_node)
builder.add_node("image", image_node)
builder.add_node("compress_insight", compress_insight)
builder.add_node("memory", save_to_memory)
builder.add_node("rank" , rank_trends_node)

builder.set_entry_point("fetch")

builder.add_edge("fetch", "rank")
builder.add_edge("rank", "topic")
builder.add_edge("topic", "content_type")
builder.add_edge("content_type", "contrarian")
builder.add_edge("contrarian", "compress_insight")
builder.add_edge("compress_insight", "write")
builder.add_edge("write", "review")
builder.add_edge("review", "score")

builder.add_conditional_edges(
    "score",
    should_retry
)

builder.add_conditional_edges(
    "visual_decision",
    route_visual
)

builder.add_edge("image_prompt", "image")
builder.add_edge("image", "evaluate")
builder.add_edge("evaluate", "memory")
builder.add_edge("memory", END)

graph = builder.compile()
