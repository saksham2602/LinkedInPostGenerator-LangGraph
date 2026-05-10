from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="mistral",
    temperature=0
)


def review_post(post, topic=None):
    topic = topic or {}
    source_name = topic.get("source", "Source") if isinstance(topic, dict) else "Source"
    source_type = topic.get("source_type", "") if isinstance(topic, dict) else ""

    prompt = f"""
Rewrite this LinkedIn post so it sounds like a thoughtful builder wrote it.

Output ONLY the final post.

Hard rules:
- No title
- No hashtags
- No emojis
- No markdown links
- No fake personal experience
- No invented identity
- No invented urgency
- No motivational ending
- No generic CTA like "Let's discuss", "What are your thoughts", or "How can we ensure"
- Do not say "I encountered", "I experienced", or "As a young AI engineer"
- Do not overclaim from a discussion source
- Keep the source line at the end
- Source format must be exactly:
  Source: {source_name}
- Do not write "Source: News Outlet" unless the source name is actually News Outlet
- Keep it between 130 and 200 words

Style:
- Short paragraphs
- Specific technical insight
- Slightly opinionated
- Calm tone
- Builder/engineer perspective
- Avoid corporate language
- Prefer concrete failure modes over abstract strategy language
- It is okay to end with a sharp observation instead of a question

For discussion sources like Hacker News or Reddit:
- Treat them as signals, not proof
- Use phrases like:
  "A Hacker News discussion raised an interesting issue..."
  "The useful part of the discussion was..."
- Do not write as if the issue is scientifically proven

Avoid these words/phrases:
- As a young AI engineer
- I've encountered
- lively conversation
- remarkable
- impressive
- undeniably
- pressing issue
- substantial errors
- disconcerting
- Let's discuss
- What are your thoughts
- How can we ensure
- develop strategies
- user preferences and behaviors
- dynamic consumer behavior
- share our thoughts
- utilizing
- delve
- revolutionary
- game-changer
- future of AI
- AI community
- changing the world
If the post sounds like consulting/corporate writing, rewrite it into simple engineering language.

Replace vague corporate phrases with concrete system design language.

Bad:
"technical hurdles loom large"

Good:
"the hard part is reliability, ownership, and failure isolation"

Bad:
"disparate systems"

Good:
"old systems built by different teams with different APIs"

Bad:
"single points of failure is a significant challenge"

Good:
"one shared layer going down can break many services at once"

Do not use a visible template.
Do not include "My takeaway:".
Do not end with multiple questions.
If you ask a question, ask only one concrete technical question.

If the post sounds like a research abstract, rewrite it into a builder-style LinkedIn post using simple engineering language.

Source name to preserve:
{source_name}

Source type:
{source_type}

POST:
{post}
"""

    return llm.invoke(prompt).content.strip()
