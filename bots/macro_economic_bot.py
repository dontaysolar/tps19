#!/usr/bin/env python3
"""Macro Economic Bot - Fed rates, CPI, GDP impact analysis"""
from datetime import datetime
from typing import Dict

class MacroEconomicBot:
    def __init__(self):
        self.name = "Macro_Economic"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'events_analyzed': 0}
    
    def analyze_macro_event(self, event_type: str, value: float, expectation: float) -> Dict:
        """Analyze macro economic event impact"""
        surprise = value - expectation
        surprise_pct = (surprise / expectation * 100) if expectation != 0 else 0
        
        # Fed rate impact
        if event_type == 'FED_RATE':
            if surprise > 0.25:  # Rate hike surprise
                signal, confidence = 'SELL', 0.80
            elif surprise < -0.25:  # Rate cut surprise
                signal, confidence = 'BUY', 0.80
            else:
                signal, confidence = 'HOLD', 0.50
        
        # CPI (inflation) impact
        elif event_type == 'CPI':
            if surprise_pct > 10:  # Higher inflation
                signal, confidence = 'BUY', 0.70  # Crypto as inflation hedge
            elif surprise_pct < -10:
                signal, confidence = 'SELL', 0.60
            else:
                signal, confidence = 'HOLD', 0.50
        
        # GDP impact
        elif event_type == 'GDP':
            if surprise_pct > 5:  # Strong growth
                signal, confidence = 'BUY', 0.65
            elif surprise_pct < -5:  # Weak growth
                signal, confidence = 'SELL', 0.65
            else:
                signal, confidence = 'HOLD', 0.50
        
        else:
            signal, confidence = 'HOLD', 0.50
        
        self.metrics['events_analyzed'] += 1
        
        return {
            'event_type': event_type,
            'value': value,
            'expectation': expectation,
            'surprise': surprise,
            'surprise_pct': surprise_pct,
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = MacroEconomicBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
