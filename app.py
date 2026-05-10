import os
from datetime import datetime

import streamlit as st
import pandas as pd

from agent.graph import graph
from evaluation.store import get_evaluation_summary, load_evaluations
from storage.memory_store import load_memory


st.set_page_config(
    page_title="LinkedIn AI Content Agent",
    page_icon="🤖",
    layout="wide"
)


# ---------- Styling ----------
st.markdown(
    """
    <style>
    .main {
        background-color: #0f1117;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .metric-card {
        background: #161b22;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #30363d;
    }

    .small-muted {
        color: #8b949e;
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
    </style>
    """,
    unsafe_allow_html=True
)


# ---------- Session ----------
if "result" not in st.session_state:
    st.session_state.result = None

if "edited_post" not in st.session_state:
    st.session_state.edited_post = ""


# ---------- Header ----------
left, right = st.columns([0.75, 0.25])

with left:
    st.title("LinkedIn AI Content Agent")
    st.caption(
        "Multi-source tech intelligence → LangGraph reasoning → post + image → human approval"
    )

with right:
    st.markdown("###")
    run_btn = st.button(
        "Generate New Post",
        type="primary",
        use_container_width=True
    )


# ---------- Run Agent ----------
if run_btn:
    with st.spinner("Running LangGraph agent..."):
        result = graph.invoke({})
        st.session_state.result = result
        st.session_state.edited_post = result.get("final_post", "")


result = st.session_state.result


# ---------- Empty State ----------
if not result:
    st.info("Click **Generate New Post** to run the agent.")
    st.stop()


# ---------- Top Metrics ----------
score = result.get("score", "-")
evaluation = result.get("evaluation", {})
evaluation_score = evaluation.get("evaluation_score", "-")
content_type = result.get("content_type", "-")
needs_image = result.get("needs_image", False)
topic = result.get("topic", {})

m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.metric("Quality Score", score)

with m2:
    st.metric("Eval Score", evaluation_score)

with m3:
    st.metric("Content Type", content_type)

with m4:
    st.metric("Image", "Yes" if needs_image else "No")

with m5:
    source = topic.get("source", "unknown") if isinstance(topic, dict) else "unknown"
    st.metric("Source", source)


st.divider()


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
        st.subheader("Final Post")

        edited_post = st.text_area(
            "Edit before approval",
            value=st.session_state.edited_post,
            height=330,
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

        st.caption("Posting is disabled for now. Manual approval first is safer.")

    with col2:
        st.subheader("Generated Image")

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
            st.info("No image generated for this post.")


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
    st.subheader("Current Post Evaluation")

    if evaluation:
        e1, e2, e3, e4, e5 = st.columns(5)

        with e1:
            st.metric("Overall", evaluation.get("evaluation_score", "-"))

        with e2:
            st.metric("Human Tone", evaluation.get("human_tone_score", "-"))

        with e3:
            st.metric("Specificity", evaluation.get("specificity_score", "-"))

        with e4:
            st.metric("Source", evaluation.get("source_faithfulness_score", "-"))

        with e5:
            st.metric("CTA", evaluation.get("cta_quality_score", "-"))

        st.dataframe(
            pd.DataFrame([evaluation]),
            use_container_width=True
        )
    else:
        st.info("No evaluation available for this run.")

    st.subheader("Evaluation History")

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
