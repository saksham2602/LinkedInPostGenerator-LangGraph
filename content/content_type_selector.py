from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=0
)


def select_content_type(state):
    print("\n[Node] Selecting content type...")

    prompt = f"""
You are choosing the best LinkedIn post format.

Topic:
{state["topic"]}

Choose ONLY one:

TREND_ANALYSIS
TECH_BREAKDOWN
BUILD_LOG
HOT_TAKE
PROJECT_SHOWCASE

Rules:
- AI news/company news â†’ TREND_ANALYSIS
- Technical concept/RAG/LangGraph â†’ TECH_BREAKDOWN
- User built something â†’ BUILD_LOG
- Strong opinion/controversial angle â†’ HOT_TAKE
- Personal project/demo â†’ PROJECT_SHOWCASE

Return only the label.
"""

    content_type = llm.invoke(prompt).content.strip().upper()

    print("Content type:", content_type)

    return {
        "content_type": content_type
    }
