#!/usr/bin/env python3
"""Options Greeks Calculator - Delta, Gamma, Theta, Vega"""
import numpy as np
from datetime import datetime
from typing import Dict

class OptionsGreeksCalculatorBot:
    def __init__(self):
        self.name = "Options_Greeks_Calculator"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'calculations': 0}
    
    def calculate_greeks(self, spot_price: float, strike_price: float, time_to_expiry: float,
                        volatility: float, risk_free_rate: float = 0.05, option_type: str = 'CALL') -> Dict:
        """Calculate option Greeks (simplified Black-Scholes)"""
        
        # Simplified calculations
        moneyness = spot_price / strike_price
        
        # Delta (price sensitivity)
        if option_type == 'CALL':
            delta = 0.5 + (moneyness - 1) * 0.5
        else:  # PUT
            delta = -0.5 + (moneyness - 1) * 0.5
        
        delta = max(-1, min(1, delta))
        
        # Gamma (delta sensitivity)
        gamma = 0.1 / (volatility * np.sqrt(time_to_expiry)) if time_to_expiry > 0 else 0
        
        # Theta (time decay)
        theta = -0.5 * spot_price * volatility / np.sqrt(time_to_expiry) if time_to_expiry > 0 else 0
        
        # Vega (volatility sensitivity)
        vega = spot_price * np.sqrt(time_to_expiry) * 0.01
        
        # Generate signal based on Greeks
        if option_type == 'CALL' and delta > 0.6 and theta < -5:
            signal = 'BUY_UNDERLYING'  # ITM call losing value
            confidence = 0.70
        elif option_type == 'PUT' and delta < -0.6:
            signal = 'SELL_UNDERLYING'
            confidence = 0.70
        else:
            signal = 'HOLD'
            confidence = 0.50
        
        self.metrics['calculations'] += 1
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'moneyness': moneyness,
            'option_type': option_type,
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = OptionsGreeksCalculatorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
