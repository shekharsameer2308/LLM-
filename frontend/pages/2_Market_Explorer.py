import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Scout — Market Explorer",
    page_icon="🧭",
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
    
    .subtitle {
        color: #8b949e;
        font-size: 1.1rem;
        margin-bottom: 2rem;
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
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        border-color: #58a6ff;
        background-color: rgba(28, 33, 40, 0.8);
    }
    
    .meta-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-industry {
        background-color: rgba(88, 166, 255, 0.15);
        color: #58a6ff;
        border-color: rgba(88, 166, 255, 0.3);
    }
    .badge-topic {
        background-color: rgba(187, 134, 252, 0.15);
        color: #bb86fc;
        border-color: rgba(187, 134, 252, 0.3);
    }
    .badge-source {
        background-color: rgba(139, 148, 158, 0.15);
        color: #8b949e;
        border-color: rgba(139, 148, 158, 0.3);
    }
    
    .read-link {
        font-size: 13px;
        color: #58a6ff;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.2s ease;
    }
    .read-link:hover {
        color: #bb86fc;
        text-decoration: underline;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to query APIs
@st.cache_data(ttl=60)
def fetch_topics():
    try:
        response = requests.get(f"{API_URL}/api/analytics/topics?limit=20", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception:
        return []

@st.cache_data(ttl=60)
def fetch_topic_velocity():
    try:
        response = requests.get(f"{API_URL}/api/analytics/topics/velocity?days=7", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception:
        return []

def fetch_articles(search="", industry="", topic=""):
    params = {"limit": 50}
    if search:
        params["search"] = search
    if industry and industry != "All":
        params["industry"] = industry
    if topic and topic != "All":
        params["topic"] = topic
        
    try:
        response = requests.get(f"{API_URL}/api/articles", params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching articles: {e}")
        return []

# Header block
st.markdown('<div class="gradient-header">🧭 Market Explorer & Trend Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Analyze dynamic topic clusters, track growth velocity, and search key intelligence.</div>', unsafe_allow_html=True)

# Setup Sidebar Filters
st.sidebar.header("🔍 Filter & Search")
search_query = st.sidebar.text_input("Search articles...", placeholder="Type keywords, e.g. AI, solar, drone...")

industries = ["All", "logistics", "pharma", "agriculture", "defense"]
industry_filter = st.sidebar.selectbox("Filter by Industry", industries)

# Load topics dynamically for filter dropdown
topic_list = ["All"]
db_topics = fetch_topics()
for t in db_topics:
    topic_list.append(t["topic_name"])
topic_filter = st.sidebar.selectbox("Filter by Topic Cluster", topic_list)

# Main dashboard columns
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📈 Topic Growth Velocity (Last 7 Days)")
    st.markdown("Metrics comparing mention frequency shifts in the **last 7 days** vs the **previous 7 days**.")
    
    velocity_data = fetch_topic_velocity()
    if velocity_data:
        df_vel = pd.DataFrame(velocity_data)
        
        # Color coding helper
        def style_velocity(val):
            color = '#2ea043' if val > 0 else ('#f85149' if val < 0 else '#8b949e')
            return f'color: {color}; font-weight: bold;'
            
        df_disp = df_vel.rename(columns={
            "topic_name": "Topic Name",
            "current_count": "Current Count (7d)",
            "previous_count": "Previous Count (7d)",
            "velocity_pct": "Velocity %"
        })
        
        # Display with color styling
        st.dataframe(
            df_disp.style.map(style_velocity, subset=["Velocity %"]),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No topic velocity data available. Make sure to run the topic modeling batch job.")

with col2:
    st.subheader("📊 Top Topic Frequency")
    if db_topics:
        df_topics = pd.DataFrame(db_topics)
        fig_topics = px.bar(
            df_topics.head(10),
            x="frequency",
            y="topic_name",
            orientation="h",
            color="frequency",
            color_continuous_scale="Purples",
            labels={"frequency": "Article Count", "topic_name": "Topic Name"}
        )
        fig_topics.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#c9d1d9",
            xaxis=dict(showgrid=True, gridcolor="#21262d"),
            yaxis=dict(showgrid=False),
            coloraxis_showscale=False,
            height=320,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_topics, use_container_width=True)
    else:
        st.info("No topic clusters generated yet.")

st.markdown("---")
st.subheader("📰 Article Intelligence Feed")

articles = fetch_articles(search=search_query, industry=industry_filter, topic=topic_filter)

if articles:
    st.write(f"Showing {len(articles)} matching articles.")
    for art in articles:
        pub_dt = datetime.fromisoformat(art["published_date"].replace("Z", "+00:00"))
        date_str = pub_dt.strftime("%B %d, %Y")
        
        st.markdown(f"""
        <div class="card">
            <h4 style="margin: 0 0 10px 0; color: #58a6ff; font-family: 'Outfit', sans-serif; font-size: 1.25rem;">{art['title']}</h4>
            <div style="margin-bottom: 15px;">
                <span class="meta-badge badge-industry">{art['industry']}</span>
                <span class="meta-badge badge-topic">{art['topic_name'] if art['topic_name'] else 'Unassigned'}</span>
                <span class="meta-badge badge-source">{art['source']}</span>
                <span style="font-size: 12px; color: #8b949e; margin-left: 10px; font-weight: 500;">{date_str}</span>
            </div>
            <p style="font-size: 14.5px; line-height: 1.6; color: #c9d1d9; margin-bottom: 12px;">{art['summary']}</p>
            <a href="{art['url']}" target="_blank" class="read-link">Read original article ↗</a>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No articles found matching the current search criteria or filters.")
 st.markdown("---")
