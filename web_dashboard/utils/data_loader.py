"""Data loader for TradingAgents results"""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class ReportMetadata:
    """Metadata for a trading report"""
    ticker: str
    date: str
    report_type: str
    language: str
    file_path: Path
    decision: Optional[str] = None


class ResultsLoader:
    """Loads and parses TradingAgents results from the file system"""

    REPORT_TYPES = [
        "market_report",
        "sentiment_report",
        "news_report",
        "fundamentals_report",
        "investment_plan",
        "trader_investment_plan",
        "final_trade_decision"
    ]

    def __init__(self, results_dir: Optional[Path] = None):
        """Initialize the results loader

        Args:
            results_dir: Path to results directory. If None, uses ./results
        """
        if results_dir is None:
            results_dir = Path(__file__).parent.parent.parent / "results"

        self.results_dir = Path(results_dir)

        if not self.results_dir.exists():
            raise FileNotFoundError(
                f"Results directory not found: {self.results_dir}. "
                "Run TradingAgents at least once to generate results."
            )

    def get_available_tickers(self) -> List[str]:
        """Get list of all available tickers"""
        tickers = [
            d.name for d in self.results_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        return sorted(tickers)

    def get_available_dates(self, ticker: str) -> List[str]:
        """Get list of available dates for a ticker"""
        ticker_dir = self.results_dir / ticker

        if not ticker_dir.exists():
            return []

        dates = [
            d.name for d in ticker_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        return sorted(dates, reverse=True)

    def get_latest_date(self, ticker: str) -> Optional[str]:
        """Get the most recent date for a ticker"""
        dates = self.get_available_dates(ticker)
        return dates[0] if dates else None

    def get_report_path(
        self,
        ticker: str,
        date: str,
        report_type: str,
        language: str = "en"
    ) -> Optional[Path]:
        """Get path to a specific report file

        Args:
            ticker: Stock ticker symbol
            date: Date in YYYY-MM-DD format
            report_type: Type of report (e.g., 'market_report')
            language: Language code ('en' or 'pt-BR')

        Returns:
            Path to report file or None if not found
        """
        reports_dir = self.results_dir / ticker / date / "reports"

        if not reports_dir.exists():
            return None

        # Construct filename
        suffix = f"_{language}" if language != "en" else ""
        filename = f"{report_type}{suffix}.md"
        file_path = reports_dir / filename

        return file_path if file_path.exists() else None

    def read_report(
        self,
        ticker: str,
        date: str,
        report_type: str,
        language: str = "en"
    ) -> Optional[str]:
        """Read content of a report file

        Args:
            ticker: Stock ticker symbol
            date: Date in YYYY-MM-DD format
            report_type: Type of report
            language: Language code

        Returns:
            Report content as string or None if not found
        """
        file_path = self.get_report_path(ticker, date, report_type, language)

        if file_path is None:
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None

    def extract_decision(self, content: str) -> Optional[str]:
        """Extract trading decision (BUY/HOLD/SELL) from report content

        Args:
            content: Report content

        Returns:
            Decision string or None
        """
        if not content:
            return None

        # Look for decision patterns
        patterns = [
            r'FINAL TRANSACTION PROPOSAL:\s*\*\*(BUY|HOLD|SELL)\*\*',
            r'FINAL TRANSACTION PROPOSAL:\s*(BUY|HOLD|SELL)',
            r'Decision:\s*\*\*(BUY|HOLD|SELL)\*\*',
            r'\*\*_(BUY|HOLD|SELL)_\*\*'
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).upper()

        return None

    def extract_technical_indicators(self, content: str) -> Dict[str, str]:
        """Extract technical indicators from market report

        Args:
            content: Report content

        Returns:
            Dictionary of indicator names to values
        """
        indicators = {}

        if not content:
            return indicators

        # Look for markdown tables
        lines = content.split('\n')
        in_table = False

        for i, line in enumerate(lines):
            # Detect table header
            if '| Indicator' in line or '|--' in line:
                in_table = True
                continue

            if in_table:
                if not line.strip() or not line.startswith('|'):
                    in_table = False
                    continue

                # Parse table row
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 2:
                    indicator_name = parts[0]
                    value = parts[1]
                    indicators[indicator_name] = value

        return indicators

    def extract_news_sources(self, content: str) -> List[Dict[str, str]]:
        """Extract news sources and links from news report

        Args:
            content: News report content

        Returns:
            List of dictionaries with news source info
        """
        news_sources = []

        if not content:
            return news_sources

        lines = content.split('\n')
        in_table = False

        for line in lines:
            if '| **Topic**' in line or '| **' in line:
                in_table = True
                continue

            if in_table:
                if not line.strip() or not line.startswith('|'):
                    in_table = False
                    continue

                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 3:
                    topic = parts[0].replace('**', '').strip()
                    details = parts[1].strip()
                    source = parts[2].strip()

                    url_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', source)
                    if url_match:
                        source_name = url_match.group(1)
                        source_url = url_match.group(2)
                        news_sources.append({
                            'topic': topic,
                            'details': details,
                            'source_name': source_name,
                            'source_url': source_url
                        })

        return news_sources

    def extract_financial_metrics(self, content: str) -> Dict[str, str]:
        """Extract financial metrics from fundamentals report

        Args:
            content: Fundamentals report content

        Returns:
            Dictionary of metric names to values
        """
        metrics = {}

        if not content:
            return metrics

        lines = content.split('\n')

        for line in lines:
            for pattern in [
                r'\*\*Market Capitalization\*\*:\s*\$?([0-9.]+\s*[BMK]?illion)',
                r'\*\*EBITDA\*\*:\s*\$?([0-9.]+\s*[BMK]?illion)',
                r'\*\*P/E\*\*:\s*([0-9.]+)',
                r'\*\*Price-to-Earnings Ratio \(P/E\)\*\*:\s*([0-9.]+)',
                r'\*\*Dividend Yield\*\*:\s*([0-9.]+)%',
                r'\*\*EPS\*\*:\s*\$?([0-9.]+)',
                r'\*\*Total Revenue\*\*:\s*\$?([0-9.]+\s*[BMK]?illion)',
                r'\*\*Net Income\*\*:\s*\$?([0-9.]+\s*[BMK]?illion)',
                r'\*\*Operating Income\*\*:\s*\$?([0-9.]+\s*[BMK]?illion)',
                r'\*\*Debt to Equity Ratio\*\*:\s*([0-9.]+)'
            ]:
                match = re.search(pattern, line)
                if match:
                    metric_name = pattern.split(r'\*\*')[1].split(r'\*\*')[0]
                    metrics[metric_name] = match.group(1)

        return metrics

    def get_all_reports(
        self,
        ticker: str,
        date: str,
        language: str = "en"
    ) -> Dict[str, str]:
        """Get all reports for a ticker and date

        Args:
            ticker: Stock ticker symbol
            date: Date in YYYY-MM-DD format
            language: Language code

        Returns:
            Dictionary mapping report types to content
        """
        reports = {}

        for report_type in self.REPORT_TYPES:
            content = self.read_report(ticker, date, report_type, language)
            if content:
                reports[report_type] = content

        return reports

    def get_ticker_summary(self, ticker: str) -> Dict:
        """Get summary information for a ticker

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with summary information
        """
        dates = self.get_available_dates(ticker)

        if not dates:
            return {
                "ticker": ticker,
                "total_analyses": 0,
                "latest_date": None,
                "latest_decision": None
            }

        latest_date = dates[0]
        decision_content = self.read_report(
            ticker, latest_date, "final_trade_decision"
        )
        latest_decision = self.extract_decision(decision_content)

        return {
            "ticker": ticker,
            "total_analyses": len(dates),
            "latest_date": latest_date,
            "latest_decision": latest_decision,
            "all_dates": dates
        }

    def get_decision_history(self, ticker: str) -> List[Dict]:
        """Get history of trading decisions for a ticker

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of decision records sorted by date (newest first)
        """
        dates = self.get_available_dates(ticker)
        history = []

        for date in dates:
            content = self.read_report(ticker, date, "final_trade_decision")
            decision = self.extract_decision(content)

            history.append({
                "date": date,
                "decision": decision,
                "ticker": ticker
            })

        return history
