import streamlit as st
import os

st.set_page_config(
    page_title="Scout — Market Intelligence Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (premium aesthetics)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .gradient-header {
        background: linear-gradient(135deg, #58a6ff 0%, #bb86fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #8b949e;
        font-size: 1.25rem;
        margin-bottom: 2.5rem;
    }
    
    .card {
        background: rgba(22, 27, 34, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid rgba(88, 166, 255, 0.15);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        min-height: 220px;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .card:hover {
        transform: translateY(-3px);
        border-color: #58a6ff;
        background-color: rgba(28, 33, 40, 0.8);
    }
    
    .card h3 {
        color: #58a6ff !important;
        font-family: 'Outfit', sans-serif;
        margin-top: 0;
        margin-bottom: 12px;
    }
    
    .card p {
        font-size: 14.5px;
        line-height: 1.6;
        color: #c9d1d9;
    }
    
    .card-nav {
        font-size: 13.5px;
        color: #bb86fc;
        font-weight: 600;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="gradient-header">🔍 Scout — Market Intelligence & Competitor Research</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your AI-powered assistant for monitoring industries, analyzing competitors, and semantic research.</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card">
        <h3>📊 Market Dashboard</h3>
        <p>Monitor industry trends, keyword frequencies, and sentiment over time. Get a real-time overview of current market activity.</p>
        <div class="card-nav">👈 Select <b>1 Dashboard</b> in the sidebar to view sentiment analytics.</div>
    </div>
    <div class="card">
        <h3>🧭 Market Explorer</h3>
        <p>Explore gathered news articles by industry, read AI-generated summaries, track trending topics, and query articles using dynamic filters.</p>
        <div class="card-nav">👈 Select <b>2 Market Explorer</b> in the sidebar to search and explore articles.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h3>🤖 AI Analyst</h3>
        <p>Ask complex research questions and let Scout generate comprehensive, structured reports backed by real citations from the article database.</p>
        <div class="card-nav">👈 Select <b>3 AI Analyst</b> in the sidebar to chat with Scout.</div>
    </div>
    <div class="card">
        <h3>⚔️ Competitor Intelligence</h3>
        <p>Compare competitors' mention volume and sentiment trends side by side, and view automated SWOT analyses.</p>
        <div class="card-nav">👈 Select <b>4 Competitor Intelligence</b> in the sidebar to begin research.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="card" style="min-height: auto; margin-bottom: 20px;">
    <h3>🛍️ Product Intelligence & Market Analysis</h3>
    <p>Search any custom product class (e.g. mobile, laptop, solar panel) to fetch live internet feeds, identify active competitor manufacturers, and compile dynamic SWOT reports.</p>
    <div class="card-nav">👈 Select <b>5 Product Analysis</b> in the sidebar to scrape and analyze products.</div>
</div>
<div class="card" style="min-height: auto;">
    <h3>Project Ingestion Pipeline</h3>
    <p>Search and ingest live articles on any custom topic or project directly into the Scout database and vector index, running the full NLP pipeline automatically.</p>
    <div class="card-nav">👈 Select <b>6 Project Ingestion</b> in the sidebar to ingest and analyze new data.</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.success("Select a page above to start.")
st.sidebar.markdown("""
---
### System Status
* **Database:** Connected 🟢
* **Vector Store (Qdrant):** Connected 🟢
* **AI Model (Gemini):** Ready 🟢
""")
