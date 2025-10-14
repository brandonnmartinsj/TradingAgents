"""CLI tool for translating TradingAgents reports to Brazilian Portuguese."""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from .translator import ReportTranslator
from .config import TranslationConfig


def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_path = Path(__file__).parent.parent / ".env"

    if not env_path.exists():
        return

    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and not os.getenv(key):
                    os.environ[key] = value


def find_results_directory() -> Path:
    """Find the results directory in the project."""
    current_dir = Path(__file__).parent.parent
    results_dir = current_dir / "results"

    if not results_dir.exists():
        raise FileNotFoundError(
            f"Results directory not found at {results_dir}. "
            "Make sure you have run TradingAgents at least once to generate reports."
        )

    return results_dir


def list_available_tickers(results_dir: Path) -> list[str]:
    """List all available tickers in the results directory."""
    tickers = [d.name for d in results_dir.iterdir() if d.is_dir()]
    return sorted(tickers)


def list_available_dates(ticker_dir: Path) -> list[str]:
    """List all available dates for a ticker."""
    dates = [d.name for d in ticker_dir.iterdir() if d.is_dir()]
    return sorted(dates)


def translate_ticker_date(
    translator: ReportTranslator,
    results_dir: Path,
    ticker: str,
    date: str,
) -> int:
    """Translate reports for a specific ticker and date.

    Returns:
        Number of files translated
    """
    reports_dir = results_dir / ticker / date / "reports"

    if not reports_dir.exists():
        print(f"[ERROR] No reports found for {ticker} on {date}")
        return 0

    print(f"\n{'='*60}")
    print(f"Translating reports: {ticker} - {date}")
    print(f"{'='*60}")

    translated_files = translator.translate_reports_directory(reports_dir)

    print(f"\n{'='*60}")
    print(f"[SUCCESS] Translated {len(translated_files)} file(s)")
    print(f"{'='*60}\n")

    return len(translated_files)


def translate_ticker_all_dates(
    translator: ReportTranslator,
    results_dir: Path,
    ticker: str,
) -> int:
    """Translate all reports for a specific ticker.

    Returns:
        Total number of files translated
    """
    ticker_dir = results_dir / ticker

    if not ticker_dir.exists():
        print(f"[ERROR] No results found for ticker: {ticker}")
        return 0

    dates = list_available_dates(ticker_dir)

    if not dates:
        print(f"[ERROR] No dates found for ticker: {ticker}")
        return 0

    print(f"\nFound {len(dates)} date(s) for {ticker}: {', '.join(dates)}")

    total_translated = 0
    for date in dates:
        count = translate_ticker_date(translator, results_dir, ticker, date)
        total_translated += count

    return total_translated


def translate_all_tickers(translator: ReportTranslator, results_dir: Path) -> int:
    """Translate all reports for all tickers.

    Returns:
        Total number of files translated
    """
    tickers = list_available_tickers(results_dir)

    if not tickers:
        print("[ERROR] No tickers found in results directory")
        return 0

    print(f"\nFound {len(tickers)} ticker(s): {', '.join(tickers)}")

    total_translated = 0
    for ticker in tickers:
        count = translate_ticker_all_dates(translator, results_dir, ticker)
        total_translated += count

    return total_translated


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Translate TradingAgents reports to Brazilian Portuguese",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate reports for specific ticker and date
  python -m translation.translate_reports --ticker ITSA4.SA --date 2025-10-10

  # Translate all reports for a ticker
  python -m translation.translate_reports --ticker ITSA4.SA --all-dates

  # Translate all reports for all tickers
  python -m translation.translate_reports --all

  # List available tickers
  python -m translation.translate_reports --list-tickers

  # Use custom OpenAI model
  python -m translation.translate_reports --ticker IBM --date 2025-10-10 --model gpt-4o
        """,
    )

    parser.add_argument(
        "--ticker",
        type=str,
        help="Stock ticker symbol (e.g., ITSA4.SA, IBM)",
    )

    parser.add_argument(
        "--date",
        type=str,
        help="Report date in YYYY-MM-DD format",
    )

    parser.add_argument(
        "--all-dates",
        action="store_true",
        help="Translate all dates for the specified ticker",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Translate all reports for all tickers",
    )

    parser.add_argument(
        "--list-tickers",
        action="store_true",
        help="List all available tickers",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Model temperature (default: 0.3)",
    )

    args = parser.parse_args()

    # Load .env file
    load_env_file()

    try:
        results_dir = find_results_directory()

        # List tickers and exit
        if args.list_tickers:
            tickers = list_available_tickers(results_dir)
            if tickers:
                print("\nAvailable tickers:")
                for ticker in tickers:
                    ticker_dir = results_dir / ticker
                    dates = list_available_dates(ticker_dir)
                    print(f"  • {ticker} ({len(dates)} date(s))")
            else:
                print("\nNo tickers found in results directory")
            return 0

        # Validate arguments
        if not (args.all or args.ticker):
            parser.error("Either --ticker or --all is required")

        if args.ticker and args.date and args.all_dates:
            parser.error("Cannot use both --date and --all-dates")

        if args.ticker and not (args.date or args.all_dates):
            parser.error("When using --ticker, specify either --date or --all-dates")

        # Initialize translator
        config = TranslationConfig(
            model=args.model,
            temperature=args.temperature,
        )
        translator = ReportTranslator(config=config)

        print(f"\nUsing OpenAI model: {config.model}")
        print(f"Target language: {config.target_language}")

        # Execute translation
        total_translated = 0

        if args.all:
            total_translated = translate_all_tickers(translator, results_dir)

        elif args.ticker and args.all_dates:
            total_translated = translate_ticker_all_dates(
                translator, results_dir, args.ticker
            )

        elif args.ticker and args.date:
            total_translated = translate_ticker_date(
                translator, results_dir, args.ticker, args.date
            )

        # Summary
        print(f"\n{'='*60}")
        print(f"Translation complete!")
        print(f"Total files translated: {total_translated}")
        print(f"{'='*60}\n")

        return 0

    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}\n", file=sys.stderr)
        return 1

    except ValueError as e:
        print(f"\n[ERROR] {e}\n", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}\n", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
