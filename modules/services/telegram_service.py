"""Simple Telegram service for TPS19.

Uses Telegram Bot API via HTTP. Requires environment variables:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
If not provided, calls are no-ops that return False.
"""
import os
import time
from typing import Optional
import requests

BOT_TOKEN_ENV = "TELEGRAM_BOT_TOKEN"
CHAT_ID_ENV = "TELEGRAM_CHAT_ID"


def enabled() -> bool:
    return bool(os.environ.get(BOT_TOKEN_ENV) and os.environ.get(CHAT_ID_ENV))


def send_message(text: str, parse_mode: Optional[str] = None) -> bool:
    token = os.environ.get(BOT_TOKEN_ENV)
    chat_id = os.environ.get(CHAT_ID_ENV)
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.ok
    except Exception:
        return False


def send_alert(title: str, body: str) -> bool:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    return send_message(f"⚠️ {title}\n{body}\n🕒 {ts}")
