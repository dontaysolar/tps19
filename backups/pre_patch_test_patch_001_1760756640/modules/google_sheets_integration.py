#!/usr/bin/env python3
"""Google Sheets Integration for TPS19 - Real-Time Dashboard & Reporting"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️ Google API libraries not available. Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


class GoogleSheetsIntegration:
    """Google Sheets integration for real-time dashboard and reporting"""
    
    def __init__(self, credentials_file='/opt/tps19/config/google_credentials.json'):
        """Initialize Google Sheets integration
        
        Args:
            credentials_file: Path to Google service account credentials
        """
        self.credentials_file = credentials_file
        self.service = None
        self.spreadsheet_id = None
        self.connected = False
        
        if GOOGLE_AVAILABLE and os.path.exists(credentials_file):
            self._connect()
        elif not os.path.exists(credentials_file):
            print(f"⚠️ Credentials file not found: {credentials_file}")
            
    def _connect(self):
        """Connect to Google Sheets API"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            self.service = build('sheets', 'v4', credentials=credentials)
            self.connected = True
            print("✅ Connected to Google Sheets API")
            
        except Exception as e:
            print(f"❌ Failed to connect to Google Sheets: {e}")
            self.connected = False
            
    def create_dashboard(self, title='TPS19 Trading Dashboard'):
        """Create new dashboard spreadsheet
        
        Args:
            title: Spreadsheet title
            
        Returns:
            Spreadsheet ID
        """
        if not self.connected:
            return None
            
        try:
            spreadsheet = {
                'properties': {'title': title},
                'sheets': [
                    {'properties': {'title': 'Overview', 'gridProperties': {'rowCount': 100, 'columnCount': 10}}},
                    {'properties': {'title': 'Trades', 'gridProperties': {'rowCount': 1000, 'columnCount': 15}}},
                    {'properties': {'title': 'Performance', 'gridProperties': {'rowCount': 500, 'columnCount': 10}}},
                    {'properties': {'title': 'Strategies', 'gridProperties': {'rowCount': 100, 'columnCount': 12}}},
                    {'properties': {'title': 'Risk Metrics', 'gridProperties': {'rowCount': 100, 'columnCount': 10}}},
                ]
            }
            
            result = self.service.spreadsheets().create(body=spreadsheet).execute()
            self.spreadsheet_id = result['spreadsheetId']
            
            # Initialize dashboard structure
            self._initialize_overview_sheet()
            self._initialize_trades_sheet()
            self._initialize_performance_sheet()
            self._initialize_strategies_sheet()
            self._initialize_risk_sheet()
            
            print(f"✅ Dashboard created: {self.spreadsheet_id}")
            print(f"📊 View at: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}")
            
            return self.spreadsheet_id
            
        except Exception as e:
            print(f"❌ Error creating dashboard: {e}")
            return None
            
    def _initialize_overview_sheet(self):
        """Initialize Overview sheet structure"""
        headers = [
            ['TPS19 Trading Dashboard - Overview'],
            [''],
            ['Metric', 'Value', 'Last Updated'],
            ['Total Balance', '', ''],
            ['24h Profit/Loss', '', ''],
            ['Total Trades', '', ''],
            ['Win Rate', '', ''],
            ['Sharpe Ratio', '', ''],
            ['Max Drawdown', '', ''],
            ['Active Positions', '', ''],
            [''],
            ['System Status', 'Value', ''],
            ['Trading Status', '', ''],
            ['Strategies Active', '', ''],
            ['AI Models Running', '', ''],
            ['Last Trade', '', '']
        ]
        
        self._write_range('Overview!A1:C20', headers)
        
        # Format header
        self._format_cells('Overview!A1:C1', {
            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
        })
        
    def _initialize_trades_sheet(self):
        """Initialize Trades sheet structure"""
        headers = [[
            'Timestamp', 'Trade ID', 'Symbol', 'Side', 'Type', 
            'Price', 'Amount', 'Value', 'Fee', 'Strategy', 
            'Profit/Loss', 'Status', 'Notes'
        ]]
        
        self._write_range('Trades!A1:M1', headers)
        self._format_cells('Trades!A1:M1', {
            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
        })
        
    def _initialize_performance_sheet(self):
        """Initialize Performance sheet structure"""
        headers = [[
            'Date', 'Starting Balance', 'Ending Balance', 'Profit/Loss', 
            'Profit %', 'Trades', 'Wins', 'Losses', 'Win Rate', 'Sharpe Ratio'
        ]]
        
        self._write_range('Performance!A1:J1', headers)
        self._format_cells('Performance!A1:J1', {
            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
        })
        
    def _initialize_strategies_sheet(self):
        """Initialize Strategies sheet structure"""
        headers = [[
            'Strategy', 'Status', 'Trades', 'Wins', 'Losses', 'Win Rate',
            'Total Profit', 'Avg Profit', 'Max Drawdown', 'Sharpe Ratio', 
            'Last Trade', 'Notes'
        ]]
        
        self._write_range('Strategies!A1:L1', headers)
        self._format_cells('Strategies!A1:L1', {
            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
        })
        
    def _initialize_risk_sheet(self):
        """Initialize Risk Metrics sheet structure"""
        headers = [[
            'Metric', 'Current', 'Limit', 'Status', 'Last Updated'
        ]]
        
        self._write_range('Risk Metrics!A1:E1', headers)
        self._format_cells('Risk Metrics!A1:E1', {
            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
        })
        
    def update_overview(self, data: Dict):
        """Update overview metrics
        
        Args:
            data: Dictionary of metrics to update
        """
        if not self.connected or not self.spreadsheet_id:
            return False
            
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            values = [
                ['', data.get('total_balance', ''), timestamp],
                ['', data.get('daily_profit', ''), timestamp],
                ['', data.get('total_trades', ''), timestamp],
                ['', data.get('win_rate', ''), timestamp],
                ['', data.get('sharpe_ratio', ''), timestamp],
                ['', data.get('max_drawdown', ''), timestamp],
                ['', data.get('active_positions', ''), timestamp],
                [''],
                [''],
                ['', data.get('trading_status', ''), timestamp],
                ['', data.get('strategies_active', ''), timestamp],
                ['', data.get('ai_models_running', ''), timestamp],
                ['', data.get('last_trade', ''), timestamp]
            ]
            
            self._write_range('Overview!B4:D16', values)
            return True
            
        except Exception as e:
            print(f"❌ Error updating overview: {e}")
            return False
            
    def add_trade(self, trade: Dict):
        """Add new trade to Trades sheet
        
        Args:
            trade: Trade data dictionary
        """
        if not self.connected or not self.spreadsheet_id:
            return False
            
        try:
            values = [[
                trade.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                trade.get('trade_id', ''),
                trade.get('symbol', ''),
                trade.get('side', ''),
                trade.get('type', ''),
                trade.get('price', ''),
                trade.get('amount', ''),
                trade.get('value', ''),
                trade.get('fee', ''),
                trade.get('strategy', ''),
                trade.get('profit_loss', ''),
                trade.get('status', ''),
                trade.get('notes', '')
            ]]
            
            self._append_range('Trades!A2:M', values)
            return True
            
        except Exception as e:
            print(f"❌ Error adding trade: {e}")
            return False
            
    def update_performance(self, date: str, performance: Dict):
        """Update daily performance
        
        Args:
            date: Date string
            performance: Performance metrics
        """
        if not self.connected or not self.spreadsheet_id:
            return False
            
        try:
            values = [[
                date,
                performance.get('starting_balance', ''),
                performance.get('ending_balance', ''),
                performance.get('profit_loss', ''),
                performance.get('profit_pct', ''),
                performance.get('trades', ''),
                performance.get('wins', ''),
                performance.get('losses', ''),
                performance.get('win_rate', ''),
                performance.get('sharpe_ratio', '')
            ]]
            
            self._append_range('Performance!A2:J', values)
            return True
            
        except Exception as e:
            print(f"❌ Error updating performance: {e}")
            return False
            
    def update_strategy(self, strategy_name: str, metrics: Dict):
        """Update strategy metrics
        
        Args:
            strategy_name: Strategy name
            metrics: Strategy metrics
        """
        if not self.connected or not self.spreadsheet_id:
            return False
            
        try:
            # Find strategy row or append new
            values = [[
                strategy_name,
                metrics.get('status', ''),
                metrics.get('trades', ''),
                metrics.get('wins', ''),
                metrics.get('losses', ''),
                metrics.get('win_rate', ''),
                metrics.get('total_profit', ''),
                metrics.get('avg_profit', ''),
                metrics.get('max_drawdown', ''),
                metrics.get('sharpe_ratio', ''),
                metrics.get('last_trade', ''),
                metrics.get('notes', '')
            ]]
            
            self._append_range('Strategies!A2:L', values)
            return True
            
        except Exception as e:
            print(f"❌ Error updating strategy: {e}")
            return False
            
    def update_risk_metrics(self, metrics: Dict):
        """Update risk metrics
        
        Args:
            metrics: Risk metrics dictionary
        """
        if not self.connected or not self.spreadsheet_id:
            return False
            
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            risk_data = [
                ['Daily Drawdown', metrics.get('daily_drawdown', ''), 
                 metrics.get('max_daily_drawdown', ''), 
                 metrics.get('drawdown_status', ''), timestamp],
                ['Position Size', metrics.get('position_size', ''), 
                 metrics.get('max_position_size', ''), 
                 metrics.get('position_status', ''), timestamp],
                ['Risk Per Trade', metrics.get('risk_per_trade', ''), 
                 metrics.get('max_risk_per_trade', ''), 
                 metrics.get('risk_status', ''), timestamp],
                ['Open Trades', metrics.get('open_trades', ''), 
                 metrics.get('max_open_trades', ''), 
                 metrics.get('trades_status', ''), timestamp],
                ['Leverage', metrics.get('leverage', ''), 
                 metrics.get('max_leverage', ''), 
                 metrics.get('leverage_status', ''), timestamp]
            ]
            
            self._write_range('Risk Metrics!A2:E6', risk_data)
            return True
            
        except Exception as e:
            print(f"❌ Error updating risk metrics: {e}")
            return False
            
    def _write_range(self, range_name: str, values: List[List]):
        """Write values to range"""
        if not self.connected or not self.spreadsheet_id:
            return False
            
        try:
            body = {'values': values}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            return True
        except Exception as e:
            print(f"❌ Error writing range: {e}")
            return False
            
    def _append_range(self, range_name: str, values: List[List]):
        """Append values to range"""
        if not self.connected or not self.spreadsheet_id:
            return False
            
        try:
            body = {'values': values}
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            return True
        except Exception as e:
            print(f"❌ Error appending range: {e}")
            return False
            
    def _format_cells(self, range_name: str, format_dict: Dict):
        """Format cells"""
        if not self.connected or not self.spreadsheet_id:
            return False
            
        try:
            requests = [{
                'repeatCell': {
                    'range': self._range_to_grid_range(range_name),
                    'cell': {'userEnteredFormat': format_dict},
                    'fields': 'userEnteredFormat'
                }
            }]
            
            body = {'requests': requests}
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            return True
        except Exception as e:
            print(f"❌ Error formatting cells: {e}")
            return False
            
    def _range_to_grid_range(self, range_name: str) -> Dict:
        """Convert A1 notation to GridRange"""
        # Simplified implementation
        parts = range_name.split('!')
        sheet_name = parts[0] if len(parts) > 1 else 'Sheet1'
        
        # Get sheet ID (simplified - assumes first sheet)
        return {
            'sheetId': 0,
            'startRowIndex': 0,
            'endRowIndex': 1,
            'startColumnIndex': 0,
            'endColumnIndex': 3
        }
        
    def get_dashboard_url(self) -> Optional[str]:
        """Get dashboard URL
        
        Returns:
            Dashboard URL or None
        """
        if self.spreadsheet_id:
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
        return None
        
    def get_status(self) -> Dict:
        """Get integration status
        
        Returns:
            Status dictionary
        """
        return {
            'connected': self.connected,
            'google_available': GOOGLE_AVAILABLE,
            'spreadsheet_id': self.spreadsheet_id,
            'dashboard_url': self.get_dashboard_url()
        }


