from langchain_nvidia_ai_endpoints import ChatNVIDIA
import re

llm = ChatNVIDIA(
  model="mistralai/mistral-large-3-675b-instruct-2512",
  api_key="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", 
)


def score_post(post):
    prompt = f"""
Score this LinkedIn post from 1 to 10.

Give low score if:
- contains emojis
- contains hashtags
- sounds motivational
- sounds generic
- overclaims
- repeats the same visible template in a stiff way
- ends with "What are your thoughts" or another generic CTA
- has phrases like "let's delve", "future of AI", "bridging the gap"
- repeats the same abstract idea without adding concrete details
- uses placeholder sources like "Source: News Outlet"
- says "perform optimally", "robust systems", "unseen scenarios", or "striking the right balance"
- ends with "How do you manage this trade-off in your projects?"
- ends with "How do you ensure..."
- starts with "In AI development"
- uses academic filler like "critical factor", "practical implications", "mechanisms", or "addresses the challenge"

Return ONLY one number.

POST:
{post}
"""

    result = llm.invoke(prompt).content.strip()

    try:
        match = re.search(r"\b10\b|[1-9]", result)
        if not match:
            return 5

        return int(match.group())
    except:
        return 5
