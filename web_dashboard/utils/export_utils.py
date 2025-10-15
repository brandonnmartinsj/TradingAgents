"""Export utilities for data export in various formats"""

import pandas as pd
import json
from typing import Dict, List
from io import BytesIO
import csv
from datetime import datetime


def export_to_csv(data: List[Dict], filename: str = None) -> str:
    """Export data to CSV format"""
    if not data:
        return ""

    df = pd.DataFrame(data)
    return df.to_csv(index=False)


def export_to_json(data: List[Dict], pretty: bool = True) -> str:
    """Export data to JSON format"""
    if pretty:
        return json.dumps(data, indent=2, default=str)
    return json.dumps(data, default=str)


def export_to_excel(data: List[Dict], sheet_name: str = "Data") -> BytesIO:
    """Export data to Excel format"""
    output = BytesIO()

    if not data:
        return output

    df = pd.DataFrame(data)

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).map(len).max(),
                len(str(col))
            )
            worksheet.set_column(idx, idx, max_length + 2)

    output.seek(0)
    return output


def export_portfolio_report(positions: List[Dict], metrics: Dict) -> str:
    """Generate comprehensive portfolio report in markdown"""
    report = f"# Portfolio Report\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    report += "## Portfolio Summary\n\n"
    report += f"- **Total Value:** ${metrics.get('total_value', 0):,.2f}\n"
    report += f"- **Total Cost:** ${metrics.get('total_cost', 0):,.2f}\n"
    report += f"- **Gain/Loss:** ${metrics.get('total_gain_loss', 0):,.2f}\n"
    report += f"- **Total Return:** {metrics.get('total_return', 0):.2f}%\n"
    report += f"- **Number of Positions:** {metrics.get('num_positions', 0)}\n\n"

    if positions:
        report += "## Position Details\n\n"
        report += "| Ticker | Shares | Avg Price | Current Price | Cost Basis | Current Value | Gain/Loss | Return (%) |\n"
        report += "|--------|--------|-----------|---------------|------------|---------------|-----------|------------|\n"

        for pos in positions:
            gain_loss = pos['current_value'] - pos['cost_basis']
            return_pct = (gain_loss / pos['cost_basis'] * 100) if pos['cost_basis'] > 0 else 0

            report += f"| {pos['ticker']} | "
            report += f"{pos['shares']:.2f} | "
            report += f"${pos['avg_price']:.2f} | "
            report += f"${pos['current_price']:.2f} | "
            report += f"${pos['cost_basis']:.2f} | "
            report += f"${pos['current_value']:.2f} | "
            report += f"${gain_loss:.2f} | "
            report += f"{return_pct:.2f}% |\n"

    return report


def export_backtest_report(ticker: str, backtest_results: Dict, metrics: Dict) -> str:
    """Generate backtest analysis report in markdown"""
    report = f"# Backtest Report: {ticker}\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    report += "## Strategy Performance\n\n"
    report += f"- **Initial Capital:** ${backtest_results['initial_capital']:,.2f}\n"
    report += f"- **Final Value:** ${backtest_results['final_value']:,.2f}\n"
    report += f"- **Total Return:** {backtest_results['total_return']:.2f}%\n"
    report += f"- **Number of Trades:** {backtest_results['num_trades']}\n\n"

    report += "## Risk Metrics\n\n"
    report += f"- **Sharpe Ratio:** {metrics.get('sharpe_ratio', 0):.2f}\n"
    report += f"- **Max Drawdown:** {metrics.get('max_drawdown', 0):.2f}%\n"
    report += f"- **Win Rate:** {metrics.get('win_rate', 0):.1f}%\n\n"

    if backtest_results['trades']:
        report += "## Trade History\n\n"
        report += "| Date | Action | Shares | Price | Value |\n"
        report += "|------|--------|--------|-------|-------|\n"

        for trade in backtest_results['trades']:
            report += f"| {trade['date']} | "
            report += f"{trade['action']} | "
            report += f"{trade['shares']} | "
            report += f"${trade['price']:.2f} | "
            report += f"${trade['value']:.2f} |\n"

    return report


