#!/usr/bin/env python3
"""Google Sheets logger via Apps Script Web App webhook.

This avoids gspread dependency by posting to a provided webhook URL.
Set environment variable:
- GOOGLE_SHEETS_WEBHOOK_URL (Apps Script published web app URL)

Apps Script sample to receive:
function doPost(e){ var sheet=SpreadsheetApp.openById('ID').getSheetByName('Logs'); var data=JSON.parse(e.postData.contents); sheet.appendRow([new Date(), data.event||'', data.symbol||'', data.price||'', data.details||'']); return ContentService.createTextOutput('ok'); }
"""

import os
import requests
from datetime import datetime
from typing import Dict, Any


class GoogleSheetsLogger:
    def __init__(self):
        self.webhook_url = os.getenv("GOOGLE_SHEETS_WEBHOOK_URL")

    def _is_configured(self) -> bool:
        return bool(self.webhook_url)

    def log_event(self, event: str, payload: Dict[str, Any]) -> bool:
        if not self._is_configured():
            # Graceful no-op to keep system working without creds
            return True
        try:
            data = {
                "event": event,
                "timestamp": datetime.now().isoformat(),
                **payload,
            }
            resp = requests.post(self.webhook_url, json=data, timeout=10)
            return resp.status_code in (200, 204)
        except Exception:
            return False


# Global instance
sheets_logger = GoogleSheetsLogger()
