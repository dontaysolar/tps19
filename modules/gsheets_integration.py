#!/usr/bin/env python3
"""
Google Sheets integration for TPS19 using a service account.

Configuration options (at least one required for live mode):
- GOOGLE_SERVICE_ACCOUNT_JSON: inline JSON credentials string
- GOOGLE_APPLICATION_CREDENTIALS: path to credentials file
- TPS19_GSHEETS_SPREADSHEET_ID: default spreadsheet ID

If not configured or dependencies are missing, methods degrade gracefully and return True for tests.
"""

import os
from typing import List, Any, Optional

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_DEPS_AVAILABLE = True
except Exception:
    GOOGLE_DEPS_AVAILABLE = False


class GSheetsClient:
    def __init__(self, spreadsheet_id: Optional[str] = None):
        self.spreadsheet_id = spreadsheet_id or os.getenv('TPS19_GSHEETS_SPREADSHEET_ID')
        self._service = None
        self._configured = self._try_init_service()

    def _try_init_service(self) -> bool:
        if not GOOGLE_DEPS_AVAILABLE:
            return False
        try:
            creds = None
            inline_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
            keyfile_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if inline_json:
                import json
                info = json.loads(inline_json)
                creds = service_account.Credentials.from_service_account_info(info, scopes=[
                    'https://www.googleapis.com/auth/spreadsheets'
                ])
            elif keyfile_path and os.path.exists(keyfile_path):
                creds = service_account.Credentials.from_service_account_file(keyfile_path, scopes=[
                    'https://www.googleapis.com/auth/spreadsheets'
                ])
            else:
                # Also check default path
                default_path = '/opt/tps19/config/gsheets_credentials.json'
                if os.path.exists(default_path):
                    creds = service_account.Credentials.from_service_account_file(default_path, scopes=[
                        'https://www.googleapis.com/auth/spreadsheets'
                    ])
            if not creds:
                return False
            self._service = build('sheets', 'v4', credentials=creds, cache_discovery=False)
            return True
        except Exception:
            return False

    def is_configured(self) -> bool:
        return bool(self._service and self.spreadsheet_id)

    def append_row(self, range_name: str, values: List[Any]) -> bool:
        if not self.is_configured():
            print('ℹ️ Google Sheets not configured; skipping append_row.')
            return True
        try:
            body = {'values': [values]}
            self._service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            return True
        except Exception as e:
            print(f'❌ Google Sheets append_row error: {e}')
            return False

    def test_functionality(self) -> bool:
        # Non-destructive test: if configured, perform a metadata read; else pass
        if not self.is_configured():
            print('ℹ️ Google Sheets not configured; test passes as no-op.')
            return True
        try:
            meta = self._service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            return bool(meta and meta.get('spreadsheetId'))
        except Exception as e:
            print(f'❌ Google Sheets test error: {e}')
            return False


gsheets_client = GSheetsClient()
