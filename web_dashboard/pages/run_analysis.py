"""Run Analysis page - Execute trading analysis from web interface"""

import streamlit as st
import datetime
from pathlib import Path
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG


LLM_PROVIDERS = {
    "OpenAI": "https://api.openai.com/v1",
    "Anthropic": "https://api.anthropic.com/",
    "Google": "https://generativelanguage.googleapis.com/v1",
    "Openrouter": "https://openrouter.ai/api/v1",
    "Ollama": "http://localhost:11434/v1",
}

SHALLOW_AGENT_OPTIONS = {
    "openai": {
        "GPT-4o-mini - Fast and efficient for quick tasks": "gpt-4o-mini",
        "GPT-4.1-nano - Ultra-lightweight model for basic operations": "gpt-4.1-nano",
        "GPT-4.1-mini - Compact model with good performance": "gpt-4.1-mini",
        "GPT-4o - Standard model with solid capabilities": "gpt-4o",
    },
    "anthropic": {
        "Claude Haiku 3.5 - Fast inference and standard capabilities": "claude-3-5-haiku-latest",
        "Claude Sonnet 3.5 - Highly capable standard model": "claude-3-5-sonnet-latest",
        "Claude Sonnet 3.7 - Exceptional hybrid reasoning and agentic capabilities": "claude-3-7-sonnet-latest",
        "Claude Sonnet 4 - High performance and excellent reasoning": "claude-sonnet-4-0",
    },
    "google": {
        "Gemini 2.0 Flash-Lite - Cost efficiency and low latency": "gemini-2.0-flash-lite",
        "Gemini 2.0 Flash - Next generation features, speed, and thinking": "gemini-2.0-flash",
        "Gemini 2.5 Flash - Adaptive thinking, cost efficiency": "gemini-2.5-flash-preview-05-20",
    },
    "openrouter": {
        "Meta: Llama 4 Scout": "meta-llama/llama-4-scout:free",
        "Meta: Llama 3.3 8B Instruct - A lightweight and ultra-fast variant of Llama 3.3 70B": "meta-llama/llama-3.3-8b-instruct:free",
        "google/gemini-2.0-flash-exp:free - Gemini Flash 2.0 offers a significantly faster time to first token": "google/gemini-2.0-flash-exp:free",
    },
    "ollama": {
        "llama3.1 local": "llama3.1",
        "llama3.2 local": "llama3.2",
    }
}

DEEP_AGENT_OPTIONS = {
    "openai": {
        "GPT-4.1-nano - Ultra-lightweight model for basic operations": "gpt-4.1-nano",
        "GPT-4.1-mini - Compact model with good performance": "gpt-4.1-mini",
        "GPT-4o - Standard model with solid capabilities": "gpt-4o",
        "o4-mini - Specialized reasoning model (compact)": "o4-mini",
        "o3-mini - Advanced reasoning model (lightweight)": "o3-mini",
        "o3 - Full advanced reasoning model": "o3",
        "o1 - Premier reasoning and problem-solving model": "o1",
    },
    "anthropic": {
        "Claude Haiku 3.5 - Fast inference and standard capabilities": "claude-3-5-haiku-latest",
        "Claude Sonnet 3.5 - Highly capable standard model": "claude-3-5-sonnet-latest",
        "Claude Sonnet 3.7 - Exceptional hybrid reasoning and agentic capabilities": "claude-3-7-sonnet-latest",
        "Claude Sonnet 4 - High performance and excellent reasoning": "claude-sonnet-4-0",
        "Claude Opus 4 - Most powerful Anthropic model": "claude-opus-4-0",
    },
    "google": {
        "Gemini 2.0 Flash-Lite - Cost efficiency and low latency": "gemini-2.0-flash-lite",
        "Gemini 2.0 Flash - Next generation features, speed, and thinking": "gemini-2.0-flash",
        "Gemini 2.5 Flash - Adaptive thinking, cost efficiency": "gemini-2.5-flash-preview-05-20",
        "Gemini 2.5 Pro": "gemini-2.5-pro-preview-06-05",
    },
    "openrouter": {
        "DeepSeek V3 - a 685B-parameter, mixture-of-experts model": "deepseek/deepseek-chat-v3-0324:free",
        "Deepseek - latest iteration of the flagship chat model family from the DeepSeek team.": "deepseek/deepseek-chat-v3-0324:free",
    },
    "ollama": {
        "llama3.1 local": "llama3.1",
        "qwen3": "qwen3",
    }
}


