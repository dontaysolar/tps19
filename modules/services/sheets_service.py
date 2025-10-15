"""Google Sheets service for TPS19.

Optional integration. Prefer service-account JSON in env var GOOGLE_SERVICE_ACCOUNT_JSON.
Requires `gspread` and `google-auth` if enabled. If unavailable or
not configured, functions return False without failing the system.
"""
from __future__ import annotations

import os
import json
from typing import List, Optional


def enabled() -> bool:
    return bool(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON") and os.environ.get("GOOGLE_SPREADSHEET_ID"))


def _get_client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except Exception:
        return None
    sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not sa_json:
        return None
    try:
        info = json.loads(sa_json)
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
        ]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception:
        return None


def append_row(sheet_name: str, row: List[str]) -> bool:
    spreadsheet_id = os.environ.get("GOOGLE_SPREADSHEET_ID")
    if not spreadsheet_id:
        return False
    client = _get_client()
    if client is None:
        return False
    try:
        sh = client.open_by_key(spreadsheet_id)
        ws = sh.worksheet(sheet_name)
    except Exception:
        try:
            ws = sh.add_worksheet(title=sheet_name, rows=1000, cols=20)
        except Exception:
            return False
    try:
        ws.append_row(row, value_input_option="USER_ENTERED")
        return True
    except Exception:
        return False
