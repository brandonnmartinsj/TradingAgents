"""Main dashboard page"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict
import yfinance as yf
from datetime import datetime, timedelta


def render_decision_badge(decision: str):
    """Render a decision badge with appropriate styling"""
    if not decision:
        return st.info("No decision found")

    color_map = {
        "BUY": "🟢",
        "HOLD": "🟡",
        "SELL": "🔴"
    }

    icon = color_map.get(decision, "⚪")
    st.markdown(f"## {icon} {decision}")


def fetch_stock_data(ticker: str, period: str = "1mo"):
    """Fetch real-time stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        info = stock.info
        return hist, info
    except Exception:
        return None, None


def create_price_chart(hist_data, ticker: str):
    """Create interactive price chart with Plotly"""
    if hist_data is None or hist_data.empty:
        return None

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=hist_data.index,
        open=hist_data['Open'],
        high=hist_data['High'],
        low=hist_data['Low'],
        close=hist_data['Close'],
        name='OHLC'
    ))

    fig.update_layout(
        title=f'{ticker} Stock Price',
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        template='plotly_white',
        height=500,
        xaxis_rangeslider_visible=False
    )

    return fig


def create_volume_chart(hist_data, ticker: str):
    """Create volume chart"""
    if hist_data is None or hist_data.empty:
        return None

    colors = ['red' if row['Close'] < row['Open'] else 'green'
              for _, row in hist_data.iterrows()]

    fig = go.Figure(data=[go.Bar(
        x=hist_data.index,
        y=hist_data['Volume'],
        marker_color=colors
    )])

    fig.update_layout(
        title=f'{ticker} Trading Volume',
        yaxis_title='Volume',
        xaxis_title='Date',
        template='plotly_white',
        height=300
    )

    return fig


def create_technical_indicators_chart(indicators: Dict[str, str], ticker: str):
    """Create chart showing technical indicators"""
    if not indicators:
        return None

    indicator_names = list(indicators.keys())
    values = []

    for val in indicators.values():
        try:
            clean_val = val.replace(',', '').strip()
            values.append(float(clean_val))
        except (ValueError, AttributeError):
            values.append(0)

    fig = go.Figure(data=[
        go.Bar(
            x=indicator_names,
            y=values,
            text=[f'{v:.2f}' for v in values],
            textposition='auto',
            marker_color='lightblue'
        )
    ])

    fig.update_layout(
        title=f'{ticker} Technical Indicators',
        yaxis_title='Value',
        template='plotly_white',
        height=400,
        xaxis_tickangle=-45
    )

    return fig


