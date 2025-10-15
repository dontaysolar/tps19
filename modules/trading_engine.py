#!/usr/bin/env python3
"""TPS Orchestrator: wires data -> AI -> signaling.

This is intentionally signals-only (no execution) to keep the system safe.
"""

import time
from datetime import datetime
from typing import Dict, Any

from modules.market_data import MarketData
from modules.ai_council import AICouncil
from dtcp.signal_provider import DTCPSignalProvider
from modules.n8n.n8n_integration import n8n_integration


class TradingEngine:
    def __init__(self):
        self.market = MarketData()
        self.ai = AICouncil()
        self.dtcp = DTCPSignalProvider()
        self.running = False

    def step(self, symbol_slug: str = "bitcoin", pair: str = "BTC_USDT") -> Dict[str, Any]:
        price = self.market.get_price(symbol_slug)
        stats = self.market.get_market_stats(symbol_slug)

        market_snapshot = {
            'price': price,
            'volume': stats.get('volume', 0) if isinstance(stats, dict) else 0,
            'change_24h': stats.get('change_24h', 0) if isinstance(stats, dict) else 0,
        }

        council = self.ai.make_trading_decision({'price': price, 'change_24h': market_snapshot['change_24h']}, {})

        signal = self.dtcp.generate_signal(
            pair,
            {
                'price': price,
                'volume': market_snapshot['volume'],
                'sma_20': price,  # placeholder
                'rsi': 50,        # placeholder
            },
        )

        if council and council.get('confidence', 0) >= 0.7 and signal:
            n8n_integration.send_trade_signal({
                'symbol': pair,
                'action': 'buy' if 'buy' in council['decision'] else 'sell' if 'sell' in council['decision'] else 'hold',
                'price': price,
                'confidence': council['confidence'],
            })

        return {
            'timestamp': datetime.now().isoformat(),
            'price': price,
            'ai_decision': council,
            'signal': signal,
        }

    def run(self, interval_seconds: int = 60):
        self.running = True
        while self.running:
            try:
                result = self.step()
                print(f"[{result['timestamp']}] {result['ai_decision']['decision']} @ {result['price']}")
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                print(f"❌ Engine error: {e}")
            time.sleep(interval_seconds)


if __name__ == "__main__":
    TradingEngine().run(30)
