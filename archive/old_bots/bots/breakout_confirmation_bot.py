#!/usr/bin/env python3
"""Breakout Confirmation Bot - Validates breakouts"""
from datetime import datetime
from typing import Dict, List

class BreakoutConfirmationBot:
    def __init__(self):
        self.name = "Breakout_Confirmation"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'breakouts': 0, 'false_breakouts': 0}
    
    def confirm_breakout(self, price: float, resistance: float, volume_ratio: float, 
                        closes_above: int) -> Dict:
        """Confirm if breakout is valid"""
        
        # Breakout criteria
        price_above_pct = ((price - resistance) / resistance) * 100
        
        is_valid = False
        confidence = 0.50
        
        # Strong breakout
        if price_above_pct > 2 and volume_ratio > 2 and closes_above >= 3:
            is_valid = True
            confidence = 0.90
            strength = 'STRONG'
            self.metrics['breakouts'] += 1
        
        # Moderate breakout
        elif price_above_pct > 1 and volume_ratio > 1.5 and closes_above >= 2:
            is_valid = True
            confidence = 0.75
            strength = 'MODERATE'
            self.metrics['breakouts'] += 1
        
        # Weak breakout
        elif price_above_pct > 0.5 and volume_ratio > 1:
            is_valid = True
            confidence = 0.60
            strength = 'WEAK'
        
        # False breakout
        elif price_above_pct < 0.5 or volume_ratio < 0.8:
            is_valid = False
            strength = 'FALSE'
            self.metrics['false_breakouts'] += 1
        
        else:
            strength = 'UNCLEAR'
        
        return {
            'is_valid_breakout': is_valid,
            'strength': strength,
            'price_above_pct': price_above_pct,
            'volume_ratio': volume_ratio,
            'closes_above': closes_above,
            'signal': 'BUY' if is_valid else 'HOLD',
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = BreakoutConfirmationBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
