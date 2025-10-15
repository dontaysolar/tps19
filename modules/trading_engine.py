#!/usr/bin/env python3
"""
Trading Engine - Minimal coordinator for SIUL and N8N.

Responsibilities:
- Fetch market snapshot (from simulated MarketFeed for now)
- Run unified logic via SIUL
- Emit actionable signals to N8N if confidence threshold met
"""

from __future__ import annotations

import time
from typing import Dict, Any

from modules.common.logging import get_logger
from modules.market.market_feed import market_feed
from modules.siul.siul_core import siul_core
from modules.n8n.n8n_integration import n8n_integration


class TradingEngine:
    def __init__(self, confidence_threshold: float = 0.7):
        self.logger = get_logger('trading.engine')
        self.confidence_threshold = confidence_threshold

    def fetch_market_snapshot(self, symbol: str = 'BTC_USDT') -> Dict[str, Any]:
        data = market_feed.get_latest_data(symbol, 1)
        if not data:
            # Fallback synthetic
            price = 45000 + (time.time() % 1000)
            return {
                'symbol': symbol,
                'price': price,
                'volume': 1500,
                'exchange': 'crypto.com',
            }
        row = data[0]
        return {
            'symbol': row.get('symbol', symbol),
            'price': row.get('close'),
            'volume': row.get('volume', 0),
            'exchange': row.get('exchange', 'crypto.com'),
        }

    def run_once(self, symbol: str = 'BTC_USDT') -> Dict[str, Any]:
        snapshot = self.fetch_market_snapshot(symbol)
        siul_result = siul_core.process_unified_logic(snapshot)

        final_decision = siul_result.get('final_decision', {}) if siul_result else {}
        confidence = float(final_decision.get('confidence', 0.0))
        action = final_decision.get('decision', 'hold')

        sent_to_n8n = False
        if confidence >= self.confidence_threshold and action in {'buy', 'sell'}:
            sent_to_n8n = n8n_integration.send_trade_signal({
                'symbol': snapshot['symbol'],
                'action': action,
                'price': snapshot['price'],
                'confidence': confidence,
            })

        result = {
            'snapshot': snapshot,
            'siul_decision': final_decision,
            'sent_to_n8n': bool(sent_to_n8n),
        }
        self.logger.info(f"Decision: {action} @ conf={confidence:.2f} | sent_to_n8n={sent_to_n8n}")
        return result

    def test_functionality(self) -> bool:
        try:
            out = self.run_once('BTC_USDT')
            return 'siul_decision' in out
        except Exception:
            return False


if __name__ == '__main__':
    engine = TradingEngine()
    res = engine.run_once('BTC_USDT')
    print({
        'decision': res.get('siul_decision', {}).get('decision'),
        'confidence': res.get('siul_decision', {}).get('confidence'),
        'sent_to_n8n': res.get('sent_to_n8n'),
    })
