import os
from html import escape
from datetime import datetime

import streamlit as st
import pandas as pd

from agent.graph import graph
from evaluation.store import get_evaluation_summary, load_evaluations
from storage.memory_store import load_memory


st.set_page_config(
    page_title="LinkedIn AI Content Agent",
    page_icon="AI",
    layout="wide"
)


# ---------- Styling ----------
st.markdown(
    """
    <style>
    :root {
        --bg: #0b0f14;
        --panel: #111821;
        --panel-2: #151d29;
        --line: #263241;
        --muted: #9aa7b5;
        --text: #f4f7fb;
        --accent: #ff4b4b;
        --accent-2: #62d0a2;
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 20% 0%, rgba(255, 75, 75, 0.12), transparent 28%),
            linear-gradient(180deg, #0b0f14 0%, #0d1118 100%);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .app-hero {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 24px 26px;
        background: linear-gradient(135deg, rgba(17, 24, 33, 0.98), rgba(13, 18, 26, 0.94));
        margin-bottom: 18px;
    }

    .app-kicker {
        color: var(--accent-2);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .app-title {
        color: var(--text);
        font-size: 2.2rem;
        line-height: 1.1;
        font-weight: 800;
        margin: 0 0 8px 0;
    }

    .app-subtitle {
        color: var(--muted);
        font-size: 0.98rem;
        max-width: 760px;
        margin: 0;
    }

    .control-panel {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 14px;
        background: rgba(17, 24, 33, 0.92);
    }

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 12px;
        margin: 12px 0 22px 0;
    }

    .metric-card {
        background: rgba(17, 24, 33, 0.94);
        padding: 16px;
        border-radius: 8px;
        border: 1px solid var(--line);
        min-height: 96px;
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .metric-value {
        color: var(--text);
        font-size: 1.65rem;
        line-height: 1.1;
        font-weight: 750;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .metric-note {
        color: var(--muted);
        font-size: 0.82rem;
        margin-top: 6px;
    }

    .section-title {
        color: var(--text);
        font-size: 1.3rem;
        font-weight: 780;
        margin: 0 0 12px 0;
    }

    .topic-strip {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 14px 16px;
        background: rgba(21, 29, 41, 0.9);
        margin-bottom: 16px;
    }

    .topic-title {
        color: var(--text);
        font-weight: 700;
        margin-bottom: 4px;
    }

    .topic-meta {
        color: var(--muted);
        font-size: 0.88rem;
    }

    .empty-panel {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 34px 28px;
        background: rgba(17, 24, 33, 0.94);
        margin-top: 18px;
    }

    .empty-panel h3 {
        color: var(--text);
        margin: 0 0 8px 0;
    }

    .empty-panel p {
        color: var(--muted);
        margin: 0;
    }

    .small-muted {
        color: var(--muted);
        font-size: 0.9rem;
    }

    .status-pill {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: #1f6feb;
        color: white;
        font-size: 0.8rem;
        font-weight: 600;
    }

    div[data-testid="stTextArea"] textarea {
        border-radius: 8px;
        border: 1px solid var(--line);
        background: #151a24;
        color: var(--text);
        font-size: 1rem;
        line-height: 1.6;
    }

    div[data-testid="stTabs"] button {
        font-weight: 650;
    }

    @media (max-width: 900px) {
        .metric-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .app-title {
            font-size: 1.7rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


def metric_card(label, value, note=""):
    return {
        "label": label,
        "value": value,
        "note": note,
    }


def render_metric_grid(items):
    columns = st.columns(len(items))

    for column, item in zip(columns, items):
        with column:
            st.metric(item["label"], item["value"])
            if item.get("note"):
                st.caption(item["note"])


# ---------- Session ----------
if "result" not in st.session_state:
    st.session_state.result = None

if "edited_post" not in st.session_state:
    st.session_state.edited_post = ""


# ---------- Header ----------
left, right = st.columns([0.72, 0.28])

with left:
    st.markdown(
        """
        <div class="app-hero">
            <div class="app-kicker">LangGraph content workflow</div>
            <h1 class="app-title">LinkedIn AI Content Agent</h1>
            <p class="app-subtitle">
                Multi-source trend collection, topic ranking, post generation,
                scoring feedback, and human approval in one demo-ready dashboard.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with right:
    st.markdown("**Run Controls**")
    enable_image = st.toggle(
        "Generate image",
        value=False,
        help="Image generation is slower, so keep it off for a faster demo."
    )

    run_btn = st.button(
        "Generate New Post",
        type="primary",
        use_container_width=True
    )
    st.caption("Fast path keeps image generation off.")


# ---------- Run Agent ----------
if run_btn:
    with st.spinner("Running LangGraph agent..."):
        result = graph.invoke({"enable_image": enable_image})
        st.session_state.result = result
        st.session_state.edited_post = result.get("final_post", "")


result = st.session_state.result


# ---------- Empty State ----------
if not result:
    st.markdown(
        """
        <div class="empty-panel">
            <h3>Ready to generate a post</h3>
            <p>
                Click Generate New Post to fetch ranked trends, select a topic,
                draft a LinkedIn post, score it, and prepare it for approval.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()


# ---------- Top Metrics ----------
score = result.get("score", "-")
evaluation = result.get("evaluation", {})
evaluation_score = evaluation.get("evaluation_score", "-")
content_type = result.get("content_type", "-")
needs_image = result.get("needs_image", False)
topic = result.get("topic", {})
source = topic.get("source", "unknown") if isinstance(topic, dict) else "unknown"
topic_title = topic.get("title", "Selected topic") if isinstance(topic, dict) else str(topic)

render_metric_grid([
    {
        "label": "Quality Score",
        "value": score,
        "note": "LLM feedback loop",
    },
    {
        "label": "Eval Score",
        "value": evaluation_score,
        "note": "deterministic checks",
    },
    {
        "label": "Content Type",
        "value": content_type,
        "note": "selected format",
    },
    {
        "label": "Image",
        "value": "Generated" if result.get("image_bytes") else "Skipped",
        "note": "optional path",
    },
    {
        "label": "Source",
        "value": source,
        "note": "selected signal",
    },
])

st.markdown(
    f"""
    <div class="topic-strip">
        <div class="topic-title">{escape(str(topic_title))}</div>
        <div class="topic-meta">Selected from {escape(str(source))} after ranking and memory checks</div>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------- Main Tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Preview",
        "Agent Reasoning",
        "Evaluation",
        "Memory",
        "Raw State"
    ]
)


