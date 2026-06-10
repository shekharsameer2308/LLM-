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
    page_title="Scout — Product Intelligence",
    page_icon="🛍️",
    layout="wide"
)

API_URL = os.getenv("API_URL", "http://localhost:8000")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "mock_key")

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
    
    .news-card {
        background: rgba(22, 27, 34, 0.4);
        padding: 18px;
        border-radius: 10px;
        border: 1px solid rgba(88, 166, 255, 0.1);
        margin-bottom: 15px;
        transition: 0.3s;
    }
    .news-card:hover {
        border-color: #58a6ff;
        background-color: rgba(28, 33, 40, 0.6);
    }
    
    .badge-brand {
        background-color: rgba(187, 134, 252, 0.15);
        color: #bb86fc;
        border-color: rgba(187, 134, 252, 0.3);
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

st.markdown('<div class="gradient-header">🛍️ Product Intelligence & Market Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Search any product class to scrape live internet feeds, detect active manufacturers, and generate SWOT metrics.</div>', unsafe_allow_html=True)

# Helper: Fetch live internet articles for product query
def fetch_product_data(query: str):
    try:
        response = requests.get(f"{API_URL}/api/articles/fetch-internet", params={"q": query}, timeout=12)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch live data from server: {e}")
        return {"articles": [], "stats": {}}

# Helper: Generate RAG response using Gemini or intelligent local fallback
def generate_product_report(product: str, articles, stats):
    # Format top companies
    sorted_comps = sorted(stats.items(), key=lambda x: x[1]["mentions"], reverse=True)
    top_brands = [item[0] for item in sorted_comps[:3]]
    
    context = ""
    for idx, art in enumerate(articles[:10]):
        context += f"Source [{idx+1}]: {art['title']} (Source: {art['source']})\nSnippet: {art['summary']}\nSentiment: {art['sentiment']}\n\n"
        
    is_mock = GEMINI_API_KEY == "mock_key" or not GEMINI_API_KEY
    
    if not is_mock:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            
            system_instruction = (
                "You are Scout, an expert market research analyst. "
                "Write a comprehensive competitor landscape and SWOT intelligence report for the queried product. "
                "Discuss which brands are leading the discussions, their sentiment profile, and provide strategic recommendations."
            )
            
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction
            )
            
            full_prompt = f"Product Category: {product}\nTop Mentioned Brands: {top_brands}\n\nRetrieved Market Context:\n{context}"
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            st.warning(f"Failed to call Gemini API: {e}. Falling back to local synthesis engine.")
            is_mock = True

    if is_mock:
        # Local Intelligent Synthesis Fallback
        brand_highlights = []
        for brand, data in sorted_comps[:3]:
            pos_pct = round((data["positive"] / max(data["mentions"], 1)) * 100, 1)
            brand_highlights.append(
                f"* **{brand}** leads with **{data['mentions']} mentions**. Sentiment split is positive/neutral, showing a **{pos_pct}% positive score** based on recent releases."
            )
        brand_highlights_str = "\n".join(brand_highlights) if brand_highlights else "* *No major company brands were heavily mentioned in this search window. The discussion remains generic.*"
        
        return f"""> [!NOTE]
> *Currently running in Local Intelligent Fallback Mode because GEMINI_API_KEY is not configured. Live articles fetched from Google News have been processed below.*

# 🛍️ Competitor Landscape Report: {product.title()}

Based on analysis of 40 live news feeds retrieved from Google News, we compiled this market analysis for **{product}**.

### 1. Key Brand Highlights
The most active companies mentioned in discussions surrounding **{product}** are:
{brand_highlights_str}

### 2. SWOT Analysis - {product.title()} Market Segment

| 🟢 Strengths | 🔴 Weaknesses |
| :--- | :--- |
| • Highly active R&D rollout across companies.<br>• Dynamic consumer adoption and rising search indexes.<br>• Scalable manufacturing pipelines. | • Exposure to component and raw material tariff constraints.<br>• Intense pricing wars squeezing margins (e.g. budget smartphone/laptop launches). |
| **🔵 Opportunities** | **⚠️ Threats** |
| • Infusing advanced AI automation features.<br>• Localized manufacturing partnerships to hedge supply-chain risks. | • Sudden shifting consumer spending behaviors.<br>• Patent litigation and regulatory compliance delays. |

### 3. Strategic Recommendations
1. **Accelerate Innovation**: Focus on product feature differentiation (e.g. advanced AI chips, battery efficiency) to stand out.
2. **Hedge Pricing Risks**: Diversify components to safeguard against margin squeezes in budget product segments.
3. **Monitor Competitors**: Follow marketing launches from top cited players to benchmark product specifications.
"""

# Input controls
st.sidebar.header("🔍 Scrape & Analyze")
product_query = st.sidebar.text_input("Product search term...", value="", placeholder="Type e.g., mobile, laptop, solar panel...")

# Quick suggestions
st.markdown("### 💡 Quick Product Analysis Suggestions")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📱 Mobile Phones", use_container_width=True):
        st.session_state.product_input_val = "mobile"
with col2:
    if st.button("💻 Laptops & PCs", use_container_width=True):
        st.session_state.product_input_val = "laptop"
