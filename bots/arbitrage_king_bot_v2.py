#!/usr/bin/env python3
"""Arbitrage King Bot v2.0 - Cross-Market Arbitrage | AEGIS
Exploits price differences"""
import os, sys
from datetime import datetime
from typing import Dict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from trading_bot_base import TradingBotBase

class ArbitrageKingBot(TradingBotBase):
    def __init__(self, exchange_config=None):
        super().__init__(
            bot_name="ARBITRAGE_KING_BOT",
            bot_version="2.0.0",
            exchange_name='mock' if not exchange_config else 'cryptocom',
            enable_psm=True,
            enable_logging=True
        )
        assert hasattr(self, 'exchange_adapter'), "Base init failed"
        self.config = {'min_spread_pct': 0.5, 'max_execution_time_sec': 10}
        self.metrics.update({'arb_opportunities': 0, 'arb_profit': 0.0})
    
    def detect_arbitrage(self, symbol: str) -> Dict:
        assert len(symbol) > 0, "Symbol required"
        try:
            orderbook = self.exchange_adapter.get_order_book(symbol, limit=5)
            if not orderbook or not orderbook.get('bids') or not orderbook.get('asks'):
                return {'symbol': symbol, 'opportunity': False}
            
            best_bid = orderbook['bids'][0][0] if orderbook['bids'] else 0
            best_ask = orderbook['asks'][0][0] if orderbook['asks'] else 0
            spread_pct = ((best_ask - best_bid) / best_bid) * 100 if best_bid > 0 else 0
            opportunity = spread_pct >= self.config['min_spread_pct']
            
            if opportunity:
                self.metrics['arb_opportunities'] += 1
            
            result = {'symbol': symbol, 'opportunity': opportunity, 'spread_pct': spread_pct, 'bid': best_bid, 'ask': best_ask, 'timestamp': datetime.now().isoformat()}
            assert isinstance(result, dict), "Result must be dict"
            return result
        except Exception as e:
            self.metrics['errors'] += 1
            return {'symbol': symbol, 'opportunity': False, 'error': str(e)}

if __name__ == '__main__':
    print("💎 Arbitrage King Bot v2.0")
    bot = ArbitrageKingBot()
    result = bot.detect_arbitrage('BTC/USDT')
    print(f"Opportunity: {result['opportunity']}")
    bot.close()
    print("✅ Arbitrage King Bot v2.0 complete!")
