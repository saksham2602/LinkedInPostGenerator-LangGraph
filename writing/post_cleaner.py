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
}

GENERIC_CTA_PATTERNS = [
    r"\n*What are your thoughts(?: on this issue)?\??\s*(?=\n+Source:|\Z)",
    r"\n*Let's discuss!?\s*(?=\n+Source:|\Z)",
    r"\n*Curious to know what you think\.?\s*(?=\n+Source:|\Z)",
    r"\n*How can we ensure [^\n?]+\?\s*(?=\n+Source:|\Z)",
]


def clean_post(post: str, topic=None) -> str:
    topic = topic or {}
    source_name = topic.get("source", "") if isinstance(topic, dict) else ""
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

    if source_name:
        cleaned = re.sub(
            r"Source:\s*(News Outlet|Unknown|Source)\s*$",
            f"Source: {source_name}",
            cleaned,
            flags=re.IGNORECASE
        )

    # Convert markdown links like [Link] - <url> to plain URL
    cleaned = re.sub(
        r"\[Link\]\s*-\s*<([^>]+)>",
        r"\1",
        cleaned
    )

    cleaned = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r"\2",
        cleaned
    )

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

    return cleaned
