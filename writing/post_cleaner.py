import re


BANNED_REPLACEMENTS = {
    "I recently stumbled upon": "I came across",
    "stumbled upon": "came across",
    "intriguing": "interesting",
    "shed light on": "pointed to",
    "tech mogul": "investor",
    "rapidly evolving field": "field",
    "serves as a reminder": "shows",
    "crucial": "important",
    "delve": "look",
    "revolutionize": "change",
    "game-changer": "useful shift",
    "enhancing personalized shopping experiences": "making shopping agents more useful",
    "dynamic and unpredictable nature": "messiness",
    "develop strategies": "build systems",
    "utilizing": "using",
    "a important": "an important",
    "In AI development, ": "",
    "perform optimally": "work well",
    "more robust systems": "more reliable systems",
    "robust systems": "reliable systems",
    "unseen scenarios": "new cases",
    "striking the right balance": "finding the right tradeoff",
    "promising guarantees": "useful bounds",
    "critical factor": "hard part",
    "practical implications": "practical use",
    "addresses the challenge": "looks at the problem",
    "informed decisions": "better choices",
    "mechanisms": "systems",
    "how much training data do you need to ensure future success?": "how much training data is enough before trusting the selector later.",
    "providing insights into": "looking at",
    "dynamic adaptation": "the selector changing over time",
    "valuable adaptive improvements": "useful updates",
    "This research offers a clearer path for engineers to make better choices about when to trust their algorithm selectors.": "That is the useful part: it gives builders a way to reason about trust before the selector is put to work.",
    "This is important for": "That matters for",
    "ensuring that": "making sure",
}

GENERIC_CTA_PATTERNS = [
    r"\n*What are your thoughts(?: on this issue)?\??\s*(?=\n+Source:|\Z)",
    r"\n*Let's discuss!?\s*(?=\n+Source:|\Z)",
    r"\n*Curious to know what you think\.?\s*(?=\n+Source:|\Z)",
    r"\n*How can we ensure [^\n?]+\?\s*(?=\n+Source:|\Z)",
    r"\n*How do you ensure [^\n?]+\?\s*(?=\n+Source:|\Z)",
    r"\n*How do you handle [^\n?]+\?\s*(?=\n+Source:|\Z)",
    r"\n*How do you manage [^\n?]+\?\s*(?=\n+Source:|\Z)",
    r"\n*How do you manage this trade-?off in your projects\?\s*(?=\n+Source:|\Z)",
]


def clean_post(post: str, topic=None) -> str:
    topic = topic or {}
    source_name = topic.get("source", "") if isinstance(topic, dict) else ""
    source_url = topic.get("url", "") if isinstance(topic, dict) else ""
    expected_source_line = (
        f"Source: [{source_name}]({source_url})"
        if source_name and source_url
        else f"Source: {source_name}"
        if source_name
        else ""
    )
    cleaned = post

    for bad, good in BANNED_REPLACEMENTS.items():
        cleaned = re.sub(
            bad,
            good,
            cleaned,
            flags=re.IGNORECASE
        )

    for pattern in GENERIC_CTA_PATTERNS:
        cleaned = re.sub(
            pattern,
            "",
            cleaned,
            flags=re.IGNORECASE
        )

    if expected_source_line:
        cleaned = re.sub(
            r"Source:\s*(?:\[[^\]]+\]\([^)]+\)|[^\n]+)\s*$",
            expected_source_line,
            cleaned,
            flags=re.IGNORECASE
        )

    elif source_name:
        cleaned = re.sub(
            r"Source:\s*(News Outlet|Unknown|Source)\s*$",
            f"Source: {source_name}",
            cleaned,
            flags=re.IGNORECASE
        )

    source_type = topic.get("source_type", "") if isinstance(topic, dict) else ""
    is_paper_source = source_name.lower() == "arxiv" or source_type.lower() == "arxiv"

    if is_paper_source:
        cleaned = re.sub(
            r"^When selecting algorithms adaptively based on past performance, how much training data is enough before you can trust the selector\?",
            "Adaptive algorithm selection has a practical failure mode: you need enough training data before you can trust the selector later.",
            cleaned,
            flags=re.IGNORECASE
        )

    # Convert markdown links like [Link] - <url> to plain URL outside the source line.
    cleaned = re.sub(
        r"\[Link\]\s*-\s*<([^>]+)>",
        r"\1",
        cleaned
    )

    lines = cleaned.splitlines()
    cleaned_lines = []

    for line in lines:
        if line.strip().lower().startswith("source:"):
            cleaned_lines.append(line)
            continue

        cleaned_lines.append(
            re.sub(
                r"\[([^\]]+)\]\(([^)]+)\)",
                r"\2",
                line
            )
        )

    cleaned = "\n".join(cleaned_lines)

    # Remove angle brackets around URLs
    cleaned = re.sub(
        r"<(https?://[^>]+)>",
        r"\1",
        cleaned
    )

    # Remove emojis/basic unicode symbols
    cleaned = re.sub(
        r"[^\x00-\x7F]+",
        "",
        cleaned
    )

    # Cleanup extra spaces/newlines
    cleaned = re.sub(
        r"\n{3,}",
        "\n\n",
        cleaned
    ).strip()

    cleaned = re.sub(
        r"([^\n])\nSource:",
        r"\1\n\nSource:",
        cleaned
    )

    if expected_source_line and not cleaned.strip().endswith(expected_source_line):
        cleaned = re.sub(
            r"\n*Source:\s*(?:\[[^\]]+\]\([^)]+\)|[^\n]+)\s*$",
            "",
            cleaned,
            flags=re.IGNORECASE
        ).strip()
        cleaned = f"{cleaned}\n\n{expected_source_line}"

    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]

    return cleaned
