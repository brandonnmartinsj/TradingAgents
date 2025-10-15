"""Historical performance analytics and backtesting"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List
import yfinance as yf


def simulate_backtest(ticker: str, decisions_history: List[Dict], initial_capital: float = 10000):
    """Simulate trading based on historical decisions"""
    portfolio_value = initial_capital
    cash = initial_capital
    shares = 0
    trades = []
    portfolio_history = []

    stock = yf.Ticker(ticker)
    price_history = stock.history(period="1y")

    for decision_record in sorted(decisions_history, key=lambda x: x['date']):
        date = decision_record['date']
        decision = decision_record['decision']

        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            if date_obj.strftime('%Y-%m-%d') in price_history.index.strftime('%Y-%m-%d'):
                price = price_history.loc[price_history.index.strftime('%Y-%m-%d') == date]['Close'].iloc[0]
            else:
                nearest_date = price_history.index[price_history.index.get_indexer([date_obj], method='nearest')[0]]
                price = price_history.loc[nearest_date, 'Close']
        except Exception:
            continue

        if decision == 'BUY' and cash >= price:
            shares_to_buy = int(cash / price)
            if shares_to_buy > 0:
                shares += shares_to_buy
                cash -= shares_to_buy * price
                trades.append({
                    'date': date,
                    'action': 'BUY',
                    'shares': shares_to_buy,
                    'price': price,
                    'value': shares_to_buy * price
                })

        elif decision == 'SELL' and shares > 0:
            cash += shares * price
            trades.append({
                'date': date,
                'action': 'SELL',
                'shares': shares,
                'price': price,
                'value': shares * price
            })
            shares = 0

        portfolio_value = cash + (shares * price)
        portfolio_history.append({
            'date': date,
            'portfolio_value': portfolio_value,
            'cash': cash,
            'shares': shares,
            'stock_value': shares * price
        })

    if shares > 0:
        current_price = price_history['Close'].iloc[-1]
        final_value = cash + (shares * current_price)
    else:
        final_value = cash

    return {
        'trades': trades,
        'portfolio_history': portfolio_history,
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return': ((final_value - initial_capital) / initial_capital) * 100,
        'num_trades': len(trades)
    }


def calculate_strategy_metrics(backtest_results: Dict) -> Dict:
    """Calculate strategy performance metrics"""
    portfolio_history = backtest_results['portfolio_history']

    if not portfolio_history:
        return {}

    df = pd.DataFrame(portfolio_history)

    returns = df['portfolio_value'].pct_change().dropna()

    metrics = {
        'total_return': backtest_results['total_return'],
        'num_trades': backtest_results['num_trades'],
        'final_value': backtest_results['final_value'],
        'sharpe_ratio': (returns.mean() / returns.std() * (252 ** 0.5)) if returns.std() > 0 else 0,
        'max_drawdown': ((df['portfolio_value'].cummax() - df['portfolio_value']) / df['portfolio_value'].cummax()).max() * 100,
        'win_rate': 0
    }

    trades = backtest_results['trades']
    if len(trades) >= 2:
        winning_trades = 0
        for i in range(0, len(trades) - 1, 2):
            if i + 1 < len(trades):
                buy_trade = trades[i]
                sell_trade = trades[i + 1]
                if buy_trade['action'] == 'BUY' and sell_trade['action'] == 'SELL':
                    if sell_trade['value'] > buy_trade['value']:
                        winning_trades += 1

        total_pairs = len(trades) // 2
        metrics['win_rate'] = (winning_trades / total_pairs * 100) if total_pairs > 0 else 0

    return metrics


def create_backtest_chart(backtest_results: Dict, ticker: str):
    """Create portfolio value chart over time"""
    portfolio_history = backtest_results['portfolio_history']

    if not portfolio_history:
        return None

    df = pd.DataFrame(portfolio_history)
    df['date'] = pd.to_datetime(df['date'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['portfolio_value'],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='blue', width=2),
        fill='tozeroy'
    ))

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=[backtest_results['initial_capital']] * len(df),
        mode='lines',
        name='Initial Capital',
        line=dict(color='gray', dash='dash')
    ))

    trades = backtest_results['trades']
    for trade in trades:
        trade_date = pd.to_datetime(trade['date'])
        trade_value = df[df['date'] == trade_date]['portfolio_value'].iloc[0] if len(df[df['date'] == trade_date]) > 0 else None

        if trade_value is not None:
            fig.add_trace(go.Scatter(
                x=[trade_date],
                y=[trade_value],
                mode='markers',
                marker=dict(
                    size=10,
                    color='green' if trade['action'] == 'BUY' else 'red',
                    symbol='triangle-up' if trade['action'] == 'BUY' else 'triangle-down'
                ),
                name=trade['action'],
                showlegend=False
            ))

    fig.update_layout(
        title=f'{ticker} Backtest: Portfolio Value Over Time',
        xaxis_title='Date',
        yaxis_title='Portfolio Value ($)',
        template='plotly_white',
        height=500,
        hovermode='x unified'
    )

    return fig


def create_trades_chart(trades: List[Dict]):
    """Create chart showing trade distribution"""
    if not trades:
        return None

    df = pd.DataFrame(trades)

    buy_trades = df[df['action'] == 'BUY']
    sell_trades = df[df['action'] == 'SELL']

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='BUY',
        x=buy_trades['date'],
        y=buy_trades['value'],
        marker_color='green'
    ))

    fig.add_trace(go.Bar(
        name='SELL',
        x=sell_trades['date'],
        y=sell_trades['value'],
        marker_color='red'
    ))

    fig.update_layout(
        title='Trade History',
        xaxis_title='Date',
        yaxis_title='Trade Value ($)',
        template='plotly_white',
        height=400,
        barmode='group'
    )

    return fig


def render(loader):
    """Render the analytics page"""

    st.markdown('<p class="main-header">Performance Analytics</p>', unsafe_allow_html=True)
    st.markdown("### Backtest trading strategies and analyze historical performance")

    tickers = loader.get_available_tickers()

    if not tickers:
        st.warning("No trading data available.")
        return

    tab1, tab2, tab3 = st.tabs(["📊 Strategy Backtest", "📈 Decision Analysis", "🎯 Performance Comparison"])

    with tab1:
        st.subheader("Strategy Backtesting")

        col1, col2 = st.columns([2, 1])

        with col1:
            selected_ticker = st.selectbox("Select Ticker", tickers)

        with col2:
            initial_capital = st.number_input(
                "Initial Capital ($)",
                min_value=1000.0,
                value=10000.0,
                step=1000.0
            )

        if st.button("Run Backtest", type="primary"):
            with st.spinner("Running backtest simulation..."):
                decisions_history = loader.get_decision_history(selected_ticker)

                if not decisions_history or len(decisions_history) < 2:
                    st.warning(f"Not enough decision history for {selected_ticker} to run backtest.")
                else:
                    backtest_results = simulate_backtest(selected_ticker, decisions_history, initial_capital)

                    st.session_state.backtest_results = backtest_results
                    st.session_state.backtest_ticker = selected_ticker

        if 'backtest_results' in st.session_state and st.session_state.get('backtest_ticker') == selected_ticker:
            results = st.session_state.backtest_results

            st.markdown("---")
            st.subheader("Backtest Results")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Final Value",
                    f"${results['final_value']:,.2f}"
                )

            with col2:
                st.metric(
                    "Total Return",
                    f"{results['total_return']:.2f}%",
                    delta=f"${results['final_value'] - results['initial_capital']:,.2f}"
                )

            with col3:
                st.metric(
                    "Total Trades",
                    results['num_trades']
                )

            with col4:
                metrics = calculate_strategy_metrics(results)
                st.metric(
                    "Win Rate",
                    f"{metrics.get('win_rate', 0):.1f}%"
                )

            metrics = calculate_strategy_metrics(results)

            if metrics:
                st.markdown("---")
                st.subheader("Strategy Metrics")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Sharpe Ratio",
                        f"{metrics['sharpe_ratio']:.2f}",
                        help="Risk-adjusted return"
                    )

                with col2:
                    st.metric(
                        "Max Drawdown",
                        f"{metrics['max_drawdown']:.2f}%",
                        help="Largest peak-to-trough decline"
                    )

                with col3:
                    annualized_return = metrics['total_return'] * (365 / 365)
                    st.metric(
                        "Annualized Return",
                        f"{annualized_return:.2f}%"
                    )

            backtest_chart = create_backtest_chart(results, selected_ticker)
            if backtest_chart:
                st.plotly_chart(backtest_chart, use_container_width=True)

            trades_chart = create_trades_chart(results['trades'])
            if trades_chart:
                st.plotly_chart(trades_chart, use_container_width=True)

            if results['trades']:
                st.markdown("---")
                st.subheader("Trade Details")

                trades_df = pd.DataFrame(results['trades'])
                st.dataframe(
                    trades_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "value": st.column_config.NumberColumn(format="$%.2f"),
                        "price": st.column_config.NumberColumn(format="$%.2f")
                    }
                )

    with tab2:
        st.subheader("Decision Pattern Analysis")

        selected_ticker = st.selectbox("Select Ticker for Analysis", tickers, key="decision_ticker")

        decisions_history = loader.get_decision_history(selected_ticker)

        if not decisions_history:
            st.warning(f"No decision history for {selected_ticker}")
        else:
            df = pd.DataFrame(decisions_history)

            col1, col2 = st.columns(2)

            with col1:
                decision_counts = df['decision'].value_counts()

                fig = px.pie(
                    values=decision_counts.values,
                    names=decision_counts.index,
                    title='Decision Distribution',
                    color_discrete_map={'BUY': 'green', 'HOLD': 'orange', 'SELL': 'red'}
                )

                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.metric("Total Decisions", len(df))
                st.metric("BUY Decisions", len(df[df['decision'] == 'BUY']))
                st.metric("SELL Decisions", len(df[df['decision'] == 'SELL']))
                st.metric("HOLD Decisions", len(df[df['decision'] == 'HOLD']))

            st.markdown("---")
            st.subheader("Decision Timeline")

            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            decision_map = {'BUY': 1, 'HOLD': 0, 'SELL': -1}
            df['decision_value'] = df['decision'].map(decision_map)

            fig = go.Figure()

            for decision in ['BUY', 'HOLD', 'SELL']:
                decision_df = df[df['decision'] == decision]
                color = {'BUY': 'green', 'HOLD': 'orange', 'SELL': 'red'}[decision]

                fig.add_trace(go.Scatter(
                    x=decision_df['date'],
                    y=decision_df['decision_value'],
                    mode='markers',
                    name=decision,
                    marker=dict(size=12, color=color)
                ))

            fig.update_layout(
                title=f'{selected_ticker} Decision Timeline',
                xaxis_title='Date',
                yaxis_title='Decision',
                yaxis=dict(
                    tickvals=[-1, 0, 1],
                    ticktext=['SELL', 'HOLD', 'BUY']
                ),
                template='plotly_white',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df[['date', 'decision']], use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Multi-Ticker Performance Comparison")

        selected_tickers = st.multiselect(
            "Select Tickers to Compare",
            tickers,
            default=tickers[:min(3, len(tickers))]
        )

        if selected_tickers and len(selected_tickers) >= 2:
            comparison_data = []

            for ticker in selected_tickers:
                summary = loader.get_ticker_summary(ticker)
                decisions_history = loader.get_decision_history(ticker)

                if decisions_history and len(decisions_history) >= 2:
                    backtest = simulate_backtest(ticker, decisions_history, 10000)
                    metrics = calculate_strategy_metrics(backtest)

                    comparison_data.append({
                        'Ticker': ticker,
                        'Total Return (%)': f"{backtest['total_return']:.2f}",
                        'Trades': backtest['num_trades'],
                        'Win Rate (%)': f"{metrics.get('win_rate', 0):.1f}",
                        'Sharpe Ratio': f"{metrics.get('sharpe_ratio', 0):.2f}",
                        'Max Drawdown (%)': f"{metrics.get('max_drawdown', 0):.2f}"
                    })

            if comparison_data:
                df = pd.DataFrame(comparison_data)

                st.dataframe(df, use_container_width=True, hide_index=True)

                st.markdown("---")

                fig = go.Figure()

                for ticker in selected_tickers:
                    decisions_history = loader.get_decision_history(ticker)

                    if decisions_history and len(decisions_history) >= 2:
                        backtest = simulate_backtest(ticker, decisions_history, 10000)
                        portfolio_history = backtest['portfolio_history']

                        if portfolio_history:
                            hist_df = pd.DataFrame(portfolio_history)
                            hist_df['date'] = pd.to_datetime(hist_df['date'])

                            fig.add_trace(go.Scatter(
                                x=hist_df['date'],
                                y=hist_df['portfolio_value'],
                                mode='lines',
                                name=ticker
                            ))

                fig.update_layout(
                    title='Portfolio Value Comparison',
                    xaxis_title='Date',
                    yaxis_title='Portfolio Value ($)',
                    template='plotly_white',
                    height=500,
                    hovermode='x unified'
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Not enough data for comparison. Need at least 2 decisions per ticker.")
        else:
            st.info("Select at least 2 tickers for comparison.")
