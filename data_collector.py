import os
import pandas as pd
from googleapiclient.discovery import build
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

analyser = SentimentIntensityAnalyzer()

# ------------------ YOUTUBE ------------------
def get_youtube_comments(brand_name, max_results=200):
    """Pull comments from YouTube fragrance review videos for a brand"""
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        # Search for fragrance review videos
        search_response = youtube.search().list(
            q=f"{brand_name} fragrance review",
            part="id",
            maxResults=10,
            type="video",
            relevanceLanguage="en"
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]

        all_comments = []

        for video_id in video_ids:
            try:
                comments_response = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=50,
                    textFormat="plainText",
                    order="relevance"
                ).execute()

                for item in comments_response.get("items", []):
                    comment = item["snippet"]["topLevelComment"]["snippet"]
                    all_comments.append({
                        "text": comment["textDisplay"],
                        "date": comment["publishedAt"][:10],
                        "source": "YouTube",
                        "brand": brand_name
                    })

            except Exception:
                continue

        return all_comments[:max_results]

    except Exception as e:
        print(f"YouTube error for {brand_name}: {e}")
        return []


# ------------------ NEWS API ------------------
def get_news_articles(brand_name, max_results=100):
    """Pull recent news articles mentioning the brand"""
    try:
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)

        response = newsapi.get_everything(
            q=f"{brand_name} perfume OR fragrance",
            language="en",
            sort_by="publishedAt",
            page_size=max_results
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


# ------------------ SENTIMENT ------------------
def analyse_sentiment(text):
    """Run VADER sentiment on a piece of text"""
    scores = analyser.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        return "positive", compound
    elif compound <= -0.05:
        return "negative", compound
    else:
        return "neutral", compound


def get_brand_data(brand_name):
    """
    Main function — pulls YouTube + News data for a brand
    and returns a DataFrame with sentiment scores
    """
    print(f"Fetching data for {brand_name}...")

    # Pull data from both sources
    youtube_data = get_youtube_comments(brand_name)
    news_data = get_news_articles(brand_name)

    all_data = youtube_data + news_data

    if not all_data:
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(all_data)

    # Run sentiment on every row
    df[["sentiment", "compound_score"]] = df["text"].apply(
        lambda x: pd.Series(analyse_sentiment(x))
    )

    df["date"] = pd.to_datetime(df["date"])

    print(f"Done — {len(df)} data points for {brand_name}")
    return df


# ------------------ TEST ------------------
if __name__ == "__main__":
    # Quick test — run this to verify everything works
    test_brand = "Dior Sauvage"
    df = get_brand_data(test_brand)

    if not df.empty:
        print(f"\nTotal data points: {len(df)}")
        print(f"YouTube comments: {len(df[df['source'] == 'YouTube'])}")
        print(f"News articles: {len(df[df['source'] == 'News'])}")
        print(f"\nSentiment breakdown:")
        print(df["sentiment"].value_counts())
        print(f"\nSample comments:")
        print(df[["text", "sentiment", "compound_score"]].head(5))
    else:
        print("No data returned — check your API keys")
    