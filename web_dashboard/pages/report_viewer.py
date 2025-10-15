"""Report viewer page"""

import streamlit as st


def render(loader):
    """Render the report viewer page"""

    st.title("📄 Report Viewer")
    st.markdown("View detailed trading reports and analysis")

    # Ticker selection
    tickers = loader.get_available_tickers()

    if not tickers:
        st.warning("No reports available.")
        return

    selected_ticker = st.selectbox("Select Ticker", tickers, key="report_ticker")

    # Date selection
    dates = loader.get_available_dates(selected_ticker)

    if not dates:
        st.warning(f"No reports found for {selected_ticker}")
        return

    selected_date = st.selectbox("Select Date", dates, key="report_date")

    # Language selection
    col1, col2 = st.columns([3, 1])
    with col2:
        language = st.radio("Language", ["en", "pt-BR"], key="report_lang")

    # Report type selection
    report_types = {
        "Final Decision": "final_trade_decision",
        "Trader Plan": "trader_investment_plan",
        "Investment Plan": "investment_plan",
        "Market Analysis": "market_report",
        "Sentiment Analysis": "sentiment_report",
        "News Analysis": "news_report",
        "Fundamentals": "fundamentals_report"
    }

    selected_report_name = st.selectbox(
        "Select Report Type",
        list(report_types.keys()),
        key="report_type"
    )

    report_type = report_types[selected_report_name]

    # Load and display report
    st.markdown("---")

    content = loader.read_report(selected_ticker, selected_date, report_type, language)

    if content:
        # Extract and display decision if available
        decision = loader.extract_decision(content)
        if decision:
            color_map = {"BUY": "🟢", "HOLD": "🟡", "SELL": "🔴"}
            icon = color_map.get(decision, "⚪")
            st.markdown(f"### Decision: {icon} **{decision}**")

        st.markdown(content)

        # Download button
        st.download_button(
            label="Download Report",
            data=content,
            file_name=f"{selected_ticker}_{selected_date}_{report_type}.md",
            mime="text/markdown"
        )
    else:
        st.error(f"Report not found: {report_type} ({language})")
