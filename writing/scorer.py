from langchain_ollama import ChatOllama
import re

llm = ChatOllama(model="mistral", temperature=0)


def score_post(post):
    prompt = f"""
Score this LinkedIn post from 1 to 10.

Give low score if:
- contains emojis
- contains hashtags
- sounds motivational
- sounds generic
- overclaims
- uses a visible template like "My takeaway:"
- ends with "What are your thoughts" or another generic CTA
- has phrases like "let's delve", "future of AI", "bridging the gap"
- repeats the same abstract idea without adding concrete details
- uses placeholder sources like "Source: News Outlet"

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