# ---------- Preview Tab ----------
with tab1:
    col1, col2 = st.columns([0.58, 0.42])

    with col1:
        st.markdown('<div class="section-title">Final Post</div>', unsafe_allow_html=True)

        edited_post = st.text_area(
            "Edit before approval",
            value=st.session_state.edited_post,
            height=360,
            label_visibility="collapsed"
        )

        st.session_state.edited_post = edited_post

        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("Save Approved Post", use_container_width=True):
                os.makedirs("approved_posts", exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"approved_posts/post_{timestamp}.txt"

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(edited_post)

                st.success(f"Saved: {filename}")

        with c2:
            st.download_button(
                "Download Post",
                data=edited_post,
                file_name="linkedin_post.txt",
                mime="text/plain",
                use_container_width=True
            )

        with c3:
            st.button(
                "Post to LinkedIn",
                disabled=True,
                use_container_width=True,
                help="Add LinkedIn API later after approval workflow is stable."
            )

        st.caption("Approval-first workflow: no automated posting is performed.")

    with col2:
        st.markdown('<div class="section-title">Generated Image</div>', unsafe_allow_html=True)

        if result.get("image_bytes"):
            image = result["image_bytes"]
            st.image(image, use_container_width=True)

            os.makedirs("approved_posts", exist_ok=True)

            # Save image preview for download
            image_path = "approved_posts/latest_image.png"
            image.save(image_path)
            

            with open(image_path, "rb") as f:
                st.download_button(
                    "Download Image",
                    data=f,
                    file_name="linkedin_image.png",
                    mime="image/png",
                    use_container_width=True
                )
        elif result.get("image_error"):

            st.warning(
                "Image generation failed."
            )

            st.code(
                result["image_error"]
            )
        else:
            st.info(
                "Image generation was skipped. Turn on Generate image before running the agent if you want one."
            )

        with st.expander("Selected topic", expanded=True):
            if isinstance(topic, dict):
                st.write(topic.get("title", ""))
                st.caption(topic.get("reason", ""))
            else:
                st.write(topic)


# ---------- Agent Reasoning Tab ----------
with tab2:
    st.subheader("Selected Topic")

    if isinstance(topic, dict):
        st.json(topic)
    else:
        st.write(topic)

    st.subheader("Reasoning Chain")

    reasoning_data = {
        "Content Type": result.get("content_type"),
        "Contrarian Insight": result.get("contrarian_insight"),
        "Compressed Insight": result.get("compressed_insight"),
        "Visual Decision": "Image required" if result.get("needs_image") else "No image",
        "Image Prompt": result.get("image_prompt", "N/A"),
    }

    for key, value in reasoning_data.items():
        with st.expander(key, expanded=False):
            st.write(value)

    st.subheader("Fetched Trends")

    trends = result.get("trends", [])
    if trends:
        st.dataframe(
            pd.DataFrame(trends),
            use_container_width=True
        )
    else:
        st.info("No trends found.")

    st.subheader("Ranked Trends")

    ranked = result.get("ranked_trends", [])
    if ranked:
        st.dataframe(
            pd.DataFrame(ranked),
            use_container_width=True
        )
    else:
        st.info("No ranked trends found.")


# ---------- Evaluation Tab ----------
with tab3:
    st.markdown('<div class="section-title">Current Post Evaluation</div>', unsafe_allow_html=True)

    if evaluation:
        render_metric_grid([
            {
                "label": "Overall",
                "value": evaluation.get("evaluation_score", "-"),
                "note": "combined score",
            },
            {
                "label": "Human Tone",
                "value": evaluation.get("human_tone_score", "-"),
                "note": "anti-generic checks",
            },
            {
                "label": "Specificity",
                "value": evaluation.get("specificity_score", "-"),
                "note": "technical detail",
            },
            {
                "label": "Source",
                "value": evaluation.get("source_faithfulness_score", "-"),
                "note": "source line match",
            },
            {
                "label": "CTA",
                "value": evaluation.get("cta_quality_score", "-"),
                "note": "ending quality",
            },
        ])

        st.dataframe(
            pd.DataFrame([evaluation]),
            use_container_width=True
        )
    else:
        st.info("No evaluation available for this run.")

    st.markdown('<div class="section-title">Evaluation History</div>', unsafe_allow_html=True)

    evaluations = load_evaluations()
    summary = get_evaluation_summary()

    if summary:
        s1, s2, s3, s4 = st.columns(4)

        with s1:
            st.metric("Evaluated Posts", summary.get("total_evaluated", 0))

        with s2:
            st.metric("Avg Eval Score", summary.get("avg_evaluation_score", 0))

        with s3:
            st.metric("Generic CTA Rate", summary.get("generic_cta_rate", 0))

        with s4:
            st.metric("Source Validity", summary.get("source_validity_rate", 0))

        st.dataframe(
            pd.DataFrame(evaluations[::-1]),
            use_container_width=True
        )
    else:
        st.info("No evaluation history yet.")


# ---------- Memory Tab ----------
with tab4:
    st.subheader("Post Memory")

    memory = load_memory()

    if memory:
        df = pd.DataFrame(memory[::-1])

        st.dataframe(
            df,
            use_container_width=True
        )

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.metric("Total Saved Posts", len(memory))

        with col_b:
            avg_score = round(
                sum(item.get("score", 0) for item in memory) / len(memory),
                2
            )
            st.metric("Average Score", avg_score)

        with col_c:
            image_count = sum(
                1 for item in memory if item.get("needs_image")
            )
            st.metric("Posts With Images", image_count)

    else:
        st.info("No memory yet.")


# ---------- Raw State Tab ----------
with tab5:
    st.subheader("Raw LangGraph State")
    st.json(result)
