from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_ollama import ChatOllama

llm = ChatNVIDIA(
  model="google/gemma-2-2b-it",
  api_key = "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", 
  temperature=0.2,
  top_p=0.7,
)


def generate_contrarian_insight(state):
    print("\n[Node] Generating contrarian insight...")

    prompt = f"""
Topic:
{state["topic"]}

Content type:
{state["content_type"]}

Give one non-obvious insight for a LinkedIn post.

Avoid generic lines like:
- AI is changing the world
- The future is AI
- Upskilling is important

Return only 1-2 sentences.
"""

    insight = llm.invoke(prompt).content.strip()

    print("Insight:", insight)

    return {
        "contrarian_insight": insight
    }
