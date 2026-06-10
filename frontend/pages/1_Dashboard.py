import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Scout — Dashboard",
    page_icon="📊",
    layout="wide"
)

API_URL = os.getenv("API_URL", "http://localhost:8000")

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
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
    }
    
    .kpi-card {
        background: rgba(22, 27, 34, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid rgba(88, 166, 255, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        text-align: center;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
    }
    .kpi-val {
        font-family: 'Outfit', sans-serif;
        font-size: 36px;
        font-weight: 800;
        color: #58a6ff;
        margin-bottom: 5px;
    }
    .kpi-lbl {
        font-size: 13px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    
    /* Subtitle styling */
    .subtitle {
        color: #8b949e;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Cache data calls for 5 minutes (300 seconds)
@st.cache_data(ttl=300)
def fetch_sentiment_summary():
    response = requests.get(f"{API_URL}/api/analytics/sentiment", timeout=5)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=300)
def fetch_sentiment_trend():
    response = requests.get(f"{API_URL}/api/analytics/sentiment-trend?days=30", timeout=5)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=300)
def fetch_keywords():
    response = requests.get(f"{API_URL}/api/analytics/keywords?days=7", timeout=5)
    response.raise_for_status()
    return response.json()

# Header block
st.markdown('<div class="gradient-header">📊 Market Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Overview of macro-market trends, public sentiment shifts, and emerging industry keywords.</div>', unsafe_allow_html=True)

try:
    # 1. Fetch data
    sentiment_data = fetch_sentiment_summary()
    trend_data = fetch_sentiment_trend()
    keyword_data = fetch_keywords()
    
    # 2. Process data for KPI Cards
    sent_dict = {item["sentiment"]: item for item in sentiment_data}
    total_articles = sum(item["count"] for item in sentiment_data)
    
    pos_pct = sent_dict.get("positive", {}).get("percentage", 0.0) if "positive" in sent_dict else 0.0
    neg_pct = sent_dict.get("negative", {}).get("percentage", 0.0) if "negative" in sent_dict else 0.0
    
    # Row 1: KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-val">{total_articles}</div>
            <div class="kpi-lbl">Total Articles</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-val">4</div>
            <div class="kpi-lbl">Industries Tracked</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="kpi-card" style="border-color: rgba(46, 160, 67, 0.3);">
            <div class="kpi-val" style="color: #2ea043;">{pos_pct:.1f}%</div>
            <div class="kpi-lbl">Positive Sentiment</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="kpi-card" style="border-color: rgba(248, 81, 73, 0.3);">
            <div class="kpi-val" style="color: #f85149;">{neg_pct:.1f}%</div>
            <div class="kpi-lbl">Negative Sentiment</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 2: Two charts side by side
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("### 📊 Sentiment Distribution")
        df_pie = pd.DataFrame(sentiment_data)
        
        color_map = {
            "positive": "#2ea043",
            "negative": "#f85149",
            "neutral": "#8b949e"
        }
        
        fig_pie = px.pie(
            df_pie, 
            values="count", 
            names="sentiment", 
            color="sentiment",
            color_discrete_map=color_map,
            hole=0.45
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#c9d1d9",
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            margin=dict(t=10, b=10, l=10, r=10)
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with chart_col2:
        st.markdown("### 📈 Sentiment Over Time (30 Days)")
        df_trend = pd.DataFrame(trend_data)
        
        if not df_trend.empty:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=df_trend["date"], y=df_trend["positive"], 
                mode="lines+markers", name="Positive", 
                line=dict(color="#2ea043", width=3),
                marker=dict(size=6)
            ))
            fig_line.add_trace(go.Scatter(
                x=df_trend["date"], y=df_trend["negative"], 
                mode="lines+markers", name="Negative", 
                line=dict(color="#f85149", width=3),
                marker=dict(size=6)
            ))
            fig_line.add_trace(go.Scatter(
                x=df_trend["date"], y=df_trend["neutral"], 
                mode="lines+markers", name="Neutral", 
                line=dict(color="#8b949e", width=2),
                marker=dict(size=4)
            ))
            
            fig_line.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#c9d1d9",
                xaxis=dict(showgrid=True, gridcolor="#21262d", title="Date"),
                yaxis=dict(showgrid=True, gridcolor="#21262d", title="Article Count"),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=10, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No time series sentiment data available yet.")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 3: Top 10 keywords
    st.markdown("### 🔥 Top Trending Keywords (Last 7 Days)")
    df_kw = pd.DataFrame(keyword_data)
    
    if not df_kw.empty:
        df_kw_top10 = df_kw.head(10).iloc[::-1]
        
        fig_bar = px.bar(
            df_kw_top10,
            x="score",
            y="keyword",
            orientation="h",
            labels={"score": "Importance Score", "keyword": "Keyword"},
            color="score",
            color_continuous_scale="magma"
        )
        
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#c9d1d9",
            xaxis=dict(showgrid=True, gridcolor="#21262d"),
            yaxis=dict(showgrid=False),
            coloraxis_showscale=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=380
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No trending keyword data available yet.")
        
except Exception as e:
    st.error("⚠️ Unable to connect to the Scout API backend server.")
    st.info("Please make sure the FastAPI backend is running at http://localhost:8000.")
    st.exception(e)

st.markdown("---")
