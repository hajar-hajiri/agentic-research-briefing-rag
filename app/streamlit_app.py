import streamlit as st
from core.engine import Engine

st.set_page_config(page_title="Agentic Research Briefing RAG", layout="wide")
st.title("Agentic Research & Briefing Copilot (Compact Core)")

engine = Engine()

topic = st.text_input("Topic", placeholder="e.g., agentic AI trends for enterprise product teams")
mode = st.selectbox("Mode", ["offline", "online"], index=0)
urls = st.text_area("Seed URLs (optional, one per line)", height=120).strip().splitlines()
urls = [u.strip() for u in urls if u.strip()]

col1, col2 = st.columns([2, 1])

if st.button("Generate briefing", type="primary", disabled=not topic.strip()):
    run = engine.run(topic.strip(), mode=mode, urls=urls or None)

    with col1:
        st.markdown(run.answer)

    with col2:
        st.subheader("Run artifacts")
        st.write(f"Trace: {run.trace_path}")
        st.write(f"Retrieved chunks: {len(run.retrieved)}")
        st.write(f"Distinct sources: {len({c.source for c in run.retrieved})}")
