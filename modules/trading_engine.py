"""
Trading Engine Abstractions

Provides exchange adapter interfaces and a light-paper trading engine for
development and fallback operation when live exchange auth is unavailable.
"""

from __future__ import annotations

from typing import Dict, Optional, Any


class ExchangeAdapter:
    """Minimal interface that concrete exchange adapters must implement."""

    def load_markets(self) -> Dict[str, Any]:
        raise NotImplementedError

    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        raise NotImplementedError

    def fetch_balance(self) -> Dict[str, Any]:
        raise NotImplementedError

    def get_min_trade_amount(self, symbol: str) -> float:
        """Return minimum base asset amount for a market symbol."""
        raise NotImplementedError

    def create_market_buy_order(self, symbol: str, amount: float) -> Dict[str, Any]:
        raise NotImplementedError

    def create_market_sell_order(self, symbol: str, amount: float) -> Dict[str, Any]:
        raise NotImplementedError


class PaperExchangeAdapter(ExchangeAdapter):
    """Simple paper trading adapter using public price feed for fills."""

    def __init__(self, public_exchange: Any, base_currency: str = 'USDT', initial_balances: Optional[Dict[str, float]] = None) -> None:
        self.public_exchange = public_exchange
        self.base_currency = base_currency
        self.markets: Dict[str, Any] = {}
        # Balances are free-only for simplicity
        self.balances: Dict[str, float] = dict(initial_balances or {self.base_currency: 1000.0})

    def load_markets(self) -> Dict[str, Any]:
        self.markets = self.public_exchange.load_markets()
        return self.markets

    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        return self.public_exchange.fetch_ticker(symbol)

    def fetch_balance(self) -> Dict[str, Any]:
        return {k: {'free': v, 'total': v} for k, v in self.balances.items()}

    def get_min_trade_amount(self, symbol: str) -> float:
        if not self.markets:
            self.load_markets()
        market = self.markets.get(symbol) or {}
        limits = market.get('limits', {})
        amount_limits = limits.get('amount', {})
        min_amount = amount_limits.get('min')
        return float(min_amount or 0.00001)

    def _ensure_asset(self, asset: str) -> None:
        if asset not in self.balances:
            self.balances[asset] = 0.0

    def create_market_buy_order(self, symbol: str, amount: float) -> Dict[str, Any]:
        ticker = self.fetch_ticker(symbol)
        price = float(ticker['last'])
        quote = self.base_currency
        base = symbol.split('/')[0]
        self._ensure_asset(base)
        self._ensure_asset(quote)

        cost = amount * price
        if self.balances[quote] + 1e-12 < cost:
            raise ValueError(f'Insufficient {quote} balance for paper trade. Needed {cost:.4f}, have {self.balances[quote]:.4f}')

        self.balances[quote] -= cost
        self.balances[base] += amount

        return {
            'id': f'paper-buy-{symbol}-{price}-{amount}',
            'symbol': symbol,
            'side': 'buy',
            'amount': amount,
            'price': price,
            'cost': cost,
            'status': 'closed',
            'type': 'market',
        }

    def create_market_sell_order(self, symbol: str, amount: float) -> Dict[str, Any]:
        ticker = self.fetch_ticker(symbol)
        price = float(ticker['last'])
        quote = self.base_currency
        base = symbol.split('/')[0]
        self._ensure_asset(base)
        self._ensure_asset(quote)

        if self.balances[base] + 1e-12 < amount:
            raise ValueError(f'Insufficient {base} balance for paper trade. Needed {amount:.8f}, have {self.balances[base]:.8f}')

        proceeds = amount * price
        self.balances[base] -= amount
        self.balances[quote] += proceeds

        return {
            'id': f'paper-sell-{symbol}-{price}-{amount}',
            'symbol': symbol,
            'side': 'sell',
            'amount': amount,
            'price': price,
            'cost': proceeds,
            'status': 'closed',
            'type': 'market',
        }
