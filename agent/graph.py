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

    return {
        "final_post": cleaned
    }


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
    if state.get("needs_image"):
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
