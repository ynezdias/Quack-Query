import hashlib
import math
import os
import logging
from groq import RateLimitError
import streamlit as st
from styles import STYLES
from presentation import brand_markup, hero_markup, EMPTY_MARKUP, FOOTER_MARKUP
from src.rag import ask
from src.knowledge import DATA_DIR
from src.runtime import request_limit, recent_requests, retry_after, service_error_message
import time

st.set_page_config(
    page_title="QuackQuery · Your campus, connected",
    page_icon="🦆",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(STYLES, unsafe_allow_html=True)


with st.sidebar:
    st.markdown(brand_markup(), unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">YOUR WORKSPACE</div>', unsafe_allow_html=True)
    corpus = st.selectbox("Knowledge base", [os.environ["QUACKQUERY_CORPUS"]] if os.getenv("QUACKQUERY_CORPUS") else ["synthetic", "unverified", "verified"],
        format_func=lambda x: {"synthetic": "Synthetic demo", "unverified": "Original documents (unverified)", "verified": "Reviewed university sources"}[x])
    st.info("Fictional test documents, not official university guidance." if corpus == "synthetic"
            else ("Selected factual summaries checked against official Stevens pages on 2026-09-17; follow the source link for the full document." if corpus == "verified" else "These documents have not been verified against official university sources."))
    st.caption("Conversations stay in this browser session. Each knowledge base has its own history.")
    if st.button("Clear conversation", icon=":material/refresh:", use_container_width=True):
        st.session_state.setdefault("conversations", {})[corpus] = []
        st.session_state.setdefault("selected_turns", {}).pop(corpus, None)
    st.caption("Citations are checked for valid sources and matching quotations. This does not guarantee that every claim is correct.")

conversations = st.session_state.setdefault("conversations", {})
messages = conversations.setdefault(corpus, [])
selected_turns = st.session_state.setdefault("selected_turns", {})
with st.sidebar:
    st.divider()
    st.markdown('<div class="sidebar-label">RECENT QUESTIONS</div>', unsafe_allow_html=True)
    if not messages:
        st.caption("A fresh page. Your questions will appear here as you explore.")
    for index in range(len(messages) - 2, -1, -2):
        if st.button(messages[index]["content"], key=f"history_{corpus}_{index}",
                     use_container_width=True, type="secondary"):
            selected_turns[corpus] = index



def render_result(result, turn):
    response = result["response"]
    if response["status"] == "answered":
        st.markdown('<div class="answer-label">YOUR ANSWER · WITH SOURCE EVIDENCE</div>', unsafe_allow_html=True)
        for number, claim in enumerate(response["claims"], 1):
            st.markdown(claim["text"])
            for evidence_number, evidence in enumerate(claim["evidence"], 1):
                source = result["chunks"][evidence["source_id"] - 1]
                meta = source["metadata"]
                with st.expander(f"Source {evidence['source_id']}: {meta['filename']} - {meta.get('locator', 'Document')}"):
                    st.caption("QUOTED EVIDENCE")
                    st.text(evidence["quote"])
                    st.caption(f"Type: {meta.get('source_type', 'unverified')} | Published: {meta.get('publication_date', 'unknown')}")
                    st.caption("SURROUNDING PASSAGE")
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
        status_label = {"unknown": "NO ANSWER IN THIS COLLECTION", "clarify": "ONE DETAIL BEFORE WE CONTINUE", "validation_failed": "EVIDENCE COULD NOT BE VERIFIED"}.get(response["status"], "RESPONSE")
        st.markdown(f'<div class="answer-label">{status_label}</div>', unsafe_allow_html=True)
        st.write(response["message"])
    timing = f"Response time: {result['seconds']:.1f}s"
    st.caption(timing + (" · Expand a source to inspect the evidence" if response["status"] == "answered" else ""))


st.markdown(hero_markup(corpus, compact=bool(messages)), unsafe_allow_html=True)
with st.container(key="composer"):
    typed_question = st.chat_input("Ask about admissions, tuition, or courses", max_chars=1000)
starter_question = None
with st.container(key="welcome"):
    if not messages:
        st.markdown(EMPTY_MARKUP, unsafe_allow_html=True)
        for column, (key, label, prompt, icon) in zip(st.columns(3), [
            ("admissions", "Explore admissions", "What are the graduate admission requirements?", ":material/school:"),
            ("tuition", "Understand tuition", "How does graduate tuition differ by academic year?", ":material/payments:"),
            ("courses", "Discover courses", "What information is available about CS 583?", ":material/menu_book:"),
        ]):
            with column:
                if st.button(label, key=f"starter_{key}", icon=icon, use_container_width=True, help=prompt):
                    starter_question = prompt
        st.caption("Choose a knowledge base in the sidebar. Answers reflect only that collection; dates and requirements can differ by year.")

question = typed_question or starter_question
with st.container(key="conversation"):
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
        recent = recent_requests(st.session_state.get("requests", []), now)
        st.session_state["requests"] = recent
        limit = request_limit()
        provider_wait = max(0, math.ceil(st.session_state.get("provider_retry_at", 0) - now))
        if provider_wait:
            st.warning(f"The AI provider is cooling down. Please try again in {provider_wait} seconds. Your conversation is preserved.")
        elif len(recent) >= limit:
            wait = max(1, math.ceil(60 - (now - min(recent))))
            st.warning(f"This session allows {limit} completed questions per minute. Please try again in {wait} seconds.")
        else:
            context_end = selected_turns.get(corpus, max(0, len(messages) - 2)) + 2
            history = [{"role": m["role"], "content": m["content"]} for m in messages[:context_end][-6:]]
            with st.spinner("Searching your documents and checking the evidence…"):
                try:
                    result = ask(question, corpus=corpus, history=history)
                except RateLimitError as exc:
                    wait = retry_after(exc)
                    st.session_state["provider_retry_at"] = time.monotonic() + wait
                    st.warning(f"The AI provider has reached its limit. Please retry in {wait} seconds. This failed request did not use your session allowance.")
                except Exception as exc:
                    logging.warning("QuackQuery request failed: %s", type(exc).__name__)
                    st.error(service_error_message(exc))
                else:
                    if result["response"]["status"] != "validation_failed":
                        finished = time.monotonic()
                        st.session_state["requests"] = recent_requests(recent, finished) + [finished]
                    st.session_state.pop("provider_retry_at", None)
                    messages.extend([{"role": "user", "content": question},
                                     {"role": "assistant", "content": result["answer"], "result": result}])
                    conversations[corpus] = messages[-20:]
                    selected_turns[corpus] = max(0, len(conversations[corpus]) - 2)
                    st.rerun()

st.markdown(FOOTER_MARKUP, unsafe_allow_html=True)
