import streamlit as st
import plotly.express as px
import requests
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Scout - Project Ingestion",
    page_icon="🔍",
    layout="wide"
)

API_URL = os.getenv("API_URL", "http://localhost:8000")

# Premium styling (no emojis, professional, clean layout)
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
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #8b949e;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .kpi-container {
        display: flex;
        gap: 15px;
        margin-bottom: 25px;
    }
    
    .kpi-card {
        flex: 1;
        background: rgba(22, 27, 34, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(88, 166, 255, 0.15);
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
    
    .kpi-val {
        font-family: 'Outfit', sans-serif;
        font-size: 32px;
        font-weight: 700;
        color: #58a6ff;
    }
    
    .kpi-lbl {
        font-size: 12px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
        margin-top: 5px;
    }
    
    .article-card {
        background: rgba(22, 27, 34, 0.4);
        padding: 18px;
        border-radius: 10px;
        border: 1px solid rgba(88, 166, 255, 0.1);
        margin-bottom: 15px;
        transition: 0.3s;
    }
    .article-card:hover {
        border-color: #58a6ff;
        background-color: rgba(28, 33, 40, 0.6);
    }
    
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        border: 1px solid transparent;
        margin-right: 5px;
    }
    
    .badge-industry {
        background-color: rgba(187, 134, 252, 0.15);
        color: #bb86fc;
        border-color: rgba(187, 134, 252, 0.3);
    }
    
    .badge-keyword {
        background-color: rgba(88, 166, 255, 0.1);
        color: #58a6ff;
        border-color: rgba(88, 166, 255, 0.2);
    }
    
    .badge-positive {
        background-color: rgba(46, 160, 67, 0.15);
        color: #2ea043;
        border-color: rgba(46, 160, 67, 0.3);
    }
    .badge-negative {
        background-color: rgba(248, 81, 73, 0.15);
        color: #f85149;
        border-color: rgba(248, 81, 73, 0.3);
    }
    .badge-neutral {
        background-color: rgba(139, 148, 158, 0.15);
        color: #8b949e;
        border-color: rgba(139, 148, 158, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="gradient-header">Project and Keyword Ingestion Pipeline</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Search and ingest live articles on any topic or project directly into the Scout database and vector index.</div>', unsafe_allow_html=True)

# Main container for controls
st.markdown("### Ingest a New Project")
col_input, col_btn = st.columns([4, 1])

with col_input:
    query = st.text_input(
        "Enter Project Keywords or Topic...",
        placeholder="Type e.g., solid state battery, generative AI regulation, hyperloop...",
        label_visibility="collapsed"
    )

with col_btn:
    submit_btn = st.button("Start Ingestion", use_container_width=True)

# Quick suggestion list (professional topics)
st.markdown("#### Suggested Topics to Ingest")
sug_col1, sug_col2, sug_col3, sug_col4 = st.columns(4)
with sug_col1:
    if st.button("Solid State Battery", use_container_width=True):
        st.session_state.ingest_query_val = "solid state battery"
with sug_col2:
    if st.button("Generative AI Regulation", use_container_width=True):
        st.session_state.ingest_query_val = "generative AI regulation"
with sug_col3:
    if st.button("Hydrogen Fuel Cells", use_container_width=True):
        st.session_state.ingest_query_val = "hydrogen fuel cells"
with sug_col4:
    if st.button("Commercial Spaceflight", use_container_width=True):
        st.session_state.ingest_query_val = "commercial spaceflight"

if "ingest_query_val" in st.session_state and st.session_state.ingest_query_val:
    query = st.session_state.ingest_query_val
    st.session_state.ingest_query_val = None
    st.rerun()

if submit_btn and query:
    st.markdown("---")
    st.subheader(f"Ingesting and Analyzing Articles for: '{query}'")
    
    with st.spinner("Executing ingestion pipeline: parsing Google News RSS feed, downloading full content, classifying industry, computing FinBERT sentiment, extracting KeyBERT keywords, and indexing into Qdrant..."):
        try:
            response = requests.post(f"{API_URL}/api/articles/ingest-keyword", params={"q": query}, timeout=90)
            response.raise_for_status()
            res_data = response.json()
            
            stats = res_data.get("stats", {})
            articles = res_data.get("articles", [])
            
            # Display KPIs
            st.markdown(f"""
                <div class="kpi-container">
                    <div class="kpi-card">
                        <div class="kpi-val">{stats.get('total_fetched', 0)}</div>
                        <div class="kpi-lbl">Total Fetched</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-val" style="color: #2ea043;">{stats.get('new_ingested', 0)}</div>
                        <div class="kpi-lbl">Newly Ingested</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-val" style="color: #8b949e;">{stats.get('duplicates_skipped', 0)}</div>
                        <div class="kpi-lbl">Duplicates Skipped</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-val" style="color: #f85149;">{stats.get('errors', 0)}</div>
                        <div class="kpi-lbl">Errors Encountered</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if not articles:
                if stats.get('duplicates_skipped', 0) > 0:
                    st.info("All fetched articles are already present in the database. No new records were added.")
                else:
                    st.warning("No articles could be retrieved for this search query. Please try different keywords.")
            else:
                st.success(f"Successfully processed and stored {len(articles)} new articles in the database!")
                
                # Visualizations
                vis_col1, vis_col2 = st.columns([1, 1])
                
                df_articles = pd.DataFrame(articles)
                
                with vis_col1:
                    st.markdown("#### Sentiment Distribution")
                    sentiment_counts = df_articles['sentiment'].value_counts().reset_index()
                    sentiment_counts.columns = ['Sentiment', 'Count']
                    
                    color_discrete_map = {
                        "positive": "#2ea043",
                        "negative": "#f85149",
                        "neutral": "#8b949e"
                    }
                    
                    fig_pie = px.pie(
                        sentiment_counts,
                        values='Count',
                        names='Sentiment',
                        color='Sentiment',
                        color_discrete_map=color_discrete_map,
                        hole=0.4
                    )
                    fig_pie.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#c9d1d9",
                        height=300,
                        margin=dict(l=10, r=10, t=10, b=10)
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                with vis_col2:
                    st.markdown("#### Industry Classifications")
                    ind_counts = df_articles['industry'].value_counts().reset_index()
                    ind_counts.columns = ['Industry', 'Count']
                    
                    fig_bar = px.bar(
                        ind_counts,
                        x='Count',
                        y='Industry',
                        orientation='h',
                        color='Count',
                        color_continuous_scale="Viridis",
                    )
                    fig_bar.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#c9d1d9",
                        xaxis=dict(showgrid=True, gridcolor="#21262d"),
                        yaxis=dict(showgrid=False),
                        coloraxis_showscale=False,
                        height=300,
                        margin=dict(l=10, r=10, t=10, b=10)
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                    
                # Ingested List
                st.markdown("---")
                st.markdown("### Newly Ingested Articles")
                
                for art in articles:
                    sent = art["sentiment"]
                    badge_class = "badge-positive" if sent == "positive" else ("badge-negative" if sent == "negative" else "badge-neutral")
                    
                    kws_span = ""
                    for kw in art["keywords"]:
                        kws_span += f'<span class="badge badge-keyword">{kw}</span>'
                        
                    st.markdown(f"""
                        <div class="article-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <h5 style="margin: 0; color: #58a6ff; font-family: 'Outfit', sans-serif; font-size: 1.1rem;">{art['title']}</h5>
                                <div>
                                    <span class="badge {badge_class}">{sent}</span>
                                    <span class="badge badge-industry">{art['industry']}</span>
                                </div>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">
                                <div>
                                    {kws_span}
                                    <span style="font-size: 11.5px; color: #8b949e; margin-left: 10px;">Source: <b>{art['source']}</b></span>
                                </div>
                                <a href="{art['url']}" target="_blank" style="font-size: 12.5px; color: #58a6ff; text-decoration: none; font-weight: 600;">Read Original ↗</a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown("---")
                st.info("The newly ingested articles are now indexed in the Qdrant vector store and relational database. You can head over to the **AI Analyst** page and ask questions about this project!")
                
        except Exception as e:
            st.error(f"Failed to execute ingestion pipeline: {e}")
elif submit_btn and not query:
    st.warning("Please enter a valid search term.")
