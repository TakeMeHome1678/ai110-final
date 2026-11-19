import json
from pathlib import Path

import streamlit as st

from agent_utils import execute_agent
from rag_utils import extract_summary


st.set_page_config(page_title="Applied AI System", page_icon="🧠", layout="wide")
st.title("🧠 Applied AI Workbench")
st.caption("A reproducible RAG, agentic, and self-checking assistant for summaries, retrieval, planning, and debugging.")

KNOWLEDGE_PATH = Path("data/knowledge.json")


def load_documents() -> list[dict]:
    if not KNOWLEDGE_PATH.exists():
        return []
    try:
        return json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_document(title: str, text: str) -> None:
    documents = load_documents()
    documents.append({"id": f"user-{len(documents) + 1}", "title": title.strip(), "text": text.strip()})
    KNOWLEDGE_PATH.write_text(json.dumps(documents, indent=2, ensure_ascii=False), encoding="utf-8")


if "documents" not in st.session_state:
    st.session_state.documents = load_documents()
if "trace" not in st.session_state:
    st.session_state.trace = []

with st.sidebar:
    st.header("Controls")
    st.write("Source documents:", len(st.session_state.documents))
    if st.button("Reset source library"):
        st.session_state.documents = load_documents()
        st.success("Source library reloaded.")

ask_tab, source_tab, log_tab = st.tabs(["Ask the system", "Add sources", "Execution log"])

with ask_tab:
    task = st.text_area(
        "Request",
        placeholder="Summarize this source, retrieve Streamlit state guidance, plan a test, or debug a traceback...",
        height=110,
    )
    source_text = st.text_area(
        "Optional text to summarize",
        placeholder="Paste text here for summarization.",
        height=150,
    )

    col1, col2 = st.columns(2)
    with col1:
        run = st.button("Run agent", type="primary")
    with col2:
        quick_summary = st.button("Summarize only")

    if quick_summary:
        if not source_text.strip():
            st.error("Paste text before requesting a summary.")
        else:
            st.subheader("Summary")
            st.write(extract_summary(source_text, max_sentences=3))

    if run:
        task = task.strip()
        if not task:
            st.error("Enter a request before running the agent.")
        else:
            with st.spinner("Planning, retrieving, executing, and checking..."):
                result = execute_agent(task, source_text, st.session_state.documents)
            st.session_state.trace.append(result)

            if result.get("error"):
                st.error(result["error"])
            else:
                st.subheader("Answer")
                st.write(result["answer"])

                st.subheader("Confidence")
                st.progress(min(result["confidence"], 1.0))
                st.write(f"{result['confidence']:.0%}")

                st.subheader("Agent plan")
                for item in result["plan"]:
                    st.write(f"{item['step']}. {item['action']} — **{item['status']}**")

                st.subheader("Retrieved evidence")
                if result["evidence"]:
                    for item in result["evidence"]:
                        st.markdown(f"**{item['title']}** (score {item['score']:.2f})")
                        st.write(item["text"])
                else:
                    st.info("No supporting source passed the retrieval threshold.")

with source_tab:
    st.subheader("Add a custom source")
    title = st.text_input("Source title")
    text = st.text_area("Source text", height=180)
    if st.button("Add source"):
        if not title.strip() or not text.strip():
            st.error("Both a title and source text are required.")
        else:
            save_document(title, text)
            st.session_state.documents = load_documents()
            st.success("Source added and available to the retriever.")

    st.subheader("Current sources")
    for document in st.session_state.documents:
        with st.expander(document["title"]):
            st.write(document["text"])

with log_tab:
    st.subheader("Recent execution results")
    if not st.session_state.trace:
        st.info("Run the agent to create a trace.")
    for result in reversed(st.session_state.trace[-10:]):
        with st.expander(f"{result['kind'].title()} — {result['timestamp']}"):
            st.write("Confidence:", result["confidence"])
            st.write("Answer:", result["answer"])
            st.write("Plan:", result["plan"])
