#!/usr/bin/env python3
"""Simple Telegram bot client for TPS19.

Environment variables:
- TELEGRAM_BOT_TOKEN: Bot token from BotFather
- TELEGRAM_CHAT_ID: Default chat ID for notifications
"""

import os
import json
import time
from typing import Optional, Dict, Any

import requests

try:
    from core.telegram_guard import guard_command
except Exception:
    def guard_command(cmd: str) -> bool:
        return True


class TelegramBot:
    def __init__(self, token: Optional[str] = None, default_chat_id: Optional[str] = None):
        self.token = token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.default_chat_id = default_chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.api_base = f"https://api.telegram.org/bot{self.token}" if self.token else None

    def is_configured(self) -> bool:
        return bool(self.token and self.default_chat_id)

    def send_message(self, text: str, chat_id: Optional[str] = None, parse_mode: Optional[str] = None) -> bool:
        if not self.is_configured():
            print("❌ Telegram not configured (missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID)")
            return False
        if not guard_command('send_message'):
            print("❌ Telegram command blocked by guard")
            return False
        try:
            payload: Dict[str, Any] = {
                'chat_id': chat_id or self.default_chat_id,
                'text': text,
            }
            if parse_mode:
                payload['parse_mode'] = parse_mode
            resp = requests.post(f"{self.api_base}/sendMessage", json=payload, timeout=10)
            if resp.status_code == 200:
                return True
            print(f"❌ Telegram sendMessage failed: {resp.status_code} {resp.text}")
            return False
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False

    def test_functionality(self) -> bool:
        """Self-test; will be no-op success if not configured to avoid hard failures."""
        if not self.is_configured():
            print("ℹ️ Telegram not configured; skipping live send test.")
            return True
        return self.send_message("✅ TPS19 Telegram self-test successful.")


telegram_bot = TelegramBot()

