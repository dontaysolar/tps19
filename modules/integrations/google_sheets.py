#!/usr/bin/env python3
"""Google Sheets Integration for Trading System"""

import json
import time
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("Google API client not installed. Install with: pip install google-api-python-client google-auth")

class GoogleSheetsIntegration:
    """Google Sheets integration for trading data and signals"""
    
    def __init__(self, credentials_path: str = None, spreadsheet_id: str = None):
        self.credentials_path = credentials_path or os.environ.get('GOOGLE_SHEETS_CREDS')
        self.spreadsheet_id = spreadsheet_id or os.environ.get('GOOGLE_SHEETS_ID')
        self.service = None
        self.db_path = "/opt/tps19/data/databases/google_sheets.db"
        
        # Initialize database for offline storage
        self.init_database()
        
        # Initialize Google Sheets API if available
        if GOOGLE_API_AVAILABLE and self.credentials_path and os.path.exists(self.credentials_path):
            self._init_google_service()
            
    def init_database(self):
        """Initialize local database for Google Sheets data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trading signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                price REAL NOT NULL,
                quantity REAL,
                confidence REAL,
                strategy TEXT,
                synced INTEGER DEFAULT 0
            )
        ''')
        
        # Portfolio positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL,
                pnl REAL,
                pnl_percent REAL,
                synced INTEGER DEFAULT 0
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_value REAL NOT NULL,
                daily_pnl REAL,
                total_pnl REAL,
                win_rate REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                synced INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _init_google_service(self):
        """Initialize Google Sheets API service"""
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=creds)
            print("✅ Google Sheets API initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Google Sheets API: {e}")
            self.service = None
            
    def log_trading_signal(self, signal: Dict) -> bool:
        """Log trading signal to database and optionally sync to Google Sheets"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert into database
            cursor.execute('''
                INSERT INTO trading_signals 
                (symbol, action, price, quantity, confidence, strategy)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                signal.get('symbol'),
                signal.get('action'),
                signal.get('price'),
                signal.get('quantity', 0),
                signal.get('confidence', 0),
                signal.get('strategy', 'unknown')
            ))
            
            signal_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Try to sync to Google Sheets
            if self.service and self.spreadsheet_id:
                self._sync_signal_to_sheets(signal_id, signal)
                
            return True
            
        except Exception as e:
            print(f"Error logging trading signal: {e}")
            return False
            
    def _sync_signal_to_sheets(self, signal_id: int, signal: Dict):
        """Sync individual signal to Google Sheets"""
        try:
            # Prepare row data
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                signal.get('symbol'),
                signal.get('action'),
                signal.get('price'),
                signal.get('quantity', 0),
                signal.get('confidence', 0),
                signal.get('strategy', 'unknown')
            ]
            
            # Append to Trading Signals sheet
            range_name = 'Trading Signals!A:G'
            body = {'values': [row_data]}
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            # Mark as synced in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE trading_signals SET synced = 1 WHERE id = ?",
                (signal_id,)
            )
            conn.commit()
            conn.close()
            
            print(f"✅ Signal synced to Google Sheets")
            
        except Exception as e:
            print(f"Error syncing signal to sheets: {e}")
            
    def update_portfolio_position(self, position: Dict) -> bool:
        """Update portfolio position in database and sheets"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate P&L
            entry_price = position.get('entry_price', 0)
            current_price = position.get('current_price', entry_price)
            quantity = position.get('quantity', 0)
            
            pnl = (current_price - entry_price) * quantity
            pnl_percent = ((current_price / entry_price) - 1) * 100 if entry_price > 0 else 0
            
            # Insert/update position
            cursor.execute('''
                INSERT OR REPLACE INTO portfolio_positions 
                (symbol, quantity, entry_price, current_price, pnl, pnl_percent)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                position.get('symbol'),
                quantity,
                entry_price,
                current_price,
                pnl,
                pnl_percent
            ))
            
            conn.commit()
            conn.close()
            
            # Sync to sheets if available
            if self.service and self.spreadsheet_id:
                self._sync_portfolio_to_sheets()
                
            return True
            
        except Exception as e:
            print(f"Error updating portfolio position: {e}")
            return False
            
    def _sync_portfolio_to_sheets(self):
        """Sync entire portfolio to Google Sheets"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all positions
            cursor.execute('''
                SELECT symbol, quantity, entry_price, current_price, pnl, pnl_percent
                FROM portfolio_positions
                ORDER BY symbol
            ''')
            
            positions = cursor.fetchall()
            conn.close()
            
            if not positions:
                return
                
            # Prepare data for sheets
            headers = ['Symbol', 'Quantity', 'Entry Price', 'Current Price', 'P&L', 'P&L %']
            rows = [headers]
            
            for pos in positions:
                rows.append([
                    pos[0],  # symbol
                    pos[1],  # quantity
                    f"${pos[2]:.2f}",  # entry_price
                    f"${pos[3]:.2f}",  # current_price
                    f"${pos[4]:.2f}",  # pnl
                    f"{pos[5]:.2f}%"  # pnl_percent
                ])
                
            # Clear and update Portfolio sheet
            range_name = 'Portfolio!A1:F'
            
            # Clear existing data
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            # Write new data
            body = {'values': rows}
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            print(f"✅ Portfolio synced to Google Sheets ({len(positions)} positions)")
            
        except Exception as e:
            print(f"Error syncing portfolio to sheets: {e}")
            
    def log_performance_metrics(self, metrics: Dict) -> bool:
        """Log performance metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (total_value, daily_pnl, total_pnl, win_rate, sharpe_ratio, max_drawdown)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                metrics.get('total_value', 0),
                metrics.get('daily_pnl', 0),
                metrics.get('total_pnl', 0),
                metrics.get('win_rate', 0),
                metrics.get('sharpe_ratio', 0),
                metrics.get('max_drawdown', 0)
            ))
            
            conn.commit()
            conn.close()
            
            # Sync to sheets
            if self.service and self.spreadsheet_id:
                self._sync_performance_to_sheets(metrics)
                
            return True
            
        except Exception as e:
            print(f"Error logging performance metrics: {e}")
            return False
            
    def _sync_performance_to_sheets(self, metrics: Dict):
        """Sync performance metrics to Google Sheets"""
        try:
            # Prepare row data
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                metrics.get('total_value', 0),
                metrics.get('daily_pnl', 0),
                metrics.get('total_pnl', 0),
                f"{metrics.get('win_rate', 0):.2f}%",
                metrics.get('sharpe_ratio', 0),
                f"{metrics.get('max_drawdown', 0):.2f}%"
            ]
            
            # Append to Performance sheet
            range_name = 'Performance!A:G'
            body = {'values': [row_data]}
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            print(f"✅ Performance metrics synced to Google Sheets")
            
        except Exception as e:
            print(f"Error syncing performance to sheets: {e}")
            
    def create_trading_spreadsheet(self) -> Optional[str]:
        """Create a new trading spreadsheet with proper structure"""
        if not self.service:
            print("Google Sheets service not available")
            return None
            
        try:
            # Create spreadsheet
            spreadsheet = {
                'properties': {
                    'title': f'TPS19 Trading System - {datetime.now().strftime("%Y-%m-%d")}'
                },
                'sheets': [
                    {'properties': {'title': 'Trading Signals'}},
                    {'properties': {'title': 'Portfolio'}},
                    {'properties': {'title': 'Performance'}},
                    {'properties': {'title': 'Market Data'}}
                ]
            }
            
            spreadsheet = self.service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId'
            ).execute()
            
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            print(f"✅ Created new spreadsheet with ID: {spreadsheet_id}")
            
            # Add headers to each sheet
            self._setup_spreadsheet_headers(spreadsheet_id)
            
            return spreadsheet_id
            
        except Exception as e:
            print(f"Error creating spreadsheet: {e}")
            return None
            
    def _setup_spreadsheet_headers(self, spreadsheet_id: str):
        """Setup headers for each sheet in the spreadsheet"""
        headers = {
            'Trading Signals!A1:G1': [['Timestamp', 'Symbol', 'Action', 'Price', 'Quantity', 'Confidence', 'Strategy']],
            'Portfolio!A1:F1': [['Symbol', 'Quantity', 'Entry Price', 'Current Price', 'P&L', 'P&L %']],
            'Performance!A1:G1': [['Timestamp', 'Total Value', 'Daily P&L', 'Total P&L', 'Win Rate', 'Sharpe Ratio', 'Max Drawdown']],
            'Market Data!A1:E1': [['Timestamp', 'Symbol', 'Price', 'Volume', 'Change %']]
        }
        
        for range_name, values in headers.items():
            try:
                body = {'values': values}
                self.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()
            except Exception as e:
                print(f"Error setting up headers for {range_name}: {e}")
                
    def sync_all_data(self):
        """Sync all unsynced data to Google Sheets"""
        if not self.service or not self.spreadsheet_id:
            print("Google Sheets sync not available")
            return
            
        print("🔄 Starting full data sync to Google Sheets...")
        
        # Sync portfolio
        self._sync_portfolio_to_sheets()
        
        # Sync unsynced signals
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, symbol, action, price, quantity, confidence, strategy
            FROM trading_signals
            WHERE synced = 0
        ''')
        
        signals = cursor.fetchall()
        
        for signal in signals:
            signal_dict = {
                'symbol': signal[1],
                'action': signal[2],
                'price': signal[3],
                'quantity': signal[4],
                'confidence': signal[5],
                'strategy': signal[6]
            }
            self._sync_signal_to_sheets(signal[0], signal_dict)
            
        conn.close()
        
        print(f"✅ Sync complete. Synced {len(signals)} new signals")
        
    def test_connection(self) -> bool:
        """Test Google Sheets connection"""
        if not self.service:
            return False
            
        try:
            # Try to get spreadsheet metadata
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            print(f"✅ Connected to spreadsheet: {sheet_metadata.get('properties', {}).get('title')}")
            return True
            
        except Exception as e:
            print(f"❌ Google Sheets connection failed: {e}")
            return False

# Global instance
google_sheets = GoogleSheetsIntegration()

if __name__ == "__main__":
    # Test the integration
    print("Testing Google Sheets Integration...")
    print("=" * 60)
    
    # Test without actual Google API (using local database)
    sheets = GoogleSheetsIntegration()
    
    # Log a test signal
    test_signal = {
        'symbol': 'BTC/USDT',
        'action': 'BUY',
        'price': 45000,
        'quantity': 0.1,
        'confidence': 0.85,
        'strategy': 'trend_following'
    }
    
    if sheets.log_trading_signal(test_signal):
        print("✅ Test signal logged successfully")
    
    # Update test portfolio position
    test_position = {
        'symbol': 'BTC/USDT',
        'quantity': 0.1,
        'entry_price': 45000,
        'current_price': 46000
    }
    
    if sheets.update_portfolio_position(test_position):
        print("✅ Test position updated successfully")
    
    # Log test performance metrics
    test_metrics = {
        'total_value': 10500,
        'daily_pnl': 100,
        'total_pnl': 500,
        'win_rate': 65.5,
        'sharpe_ratio': 1.85,
        'max_drawdown': 5.2
    }
    
    if sheets.log_performance_metrics(test_metrics):
        print("✅ Test metrics logged successfully")