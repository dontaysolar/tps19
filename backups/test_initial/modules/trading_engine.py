#!/usr/bin/env python3
"""TPS19 Trading Engine with basic liquidity router.

Offline-friendly: works without network/ccxt by using a local stub to
generate deterministic quotes. In production, detects ccxt and queries venues.
"""

import os
import time
from typing import Dict, List, Optional, Tuple


class _StubVenue:
    """Offline venue stub for deterministic quotes without network."""

    def __init__(self, name: str) -> None:
        self.name = name

    def fetch_ticker(self, symbol: str) -> Dict:
        # Deterministic price based on venue+symbol
        base = 50000.0 if 'BTC' in symbol else 3000.0 if 'ETH' in symbol else 100.0
        seed = abs(hash((self.name, symbol))) % 1000
        price = base * (1 + (seed - 500) / 50000.0)  # +/- 2%
        return {
            'symbol': symbol,
            'last': price,
            'timestamp': int(time.time() * 1000),
        }


class LiquidityRouter:
    """Selects best venue/price for a symbol across configured exchanges."""

    def __init__(self, venues: Optional[List[str]] = None) -> None:
        venues = venues or ['cryptocom', 'binance', 'kraken']
        self._use_ccxt = False
        self._adapters = {}

        try:
            import ccxt  # type: ignore
            self._use_ccxt = True
            for v in venues:
                try:
                    ex = getattr(ccxt, v)()
                    self._adapters[v] = ex
                except Exception:
                    self._adapters[v] = _StubVenue(v)
        except Exception:
            for v in venues:
                self._adapters[v] = _StubVenue(v)

    def best_quote(self, symbol: str, side: str, amount: float) -> Tuple[str, float]:
        """Return (venue, price) best for the given side."""
        quotes: List[Tuple[str, float]] = []
        for name, adapter in self._adapters.items():
            try:
                ticker = adapter.fetch_ticker(symbol)
                price = float(ticker['last'])
                quotes.append((name, price))
            except Exception:
                continue

        if not quotes:
            # Fallback to cryptocom stub
            price = _StubVenue('cryptocom').fetch_ticker(symbol)['last']
            return 'cryptocom', float(price)

        # For a buy, choose lowest price; for a sell, choose highest
        reverse = True if side == 'sell' else False
        quotes.sort(key=lambda x: x[1], reverse=reverse)
        return quotes[0]


class TradingEngine:
    """High-level trading engine that routes and executes simple orders."""

    def __init__(self, venues: Optional[List[str]] = None) -> None:
        self.router = LiquidityRouter(venues)

    def get_best_quote(self, symbol: str, side: str, amount: float) -> Dict:
        venue, price = self.router.best_quote(symbol, side, amount)
        return {
            'venue': venue,
            'price': price,
            'symbol': symbol,
            'side': side,
        }

    def execute_order(self, symbol: str, side: str, amount: float, order_type: str = 'market') -> Dict:
        quote = self.get_best_quote(symbol, side, amount)
        # Offline-friendly: simulate immediate fill at quote price
        value = amount * quote['price']
        return {
            'status': 'filled',
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': quote['price'],
            'value_usd': value,
            'venue': quote['venue'],
            'type': order_type,
            'timestamp': int(time.time() * 1000),
        }

    def get_status(self) -> Dict:
        return {
            'venues': list(self.router._adapters.keys()),
            'online': self.router._use_ccxt,
        }


if __name__ == '__main__':
    engine = TradingEngine()
    quote = engine.get_best_quote('BTC/USDT', 'buy', 0.01)
    print('Best quote:', quote)
    res = engine.execute_order('BTC/USDT', 'buy', 0.01)
    print('Order result:', res)
