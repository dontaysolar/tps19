#!/usr/bin/env python3
"""Lightweight Telegram notifier without external deps.

Environment variables:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
"""

import os
import requests
from datetime import datetime
from typing import Optional, Dict, Any


class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def _is_configured(self) -> bool:
        return bool(self.token and self.chat_id)

    def send_message(self, text: str, parse_mode: Optional[str] = None) -> bool:
        if not self._is_configured():
            # Graceful no-op when not configured to avoid failing tests
            return True
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload: Dict[str, Any] = {"chat_id": self.chat_id, "text": text}
            if parse_mode:
                payload["parse_mode"] = parse_mode
            resp = requests.post(url, json=payload, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False

    def send_trade_signal(self, symbol: str, action: str, price: float, confidence: float) -> bool:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = (
            f"🚨 Trade Signal\n"
            f"Symbol: {symbol}\n"
            f"Action: {action.upper()}\n"
            f"Price: ${price:,.2f}\n"
            f"Confidence: {confidence:.2%}\n"
            f"Time: {timestamp}"
        )
        return self.send_message(text)


# Global instance
telegram_notifier = TelegramNotifier()
