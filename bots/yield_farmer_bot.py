#!/usr/bin/env python3
"""
Yield Farmer Bot
Stakes idle balances for passive income
Part of APEX AI Trading System
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
except ImportError:
    os.system("pip3 install --break-system-packages ccxt -q")
    import ccxt

class YieldFarmerBot:
    """Manages staking and yield farming for idle funds"""
    
    def __init__(self, exchange_config: Dict = None):
        self.name = "YieldFarmerBot"
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
            'min_idle_balance_usd': 2.0,      # Min $2 to stake
            'idle_threshold_pct': 20.0,       # 20% of balance can be idle
            'preferred_assets': ['USDT', 'USDC', 'BTC', 'ETH'],
            'check_interval': 3600            # Check every hour
        }
        
        self.staked_positions = {}
        
        self.metrics = {
            'total_staked_usd': 0.0,
            'yield_earned_usd': 0.0,
            'active_stakes': 0
        }
    
    def get_idle_balance(self) -> Dict:
        """Calculate idle balance not in active trades"""
        try:
            balance = self.exchange.fetch_balance()
            
            idle_balances = {}
            total_idle_usd = 0
            
            for asset in self.config['preferred_assets']:
                if asset in balance['free'] and balance['free'][asset] > 0:
                    free_amount = balance['free'][asset]
                    
                    # Get USD value
                    if asset == 'USDT' or asset == 'USDC':
                        usd_value = free_amount
                    else:
                        # Get price
                        try:
                            ticker = self.exchange.fetch_ticker(f'{asset}/USDT')
                            usd_value = free_amount * ticker['last']
                        except:
                            usd_value = 0
                    
                    idle_balances[asset] = {
                        'amount': free_amount,
                        'usd_value': usd_value
                    }
                    
                    total_idle_usd += usd_value
            
            return {
                'idle_balances': idle_balances,
                'total_idle_usd': total_idle_usd,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Idle balance check error: {e}")
            return {}
    
    def find_staking_opportunities(self) -> List[Dict]:
        """Find available staking opportunities"""
        # Note: Crypto.com API might not expose staking via CCXT
        # This is a placeholder for future integration
        
        opportunities = [
            {'asset': 'USDT', 'apy': 6.0, 'min_amount': 1.0, 'lock_days': 0},
            {'asset': 'BTC', 'apy': 4.5, 'min_amount': 0.0001, 'lock_days': 30},
            {'asset': 'ETH', 'apy': 5.0, 'min_amount': 0.001, 'lock_days': 30}
        ]
        
        return opportunities
    
    def stake_idle_funds(self) -> Dict:
        """Stake available idle funds"""
        idle = self.get_idle_balance()
        
        if not idle or idle['total_idle_usd'] < self.config['min_idle_balance_usd']:
            return {
                'staked': False,
                'reason': f"Idle balance ${idle.get('total_idle_usd', 0):.2f} below minimum ${self.config['min_idle_balance_usd']:.2f}"
            }
        
        opportunities = self.find_staking_opportunities()
        staked = []
        
        for opp in opportunities:
            asset = opp['asset']
            
            if asset not in idle['idle_balances']:
                continue
            
            idle_amount = idle['idle_balances'][asset]['amount']
            
            if idle_amount >= opp['min_amount']:
                # In production, would execute staking here
                # For now, simulate
                
                stake_id = f"{asset}_{datetime.now().timestamp()}"
                
                self.staked_positions[stake_id] = {
                    'asset': asset,
                    'amount': idle_amount,
                    'apy': opp['apy'],
                    'start_date': datetime.now().isoformat(),
                    'lock_days': opp['lock_days'],
                    'status': 'ACTIVE'
                }
                
                staked.append({
                    'asset': asset,
                    'amount': idle_amount,
                    'apy': opp['apy'],
                    'estimated_yearly_yield': idle_amount * (opp['apy'] / 100)
                })
                
                self.metrics['total_staked_usd'] += idle['idle_balances'][asset]['usd_value']
                self.metrics['active_stakes'] += 1
        
        return {
            'staked': len(staked) > 0,
            'positions': staked,
            'total_staked_usd': self.metrics['total_staked_usd'],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'active_stakes': len(self.staked_positions),
            'metrics': self.metrics,
            'config': self.config
        }

if __name__ == '__main__':
    bot = YieldFarmerBot()
    print("🌾 Yield Farmer Bot - Test Mode\n")
    
    result = bot.stake_idle_funds()
    print(json.dumps(result, indent=2))
