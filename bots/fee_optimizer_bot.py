#!/usr/bin/env python3
"""
Fee Optimization Bot
Pre-calculates fees and slippage before trades to maximize profit
Part of APEX AI Trading System
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Tuple, Optional

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
except ImportError:
    os.system("pip3 install --break-system-packages ccxt -q")
    import ccxt

class FeeOptimizerBot:
    """Calculates and optimizes trading fees and slippage"""
    
    def __init__(self, exchange_config: Dict = None):
        self.name = "FeeOptimizerBot"
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
        
        self.metrics = {
            'total_calculations': 0,
            'trades_optimized': 0,
            'fees_saved': 0.0,
            'slippage_avoided': 0.0
        }
    
    def calculate_fees(self, symbol: str, amount: float, side: str) -> Dict:
        """Calculate trading fees for an order"""
        try:
            market = self.exchange.market(symbol)
            
            # Get fee structure
            maker_fee = market.get('maker', 0.001)  # 0.1% default
            taker_fee = market.get('taker', 0.001)  # 0.1% default
            
            # Get current price
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            
            # Calculate order value
            order_value = amount * price
            
            # Assume market order = taker fee
            fee_amount = order_value * taker_fee
            
            # Calculate net proceeds
            if side == 'buy':
                total_cost = order_value + fee_amount
                net_amount = amount
            else:  # sell
                total_cost = order_value
                net_amount = order_value - fee_amount
            
            self.metrics['total_calculations'] += 1
            
            return {
                'symbol': symbol,
                'amount': amount,
                'side': side,
                'price': price,
                'order_value': order_value,
                'maker_fee_pct': maker_fee * 100,
                'taker_fee_pct': taker_fee * 100,
                'fee_amount': fee_amount,
                'total_cost': total_cost,
                'net_proceeds': net_amount,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Fee calculation error: {e}")
            return {}
    
    def estimate_slippage(self, symbol: str, amount: float, side: str) -> Dict:
        """Estimate price slippage for an order"""
        try:
            # Get order book
            orderbook = self.exchange.fetch_order_book(symbol, limit=20)
            
            # Get current price
            ticker = self.exchange.fetch_ticker(symbol)
            mid_price = (ticker['bid'] + ticker['ask']) / 2
            
            # Calculate slippage based on order book depth
            if side == 'buy':
                # Check ask side
                asks = orderbook['asks']
                cumulative_volume = 0
                weighted_price = 0
                
                for price, volume in asks:
                    if cumulative_volume >= amount:
                        break
                    fill_amount = min(volume, amount - cumulative_volume)
                    weighted_price += price * fill_amount
                    cumulative_volume += fill_amount
                
                avg_fill_price = weighted_price / cumulative_volume if cumulative_volume > 0 else mid_price
                slippage_pct = ((avg_fill_price - mid_price) / mid_price) * 100
                
            else:  # sell
                # Check bid side
                bids = orderbook['bids']
                cumulative_volume = 0
                weighted_price = 0
                
                for price, volume in bids:
                    if cumulative_volume >= amount:
                        break
                    fill_amount = min(volume, amount - cumulative_volume)
                    weighted_price += price * fill_amount
                    cumulative_volume += fill_amount
                
                avg_fill_price = weighted_price / cumulative_volume if cumulative_volume > 0 else mid_price
                slippage_pct = ((mid_price - avg_fill_price) / mid_price) * 100
            
            slippage_amount = abs(avg_fill_price - mid_price) * amount
            
            return {
                'symbol': symbol,
                'amount': amount,
                'side': side,
                'mid_price': mid_price,
                'expected_fill_price': avg_fill_price,
                'slippage_pct': slippage_pct,
                'slippage_amount': slippage_amount,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Slippage estimation error: {e}")
            return {}
    
    def optimize_order(self, symbol: str, amount: float, side: str) -> Dict:
        """Full order optimization with fees and slippage"""
        fee_calc = self.calculate_fees(symbol, amount, side)
        slippage_calc = self.estimate_slippage(symbol, amount, side)
        
        if not fee_calc or not slippage_calc:
            return {}
        
        # Calculate total cost
        total_cost = fee_calc['fee_amount'] + slippage_calc['slippage_amount']
        total_cost_pct = (total_cost / fee_calc['order_value']) * 100
        
        # Optimization recommendation
        recommendation = "EXECUTE"
        if total_cost_pct > 1.0:
            recommendation = "HIGH_COST_WARNING"
        elif slippage_calc['slippage_pct'] > 0.5:
            recommendation = "HIGH_SLIPPAGE_WARNING"
        
        self.metrics['trades_optimized'] += 1
        
        return {
            'symbol': symbol,
            'amount': amount,
            'side': side,
            'order_value': fee_calc['order_value'],
            'fee_amount': fee_calc['fee_amount'],
            'fee_pct': fee_calc['taker_fee_pct'],
            'slippage_amount': slippage_calc['slippage_amount'],
            'slippage_pct': slippage_calc['slippage_pct'],
            'total_cost': total_cost,
            'total_cost_pct': total_cost_pct,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'metrics': self.metrics
        }

if __name__ == '__main__':
    bot = FeeOptimizerBot()
    print("🤖 Fee Optimizer Bot - Test Mode\n")
    
    result = bot.optimize_order('BTC/USDT', 0.001, 'buy')
    print(json.dumps(result, indent=2))
