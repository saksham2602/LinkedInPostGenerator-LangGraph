from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=0.35
)


def generate_post(state):
    topic = state.get("topic", {})

    title = topic.get("title", "")
    summary = topic.get("summary", "")
    source = topic.get("source", "Source")
    url = topic.get("url", "")

    content_type = state.get("content_type", "AI trend")
    insight = state.get("compressed_insight", "")

    source_type = topic.get("source_type", "")

    prompt = f"""
Write a LinkedIn post for a technical AI audience.

The post should sound like a thoughtful builder explaining one concrete thing they noticed.
It should not sound like an AI newsletter, a consultant memo, or a motivational post.

Use the content type as a loose hint, not a template.

Audience:
- engineers
- AI developers
- technical recruiters
- startup builders

Writing style:
- conversational but intelligent
- avoid corporate tone
- avoid motivational fluff
- avoid sounding like ChatGPT
- avoid generic excitement
- prefer concrete observations
- slightly opinionated is good
- use simple engineering language
- name real failure modes when possible
- vary sentence length like a human would

STRICT RULES:
- Output ONLY the final LinkedIn post
- No title
- No hashtags
- No markdown links
- No raw URL inside the post body
- No emojis
- Do not invent personal experience
- Do not invent author names, paper results, metrics, or background
- Do not overclaim
- Keep it between 140 and 220 words
- Keep the final source line exactly: Source: {source}

NEVER start with:
- "As an engineer"
- "I came across"
- "This highlights"
- "It's fascinating"
- "In today's AI landscape"
- "In the rapidly evolving"
- "Excited to share"

STRICT ANTI-INVENTION RULES:
- Never write in first person unless the source explicitly supports it.
- Do not say "I encountered", "I experienced", "I worked on", or "I noticed in my own work".
- You may say "One thing that stood out..." but not fake personal involvement.
- Do not invent urgency, risk, or impact level.
- Do not turn a discussion into a confirmed fact.
- If the source is Hacker News, Reddit, or a discussion forum, say "A discussion raised..." not "revealed" or "proved".

Avoid these words/phrases:
- As a young AI engineer
- I've encountered
- lively conversation
- pressing issue
- substantial errors
- Wouldn't it be
- Let's discuss
- share our thoughts
- utilizing
- preserving the intended content
- revolutionary
- game-changing
- transformative
- cutting-edge
- fascinating
- exciting
- underscores
- emphasizes
- delve
-seamless user experiences
-technical hurdles
-loom large
-paramount concerns
-disparate systems
-significant challenge
-demands attention
-grappled with
-predicaments
-mitigate these risks
-careful consideration
-potential impact
-additional complexity
-the question remains
-what strategies have you found successful
- landscape
- future of AI
- AI community
- changing the world
- Experience the
- remarkable
- undeniably impressive
- Curious to know
- Let's discuss
- How soon can we expect
- The secret lies
- My perspective:
- My takeaway:
- What are your thoughts
- How can we ensure
- How do you ensure
- develop strategies
- In AI development
- user preferences and behaviors
- perform optimally
- robust systems
- unseen scenarios
- striking the right balance
- promising guarantees
- critical factor
- practical implications
- addresses the challenge
- informed decisions
- mechanisms
- How do you manage this trade-off
- advancement
- boundaries of

Ending:
- You may end with one concrete technical question, but you do not have to.
- Never end with a generic engagement question.
- Do not ask more than one question.

Example:
Bad: "Let's discuss!"
Good: "Would you trust the agent to buy, or only to narrow the options?"

Prefer concrete engineering words over academic words.
Example:
Bad:
"formidable challenges due to the intricate nature of these systems"

Good:
"these systems change over time, depend on physical constraints, and can fail in rare edge cases"

Concrete beats abstract:
Bad:
"Consumer behavior is dynamic and unpredictable."

Good:
"A shopping agent has to deal with changing prices, seller trust, delivery dates, refunds, and users changing their mind halfway through."

Do not use a visible template.
Do not include "My takeaway:".
Do not write a paragraph that only says the world is complex or unpredictable.

If the source is arXiv or a research paper:
- Translate the paper into a practical engineering problem.
- Avoid academic filler like "promising guarantees" or "robust systems".
- Explain what a builder would actually decide differently.
- Good angle: "how much data is enough before trusting an algorithm selector?"
- End with a concrete observation, not a question.

Post context:

Title:
{title}

Summary:
{summary}

Content type:
{content_type}

Insight:
{insight}

Source name:
{source}

Source URL:
{url}

Source formatting rule:
At the end, write exactly:
Source: {source}

If source_type is "hackernews" or "reddit":
- Do not present the content as verified news.
- Frame it as a discussion or signal.
- Avoid strong claims like "this proves", "revealed", or "confirmed".

Do NOT include the raw URL.
"""

    return llm.invoke(prompt).content.strip()
