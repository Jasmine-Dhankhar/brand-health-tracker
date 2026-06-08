import pandas as pd
from data_collector import get_brand_data
import time
import os
from googleapiclient.discovery import build
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from newsapi import NewsApiClient
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

analyser = SentimentIntensityAnalyzer()

def get_youtube_comments_large(brand_name, max_comments=1000):
    """Pull up to 1000 comments per brand from multiple videos"""
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        # Search for more videos — 15 instead of 5
        search_response = youtube.search().list(
            q=f"{brand_name} fragrance review",
            part="id",
            maxResults=15,
            type="video",
            relevanceLanguage="en"
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]

        all_comments = []

        for video_id in video_ids:
            if len(all_comments) >= max_comments:
                break
            try:
                # Pull multiple pages of comments per video
                next_page_token = None
                while len(all_comments) < max_comments:
                    request_params = {
                        "part": "snippet",
                        "videoId": video_id,
                        "maxResults": 100,
                        "textFormat": "plainText",
                        "order": "relevance"
                    }
                    if next_page_token:
                        request_params["pageToken"] = next_page_token

                    comments_response = youtube.commentThreads().list(
                        **request_params
                    ).execute()

                    for item in comments_response.get("items", []):
                        comment = item["snippet"]["topLevelComment"]["snippet"]
                        all_comments.append({
                            "text": comment["textDisplay"],
                            "date": comment["publishedAt"][:10],
                            "source": "YouTube",
                            "brand": brand_name
                        })

                    next_page_token = comments_response.get("nextPageToken")
                    if not next_page_token:
                        break

            except Exception:
                continue

        return all_comments[:max_comments]

    except Exception as e:
        print(f"YouTube error for {brand_name}: {e}")
        return []

def get_news_articles_large(brand_name, max_results=100):
    """Pull up to 100 news articles"""
    try:
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        response = newsapi.get_everything(
            q=f"{brand_name} perfume OR fragrance",
            language="en",
            sort_by="publishedAt",
            page_size=100
        )
        articles = []
        for article in response.get("articles", []):
            if article["title"] and article["title"] != "[Removed]":
                articles.append({
                    "text": article["title"] + ". " + (article["description"] or ""),
                    "date": article["publishedAt"][:10],
                    "source": "News",
                    "brand": brand_name
                })
        return articles
    except Exception as e:
        print(f"News error for {brand_name}: {e}")
        return []

def analyse_sentiment(text):
    scores = analyser.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        return "positive", compound
    elif compound <= -0.05:
        return "negative", compound
    else:
        return "neutral", compound

# ------------------ MAIN ------------------
brands = [
    "Dior Sauvage",
    "Creed Aventus",
    "YSL Black Opium",
    "Skinn by Titan",
    "Bella Vita Perfume",
    "Engage Perfume",
    "Fogg Perfume"
]

all_data = []

for brand in brands:
    print(f"\nCollecting data for {brand}...")

    youtube_comments = get_youtube_comments_large(brand, max_comments=1000)
    print(f"YouTube: {len(youtube_comments)} comments")

    news_articles = get_news_articles_large(brand, max_results=100)
    print(f"News: {len(news_articles)} articles")

    combined = youtube_comments + news_articles

    if combined:
        df = pd.DataFrame(combined)
        df[["sentiment", "compound_score"]] = df["text"].apply(
            lambda x: pd.Series(analyse_sentiment(x))
        )
        df["date"] = pd.to_datetime(df["date"])
        all_data.append(df)
        print(f"Done — {len(df)} total data points for {brand}")

    time.sleep(5)  # Avoid rate limits between brands

# Save
final_df = pd.concat(all_data, ignore_index=True)
final_df.to_csv("brand_data.csv", index=False)
print(f"\nTotal data points collected: {len(final_df)}")
print(final_df['brand'].value_counts())