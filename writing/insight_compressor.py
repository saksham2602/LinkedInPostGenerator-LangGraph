from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="mistral",
    temperature=0.1
)


def compress_insight(state):
    print("\n[Node] Compressing insight...")

    prompt = f"""
Topic:
{state["topic"]}

Raw insight:
{state["contrarian_insight"]}

Create ONE sharp engineering takeaway.

STRICT RULES:
- Do not add new claims
- Do not say LLMs understand personality, emotions, or cognitive ability
- Do not say revolutionize, transform, streamline, or personalize
- Focus on evaluation/testing of LLM behavior
- Mention uncertainty if needed
- Max 2 sentences
- No hype

Return only the takeaway.
"""

    takeaway = llm.invoke(prompt).content.strip()

    print("Compressed insight:", takeaway)

    return {
        "compressed_insight": takeaway
    }