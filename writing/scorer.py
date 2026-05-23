import os
import re

from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from writing.llm_utils import invoke_with_retries

load_dotenv()

llm = ChatNVIDIA(
  model="google/gemma-2-2b-it",
  api_key=os.getenv("NVIDIA_API_KEY"),
  temperature=0.1,
  max_tokens=8,
)


def score_post(post):
    prompt = f"""
Return one integer from 1 to 10 for this LinkedIn post.

Score high if it is specific, technical, grounded in the source, and human.
Score low if it has emojis, hashtags, hype, generic CTA, fake claims, weak source, or corporate filler.

Return ONLY one number.

POST:
{post}
"""

    try:
        result = invoke_with_retries(llm, prompt)
    except Exception:
        return 5

    try:
        match = re.search(r"\b10\b|[1-9]", result)
        if not match:
            return 5

        return int(match.group())
    except:
        return 5
