#!/usr/bin/env python3
"""
Profit Lock Bot
Secures profits after wins based on volatility
Part of APEX AI Trading System
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
except ImportError:
    os.system("pip3 install --break-system-packages ccxt -q")
    import ccxt

class ProfitLockBot:
    """Locks in profits after successful trades"""
    
    def __init__(self, exchange_config: Dict = None):
        self.name = "ProfitLockBot"
        self.version = "1.0.0"
        
        if exchange_config:
            self.exchange = ccxt.cryptocom(exchange_config)
        else:
            from dotenv import load_dotenv
            load_dotenv()
            self.exchange = ccxt.cryptocom({
                'apiKey': os.getenv('EXCHANGE_API_KEY'),
                'secret': os.getenv('EXCHANGE_API_SECRET'),
                'enableRateLimit': True
            })
        
        self.config = {
            'lock_threshold_pct': 10.0,   # Lock profits after 10% gain
            'lock_percentage': 50.0,       # Lock 50% of position
            'min_profit_usd': 0.50,        # Min $0.50 profit to lock
            'volatility_multiplier': 1.5   # Adjust based on volatility
        }
        
        self.metrics = {
            'locks_executed': 0,
            'total_locked': 0.0,
            'profits_preserved': 0.0
        }
    
    def should_lock_profit(self, entry_price: float, current_price: float, 
                           amount: float, volatility: float = 0.05) -> Dict:
        """Determine if profit should be locked"""
        try:
            # Calculate unrealized profit
            profit = (current_price - entry_price) * amount
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            
            # Check thresholds
            if profit < self.config['min_profit_usd']:
                return {
                    'should_lock': False,
                    'reason': f'Profit ${profit:.2f} below minimum ${self.config["min_profit_usd"]:.2f}'
                }
            
            # Adjust threshold based on volatility
            adjusted_threshold = self.config['lock_threshold_pct'] * (1 + volatility * self.config['volatility_multiplier'])
            
            if profit_pct >= adjusted_threshold:
                # Calculate lock amount
                lock_amount = amount * (self.config['lock_percentage'] / 100)
                lock_value = lock_amount * current_price
                
                return {
                    'should_lock': True,
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'lock_amount': lock_amount,
                    'lock_value': lock_value,
                    'remaining_amount': amount - lock_amount,
                    'threshold_used': adjusted_threshold
                }
            
            return {
                'should_lock': False,
                'reason': f'Profit {profit_pct:.2f}% below threshold {adjusted_threshold:.2f}%',
                'current_profit': profit,
                'profit_pct': profit_pct
            }
            
        except Exception as e:
            print(f"❌ Profit lock check error: {e}")
            return {'should_lock': False, 'error': str(e)}
    
    def execute_profit_lock(self, symbol: str, entry_price: float, 
                           current_price: float, amount: float) -> Dict:
        """Execute profit lock by selling portion of position"""
        try:
            lock_decision = self.should_lock_profit(entry_price, current_price, amount)
            
            if not lock_decision['should_lock']:
                return {
                    'locked': False,
                    'reason': lock_decision.get('reason', 'Conditions not met')
                }
            
            lock_amount = lock_decision['lock_amount']
            
            # In production, would execute sell order here
            # For now, just simulate
            
            self.metrics['locks_executed'] += 1
            self.metrics['total_locked'] += lock_decision['lock_value']
            self.metrics['profits_preserved'] += lock_decision['profit'] * (self.config['lock_percentage'] / 100)
            
            return {
                'locked': True,
                'symbol': symbol,
                'lock_amount': lock_amount,
                'lock_value': lock_decision['lock_value'],
                'profit_secured': lock_decision['profit'] * (self.config['lock_percentage'] / 100),
                'remaining_position': lock_decision['remaining_amount'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Profit lock execution error: {e}")
            return {'locked': False, 'error': str(e)}
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'metrics': self.metrics,
            'config': self.config
        }

if __name__ == '__main__':
    bot = ProfitLockBot()
    print("💰 Profit Lock Bot - Test Mode\n")
    
    # Simulate winning trade
    result = bot.execute_profit_lock('BTC/USDT', 50000, 55500, 0.001)
    print(json.dumps(result, indent=2))
