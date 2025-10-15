"""Reddit sentiment analysis utilities

This module provides real-time sentiment analysis from Reddit posts.
Supports multiple subreddits and weighted sentiment scoring based on engagement.
"""

import streamlit as st
import praw
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter
import os
from pathlib import Path

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False


# Ticker mapping for common stocks
TICKER_MAPPING = {
    'AAPL': ['Apple', 'AAPL', '$AAPL'],
    'MSFT': ['Microsoft', 'MSFT', '$MSFT'],
    'GOOGL': ['Google', 'Alphabet', 'GOOGL', '$GOOGL'],
    'GOOG': ['Google', 'Alphabet', 'GOOG', '$GOOG'],
    'AMZN': ['Amazon', 'AMZN', '$AMZN'],
    'META': ['Meta', 'Facebook', 'META', '$META'],
    'TSLA': ['Tesla', 'TSLA', '$TSLA'],
    'NVDA': ['NVIDIA', 'Nvidia', 'NVDA', '$NVDA'],
    'AMD': ['AMD', '$AMD'],
    'INTC': ['Intel', 'INTC', '$INTC'],
    'NFLX': ['Netflix', 'NFLX', '$NFLX'],
    'DIS': ['Disney', 'DIS', '$DIS'],
    'AVGO': ['Broadcom', 'AVGO', '$AVGO'],
    'JPM': ['JPMorgan', 'JP Morgan', 'JPM', '$JPM'],
    'V': ['Visa', 'V', '$V'],
    'MA': ['Mastercard', 'MA', '$MA'],
    'WMT': ['Walmart', 'WMT', '$WMT'],
    'BAC': ['Bank of America', 'BofA', 'BAC', '$BAC'],
    'PETR4.SA': ['Petrobras', 'PETR4', '$PETR4'],
    'VALE3': ['Vale', 'VALE3', '$VALE3'],
}


class RedditClient:
    """Client for fetching Reddit posts"""

    def __init__(self, client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 user_agent: Optional[str] = None):
        """Initialize Reddit client

        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string
        """
        self.client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = user_agent or os.getenv('REDDIT_USER_AGENT', 'TradingAgents/1.0')

        self.reddit = None
        if self.client_id and self.client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
            except Exception as e:
                st.warning(f"Failed to initialize Reddit client: {e}")

    @st.cache_data(ttl=900)
    def fetch_posts(_self, ticker: str, subreddits: List[str],
                    limit: int = 50, time_filter: str = 'day') -> List[Dict]:
        """Fetch posts mentioning a ticker from subreddits

        Args:
            ticker: Stock ticker symbol
            subreddits: List of subreddit names
            limit: Maximum posts per subreddit
            time_filter: Time filter (hour, day, week, month)

        Returns:
            List of post dictionaries
        """
        if not _self.reddit:
            return []

        all_posts = []
        search_terms = _self._get_search_terms(ticker)

        for subreddit_name in subreddits:
            try:
                subreddit = _self.reddit.subreddit(subreddit_name)

                # Search for ticker mentions
                for search_term in search_terms[:2]:  # Limit to 2 terms to avoid rate limits
                    posts = subreddit.search(
                        search_term,
                        time_filter=time_filter,
                        limit=limit
                    )

                    for post in posts:
                        # Check if ticker is actually mentioned
                        text = f"{post.title} {post.selftext}"
                        if _self._contains_ticker(text, ticker):
                            post_data = {
                                'id': post.id,
                                'title': post.title,
                                'text': post.selftext,
                                'ticker': ticker,
                                'subreddit': subreddit_name,
                                'created_utc': post.created_utc,
                                'upvotes': post.score,
                                'num_comments': post.num_comments,
                                'awards': post.total_awards_received,
                                'url': f"https://reddit.com{post.permalink}",
                                'author': str(post.author) if post.author else '[deleted]'
                            }
                            all_posts.append(post_data)

            except Exception as e:
                st.warning(f"Error fetching from r/{subreddit_name}: {e}")
                continue

        # Remove duplicates
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post['id'] not in seen_ids:
                seen_ids.add(post['id'])
                unique_posts.append(post)

        return unique_posts

    @st.cache_data(ttl=900)
    def fetch_trending_tickers(_self, subreddits: List[str],
                               limit: int = 100) -> List[Tuple[str, int]]:
        """Fetch trending tickers from subreddits

        Args:
            subreddits: List of subreddit names
            limit: Posts to analyze per subreddit

        Returns:
            List of (ticker, mention_count) tuples
        """
        if not _self.reddit:
            return []

        ticker_mentions = Counter()

        for subreddit_name in subreddits:
            try:
                subreddit = _self.reddit.subreddit(subreddit_name)
                posts = subreddit.hot(limit=limit)

                for post in posts:
                    text = f"{post.title} {post.selftext}"
                    tickers = _self._extract_tickers(text)
                    for ticker in tickers:
                        ticker_mentions[ticker] += 1

            except Exception:
                continue

        return ticker_mentions.most_common(20)

    def _get_search_terms(self, ticker: str) -> List[str]:
        """Get search terms for a ticker"""
        terms = TICKER_MAPPING.get(ticker, [ticker])
        return list(set(terms))

    def _contains_ticker(self, text: str, ticker: str) -> bool:
        """Check if text contains ticker mention"""
        search_terms = self._get_search_terms(ticker)
        text_upper = text.upper()

        for term in search_terms:
            if term.upper() in text_upper:
                return True

        # Check for $TICKER pattern
        if re.search(rf'\${ticker}\b', text, re.IGNORECASE):
            return True

        return False

    def _extract_tickers(self, text: str) -> List[str]:
        """Extract ticker symbols from text"""
        tickers = []

        # Extract $TICKER patterns
        dollar_tickers = re.findall(r'\$([A-Z]{1,5})\b', text)
        tickers.extend(dollar_tickers)

        # Check against known tickers
        text_upper = text.upper()
        for ticker, terms in TICKER_MAPPING.items():
            for term in terms:
                if term.upper() in text_upper:
                    tickers.append(ticker)
                    break

        return list(set(tickers))