# Test functionality
def test_google_sheets():
    """Test Google Sheets integration"""
    print("🧪 Testing Google Sheets Integration...")
    
    sheets = GoogleSheetsIntegration()
    
    if not sheets.connected:
        print("⚠️ Google Sheets not available, skipping tests")
        print("To enable:")
        print("1. Create a Google Cloud project")
        print("2. Enable Google Sheets API")
        print("3. Create service account and download credentials")
        print("4. Save credentials to /opt/tps19/config/google_credentials.json")
        return
        
    # Create dashboard
    spreadsheet_id = sheets.create_dashboard('TPS19 Test Dashboard')
    
    if spreadsheet_id:
        print(f"✅ Dashboard created: {spreadsheet_id}")
        
        # Update overview
        sheets.update_overview({
            'total_balance': '$10,487.32',
            'daily_profit': '+$127.53',
            'total_trades': '42',
            'win_rate': '68.2%',
            'sharpe_ratio': '2.3',
            'max_drawdown': '-5.2%',
            'active_positions': '3',
            'trading_status': 'Active',
            'strategies_active': '5',
            'ai_models_running': '3',
            'last_trade': '2 minutes ago'
        })
        print("✅ Overview updated")
        
        # Add trade
        sheets.add_trade({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'trade_id': 'TEST123',
            'symbol': 'BTC/USDT',
            'side': 'BUY',
            'type': 'MARKET',
            'price': '26,500.00',
            'amount': '0.01',
            'value': '265.00',
            'fee': '0.27',
            'strategy': 'Momentum',
            'profit_loss': '+$12.35',
            'status': 'CLOSED',
            'notes': 'Test trade'
        })
        print("✅ Trade added")
        
        print(f"📊 View dashboard: {sheets.get_dashboard_url()}")
        
    print(f"✅ Status: {sheets.get_status()}")


if __name__ == '__main__':
    test_google_sheets()
