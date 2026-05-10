from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=0.1
)


def review_post(post, topic=None):
    topic = topic or {}
    source_name = topic.get("source", "Source") if isinstance(topic, dict) else "Source"
    source_type = topic.get("source_type", "") if isinstance(topic, dict) else ""
    title = topic.get("title", "") if isinstance(topic, dict) else ""
    summary = topic.get("summary", "") if isinstance(topic, dict) else ""

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

Draft to improve:
{post}

Output rules:
- Output ONLY the final post
- 120 to 190 words
- No title, hashtags, emojis, markdown links, or raw URL
- No fake personal experience
- No invented claims, metrics, incidents, companies, or author names
- End with exactly: Source: {source_name}

Style rules:
- Sound like a builder explaining the useful part to another builder
- Use short paragraphs
- Prefer concrete engineering language
- Start with the actual subject, not "In AI development"
- The first sentence must be a statement, not a question
- Rewrite vague sentences instead of polishing them
- Do not use a visible template
- Do not include "My takeaway:"
- Prefer "how much data is enough before trusting it" over "training set size becomes a critical factor"
- Prefer "pick too early and you overfit to noise" over "balancing sufficient evidence and adaptation"
- Prefer "model routing, solver selection, fallback choices" over "practical implications"

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
- Do not include any question marks
- Do not open with a question
- Explain the practical engineering problem plainly
- Good angle for algorithm-selection papers: how much evidence is enough before trusting a selector that adapts from past results

For Reddit or Hacker News:
- Frame it as a discussion signal, not verified news

Do not copy examples from these instructions.
"""

    return llm.invoke(prompt).content.strip()
