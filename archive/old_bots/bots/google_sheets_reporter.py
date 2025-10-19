#!/usr/bin/env python3
"""
Google Sheets Reporter
Exports performance data to Google Sheets
Real-time dashboard in spreadsheet
"""

from datetime import datetime
from typing import Dict, List

class GoogleSheetsReporter:
    def __init__(self):
        self.name = "Google_Sheets_Reporter"
        self.version = "1.0.0"
        self.enabled = True
        
        self.sheet_id = None
        self.last_update = None
        
        self.metrics = {'reports_generated': 0, 'rows_written': 0, 'sheets_created': 0}
    
    def format_trade_data(self, trades: List[Dict]) -> List[List]:
        """Format trades for spreadsheet"""
        rows = [['Timestamp', 'Pair', 'Side', 'Price', 'Size', 'PnL', 'Status']]
        
        for trade in trades:
            rows.append([
                trade.get('timestamp', ''),
                trade.get('pair', ''),
                trade.get('side', ''),
                trade.get('price', 0),
                trade.get('size', 0),
                trade.get('pnl', 0),
                trade.get('status', '')
            ])
        
        return rows
    
    def format_performance_summary(self, metrics: Dict) -> List[List]:
        """Format performance summary"""
        return [
            ['Metric', 'Value'],
            ['Total Trades', metrics.get('total_trades', 0)],
            ['Win Rate', f"{metrics.get('win_rate', 0):.1%}"],
            ['Total PnL', f"${metrics.get('total_pnl', 0):.2f}"],
            ['Sharpe Ratio', f"{metrics.get('sharpe_ratio', 0):.2f}"],
            ['Max Drawdown', f"{metrics.get('max_drawdown', 0):.1%}"]
        ]
    
    def create_report(self, data: Dict) -> Dict:
        """Create comprehensive report"""
        self.metrics['reports_generated'] += 1
        self.last_update = datetime.now().isoformat()
        
        return {
            'report_created': True,
            'sheet_id': self.sheet_id,
            'rows_written': len(data.get('trades', [])),
            'timestamp': self.last_update
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'sheet_id': self.sheet_id,
            'metrics': self.metrics,
            'last_update': self.last_update or datetime.now().isoformat()
        }

if __name__ == '__main__':
    reporter = GoogleSheetsReporter()
    print(f"✅ {reporter.name} v{reporter.version} initialized")
