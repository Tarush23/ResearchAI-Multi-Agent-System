"""
Streamlit UI for the Multi-Agent Research System.

Drop this file into your `multi agent system project` folder (same level as
pipeline.py, agents.py, tools.py) and run it with:

    streamlit run streamlit_app.py

It calls `run_research_pipeline` from pipeline.py and displays the
search results, scraped content, final report, and critic feedback.
"""

import io
import contextlib
import traceback

import streamlit as st

from pipeline import run_research_pipeline


st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🔎",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "result" not in st.session_state:
    st.session_state.result = None
if "logs" not in st.session_state:
    st.session_state.logs = ""
if "error" not in st.session_state:
    st.session_state.error = None

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ About")
    st.write(
        "This UI drives a 4-stage pipeline:\n\n"
        "1. **Search Agent** — finds recent, reliable sources\n"
        "2. **Reader Agent** — scrapes the most relevant source\n"
        "3. **Writer Chain** — drafts the report\n"
        "4. **Critic Chain** — reviews and gives feedback"
    )
    st.divider()
    show_logs = st.toggle("Show raw console logs", value=False)
    if st.button("🗑️ Clear results", use_container_width=True):
        st.session_state.result = None
        st.session_state.logs = ""
        st.session_state.error = None
        st.rerun()

# ---------------------------------------------------------------------------
# Header + input
# ---------------------------------------------------------------------------
st.title("🔎 Multi-Agent Research System")
st.caption("Search → Read → Write → Critique, powered by your agent pipeline")

with st.form("research_form"):
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. Impact of quantum computing on cryptography",
    )
    submitted = st.form_submit_button("🚀 Run research", use_container_width=True)

# ---------------------------------------------------------------------------
# Run pipeline
# ---------------------------------------------------------------------------
if submitted:
    if not topic or not topic.strip():
        st.warning("Please enter a topic before running the pipeline.")
    else:
        st.session_state.error = None
        log_buffer = io.StringIO()
        with st.status("Running research pipeline...", expanded=True) as status:
            try:
                status.write("Step 1 — Search agent is working...")
                status.write("Step 2 — Reader agent will scrape top resources...")
                status.write("Step 3 — Writer agent will draft the report...")
                status.write("Step 4 — Critic agent will review the report...")

                # pipeline.py uses print() internally; capture that output
                # so it can optionally be shown in the UI instead of only
                # appearing in the terminal.
                with contextlib.redirect_stdout(log_buffer):
                    result = run_research_pipeline(topic.strip())

                st.session_state.result = result
                st.session_state.logs = log_buffer.getvalue()
                status.update(label="Pipeline complete ✅", state="complete")

            except Exception as e:
                st.session_state.error = f"{e}\n\n{traceback.format_exc()}"
                st.session_state.logs = log_buffer.getvalue()
                status.update(label="Pipeline failed ❌", state="error")

# ---------------------------------------------------------------------------
# Error display
# ---------------------------------------------------------------------------
if st.session_state.error:
    st.error("The pipeline raised an error:")
    st.code(st.session_state.error)

# ---------------------------------------------------------------------------
# Results display
# ---------------------------------------------------------------------------
if st.session_state.result:
    result = st.session_state.result

    tab_report, tab_critic, tab_search, tab_scraped = st.tabs(
        ["📄 Final Report", "🧐 Critic Feedback", "🔍 Search Results", "📚 Scraped Content"]
    )

    with tab_report:
        st.subheader("Final Report")
        report = result.get("report", "No report generated.")
        st.markdown(
            report if isinstance(report, str) else str(report)
        )
        st.download_button(
            "⬇️ Download report (.md)",
            data=report if isinstance(report, str) else str(report),
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_critic:
        st.subheader("Critic Feedback")
        feedback = result.get("feedback", "No feedback generated.")
        st.markdown(feedback if isinstance(feedback, str) else str(feedback))

    with tab_search:
        st.subheader("Raw Search Results")
        st.text(result.get("search_results", "No search results."))

    with tab_scraped:
        st.subheader("Scraped Content")
        st.text(result.get("scraped_content", "No scraped content."))

# ---------------------------------------------------------------------------
# Optional raw logs
# ---------------------------------------------------------------------------
if show_logs and st.session_state.logs:
    with st.expander("🖥️ Console logs", expanded=False):
        st.code(st.session_state.logs)