"""Utilities for fetching and displaying real-time news"""

import streamlit as st
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
from pathlib import Path
import os


@st.cache_data(ttl=1800)
def fetch_news_from_newsapi(ticker: str, api_key: Optional[str] = None, max_results: int = 10) -> List[Dict]:
    """Fetch news from NewsAPI

    Args:
        ticker: Stock ticker symbol
        api_key: NewsAPI key
        max_results: Maximum number of results

    Returns:
        List of news articles
    """
    if not api_key:
        return []

    try:
        company_name = get_company_name(ticker)

        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        url = "https://newsapi.org/v2/everything"
        params = {
            'q': f'{company_name} OR {ticker}',
            'from': from_date,
            'sortBy': 'publishedAt',
            'language': 'en',
            'pageSize': max_results,
            'apiKey': api_key
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            articles = []

            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'publishedAt': article.get('publishedAt', ''),
                    'sentiment': analyze_sentiment_simple(article.get('title', '') + ' ' + article.get('description', ''))
                })

            return articles

    except Exception:
        return []

    return []


@st.cache_data(ttl=1800)
def fetch_news_from_alphavantage(ticker: str, api_key: Optional[str] = None) -> List[Dict]:
    """Fetch news from Alpha Vantage

    Args:
        ticker: Stock ticker symbol
        api_key: Alpha Vantage API key

    Returns:
        List of news articles
    """
    if not api_key:
        return []

    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': ticker,
            'apikey': api_key,
            'limit': 50
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if 'feed' not in data:
                return []

            articles = []

            for item in data.get('feed', []):
                articles.append({
                    'title': item.get('title', ''),
                    'description': item.get('summary', ''),
                    'url': item.get('url', ''),
                    'source': item.get('source', 'Unknown'),
                    'publishedAt': item.get('time_published', ''),
                    'sentiment': convert_av_sentiment(item.get('overall_sentiment_score', 0)),
                    'sentiment_score': item.get('overall_sentiment_score', 0)
                })

            return articles

    except Exception:
        return []

    return []


def get_company_name(ticker: str) -> str:
    """Get company name from ticker

    Args:
        ticker: Stock ticker symbol

    Returns:
        Company name
    """
    company_mapping = {
        'AAPL': 'Apple',
        'MSFT': 'Microsoft',
        'GOOGL': 'Google',
        'GOOG': 'Google',
        'AMZN': 'Amazon',
        'META': 'Meta',
        'TSLA': 'Tesla',
        'NVDA': 'NVIDIA',
        'AVGO': 'Broadcom',
        'IBM': 'IBM',
        'ORCL': 'Oracle',
        'INTC': 'Intel',
        'AMD': 'AMD',
        'NFLX': 'Netflix',
        'DIS': 'Disney',
        'BA': 'Boeing',
        'JPM': 'JPMorgan',
        'V': 'Visa',
        'MA': 'Mastercard',
        'WMT': 'Walmart',
        'KO': 'Coca-Cola',
        'PFE': 'Pfizer',
        'JNJ': 'Johnson',
        'PG': 'Procter',
        'BAC': 'Bank of America',
        'CSCO': 'Cisco',
        'ADBE': 'Adobe',
        'CRM': 'Salesforce',
        'PETR4.SA': 'Petrobras',
        'VALE3': 'Vale',
        'ITUB4': 'Itau',
        'BBDC4': 'Bradesco',
    }

    return company_mapping.get(ticker.upper(), ticker)


def analyze_sentiment_simple(text: str) -> str:
    """Simple sentiment analysis based on keywords

    Args:
        text: Text to analyze

    Returns:
        Sentiment: positive, negative, or neutral
    """
    if not text:
        return 'neutral'

    text_lower = text.lower()

    positive_words = ['rise', 'gain', 'profit', 'growth', 'bull', 'positive', 'surge',
                      'jump', 'rally', 'upgrade', 'beat', 'strong', 'boost', 'win']

    negative_words = ['fall', 'loss', 'decline', 'bear', 'negative', 'drop',
                      'plunge', 'downgrade', 'miss', 'weak', 'concern', 'risk']

    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'


