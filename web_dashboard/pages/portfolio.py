"""Portfolio management page"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List


def calculate_portfolio_metrics(positions: List[Dict]) -> Dict:
    """Calculate portfolio-level metrics"""
    if not positions:
        return {}

    total_value = sum(p['current_value'] for p in positions)
    total_cost = sum(p['cost_basis'] for p in positions)
    total_gain_loss = total_value - total_cost
    total_return = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0

    return {
        'total_value': total_value,
        'total_cost': total_cost,
        'total_gain_loss': total_gain_loss,
        'total_return': total_return,
        'num_positions': len(positions)
    }


def calculate_risk_metrics(positions: List[Dict], historical_data: Dict) -> Dict:
    """Calculate portfolio risk metrics"""
    returns = []

    for position in positions:
        ticker = position['ticker']
        if ticker in historical_data and not historical_data[ticker].empty:
            daily_returns = historical_data[ticker]['Close'].pct_change().dropna()
            returns.extend(daily_returns.tolist())

    if not returns:
        return {}

    returns_series = pd.Series(returns)

    volatility = returns_series.std() * (252 ** 0.5) * 100
    sharpe_ratio = (returns_series.mean() / returns_series.std() * (252 ** 0.5)) if returns_series.std() > 0 else 0
    max_drawdown = ((returns_series.cumsum().cummax() - returns_series.cumsum()).max()) * 100

    return {
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown
    }


def create_portfolio_allocation_chart(positions: List[Dict]):
    """Create pie chart showing portfolio allocation"""
    if not positions:
        return None

    df = pd.DataFrame(positions)

    fig = px.pie(
        df,
        values='current_value',
        names='ticker',
        title='Portfolio Allocation',
        hole=0.4
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig


def create_performance_chart(positions: List[Dict]):
    """Create bar chart showing performance by position"""
    if not positions:
        return None

    df = pd.DataFrame(positions)
    df['return_pct'] = ((df['current_value'] - df['cost_basis']) / df['cost_basis'] * 100)

    colors = ['green' if x > 0 else 'red' for x in df['return_pct']]

    fig = go.Figure(data=[
        go.Bar(
            x=df['ticker'],
            y=df['return_pct'],
            marker_color=colors,
            text=[f"{x:.2f}%" for x in df['return_pct']],
            textposition='outside'
        )
    ])

    fig.update_layout(
        title='Position Performance',
        xaxis_title='Ticker',
        yaxis_title='Return (%)',
        template='plotly_white',
        height=400
    )

    return fig


def create_gain_loss_chart(positions: List[Dict]):
    """Create waterfall chart showing gain/loss contribution"""
    if not positions:
        return None

    df = pd.DataFrame(positions)
    df['gain_loss'] = df['current_value'] - df['cost_basis']

    fig = go.Figure(go.Waterfall(
        name="P&L",
        orientation="v",
        x=df['ticker'],
        y=df['gain_loss'],
        text=[f"${x:,.2f}" for x in df['gain_loss']],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))

    fig.update_layout(
        title="Gain/Loss by Position",
        template='plotly_white',
        height=400
    )

    return fig


def render(loader):
    """Render the portfolio management page"""

    st.markdown('<p class="main-header">Portfolio Manager</p>', unsafe_allow_html=True)
    st.markdown("### Track your positions and analyze portfolio risk")

    st.info("💡 Enter your positions manually or load from saved portfolio")

    if 'portfolio_positions' not in st.session_state:
        st.session_state.portfolio_positions = []

    tab1, tab2, tab3 = st.tabs(["📊 Overview", "➕ Add Position", "📈 Analytics"])

    with tab1:
        if not st.session_state.portfolio_positions:
            st.warning("No positions in portfolio. Add positions in the 'Add Position' tab.")
        else:
            positions = st.session_state.portfolio_positions

            metrics = calculate_portfolio_metrics(positions)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total Value",
                    f"${metrics['total_value']:,.2f}"
                )

            with col2:
                st.metric(
                    "Total Cost",
                    f"${metrics['total_cost']:,.2f}"
                )

            with col3:
                delta_color = "normal" if metrics['total_gain_loss'] >= 0 else "inverse"
                st.metric(
                    "Gain/Loss",
                    f"${metrics['total_gain_loss']:,.2f}",
                    delta=f"{metrics['total_return']:.2f}%",
                    delta_color=delta_color
                )

            with col4:
                st.metric(
                    "Positions",
                    metrics['num_positions']
                )

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                allocation_chart = create_portfolio_allocation_chart(positions)
                if allocation_chart:
                    st.plotly_chart(allocation_chart, use_container_width=True)

            with col2:
                performance_chart = create_performance_chart(positions)
                if performance_chart:
                    st.plotly_chart(performance_chart, use_container_width=True)

            gain_loss_chart = create_gain_loss_chart(positions)
            if gain_loss_chart:
                st.plotly_chart(gain_loss_chart, use_container_width=True)

            st.markdown("---")
            st.subheader("Position Details")

            df = pd.DataFrame(positions)
            df['return_pct'] = ((df['current_value'] - df['cost_basis']) / df['cost_basis'] * 100).round(2)
            df['gain_loss'] = (df['current_value'] - df['cost_basis']).round(2)

            display_df = df[['ticker', 'shares', 'cost_basis', 'current_value', 'gain_loss', 'return_pct']]
            display_df.columns = ['Ticker', 'Shares', 'Cost Basis', 'Current Value', 'Gain/Loss', 'Return (%)']

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Cost Basis": st.column_config.NumberColumn(format="$%.2f"),
                    "Current Value": st.column_config.NumberColumn(format="$%.2f"),
                    "Gain/Loss": st.column_config.NumberColumn(format="$%.2f"),
                    "Return (%)": st.column_config.NumberColumn(format="%.2f%%")
                }
            )

            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Clear Portfolio", type="secondary"):
                    st.session_state.portfolio_positions = []
                    st.rerun()

    with tab2:
        st.subheader("Add New Position")

        available_tickers = loader.get_available_tickers()

        with st.form("add_position_form"):
            col1, col2 = st.columns(2)

            with col1:
                ticker = st.selectbox("Ticker", available_tickers)
                shares = st.number_input("Shares", min_value=0.0, value=10.0, step=1.0)

            with col2:
                avg_price = st.number_input("Average Price ($)", min_value=0.0, value=100.0, step=0.01)
                purchase_date = st.date_input("Purchase Date", value=datetime.now() - timedelta(days=30))

            submitted = st.form_submit_button("Add Position", type="primary")

            if submitted:
                import yfinance as yf

                try:
                    stock = yf.Ticker(ticker)
                    current_price = stock.info.get('currentPrice', stock.info.get('regularMarketPrice', avg_price))

                    position = {
                        'ticker': ticker,
                        'shares': shares,
                        'avg_price': avg_price,
                        'cost_basis': shares * avg_price,
                        'current_price': current_price,
                        'current_value': shares * current_price,
                        'purchase_date': purchase_date.strftime('%Y-%m-%d')
                    }

                    st.session_state.portfolio_positions.append(position)
                    st.success(f"✅ Added {shares} shares of {ticker}")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error adding position: {str(e)}")

        if st.session_state.portfolio_positions:
            st.markdown("---")
            st.subheader("Current Positions")

            for idx, pos in enumerate(st.session_state.portfolio_positions):
                col1, col2, col3 = st.columns([3, 3, 1])

                with col1:
                    st.text(f"{pos['ticker']}: {pos['shares']} shares @ ${pos['avg_price']:.2f}")

                with col2:
                    gain_loss = pos['current_value'] - pos['cost_basis']
                    return_pct = (gain_loss / pos['cost_basis'] * 100) if pos['cost_basis'] > 0 else 0
                    color = "green" if gain_loss >= 0 else "red"
                    st.markdown(f":{color}[P&L: ${gain_loss:.2f} ({return_pct:.2f}%)]")

                with col3:
                    if st.button("🗑️", key=f"delete_{idx}"):
                        st.session_state.portfolio_positions.pop(idx)
                        st.rerun()

    with tab3:
        st.subheader("Portfolio Analytics & Risk Metrics")

        if not st.session_state.portfolio_positions:
            st.warning("No positions to analyze. Add positions first.")
        else:
            positions = st.session_state.portfolio_positions

            with st.spinner("Calculating risk metrics..."):
                import yfinance as yf

                historical_data = {}
                for pos in positions:
                    ticker = pos['ticker']
                    try:
                        stock = yf.Ticker(ticker)
                        historical_data[ticker] = stock.history(period="1y")
                    except Exception:
                        continue

                risk_metrics = calculate_risk_metrics(positions, historical_data)

                if risk_metrics:
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Portfolio Volatility",
                            f"{risk_metrics['volatility']:.2f}%",
                            help="Annualized standard deviation of returns"
                        )

                    with col2:
                        st.metric(
                            "Sharpe Ratio",
                            f"{risk_metrics['sharpe_ratio']:.2f}",
                            help="Risk-adjusted return measure"
                        )

                    with col3:
                        st.metric(
                            "Max Drawdown",
                            f"{risk_metrics['max_drawdown']:.2f}%",
                            help="Largest peak-to-trough decline"
                        )

                    st.markdown("---")
                    st.subheader("Correlation Matrix")

                    if len(historical_data) > 1:
                        returns_df = pd.DataFrame()

                        for ticker, data in historical_data.items():
                            if not data.empty:
                                returns_df[ticker] = data['Close'].pct_change()

                        if not returns_df.empty:
                            corr_matrix = returns_df.corr()

                            fig = px.imshow(
                                corr_matrix,
                                text_auto='.2f',
                                aspect="auto",
                                color_continuous_scale='RdYlGn',
                                title='Asset Correlation Matrix'
                            )

                            st.plotly_chart(fig, use_container_width=True)

                    st.markdown("---")
                    st.subheader("Individual Position Risk")

                    position_risk = []

                    for pos in positions:
                        ticker = pos['ticker']
                        if ticker in historical_data and not historical_data[ticker].empty:
                            daily_returns = historical_data[ticker]['Close'].pct_change().dropna()
                            volatility = daily_returns.std() * (252 ** 0.5) * 100

                            position_risk.append({
                                'Ticker': ticker,
                                'Volatility (%)': f"{volatility:.2f}",
                                'Beta': 'N/A',
                                'VaR (95%)': f"{daily_returns.quantile(0.05) * 100:.2f}%"
                            })

                    if position_risk:
                        st.dataframe(
                            pd.DataFrame(position_risk),
                            use_container_width=True,
                            hide_index=True
                        )
                else:
                    st.warning("Unable to calculate risk metrics. Insufficient historical data.")
