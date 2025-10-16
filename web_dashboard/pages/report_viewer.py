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

    col1, col2 = st.columns([4, 1])
    with col1:
        selected_date = st.selectbox("Select Date", dates, key="report_date")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Delete Analysis", key="delete_analysis", type="secondary", use_container_width=True):
            if st.session_state.get('confirm_delete_analysis') == f"{selected_ticker}_{selected_date}":
                if loader.delete_analysis(selected_ticker, selected_date):
                    st.success(f"✅ Successfully deleted all reports for {selected_ticker} on {selected_date}")
                    st.session_state.pop('confirm_delete_analysis', None)
                    st.rerun()
                else:
                    st.error("❌ Failed to delete analysis")
            else:
                st.session_state['confirm_delete_analysis'] = f"{selected_ticker}_{selected_date}"
                st.warning("⚠️ Click again to confirm deletion of ALL reports for this analysis")

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

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download Report",
                data=content,
                file_name=f"{selected_ticker}_{selected_date}_{report_type}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col2:
            delete_key = f"delete_report_{report_type}_{language}"
            if st.button("🗑️ Delete This Report", key=delete_key, type="secondary", use_container_width=True):
                confirm_key = f"confirm_{delete_key}"
                if st.session_state.get(confirm_key) == f"{selected_ticker}_{selected_date}_{report_type}_{language}":
                    if loader.delete_specific_report(selected_ticker, selected_date, report_type, language):
                        st.success(f"✅ Successfully deleted {selected_report_name} report")
                        st.session_state.pop(confirm_key, None)
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete report")
                else:
                    st.session_state[confirm_key] = f"{selected_ticker}_{selected_date}_{report_type}_{language}"
                    st.warning("⚠️ Click again to confirm deletion of this specific report")
    else:
        st.error(f"Report not found: {report_type} ({language})")
