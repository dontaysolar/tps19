#!/usr/bin/env python3
"""Central Order Executor - routes orders to real exchange or paper engine.

Use a unified interface:
- execute_buy(pair, amount, price_hint=None)
- execute_sell(pair, amount, price_hint=None)

Configure with:
- mode: 'real' | 'paper'
- exchange: ccxt instance (for real) or market data source (for paper)
- paper_engine: PaperTradingEngine instance when mode='paper'
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class ExecutorConfig:
    mode: str  # 'real' or 'paper'
    min_amount: float = 0.0


class OrderExecutor:
    def __init__(self, config: ExecutorConfig, exchange: Any = None, paper_engine: Any = None) -> None:
        self.config = config
        self.exchange = exchange
        self.paper = paper_engine

    def execute_buy(self, pair: str, amount: float, price_hint: Optional[float] = None) -> Dict:
        if amount <= 0 or amount < self.config.min_amount:
            return {'status': 'rejected', 'reason': 'below_min_amount'}
        if self.config.mode == 'paper' and self.paper:
            price = price_hint if price_hint is not None else self._last_price(pair)
            return self.paper.create_market_buy(pair, amount, float(price))
        elif self.config.mode == 'real' and self.exchange:
            try:
                return self.exchange.create_market_buy_order(pair, amount)
            except Exception as e:
                return {'status': 'error', 'error': str(e)}
        return {'status': 'error', 'error': 'invalid_config'}

    def execute_sell(self, pair: str, amount: float, price_hint: Optional[float] = None) -> Dict:
        if amount <= 0 or amount < self.config.min_amount:
            return {'status': 'rejected', 'reason': 'below_min_amount'}
        if self.config.mode == 'paper' and self.paper:
            price = price_hint if price_hint is not None else self._last_price(pair)
            return self.paper.create_market_sell(pair, float(price))
        elif self.config.mode == 'real' and self.exchange:
            try:
                return self.exchange.create_market_sell_order(pair, amount)
            except Exception as e:
                return {'status': 'error', 'error': str(e)}
        return {'status': 'error', 'error': 'invalid_config'}

    def _last_price(self, _pair: str) -> float:
        return float(price_hint)  # fallback, should be replaced by market data source
