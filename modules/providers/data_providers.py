"""Unified market data providers for TPS19.

This module implements data fetching from Crypto.com public endpoints with
an Alpha Vantage fallback. It avoids CoinGecko usage entirely.
"""

from __future__ import annotations

import os
import time
import json
from typing import Dict, Optional, Tuple

import requests


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        # Strings like "12345.67" are supported
        return float(str(value))
    except Exception:
        return default


def normalize_pair(symbol_or_pair: str) -> Tuple[str, str, str]:
    """Normalize a symbol or pair into (base, quote, instrument_name).

    Accepts inputs like "BTC_USDT", "BTC-USDT", "BTCUSD", "BTC/USD",
    or common coin ids like "bitcoin" (mapped to BTC_USDT).
    """
    s = (symbol_or_pair or "").strip()
    s_upper = s.upper().replace("-", "_").replace("/", "_")

    id_to_symbol = {
        "BITCOIN": "BTC",
        "ETHEREUM": "ETH",
        "CARDANO": "ADA",
        "SOLANA": "SOL",
        "CHAINLINK": "LINK",
    }

    # If looks like a known id
    if s and s.upper() in id_to_symbol:
        base = id_to_symbol[s.upper()]
        quote = "USDT"
        return base, quote, f"{base}_{quote}"

    # If contains an underscore, assume BASE_QUOTE
    if "_" in s_upper:
        parts = s_upper.split("_")
        if len(parts) == 2:
            base, quote = parts[0], parts[1]
            return base, quote, f"{base}_{quote}"

    # Compact forms like BTCUSD or ETHUSDT
    if s_upper.endswith("USDT"):
        base = s_upper[:-4]
        quote = "USDT"
        return base, quote, f"{base}_{quote}"
    if s_upper.endswith("USD"):
        base = s_upper[:-3]
        quote = "USD"
        return base, quote, f"{base}_{quote}"

    # Fallback to BTC_USDT
    return "BTC", "USDT", "BTC_USDT"


def fetch_crypto_com_ticker(symbol_or_pair: str) -> Optional[Dict[str, float]]:
    """Fetch price/volume from Crypto.com public get-ticker endpoint.

    Returns a dict like: { 'price': float, 'volume': float }
    or None on failure.
    """
    _, _, instrument = normalize_pair(symbol_or_pair)
    url = "https://api.crypto.com/v2/public/get-ticker"
    try:
        response = requests.get(url, params={"instrument_name": instrument}, timeout=10)
        data = response.json()
        # Expected structure includes a 'result' with 'data' list
        result = (data or {}).get("result", {})
        items = result.get("data") or result.get("tickers") or []
        if isinstance(items, dict):
            items = [items]
        if not items:
            return None
        first = items[0]

        # Crypto.com responses use various keys depending on endpoint version.
        # Try multiple reasonable keys for last price and 24h volume.
        price = _safe_float(
            first.get("last_price")
            or first.get("k")
            or first.get("price")
            or first.get("c")
        )
        volume = _safe_float(
            first.get("v")
            or first.get("volume_24h")
            or first.get("volume")
        )

        if price <= 0:
            return None
        return {"price": price, "volume": volume}
    except Exception:
        return None


def fetch_alpha_vantage_price(symbol_or_pair: str) -> Optional[Dict[str, float]]:
    """Fetch price from Alpha Vantage CURRENCY_EXCHANGE_RATE.

    Requires ALPHAVANTAGE_API_KEY in environment. Returns
    { 'price': float, 'volume': 0.0 } or None on failure.
    """
    api_key = os.environ.get("ALPHAVANTAGE_API_KEY")
    if not api_key:
        return None

    base, quote, _ = normalize_pair(symbol_or_pair)
    # Alpha Vantage expects ISO currency symbols; try to normalize common quotes
    if quote == "USDT":
        quote = "USD"

    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": base,
            "to_currency": quote,
            "apikey": api_key,
        }
        response = requests.get(url, params=params, timeout=15)
        data = response.json() or {}
        section = data.get("Realtime Currency Exchange Rate", {})
        # Common keys seen in Alpha Vantage responses
        price = _safe_float(
            section.get("5. Exchange Rate")
            or section.get("Exchange Rate")
            or section.get("price")
        )
        if price <= 0:
            return None
        return {"price": price, "volume": 0.0}
    except Exception:
        return None


def get_price(symbol_or_pair: str) -> Optional[Dict[str, float]]:
    """Get price/volume using Crypto.com first, Alpha Vantage as fallback."""
    data = fetch_crypto_com_ticker(symbol_or_pair)
    if data is not None:
        return data
    return fetch_alpha_vantage_price(symbol_or_pair)


def get_market_stats(symbol_or_pair: str) -> Dict[str, float]:
    """Return basic market stats. Crypto.com provides last price and may expose
    24h aggregates via ticker; if not available, set defaults.
    """
    info = fetch_crypto_com_ticker(symbol_or_pair)
    if info is None:
        info = fetch_alpha_vantage_price(symbol_or_pair) or {"price": 0.0, "volume": 0.0}
    return {
        "price": _safe_float(info.get("price", 0.0)),
        "high_24h": 0.0,  # Not available via basic endpoints without additional calls
        "low_24h": 0.0,
        "change_24h": 0.0,
    }