def save_reports(final_state, ticker, analysis_date, config):
    """Save analysis reports to files"""
    results_dir = Path(config["results_dir"]) / ticker / analysis_date
    results_dir.mkdir(parents=True, exist_ok=True)
    report_dir = results_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_sections = {
        "market_report": final_state.get("market_report"),
        "sentiment_report": final_state.get("sentiment_report"),
        "news_report": final_state.get("news_report"),
        "fundamentals_report": final_state.get("fundamentals_report"),
        "investment_plan": final_state.get("investment_debate_state", {}).get("judge_decision"),
        "trader_investment_plan": final_state.get("trader_investment_plan"),
        "final_trade_decision": final_state.get("risk_debate_state", {}).get("judge_decision"),
    }

    for section_name, content in report_sections.items():
        if content:
            file_name = f"{section_name}.md"
            with open(report_dir / file_name, "w") as f:
                f.write(content)


def render(loader):
    """Render the run analysis page"""

    st.markdown('<p class="main-header">🚀 Run New Analysis</p>', unsafe_allow_html=True)
    st.markdown("### Execute Trading Analysis")

    st.markdown("---")

    with st.form("analysis_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📊 Analysis Parameters")

            ticker = st.text_input(
                "Ticker Symbol",
                value="SPY",
                help="Enter the stock ticker symbol to analyze"
            ).upper()

            today = datetime.date.today()
            analysis_date = st.date_input(
                "Analysis Date",
                value=today,
                max_value=today,
                help="Select the date for analysis"
            )

            analysts = st.multiselect(
                "Select Analysts",
                ["market", "social", "news", "fundamentals"],
                default=["market", "social", "news", "fundamentals"],
                help="Choose which analyst agents to include in the analysis"
            )

            research_depth = st.select_slider(
                "Research Depth",
                options=[1, 3, 5],
                value=3,
                format_func=lambda x: {
                    1: "Shallow - Quick research",
                    3: "Medium - Moderate depth",
                    5: "Deep - Comprehensive research"
                }[x],
                help="Number of debate rounds for research and risk analysis"
            )

        with col2:
            st.markdown("#### 🤖 LLM Configuration")

            llm_provider = st.selectbox(
                "LLM Provider",
                list(LLM_PROVIDERS.keys()),
                index=0,
                help="Select the LLM provider to use"
            )

            provider_key = llm_provider.lower()

            shallow_options = list(SHALLOW_AGENT_OPTIONS.get(provider_key, {}).keys())
            shallow_thinker = st.selectbox(
                "Quick-Thinking Model",
                shallow_options,
                index=0 if shallow_options else None,
                help="Model for fast, routine tasks"
            )

            deep_options = list(DEEP_AGENT_OPTIONS.get(provider_key, {}).keys())
            deep_thinker = st.selectbox(
                "Deep-Thinking Model",
                deep_options,
                index=0 if deep_options else None,
                help="Model for complex reasoning tasks"
            )

        st.markdown("---")

        submitted = st.form_submit_button(
            "🚀 Run Analysis",
            use_container_width=True,
            type="primary"
        )

    if submitted:
        if not ticker:
            st.error("Please enter a ticker symbol")
            return

        if not analysts:
            st.error("Please select at least one analyst")
            return

        if not shallow_thinker or not deep_thinker:
            st.error("Please select both thinking models")
            return

        shallow_model = SHALLOW_AGENT_OPTIONS.get(provider_key, {}).get(shallow_thinker)
        deep_model = DEEP_AGENT_OPTIONS.get(provider_key, {}).get(deep_thinker)

        config = DEFAULT_CONFIG.copy()
        config["max_debate_rounds"] = research_depth
        config["max_risk_discuss_rounds"] = research_depth
        config["quick_think_llm"] = shallow_model
        config["deep_think_llm"] = deep_model
        config["backend_url"] = LLM_PROVIDERS[llm_provider]
        config["llm_provider"] = provider_key

        analysis_date_str = analysis_date.strftime("%Y-%m-%d")

        st.markdown("---")
        st.markdown(f"### 🔄 Running Analysis for {ticker} on {analysis_date_str}")

        progress_container = st.container()

        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("Initializing trading agents...")
            progress_bar.progress(10)

            try:
                graph = TradingAgentsGraph(
                    selected_analysts=analysts,
                    config=config,
                    debug=False
                )

                status_text.text(f"Running analysis for {ticker}...")
                progress_bar.progress(30)

                init_agent_state = graph.propagator.create_initial_state(
                    ticker, analysis_date_str
                )
                args = graph.propagator.get_graph_args()

                team_stages = [
                    ("Analyst Team", 30, 50),
                    ("Research Team", 50, 70),
                    ("Trading Team", 70, 85),
                    ("Risk Management Team", 85, 95),
                ]

                current_stage = 0
                trace = []

                for chunk in graph.graph.stream(init_agent_state, **args):
                    if len(chunk.get("messages", [])) > 0:
                        trace.append(chunk)

                        if "market_report" in chunk or "sentiment_report" in chunk or "news_report" in chunk or "fundamentals_report" in chunk:
                            if current_stage < len(team_stages):
                                stage_name, start, end = team_stages[current_stage]
                                status_text.text(f"Processing {stage_name}...")
                                progress_bar.progress(end)
                                current_stage += 1

                        elif "investment_debate_state" in chunk:
                            if current_stage < len(team_stages) and team_stages[current_stage][0] == "Research Team":
                                stage_name, start, end = team_stages[current_stage]
                                status_text.text(f"Processing {stage_name}...")
                                progress_bar.progress(end)
                                current_stage += 1

                        elif "trader_investment_plan" in chunk:
                            if current_stage < len(team_stages) and team_stages[current_stage][0] == "Trading Team":
                                stage_name, start, end = team_stages[current_stage]
                                status_text.text(f"Processing {stage_name}...")
                                progress_bar.progress(end)
                                current_stage += 1

                        elif "risk_debate_state" in chunk:
                            if current_stage < len(team_stages) and team_stages[current_stage][0] == "Risk Management Team":
                                stage_name, start, end = team_stages[current_stage]
                                status_text.text(f"Processing {stage_name}...")
                                progress_bar.progress(end)
                                current_stage += 1

                if not trace:
                    st.error("Analysis completed but no results were generated")
                    return

                final_state = trace[-1]

                status_text.text("Saving reports...")
                progress_bar.progress(95)

                save_reports(final_state, ticker, analysis_date_str, config)

                decision = graph.process_signal(final_state.get("final_trade_decision", ""))

                progress_bar.progress(100)
                status_text.text("Analysis completed successfully!")

                st.success(f"✅ Analysis completed for {ticker}!")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Ticker", ticker)
                with col2:
                    st.metric("Date", analysis_date_str)
                with col3:
                    decision_color = {
                        "BUY": "🟢",
                        "HOLD": "🟡",
                        "SELL": "🔴"
                    }.get(decision, "⚪")
                    st.metric("Decision", f"{decision_color} {decision}")

                st.markdown("---")
                st.markdown("### 📊 Reports Generated")

                reports_generated = []
                if final_state.get("market_report"):
                    reports_generated.append("Market Analysis")
                if final_state.get("sentiment_report"):
                    reports_generated.append("Sentiment Analysis")
                if final_state.get("news_report"):
                    reports_generated.append("News Analysis")
                if final_state.get("fundamentals_report"):
                    reports_generated.append("Fundamentals Analysis")
                if final_state.get("trader_investment_plan"):
                    reports_generated.append("Trading Plan")
                if final_state.get("risk_debate_state", {}).get("judge_decision"):
                    reports_generated.append("Final Decision")

                st.markdown(f"**Generated {len(reports_generated)} reports:**")
                for report in reports_generated:
                    st.markdown(f"✓ {report}")

                st.info("💡 View detailed reports in the 'Report Viewer' page")

            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.exception(e)
