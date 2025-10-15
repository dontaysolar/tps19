#!/usr/bin/env python3
"""TPS19 Google Sheets Integration - Data logging and reporting"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import sqlite3

class GoogleSheetsIntegration:
    """Google Sheets Integration for TPS19 Trading System"""
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, spreadsheet_id: str = None, credentials_file: str = None):
        self.spreadsheet_id = spreadsheet_id or os.getenv('GOOGLE_SHEETS_ID', '')
        self.credentials_file = credentials_file or 'credentials.json'
        self.token_file = 'token.json'
        self.service = None
        self.db_path = "/workspace/data/databases/google_sheets_log.db"
        
        self._init_database()
        self._authenticate()
        
    def _init_database(self):
        """Initialize database for Google Sheets logging"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Data sync log table
            cursor.execute("""CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_type TEXT NOT NULL,
                record_id TEXT NOT NULL,
                synced_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'PENDING',
                error_message TEXT
            )""")
            
            # Trading data table
            cursor.execute("""CREATE TABLE IF NOT EXISTS trading_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                commission REAL NOT NULL,
                pnl REAL DEFAULT 0,
                synced_to_sheets BOOLEAN DEFAULT FALSE
            )""")
            
            # Portfolio data table
            cursor.execute("""CREATE TABLE IF NOT EXISTS portfolio_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                balance REAL NOT NULL,
                total_value REAL NOT NULL,
                total_pnl REAL NOT NULL,
                positions_count INTEGER NOT NULL,
                synced_to_sheets BOOLEAN DEFAULT FALSE
            )""")
            
            # Market data table
            cursor.execute("""CREATE TABLE IF NOT EXISTS market_data_sheets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume_24h REAL,
                change_24h REAL,
                high_24h REAL,
                low_24h REAL,
                synced_to_sheets BOOLEAN DEFAULT FALSE
            )""")
            
            conn.commit()
            conn.close()
            print("✅ Google Sheets database initialized")
            
        except Exception as e:
            print(f"❌ Google Sheets database initialization failed: {e}")
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            creds = None
            
            # The file token.json stores the user's access and refresh tokens.
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
            
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        print(f"❌ Credentials file {self.credentials_file} not found")
                        print("Please download credentials.json from Google Cloud Console")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('sheets', 'v4', credentials=creds)
            print("✅ Google Sheets authentication successful")
            return True
            
        except Exception as e:
            print(f"❌ Google Sheets authentication failed: {e}")
            return False
    
    def _get_sheet_values(self, range_name: str) -> List[List]:
        """Get values from a Google Sheet"""
        try:
            if not self.service or not self.spreadsheet_id:
                return []
            
            sheet = self.service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            return result.get('values', [])
            
        except HttpError as e:
            print(f"❌ Error getting sheet values: {e}")
            return []
    
    def _update_sheet_values(self, range_name: str, values: List[List]) -> bool:
        """Update values in a Google Sheet"""
        try:
            if not self.service or not self.spreadsheet_id:
                return False
            
            body = {'values': values}
            sheet = self.service.spreadsheets()
            result = sheet.values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            return True
            
        except HttpError as e:
            print(f"❌ Error updating sheet values: {e}")
            return False
    
    def _append_sheet_values(self, range_name: str, values: List[List]) -> bool:
        """Append values to a Google Sheet"""
        try:
            if not self.service or not self.spreadsheet_id:
                return False
            
            body = {'values': values}
            sheet = self.service.spreadsheets()
            result = sheet.values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return True
            
        except HttpError as e:
            print(f"❌ Error appending sheet values: {e}")
            return False
    
    def log_trade(self, trade_data: Dict) -> bool:
        """Log trade data to Google Sheets"""
        try:
            # Store in local database first
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""INSERT INTO trading_data 
                (timestamp, symbol, side, quantity, price, commission, pnl)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (trade_data.get('timestamp', datetime.now().isoformat()),
                 trade_data.get('symbol', ''),
                 trade_data.get('side', ''),
                 trade_data.get('quantity', 0),
                 trade_data.get('price', 0),
                 trade_data.get('commission', 0),
                 trade_data.get('pnl', 0)))
            
            record_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Prepare data for Google Sheets
            values = [[
                trade_data.get('timestamp', datetime.now().isoformat()),
                trade_data.get('symbol', ''),
                trade_data.get('side', ''),
                trade_data.get('quantity', 0),
                trade_data.get('price', 0),
                trade_data.get('commission', 0),
                trade_data.get('pnl', 0)
            ]]
            
            # Append to Google Sheets
            success = self._append_sheet_values('Trading Data!A:G', values)
            
            if success:
                # Mark as synced
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE trading_data SET synced_to_sheets = TRUE WHERE id = ?", (record_id,))
                conn.commit()
                conn.close()
                
                print("✅ Trade data logged to Google Sheets")
                return True
            else:
                print("❌ Failed to log trade data to Google Sheets")
                return False
                
        except Exception as e:
            print(f"❌ Trade logging error: {e}")
            return False
    
    def log_portfolio_update(self, portfolio_data: Dict) -> bool:
        """Log portfolio update to Google Sheets"""
        try:
            # Store in local database first
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""INSERT INTO portfolio_data 
                (timestamp, balance, total_value, total_pnl, positions_count)
                VALUES (?, ?, ?, ?, ?)""",
                (datetime.now().isoformat(),
                 portfolio_data.get('balance', 0),
                 portfolio_data.get('total_value', 0),
                 portfolio_data.get('total_pnl', 0),
                 portfolio_data.get('positions', 0)))
            
            record_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Prepare data for Google Sheets
            values = [[
                datetime.now().isoformat(),
                portfolio_data.get('balance', 0),
                portfolio_data.get('total_value', 0),
                portfolio_data.get('total_pnl', 0),
                portfolio_data.get('positions', 0)
            ]]
            
            # Append to Google Sheets
            success = self._append_sheet_values('Portfolio Data!A:E', values)
            
            if success:
                # Mark as synced
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE portfolio_data SET synced_to_sheets = TRUE WHERE id = ?", (record_id,))
                conn.commit()
                conn.close()
                
                print("✅ Portfolio data logged to Google Sheets")
                return True
            else:
                print("❌ Failed to log portfolio data to Google Sheets")
                return False
                
        except Exception as e:
            print(f"❌ Portfolio logging error: {e}")
            return False
    
    def log_market_data(self, market_data: Dict) -> bool:
        """Log market data to Google Sheets"""
        try:
            # Store in local database first
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""INSERT INTO market_data_sheets 
                (timestamp, symbol, price, volume_24h, change_24h, high_24h, low_24h)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (datetime.now().isoformat(),
                 market_data.get('symbol', ''),
                 market_data.get('price', 0),
                 market_data.get('volume_24h', 0),
                 market_data.get('change_24h', 0),
                 market_data.get('high_24h', 0),
                 market_data.get('low_24h', 0)))
            
            record_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Prepare data for Google Sheets
            values = [[
                datetime.now().isoformat(),
                market_data.get('symbol', ''),
                market_data.get('price', 0),
                market_data.get('volume_24h', 0),
                market_data.get('change_24h', 0),
                market_data.get('high_24h', 0),
                market_data.get('low_24h', 0)
            ]]
            
            # Append to Google Sheets
            success = self._append_sheet_values('Market Data!A:G', values)
            
            if success:
                # Mark as synced
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE market_data_sheets SET synced_to_sheets = TRUE WHERE id = ?", (record_id,))
                conn.commit()
                conn.close()
                
                print("✅ Market data logged to Google Sheets")
                return True
            else:
                print("❌ Failed to log market data to Google Sheets")
                return False
                
        except Exception as e:
            print(f"❌ Market data logging error: {e}")
            return False
    
    def create_dashboard(self) -> bool:
        """Create a trading dashboard in Google Sheets"""
        try:
            if not self.service or not self.spreadsheet_id:
                return False
            
            # Create headers for different sheets
            trading_headers = [['Timestamp', 'Symbol', 'Side', 'Quantity', 'Price', 'Commission', 'P&L']]
            portfolio_headers = [['Timestamp', 'Balance', 'Total Value', 'Total P&L', 'Positions Count']]
            market_headers = [['Timestamp', 'Symbol', 'Price', 'Volume 24h', 'Change 24h', 'High 24h', 'Low 24h']]
            
            # Create trading data sheet
            self._update_sheet_values('Trading Data!A1:G1', trading_headers)
            
            # Create portfolio data sheet
            self._update_sheet_values('Portfolio Data!A1:E1', portfolio_headers)
            
            # Create market data sheet
            self._update_sheet_values('Market Data!A1:G1', market_headers)
            
            # Create summary dashboard
            summary_data = [
                ['TPS19 Trading Dashboard'],
                ['Last Updated:', '=NOW()'],
                [''],
                ['Portfolio Summary'],
                ['Balance:', '=INDEX(Portfolio Data!B:B,COUNTA(Portfolio Data!B:B))'],
                ['Total Value:', '=INDEX(Portfolio Data!C:C,COUNTA(Portfolio Data!C:C))'],
                ['Total P&L:', '=INDEX(Portfolio Data!D:D,COUNTA(Portfolio Data!D:D))'],
                [''],
                ['Recent Trades'],
                ['=QUERY(Trading Data!A:G,"SELECT * ORDER BY A DESC LIMIT 10")']
            ]
            
            self._update_sheet_values('Dashboard!A1', summary_data)
            
            print("✅ Trading dashboard created in Google Sheets")
            return True
            
        except Exception as e:
            print(f"❌ Dashboard creation error: {e}")
            return False
    
    def sync_pending_data(self) -> bool:
        """Sync all pending data to Google Sheets"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Sync trading data
            cursor.execute("SELECT * FROM trading_data WHERE synced_to_sheets = FALSE")
            trading_data = cursor.fetchall()
            
            if trading_data:
                values = []
                for row in trading_data:
                    values.append([row[1], row[2], row[3], row[4], row[5], row[6], row[7]])  # Skip ID
                
                if self._append_sheet_values('Trading Data!A:G', values):
                    cursor.execute("UPDATE trading_data SET synced_to_sheets = TRUE WHERE synced_to_sheets = FALSE")
                    conn.commit()
            
            # Sync portfolio data
            cursor.execute("SELECT * FROM portfolio_data WHERE synced_to_sheets = FALSE")
            portfolio_data = cursor.fetchall()
            
            if portfolio_data:
                values = []
                for row in portfolio_data:
                    values.append([row[1], row[2], row[3], row[4], row[5]])  # Skip ID
                
                if self._append_sheet_values('Portfolio Data!A:E', values):
                    cursor.execute("UPDATE portfolio_data SET synced_to_sheets = TRUE WHERE synced_to_sheets = FALSE")
                    conn.commit()
            
            # Sync market data
            cursor.execute("SELECT * FROM market_data_sheets WHERE synced_to_sheets = FALSE")
            market_data = cursor.fetchall()
            
            if market_data:
                values = []
                for row in market_data:
                    values.append([row[1], row[2], row[3], row[4], row[5], row[6], row[7]])  # Skip ID
                
                if self._append_sheet_values('Market Data!A:G', values):
                    cursor.execute("UPDATE market_data_sheets SET synced_to_sheets = TRUE WHERE synced_to_sheets = FALSE")
                    conn.commit()
            
            conn.close()
            print("✅ Pending data synced to Google Sheets")
            return True
            
        except Exception as e:
            print(f"❌ Data sync error: {e}")
            return False
    
    def test_google_sheets(self) -> bool:
        """Test Google Sheets integration"""
        try:
            print("🧪 Testing Google Sheets Integration...")
            
            if not self.service:
                print("❌ Google Sheets service not available")
                return False
            
            # Test creating dashboard
            if not self.create_dashboard():
                print("❌ Dashboard creation test failed")
                return False
            
            # Test logging sample data
            sample_trade = {
                'timestamp': datetime.now().isoformat(),
                'symbol': 'BTC_USDT',
                'side': 'BUY',
                'quantity': 0.001,
                'price': 50000,
                'commission': 0.05,
                'pnl': 0
            }
            
            if not self.log_trade(sample_trade):
                print("❌ Trade logging test failed")
                return False
            
            print("✅ Google Sheets integration test passed")
            return True
            
        except Exception as e:
            print(f"❌ Google Sheets test error: {e}")
            return False

# Global instance
google_sheets = GoogleSheetsIntegration()
