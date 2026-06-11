# Brand-health-tracker
# 🏷️ Brand Health Tracker

A live brand health analytics dashboard that tracks consumer sentiment for fragrance brands — from global luxury to Indian mass market — using real YouTube comments, news articles, and AI-generated brand audit reports.

## 🔗 Live App
👉 https://brand-health-tracker.streamlit.app

## 📊 What It Does
- Analyses 6,500 real YouTube comments and news articles across 7 brands
- Runs VADER NLP sentiment analysis on every data point
- Tracks Share of Voice between competing brands
- Shows consumer perception keywords from positive comments
- Generates AI-powered consulting-style brand audit reports using GPT-4o-mini

## 🏢 Brands Covered
| Tier | Brands |
|------|--------|
| 🌍 Global Luxury | Dior Sauvage, Creed Aventus, YSL Black Opium |
| 🇮🇳 Indian Premium | Skinn by Titan, Bella Vita Perfume |
| 🇮🇳 Indian Mass Market | Engage Perfume, Fogg Perfume |

## 💡 Key Finding
The sentiment gap between global luxury and Indian mass market brands is surprisingly small — Dior Sauvage scores 60.4% positive while Bella Vita scores 63.9%. The price gap is 10x. The perception gap is almost nothing.

## 🛠️ Built With
- Python
- Streamlit
- YouTube Data API v3
- NewsAPI
- VADER Sentiment Analysis
- Plotly
- OpenAI GPT-4o-mini
- Pandas

## 📁 Project Structure
- app.py — Main Streamlit dashboard
- data_collector.py — YouTube + NewsAPI data collection + VADER sentiment
- collect_data.py — One-time data collection script for all 7 brands
- brand_data.csv — Pre-collected dataset (6,500 data points)
- requirements.txt — Python dependencies

## 📌 Data Source
Data collected via YouTube Data API v3 and NewsAPI. Sentiment scored using VADER NLP on real consumer comments. Data collected: June 2026.
