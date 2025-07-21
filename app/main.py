from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from app.scraper import get_financial_headlines_with_sentiment
from collections import Counter
import re

app = FastAPI(title="Stock Market News Sentiment API")

# Allow all origins for development (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "🚀 Welcome to the Financial News Sentiment API"}

@app.get("/scrape-news")
def scrape_news():
    """
    Raw headline fetch endpoint (all financial news)
    """
    headlines_with_sentiment = get_financial_headlines_with_sentiment()
    return {"results": headlines_with_sentiment}

@app.get("/sentiment")
def get_sentiment(stock: str = Query(..., description="Name of the stock or keyword to search")):
    """
    Filters headlines that mention the stock or its aliases (case-insensitive).
    Used by the dashboard for sentiment analysis.
    """
    try:
        headlines_with_sentiment = get_financial_headlines_with_sentiment()

        # Alias mapping for better results
        aliases = {
            "google": ["google", "alphabet"],
            "tesla": ["tesla", "elon musk"],
            "apple": ["apple", "aapl"],
            "microsoft": ["microsoft", "msft"],
            "amazon": ["amazon", "amzn"],
            "meta": ["meta", "facebook", "mark zuckerberg"],
            "nvidia": ["nvidia", "nvda"],
            "netflix": ["netflix", "nflx"]
        }

        query = stock.lower()
        keywords = aliases.get(query, [query])

        filtered = [
            item for item in headlines_with_sentiment
            if any(keyword in item["headline"].lower() for keyword in keywords)
        ]
        return filtered
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug")
def debug_raw_headlines():
    try:
        headlines_with_sentiment = get_financial_headlines_with_sentiment()
        return {"count": len(headlines_with_sentiment), "sample": headlines_with_sentiment[:3]}
    except Exception as e:
        return {"error": str(e)}

@app.get("/keywords")
def get_keywords():
    """
    Extract and return common capitalized words (likely company names or tickers) from headlines.
    Helps frontend populate stock/company dropdown.
    """
    try:
        headlines_with_sentiment = get_financial_headlines_with_sentiment()
        keywords = []

        for item in headlines_with_sentiment:
            headline = item["headline"]
            # Extract proper nouns (capitalized words, length >= 3)
            words = re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', headline)
            keywords.extend(words)

        # Count most frequent proper nouns
        common = Counter(keywords).most_common(15)
        return {"keywords": [word for word, _ in common]}
    except Exception as e:
        return {"error": str(e)}
