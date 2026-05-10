from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="mistral",
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

    return llm.invoke(prompt).content.strip()