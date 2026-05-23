import os

from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from writing.llm_utils import invoke_with_retries

load_dotenv()

llm = ChatNVIDIA(
    model="google/gemma-3n-e4b-it",
    api_key=os.getenv("NVIDIA_API_KEY"),
    temperature=0.2
)


def generate_image_prompt(post):
    prompt = f"""
Create a professional LinkedIn image prompt based on this post.

Rules:
- No readable text
- No letters
- No words
- No UI labels
- No charts with numbers
- No screenshots
- No fake interface text
- Use abstract visual metaphors only
- Clean professional AI/engineering style
- Suitable for LinkedIn
- 1:1 square composition

Post:
{post}

Return only the image prompt.
"""

    return invoke_with_retries(llm, prompt)
