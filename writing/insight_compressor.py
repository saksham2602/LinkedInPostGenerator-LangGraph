import os

from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_ollama import ChatOllama
from writing.llm_utils import invoke_with_retries

load_dotenv()

llm = ChatNVIDIA(
  model="google/gemma-2-2b-it",
  api_key=os.getenv("NVIDIA_API_KEY"),
  temperature=0.2,
  top_p=0.7,
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

    takeaway = invoke_with_retries(llm, prompt)

    print("Compressed insight:", takeaway)

    return {
        "compressed_insight": takeaway
    }