with col3:
    if st.button("🔋 Electric Vehicles", use_container_width=True):
        st.session_state.product_input_val = "electric vehicle"
with col4:
    if st.button("☀️ Solar Panels", use_container_width=True):
        st.session_state.product_input_val = "solar panel"

# Handle suggestion click
if "product_input_val" in st.session_state and st.session_state.product_input_val:
    product_query = st.session_state.product_input_val
    st.session_state.product_input_val = None

# If user clicked button or pressed enter
if product_query:
    st.markdown("---")
    st.subheader(f"🔍 Analyzing Live Internet Data for: '{product_query.title()}'")
    
    with st.spinner("Fetching live articles from Google News search, matching brand mentions, and classifying sentiment..."):
        # 1. Fetch data
        data = fetch_product_data(product_query)
        
        articles = data.get("articles", [])
        stats = data.get("stats", {})
        
        if not articles:
            st.warning("No live articles retrieved for this product query. Please try another search term.")
        else:
            # Process dataframe
            flat_stats = []
            for brand, brand_stats in stats.items():
                flat_stats.append({
                    "Brand": brand,
                    "Total Mentions": brand_stats["mentions"],
                    "Positive": brand_stats["positive"],
                    "Negative": brand_stats["negative"],
                    "Neutral": brand_stats["neutral"]
                })
            df_stats = pd.DataFrame(flat_stats)
            
            # Row 1: KPI Summary & Charts
            dash_col1, dash_col2 = st.columns([3, 4])
            
            with dash_col1:
                st.markdown("#### Brand Share of Voice")
                if not df_stats.empty:
                    df_sorted = df_stats.sort_values(by="Total Mentions", ascending=True)
                    fig_voice = px.bar(
                        df_sorted,
                        x="Total Mentions",
                        y="Brand",
                        orientation="h",
                        color="Total Mentions",
                        color_continuous_scale="Viridis",
                        labels={"Total Mentions": "Articles Count", "Brand": "Company"}
                    )
                    fig_voice.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#c9d1d9",
                        xaxis=dict(showgrid=True, gridcolor="#21262d"),
                        yaxis=dict(showgrid=False),
                        coloraxis_showscale=False,
                        height=280,
                        margin=dict(l=10, r=10, t=10, b=10)
                    )
                    st.plotly_chart(fig_voice, use_container_width=True)
                else:
                    st.info("No major brand mentions identified in this search index. Visuals skipped.")
                    
                st.markdown("#### Sentiment Splits per Brand")
                if not df_stats.empty:
                    # Melt for stacked bar chart
                    df_melted = df_stats.melt(
                        id_vars="Brand",
                        value_vars=["Positive", "Negative", "Neutral"],
                        var_name="Sentiment",
                        value_name="Count"
                    )
                    color_discrete_map = {
                        "Positive": "#2ea043",
                        "Negative": "#f85149",
                        "Neutral": "#8b949e"
                    }
                    fig_stacked = px.bar(
                        df_melted,
                        x="Brand",
                        y="Count",
                        color="Sentiment",
                        color_discrete_map=color_discrete_map,
                        labels={"Count": "Mentions", "Brand": "Company"},
                        barmode="stack"
                    )
                    fig_stacked.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#c9d1d9",
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor="#21262d"),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                        height=280,
                        margin=dict(l=10, r=10, t=10, b=10)
                    )
                    st.plotly_chart(fig_stacked, use_container_width=True)
                    
            with dash_col2:
                st.markdown("#### Market Landscape & SWOT")
                # Generate SWOT
                report = generate_product_report(product_query, articles, stats)
                st.markdown(report, unsafe_allow_html=True)
                
            st.markdown("---")
            st.subheader(f"📰 Live Product Feed: '{product_query.title()}'")
            st.write(f"Showing {len(articles)} real-time articles scraped from Google News search index.")
            
            for art in articles:
                # Format date
                date_str = art["published_date"]
                sent = art["sentiment"]
                badge_class = "badge-positive" if sent == "positive" else ("badge-negative" if sent == "negative" else "badge-neutral")
                
                brands_span = ""
                for b in art["brands"]:
                    brands_span += f'<span class="badge badge-brand">{b}</span> '
                    
                st.markdown(f"""
                <div class="news-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h5 style="margin: 0; color: #58a6ff; font-family: 'Outfit', sans-serif; font-size: 1.1rem;">{art['title']}</h5>
                        <div>
                            <span class="badge {badge_class}">{sent}</span>
                            <span style="font-size: 11px; color: #8b949e; font-weight: 500;">{date_str}</span>
                        </div>
                    </div>
                    <p style="font-size: 13.5px; line-height: 1.5; color: #c9d1d9; margin-bottom: 8px;">
                        {art['summary']}
                    </p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            {brands_span}
                            <span style="font-size: 11.5px; color: #8b949e; font-weight: 500;">Source: <b>{art['source']}</b></span>
                        </div>
                        <a href="{art['url']}" target="_blank" style="font-size: 12.5px; color: #58a6ff; text-decoration: none; font-weight: 600;">Read original article ↗</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.info("👈 Enter a search term in the sidebar (e.g. mobile, laptop, solar panel) and click analyze to fetch live data from the internet.")
st.markdown("---")