def render(loader):
    """Render the main dashboard page"""

    st.markdown('<p class="main-header">TradingAgents Dashboard</p>', unsafe_allow_html=True)
    st.markdown("### Multi-Agent Trading Analysis Results")

    # Get all tickers
    tickers = loader.get_available_tickers()

    if not tickers:
        st.warning("No trading data available. Run TradingAgents to generate reports.")
        return

    st.markdown(f"**Total Tickers Analyzed:** {len(tickers)}")

    # Get summary for all tickers
    summaries = []
    for ticker in tickers:
        summary = loader.get_ticker_summary(ticker)
        if summary['total_analyses'] > 0:
            summaries.append(summary)

    # Display ticker cards
    st.markdown("---")
    st.markdown("### 📊 Latest Trading Decisions")

    cols = st.columns(3)

    for idx, summary in enumerate(summaries):
        col_idx = idx % 3
        with cols[col_idx]:
            with st.container():
                st.markdown(f"#### {summary['ticker']}")

                decision = summary['latest_decision']
                if decision:
                    color_class = f"decision-{decision.lower()}"
                    st.markdown(
                        f'<div class="decision-badge {color_class}">{decision}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown('<div class="decision-badge">N/A</div>', unsafe_allow_html=True)

                st.caption(f"Latest: {summary['latest_date']}")
                st.caption(f"Total Analyses: {summary['total_analyses']}")

    st.markdown("---")
    st.markdown("### 📈 Detailed Analysis")

    selected_ticker = st.selectbox("Select Ticker for Detailed View", tickers)

    if selected_ticker:
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Charts", "📉 Technical Indicators", "📰 News", "📋 Fundamentals"])

        latest_date = loader.get_latest_date(selected_ticker)

        with tab1:
            st.subheader(f"Real-Time Price Data for {selected_ticker}")

            with st.spinner("Fetching real-time data..."):
                hist_data, stock_info = fetch_stock_data(selected_ticker, period="1mo")

            if hist_data is not None and not hist_data.empty:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Current Price", f"${hist_data['Close'].iloc[-1]:.2f}",
                             delta=f"{((hist_data['Close'].iloc[-1] / hist_data['Close'].iloc[0] - 1) * 100):.2f}%")
                with col2:
                    st.metric("High (1M)", f"${hist_data['High'].max():.2f}")
                with col3:
                    st.metric("Low (1M)", f"${hist_data['Low'].min():.2f}")
                with col4:
                    st.metric("Avg Volume", f"{hist_data['Volume'].mean()/1e6:.2f}M")

                price_chart = create_price_chart(hist_data, selected_ticker)
                if price_chart:
                    st.plotly_chart(price_chart, use_container_width=True)

                volume_chart = create_volume_chart(hist_data, selected_ticker)
                if volume_chart:
                    st.plotly_chart(volume_chart, use_container_width=True)

            else:
                st.warning("Unable to fetch real-time data. Ticker might not be available on Yahoo Finance.")

            history = loader.get_decision_history(selected_ticker)
            if history:
                st.subheader("Decision History")
                df = pd.DataFrame(history)

                decision_counts = df['decision'].value_counts()
                fig = px.pie(
                    values=decision_counts.values,
                    names=decision_counts.index,
                    title=f'{selected_ticker} Decision Distribution',
                    color_discrete_map={'BUY': 'green', 'HOLD': 'orange', 'SELL': 'red'}
                )
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(df, use_container_width=True, hide_index=True)

        with tab2:
            st.subheader(f"Technical Indicators for {selected_ticker}")

            if latest_date:
                market_report = loader.read_report(selected_ticker, latest_date, "market_report")
                if market_report:
                    indicators = loader.extract_technical_indicators(market_report)

                    if indicators:
                        col1, col2, col3 = st.columns(3)

                        indicator_items = list(indicators.items())
                        for i, (name, value) in enumerate(indicator_items):
                            with [col1, col2, col3][i % 3]:
                                st.metric(name, value)

                        tech_chart = create_technical_indicators_chart(indicators, selected_ticker)
                        if tech_chart:
                            st.plotly_chart(tech_chart, use_container_width=True)
                    else:
                        st.info("No technical indicators found in the report.")
                else:
                    st.warning("Market report not available.")

        with tab3:
            st.subheader(f"News Sources for {selected_ticker}")

            if latest_date:
                news_report = loader.read_report(selected_ticker, latest_date, "news_report")
                if news_report:
                    news_sources = loader.extract_news_sources(news_report)

                    if news_sources:
                        for news in news_sources:
                            with st.expander(f"📰 {news['topic']}", expanded=False):
                                st.markdown(f"**Details:** {news['details']}")
                                st.markdown(f"**Source:** [{news['source_name']}]({news['source_url']})")
                                st.link_button("Read Full Article", news['source_url'])
                    else:
                        st.info("No news sources found in the report.")
                else:
                    st.warning("News report not available.")

        with tab4:
            st.subheader(f"Fundamental Metrics for {selected_ticker}")

            if latest_date:
                fundamentals_report = loader.read_report(selected_ticker, latest_date, "fundamentals_report")
                if fundamentals_report:
                    metrics = loader.extract_financial_metrics(fundamentals_report)

                    if metrics:
                        cols = st.columns(3)
                        for i, (name, value) in enumerate(metrics.items()):
                            with cols[i % 3]:
                                st.metric(name, value)
                    else:
                        st.info("No financial metrics found in the report.")

                    decision = loader.extract_decision(fundamentals_report)
                    if decision:
                        st.markdown("---")
                        st.markdown("### Fundamentals Analysis Decision")
                        render_decision_badge(decision)
                else:
                    st.warning("Fundamentals report not available.")
