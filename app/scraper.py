import asyncio
import feedparser
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import time
import random

from app.proxy_utils import get_proxy, get_headers  # 👈 Proxy helpers added

# Download VADER lexicon if not already downloaded
nltk.download('vader_lexicon')
analyzer = SentimentIntensityAnalyzer()

# RSS Feeds as fallback
RSS_FEEDS = [
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.investing.com/rss/news.rss"
]

# Website configurations
WEBSITE_CONFIGS = {
    "cnbc": {
        "url": "https://www.cnbc.com/finance/",
        "headline_selectors": [
            "h2 a[href*='/2024/']",
            "h2 a[href*='/2025/']",
            ".InlineVideo-container a",
            ".Card-title a",
            ".FeedCard-title",
            "h3 a[href*='cnbc.com']"
        ]
    },
    "reuters": {
        "url": "https://www.reuters.com/business/",
        "headline_selectors": [
            "[data-testid='Heading'] a",
            ".story-title a",
            ".media-story-card__headline__eqhp9 a",
            "h3 a[href*='/business/']",
            "h2 a[href*='/business/']"
        ]
    },
    "investing": {
        "url": "https://www.investing.com/news/",
        "headline_selectors": [
            ".articleItem .title a",
            ".js-article-item .title a",
            ".articleList .articleItem h4 a",
            ".largeTitle .title a"
        ]
    }
}

def get_sentiment(text):
    scores = analyzer.polarity_scores(text)
    polarity = scores["compound"]
    sentiment = (
        "positive" if polarity > 0.05 else
        "negative" if polarity < -0.05 else
        "neutral"
    )
    return {"headline": text, "polarity": polarity, "sentiment": sentiment}

async def scrape_website_with_playwright(site_name, config, limit=10):
    headlines = []

    try:
        async with async_playwright() as p:
            # Pick proxy & headers
            proxy_config = get_proxy()
            proxy_server = proxy_config["http"].replace("http://", "") if proxy_config else None
            headers = get_headers()

            browser = await p.chromium.launch(headless=True, proxy={"server": f"http://{proxy_server}"} if proxy_server else None)
            context = await browser.new_context(user_agent=headers["User-Agent"])
            page = await context.new_page()

            print(f"🌐 Scraping {site_name} with proxy {proxy_server}...")

            await page.goto(config["url"], wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(3000)

            content = await page.content()
            await browser.close()

            soup = BeautifulSoup(content, 'html.parser')
            for selector in config["headline_selectors"]:
                for element in soup.select(selector):
                    title = element.get_text().strip()
                    if title and len(title) > 20 and title not in [h["headline"] for h in headlines]:
                        analyzed = get_sentiment(title)
                        print(f"📌 [{site_name.upper()}] {analyzed['headline']} → {analyzed['sentiment']}")
                        headlines.append(analyzed)
                        if len(headlines) >= limit:
                            return headlines
    except Exception as e:
        print(f"[ERROR] Failed to scrape {site_name}: {e}")

    return headlines

def scrape_rss_feeds(limit=10):
    headlines = []

    print("\n📡 Using RSS feeds as fallback...")
    for feed_url in RSS_FEEDS:
        try:
            print(f"📡 Fetching RSS: {feed_url}")
            feed = feedparser.parse(feed_url)
            for entry in getattr(feed, 'entries', []):
                title = entry.title.strip()
                if title and title not in [h["headline"] for h in headlines]:
                    analyzed = get_sentiment(title)
                    print(f"📌 [RSS] {analyzed['headline']} → {analyzed['sentiment']}")
                    headlines.append(analyzed)
                    if len(headlines) >= limit:
                        return headlines
        except Exception as e:
            print(f"[ERROR] RSS parsing failed for {feed_url}: {e}")

    return headlines

async def scrape_top_headlines(limit=10, use_playwright=True):
    all_headlines = []

    print("\n📰 Fetching Top Financial Headlines...\n")

    if use_playwright:
        for site_name, config in WEBSITE_CONFIGS.items():
            headlines = await scrape_website_with_playwright(site_name, config, limit - len(all_headlines))
            all_headlines.extend(headlines)
            if len(all_headlines) >= limit:
                break
            await asyncio.sleep(random.uniform(1, 3))

    if len(all_headlines) < limit:
        remaining = limit - len(all_headlines)
        rss_headlines = scrape_rss_feeds(remaining)
        for h in rss_headlines:
            if h["headline"] not in [x["headline"] for x in all_headlines]:
                all_headlines.append(h)
                if len(all_headlines) >= limit:
                    break

    return all_headlines[:limit]

def get_financial_headlines_with_sentiment(limit=10):
    return asyncio.run(scrape_top_headlines(limit=limit))

# Optional local test
if __name__ == "__main__":
    print("🚀 Starting Financial Headlines Scraper with Sentiment...")
    headlines = get_financial_headlines_with_sentiment(limit=10)
    for h in headlines:
        print(f"{h['headline']} → {h['sentiment']}")
