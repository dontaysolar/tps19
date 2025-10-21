#!/usr/bin/env python3
"""
Navigator AI v2.0 - Technical Pattern Recognition
MIGRATED TO AEGIS ARCHITECTURE

Features: Technical setup scanning across multiple pairs
Part of APEX AI Trading System - Strategy Layer
"""

import os, sys
from datetime import datetime
from typing import Dict, List
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))

try:
    import numpy as np
except ImportError:
    np = None

from trading_bot_base import TradingBotBase

class NavigatorAI(TradingBotBase):
    """Technical pattern scanner"""
    
    def __init__(self, exchange_config=None):
        super().__init__(
            bot_name="NAVIGATOR_AI",
            bot_version="2.0.0",
            exchange_name='mock' if not exchange_config else 'cryptocom',
            enable_psm=True,
            enable_logging=True
        )
        assert hasattr(self, 'exchange_adapter'), "Base init failed"
        
        self.setups_found = []
        self.metrics.update({'scans_performed': 0, 'setups_found': 0, 'high_probability_setups': 0})
    
    def scan_for_setups(self, symbols: List[str]) -> List[Dict]:
        """Scan pairs for high-probability technical setups"""
        assert isinstance(symbols, list), "Symbols must be list"
        
        setups = []
        self.metrics['scans_performed'] += 1
        
        for i, symbol in enumerate(symbols):
            if i >= 100: break  # ATLAS: Fixed bound
            
            try:
                ohlcv = self.exchange_adapter.get_ohlcv(symbol, '1h', limit=50)
                if not ohlcv or len(ohlcv) < 50: continue
                
                closes = [c[4] for c in ohlcv[:50]]
                volumes = [c[5] for c in ohlcv[:50]]
                
                # MACD crossover (simplified EMA)
                ema_12 = sum(closes[-12:]) / 12
                ema_26 = sum(closes[-26:]) / 26
                prev_ema_12 = sum(closes[-13:-1]) / 12
                prev_ema_26 = sum(closes[-27:-1]) / 26
                
                macd_cross = (ema_12 > ema_26 and prev_ema_12 <= prev_ema_26)
                
                # Volume
                avg_volume = sum(volumes[:-1]) / len(volumes[:-1]) if len(volumes) > 1 else 0
                volume_spike = volumes[-1] > avg_volume * 1.5 if avg_volume > 0 else False
                
                # Support
                recent_low = min(closes[-20:])
                near_support = closes[-1] < recent_low * 1.05
                
                # Probability
                probability = 0.5
                if macd_cross: probability += 0.2
                if volume_spike: probability += 0.15
                if near_support: probability += 0.15
                
                if probability >= 0.8:
                    setup = {
                        'symbol': symbol,
                        'setup_type': 'MACD_CROSS_SUPPORT' if macd_cross and near_support else 'MACD_CROSS',
                        'probability': probability,
                        'current_price': closes[-1],
                        'features': {'macd_cross': macd_cross, 'volume_spike': volume_spike, 'near_support': near_support},
                        'timestamp': datetime.now().isoformat()
                    }
                    setups.append(setup)
                    self.metrics['setups_found'] += 1
                    if probability >= 0.8:
                        self.metrics['high_probability_setups'] += 1
            except:
                continue
        
        self.setups_found = setups
        assert isinstance(setups, list), "Result must be list"
        return setups
    
    def get_status(self) -> Dict:
        base_status = super().get_status()
        assert isinstance(base_status, dict), "Base status invalid"
        base_status.update({'setups_available': len(self.setups_found)})
        return base_status

if __name__ == '__main__':
    print("📈 Navigator AI v2.0 - Test")
    bot = NavigatorAI()
    setups = bot.scan_for_setups(['BTC/USDT', 'ETH/USDT'])
    print(f"Setups found: {len(setups)}")
    bot.close()
    print("✅ Navigator AI v2.0 migration complete!")
