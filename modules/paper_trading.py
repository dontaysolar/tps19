#!/usr/bin/env python3
"""Paper Trading Engine for TPS19.

Simulates order execution, positions, and P&L without touching the exchange.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime


@dataclass
class PaperTrade:
    pair: str
    side: str  # BUY or SELL
    amount: float
    entry_price: float
    time: str


class PaperTradingEngine:
    def __init__(self, starting_balance: float = 100.0):
        self.balance = float(starting_balance)
        self.positions: Dict[str, PaperTrade] = {}
        self.realized_pnl = 0.0
        self.enabled = True

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = bool(enabled)

    def get_status(self) -> Dict:
        return {
            'enabled': self.enabled,
            'balance': round(self.balance, 2),
            'positions': {k: v.__dict__ for k, v in self.positions.items()},
            'realized_pnl': round(self.realized_pnl, 2),
        }

    def create_market_buy(self, pair: str, amount: float, price: float) -> Dict:
        if not self.enabled:
            return {'status': 'disabled'}
        cost = amount * price
        if cost > self.balance:
            return {'status': 'rejected', 'reason': 'insufficient_funds'}
        self.balance -= cost
        self.positions[pair] = PaperTrade(pair, 'BUY', amount, price, datetime.now().isoformat())
        return {'status': 'filled', 'pair': pair, 'amount': amount, 'price': price}

    def create_market_sell(self, pair: str, price: float) -> Dict:
        if not self.enabled:
            return {'status': 'disabled'}
        pos = self.positions.get(pair)
        if not pos:
            return {'status': 'rejected', 'reason': 'no_position'}
        proceeds = pos.amount * price
        pnl = (price - pos.entry_price) * pos.amount
        self.balance += proceeds
        self.realized_pnl += pnl
        del self.positions[pair]
        return {'status': 'filled', 'pair': pair, 'amount': pos.amount, 'price': price, 'pnl': pnl}
