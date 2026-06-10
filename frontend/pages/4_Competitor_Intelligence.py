import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Scout — Competitor Intelligence",
    page_icon="⚔️",
    layout="wide"
)

API_URL = os.getenv("API_URL", "http://localhost:8000")

# Premium styling
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
    
    .kpi-card {
        background: rgba(22, 27, 34, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(88, 166, 255, 0.15);
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        margin-bottom: 15px;
    }
    .kpi-val {
        font-family: 'Outfit', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: #58a6ff;
    }
    .kpi-lbl {
        font-size: 12px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
    }
    
    .swot-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        margin-top: 15px;
    }
    
    .swot-box {
        background: rgba(22, 27, 34, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 18px;
    }
    
    .swot-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 16px;
        margin-bottom: 10px;
    }
    
    .mention-card {
        background: rgba(22, 27, 34, 0.4);
        padding: 18px;
        border-radius: 10px;
        border: 1px solid rgba(88, 166, 255, 0.1);
        margin-bottom: 15px;
    }
    
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        border: 1px solid transparent;
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

st.markdown('<div class="gradient-header">⚔️ Competitor Intelligence Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Analyze competitor brand presence, sentiment splits, and comparative SWOT analytics.</div>', unsafe_allow_html=True)

# Helper: Fetch summaries of all competitors
@st.cache_data(ttl=60)
def fetch_competitor_summaries():
    try:
        response = requests.get(f"{API_URL}/api/analytics/competitors", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching competitor summaries: {e}")
        return []

# Helper: Fetch details for a specific competitor
def fetch_competitor_mentions(company_name: str):
    try:
        response = requests.get(f"{API_URL}/api/analytics/competitors/{company_name}", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching competitor mentions: {e}")
        return []

# Load overall competitors
comp_data = fetch_competitor_summaries()

if not comp_data:
    st.info("No competitor mention data available. Make sure to run the ingestion pipeline to parse competitor mentions.")
else:
    df_comp = pd.DataFrame(comp_data)
    
    # Left column: Comparative analysis, Right column: Deep-dive
    col1, col2 = st.columns([3, 4])
    
    with col1:
        st.subheader("📊 Competitor Share of Voice")
        st.markdown("Comparison of total mention counts across all companies on the watchlist.")
        
        fig_bar = px.bar(
            df_comp,
            x="total_mentions",
            y="company_name",
            orientation="h",
            color="total_mentions",
            color_continuous_scale="Tealgrn",
            labels={"total_mentions": "Mention Count", "company_name": "Company"}
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#c9d1d9",
            xaxis=dict(showgrid=True, gridcolor="#21262d"),
            yaxis=dict(showgrid=False),
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("---")
        st.subheader("⚔️ Side-by-Side Comparison")
        
        # Select two competitors for quick comparison table
        comp_list = df_comp["company_name"].tolist()
        comp_a = st.selectbox("Select Competitor A", comp_list, index=0)
        comp_b = st.selectbox("Select Competitor B", comp_list, index=min(1, len(comp_list)-1))
        
        row_a = df_comp[df_comp["company_name"] == comp_a].iloc[0]
        row_b = df_comp[df_comp["company_name"] == comp_b].iloc[0]
        
        # Build comparative table
        compare_dict = {
            "Metric": ["Total Mentions", "Positive Mentions", "Negative Mentions", "Neutral Mentions"],
            comp_a: [
                row_a["total_mentions"],
                row_a["sentiment_breakdown"].get("positive", 0),
                row_a["sentiment_breakdown"].get("negative", 0),
                row_a["sentiment_breakdown"].get("neutral", 0)
            ],
            comp_b: [
                row_b["total_mentions"],
                row_b["sentiment_breakdown"].get("positive", 0),
                row_b["sentiment_breakdown"].get("negative", 0),
                row_b["sentiment_breakdown"].get("neutral", 0)
            ]
        }
        df_compare = pd.DataFrame(compare_dict)
        st.dataframe(df_compare, use_container_width=True, hide_index=True)
        
    with col2:
        st.subheader("🔍 Competitor Profile Deep-Dive")
        
        # Deep-dive Selector
        target_company = st.selectbox("Select Target Company", comp_list, index=0)
        target_row = df_comp[df_comp["company_name"] == target_company].iloc[0]
        
        # Calculate Primary Industry
        ind_breakdown = target_row["industry_breakdown"]
        primary_ind = max(ind_breakdown, key=ind_breakdown.get) if ind_breakdown else "N/A"
        
        # KPI metrics
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        with kpi_col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val">{target_row['total_mentions']}</div>
                <div class="kpi-lbl">Total Mentions</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi_col2:
            sent_breakdown = target_row["sentiment_breakdown"]
            pos_pct = round((sent_breakdown.get("positive", 0) / max(target_row["total_mentions"], 1)) * 100, 1)
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val" style="color: #2ea043;">{pos_pct}%</div>
                <div class="kpi-lbl">Positive Ratio</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi_col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val" style="color: #bb86fc; font-size: 20px; padding: 5px 0;">{primary_ind.title()}</div>
                <div class="kpi-lbl">Primary Sector</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Sentiment Chart
        st.markdown("#### Sentiment Distribution")
        sent_labels = list(sent_breakdown.keys())
        sent_values = list(sent_breakdown.values())
        
        if sent_values:
            color_map = {
                "positive": "#2ea043",
                "negative": "#f85149",
                "neutral": "#8b949e"
            }
            fig_donut = px.pie(
                names=sent_labels,
                values=sent_values,
                color=sent_labels,
                color_discrete_map=color_map,
                hole=0.5
            )
            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#c9d1d9",
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
                height=260,
                margin=dict(t=10, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No sentiment metrics generated for this competitor.")
            
        # SWOT grid
        st.markdown("#### SWOT Intelligence")
        st.markdown(f"""
        <div class="swot-grid">
            <div class="swot-box" style="border-color: rgba(46, 160, 67, 0.25);">
                <div class="swot-title" style="color: #2ea043;">🟢 Strengths</div>
                <div style="font-size: 13px; color: #c9d1d9; line-height: 1.5;">
                    • High frequency mentions in key sectors.<br>
                    • Active technological rollouts and operational scaling.<br>
                    • Resilient corporate presence.
                </div>
            </div>
            <div class="swot-box" style="border-color: rgba(248, 81, 73, 0.25);">
                <div class="swot-title" style="color: #f85149;">🔴 Weaknesses</div>
                <div style="font-size: 13px; color: #c9d1d9; line-height: 1.5;">
                    • Subject to high public debate and media scrutiny.<br>
                    • Supply vulnerabilities and regional dependency.
                </div>
            </div>
            <div class="swot-box" style="border-color: rgba(88, 166, 255, 0.25);">
                <div class="swot-title" style="color: #58a6ff;">🔵 Opportunities</div>
                <div style="font-size: 13px; color: #c9d1d9; line-height: 1.5;">
                    • Emerging automation integration.<br>
                    • Capitalize on green transition demands in primary markets.
                </div>
            </div>
            <div class="swot-box" style="border-color: rgba(139, 148, 158, 0.25);">
                <div class="swot-title" style="color: #8b949e;">⚠️ Threats</div>
                <div style="font-size: 13px; color: #c9d1d9; line-height: 1.5;">
                    • Regulatory compliance adjustments.<br>
                    • Competitor price reductions and market saturation.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader(f"⚔️ Mention Ingestion Feed for {target_company}")
    
    mentions = fetch_competitor_mentions(target_company)
    
    if not mentions:
        st.info("No detailed mention occurrences found.")
    else:
        st.write(f"Displaying {len(mentions)} mention events.")
        for m in mentions:
            pub_dt = datetime.fromisoformat(m["published_date"].replace("Z", "+00:00"))
            date_str = pub_dt.strftime("%B %d, %Y")
            
            sent = m["sentiment"]
            badge_class = "badge-positive" if sent == "positive" else ("badge-negative" if sent == "negative" else "badge-neutral")
            
            st.markdown(f"""
            <div class="mention-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h5 style="margin: 0; color: #58a6ff; font-family: 'Outfit', sans-serif; font-size: 1.1rem;">{m['article_title']}</h5>
                    <div>
                        <span class="badge {badge_class}">{sent}</span>
                        <span style="font-size: 11px; color: #8b949e; margin-left: 10px; font-weight: 500;">{date_str}</span>
                    </div>
                </div>
                <p style="font-size: 13.5px; font-style: italic; color: #c9d1d9; border-left: 3px solid #30363d; padding-left: 10px; margin-bottom: 10px;">
                    "...{m['context_snippet']}..."
                </p>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 11.5px; color: #8b949e; font-weight: 500;">Mentions in article: <b>{m['mention_count']}</b></span>
                    <a href="{m['article_url']}" target="_blank" style="font-size: 12.5px; color: #58a6ff; text-decoration: none; font-weight: 600;">View source ↗</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
st.markdown("---")
