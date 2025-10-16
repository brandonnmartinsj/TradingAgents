"""TradingAgents Web Dashboard - Streamlit Application"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path to import project modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from web_dashboard.utils.data_loader import ResultsLoader
from web_dashboard.pages import dashboard, report_viewer, comparison, portfolio, alerts, analytics, settings, reddit_sentiment, run_analysis

# Page configuration
st.set_page_config(
    page_title="TradingAgents Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .decision-badge {
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 1.2rem;
        text-align: center;
        margin: 1rem 0;
    }

    .decision-buy {
        background-color: #10b981;
        color: white;
    }

    .decision-hold {
        background-color: #f59e0b;
        color: white;
    }

    .decision-sell {
        background-color: #ef4444;
        color: white;
    }

    .metric-card {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }

    .stMarkdown table {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point"""

    # Sidebar navigation
    st.sidebar.title("📊 Navigation")

    page = st.sidebar.radio(
        "Select Page",
        [
            "🏠 Dashboard",
            "🚀 Run Analysis",
            "📄 Report Viewer",
            "🔍 Comparison",
            "💼 Portfolio",
            "🔔 Alerts",
            "📈 Analytics",
            "🤖 Reddit Sentiment",
            "⚙️ Settings"
        ],
        label_visibility="collapsed"
    )

    # Initialize data loader
    try:
        loader = ResultsLoader()
        has_results = bool(loader.get_available_tickers())
    except FileNotFoundError:
        loader = None
        has_results = False

    # Special handling for Run Analysis page - always accessible
    if page == "🚀 Run Analysis":
        run_analysis.render(loader)
        return

    # For other pages, check if results exist
    if not has_results:
        st.error("⚠️ No results found! Please run TradingAgents at least once to generate reports.")
        st.info("💡 Tip: Use the '🚀 Run Analysis' page to generate your first trading analysis!")
        return

    # Route to appropriate page
    if page == "🏠 Dashboard":
        dashboard.render(loader)
    elif page == "📄 Report Viewer":
        report_viewer.render(loader)
    elif page == "🔍 Comparison":
        comparison.render(loader)
    elif page == "💼 Portfolio":
        portfolio.render(loader)
    elif page == "🔔 Alerts":
        alerts.render(loader)
    elif page == "📈 Analytics":
        analytics.render(loader)
    elif page == "🤖 Reddit Sentiment":
        reddit_sentiment.render(loader)
    elif page == "⚙️ Settings":
        settings.render(loader)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**TradingAgents Dashboard**  \n"
        "Built with Streamlit  \n"
        "[GitHub](https://github.com/TauricResearch/TradingAgents)"
    )


if __name__ == "__main__":
    main()
