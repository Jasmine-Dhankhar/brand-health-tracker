import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from collections import Counter
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------ CONFIG ------------------
st.set_page_config(layout="wide", page_title="Brand Health Tracker")
st.title("🏷️ Brand Health Tracker")
st.caption("Consumer sentiment and brand perception — powered by YouTube, News, and AI")

# ------------------ BRAND LIST ------------------
BRANDS = {
    "🌍 Global Luxury": [
        "Dior Sauvage",
        "Creed Aventus",
        "YSL Black Opium"
    ],
    "🇮🇳 Indian Premium": [
        "Skinn by Titan",
        "Bella Vita Perfume"
    ],
    "🇮🇳 Indian Mass Market": [
        "Engage Perfume",
        "Fogg Perfume"
    ]
}

all_brands = []
for tier, brands in BRANDS.items():
    all_brands.extend(brands)

# ------------------ SESSION STATE INIT ------------------
if "primary_df" not in st.session_state:
    st.session_state.primary_df = pd.DataFrame()
if "competitor_df" not in st.session_state:
    st.session_state.competitor_df = pd.DataFrame()
if "primary_brand" not in st.session_state:
    st.session_state.primary_brand = None
if "competitor_brand" not in st.session_state:
    st.session_state.competitor_brand = None
if "audit_result" not in st.session_state:
    st.session_state.audit_result = None

# ------------------ SIDEBAR ------------------
# ------------------ SIDEBAR ------------------
st.sidebar.header("🔍 Brand Selection")

primary_brand = st.sidebar.selectbox(
    "Select primary brand",
    options=all_brands,
    index=0
)

competitor_brand = st.sidebar.selectbox(
    "Select competitor brand (optional)",
    options=["None"] + all_brands,
    index=0
)

analyse_button = st.sidebar.button("🔍 Analyse Brand", type="primary")

st.sidebar.markdown("---")
st.sidebar.caption(
    "📌 Data Source: 6,500 real YouTube comments and news articles "
    "collected via YouTube Data API and NewsAPI. "
    "Sentiment analysed using VADER NLP. "
    "Data collected: June 2026."
)

# ------------------ HELPER FUNCTIONS ------------------
def get_sentiment_counts(df):
    counts = df["sentiment"].value_counts()
    positive = counts.get("positive", 0)
    negative = counts.get("negative", 0)
    neutral = counts.get("neutral", 0)
    total = len(df)
    return positive, negative, neutral, total

def get_top_keywords(df, sentiment_filter="positive", top_n=20):
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "this", "is", "it", "i", "my", "me",
        "its", "that", "was", "are", "be", "been", "have", "has",
        "not", "no", "so", "do", "did", "just", "get", "got",
        "very", "really", "like", "one", "from", "by", "you", "your",
        "they", "them", "their", "we", "our", "will", "would", "could",
        "also", "more", "about", "what", "when", "who", "which", "than",
        "into", "there", "here", "then", "than", "these", "those",
        "sauvage", "creed", "dior", "ysl", "skinn", "bella", "vita",
        "engage", "fogg", "titan", "aventus", "opium", "perfume",
        "fragrance", "cologne", "scent", "video", "channel", "watch",
        "brand", "product", "review", "smell", "smells", "wearing", "wear"
        "dont", "still", "most", "because", "people", "think",
        "even", "please", "videos", "also", "time", "make",
        "know", "want", "need", "much", "many", "only", "other",
        "some", "them", "been", "have", "come", "back", "well",
        "bought", "since", "every", "over", "after", "before",
        "better", "never", "always", "another", "something"
    }
    filtered = df[df["sentiment"] == sentiment_filter]["text"]
    words = []
    for text in filtered:
        clean = re.sub(r'[^a-zA-Z\s]', '', str(text).lower())
        words.extend([
            w for w in clean.split()
            if w not in stopwords and len(w) > 3
        ])
    return Counter(words).most_common(top_n)

def calculate_share_of_voice(brand1_df, brand2_df):
    total = len(brand1_df) + len(brand2_df)
    if total == 0:
        return 0, 0
    sov1 = round((len(brand1_df) / total) * 100, 1)
    sov2 = round((len(brand2_df) / total) * 100, 1)
    return sov1, sov2

