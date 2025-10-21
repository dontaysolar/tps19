#!/usr/bin/env python3
"""
Google Sheets Integration for APEX Trading System
Trade tracking, reporting, and dashboard integration
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import pandas as pd

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError as e:
    print(f"❌ Missing Google Sheets dependencies: {e}")
    print("Installing required packages...")
    os.system("pip3 install --break-system-packages google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client -q")
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

class GoogleSheetsHandler:
    """
    Google Sheets integration for trading data
    Features:
    - Trade logging
    - Performance tracking
    - Portfolio monitoring
    - Real-time updates
    - Dashboard integration
    """
    
    # Scopes for Google Sheets API
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.creds = None
        
        # Spreadsheet configuration
        self.spreadsheet_id = None
        self.sheets = {
            'trades': 'Trades',
            'positions': 'Positions',
            'performance': 'Performance',
            'alerts': 'Alerts',
            'bot_status': 'Bot Status',
            'market_data': 'Market Data'
        }
        
        self._authenticate()
    
    def _authenticate(self) -> bool:
        """Authenticate with Google Sheets API"""
        try:
            # Load existing credentials
            if os.path.exists(self.token_file):
                self.creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
            
            # If no valid credentials, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        print(f"❌ Credentials file not found: {self.credentials_file}")
                        print("Please download credentials.json from Google Cloud Console")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.token_file, 'w') as token:
                    token.write(self.creds.to_json())
            
            # Build service
            self.service = build('sheets', 'v4', credentials=self.creds)
            print("✅ Google Sheets authentication successful")
            return True
            
        except Exception as e:
            print(f"❌ Google Sheets authentication failed: {e}")
            return False
    
    def create_spreadsheet(self, title: str = "APEX Trading Dashboard") -> Optional[str]:
        """Create a new spreadsheet"""
        if not self.service:
            return None
        
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                },
                'sheets': [
                    {
                        'properties': {
                            'title': self.sheets['trades'],
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 20
                            }
                        }
                    },
                    {
                        'properties': {
                            'title': self.sheets['positions'],
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 15
                            }
                        }
                    },
                    {
                        'properties': {
                            'title': self.sheets['performance'],
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 10
                            }
                        }
                    },
                    {
                        'properties': {
                            'title': self.sheets['alerts'],
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 8
                            }
                        }
                    },
                    {
                        'properties': {
                            'title': self.sheets['bot_status'],
                            'gridProperties': {
                                'rowCount': 100,
                                'columnCount': 10
                            }
                        }
                    },
                    {
                        'properties': {
                            'title': self.sheets['market_data'],
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 12
                            }
                        }
                    }
                ]
            }
            
            spreadsheet = self.service.spreadsheets().create(body=spreadsheet).execute()
            self.spreadsheet_id = spreadsheet.get('spreadsheetId')
            
            # Set up headers
            self._setup_headers()
            
            print(f"✅ Spreadsheet created: {self.spreadsheet_id}")
            return self.spreadsheet_id
            
        except HttpError as e:
            print(f"❌ Error creating spreadsheet: {e}")
            return None
    
    def set_spreadsheet_id(self, spreadsheet_id: str) -> bool:
        """Set existing spreadsheet ID"""
        self.spreadsheet_id = spreadsheet_id
        return True
    
    def _setup_headers(self) -> bool:
        """Set up headers for all sheets"""
        if not self.spreadsheet_id:
            return False
        
        try:
            # Trades sheet headers
            trades_headers = [
                'Timestamp', 'Trade ID', 'Symbol', 'Side', 'Amount', 'Price', 
                'Value', 'Profit', 'Profit %', 'Status', 'Strategy', 'Confidence',
                'Entry Time', 'Exit Time', 'Duration', 'Fees', 'Slippage', 'Notes'
            ]
            self._write_data(self.sheets['trades'], 'A1', [trades_headers])
            
            # Positions sheet headers
            positions_headers = [
                'Position ID', 'Symbol', 'Side', 'Amount', 'Entry Price', 'Current Price',
                'Unrealized P&L', 'Unrealized %', 'Stop Loss', 'Take Profit', 'Status',
                'Entry Time', 'Last Update', 'Strategy'
            ]
            self._write_data(self.sheets['positions'], 'A1', [positions_headers])
            
            # Performance sheet headers
            performance_headers = [
                'Date', 'Total Trades', 'Winning Trades', 'Losing Trades', 'Win Rate %',
                'Total Profit', 'Total Volume', 'Best Trade', 'Worst Trade', 'Sharpe Ratio'
            ]
            self._write_data(self.sheets['performance'], 'A1', [performance_headers])
            
            # Alerts sheet headers
            alerts_headers = [
                'Timestamp', 'Type', 'Severity', 'Message', 'Symbol', 'Value', 'Status', 'Notes'
            ]
            self._write_data(self.sheets['alerts'], 'A1', [alerts_headers])
            
            # Bot status sheet headers
            bot_headers = [
                'Bot Name', 'Status', 'Last Update', 'Trades Executed', 'Success Rate %',
                'Total Profit', 'Active Positions', 'Error Count', 'Uptime %', 'Version'
            ]
            self._write_data(self.sheets['bot_status'], 'A1', [bot_headers])
            
            # Market data sheet headers
            market_headers = [
                'Timestamp', 'Symbol', 'Price', 'Volume', 'Change 24h %', 'High 24h',
                'Low 24h', 'Market Cap', 'Sentiment', 'RSI', 'MACD', 'Trend'
            ]
            self._write_data(self.sheets['market_data'], 'A1', [market_headers])
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up headers: {e}")
            return False
    
    def _write_data(self, sheet_name: str, range_name: str, values: List[List]) -> bool:
        """Write data to a specific range in the sheet"""
        if not self.service or not self.spreadsheet_id:
            return False
        
        try:
            body = {'values': values}
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!{range_name}",
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
        except HttpError as e:
            print(f"❌ Error writing data to {sheet_name}: {e}")
            return False
    
    def _read_data(self, sheet_name: str, range_name: str) -> Optional[List[List]]:
        """Read data from a specific range in the sheet"""
        if not self.service or not self.spreadsheet_id:
            return None
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!{range_name}"
            ).execute()
            
            return result.get('values', [])
        except HttpError as e:
            print(f"❌ Error reading data from {sheet_name}: {e}")
            return None
    
    def log_trade(self, trade_data: Dict) -> bool:
        """Log a trade to the trades sheet"""
        try:
            # Prepare trade row
            trade_row = [
                trade_data.get('timestamp', datetime.now().isoformat()),
                trade_data.get('trade_id', ''),
                trade_data.get('symbol', ''),
                trade_data.get('side', ''),
                trade_data.get('amount', 0),
                trade_data.get('price', 0),
                trade_data.get('value', 0),
                trade_data.get('profit', 0),
                trade_data.get('profit_pct', 0),
                trade_data.get('status', 'open'),
                trade_data.get('strategy', ''),
                trade_data.get('confidence', 0),
                trade_data.get('entry_time', ''),
                trade_data.get('exit_time', ''),
                trade_data.get('duration', ''),
                trade_data.get('fees', 0),
                trade_data.get('slippage', 0),
                trade_data.get('notes', '')
            ]
            
            # Find next empty row
            next_row = self._get_next_empty_row(self.sheets['trades'])
            range_name = f"A{next_row}:R{next_row}"
            
            return self._write_data(self.sheets['trades'], range_name, [trade_row])
            
        except Exception as e:
            print(f"❌ Error logging trade: {e}")
            return False
    
    def update_position(self, position_data: Dict) -> bool:
        """Update position in the positions sheet"""
        try:
            # Prepare position row
            position_row = [
                position_data.get('position_id', ''),
                position_data.get('symbol', ''),
                position_data.get('side', ''),
                position_data.get('amount', 0),
                position_data.get('entry_price', 0),
                position_data.get('current_price', 0),
                position_data.get('unrealized_pnl', 0),
                position_data.get('unrealized_pct', 0),
                position_data.get('stop_loss', 0),
                position_data.get('take_profit', 0),
                position_data.get('status', 'open'),
                position_data.get('entry_time', ''),
                position_data.get('last_update', datetime.now().isoformat()),
                position_data.get('strategy', '')
            ]
            
            # Find existing position or add new
            position_id = position_data.get('position_id', '')
            row = self._find_position_row(position_id)
            
            if row is None:
                # Add new position
                next_row = self._get_next_empty_row(self.sheets['positions'])
                range_name = f"A{next_row}:N{next_row}"
            else:
                # Update existing position
                range_name = f"A{row}:N{row}"
            
            return self._write_data(self.sheets['positions'], range_name, [position_row])
            
        except Exception as e:
            print(f"❌ Error updating position: {e}")
            return False
    
    def log_performance(self, performance_data: Dict) -> bool:
        """Log daily performance metrics"""
        try:
            # Prepare performance row
            perf_row = [
                performance_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                performance_data.get('total_trades', 0),
                performance_data.get('winning_trades', 0),
                performance_data.get('losing_trades', 0),
                performance_data.get('win_rate', 0),
                performance_data.get('total_profit', 0),
                performance_data.get('total_volume', 0),
                performance_data.get('best_trade', 0),
                performance_data.get('worst_trade', 0),
                performance_data.get('sharpe_ratio', 0)
            ]
            
            # Find next empty row
            next_row = self._get_next_empty_row(self.sheets['performance'])
            range_name = f"A{next_row}:J{next_row}"
            
            return self._write_data(self.sheets['performance'], range_name, [perf_row])
            
        except Exception as e:
            print(f"❌ Error logging performance: {e}")
            return False
    
    def log_alert(self, alert_data: Dict) -> bool:
        """Log an alert to the alerts sheet"""
        try:
            # Prepare alert row
            alert_row = [
                alert_data.get('timestamp', datetime.now().isoformat()),
                alert_data.get('type', ''),
                alert_data.get('severity', 'info'),
                alert_data.get('message', ''),
                alert_data.get('symbol', ''),
                alert_data.get('value', ''),
                alert_data.get('status', 'active'),
                alert_data.get('notes', '')
            ]
            
            # Find next empty row
            next_row = self._get_next_empty_row(self.sheets['alerts'])
            range_name = f"A{next_row}:H{next_row}"
            
            return self._write_data(self.sheets['alerts'], range_name, [alert_row])
            
        except Exception as e:
            print(f"❌ Error logging alert: {e}")
            return False
    
    def update_bot_status(self, bot_name: str, status_data: Dict) -> bool:
        """Update bot status in the bot status sheet"""
        try:
            # Prepare bot status row
            bot_row = [
                bot_name,
                status_data.get('status', 'unknown'),
                status_data.get('last_update', datetime.now().isoformat()),
                status_data.get('trades_executed', 0),
                status_data.get('success_rate', 0),
                status_data.get('total_profit', 0),
                status_data.get('active_positions', 0),
                status_data.get('error_count', 0),
                status_data.get('uptime', 0),
                status_data.get('version', '1.0.0')
            ]
            
            # Find existing bot or add new
            row = self._find_bot_row(bot_name)
            
            if row is None:
                # Add new bot
                next_row = self._get_next_empty_row(self.sheets['bot_status'])
                range_name = f"A{next_row}:J{next_row}"
            else:
                # Update existing bot
                range_name = f"A{row}:J{row}"
            
            return self._write_data(self.sheets['bot_status'], range_name, [bot_row])
            
        except Exception as e:
            print(f"❌ Error updating bot status: {e}")
            return False
    
    def log_market_data(self, market_data: Dict) -> bool:
        """Log market data to the market data sheet"""
        try:
            # Prepare market data row
            market_row = [
                market_data.get('timestamp', datetime.now().isoformat()),
                market_data.get('symbol', ''),
                market_data.get('price', 0),
                market_data.get('volume', 0),
                market_data.get('change_24h', 0),
                market_data.get('high_24h', 0),
                market_data.get('low_24h', 0),
                market_data.get('market_cap', 0),
                market_data.get('sentiment', 0),
                market_data.get('rsi', 0),
                market_data.get('macd', 0),
                market_data.get('trend', '')
            ]
            
            # Find next empty row
            next_row = self._get_next_empty_row(self.sheets['market_data'])
            range_name = f"A{next_row}:L{next_row}"
            
            return self._write_data(self.sheets['market_data'], range_name, [market_row])
            
        except Exception as e:
            print(f"❌ Error logging market data: {e}")
            return False
    
    def _get_next_empty_row(self, sheet_name: str) -> int:
        """Find the next empty row in a sheet"""
        try:
            # Read all data to find last row
            data = self._read_data(sheet_name, 'A:A')
            if not data:
                return 2  # Start after header
            
            return len(data) + 1
        except Exception:
            return 2
    
    def _find_position_row(self, position_id: str) -> Optional[int]:
        """Find row number for a position ID"""
        try:
            data = self._read_data(self.sheets['positions'], 'A:A')
            for i, row in enumerate(data):
                if row and row[0] == position_id:
                    return i + 1
            return None
        except Exception:
            return None
    
    def _find_bot_row(self, bot_name: str) -> Optional[int]:
        """Find row number for a bot name"""
        try:
            data = self._read_data(self.sheets['bot_status'], 'A:A')
            for i, row in enumerate(data):
                if row and row[0] == bot_name:
                    return i + 1
            return None
        except Exception:
            return None
    
    def get_trading_summary(self) -> Dict:
        """Get trading summary from sheets"""
        try:
            # Get recent trades
            trades_data = self._read_data(self.sheets['trades'], 'A2:R1000')
            
            if not trades_data:
                return {}
            
            # Calculate summary
            total_trades = len(trades_data)
            winning_trades = len([t for t in trades_data if float(t[7] or 0) > 0])
            losing_trades = len([t for t in trades_data if float(t[7] or 0) < 0])
            
            total_profit = sum(float(t[7] or 0) for t in trades_data)
            total_volume = sum(float(t[6] or 0) for t in trades_data)
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_profit': total_profit,
                'total_volume': total_volume,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Error getting trading summary: {e}")
            return {}
    
    def get_spreadsheet_url(self) -> Optional[str]:
        """Get the spreadsheet URL"""
        if self.spreadsheet_id:
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
        return None


class SheetsManager:
    """
    High-level Google Sheets manager
    Coordinates multiple sheet operations
    """
    
    def __init__(self, spreadsheet_id: str = None):
        self.sheets_handler = GoogleSheetsHandler()
        
        if spreadsheet_id:
            self.sheets_handler.set_spreadsheet_id(spreadsheet_id)
        else:
            # Create new spreadsheet
            spreadsheet_id = self.sheets_handler.create_spreadsheet()
            if not spreadsheet_id:
                raise Exception("Failed to create spreadsheet")
    
    def sync_trading_data(self, trades: List[Dict], positions: List[Dict], 
                         performance: Dict, alerts: List[Dict]) -> bool:
        """Sync all trading data to sheets"""
        try:
            # Log trades
            for trade in trades:
                self.sheets_handler.log_trade(trade)
            
            # Update positions
            for position in positions:
                self.sheets_handler.update_position(position)
            
            # Log performance
            if performance:
                self.sheets_handler.log_performance(performance)
            
            # Log alerts
            for alert in alerts:
                self.sheets_handler.log_alert(alert)
            
            return True
        except Exception as e:
            print(f"❌ Error syncing trading data: {e}")
            return False
    
    def get_dashboard_data(self) -> Dict:
        """Get data for dashboard display"""
        try:
            summary = self.sheets_handler.get_trading_summary()
            
            # Get recent trades
            recent_trades = self.sheets_handler._read_data(
                self.sheets_handler.sheets['trades'], 'A2:R10'
            )
            
            # Get active positions
            positions = self.sheets_handler._read_data(
                self.sheets_handler.sheets['positions'], 'A2:N100'
            )
            
            # Get recent alerts
            alerts = self.sheets_handler._read_data(
                self.sheets_handler.sheets['alerts'], 'A2:H20'
            )
            
            return {
                'summary': summary,
                'recent_trades': recent_trades,
                'positions': positions,
                'alerts': alerts,
                'spreadsheet_url': self.sheets_handler.get_spreadsheet_url()
            }
        except Exception as e:
            print(f"❌ Error getting dashboard data: {e}")
            return {}


if __name__ == '__main__':
    print("📊 Google Sheets Handler Test\n")
    
    # Test Google Sheets integration
    try:
        sheets = GoogleSheetsHandler()
        
        if sheets.service:
            print("✅ Google Sheets authentication successful")
            
            # Create test spreadsheet
            spreadsheet_id = sheets.create_spreadsheet("APEX Test Dashboard")
            if spreadsheet_id:
                print(f"✅ Test spreadsheet created: {spreadsheet_id}")
                
                # Test logging trade
                test_trade = {
                    'trade_id': 'test_001',
                    'symbol': 'BTC/USDT',
                    'side': 'buy',
                    'amount': 0.001,
                    'price': 50000.0,
                    'value': 50.0,
                    'profit': 0.0,
                    'status': 'open',
                    'strategy': 'test'
                }
                
                if sheets.log_trade(test_trade):
                    print("✅ Test trade logged")
                
                # Test logging alert
                test_alert = {
                    'type': 'trade_executed',
                    'severity': 'info',
                    'message': 'Test trade executed successfully',
                    'symbol': 'BTC/USDT'
                }
                
                if sheets.log_alert(test_alert):
                    print("✅ Test alert logged")
                
                # Get summary
                summary = sheets.get_trading_summary()
                print(f"✅ Trading summary: {summary}")
                
                print(f"\n📊 Dashboard URL: {sheets.get_spreadsheet_url()}")
            else:
                print("❌ Failed to create test spreadsheet")
        else:
            print("❌ Google Sheets authentication failed")
            print("Please ensure credentials.json is in the project directory")
    
    except Exception as e:
        print(f"❌ Google Sheets test failed: {e}")
    
    print("\n✅ Google Sheets handler test completed!")