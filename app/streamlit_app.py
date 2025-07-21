import streamlit as st
import requests
import plotly.express as px

st.set_page_config(page_title="📈 Stock Sentiment Dashboard", layout="wide")
st.title("📊 Stock Market News Sentiment")
st.markdown("Select a stock or keyword to fetch recent financial news and analyze sentiment.")

API_BASE = "http://localhost:8000"

# Fetch keyword suggestions from backend
@st.cache_data(ttl=300)
def fetch_keywords():
    try:
        res = requests.get(f"{API_BASE}/keywords")
        return res.json().get("keywords", [])
    except Exception:
        return []

keywords = fetch_keywords()

# UI components
col1, col2 = st.columns([2, 1])
with col1:
    selected_keyword = st.selectbox("🔍 Select Stock/Company", keywords, index=0 if keywords else None)
with col2:
    reload_requested = st.checkbox("🔁 Force Reload", value=False)

# Analyze button
if st.button("Analyze"):
    with st.spinner("Fetching headlines and analyzing sentiment..."):
        try:
            res = requests.get(
                f"{API_BASE}/sentiment",
                params={"stock": selected_keyword, "reload": reload_requested}
            )
            data = res.json()

            if isinstance(data, dict) and "error" in data:
                st.error(f"❌ API Error: {data['error']}")
                st.stop()

            if not data:
                st.warning("⚠️ No headlines found for this keyword.")
                st.stop()

            sentiments = [item["sentiment"] for item in data]
            sentiment_counts = {
                "positive": sentiments.count("positive"),
                "neutral": sentiments.count("neutral"),
                "negative": sentiments.count("negative")
            }

            fig = px.pie(
                names=list(sentiment_counts.keys()),
                values=list(sentiment_counts.values()),
                title=f"Sentiment Breakdown for {selected_keyword}",
                color_discrete_sequence=["green", "gray", "red"]
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📰 Headlines")
            for i, item in enumerate(data, 1):
                st.markdown(f"""
                **{i}. {item['headline']}**  
                Sentiment: `{item['sentiment'].capitalize()}`  
                Polarity: `{item['polarity']:.2f}`
                ---
                """)
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
