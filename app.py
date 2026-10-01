import hashlib
import os
import logging
from groq import RateLimitError
import streamlit as st
from styles import STYLES
from src.rag import ask
from src.knowledge import DATA_DIR
import time

st.set_page_config(
    page_title="QuackQuery",
    page_icon="🎓",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(STYLES, unsafe_allow_html=True)


st.title("QuackQuery")
st.caption("University document intelligence with inspectable evidence")

with st.sidebar:
    corpus = st.selectbox("Knowledge base", [os.environ["QUACKQUERY_CORPUS"]] if os.getenv("QUACKQUERY_CORPUS") else ["synthetic", "unverified", "verified"],
        format_func=lambda x: {"synthetic": "Synthetic demo", "unverified": "Original documents (unverified)", "verified": "Reviewed university sources"}[x])
    st.info("Fictional test documents, not official university guidance." if corpus == "synthetic"
            else ("Selected factual summaries checked against official Stevens pages on 2026-09-17; follow the source link for the full document." if corpus == "verified" else "These documents have not been verified against official university sources."))
    st.caption("Conversations stay in this browser session. Each knowledge base has its own history.")
    if st.button("Clear conversation"):
        st.session_state.setdefault("conversations", {})[corpus] = []
        st.session_state.setdefault("selected_turns", {}).pop(corpus, None)
    st.caption("Citations are checked for valid sources and matching quotations. This does not guarantee that every claim is correct.")

conversations = st.session_state.setdefault("conversations", {})
messages = conversations.setdefault(corpus, [])
selected_turns = st.session_state.setdefault("selected_turns", {})
with st.sidebar:
    st.subheader("Question history")
    if not messages:
        st.caption("Your questions will appear here.")
    for index in range(len(messages) - 2, -1, -2):
        if st.button(messages[index]["content"], key=f"history_{corpus}_{index}",
                     use_container_width=True, type="secondary"):
            selected_turns[corpus] = index



def render_result(result, turn):
    response = result["response"]
    if response["status"] == "answered":
        for number, claim in enumerate(response["claims"], 1):
            st.markdown(claim["text"])
            for evidence_number, evidence in enumerate(claim["evidence"], 1):
                source = result["chunks"][evidence["source_id"] - 1]
                meta = source["metadata"]
                with st.expander(f"Source {evidence['source_id']}: {meta['filename']} - {meta.get('locator', 'Document')}"):
                    st.text(evidence["quote"])
                    st.caption(f"Type: {meta.get('source_type', 'unverified')} | Published: {meta.get('publication_date', 'unknown')}")
                    st.text(source["text"])
                    if meta.get("source_type") == "verified_official_summary":
                        st.caption("Reviewed summary, not an original university document. Checked: " + meta.get("verified_at", "unknown"))
                        st.link_button("Open official source", meta["source_url"])
                    path = (DATA_DIR / meta.get("document_id", "")).resolve()
                    if path.is_relative_to(DATA_DIR.resolve()) and path.is_file() and path.suffix.lower() in (".pdf", ".docx"):
                        source_bytes = path.read_bytes()
                        if hashlib.sha256(source_bytes).hexdigest() == meta.get("content_hash"):
                            st.download_button("Download source", source_bytes, file_name=path.name,
                                key=f"download_{corpus}_{turn}_{number}_{evidence_number}")
                        else:
                            st.caption("The local document has changed since this answer was indexed. Re-index to download matching evidence.")
    else:
        st.write(response["message"])
    st.caption(f"Response time: {result['seconds']:.1f}s")


question = st.chat_input("Ask about requirements, courses, or a specific academic year", max_chars=1000)
# Render the submitted question before retrieval starts, with history in the sidebar.
if question:
    with st.chat_message("user"):
        st.write(question)
else:
    selected = selected_turns.get(corpus, max(0, len(messages) - 2))
    for index in range(selected, min(selected + 2, len(messages))):
        message = messages[index]
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.write(message["content"])
            else:
                render_result(message["result"], index)

if question:
    now = time.monotonic()
    recent = [timestamp for timestamp in st.session_state.get("requests", []) if now - timestamp < 60]
    if len(recent) >= 6:
        st.warning("Please wait a moment. This demo allows six questions per minute per session.")
    else:
        st.session_state["requests"] = recent + [now]
        context_end = selected_turns.get(corpus, max(0, len(messages) - 2)) + 2
        history = [{"role": m["role"], "content": m["content"]} for m in messages[:context_end][-6:]]
        with st.spinner("Finding evidence..."):
            try:
                result = ask(question, corpus=corpus, history=history)
            except RateLimitError:
                st.warning("The AI service has reached its rate limit. Please wait a minute and try again.")
            except Exception:
                logging.exception("QuackQuery request failed")
                st.error("The answer service is unavailable. Please try again shortly.")
            else:
                messages.extend([{"role": "user", "content": question},
                                 {"role": "assistant", "content": result["answer"], "result": result}])
                conversations[corpus] = messages[-20:]
                selected_turns[corpus] = max(0, len(conversations[corpus]) - 2)
                st.rerun()
