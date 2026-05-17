import os

from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

load_dotenv()

llm = ChatNVIDIA(
  model="stepfun-ai/step-3.5-flash",
  api_key=os.getenv("NVIDIA_API_KEY"),
)


def review_post(post, topic=None):
    topic = topic or {}
    source_name = topic.get("source", "Source") if isinstance(topic, dict) else "Source"
    source_type = topic.get("source_type", "") if isinstance(topic, dict) else ""
    title = topic.get("title", "") if isinstance(topic, dict) else ""
    summary = topic.get("summary", "") if isinstance(topic, dict) else ""
    url = topic.get("url", "") if isinstance(topic, dict) else ""
    source_line = (
        f"Source: [{source_name}]({url})"
        if url
        else f"Source: {source_name}"
    )

    prompt = f"""
Rewrite the draft from scratch as a human LinkedIn post for technical readers.

Use the original topic as the source of truth. The draft is flawed input, not wording to preserve.

Original topic title:
{title}

Original topic summary:
{summary}

Source name:
{source_name}

Source type:
{source_type}

Source URL:
{url}

Draft to improve:
{post}

Output rules:
- Output ONLY the final post
- 110 to 180 words
- No title, hashtags, emojis, or raw URL in the body
- No markdown links except the final source line
- No fake personal experience
- No invented claims, metrics, incidents, companies, or author names
- Do not copy the original summary verbatim
- Do not mention this app, demos, interviews, dashboards, or content generation
- Every paragraph must be grounded in the original topic, source type, or draft
- End with exactly: {source_line}

Style rules:
- Sound like a builder explaining the useful part to another builder
- Do not sound like an essay, article, newsletter, analyst note, or consultant memo
- Use short paragraphs, usually 1 or 2 sentences each
- Prefer concrete engineering language
- Start with the actual subject, not "In AI development"
- The first sentence must be a statement, not a question
- Rewrite vague sentences instead of polishing them
- It is okay to use a small pivot like "The hard part:" or "My takeaway:" if it makes the post feel natural
- Prefer "how much data is enough before trusting it" over "training set size becomes a critical factor"
- Prefer "pick too early and you overfit to noise" over "balancing sufficient evidence and adaptation"
- Prefer "model routing, solver selection, fallback choices" over "practical implications"

Target cadence:
- One direct opening sentence
- One short paragraph saying what the source looked at
- Two or three paragraphs explaining the technical failure mode or design choice
- A short takeaway or one concrete question
- Source line

Keep the post grounded. If a sentence could fit any AI topic, replace it with a detail from the topic.

Forbidden phrases:
- In AI development
- important aspect
- critical factor
- necessary
- ensure
- perform optimally
- promising guarantees
- robust systems
- unseen scenarios
- striking the right balance
- this insight can lead
- generalize well
- addresses the challenge
- practical implications
- significant
- mechanisms
- informed decisions
- dynamic nature
- historical data
- sufficient evidence
- crucial
- tough nut to crack
- Let's discuss
- What are your thoughts
- How do you manage
- How do you handle
- How do you ensure

For arXiv or paper sources:
- Use "paper" or "research note"
- Do not call it a discussion
- Do not open with a question
- Explain the practical engineering problem plainly
- Good angle for algorithm-selection papers: how much evidence is enough before trusting a selector that adapts from past results
- A final question is allowed only if it is specific and technical

For Reddit or Hacker News:
- Frame it as a discussion signal, not verified news

Example of the intended feel:
Power grid control is one of those AI use cases where "good performance" is not enough.

A recent arXiv paper explores voltage control using deep reinforcement learning.

The technical challenge is not only choosing the right DRL algorithm. It is also deciding what the model should observe, how the state space is represented, and how the reward function is designed.

That matters because reward design can quietly shape the behavior of the entire system.

My takeaway:

For AI in power systems, the hard part is not just training an agent. It is proving that the agent remains reliable when the grid behaves differently from the training environment.

Source: arXiv

Do not copy examples from these instructions.
"""

    return llm.invoke(prompt).content.strip()