# ------------------ FETCH DATA ON ANALYSE ------------------
@st.cache_data
def load_all_data():
    df = pd.read_csv("brand_data.csv", parse_dates=["date"])
    return df

all_data = load_all_data()

if analyse_button:
    st.session_state.audit_result = None

    primary_df = all_data[all_data["brand"] == primary_brand].copy()
    st.session_state.primary_df = primary_df
    st.session_state.primary_brand = primary_brand

    if competitor_brand != "None":
        competitor_df = all_data[all_data["brand"] == competitor_brand].copy()
        st.session_state.competitor_df = competitor_df
        st.session_state.competitor_brand = competitor_brand
    else:
        st.session_state.competitor_df = pd.DataFrame()
        st.session_state.competitor_brand = None
# ------------------ DISPLAY RESULTS ------------------
if not st.session_state.primary_df.empty:

    primary_df = st.session_state.primary_df
    competitor_df = st.session_state.competitor_df
    primary_brand = st.session_state.primary_brand
    competitor_brand = st.session_state.competitor_brand

    pos, neg, neu, total = get_sentiment_counts(primary_df)
    positive_pct = round((pos / total) * 100, 1) if total > 0 else 0
    yt_count = len(primary_df[primary_df['source'] == 'YouTube'])
    news_count = len(primary_df[primary_df['source'] == 'News'])

    # ------------------ HEADER ------------------
    st.markdown(f"### 📍 {primary_brand}")
    if competitor_brand:
        st.markdown(f"*Compared against: {competitor_brand}*")
    st.markdown("---")

    # ------------------ KPI CARDS ------------------
   # ------------------ KPI CARDS ------------------
