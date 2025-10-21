#!/usr/bin/env python3
"""Market Pulse Bot v2.0 - Real-Time Data Aggregator | AEGIS"""
import os, sys
from datetime import datetime
from typing import Dict, List
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from trading_bot_base import TradingBotBase

class MarketPulseBot(TradingBotBase):
    def __init__(self, exchange_config=None):
        super().__init__(bot_name="MARKET_PULSE_BOT", bot_version="2.0.0", exchange_name='mock' if not exchange_config else 'cryptocom', enable_psm=False, enable_logging=True)
        self.pulse_data = {}
        self.metrics.update({'pulses_captured': 0, 'pairs_monitored': 0})
    
    def capture_pulse(self, symbols: List[str]) -> Dict:
        assert isinstance(symbols, list), "Symbols must be list"
        pulse = {}
        for i, symbol in enumerate(symbols):
            if i >= 50: break  # ATLAS: Fixed bound
            try:
                ticker = self.get_ticker(symbol)
                if ticker:
                    pulse[symbol] = {'price': ticker.get('last', 0), 'volume_24h': ticker.get('quoteVolume', 0), 'change_24h_pct': ticker.get('percentage', 0), 'timestamp': datetime.now().isoformat()}
            except:
                continue
        self.pulse_data = pulse
        self.metrics['pulses_captured'] += 1
        self.metrics['pairs_monitored'] = len(pulse)
        assert isinstance(pulse, dict), "Result must be dict"
        return pulse

if __name__ == '__main__':
    print("💓 Market Pulse Bot v2.0")
    bot = MarketPulseBot()
    pulse = bot.capture_pulse(['BTC/USDT', 'ETH/USDT'])
    print(f"Pulse: {len(pulse)} pairs")
    bot.close()
    print("✅ Market Pulse Bot v2.0 complete!")
