"""Comparison page"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.export_utils import prepare_export_data


def create_price_comparison_chart(tickers: list, period: str = "1mo"):
    """Create overlaid price comparison chart"""
    fig = go.Figure()

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            if not hist.empty:
                normalized = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100

                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=normalized,
                    mode='lines',
                    name=ticker,
                    line=dict(width=2)
                ))
        except Exception:
            continue

    fig.update_layout(
        title='Normalized Price Comparison (% Change)',
        xaxis_title='Date',
        yaxis_title='Change (%)',
        template='plotly_white',
        height=500,
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    return fig


def create_volume_comparison_chart(tickers: list, period: str = "1mo"):
    """Create volume comparison chart"""
    fig = go.Figure()

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            if not hist.empty:
                fig.add_trace(go.Bar(
                    x=hist.index,
                    y=hist['Volume'],
                    name=ticker,
                    opacity=0.7
                ))
        except Exception:
            continue

    fig.update_layout(
        title='Trading Volume Comparison',
        xaxis_title='Date',
        yaxis_title='Volume',
        template='plotly_white',
        height=400,
        barmode='group',
        hovermode='x unified'
    )

    return fig


def create_returns_heatmap(tickers: list, period: str = "1mo"):
    """Create returns correlation heatmap"""
    returns_df = pd.DataFrame()

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            if not hist.empty:
                returns_df[ticker] = hist['Close'].pct_change()
        except Exception:
            continue

    if returns_df.empty or len(returns_df.columns) < 2:
        return None

    corr_matrix = returns_df.corr()

    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        aspect="auto",
        color_continuous_scale='RdYlGn',
        title='Returns Correlation Matrix'
    )

    fig.update_layout(
        height=400
    )

    return fig


def render(loader):
    """Render the comparison page"""

    st.markdown('<p class="main-header">Multi-Ticker Comparison</p>', unsafe_allow_html=True)
    st.markdown("### Compare trading decisions and real-time market data across multiple tickers")

    tickers = loader.get_available_tickers()

    if not tickers:
        st.warning("No data available for comparison.")
        return

    selected_tickers = st.multiselect(
        "Select Tickers to Compare",
        tickers,
        default=tickers[:min(3, len(tickers))]
    )

    if not selected_tickers:
        st.info("Please select at least one ticker.")
        return

    tab1, tab2, tab3 = st.tabs(["📊 Decision Comparison", "📈 Price Comparison", "📉 Market Analysis"])

    with tab1:
        comparison_data = []

        for ticker in selected_tickers:
            summary = loader.get_ticker_summary(ticker)
            if summary['total_analyses'] > 0:
                comparison_data.append({
                    "Ticker": ticker,
                    "Latest Date": summary['latest_date'],
                    "Latest Decision": summary['latest_decision'] or "N/A",
                    "Total Analyses": summary['total_analyses']
                })

        if comparison_data:
            df = pd.DataFrame(comparison_data)

            st.subheader("Summary Table")
            st.dataframe(df, use_container_width=True, hide_index=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Decision Distribution")
                decision_counts = df['Latest Decision'].value_counts()

                fig = px.pie(
                    values=decision_counts.values,
                    names=decision_counts.index,
                    color_discrete_map={'BUY': 'green', 'HOLD': 'orange', 'SELL': 'red', 'N/A': 'gray'}
                )

                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("### Total Analyses by Ticker")

                fig = go.Figure(data=[
                    go.Bar(
                        x=df['Ticker'],
                        y=df['Total Analyses'],
                        marker_color='lightblue',
                        text=df['Total Analyses'],
                        textposition='outside'
                    )
                ])

                fig.update_layout(
                    yaxis_title='Number of Analyses',
                    template='plotly_white',
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.subheader("Decision History Comparison")

            all_decisions = []

            for ticker in selected_tickers:
                decisions = loader.get_decision_history(ticker)
                for decision in decisions:
                    all_decisions.append({
                        'Ticker': ticker,
                        'Date': decision['date'],
                        'Decision': decision['decision']
                    })

            if all_decisions:
                decisions_df = pd.DataFrame(all_decisions)
                decisions_df['Date'] = pd.to_datetime(decisions_df['Date'])

                fig = px.scatter(
                    decisions_df,
                    x='Date',
                    y='Ticker',
                    color='Decision',
                    color_discrete_map={'BUY': 'green', 'HOLD': 'orange', 'SELL': 'red'},
                    title='Decision Timeline by Ticker',
                    size_max=15
                )

                fig.update_traces(marker=dict(size=12))
                fig.update_layout(height=400, template='plotly_white')

                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            export_formats = prepare_export_data('comparison', {
                'data': comparison_data,
                'tickers': selected_tickers
            })

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if export_formats.get('csv'):
                    st.download_button(
                        label="📥 Export CSV",
                        data=export_formats['csv'],
                        file_name=f"comparison_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

            with col2:
                if export_formats.get('json'):
                    st.download_button(
                        label="📥 Export JSON",
                        data=export_formats['json'],
                        file_name=f"comparison_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json"
                    )

            with col3:
                if export_formats.get('excel'):
                    st.download_button(
                        label="📥 Export Excel",
                        data=export_formats['excel'],
                        file_name=f"comparison_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            with col4:
                if export_formats.get('report'):
                    st.download_button(
                        label="📥 Export Report",
                        data=export_formats['report'],
                        file_name=f"comparison_report_{datetime.now().strftime('%Y%m%d')}.md",
                        mime="text/markdown"
                    )
        else:
            st.info("No data available for selected tickers.")

    with tab2:
        st.subheader("Real-Time Price Comparison")

        period = st.selectbox(
            "Time Period",
            ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"],
            index=2
        )

        with st.spinner("Fetching real-time data..."):
            price_chart = create_price_comparison_chart(selected_tickers, period)

            if price_chart:
                st.plotly_chart(price_chart, use_container_width=True)

            st.markdown("---")
            st.subheader("Current Metrics")

            metrics_data = []

            for ticker in selected_tickers:
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    hist = stock.history(period=period)

                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        change = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100

                        metrics_data.append({
                            'Ticker': ticker,
                            'Current Price': f"${current_price:.2f}",
                            'Change': f"{change:+.2f}%",
                            'Volume': f"{hist['Volume'].iloc[-1] / 1e6:.2f}M",
                            'Market Cap': f"${info.get('marketCap', 0) / 1e9:.2f}B"
                        })
                except Exception:
                    continue

            if metrics_data:
                metrics_df = pd.DataFrame(metrics_data)
                st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Market Analysis & Correlations")

        with st.spinner("Analyzing market data..."):
            col1, col2 = st.columns(2)

            with col1:
                volume_chart = create_volume_comparison_chart(selected_tickers, period)
                if volume_chart:
                    st.plotly_chart(volume_chart, use_container_width=True)

            with col2:
                heatmap = create_returns_heatmap(selected_tickers, period)
                if heatmap:
                    st.plotly_chart(heatmap, use_container_width=True)
                else:
                    st.info("Need at least 2 tickers with data for correlation analysis")

            st.markdown("---")
            st.subheader("Volatility Comparison")

            volatility_data = []

            for ticker in selected_tickers:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period=period)

                    if not hist.empty:
                        daily_returns = hist['Close'].pct_change().dropna()
                        volatility = daily_returns.std() * (252 ** 0.5) * 100

                        volatility_data.append({
                            'Ticker': ticker,
                            'Volatility': volatility
                        })
                except Exception:
                    continue

            if volatility_data:
                vol_df = pd.DataFrame(volatility_data)

                fig = go.Figure(data=[
                    go.Bar(
                        x=vol_df['Ticker'],
                        y=vol_df['Volatility'],
                        text=[f"{v:.2f}%" for v in vol_df['Volatility']],
                        textposition='outside',
                        marker_color='coral'
                    )
                ])

                fig.update_layout(
                    title='Annualized Volatility Comparison',
                    xaxis_title='Ticker',
                    yaxis_title='Volatility (%)',
                    template='plotly_white',
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)
