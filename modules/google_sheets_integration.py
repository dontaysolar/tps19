#!/usr/bin/env python3
"""
TPS19 Google Sheets Integration
Real-time dashboard and reporting via Google Sheets
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️ Google API libraries not installed. Run: pip install google-auth google-api-python-client")

class GoogleSheetsIntegration:
    """Google Sheets integration for TPS19 trading dashboard"""
    
    def __init__(self, credentials_path='/opt/tps19/config/google_credentials.json'):
        self.credentials_path = credentials_path
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID', '')
        self.service = None
        self.db_path = "/opt/tps19/data/databases/trading.db"
        
        if GOOGLE_AVAILABLE:
            self._initialize_service()
        else:
            print("⚠️ Google Sheets integration unavailable - install required packages")
    
    def _initialize_service(self):
        """Initialize Google Sheets service"""
        try:
            if not os.path.exists(self.credentials_path):
                print(f"⚠️ Google credentials not found at {self.credentials_path}")
                self._create_credentials_template()
                return
            
            # Define the required scopes
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            
            # Load credentials
            credentials = Credentials.from_service_account_file(
                self.credentials_path, scopes=SCOPES
            )
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=credentials)
            print("✅ Google Sheets service initialized")
            
        except Exception as e:
            print(f"❌ Google Sheets initialization error: {e}")
    
    def _create_credentials_template(self):
        """Create a template for Google service account credentials"""
        try:
            os.makedirs(os.path.dirname(self.credentials_path), exist_ok=True)
            
            template = {
                "type": "service_account",
                "project_id": "your-project-id",
                "private_key_id": "your-private-key-id",
                "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
                "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
                "client_id": "your-client-id",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
            }
            
            with open(self.credentials_path, 'w') as f:
                json.dump(template, f, indent=2)
            
            print(f"✅ Created credentials template at {self.credentials_path}")
            print("⚠️ Please replace with actual Google service account credentials")
            
        except Exception as e:
            print(f"❌ Template creation error: {e}")
    
    def create_dashboard(self, spreadsheet_name: str = "TPS19 Trading Dashboard") -> Optional[str]:
        """Create a new trading dashboard spreadsheet"""
        if not self.service:
            print("❌ Google Sheets service not available")
            return None
        
        try:
            spreadsheet = {
                'properties': {
                    'title': spreadsheet_name
                },
                'sheets': [
                    {'properties': {'title': 'Overview', 'gridProperties': {'rowCount': 100, 'columnCount': 10}}},
                    {'properties': {'title': 'Trade History', 'gridProperties': {'rowCount': 1000, 'columnCount': 12}}},
                    {'properties': {'title': 'Performance', 'gridProperties': {'rowCount': 100, 'columnCount': 8}}},
                    {'properties': {'title': 'Market Data', 'gridProperties': {'rowCount': 100, 'columnCount': 10}}},
                ]
            }
            
            result = self.service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = result.get('spreadsheetId')
            
            # Initialize dashboard with headers
            self._initialize_dashboard_headers(spreadsheet_id)
            
            print(f"✅ Dashboard created: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
            return spreadsheet_id
            
        except Exception as e:
            print(f"❌ Dashboard creation error: {e}")
            return None
    
    def _initialize_dashboard_headers(self, spreadsheet_id: str):
        """Initialize dashboard with headers"""
        try:
            # Overview sheet headers
            overview_headers = [
                ['TPS19 TRADING DASHBOARD'],
                ['Exchange', 'crypto.com'],
                ['Last Updated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                [''],
                ['Metric', 'Value'],
                ['Total Trades', '0'],
                ['Win Rate', '0%'],
                ['Total Profit/Loss', '$0.00'],
                ['Active Positions', '0'],
                ['Portfolio Value', '$0.00']
            ]
            
            # Trade History headers
            trade_headers = [[
                'Date', 'Time', 'Symbol', 'Action', 'Price', 'Quantity', 
                'Total', 'Profit/Loss', 'Confidence', 'Source', 'Status', 'Notes'
            ]]
            
            # Performance headers
            performance_headers = [[
                'Date', 'Total Trades', 'Wins', 'Losses', 'Win Rate', 
                'Profit/Loss', 'Best Trade', 'Worst Trade'
            ]]
            
            # Market Data headers
            market_headers = [[
                'Symbol', 'Price', 'Change 24h', 'Volume', 'High 24h', 
                'Low 24h', 'Market Cap', 'Source', 'Last Updated', 'Trend'
            ]]
            
            # Update sheets
            requests = []
            
            # Overview
            requests.append({
                'updateCells': {
                    'range': {'sheetId': 0, 'startRowIndex': 0, 'startColumnIndex': 0},
                    'rows': [{'values': [{'userEnteredValue': {'stringValue': str(cell)}} for cell in row]} for row in overview_headers],
                    'fields': 'userEnteredValue'
                }
            })
            
            # Trade History
            requests.append({
                'updateCells': {
                    'range': {'sheetId': 1, 'startRowIndex': 0, 'startColumnIndex': 0},
                    'rows': [{'values': [{'userEnteredValue': {'stringValue': cell}} for cell in row]} for row in trade_headers],
                    'fields': 'userEnteredValue'
                }
            })
            
            # Performance
            requests.append({
                'updateCells': {
                    'range': {'sheetId': 2, 'startRowIndex': 0, 'startColumnIndex': 0},
                    'rows': [{'values': [{'userEnteredValue': {'stringValue': cell}} for cell in row]} for row in performance_headers],
                    'fields': 'userEnteredValue'
                }
            })
            
            # Market Data
            requests.append({
                'updateCells': {
                    'range': {'sheetId': 3, 'startRowIndex': 0, 'startColumnIndex': 0},
                    'rows': [{'values': [{'userEnteredValue': {'stringValue': cell}} for cell in row]} for row in market_headers],
                    'fields': 'userEnteredValue'
                }
            })
            
            body = {'requests': requests}
            self.service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
            
            print("✅ Dashboard headers initialized")
            
        except Exception as e:
            print(f"❌ Header initialization error: {e}")
    
    def update_overview(self, data: Dict[str, Any]) -> bool:
        """Update overview sheet with current statistics"""
        if not self.service or not self.spreadsheet_id:
            return False
        
        try:
            values = [
                [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],  # Last updated
                [''],
                ['Metric', 'Value'],
                ['Total Trades', data.get('total_trades', 0)],
                ['Win Rate', f"{data.get('win_rate', 0):.1f}%"],
                ['Total Profit/Loss', f"${data.get('total_profit', 0):,.2f}"],
                ['Active Positions', data.get('active_positions', 0)],
                ['Portfolio Value', f"${data.get('portfolio_value', 0):,.2f}"],
                ['Best Trade', f"${data.get('best_trade', 0):,.2f}"],
                ['Worst Trade', f"${data.get('worst_trade', 0):,.2f}"]
            ]
            
            body = {'values': values}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range='Overview!C3:D12',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print("✅ Overview updated")
            return True
            
        except Exception as e:
            print(f"❌ Overview update error: {e}")
            return False
    
    def add_trade(self, trade_data: Dict[str, Any]) -> bool:
        """Add a trade to the Trade History sheet"""
        if not self.service or not self.spreadsheet_id:
            return False
        
        try:
            values = [[
                trade_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                trade_data.get('time', datetime.now().strftime('%H:%M:%S')),
                trade_data.get('symbol', ''),
                trade_data.get('action', ''),
                f"${trade_data.get('price', 0):,.2f}",
                trade_data.get('quantity', 0),
                f"${trade_data.get('total', 0):,.2f}",
                f"${trade_data.get('profit_loss', 0):,.2f}",
                f"{trade_data.get('confidence', 0):.1f}%",
                trade_data.get('source', 'TPS19'),
                trade_data.get('status', 'completed'),
                trade_data.get('notes', '')
            ]]
            
            body = {'values': values}
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='Trade History!A2:L2',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            print("✅ Trade added to history")
            return True
            
        except Exception as e:
            print(f"❌ Trade add error: {e}")
            return False
    
    def update_market_data(self, market_data: List[Dict[str, Any]]) -> bool:
        """Update market data sheet"""
        if not self.service or not self.spreadsheet_id:
            return False
        
        try:
            values = []
            for item in market_data:
                values.append([
                    item.get('symbol', ''),
                    f"${item.get('price', 0):,.2f}",
                    f"{item.get('change_24h', 0):+.2f}%",
                    f"${item.get('volume', 0):,.0f}",
                    f"${item.get('high_24h', 0):,.2f}",
                    f"${item.get('low_24h', 0):,.2f}",
                    f"${item.get('market_cap', 0):,.0f}",
                    item.get('source', 'crypto.com'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    '⬆️' if item.get('change_24h', 0) > 0 else '⬇️'
                ])
            
            body = {'values': values}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range='Market Data!A2:J100',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print("✅ Market data updated")
            return True
            
        except Exception as e:
            print(f"❌ Market data update error: {e}")
            return False
    
    def get_sheet_url(self) -> Optional[str]:
        """Get the URL of the current spreadsheet"""
        if self.spreadsheet_id:
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
        return None
    
    def test_connection(self) -> bool:
        """Test Google Sheets connection"""
        if not GOOGLE_AVAILABLE:
            print("❌ Google API libraries not installed")
            return False
        
        if not self.service:
            print("❌ Google Sheets service not initialized")
            return False
        
        try:
            # Try to access the spreadsheet
            if self.spreadsheet_id:
                result = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
                print(f"✅ Connected to: {result.get('properties', {}).get('title', 'Unknown')}")
                return True
            else:
                print("⚠️ No spreadsheet ID configured")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

# Global Google Sheets instance
google_sheets = GoogleSheetsIntegration()

if __name__ == "__main__":
    sheets = GoogleSheetsIntegration()
    
    print("📊 TPS19 Google Sheets Integration")
    print("=" * 60)
    
    # Test connection
    print("\n🔍 Testing Google Sheets connection...")
    sheets.test_connection()
    
    if GOOGLE_AVAILABLE and sheets.service:
        print("\n📝 Google Sheets integration is configured")
        if sheets.spreadsheet_id:
            print(f"  Spreadsheet URL: {sheets.get_sheet_url()}")
        else:
            print("  ⚠️ Set GOOGLE_SHEETS_ID environment variable or create new dashboard")
    else:
        print("\n⚠️ Google Sheets integration not available")
        print("  To enable:")
        print("  1. Install: pip install google-auth google-api-python-client")
        print("  2. Create Google Cloud service account")
        print("  3. Download credentials JSON")
        print(f"  4. Place credentials at: {sheets.credentials_path}")
        print("  5. Set GOOGLE_SHEETS_ID environment variable")
    
    print("\n✅ Google Sheets Module Ready")
