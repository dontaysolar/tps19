#!/usr/bin/env python3
"""Market Pulse Bot - Real-Time Data Aggregator
Part of APEX AI Trading System - TCC"""

import os, sys, json
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
except ImportError:
    os.system("pip3 install --break-system-packages ccxt -q")
    import ccxt

class MarketPulseBot:
    def __init__(self, exchange_config: Dict = None):
        self.name, self.version = "MarketPulseBot", "1.0.0"
        
        if exchange_config:
            self.exchange = ccxt.cryptocom(exchange_config)
        else:
            from dotenv import load_dotenv
            load_dotenv()
            self.exchange = ccxt.cryptocom({'apiKey': os.getenv('EXCHANGE_API_KEY'), 'secret': os.getenv('EXCHANGE_API_SECRET'), 'enableRateLimit': True})
        
        self.pulse_data = {}
        self.metrics = {'pulses_captured': 0, 'pairs_monitored': 0}
    
    def capture_pulse(self, symbols: List[str]) -> Dict:
        pulse = {}
        
        for symbol in symbols:
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                pulse[symbol] = {'price': ticker['last'], 'volume_24h': ticker.get('quoteVolume', 0), 'change_24h_pct': ticker.get('percentage', 0), 'timestamp': datetime.now().isoformat()}
            except:
                pass
        
        self.pulse_data = pulse
        self.metrics['pulses_captured'] += 1
        self.metrics['pairs_monitored'] = len(pulse)
        
        return pulse
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'metrics': self.metrics}

if __name__ == '__main__':
    bot = MarketPulseBot()
    print("💓 Market Pulse Bot - Test\n")
    pulse = bot.capture_pulse(['BTC/USDT', 'ETH/USDT'])
    print(f"Pulse captured: {len(pulse)} pairs")