def export_comparison_report(tickers: List[str], comparison_data: List[Dict]) -> str:
    """Generate multi-ticker comparison report"""
    report = "# Multi-Ticker Comparison Report\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    report += f"**Tickers Analyzed:** {', '.join(tickers)}\n\n"

    report += "## Performance Comparison\n\n"
    report += "| Ticker | Latest Date | Latest Decision | Total Analyses |\n"
    report += "|--------|-------------|-----------------|----------------|\n"

    for data in comparison_data:
        report += f"| {data['Ticker']} | "
        report += f"{data['Latest Date']} | "
        report += f"{data['Latest Decision']} | "
        report += f"{data['Total Analyses']} |\n"

    return report


def export_alerts_report(alerts: List[Dict], triggered_alerts: List[Dict]) -> str:
    """Generate alerts summary report"""
    report = "# Trading Alerts Report\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    report += f"## Summary\n\n"
    report += f"- **Active Alerts:** {len([a for a in alerts if a.get('active', True)])}\n"
    report += f"- **Triggered Alerts:** {len(triggered_alerts)}\n\n"

    active_alerts = [a for a in alerts if a.get('active', True)]

    if active_alerts:
        report += "## Active Alerts\n\n"
        report += "| Ticker | Type | Created At | Status |\n"
        report += "|--------|------|------------|--------|\n"

        for alert in active_alerts:
            report += f"| {alert['ticker']} | "
            report += f"{alert['type']} | "
            report += f"{alert['created_at']} | "
            report += f"{'Triggered' if alert.get('triggered', False) else 'Active'} |\n"

    if triggered_alerts:
        report += "\n## Triggered Alerts History\n\n"
        report += "| Ticker | Type | Triggered At | Trigger Value |\n"
        report += "|--------|------|--------------|---------------|\n"

        for alert in triggered_alerts:
            report += f"| {alert['ticker']} | "
            report += f"{alert['type']} | "
            report += f"{alert.get('triggered_at', 'N/A')} | "
            report += f"{alert.get('trigger_value', 'N/A')} |\n"

    return report


def prepare_export_data(data_type: str, data: Dict) -> Dict:
    """Prepare data for export based on type"""
    export_formats = {}

    if data_type == "portfolio":
        positions = data.get('positions', [])
        metrics = data.get('metrics', {})

        export_formats['csv'] = export_to_csv(positions)
        export_formats['json'] = export_to_json(positions)
        export_formats['excel'] = export_to_excel(positions, sheet_name="Portfolio")
        export_formats['report'] = export_portfolio_report(positions, metrics)

    elif data_type == "backtest":
        ticker = data.get('ticker', 'Unknown')
        results = data.get('results', {})
        metrics = data.get('metrics', {})

        trades = results.get('trades', [])
        export_formats['csv'] = export_to_csv(trades)
        export_formats['json'] = export_to_json(results)
        export_formats['excel'] = export_to_excel(trades, sheet_name="Trades")
        export_formats['report'] = export_backtest_report(ticker, results, metrics)

    elif data_type == "comparison":
        comparison_data = data.get('data', [])
        tickers = data.get('tickers', [])

        export_formats['csv'] = export_to_csv(comparison_data)
        export_formats['json'] = export_to_json(comparison_data)
        export_formats['excel'] = export_to_excel(comparison_data, sheet_name="Comparison")
        export_formats['report'] = export_comparison_report(tickers, comparison_data)

    elif data_type == "alerts":
        alerts = data.get('alerts', [])
        triggered_alerts = data.get('triggered_alerts', [])

        export_formats['csv'] = export_to_csv(triggered_alerts)
        export_formats['json'] = export_to_json(alerts)
        export_formats['report'] = export_alerts_report(alerts, triggered_alerts)

    return export_formats
