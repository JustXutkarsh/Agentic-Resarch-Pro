import streamlit as st
import os
from dotenv import load_dotenv

from src.scraper import scrape_urls
from src.chunker import chunk_text
from src.embedder import OpenAIEmbedder
from src.chroma_store import get_vector_store, save_vectors, query_vectors
from src.summarizer import Summarizer

import requests
from fpdf import FPDF

load_dotenv()

st.set_page_config(
    page_title="Agentic Research PRO",
    layout="wide",
    page_icon="🤝"
)

# ============================================
#                STYLES
# ============================================
st.markdown("""
<style>
    body {
        background-color: #0d0d0d !important;
        color: #ffffff !important;
    }

    .big-title {
        font-size: 42px;
        font-weight: 900;
        color: white;
    }

    .subtitle {
        font-size: 18px;
        color: #aaaaaa;
        padding-bottom: 12px;
    }

    .agent-card {
        padding: 18px 20px;
        border-radius: 18px;
        margin-bottom: 14px;
        font-size: 17px;
        font-weight: 600;
        color: white;
        background: rgba(20,20,20,0.6);
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0px 0px 18px rgba(0,0,0,0.4);
    }

    .working {
        background: rgba(80, 50, 8, 0.4);
        border-left: 6px solid #ffb74d;
        box-shadow: 0px 0px 18px #ffb74daa;
    }

    .done {
        background: rgba(7, 60, 45, 0.45);
        border-left: 6px solid #00e676;
        box-shadow: 0px 0px 18px #00e676aa;
    }

    .stButton > button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 10px 18px !important;
        border: none !important;
    }

    .stButton > button:hover {
        transform: scale(1.02);
        opacity: 0.9;
    }

    .source-link {
        font-size: 15px;
        padding: 4px 0px;
    }

</style>
""", unsafe_allow_html=True)

# ============================================
#                HEADER
# ============================================
st.markdown('<div class="big-title">🤝 Agentic Research PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Multi-agent pipeline: search → scrape → chunk → embed → retrieve → write → export</div>', unsafe_allow_html=True)
st.markdown("---")

# ============================================
#              INPUT SECTION
# ============================================
col1, col2 = st.columns([2, 1])

with col1:
    topic = st.text_input("Enter a research topic")
with col2:
    depth = st.selectbox("Report Depth", ["Short", "Medium", "Long"])

run_btn = st.button("Run Agentic Research 🚀", use_container_width=True)

st.markdown("---")

# ============================================
#               UTILITY
# ============================================
def agent_status(name, status):
    if status == "working":
        st.markdown(f"<div class='agent-card working'>🟡 {name} — Working...</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='agent-card done'>🟢 {name} — Completed</div>", unsafe_allow_html=True)


# ============================================
#               PIPELINE EXECUTION
# ============================================
if run_btn:

    if not topic.strip():
        st.error("Enter a topic first")
        st.stop()

    st.subheader("🤖 Agent Pipeline Execution")

    # ------------------------------
    # 1. Web Search Agent
    # ------------------------------
    agent_status("Web Search Agent", "working")

    tavily_key = os.getenv("TAVILY_API_KEY")
    search_resp = requests.post(
        "https://api.tavily.com/search",
        json={"api_key": tavily_key, "query": topic, "max_results": 5},
        timeout=12
    ).json()

    urls = [r["url"] for r in search_resp.get("results", [])]

    agent_status("Web Search Agent", "done")

    # clickable links
    st.markdown("### Sources Found:")
    for u in urls:
        st.markdown(f"<div class='source-link'><a href='{u}' target='_blank'>{u}</a></div>", unsafe_allow_html=True)

    # ------------------------------
    # 2. Scraper Agent
    # ------------------------------
    agent_status("Scraper Agent", "working")
    scraped = scrape_urls(urls)
    agent_status("Scraper Agent", "done")

    st.write(f"Scraped {len(scraped)} articles")

    if len(scraped) == 0:
        st.error("No articles could be scraped. Try another topic.")
        st.stop()

    # ------------------------------
    # 3. Chunker Agent
    # ------------------------------
    agent_status("Chunker Agent", "working")
    chunks = []
    for t in scraped:
        chunks.extend(chunk_text(t))
    agent_status("Chunker Agent", "done")
    st.write(f"Chunk Count: {len(chunks)}")

    # ------------------------------
    # 4. Embedding Agent
    # ------------------------------
    agent_status("Embedding Agent", "working")
    embedder = OpenAIEmbedder()
    embeddings = embedder.embed(chunks)
    agent_status("Embedding Agent", "done")

    # ------------------------------
    # 5. Vector Store
    # ------------------------------
    agent_status("Vector Store Agent", "working")
    store = get_vector_store()
    save_vectors(store, embeddings, chunks)
    agent_status("Vector Store Agent", "done")

    # ------------------------------
    # 6. Retrieval Agent
    # ------------------------------
    agent_status("Retrieval Agent", "working")

    try:
        retrieved = query_vectors(store, topic, top_k=10)
        if (
            not retrieved
            or "documents" not in retrieved
            or len(retrieved["documents"]) == 0
        ):
            docs = chunks
        else:
            docs = retrieved["documents"][0]
    except:
        docs = chunks

    agent_status("Retrieval Agent", "done")

    # ------------------------------
    # 7. Writer Agent
    # ------------------------------
    agent_status("Writer Agent", "working")
    writer = Summarizer()
    report = writer.summarize(topic, docs, depth)
    agent_status("Writer Agent", "done")

    st.markdown("---")
    st.subheader("📄 Final Research Report")
    st.write(report)

    # ------------------------------
    # 8. PDF Export
    # ------------------------------
    agent_status("Export Agent", "working")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=11)

    for line in report.split("\n"):
        pdf.multi_cell(0, 7, line)

    pdf.output("research.pdf")

    agent_status("Export Agent", "done")

    with open("research.pdf", "rb") as f:
        st.download_button(
            "📥 Download Research PDF",
            f,
            file_name="research.pdf",
            use_container_width=True
        )
