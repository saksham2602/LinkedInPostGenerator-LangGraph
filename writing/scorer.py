from langchain_ollama import ChatOllama

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
- has phrases like "let's delve", "future of AI", "bridging the gap"

Return ONLY one number.

POST:
{post}
"""

    result = llm.invoke(prompt).content.strip()

    try:
        return int(result[0])
    except:
        return 5