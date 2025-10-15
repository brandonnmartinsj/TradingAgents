"""Utilities for fetching and displaying company logos"""

import streamlit as st
from typing import Optional
import yfinance as yf
from pathlib import Path
import requests
from io import BytesIO


@st.cache_data(ttl=86400)
def get_company_logo_url(ticker: str) -> Optional[str]:
    """Get company logo URL from various sources

    Args:
        ticker: Stock ticker symbol

    Returns:
        Logo URL or None if not found
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        logo_url = info.get('logo_url')
        if logo_url:
            return logo_url

    except Exception:
        pass

    try:
        clearbit_url = f"https://logo.clearbit.com/{get_domain_from_ticker(ticker)}"
        response = requests.head(clearbit_url, timeout=2)
        if response.status_code == 200:
            return clearbit_url
    except Exception:
        pass

    return None


def get_domain_from_ticker(ticker: str) -> str:
    """Convert ticker to likely company domain

    Args:
        ticker: Stock ticker symbol

    Returns:
        Company domain guess
    """
    ticker_clean = ticker.replace('.SA', '').replace('-', '').lower()

    domain_mapping = {
        'aapl': 'apple.com',
        'msft': 'microsoft.com',
        'googl': 'google.com',
        'goog': 'google.com',
        'amzn': 'amazon.com',
        'meta': 'meta.com',
        'tsla': 'tesla.com',
        'nvda': 'nvidia.com',
        'avgo': 'broadcom.com',
        'ibm': 'ibm.com',
        'orcl': 'oracle.com',
        'intc': 'intel.com',
        'amd': 'amd.com',
        'nflx': 'netflix.com',
        'dis': 'disney.com',
        'ba': 'boeing.com',
        'jpm': 'jpmorganchase.com',
        'v': 'visa.com',
        'ma': 'mastercard.com',
        'wmt': 'walmart.com',
        'ko': 'coca-cola.com',
        'pfe': 'pfizer.com',
        'jnj': 'jnj.com',
        'pg': 'pg.com',
        'bac': 'bankofamerica.com',
        'csco': 'cisco.com',
        'adbe': 'adobe.com',
        'crm': 'salesforce.com',
        'petr4': 'petrobras.com.br',
        'vale3': 'vale.com',
        'itub4': 'itau.com.br',
        'bbdc4': 'bb.com.br',
    }

    return domain_mapping.get(ticker_clean, f"{ticker_clean}.com")


def display_ticker_with_logo(ticker: str, size: int = 20) -> str:
    """Generate HTML for ticker with logo

    Args:
        ticker: Stock ticker symbol
        size: Logo size in pixels

    Returns:
        HTML string with logo and ticker
    """
    logo_url = get_company_logo_url(ticker)

    if logo_url:
        return f'''
        <div style="display: flex; align-items: center; gap: 8px;">
            <img src="{logo_url}"
                 style="width: {size}px; height: {size}px; border-radius: 4px; object-fit: contain;"
                 onerror="this.style.display='none'"
                 alt="{ticker}">
            <span style="font-weight: 600;">{ticker}</span>
        </div>
        '''
    else:
        return f'<span style="font-weight: 600;">{ticker}</span>'


def get_ticker_display_name(ticker: str) -> str:
    """Get display name with emoji for ticker

    Args:
        ticker: Stock ticker symbol

    Returns:
        Display name with emoji prefix
    """
    return f"📊 {ticker}"


def render_ticker_header(ticker: str, size: int = 32):
    """Render ticker as a header with logo

    Args:
        ticker: Stock ticker symbol
        size: Logo size in pixels
    """
    html = display_ticker_with_logo(ticker, size)
    st.markdown(html, unsafe_allow_html=True)


def get_logo_as_bytes(ticker: str) -> Optional[BytesIO]:
    """Download logo and return as bytes

    Args:
        ticker: Stock ticker symbol

    Returns:
        BytesIO object with logo data or None
    """
    logo_url = get_company_logo_url(ticker)

    if not logo_url:
        return None

    try:
        response = requests.get(logo_url, timeout=5)
        if response.status_code == 200:
            return BytesIO(response.content)
    except Exception:
        pass

    return None


def create_ticker_badge(ticker: str, decision: Optional[str] = None) -> str:
    """Create styled badge for ticker with optional decision

    Args:
        ticker: Stock ticker symbol
        decision: Optional trading decision (BUY/HOLD/SELL)

    Returns:
        HTML string with styled badge
    """
    logo_url = get_company_logo_url(ticker)

    decision_colors = {
        'BUY': '#10b981',
        'HOLD': '#f59e0b',
        'SELL': '#ef4444'
    }

    decision_html = ''
    if decision:
        color = decision_colors.get(decision, '#6b7280')
        decision_html = f'''
        <span style="background-color: {color}; color: white; padding: 2px 8px;
                     border-radius: 4px; font-size: 11px; font-weight: 600; margin-left: 8px;">
            {decision}
        </span>
        '''

    if logo_url:
        return f'''
        <div style="display: inline-flex; align-items: center; gap: 8px;
                    background: #f8fafc; padding: 8px 12px; border-radius: 8px;
                    border: 1px solid #e2e8f0;">
            <img src="{logo_url}"
                 style="width: 24px; height: 24px; border-radius: 4px; object-fit: contain;"
                 onerror="this.style.display='none'"
                 alt="{ticker}">
            <span style="font-weight: 600; font-size: 14px;">{ticker}</span>
            {decision_html}
        </div>
        '''
    else:
        return f'''
        <div style="display: inline-flex; align-items: center; gap: 8px;
                    background: #f8fafc; padding: 8px 12px; border-radius: 8px;
                    border: 1px solid #e2e8f0;">
            <span style="font-weight: 600; font-size: 14px;">📊 {ticker}</span>
            {decision_html}
        </div>
        '''