def convert_av_sentiment(score: float) -> str:
    """Convert Alpha Vantage sentiment score to category

    Args:
        score: Sentiment score from -1 to 1

    Returns:
        Sentiment category
    """
    if score >= 0.15:
        return 'positive'
    elif score <= -0.15:
        return 'negative'
    else:
        return 'neutral'


def get_sentiment_emoji(sentiment: str) -> str:
    """Get emoji for sentiment

    Args:
        sentiment: Sentiment category

    Returns:
        Emoji string
    """
    emoji_map = {
        'positive': '🟢',
        'negative': '🔴',
        'neutral': '⚪'
    }

    return emoji_map.get(sentiment, '⚪')


def get_sentiment_color(sentiment: str) -> str:
    """Get color for sentiment

    Args:
        sentiment: Sentiment category

    Returns:
        Color hex code
    """
    color_map = {
        'positive': '#10b981',
        'negative': '#ef4444',
        'neutral': '#6b7280'
    }

    return color_map.get(sentiment, '#6b7280')


def format_published_date(date_str: str) -> str:
    """Format published date to readable format

    Args:
        date_str: Date string in various formats

    Returns:
        Formatted date string
    """
    if not date_str:
        return 'Unknown date'

    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_str[:14], '%Y%m%dT%H%M%S')

        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt

        if diff.days == 0:
            if diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"{minutes}m ago"
            else:
                hours = diff.seconds // 3600
                return f"{hours}h ago"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days}d ago"
        else:
            return dt.strftime('%b %d, %Y')

    except Exception:
        return date_str


def render_news_card(article: Dict, show_description: bool = True):
    """Render news article as a styled card

    Args:
        article: Article dictionary
        show_description: Whether to show full description
    """
    sentiment = article.get('sentiment', 'neutral')
    sentiment_emoji = get_sentiment_emoji(sentiment)
    sentiment_color = get_sentiment_color(sentiment)

    published = format_published_date(article.get('publishedAt', ''))
    source = article.get('source', 'Unknown')
    title = article.get('title', 'No title')
    description = article.get('description', '')
    url = article.get('url', '#')

    card_html = f'''
    <div style="border-left: 4px solid {sentiment_color}; padding: 16px; margin-bottom: 16px;
                background: #f8fafc; border-radius: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                    <span style="font-size: 12px; font-weight: 600; color: #64748b;">
                        {source}
                    </span>
                    <span style="font-size: 12px; color: #94a3b8;">•</span>
                    <span style="font-size: 12px; color: #94a3b8;">{published}</span>
                </div>
                <h4 style="margin: 0; font-size: 16px; font-weight: 600; color: #1e293b;">
                    {title}
                </h4>
            </div>
            <span style="font-size: 20px; margin-left: 12px;">{sentiment_emoji}</span>
        </div>
    </div>
    '''

    st.markdown(card_html, unsafe_allow_html=True)

    if show_description and description:
        st.markdown(f"<p style='color: #64748b; font-size: 14px; margin-top: -8px; margin-bottom: 8px;'>{description}</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 5])
    with col1:
        if url and url != '#':
            st.link_button("Read More", url, use_container_width=True)


def fetch_all_news(ticker: str, newsapi_key: Optional[str] = None,
                   alphavantage_key: Optional[str] = None) -> List[Dict]:
    """Fetch news from all available sources

    Args:
        ticker: Stock ticker symbol
        newsapi_key: NewsAPI key
        alphavantage_key: Alpha Vantage API key

    Returns:
        Combined list of news articles
    """
    all_news = []

    if newsapi_key:
        newsapi_articles = fetch_news_from_newsapi(ticker, newsapi_key)
        all_news.extend(newsapi_articles)

    if alphavantage_key:
        av_articles = fetch_news_from_alphavantage(ticker, alphavantage_key)
        all_news.extend(av_articles)

    all_news = remove_duplicates(all_news)

    all_news.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)

    return all_news


def remove_duplicates(articles: List[Dict]) -> List[Dict]:
    """Remove duplicate articles based on title similarity

    Args:
        articles: List of articles

    Returns:
        De-duplicated list
    """
    seen_titles = set()
    unique_articles = []

    for article in articles:
        title = article.get('title', '').lower().strip()

        title_normalized = re.sub(r'[^\w\s]', '', title)

        if title_normalized and title_normalized not in seen_titles:
            seen_titles.add(title_normalized)
            unique_articles.append(article)

    return unique_articles
