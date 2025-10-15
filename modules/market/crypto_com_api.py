#!/usr/bin/env python3
"""
Crypto.com Public API helper for TPS19

Note: Uses public endpoint v2/get-ticker to fetch latest price data.
If the response format changes or network is unavailable, callers should
handle None/empty results gracefully.
"""

import requests
from typing import Optional, Dict, Any

BASE_URL = "https://api.crypto.com/v2"


def _instrument_from_symbol(symbol: str) -> str:
    symbol = (symbol or "").upper()
    # Default to USD Tether pairs where applicable
    if symbol in {"BTC", "ETH", "ADA", "SOL", "LINK"}:
        return f"{symbol}_USDT"
    # Fallback guess
    return f"{symbol}_USDT"


def get_ticker(symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch ticker for symbol from Crypto.com public API.

    Returns a dict with keys: instrument_name, price, bid, ask, volume, change_24h
    or None on failure.
    """
    try:
        instrument = _instrument_from_symbol(symbol)
        resp = requests.get(
            f"{BASE_URL}/public/get-ticker",
            params={"instrument_name": instrument},
            timeout=10,
        )
        data = resp.json()
        if data.get("code") == 0 and data.get("result", {}).get("data"):
            entry = data["result"]["data"][0]
            # Attempt to derive last price from typical fields ('a' ask, 'b' bid, 'k' last?)
            # Use a conservative priority; not all fields are guaranteed.
            price = (
                entry.get("a")
                or entry.get("b")
                or entry.get("k")
                or entry.get("c")
            )
            bid = entry.get("b")
            ask = entry.get("a")
            volume = entry.get("v") or entry.get("qv") or 0
            change_24h = entry.get("pc") or 0
            try:
                price = float(price)
            except Exception:
                price = None
            return {
                "instrument_name": instrument,
                "price": price,
                "bid": bid,
                "ask": ask,
                "volume": volume,
                "change_24h": change_24h,
                "raw": entry,
            }
    except Exception:
        pass
    return None


def get_price(symbol: str) -> Optional[float]:
    ticker = get_ticker(symbol)
    return ticker.get("price") if ticker else None
