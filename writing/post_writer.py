import os

from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

load_dotenv()

llm = ChatNVIDIA(
  model="stepfun-ai/step-3.5-flash",
  api_key=os.getenv("NVIDIA_API_KEY"),
)


def generate_post(state):
    topic = state.get("topic", {})

    title = topic.get("title", "")
    summary = topic.get("summary", "")
    source = topic.get("source", "Source")
    url = topic.get("url", "")
    source_line = (
        f"Source: [{source}]({url})"
        if url
        else f"Source: {source}"
    )

    content_type = state.get("content_type", "AI trend")
    insight = state.get("compressed_insight", "")

    source_type = topic.get("source_type", "")

    prompt = f"""
Write a LinkedIn post for a technical AI audience.

Aim for this feel:
- a smart person explaining one useful technical point
- short paragraphs, like someone posting from notes
- specific enough for engineers, simple enough to read quickly
- calm, plain, and slightly opinionated

Do not write an essay.
Do not write a newsletter summary.
Do not sound like a consultant, brand page, or motivational post.

Use the content type as a loose hint, not a template.

Audience:
- engineers
- AI developers
- technical recruiters
- startup builders

Writing style:
- Open with the actual technical subject in one clean sentence
- Keep most paragraphs 1 or 2 sentences
- Prefer concrete observations over broad claims
- Name real failure modes when the source supports them
- Use simple engineering language
- Vary sentence length like a human would
- It is okay to use a small pivot like "The hard part:" or "My takeaway:" if it fits
- Avoid corporate tone, academic filler, motivational fluff, and generic excitement

STRICT RULES:
- Output ONLY the final LinkedIn post
- No title
- No hashtags
- No markdown links except the final source line
- No raw URL inside the post body
- No emojis
- Do not invent personal experience
- Do not invent author names, paper results, metrics, or background
- Do not overclaim
- Keep it between 110 and 180 words
- Keep the final source line exactly: {source_line}

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

Shape to imitate:
1. Start with one direct sentence about why the topic matters.
2. Add one short paragraph with what the source looked at.
3. Explain the technical decision or failure mode.
4. Add a short takeaway or concrete closing question.
5. End with the source line.

Do not use this shape so rigidly that every post feels identical.
Do not write a paragraph that only says the world is complex or unpredictable.

Example of the target cadence and level of detail:
Power grid control is one of those AI use cases where "good performance" is not enough.

A recent arXiv paper explores voltage control using deep reinforcement learning.

The technical challenge is not only choosing the right DRL algorithm. It is also deciding what the model should observe, how the state space is represented, and how the reward function is designed.

That matters because reward design can quietly shape the behavior of the entire system.

A model might learn to improve voltage stability in simulation, but still behave unpredictably under demand changes, sensor noise, renewable fluctuations, or fault conditions.

My takeaway:

For AI in power systems, the hard part is not just training an agent. It is proving that the agent remains reliable when the grid behaves differently from the training environment.

Would you trust a DRL-based controller after strong simulation results, or only after testing it against rare failure scenarios too?

Source: arXiv

If the source is arXiv or a research paper:
- Translate the paper into a practical engineering problem.
- Avoid academic filler like "promising guarantees" or "robust systems".
- Explain what a builder would actually decide differently.
- Good angle: "how much data is enough before trusting an algorithm selector?"
- End with either a concrete observation or one specific technical question.

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
{source_line}

If source_type is "hackernews" or "reddit":
- Do not present the content as verified news.
- Frame it as a discussion or signal.
- Avoid strong claims like "this proves", "revealed", or "confirmed".

Do NOT include the raw URL outside the final markdown source line.
"""

    return llm.invoke(prompt).content.strip()
