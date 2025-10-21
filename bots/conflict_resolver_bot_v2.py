#!/usr/bin/env python3
"""Conflict Resolver Bot v2.0 - Signal Conflict Resolution | AEGIS"""
import os, sys
from datetime import datetime
from typing import Dict, List
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from trading_bot_base import TradingBotBase

class ConflictResolverBot(TradingBotBase):
    def __init__(self):
        super().__init__(bot_name="CONFLICT_RESOLVER_BOT", bot_version="2.0.0", exchange_name='mock', enable_psm=False, enable_logging=False)
        self.config = {'max_concurrent_positions': 4, 'min_signal_agreement': 0.6, 'position_priority': {'BTC/USDT': 1, 'ETH/USDT': 2}}
        self.active_signals = {}
        self.active_positions = {}
        self.metrics.update({'conflicts_detected': 0, 'conflicts_resolved': 0, 'signals_blocked': 0})
    
    def register_signal(self, bot_name: str, symbol: str, signal: str, confidence: float) -> str:
        assert len(bot_name) > 0 and len(symbol) > 0, "Bot name and symbol required"
        signal_id = f"{bot_name}_{symbol}_{datetime.now().timestamp()}"
        if symbol not in self.active_signals:
            self.active_signals[symbol] = []
        self.active_signals[symbol].append({'signal_id': signal_id, 'bot': bot_name, 'signal': signal, 'confidence': confidence, 'timestamp': datetime.now().isoformat()})
        assert isinstance(signal_id, str), "Signal ID must be string"
        return signal_id
    
    def check_conflicts(self, symbol: str) -> Dict:
        assert len(symbol) > 0, "Symbol required"
        if symbol not in self.active_signals or not self.active_signals[symbol]:
            return {'conflict': False}
        signals = self.active_signals[symbol]
        buy_signals = [s for s in signals[:20] if s['signal'] == 'BUY']  # ATLAS: Fixed bound
        sell_signals = [s for s in signals[:20] if s['signal'] == 'SELL']
        if buy_signals and sell_signals:
            self.metrics['conflicts_detected'] += 1
            buy_confidence = sum(s['confidence'] for s in buy_signals) / len(buy_signals)
            sell_confidence = sum(s['confidence'] for s in sell_signals) / len(sell_signals)
            if abs(buy_confidence - sell_confidence) < 0.1:
                return {'conflict': True, 'resolution': 'BLOCK', 'reason': 'Signals too conflicted', 'buy_confidence': buy_confidence, 'sell_confidence': sell_confidence}
            resolution = 'BUY' if buy_confidence > sell_confidence else 'SELL'
            self.metrics['conflicts_resolved'] += 1
            result = {'conflict': True, 'resolution': resolution, 'buy_confidence': buy_confidence, 'sell_confidence': sell_confidence}
        else:
            result = {'conflict': False}
        assert isinstance(result, dict), "Result must be dict"
        return result
    
    def clear_signals(self, symbol: str):
        assert len(symbol) > 0, "Symbol required"
        if symbol in self.active_signals:
            self.active_signals[symbol] = []

if __name__ == '__main__':
    bot = ConflictResolverBot()
    bot.register_signal('Bot1', 'BTC/USDT', 'BUY', 0.8)
    bot.register_signal('Bot2', 'BTC/USDT', 'SELL', 0.7)
    conflict = bot.check_conflicts('BTC/USDT')
    print(f"Conflict: {conflict['conflict']}, Resolution: {conflict.get('resolution', 'N/A')}")
    bot.close()
    print("✅ Conflict Resolver Bot v2.0 complete!")