st.markdown(f"""
<div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;'>
    <div style='background: #1a1a2e; border: 1px solid #00b4d8;
                border-radius: 12px; padding: 20px; text-align: center;'>
        <p style='color: #888; font-size: 13px; margin: 0 0 8px;'>Overall Sentiment</p>
        <p style='color: #00b4d8; font-size: 28px; font-weight: 700; margin: 0;'>{positive_pct}%</p>
        <p style='color: #888; font-size: 12px; margin: 4px 0 0;'>positive</p>
    </div>
    <div style='background: #1a1a2e; border: 1px solid #555;
                border-radius: 12px; padding: 20px; text-align: center;'>
        <p style='color: #888; font-size: 13px; margin: 0 0 8px;'>Data Points</p>
        <p style='color: white; font-size: 28px; font-weight: 700; margin: 0;'>{total:,}</p>
        <p style='color: #888; font-size: 12px; margin: 4px 0 0;'>analysed</p>
    </div>
    <div style='background: #1a1a2e; border: 1px solid #555;
                border-radius: 12px; padding: 20px; text-align: center;'>
        <p style='color: #888; font-size: 13px; margin: 0 0 8px;'>YouTube Comments</p>
        <p style='color: white; font-size: 28px; font-weight: 700; margin: 0;'>{yt_count:,}</p>
        <p style='color: #888; font-size: 12px; margin: 4px 0 0;'>comments</p>
    </div>
    <div style='background: #1a1a2e; border: 1px solid #555;
                border-radius: 12px; padding: 20px; text-align: center;'>
        <p style='color: #888; font-size: 13px; margin: 0 0 8px;'>News Articles</p>
        <p style='color: white; font-size: 28px; font-weight: 700; margin: 0;'>{news_count:,}</p>
        <p style='color: #888; font-size: 12px; margin: 4px 0 0;'>articles</p>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

    # ------------------ SENTIMENT BREAKDOWN ------------------
    st.subheader("📊 Sentiment Breakdown")
    col1, col2 = st.columns(2)

    with col1:
        sentiment_data = pd.DataFrame({
            "Sentiment": ["Positive", "Neutral", "Negative"],
            "Count": [pos, neu, neg],
            "Percentage": [
                round((pos/total)*100, 1),
                round((neu/total)*100, 1),
                round((neg/total)*100, 1)
            ]
        })
        fig = px.bar(
            sentiment_data,
            x="Sentiment",
            y="Percentage",
            color="Sentiment",
            color_discrete_map={
                "Positive": "#1D9E75",
                "Neutral": "#B4B2A9",
                "Negative": "#E24B4A"
            },
            title=f"Sentiment Distribution — {primary_brand}"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Sentiment scores:**")
        st.markdown(f"🟢 Positive: **{round((pos/total)*100, 1)}%**")
        st.progress(pos/total)
        st.markdown(f"⚪ Neutral: **{round((neu/total)*100, 1)}%**")
        st.progress(neu/total)
        st.markdown(f"🔴 Negative: **{round((neg/total)*100, 1)}%**")
        st.progress(neg/total)
        st.markdown("---")
        st.markdown("**Data sources:**")
        st.markdown(f"📺 YouTube: **{yt_count}** comments")
        st.markdown(f"📰 News: **{news_count}** articles")

    st.markdown("---")

    # ------------------ SENTIMENT TREND ------------------
    st.subheader("📈 Sentiment Trend Over Time")

    primary_df["month"] = primary_df["date"].dt.to_period("M").astype(str)
    monthly = primary_df.groupby("month").apply(
    lambda x: round((x["sentiment"] == "positive").mean() * 100, 1)
    if len(x) >= 5 else None
).dropna().reset_index()
    monthly.columns = ["month", "positive_pct"]
    monthly = monthly.sort_values("month").tail(24)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=monthly["month"],
        y=monthly["positive_pct"],
        name=primary_brand,
        line=dict(color="#00b4d8", width=2),
        mode="lines+markers"
    ))

    if not competitor_df.empty:
    competitor_df["month"] = competitor_df["date"].dt.to_period("M").astype(str)
    comp_monthly = competitor_df.groupby("month").apply(
        lambda x: round((x["sentiment"] == "positive").mean() * 100, 1)
        if len(x) >= 5 else None
    ).dropna().reset_index()
    comp_monthly.columns = ["month", "positive_pct"]
    comp_monthly = comp_monthly.sort_values("month").tail(24)

        fig2.add_trace(go.Scatter(
            x=comp_monthly["month"],
            y=comp_monthly["positive_pct"],
            name=competitor_brand,
            line=dict(color="#f77f00", width=2, dash="dot"),
            mode="lines+markers"
        ))

    fig2.update_layout(
        yaxis_title="% Positive Sentiment",
        xaxis_title="Month",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(
        "⚠️ Trend based on YouTube comment publish dates. "
        "Months with fewer than 5 data points may show extreme values."
    )
    st.markdown("---")

    # ------------------ SHARE OF VOICE ------------------
    if not competitor_df.empty:
    st.subheader("📢 Share of Voice")
    sov1, sov2 = calculate_share_of_voice(primary_df, competitor_df)

    st.markdown(f"""
    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 16px;'>
        <div style='background: #1a1a2e; border: 1px solid #00b4d8;
                    border-radius: 12px; padding: 20px; text-align: center;'>
            <p style='color: #888; font-size: 13px; margin: 0 0 8px;'>{primary_brand}</p>
            <p style='color: #00b4d8; font-size: 32px; font-weight: 700; margin: 0;'>{sov1}%</p>
            <p style='color: #888; font-size: 12px; margin: 4px 0 0;'>share of voice</p>
        </div>
        <div style='background: #2e1a0a; border: 1px solid #f77f00;
                    border-radius: 12px; padding: 20px; text-align: center;'>
            <p style='color: #888; font-size: 13px; margin: 0 0 8px;'>{competitor_brand}</p>
            <p style='color: #f77f00; font-size: 32px; font-weight: 700; margin: 0;'>{sov2}%</p>
            <p style='color: #888; font-size: 12px; margin: 4px 0 0;'>share of voice</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ------------------ CONSUMER KEYWORDS ------------------
    st.subheader("💬 Consumer Perception Keywords")
    st.caption("Most frequent meaningful words in positive comments")

    keywords = get_top_keywords(primary_df, sentiment_filter="positive")

    if keywords:
        keyword_df = pd.DataFrame(keywords, columns=["Word", "Count"])
        fig3 = px.bar(
            keyword_df.head(15),
            x="Count",
            y="Word",
            orientation="h",
            title=f"Top Keywords — {primary_brand} (Positive Comments)",
            color="Count",
            color_continuous_scale="Blues"
        )
        fig3.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ------------------ AI BRAND AUDIT ------------------
    st.subheader("🤖 AI Brand Audit Report")

    neg_keywords = get_top_keywords(primary_df, sentiment_filter="negative", top_n=5)
    pos_keywords = get_top_keywords(primary_df, sentiment_filter="positive", top_n=5)

    summary = f"""
Brand: {primary_brand}
Total data points analysed: {total}
Positive sentiment: {positive_pct}%
Negative sentiment: {round((neg/total)*100, 1)}%
Neutral sentiment: {round((neu/total)*100, 1)}%
Top positive keywords: {[w for w, c in pos_keywords]}
Top negative keywords: {[w for w, c in neg_keywords]}
Data sources: YouTube comments ({yt_count}), News articles ({news_count})
Note: Data from fragrance review videos and news coverage. Sentiment via VADER NLP.
"""

    if competitor_brand and not competitor_df.empty:
        comp_pos, comp_neg, comp_neu, comp_total = get_sentiment_counts(competitor_df)
        comp_positive_pct = round((comp_pos / comp_total) * 100, 1) if comp_total > 0 else 0
        sov1, sov2 = calculate_share_of_voice(primary_df, competitor_df)
        summary += f"""
Competitor: {competitor_brand}
Competitor positive sentiment: {comp_positive_pct}%
Competitor share of voice: {sov2}%
Primary brand share of voice: {sov1}%
"""

    if st.button("Generate AI Brand Audit"):
        with st.spinner("Generating brand audit report..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a senior marketing consultant specialising in brand strategy and consumer insights for the fragrance industry."
                        },
                        {
                            "role": "user",
                            "content": f"""Analyse the following brand health data and provide a consulting-style brand audit:

1. Brand Position — how consumers currently perceive this brand
2. Risk or Concern — key risks from negative sentiment patterns
3. Business Recommendation — specific strategic recommendation
4. One Actionable Strategy — concrete next step

Data:
{summary}
"""
                        }
                    ]
                )
                st.session_state.audit_result = response.choices[0].message.content

            except Exception as e:
                st.error(f"AI analysis failed: {e}")

    # Display audit result if it exists in session state
    if st.session_state.audit_result:
        st.success("Audit complete!")
        st.markdown("### 📋 Brand Audit Report")
        st.write(st.session_state.audit_result)
        st.download_button(
            label="📥 Download Report",
            data=st.session_state.audit_result,
            file_name=f"brand_audit_{primary_brand.replace(' ', '_')}.txt"
        )

    st.markdown("---")

    # ------------------ RAW DATA ------------------
    with st.expander("📁 View Raw Data"):
        st.caption(f"All data points for {primary_brand}")
        st.dataframe(
            primary_df[["text", "sentiment", "compound_score", "source", "date"]].reset_index(drop=True),
            use_container_width=True
        )

else:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
                    border: 1px solid #0f3460;
                    border-radius: 12px;
                    padding: 24px;
                    text-align: center;'>
            <h2 style='color: #00b4d8; margin: 0 0 8px;'>🌍</h2>
            <h3 style='color: white; margin: 0 0 12px;'>Global Luxury</h3>
            <p style='color: #aaa; font-size: 14px; line-height: 1.8; margin: 0;'>
                Dior Sauvage<br>Creed Aventus<br>YSL Black Opium
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1a2e1a, #162116);
                    border: 1px solid #0f6030;
                    border-radius: 12px;
                    padding: 24px;
                    text-align: center;'>
            <h2 style='color: #06d6a0; margin: 0 0 8px;'>🇮🇳</h2>
            <h3 style='color: white; margin: 0 0 12px;'>Indian Premium</h3>
            <p style='color: #aaa; font-size: 14px; line-height: 1.8; margin: 0;'>
                Skinn by Titan<br>Bella Vita Perfume
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #2e1a1a, #211616);
                    border: 1px solid #602010;
                    border-radius: 12px;
                    padding: 24px;
                    text-align: center;'>
            <h2 style='color: #f77f00; margin: 0 0 8px;'>🇮🇳</h2>
            <h3 style='color: white; margin: 0 0 12px;'>Indian Mass Market</h3>
            <p style='color: #aaa; font-size: 14px; line-height: 1.8; margin: 0;'>
                Engage Perfume<br>Fogg Perfume
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Select a brand from the sidebar and click **Analyse Brand** to get started.")