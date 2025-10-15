"""Alerts and notifications system"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List
import json


def check_price_alert(ticker: str, current_price: float, target_price: float, condition: str) -> bool:
    """Check if price alert condition is met"""
    if condition == "Above":
        return current_price >= target_price
    elif condition == "Below":
        return current_price <= target_price
    return False


def check_decision_alert(ticker: str, decision: str, target_decision: str) -> bool:
    """Check if decision alert condition is met"""
    return decision == target_decision


def create_alert(alert_type: str, ticker: str, params: Dict) -> Dict:
    """Create new alert"""
    return {
        'id': datetime.now().timestamp(),
        'type': alert_type,
        'ticker': ticker,
        'params': params,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'triggered': False,
        'active': True
    }


def render(loader):
    """Render the alerts page"""

    st.markdown('<p class="main-header">Trading Alerts</p>', unsafe_allow_html=True)
    st.markdown("### Set up price and trading decision alerts")

    if 'alerts' not in st.session_state:
        st.session_state.alerts = []

    if 'triggered_alerts' not in st.session_state:
        st.session_state.triggered_alerts = []

    tab1, tab2, tab3 = st.tabs(["🔔 Active Alerts", "➕ Create Alert", "📋 Alert History"])

    with tab1:
        st.subheader("Active Alerts")

        active_alerts = [a for a in st.session_state.alerts if a['active']]

        if not active_alerts:
            st.info("No active alerts. Create one in the 'Create Alert' tab.")
        else:
            import yfinance as yf

            triggered_count = 0

            for alert in active_alerts:
                ticker = alert['ticker']
                alert_type = alert['type']

                with st.container():
                    col1, col2, col3 = st.columns([3, 4, 1])

                    with col1:
                        st.markdown(f"**{ticker}**")
                        st.caption(alert_type)

                    with col2:
                        if alert_type == "Price Alert":
                            condition = alert['params']['condition']
                            target_price = alert['params']['target_price']
                            st.text(f"Price {condition} ${target_price:.2f}")

                            try:
                                stock = yf.Ticker(ticker)
                                current_price = stock.info.get('currentPrice', stock.info.get('regularMarketPrice', 0))

                                if current_price > 0:
                                    is_triggered = check_price_alert(ticker, current_price, target_price, condition)

                                    if is_triggered and not alert['triggered']:
                                        st.success(f"🔔 TRIGGERED! Current: ${current_price:.2f}")
                                        alert['triggered'] = True
                                        triggered_alert = alert.copy()
                                        triggered_alert['triggered_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        triggered_alert['trigger_value'] = current_price
                                        st.session_state.triggered_alerts.append(triggered_alert)
                                        triggered_count += 1
                                    else:
                                        st.text(f"Current: ${current_price:.2f}")
                            except Exception:
                                st.warning("Unable to fetch current price")

                        elif alert_type == "Decision Alert":
                            target_decision = alert['params']['target_decision']
                            st.text(f"Waiting for {target_decision} decision")

                            latest_date = loader.get_latest_date(ticker)
                            if latest_date:
                                decision_content = loader.read_report(ticker, latest_date, "final_trade_decision")
                                current_decision = loader.extract_decision(decision_content)

                                if current_decision:
                                    is_triggered = check_decision_alert(ticker, current_decision, target_decision)

                                    if is_triggered and not alert['triggered']:
                                        st.success(f"🔔 TRIGGERED! Decision: {current_decision}")
                                        alert['triggered'] = True
                                        triggered_alert = alert.copy()
                                        triggered_alert['triggered_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        triggered_alert['trigger_value'] = current_decision
                                        st.session_state.triggered_alerts.append(triggered_alert)
                                        triggered_count += 1
                                    else:
                                        st.text(f"Current: {current_decision}")

                        elif alert_type == "Volatility Alert":
                            threshold = alert['params']['threshold']
                            st.text(f"Volatility > {threshold}%")

                            try:
                                stock = yf.Ticker(ticker)
                                hist = stock.history(period="1mo")

                                if not hist.empty:
                                    daily_returns = hist['Close'].pct_change().dropna()
                                    volatility = daily_returns.std() * (252 ** 0.5) * 100

                                    is_triggered = volatility >= threshold

                                    if is_triggered and not alert['triggered']:
                                        st.success(f"🔔 TRIGGERED! Volatility: {volatility:.2f}%")
                                        alert['triggered'] = True
                                        triggered_alert = alert.copy()
                                        triggered_alert['triggered_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        triggered_alert['trigger_value'] = volatility
                                        st.session_state.triggered_alerts.append(triggered_alert)
                                        triggered_count += 1
                                    else:
                                        st.text(f"Current: {volatility:.2f}%")
                            except Exception:
                                st.warning("Unable to calculate volatility")

                    with col3:
                        if st.button("🗑️", key=f"delete_alert_{alert['id']}"):
                            alert['active'] = False

                    st.markdown("---")

            if triggered_count > 0:
                st.rerun()

            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Refresh All", type="primary"):
                    st.rerun()

    with tab2:
        st.subheader("Create New Alert")

        available_tickers = loader.get_available_tickers()

        alert_type = st.selectbox(
            "Alert Type",
            ["Price Alert", "Decision Alert", "Volatility Alert"]
        )

        ticker = st.selectbox("Ticker", available_tickers)

        if alert_type == "Price Alert":
            col1, col2 = st.columns(2)

            with col1:
                condition = st.selectbox("Condition", ["Above", "Below"])

            with col2:
                target_price = st.number_input("Target Price ($)", min_value=0.0, value=100.0, step=0.01)

            if st.button("Create Alert", type="primary"):
                alert = create_alert(
                    alert_type,
                    ticker,
                    {
                        'condition': condition,
                        'target_price': target_price
                    }
                )
                st.session_state.alerts.append(alert)
                st.success(f"✅ Created price alert for {ticker}")
                st.rerun()

        elif alert_type == "Decision Alert":
            target_decision = st.selectbox("Target Decision", ["BUY", "HOLD", "SELL"])

            if st.button("Create Alert", type="primary"):
                alert = create_alert(
                    alert_type,
                    ticker,
                    {
                        'target_decision': target_decision
                    }
                )
                st.session_state.alerts.append(alert)
                st.success(f"✅ Created decision alert for {ticker}")
                st.rerun()

        elif alert_type == "Volatility Alert":
            threshold = st.number_input(
                "Volatility Threshold (%)",
                min_value=0.0,
                value=25.0,
                step=1.0,
                help="Alert when annualized volatility exceeds this threshold"
            )

            if st.button("Create Alert", type="primary"):
                alert = create_alert(
                    alert_type,
                    ticker,
                    {
                        'threshold': threshold
                    }
                )
                st.session_state.alerts.append(alert)
                st.success(f"✅ Created volatility alert for {ticker}")
                st.rerun()

        st.markdown("---")
        st.info("💡 **Tip:** Alerts are checked in real-time when you view the Active Alerts tab. "
               "For continuous monitoring, consider setting up email notifications (coming soon).")

    with tab3:
        st.subheader("Triggered Alerts History")

        if not st.session_state.triggered_alerts:
            st.info("No alerts have been triggered yet.")
        else:
            triggered_data = []

            for alert in st.session_state.triggered_alerts:
                triggered_data.append({
                    'Ticker': alert['ticker'],
                    'Type': alert['type'],
                    'Triggered At': alert['triggered_at'],
                    'Trigger Value': str(alert.get('trigger_value', 'N/A')),
                    'Created At': alert['created_at']
                })

            df = pd.DataFrame(triggered_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Clear History", type="secondary"):
                    st.session_state.triggered_alerts = []
                    st.rerun()

        st.markdown("---")
        st.subheader("Export Alerts")

        if st.session_state.alerts:
            alerts_json = json.dumps(st.session_state.alerts, indent=2)

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="Download Alerts (JSON)",
                    data=alerts_json,
                    file_name=f"trading_alerts_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )

            with col2:
                uploaded_file = st.file_uploader("Import Alerts (JSON)", type=['json'])

                if uploaded_file is not None:
                    try:
                        imported_alerts = json.loads(uploaded_file.read())
                        st.session_state.alerts.extend(imported_alerts)
                        st.success(f"✅ Imported {len(imported_alerts)} alerts")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error importing alerts: {str(e)}")
