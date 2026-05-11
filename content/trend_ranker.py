from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_ollama import ChatOllama

llm = ChatNVIDIA(
  model="mistralai/mistral-large-3-675b-instruct-2512",
  api_key="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", 
)

SOURCE_WEIGHTS = {
    "arxiv": 10,
    "huggingface": 10,
    "github": 9,
    "hackernews": 8,
    "reddit": 7,
    "newsapi": 4,
}


def get_source_weight(item):
    source = item.get("source", "").lower()
    source_type = item.get("source_type", "").lower()

    if source_type in SOURCE_WEIGHTS:
        return SOURCE_WEIGHTS[source_type]

    if source in SOURCE_WEIGHTS:
        return SOURCE_WEIGHTS[source]

    return 3


def score_single_trend(item):

    prompt = f"""
Rate this topic for a technical LinkedIn AI audience.

Prefer:
- AI agents
- RAG
- robotics
- inference
- infrastructure
- open-source AI
- engineering insights
- benchmarks
- evaluation

Avoid:
- celebrity drama
- generic finance
- vague hype
- non-technical content

Return ONLY a single integer from 1-10.

Topic:
Title: {item.get("title", "")}

Summary:
{item.get("summary", "")}
"""

    try:

        raw = (
            llm.invoke(prompt)
            .content
            .strip()
        )

        score = int(raw)

        return max(
            1,
            min(score, 10)
        )

    except:
        return 5


def rank_trends(state):

    print("\n[Node] Ranking trends...")

    trends = state["trends"]

    scored = []

    for item in trends:

        llm_score = score_single_trend(item)

        final_score = (
            llm_score
            + get_source_weight(item)
        )

        item["ranking_score"] = final_score

        scored.append(item)

    scored.sort(
        key=lambda x: x["ranking_score"],
        reverse=True
    )

    return {
        "ranked_trends": scored
    }