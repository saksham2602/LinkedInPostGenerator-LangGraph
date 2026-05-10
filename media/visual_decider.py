def decide_visual(state):
    print("\n[Node] Deciding image...")

    content_type = state.get("content_type", "")
    topic = str(state.get("topic", "")).lower()

    visual_keywords = [
        "robotics",
        "edge ai",
        "autonomy",
        "rag",
        "langgraph",
        "architecture",
        "agents",
        "llm",
        "model",
        "benchmark",
        "inference",
        "local"
    ]

    needs_image = (
        content_type in ["TECH_BREAKDOWN", "TREND_ANALYSIS", "PROJECT_SHOWCASE", "HOT_TAKE"]
        or any(word in topic for word in visual_keywords)
    )

    print("Visual decision:", "YES" if needs_image else "NO")

    return {"needs_image": needs_image}