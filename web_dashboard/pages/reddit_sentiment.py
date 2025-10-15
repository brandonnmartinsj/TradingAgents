"""Reddit Sentiment Analysis Page"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from collections import Counter
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.reddit_sentiment_utils import (
    RedditClient,
    SentimentAnalyzer,
    get_sentiment_emoji,
    get_sentiment_color,
    get_sentiment_label,
    format_timeago
)


def load_settings():
    """Load settings from settings.json"""
    settings_file = Path(__file__).parent.parent / "settings.json"
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def create_sentiment_timeline_chart(posts):
    """Create sentiment timeline chart"""
    if not posts:
        return None

    # Group by hour
    df = pd.DataFrame(posts)
    df['datetime'] = pd.to_datetime(df['created_utc'], unit='s')
    df['hour'] = df['datetime'].dt.floor('H')

    # Calculate average sentiment per hour
    hourly = df.groupby('hour').agg({
        'sentiment': lambda x: sum(s['score'] for s in x) / len(x),
        'id': 'count'
    }).reset_index()

    hourly.columns = ['hour', 'avg_sentiment', 'post_count']

    fig = go.Figure()

    # Sentiment line
    fig.add_trace(go.Scatter(
        x=hourly['hour'],
        y=hourly['avg_sentiment'],
        mode='lines+markers',
        name='Sentiment Score',
        line=dict(color='rgb(75, 192, 192)', width=3),
        marker=dict(size=8)
    ))

    # Volume bars
    fig.add_trace(go.Bar(
        x=hourly['hour'],
        y=hourly['post_count'],
        name='Post Volume',
        yaxis='y2',
        opacity=0.3,
        marker_color='rgb(100, 100, 100)'
    ))

    fig.update_layout(
        title='Reddit Sentiment Timeline',
        xaxis=dict(title='Time'),
        yaxis=dict(title='Sentiment Score', range=[-1, 1]),
        yaxis2=dict(
            title='Post Volume',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )

    return fig


def create_sentiment_distribution_chart(posts):
    """Create sentiment distribution pie chart"""
    if not posts:
        return None

    bullish = sum(1 for p in posts if p.get('sentiment', {}).get('label') == 'bullish')
    neutral = sum(1 for p in posts if p.get('sentiment', {}).get('label') == 'neutral')
    bearish = sum(1 for p in posts if p.get('sentiment', {}).get('label') == 'bearish')

    fig = go.Figure(data=[go.Pie(
        labels=['🟢 Bullish', '⚪ Neutral', '🔴 Bearish'],
        values=[bullish, neutral, bearish],
        marker=dict(colors=['#10b981', '#6b7280', '#ef4444']),
        hole=0.3
    )])

    fig.update_layout(
        title='Sentiment Distribution',
        template='plotly_white',
        height=350
    )

    return fig


def create_engagement_chart(posts):
    """Create engagement vs sentiment scatter plot"""
    if not posts:
        return None

    df = pd.DataFrame([{
        'engagement': p.get('upvotes', 0) + p.get('num_comments', 0),
        'sentiment': p.get('sentiment', {}).get('score', 0),
        'title': p.get('title', '')[:50] + '...',
        'upvotes': p.get('upvotes', 0),
        'comments': p.get('num_comments', 0)
    } for p in posts])

    fig = px.scatter(
        df,
        x='engagement',
        y='sentiment',
        hover_data=['title', 'upvotes', 'comments'],
        color='sentiment',
        color_continuous_scale=['#ef4444', '#6b7280', '#10b981'],
        color_continuous_midpoint=0,
        title='Post Engagement vs Sentiment'
    )

    fig.update_layout(
        xaxis_title='Total Engagement (Upvotes + Comments)',
        yaxis_title='Sentiment Score',
        template='plotly_white',
        height=400
    )

    return fig


def create_subreddit_comparison_chart(posts):
    """Create subreddit comparison chart"""
    if not posts:
        return None

    # Group by subreddit
    subreddit_data = {}
    for post in posts:
        sub = post.get('subreddit', 'unknown')
        if sub not in subreddit_data:
            subreddit_data[sub] = {'scores': [], 'count': 0}

        subreddit_data[sub]['scores'].append(post.get('sentiment', {}).get('score', 0))
        subreddit_data[sub]['count'] += 1

    subreddits = list(subreddit_data.keys())
    avg_sentiments = [sum(data['scores']) / len(data['scores']) for data in subreddit_data.values()]
    post_counts = [data['count'] for data in subreddit_data.values()]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=subreddits,
        y=avg_sentiments,
        name='Avg Sentiment',
        marker_color=['#10b981' if s > 0.15 else '#ef4444' if s < -0.15 else '#6b7280'
                     for s in avg_sentiments],
        text=[f"{s:+.2f}" for s in avg_sentiments],
        textposition='auto'
    ))

    fig.update_layout(
        title='Sentiment by Subreddit',
        xaxis_title='Subreddit',
        yaxis_title='Average Sentiment Score',
        template='plotly_white',
        height=350,
        yaxis=dict(range=[-1, 1])
    )

    return fig


def render_post_card(post):
    """Render a Reddit post card"""
    sentiment = post.get('sentiment', {})
    score = sentiment.get('score', 0)
    label = sentiment.get('label', 'neutral')
    emoji = get_sentiment_emoji(score)
    color = get_sentiment_color(score)

    timeago = format_timeago(post.get('created_utc', 0))

    card_html = f'''
    <div style="border-left: 4px solid {color}; padding: 16px; margin-bottom: 16px;
                background: #f8fafc; border-radius: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                    <span style="font-size: 12px; font-weight: 600; color: #64748b;">
                        r/{post.get('subreddit', 'unknown')}
                    </span>
                    <span style="font-size: 12px; color: #94a3b8;">•</span>
                    <span style="font-size: 12px; color: #94a3b8;">u/{post.get('author', 'unknown')}</span>
                    <span style="font-size: 12px; color: #94a3b8;">•</span>
                    <span style="font-size: 12px; color: #94a3b8;">{timeago}</span>
                </div>
                <h4 style="margin: 0; font-size: 16px; font-weight: 600; color: #1e293b;">
                    {post.get('title', 'No title')}
                </h4>
            </div>
            <span style="font-size: 24px; margin-left: 12px;">{emoji}</span>
        </div>
        <div style="display: flex; gap: 16px; margin-top: 8px;">
            <span style="font-size: 13px; color: #64748b;">
                ⬆ {post.get('upvotes', 0):,}
            </span>
            <span style="font-size: 13px; color: #64748b;">
                💬 {post.get('num_comments', 0):,}
            </span>
            <span style="font-size: 13px; color: {color}; font-weight: 600;">
                {label.capitalize()}: {score:+.2f}
            </span>
        </div>
    </div>
    '''

    st.markdown(card_html, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 5])
    with col1:
        st.link_button("View Post", post.get('url', '#'), use_container_width=True)


def render(loader):
    """Render Reddit Sentiment Analysis page"""

    st.markdown('<p class="main-header">🤖 Reddit Sentiment Analysis</p>', unsafe_allow_html=True)
    st.markdown("Real-time sentiment analysis from Reddit discussions")

    # Load settings
    settings = load_settings()
    reddit_settings = settings.get('reddit', {})
    api_keys = settings.get('api_keys', {})

    # Check if Reddit is configured
    reddit_client_id = api_keys.get('reddit_client_id')
    reddit_client_secret = api_keys.get('reddit_client_secret')

    if not reddit_client_id or not reddit_client_secret:
        st.warning("⚠️ Reddit API not configured. Please add your Reddit API credentials in Settings page.")
        st.info("💡 Go to Settings → API Keys to configure your Reddit credentials.")
        st.markdown("---")
        st.markdown("""
        ### How to get Reddit API credentials:
        1. Go to https://www.reddit.com/prefs/apps
        2. Click "create another app..." or "create app"
        3. Fill in:
           - **name**: TradingAgents
           - **App type**: script
           - **description**: Real-time sentiment analysis
           - **redirect uri**: http://localhost:8080
        4. Copy your **client_id** and **client_secret**
        5. Add them to Settings page
        """)
        return

    # Initialize clients
    reddit_client = RedditClient(
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        user_agent=api_keys.get('reddit_user_agent', 'TradingAgents/1.0')
    )

    sentiment_analyzer = SentimentAnalyzer(
        method=reddit_settings.get('sentiment_method', 'vader')
    )

    # Sidebar controls
    st.sidebar.markdown("### 🎛️ Controls")

    # Get available tickers from results + popular tickers
    results_tickers = loader.get_available_tickers()

    # Popular tickers commonly discussed on Reddit
    popular_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA',
        'AMD', 'INTC', 'NFLX', 'DIS', 'AVGO', 'JPM', 'V', 'MA',
        'WMT', 'BAC', 'COIN', 'PLTR', 'GME', 'AMC', 'BB', 'BBBY',
        'SPY', 'QQQ', 'SOFI', 'RIVN', 'LCID', 'NIO', 'BABA',
        'PETR4.SA', 'VALE3', 'ITUB4', 'BBDC4'  # Brazilian stocks
    ]

    # Combine and deduplicate
    all_tickers = list(set(results_tickers + popular_tickers))
    all_tickers.sort()

    if not all_tickers:
        all_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']

    # Ticker selection with custom input option
    ticker_input_method = st.sidebar.radio(
        "Ticker Selection",
        ["Select from List", "Enter Custom Ticker"],
        horizontal=True
    )

    if ticker_input_method == "Select from List":
        selected_ticker = st.sidebar.selectbox(
            "Select Ticker",
            all_tickers,
            index=all_tickers.index('AAPL') if 'AAPL' in all_tickers else 0
        )
    else:
        selected_ticker = st.sidebar.text_input(
            "Enter Ticker Symbol",
            value="AAPL",
            max_chars=10,
            help="Enter any ticker symbol (e.g., AAPL, TSLA, GME)"
        ).upper().strip()

        if not selected_ticker:
            st.sidebar.warning("Please enter a ticker symbol")
            return

    time_filters = {
        'Past Hour': 'hour',
        'Past 24 Hours': 'day',
        'Past Week': 'week',
        'Past Month': 'month'
    }
    time_filter_label = st.sidebar.selectbox("Time Range", list(time_filters.keys()), index=1)
    time_filter = time_filters[time_filter_label]

    default_subreddits = reddit_settings.get('subreddits', ['wallstreetbets', 'stocks', 'investing'])
    available_subreddits = {
        'r/wallstreetbets': 'wallstreetbets',
        'r/stocks': 'stocks',
        'r/investing': 'investing',
        'r/StockMarket': 'StockMarket',
        'r/options': 'options'
    }

    selected_subreddits = st.sidebar.multiselect(
        "Subreddits",
        list(available_subreddits.keys()),
        default=[f"r/{sub}" for sub in default_subreddits if f"r/{sub}" in available_subreddits.keys()]
    )

    subreddits = [available_subreddits[sub] for sub in selected_subreddits]

    posts_limit = st.sidebar.slider("Posts per Subreddit", 10, 100, 50, 10)

    refresh_button = st.sidebar.button("🔄 Refresh Data", use_container_width=True)

    st.markdown("---")

    # Fetch and analyze posts
    if not subreddits:
        st.warning("Please select at least one subreddit")
        return

    with st.spinner(f"Fetching Reddit posts about ${selected_ticker}..."):
        posts = reddit_client.fetch_posts(
            ticker=selected_ticker,
            subreddits=subreddits,
            limit=posts_limit,
            time_filter=time_filter
        )

        if posts:
            posts = sentiment_analyzer.batch_analyze(posts)

    if not posts:
        st.info(f"No Reddit posts found for ${selected_ticker} in selected subreddits and time range.")
        st.markdown("Try:")
        st.markdown("- Expanding the time range")
        st.markdown("- Adding more subreddits")
        st.markdown("- Trying a different ticker")
        return

    # Calculate aggregate metrics
    aggregate = sentiment_analyzer.get_aggregate_sentiment(posts)

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_sent = aggregate['weighted_sentiment']
        emoji = get_sentiment_emoji(avg_sent)
        st.metric(
            "Average Sentiment",
            f"{emoji} {avg_sent:+.3f}",
            delta=get_sentiment_label(avg_sent)
        )

    with col2:
        st.metric("Total Posts", f"{aggregate['total_posts']:,}")

    with col3:
        bullish_pct = (aggregate['bullish_count'] / aggregate['total_posts'] * 100) if aggregate['total_posts'] > 0 else 0
        st.metric("Bullish %", f"{bullish_pct:.1f}%", delta=f"{aggregate['bullish_count']} posts")

    with col4:
        st.metric("Total Engagement", f"{aggregate['total_engagement']:,}")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "💬 Posts", "🔥 Analysis", "📊 Statistics"])

    with tab1:
        st.markdown(f"### Sentiment Timeline for ${selected_ticker}")

        # Timeline chart
        timeline_chart = create_sentiment_timeline_chart(posts)
        if timeline_chart:
            st.plotly_chart(timeline_chart, use_container_width=True)

        # Distribution
        col1, col2 = st.columns(2)

        with col1:
            dist_chart = create_sentiment_distribution_chart(posts)
            if dist_chart:
                st.plotly_chart(dist_chart, use_container_width=True)

        with col2:
            # Sentiment breakdown
            st.markdown("### Sentiment Breakdown")
            st.markdown(f"**🟢 Bullish**: {aggregate['bullish_count']} posts ({aggregate['bullish_count']/aggregate['total_posts']*100:.1f}%)")
            st.markdown(f"**⚪ Neutral**: {aggregate['neutral_count']} posts ({aggregate['neutral_count']/aggregate['total_posts']*100:.1f}%)")
            st.markdown(f"**🔴 Bearish**: {aggregate['bearish_count']} posts ({aggregate['bearish_count']/aggregate['total_posts']*100:.1f}%)")

            st.markdown("### Top Subreddits")
            subreddit_counts = Counter(p['subreddit'] for p in posts)
            for sub, count in subreddit_counts.most_common(5):
                st.markdown(f"**r/{sub}**: {count} posts")

    with tab2:
        st.markdown(f"### Reddit Posts about ${selected_ticker}")

        # Filter controls
        col1, col2 = st.columns([3, 1])

        with col1:
            sentiment_filter = st.selectbox(
                "Filter by Sentiment",
                ["All", "🟢 Bullish", "⚪ Neutral", "🔴 Bearish"]
            )

        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Recent", "Top", "Engagement"]
            )

        # Filter posts
        filtered_posts = posts.copy()

        if sentiment_filter != "All":
            filter_map = {
                "🟢 Bullish": "bullish",
                "⚪ Neutral": "neutral",
                "🔴 Bearish": "bearish"
            }
            target_label = filter_map[sentiment_filter]
            filtered_posts = [p for p in filtered_posts if p.get('sentiment', {}).get('label') == target_label]

        # Sort posts
        if sort_by == "Recent":
            filtered_posts.sort(key=lambda x: x.get('created_utc', 0), reverse=True)
        elif sort_by == "Top":
            filtered_posts.sort(key=lambda x: x.get('upvotes', 0), reverse=True)
        elif sort_by == "Engagement":
            filtered_posts.sort(
                key=lambda x: x.get('upvotes', 0) + x.get('num_comments', 0),
                reverse=True
            )

        st.markdown(f"**Showing {len(filtered_posts)} posts**")
        st.markdown("---")

        # Display posts
        for post in filtered_posts[:20]:  # Limit to 20 posts
            render_post_card(post)

    with tab3:
        st.markdown(f"### Detailed Analysis for ${selected_ticker}")

        # Engagement vs Sentiment
        engagement_chart = create_engagement_chart(posts)
        if engagement_chart:
            st.plotly_chart(engagement_chart, use_container_width=True)

        # Subreddit comparison
        subreddit_chart = create_subreddit_comparison_chart(posts)
        if subreddit_chart:
            st.plotly_chart(subreddit_chart, use_container_width=True)

        # Top keywords
        st.markdown("### 🔑 Most Common Keywords")
        all_text = ' '.join([f"{p.get('title', '')} {p.get('text', '')}" for p in posts])
        words = all_text.lower().split()

        # Filter out common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                    'of', 'is', 'it', 'that', 'this', 'was', 'are', 'been', 'be', 'have',
                    'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}

        filtered_words = [w for w in words if len(w) > 3 and w not in stopwords and not w.isdigit()]
        word_counts = Counter(filtered_words)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Top 10 Keywords:**")
            for word, count in word_counts.most_common(10):
                st.markdown(f"- **{word}**: {count} mentions")

        with col2:
            # Most engaged posts
            st.markdown("**Most Engaged Posts:**")
            top_engaged = sorted(posts, key=lambda x: x.get('upvotes', 0) + x.get('num_comments', 0), reverse=True)[:3]
            for i, post in enumerate(top_engaged, 1):
                engagement = post.get('upvotes', 0) + post.get('num_comments', 0)
                sentiment = post.get('sentiment', {}).get('score', 0)
                emoji = get_sentiment_emoji(sentiment)
                st.markdown(f"{i}. {emoji} [{post.get('title', '')[:40]}...]({post.get('url', '#')}) - {engagement:,} engagement")

    with tab4:
        st.markdown(f"### Statistics for ${selected_ticker}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Sentiment Metrics")
            st.markdown(f"**Average Score**: {aggregate['avg_sentiment']:+.3f}")
            st.markdown(f"**Weighted Score**: {aggregate['weighted_sentiment']:+.3f}")
            st.markdown(f"**Std Deviation**: {pd.Series([p['sentiment']['score'] for p in posts]).std():.3f}")
            st.markdown(f"**Median Score**: {pd.Series([p['sentiment']['score'] for p in posts]).median():+.3f}")

        with col2:
            st.markdown("#### Engagement Metrics")
            st.markdown(f"**Total Upvotes**: {sum(p.get('upvotes', 0) for p in posts):,}")
            st.markdown(f"**Total Comments**: {sum(p.get('num_comments', 0) for p in posts):,}")
            st.markdown(f"**Avg Upvotes/Post**: {sum(p.get('upvotes', 0) for p in posts) / len(posts):.1f}")
            st.markdown(f"**Avg Comments/Post**: {sum(p.get('num_comments', 0) for p in posts) / len(posts):.1f}")

        # Export data
        st.markdown("---")
        st.markdown("### 📥 Export Data")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Export as CSV", use_container_width=True):
                df = pd.DataFrame([{
                    'ticker': p.get('ticker'),
                    'subreddit': p.get('subreddit'),
                    'title': p.get('title'),
                    'url': p.get('url'),
                    'upvotes': p.get('upvotes'),
                    'comments': p.get('num_comments'),
                    'sentiment_score': p.get('sentiment', {}).get('score'),
                    'sentiment_label': p.get('sentiment', {}).get('label'),
                    'created_utc': p.get('created_utc')
                } for p in posts])

                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    f"{selected_ticker}_reddit_sentiment.csv",
                    "text/csv"
                )

        with col2:
            if st.button("Export as JSON", use_container_width=True):
                import json
                json_data = json.dumps(posts, indent=2)
                st.download_button(
                    "Download JSON",
                    json_data,
                    f"{selected_ticker}_reddit_sentiment.json",
                    "application/json"
                )

        with col3:
            if st.button("Export Summary", use_container_width=True):
                summary = f"""
# Reddit Sentiment Summary: ${selected_ticker}

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Time Range**: {time_filter_label}
**Subreddits**: {', '.join(subreddits)}

## Aggregate Metrics
- **Average Sentiment**: {aggregate['avg_sentiment']:+.3f}
- **Weighted Sentiment**: {aggregate['weighted_sentiment']:+.3f}
- **Total Posts**: {aggregate['total_posts']}
- **Bullish**: {aggregate['bullish_count']} ({aggregate['bullish_count']/aggregate['total_posts']*100:.1f}%)
- **Neutral**: {aggregate['neutral_count']} ({aggregate['neutral_count']/aggregate['total_posts']*100:.1f}%)
- **Bearish**: {aggregate['bearish_count']} ({aggregate['bearish_count']/aggregate['total_posts']*100:.1f}%)
- **Total Engagement**: {aggregate['total_engagement']:,}
"""
                st.download_button(
                    "Download Summary",
                    summary,
                    f"{selected_ticker}_reddit_summary.md",
                    "text/markdown"
                )