class SentimentAnalyzer:
    """Sentiment analyzer for social media text"""

    def __init__(self, method: str = 'vader'):
        """Initialize sentiment analyzer

        Args:
            method: Analysis method ('vader', 'textblob', 'hybrid')
        """
        self.method = method

        if method in ['vader', 'hybrid'] and VADER_AVAILABLE:
            self.vader = SentimentIntensityAnalyzer()
        else:
            self.vader = None

        if method in ['textblob', 'hybrid'] and TEXTBLOB_AVAILABLE:
            self.use_textblob = True
        else:
            self.use_textblob = False

    def analyze_text(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text

        Args:
            text: Text to analyze

        Returns:
            Dictionary with score, label, confidence
        """
        if not text or not text.strip():
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}

        cleaned_text = clean_text(text)

        if self.method == 'vader' and self.vader:
            return self._analyze_vader(cleaned_text)
        elif self.method == 'textblob' and self.use_textblob:
            return self._analyze_textblob(cleaned_text)
        elif self.method == 'hybrid':
            return self._analyze_hybrid(cleaned_text)
        else:
            # Fallback to simple keyword-based
            return self._analyze_simple(cleaned_text)

    def _analyze_vader(self, text: str) -> Dict[str, float]:
        """VADER sentiment analysis"""
        scores = self.vader.polarity_scores(text)
        compound = scores['compound']

        if compound >= 0.15:
            label = 'bullish'
        elif compound <= -0.15:
            label = 'bearish'
        else:
            label = 'neutral'

        confidence = abs(compound)

        return {
            'score': compound,
            'label': label,
            'confidence': confidence
        }

    def _analyze_textblob(self, text: str) -> Dict[str, float]:
        """TextBlob sentiment analysis"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1

        if polarity >= 0.15:
            label = 'bullish'
        elif polarity <= -0.15:
            label = 'bearish'
        else:
            label = 'neutral'

        confidence = abs(polarity)

        return {
            'score': polarity,
            'label': label,
            'confidence': confidence
        }

    def _analyze_hybrid(self, text: str) -> Dict[str, float]:
        """Hybrid analysis combining VADER and TextBlob"""
        vader_result = self._analyze_vader(text) if self.vader else {'score': 0}
        textblob_result = self._analyze_textblob(text) if self.use_textblob else {'score': 0}

        # Average the scores
        avg_score = (vader_result['score'] + textblob_result['score']) / 2

        if avg_score >= 0.15:
            label = 'bullish'
        elif avg_score <= -0.15:
            label = 'bearish'
        else:
            label = 'neutral'

        confidence = abs(avg_score)

        return {
            'score': avg_score,
            'label': label,
            'confidence': confidence
        }

    def _analyze_simple(self, text: str) -> Dict[str, float]:
        """Simple keyword-based sentiment"""
        bullish_words = ['buy', 'bull', 'calls', 'moon', 'rocket', 'gain', 'profit',
                        'up', 'rise', 'surge', 'rally', 'strong', 'bullish', 'long']
        bearish_words = ['sell', 'bear', 'puts', 'crash', 'loss', 'down', 'fall',
                        'drop', 'decline', 'weak', 'bearish', 'short']

        text_lower = text.lower()
        bullish_count = sum(1 for word in bullish_words if word in text_lower)
        bearish_count = sum(1 for word in bearish_words if word in text_lower)

        score = (bullish_count - bearish_count) / max(len(text.split()), 1)
        score = max(-1, min(1, score * 5))  # Normalize to -1 to 1

        if score >= 0.15:
            label = 'bullish'
        elif score <= -0.15:
            label = 'bearish'
        else:
            label = 'neutral'

        return {
            'score': score,
            'label': label,
            'confidence': abs(score)
        }

    def batch_analyze(self, posts: List[Dict]) -> List[Dict]:
        """Analyze sentiment for multiple posts

        Args:
            posts: List of post dictionaries

        Returns:
            Posts with added sentiment data
        """
        for post in posts:
            text = f"{post.get('title', '')} {post.get('text', '')}"
            sentiment = self.analyze_text(text)
            post['sentiment'] = sentiment
            post['weight'] = calculate_post_weight(
                post.get('upvotes', 0),
                post.get('num_comments', 0),
                post.get('awards', 0)
            )

        return posts

    def get_aggregate_sentiment(self, posts: List[Dict]) -> Dict:
        """Calculate aggregate sentiment metrics

        Args:
            posts: List of posts with sentiment data

        Returns:
            Aggregate sentiment metrics
        """
        if not posts:
            return {
                'avg_sentiment': 0.0,
                'weighted_sentiment': 0.0,
                'total_posts': 0,
                'bullish_count': 0,
                'neutral_count': 0,
                'bearish_count': 0,
                'total_engagement': 0
            }

        scores = [p['sentiment']['score'] for p in posts if 'sentiment' in p]
        weights = [p.get('weight', 1.0) for p in posts]

        avg_sentiment = sum(scores) / len(scores) if scores else 0.0
        weighted_sentiment = sum(s * w for s, w in zip(scores, weights)) / sum(weights) if weights else 0.0

        bullish = sum(1 for p in posts if p.get('sentiment', {}).get('label') == 'bullish')
        neutral = sum(1 for p in posts if p.get('sentiment', {}).get('label') == 'neutral')
        bearish = sum(1 for p in posts if p.get('sentiment', {}).get('label') == 'bearish')

        total_engagement = sum(
            p.get('upvotes', 0) + p.get('num_comments', 0)
            for p in posts
        )

        return {
            'avg_sentiment': avg_sentiment,
            'weighted_sentiment': weighted_sentiment,
            'total_posts': len(posts),
            'bullish_count': bullish,
            'neutral_count': neutral,
            'bearish_count': bearish,
            'total_engagement': total_engagement
        }


# Utility functions

def clean_text(text: str) -> str:
    """Clean text for sentiment analysis"""
    if not text:
        return ""

    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove markdown formatting
    text = re.sub(r'[*_~`]', '', text)

    return text.strip()


def calculate_post_weight(upvotes: int, comments: int, awards: int) -> float:
    """Calculate engagement weight for a post

    Weight formula: log(1 + upvotes + 2*comments + 10*awards)
    """
    import math

    engagement = upvotes + (2 * comments) + (10 * awards)
    weight = math.log(1 + engagement) / 10  # Normalize

    return min(weight, 1.0)  # Cap at 1.0


def get_sentiment_emoji(score: float) -> str:
    """Get emoji for sentiment score"""
    if score >= 0.15:
        return '🟢'
    elif score <= -0.15:
        return '🔴'
    else:
        return '⚪'


def get_sentiment_color(score: float) -> str:
    """Get color for sentiment score"""
    if score >= 0.15:
        return '#10b981'  # Green
    elif score <= -0.15:
        return '#ef4444'  # Red
    else:
        return '#6b7280'  # Gray


def get_sentiment_label(score: float) -> str:
    """Get label for sentiment score"""
    if score >= 0.15:
        return 'Bullish'
    elif score <= -0.15:
        return 'Bearish'
    else:
        return 'Neutral'


def format_timeago(timestamp: float) -> str:
    """Format timestamp as time ago"""
    now = datetime.now()
    post_time = datetime.fromtimestamp(timestamp)
    diff = now - post_time

    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours}h ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes}m ago"
    else:
        return "just now"
