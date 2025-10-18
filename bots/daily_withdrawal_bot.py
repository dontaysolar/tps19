#!/usr/bin/env python3
"""
Daily Withdrawal Bot
Manages profit distribution (30% BTC, 20% USDT, 50% reinvest)
Part of APEX AI Trading System
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
except ImportError:
    os.system("pip3 install --break-system-packages ccxt -q")
    import ccxt

class DailyWithdrawalBot:
    """Automates profit withdrawal and reallocation"""
    
    def __init__(self, exchange_config: Dict = None):
        self.name = "DailyWithdrawalBot"
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
            'btc_allocation_pct': 30.0,       # 30% to BTC
            'usdt_allocation_pct': 20.0,      # 20% to USDT
            'reinvest_pct': 50.0,             # 50% reinvest
            'min_profit_for_withdrawal': 5.0, # Min $5 profit to withdraw
            'withdrawal_schedule': '00:00',   # Daily at midnight
            'initial_balance': 3.0            # Track original capital
        }
        
        self.withdrawal_history = []
        
        self.metrics = {
            'total_withdrawn_btc': 0.0,
            'total_withdrawn_usdt': 0.0,
            'total_reinvested': 0.0,
            'withdrawals_count': 0
        }
    
    def calculate_profit(self) -> Dict:
        """Calculate current profit vs initial balance"""
        try:
            balance = self.exchange.fetch_balance()
            
            # Calculate total balance in USDT
            total_usd = balance['total'].get('USDT', 0) or 0
            
            # Add value of other assets
            for asset in ['BTC', 'ETH', 'SOL', 'ADA']:
                if asset in balance['total'] and balance['total'][asset] > 0:
                    try:
                        ticker = self.exchange.fetch_ticker(f'{asset}/USDT')
                        total_usd += balance['total'][asset] * ticker['last']
                    except:
                        pass
            
            profit = total_usd - self.config['initial_balance']
            profit_pct = (profit / self.config['initial_balance']) * 100 if self.config['initial_balance'] > 0 else 0
            
            return {
                'current_balance_usd': total_usd,
                'initial_balance_usd': self.config['initial_balance'],
                'total_profit_usd': profit,
                'profit_pct': profit_pct,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Profit calculation error: {e}")
            return {}
    
    def execute_withdrawal(self) -> Dict:
        """DISABLED - Only calculates profit, does not withdraw"""
        if self.WITHDRAWAL_DISABLED:
            return {
                'executed': False,
                'reason': 'SECURITY: Withdrawals disabled. Bot tracks profit only.',
                'withdrawal_disabled': True
            }
        
        profit_data = self.calculate_profit()
        
        if not profit_data:
            return {'executed': False, 'error': 'Failed to calculate profit'}
        
        profit = profit_data['total_profit_usd']
        
        if profit < self.config['min_profit_for_withdrawal']:
            return {
                'executed': False,
                'reason': f"Profit ${profit:.2f} below minimum ${self.config['min_profit_for_withdrawal']:.2f}",
                'current_profit': profit
            }
        
        # Calculate allocations
        btc_amount_usd = profit * (self.config['btc_allocation_pct'] / 100)
        usdt_amount = profit * (self.config['usdt_allocation_pct'] / 100)
        reinvest_amount = profit * (self.config['reinvest_pct'] / 100)
        
        # Get BTC price for conversion
        try:
            btc_ticker = self.exchange.fetch_ticker('BTC/USDT')
            btc_amount = btc_amount_usd / btc_ticker['last']
        except:
            btc_amount = 0
            btc_amount_usd = 0
        
        # In production, would execute actual withdrawals here
        # For now, simulate and track
        
        withdrawal = {
            'btc_amount': btc_amount,
            'btc_usd_value': btc_amount_usd,
            'usdt_amount': usdt_amount,
            'reinvest_amount': reinvest_amount,
            'total_profit': profit,
            'timestamp': datetime.now().isoformat(),
            'status': 'SIMULATED'
        }
        
        self.withdrawal_history.append(withdrawal)
        
        self.metrics['total_withdrawn_btc'] += btc_amount
        self.metrics['total_withdrawn_usdt'] += usdt_amount
        self.metrics['total_reinvested'] += reinvest_amount
        self.metrics['withdrawals_count'] += 1
        
        return {
            'executed': True,
            'profit_withdrawn': profit,
            'allocations': withdrawal,
            'remaining_for_trading': reinvest_amount,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_withdrawal_summary(self) -> Dict:
        """Get summary of all withdrawals"""
        return {
            'total_withdrawals': len(self.withdrawal_history),
            'total_btc': self.metrics['total_withdrawn_btc'],
            'total_usdt': self.metrics['total_withdrawn_usdt'],
            'total_reinvested': self.metrics['total_reinvested'],
            'history': self.withdrawal_history[-10:]  # Last 10
        }
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'metrics': self.metrics,
            'config': self.config
        }

if __name__ == '__main__':
    bot = DailyWithdrawalBot()
    print("🌾 Daily Withdrawal Bot - Test Mode\n")
    
    result = bot.execute_withdrawal()
    print(json.dumps(result, indent=2))
