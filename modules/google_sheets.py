#!/usr/bin/env python3
"""
TPS19 Google Sheets Integration
Real-time data logging and reporting to Google Sheets
"""

import os
import json
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class TPS19SheetsIntegration:
    def __init__(self):
        self.config_path = "/workspace/config/api_config.json"
        self.credentials_path = "/workspace/config/google_credentials.json"
        self.db_path = "/opt/tps19/data/databases/sheets.db"
        self.load_config()
        self.init_database()
        self.client = None
        self.spreadsheet = None
        
    def load_config(self):
        """Load Google Sheets configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.config = config.get('google_sheets', {})
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            self.config = {
                "scope": [
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive"
                ]
            }
            
    def init_database(self):
        """Initialize Sheets tracking database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sheet_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    sheet_name TEXT,
                    operation TEXT,
                    data TEXT,
                    success BOOLEAN DEFAULT FALSE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trade_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT,
                    action TEXT,
                    price REAL,
                    quantity REAL,
                    confidence REAL,
                    profit_loss REAL DEFAULT 0,
                    logged_to_sheets BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.commit()
            conn.close()
            print("✅ Google Sheets database initialized")
        except Exception as e:
            print(f"❌ Google Sheets database error: {e}")
            
    def authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            if not os.path.exists(self.credentials_path):
                print("❌ Google credentials file not found")
                return False
                
            scope = self.config.get('scope', [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ])
            
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_path, scope
            )
            self.client = gspread.authorize(credentials)
            print("✅ Google Sheets authenticated")
            return True
        except Exception as e:
            print(f"❌ Google Sheets authentication error: {e}")
            return False
            
    def get_or_create_spreadsheet(self, spreadsheet_name: str = "TPS19_Trading_Log"):
        """Get or create trading spreadsheet"""
        try:
            if not self.client:
                if not self.authenticate():
                    return None
                    
            try:
                self.spreadsheet = self.client.open(spreadsheet_name)
                print(f"✅ Opened existing spreadsheet: {spreadsheet_name}")
            except gspread.SpreadsheetNotFound:
                self.spreadsheet = self.client.create(spreadsheet_name)
                print(f"✅ Created new spreadsheet: {spreadsheet_name}")
                self.setup_sheets()
                
            return self.spreadsheet
        except Exception as e:
            print(f"❌ Error with spreadsheet: {e}")
            return None
            
    def setup_sheets(self):
        """Setup initial sheets and headers"""
        try:
            # Trading Log Sheet
            trading_sheet = self.spreadsheet.sheet1
            trading_sheet.update('A1:H1', [[
                'Timestamp', 'Symbol', 'Action', 'Price', 'Quantity', 
                'Confidence', 'P&L', 'Notes'
            ]])
            trading_sheet.update_title("Trading_Log")
            
            # Market Data Sheet
            market_sheet = self.spreadsheet.add_worksheet(title="Market_Data", rows="1000", cols="10")
            market_sheet.update('A1:F1', [[
                'Timestamp', 'Symbol', 'Price', 'Volume', '24h_Change', 'Source'
            ]])
            
            # System Status Sheet
            status_sheet = self.spreadsheet.add_worksheet(title="System_Status", rows="1000", cols="8")
            status_sheet.update('A1:E1', [[
                'Timestamp', 'Component', 'Status', 'Message', 'Uptime'
            ]])
            
            print("✅ Sheets setup completed")
        except Exception as e:
            print(f"❌ Error setting up sheets: {e}")
            
    def log_trade(self, symbol: str, action: str, price: float, quantity: float = 0.0, 
                  confidence: float = 0.0, profit_loss: float = 0.0, notes: str = ""):
        """Log trade to Google Sheets"""
        try:
            if not self.spreadsheet:
                if not self.get_or_create_spreadsheet():
                    return False
                    
            trading_sheet = self.spreadsheet.worksheet("Trading_Log")
            
            # Prepare row data
            row_data = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                symbol,
                action,
                price,
                quantity,
                f"{confidence:.2%}",
                profit_loss,
                notes
            ]
            
            # Append to sheet
            trading_sheet.append_row(row_data)
            
            # Log to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trade_records 
                (symbol, action, price, quantity, confidence, profit_loss, logged_to_sheets)
                VALUES (?, ?, ?, ?, ?, ?, TRUE)
            """, (symbol, action, price, quantity, confidence, profit_loss))
            conn.commit()
            conn.close()
            
            # Log operation
            self.log_operation("Trading_Log", "trade_logged", json.dumps(row_data), True)
            
            print(f"✅ Trade logged: {symbol} {action} @ ${price}")
            return True
        except Exception as e:
            print(f"❌ Error logging trade: {e}")
            self.log_operation("Trading_Log", "trade_logged", str(e), False)
            return False
            
    def log_market_data(self, symbol: str, price: float, volume: float = 0.0, 
                       change_24h: float = 0.0, source: str = ""):
        """Log market data to Google Sheets"""
        try:
            if not self.spreadsheet:
                if not self.get_or_create_spreadsheet():
                    return False
                    
            market_sheet = self.spreadsheet.worksheet("Market_Data")
            
            row_data = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                symbol,
                price,
                volume,
                f"{change_24h:.2f}%",
                source
            ]
            
            market_sheet.append_row(row_data)
            self.log_operation("Market_Data", "data_logged", json.dumps(row_data), True)
            
            return True
        except Exception as e:
            print(f"❌ Error logging market data: {e}")
            self.log_operation("Market_Data", "data_logged", str(e), False)
            return False
            
    def log_system_status(self, component: str, status: str, message: str = "", uptime: str = ""):
        """Log system status to Google Sheets"""
        try:
            if not self.spreadsheet:
                if not self.get_or_create_spreadsheet():
                    return False
                    
            status_sheet = self.spreadsheet.worksheet("System_Status")
            
            row_data = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                component,
                status,
                message,
                uptime
            ]
            
            status_sheet.append_row(row_data)
            self.log_operation("System_Status", "status_logged", json.dumps(row_data), True)
            
            return True
        except Exception as e:
            print(f"❌ Error logging system status: {e}")
            self.log_operation("System_Status", "status_logged", str(e), False)
            return False
            
    def log_operation(self, sheet_name: str, operation: str, data: str, success: bool):
        """Log operation to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sheet_logs (sheet_name, operation, data, success)
                VALUES (?, ?, ?, ?)
            """, (sheet_name, operation, data, success))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Error logging operation: {e}")
            
    def get_trading_summary(self, days: int = 7):
        """Get trading summary from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN action = 'BUY' THEN 1 ELSE 0 END) as buys,
                    SUM(CASE WHEN action = 'SELL' THEN 1 ELSE 0 END) as sells,
                    AVG(confidence) as avg_confidence,
                    SUM(profit_loss) as total_pnl
                FROM trade_records 
                WHERE timestamp >= datetime('now', '-{} days')
            """.format(days))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'total_trades': result[0],
                    'buys': result[1],
                    'sells': result[2],
                    'avg_confidence': result[3] or 0,
                    'total_pnl': result[4] or 0
                }
        except Exception as e:
            print(f"❌ Error getting trading summary: {e}")
            
        return None
        
    def update_summary_sheet(self):
        """Update summary sheet with latest statistics"""
        try:
            if not self.spreadsheet:
                if not self.get_or_create_spreadsheet():
                    return False
                    
            # Get or create summary sheet
            try:
                summary_sheet = self.spreadsheet.worksheet("Summary")
            except gspread.WorksheetNotFound:
                summary_sheet = self.spreadsheet.add_worksheet(title="Summary", rows="100", cols="10")
                summary_sheet.update('A1:B1', [['Metric', 'Value']])
                
            # Get trading summary
            summary = self.get_trading_summary()
            if summary:
                data = [
                    ['Last Updated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                    ['Total Trades (7d)', summary['total_trades']],
                    ['Buy Orders', summary['buys']],
                    ['Sell Orders', summary['sells']],
                    ['Average Confidence', f"{summary['avg_confidence']:.2%}"],
                    ['Total P&L', f"${summary['total_pnl']:.2f}"]
                ]
                
                summary_sheet.update('A1:B7', [['Metric', 'Value']] + data)
                print("✅ Summary sheet updated")
                return True
                
        except Exception as e:
            print(f"❌ Error updating summary sheet: {e}")
            
        return False

# Global sheets instance
sheets_integration = TPS19SheetsIntegration()

def log_trade_to_sheets(symbol: str, action: str, price: float, **kwargs):
    """Log trade to Google Sheets"""
    return sheets_integration.log_trade(symbol, action, price, **kwargs)

def log_market_data_to_sheets(symbol: str, price: float, **kwargs):
    """Log market data to Google Sheets"""
    return sheets_integration.log_market_data(symbol, price, **kwargs)

def log_system_status_to_sheets(component: str, status: str, **kwargs):
    """Log system status to Google Sheets"""
    return sheets_integration.log_system_status(component, status, **kwargs)

if __name__ == "__main__":
    # Test the integration
    if sheets_integration.authenticate():
        if sheets_integration.get_or_create_spreadsheet():
            # Test trade logging
            sheets_integration.log_trade("BTC_USDT", "BUY", 50000.0, 0.1, 0.85, 0.0, "Test trade")
            
            # Test market data logging
            sheets_integration.log_market_data("BTC_USDT", 50000.0, 1500000, 2.5, "crypto.com")
            
            # Test system status
            sheets_integration.log_system_status("TPS19", "ONLINE", "System running normally", "24h")
            
            # Update summary
            sheets_integration.update_summary_sheet()
            
            print("✅ Google Sheets integration test completed")
        else:
            print("❌ Failed to setup spreadsheet")
    else:
        print("❌ Failed to authenticate with Google Sheets")