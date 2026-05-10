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
}


def clean_post(post: str) -> str:
    cleaned = post

    for bad, good in BANNED_REPLACEMENTS.items():
        cleaned = re.sub(
            bad,
            good,
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

    return cleaned