"""Comparison page"""

import streamlit as st
import pandas as pd


def render(loader):
    """Render the comparison page"""

    st.title("🔍 Comparison")
    st.markdown("Compare trading decisions across tickers and dates")

    tickers = loader.get_available_tickers()

    if not tickers:
        st.warning("No data available for comparison.")
        return

    # Multi-ticker selection
    selected_tickers = st.multiselect(
        "Select Tickers to Compare",
        tickers,
        default=tickers[:min(3, len(tickers))]
    )

    if not selected_tickers:
        st.info("Please select at least one ticker.")
        return

    # Collect data
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
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Decision distribution
        st.markdown("### Decision Distribution")
        decision_col = df['Latest Decision'].value_counts()
        st.bar_chart(decision_col)
    else:
        st.info("No data available for selected tickers.")
