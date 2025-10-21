#!/usr/bin/env python3
"""Flash Trade Bot v2.0 - Volatility Burst Trader | AEGIS
Ultra-fast trades during volatility spikes"""
import os, sys
from datetime import datetime
from typing import Dict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from trading_bot_base import TradingBotBase

try:
    import numpy as np
except ImportError:
    np = None

class FlashTradeBot(TradingBotBase):
    def __init__(self, exchange_config=None):
        super().__init__(bot_name="FLASH_TRADE_BOT", bot_version="2.0.0", exchange_name='mock' if not exchange_config else 'cryptocom', enable_psm=True, enable_logging=True)
        assert hasattr(self, 'exchange_adapter'), "Base init failed"
        self.config = {'volatility_threshold': 0.05, 'min_volume_spike': 2.0, 'max_hold_seconds': 300}
        self.metrics.update({'flash_trades': 0, 'flash_profit': 0.0})
    
    def detect_volatility_burst(self, symbol: str) -> Dict:
        assert len(symbol) > 0, "Symbol required"
        try:
            ohlcv = self.exchange_adapter.get_ohlcv(symbol, '1m', limit=60)
            if not ohlcv or len(ohlcv) < 60:
                return {'symbol': symbol, 'burst_detected': False}
            
            recent = ohlcv[-10:]
            closes = [c[4] for c in recent]
            if np:
                volatility = float(np.std(closes) / np.mean(closes))
                vol_avg = float(np.mean([c[5] for c in ohlcv[:-1]]))
            else:
                mean_close = sum(closes) / len(closes)
                volatility = (sum((x - mean_close) ** 2 for x in closes) / len(closes)) ** 0.5 / mean_close
                volumes = [c[5] for c in ohlcv[:-1]]
                vol_avg = sum(volumes) / len(volumes) if volumes else 1
            
            vol_current = ohlcv[-1][5]
            vol_spike = vol_current / vol_avg if vol_avg > 0 else 0
            burst_detected = volatility >= self.config['volatility_threshold'] and vol_spike >= self.config['min_volume_spike']
            
            result = {'symbol': symbol, 'burst_detected': burst_detected, 'volatility': volatility, 'volume_spike': vol_spike, 'signal': 'FLASH_BUY' if burst_detected else 'HOLD', 'timestamp': datetime.now().isoformat()}
            assert isinstance(result, dict), "Result must be dict"
            return result
        except Exception as e:
            self.metrics['errors'] += 1
            return {'symbol': symbol, 'burst_detected': False, 'error': str(e)}

if __name__ == '__main__':
    print("⚡ Flash Trade Bot v2.0")
    bot = FlashTradeBot()
    result = bot.detect_volatility_burst('BTC/USDT')
    print(f"Burst: {result['burst_detected']}")
    bot.close()
    print("✅ Flash Trade Bot v2.0 complete!")
