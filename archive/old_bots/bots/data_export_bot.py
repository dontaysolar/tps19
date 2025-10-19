#!/usr/bin/env python3
"""Data Export Bot - Export trading data to various formats"""
import json
import csv
from datetime import datetime
from typing import Dict, List
from io import StringIO

class DataExportBot:
    def __init__(self):
        self.name = "Data_Export"
        self.version = "1.0.0"
        self.enabled = True
        
        self.metrics = {'exports': 0, 'records_exported': 0}
    
    def export_to_json(self, data: List[Dict], filename: str = None) -> Dict:
        """Export data to JSON"""
        try:
            json_str = json.dumps(data, indent=2)
            
            self.metrics['exports'] += 1
            self.metrics['records_exported'] += len(data)
            
            return {
                'format': 'JSON',
                'records': len(data),
                'data': json_str if not filename else None,
                'filename': filename,
                'size_bytes': len(json_str),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def export_to_csv(self, data: List[Dict], filename: str = None) -> Dict:
        """Export data to CSV"""
        try:
            if not data:
                return {'error': 'No data to export'}
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            
            csv_str = output.getvalue()
            
            self.metrics['exports'] += 1
            self.metrics['records_exported'] += len(data)
            
            return {
                'format': 'CSV',
                'records': len(data),
                'data': csv_str if not filename else None,
                'filename': filename,
                'size_bytes': len(csv_str),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def export_trades(self, trades: List[Dict], format: str = 'JSON') -> Dict:
        """Export trade history"""
        if format.upper() == 'JSON':
            return self.export_to_json(trades, 'trades.json')
        elif format.upper() == 'CSV':
            return self.export_to_csv(trades, 'trades.csv')
        else:
            return {'error': 'Unsupported format', 'supported': ['JSON', 'CSV']}
    
    def export_performance_report(self, report_data: Dict) -> Dict:
        """Export performance report"""
        report_str = f"""
APEX PERFORMANCE REPORT
Generated: {datetime.now().isoformat()}

SUMMARY
Total P&L: ${report_data.get('total_pnl', 0):,.2f}
Total Trades: {report_data.get('total_trades', 0)}
Win Rate: {report_data.get('win_rate', 0):.2f}%
Sharpe Ratio: {report_data.get('sharpe_ratio', 0):.2f}
Max Drawdown: {report_data.get('max_drawdown', 0):.2f}%

TRADES
{json.dumps(report_data.get('trades', []), indent=2)}
"""
        
        self.metrics['exports'] += 1
        
        return {
            'format': 'TXT',
            'report': report_str,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'supported_formats': ['JSON', 'CSV', 'TXT'],
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = DataExportBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
