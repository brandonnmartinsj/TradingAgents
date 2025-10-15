"""Settings and configuration page"""

import streamlit as st
import json
from pathlib import Path


def load_settings():
    """Load settings from file"""
    settings_file = Path(__file__).parent.parent / "settings.json"

    default_settings = {
        'theme': 'light',
        'refresh_interval': 60,
        'default_currency': 'USD',
        'default_period': '1mo',
        'show_news': True,
        'show_technical_indicators': True,
        'max_tickers_display': 10,
        'enable_notifications': False,
        'api_keys': {
            'alpha_vantage': '',
            'news_api': ''
        }
    }

    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                saved_settings = json.load(f)
                default_settings.update(saved_settings)
        except Exception:
            pass

    return default_settings


def save_settings(settings: dict):
    """Save settings to file"""
    settings_file = Path(__file__).parent.parent / "settings.json"

    try:
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception:
        return False


def render(loader):
    """Render the settings page"""

    st.markdown('<p class="main-header">Dashboard Settings</p>', unsafe_allow_html=True)
    st.markdown("### Configure your dashboard preferences")

    if 'settings' not in st.session_state:
        st.session_state.settings = load_settings()

    settings = st.session_state.settings

    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Display", "📊 Data", "🔔 Notifications", "🔑 API Keys"])

    with tab1:
        st.subheader("Display Settings")

        col1, col2 = st.columns(2)

        with col1:
            theme = st.selectbox(
                "Theme",
                ["light", "dark"],
                index=0 if settings.get('theme', 'light') == 'light' else 1
            )
            settings['theme'] = theme

            max_tickers = st.number_input(
                "Max Tickers on Dashboard",
                min_value=5,
                max_value=50,
                value=settings.get('max_tickers_display', 10),
                step=5
            )
            settings['max_tickers_display'] = int(max_tickers)

        with col2:
            refresh_interval = st.number_input(
                "Auto-Refresh Interval (seconds)",
                min_value=30,
                max_value=300,
                value=settings.get('refresh_interval', 60),
                step=30,
                help="How often to refresh real-time data"
            )
            settings['refresh_interval'] = int(refresh_interval)

        st.markdown("---")
        st.subheader("Widget Visibility")

        col1, col2 = st.columns(2)

        with col1:
            show_news = st.checkbox(
                "Show News Section",
                value=settings.get('show_news', True)
            )
            settings['show_news'] = show_news

        with col2:
            show_technical = st.checkbox(
                "Show Technical Indicators",
                value=settings.get('show_technical_indicators', True)
            )
            settings['show_technical_indicators'] = show_technical

        st.markdown("---")
        st.subheader("Color Scheme")

        col1, col2, col3 = st.columns(3)

        with col1:
            buy_color = st.color_picker(
                "BUY Color",
                value=settings.get('colors', {}).get('buy', '#10b981')
            )

        with col2:
            hold_color = st.color_picker(
                "HOLD Color",
                value=settings.get('colors', {}).get('hold', '#f59e0b')
            )

        with col3:
            sell_color = st.color_picker(
                "SELL Color",
                value=settings.get('colors', {}).get('sell', '#ef4444')
            )

        if 'colors' not in settings:
            settings['colors'] = {}

        settings['colors']['buy'] = buy_color
        settings['colors']['hold'] = hold_color
        settings['colors']['sell'] = sell_color

    with tab2:
        st.subheader("Data Settings")

        col1, col2 = st.columns(2)

        with col1:
            default_currency = st.selectbox(
                "Default Currency",
                ["USD", "EUR", "GBP", "BRL"],
                index=["USD", "EUR", "GBP", "BRL"].index(settings.get('default_currency', 'USD'))
            )
            settings['default_currency'] = default_currency

            default_period = st.selectbox(
                "Default Time Period",
                ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"],
                index=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"].index(settings.get('default_period', '1mo'))
            )
            settings['default_period'] = default_period

        with col2:
            data_source = st.selectbox(
                "Price Data Source",
                ["Yahoo Finance", "Alpha Vantage"],
                index=0
            )
            settings['data_source'] = data_source

            cache_duration = st.number_input(
                "Cache Duration (minutes)",
                min_value=5,
                max_value=60,
                value=settings.get('cache_duration', 15),
                step=5,
                help="How long to cache API responses"
            )
            settings['cache_duration'] = int(cache_duration)

        st.markdown("---")
        st.subheader("Export Settings")

        col1, col2 = st.columns(2)

        with col1:
            export_format = st.selectbox(
                "Default Export Format",
                ["CSV", "JSON", "Excel"],
                index=0
            )
            settings['export_format'] = export_format

        with col2:
            include_metadata = st.checkbox(
                "Include Metadata in Exports",
                value=settings.get('include_metadata', True)
            )
            settings['include_metadata'] = include_metadata

    with tab3:
        st.subheader("Notification Settings")

        enable_notifications = st.checkbox(
            "Enable Notifications",
            value=settings.get('enable_notifications', False)
        )
        settings['enable_notifications'] = enable_notifications

        if enable_notifications:
            st.info("💡 Notifications are enabled. Configure alert thresholds below.")

            col1, col2 = st.columns(2)

            with col1:
                price_change_threshold = st.number_input(
                    "Price Change Alert (%)",
                    min_value=1.0,
                    max_value=50.0,
                    value=settings.get('price_change_threshold', 5.0),
                    step=0.5,
                    help="Alert when price changes by this percentage"
                )
                settings['price_change_threshold'] = price_change_threshold

            with col2:
                volume_spike_threshold = st.number_input(
                    "Volume Spike Alert (x)",
                    min_value=1.0,
                    max_value=10.0,
                    value=settings.get('volume_spike_threshold', 2.0),
                    step=0.5,
                    help="Alert when volume exceeds average by this multiple"
                )
                settings['volume_spike_threshold'] = volume_spike_threshold

            st.markdown("---")
            st.subheader("Notification Methods")

            notification_email = st.text_input(
                "Email Address",
                value=settings.get('notification_email', ''),
                help="Receive alerts via email"
            )
            settings['notification_email'] = notification_email

            notification_webhook = st.text_input(
                "Webhook URL",
                value=settings.get('notification_webhook', ''),
                help="Send alerts to a webhook (e.g., Slack, Discord)"
            )
            settings['notification_webhook'] = notification_webhook
        else:
            st.info("Notifications are currently disabled.")

    with tab4:
        st.subheader("API Keys")

        st.markdown("Configure API keys for external data sources.")

        st.markdown("#### Alpha Vantage")
        alpha_vantage_key = st.text_input(
            "API Key",
            value=settings.get('api_keys', {}).get('alpha_vantage', ''),
            type="password",
            help="Get a free key at https://www.alphavantage.co/support/#api-key"
        )

        if 'api_keys' not in settings:
            settings['api_keys'] = {}

        settings['api_keys']['alpha_vantage'] = alpha_vantage_key

        st.markdown("#### News API")
        news_api_key = st.text_input(
            "API Key",
            value=settings.get('api_keys', {}).get('news_api', ''),
            type="password",
            help="Get a free key at https://newsapi.org/"
        )

        settings['api_keys']['news_api'] = news_api_key

        st.markdown("---")
        st.warning("⚠️ Keep your API keys secure. Never share them publicly.")

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.info("💡 Settings are saved automatically when you click 'Save Settings'")

    with col2:
        if st.button("Reset to Defaults", type="secondary"):
            st.session_state.settings = load_settings()
            st.success("Settings reset to defaults")
            st.rerun()

    with col3:
        if st.button("Save Settings", type="primary"):
            if save_settings(settings):
                st.success("✅ Settings saved successfully")
            else:
                st.error("❌ Failed to save settings")

    st.markdown("---")
    st.subheader("Dashboard Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        tickers = loader.get_available_tickers()
        st.metric("Total Tickers", len(tickers))

    with col2:
        total_analyses = 0
        for ticker in tickers:
            summary = loader.get_ticker_summary(ticker)
            total_analyses += summary['total_analyses']
        st.metric("Total Analyses", total_analyses)

    with col3:
        settings_file = Path(__file__).parent.parent / "settings.json"
        if settings_file.exists():
            st.metric("Settings File", "✅ Exists")
        else:
            st.metric("Settings File", "❌ Not Found")

    st.markdown("---")
    st.subheader("Export/Import Settings")

    col1, col2 = st.columns(2)

    with col1:
        settings_json = json.dumps(settings, indent=2)
        st.download_button(
            label="📥 Export Settings",
            data=settings_json,
            file_name="dashboard_settings.json",
            mime="application/json"
        )

    with col2:
        uploaded_file = st.file_uploader("📤 Import Settings", type=['json'])

        if uploaded_file is not None:
            try:
                imported_settings = json.loads(uploaded_file.read())
                st.session_state.settings = imported_settings

                if save_settings(imported_settings):
                    st.success("✅ Settings imported successfully")
                    st.rerun()
                else:
                    st.error("❌ Failed to save imported settings")
            except Exception as e:
                st.error(f"Error importing settings: {str(e)}")
