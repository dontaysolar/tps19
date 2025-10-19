#!/usr/bin/env python3
"""Candlestick Patterns Bot - Doji, Hammer, Engulfing, etc"""
from datetime import datetime
from typing import Dict

class CandlestickPatternsBot:
    def __init__(self):
        self.name = "Candlestick_Patterns"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'patterns_detected': 0}
    
    def detect_patterns(self, candle: Dict, prev_candle: Dict = None) -> Dict:
        """Detect candlestick patterns"""
        o, h, l, c = candle.get('open', 0), candle.get('high', 0), candle.get('low', 0), candle.get('close', 0)
        
        body = abs(c - o)
        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l
        total_range = h - l
        
        patterns = []
        
        # Doji
        if body < total_range * 0.1:
            patterns.append('DOJI')
        
        # Hammer (bullish)
        if lower_wick > body * 2 and upper_wick < body * 0.5 and c > o:
            patterns.append('HAMMER')
        
        # Hanging Man (bearish)
        if lower_wick > body * 2 and upper_wick < body * 0.5 and c < o:
            patterns.append('HANGING_MAN')
        
        # Shooting Star
        if upper_wick > body * 2 and lower_wick < body * 0.5:
            patterns.append('SHOOTING_STAR')
        
        # Bullish Engulfing
        if prev_candle:
            prev_body = abs(prev_candle.get('close', 0) - prev_candle.get('open', 0))
            if c > o and body > prev_body * 1.5:
                patterns.append('BULLISH_ENGULFING')
        
        # Generate signal
        bullish = sum(1 for p in patterns if p in ['HAMMER', 'BULLISH_ENGULFING'])
        bearish = sum(1 for p in patterns if p in ['HANGING_MAN', 'SHOOTING_STAR'])
        
        if bullish > bearish:
            signal, confidence = 'BUY', 0.75
        elif bearish > bullish:
            signal, confidence = 'SELL', 0.75
        else:
            signal, confidence = 'HOLD', 0.50
        
        if patterns:
            self.metrics['patterns_detected'] += 1
        
        return {
            'patterns': patterns,
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = CandlestickPatternsBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
