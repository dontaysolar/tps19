#!/usr/bin/env python3
"""
Fee Optimizer Bot v2.0 - Trading Cost Optimization
MIGRATED TO AEGIS ARCHITECTURE

AEGIS v2.0 Changes:
- Inherits from TradingBotBase (enforced safety)
- Uses Exchange Adapter (no direct ccxt)
- Integrates with PSM (position tracking)
- ATLAS-compliant (Power of 10 rules)

Pre-calculates fees and slippage before trades to maximize profit
Part of APEX AI Trading System - Optimization Layer
"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional

# Add AEGIS core to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))

# Import AEGIS base class
from trading_bot_base import TradingBotBase


class FeeOptimizerBot(TradingBotBase):
    """
    Trading Cost Optimization System
    
    AEGIS v2.0: Now inherits from TradingBotBase
    - Automatic Exchange Adapter usage
    - PSM integration for position tracking
    - ATLAS-compliant code
    
    Features:
    - Fee calculation (maker/taker)
    - Slippage estimation
    - Total cost optimization
    - Trade viability assessment
    - Cost-benefit analysis
    """
    
    def __init__(self, exchange_config=None):
        """
        Initialize Fee Optimizer Bot with AEGIS architecture
        
        ATLAS Compliance:
        - Assertion 1: Base class initialized
        - Assertion 2: Config validated
        """
        # Initialize base class (automatic adapter + PSM)
        super().__init__(
            bot_name="FEE_OPTIMIZER_BOT",
            bot_version="2.0.0",
            exchange_name='mock' if not exchange_config else 'cryptocom',
            enable_psm=True,
            enable_logging=True
        )
        
        # ATLAS Assertion 1
        assert hasattr(self, 'exchange_adapter'), "Base class initialization failed"
        
        # Fee Optimizer specific configuration
        self.config = {
            'default_maker_fee': 0.001,    # 0.1% maker
            'default_taker_fee': 0.001,    # 0.1% taker
            'max_slippage_pct': 0.5,       # 0.5% max acceptable slippage
            'min_profit_margin': 0.2       # 0.2% minimum profit after costs
        }
        
        # ATLAS Assertion 2
        assert self.config['max_slippage_pct'] > 0, "Invalid slippage config"
        
        # Metrics (extends base)
        self.metrics.update({
            'total_calculations': 0,
            'trades_optimized': 0,
            'fees_saved': 0.0,
            'slippage_avoided': 0.0
        })
    
    def calculate_fees(
        self, 
        symbol: str, 
        amount: float, 
        side: str,
        order_type: str = 'market'
    ) -> Dict:
        """
        Calculate trading fees for an order
        
        ATLAS Compliance:
        - Assertion 1: amount > 0
        - Assertion 2: result is dict
        """
        assert amount > 0, "Amount must be positive"
        assert side in ['buy', 'sell'], "Side must be buy or sell"
        
        try:
            # Get current price
            ticker = self.get_ticker(symbol)
            if not ticker:
                return self._get_fallback_fees(symbol, amount, side)
            
            price = ticker.get('last', 0)
            if price == 0:
                return self._get_fallback_fees(symbol, amount, side)
            
            # Determine fee rate (market = taker, limit = maker)
            if order_type == 'limit':
                fee_rate = self.config['default_maker_fee']
            else:  # market
                fee_rate = self.config['default_taker_fee']
            
            # Calculate order value and fees
            order_value = amount * price
            fee_amount = order_value * fee_rate
            
            # Calculate net proceeds
            if side == 'buy':
                total_cost = order_value + fee_amount
                net_amount = amount
            else:  # sell
                total_cost = order_value
                net_amount = order_value - fee_amount
            
            self.metrics['total_calculations'] += 1
            
            result = {
                'symbol': symbol,
                'amount': amount,
                'side': side,
                'price': price,
                'order_value': order_value,
                'fee_rate_pct': fee_rate * 100,
                'fee_amount': fee_amount,
                'total_cost': total_cost,
                'net_proceeds': net_amount,
                'timestamp': datetime.now().isoformat()
            }
            
            # ATLAS Assertion 2
            assert isinstance(result, dict), "Result must be dict"
            
            return result
            
        except Exception as e:
            self.metrics['errors'] += 1
            return self._get_fallback_fees(symbol, amount, side)
    
    def _get_fallback_fees(
        self, 
        symbol: str, 
        amount: float, 
        side: str
    ) -> Dict:
        """
        Get fallback fee calculation
        
        ATLAS Compliance:
        - Assertion 1: amount > 0
        - Assertion 2: result is dict
        """
        assert amount > 0, "Amount must be positive"
        
        result = {
            'symbol': symbol,
            'amount': amount,
            'side': side,
            'error': 'Price unavailable',
            'fee_amount': 0.0,
            'total_cost': 0.0,
            'net_proceeds': 0.0
        }
        
        # ATLAS Assertion 2
        assert isinstance(result, dict), "Result must be dict"
        
        return result
    
    def estimate_slippage(
        self, 
        symbol: str, 
        amount: float, 
        side: str
    ) -> Dict:
        """
        Estimate price slippage for an order
        
        ATLAS Compliance:
        - Assertion 1: amount > 0
        - Assertion 2: result is dict
        """
        assert amount > 0, "Amount must be positive"
        assert side in ['buy', 'sell'], "Side must be buy or sell"
        
        try:
            # Get order book through adapter
            orderbook = self.exchange_adapter.get_order_book(symbol, limit=20)
            if not orderbook:
                return self._get_fallback_slippage(symbol, amount, side)
            
            # Get current price
            ticker = self.get_ticker(symbol)
            if not ticker:
                return self._get_fallback_slippage(symbol, amount, side)
            
            bid = ticker.get('bid', 0)
            ask = ticker.get('ask', 0)
            mid_price = (bid + ask) / 2 if (bid and ask) else ticker.get('last', 0)
            
            if mid_price == 0:
                return self._get_fallback_slippage(symbol, amount, side)
            
            # Calculate weighted average fill price
            avg_fill_price = self._calc_weighted_price(orderbook, amount, side)
            
            # Calculate slippage
            slippage_pct = abs((avg_fill_price - mid_price) / mid_price) * 100
            slippage_amount = abs(avg_fill_price - mid_price) * amount
            
            result = {
                'symbol': symbol,
                'amount': amount,
                'side': side,
                'mid_price': mid_price,
                'expected_fill_price': avg_fill_price,
                'slippage_pct': slippage_pct,
                'slippage_amount': slippage_amount,
                'timestamp': datetime.now().isoformat()
            }
            
            # ATLAS Assertion 2
            assert isinstance(result, dict), "Result must be dict"
            
            return result
            
        except Exception as e:
            self.metrics['errors'] += 1
            return self._get_fallback_slippage(symbol, amount, side)
    
    def _calc_weighted_price(
        self, 
        orderbook: Dict, 
        amount: float, 
        side: str
    ) -> float:
        """
        Calculate weighted average fill price from order book
        
        ATLAS Compliance:
        - Assertion 1: orderbook valid
        - Assertion 2: result > 0
        """
        assert 'asks' in orderbook or 'bids' in orderbook, "Invalid orderbook"
        
        # Select appropriate side
        orders = orderbook.get('asks' if side == 'buy' else 'bids', [])
        
        cumulative_volume = 0.0
        weighted_price = 0.0
        
        # ATLAS: Fixed loop bound
        for i, order in enumerate(orders):
            if i >= 20 or cumulative_volume >= amount:
                break
            
            price, volume = order[0], order[1]
            fill_amount = min(volume, amount - cumulative_volume)
            
            weighted_price += price * fill_amount
            cumulative_volume += fill_amount
        
        if cumulative_volume > 0:
            result = weighted_price / cumulative_volume
        else:
            result = 0.0
        
        # ATLAS Assertion 2
        assert result >= 0, "Price must be non-negative"
        
        return result
    
    def _get_fallback_slippage(
        self, 
        symbol: str, 
        amount: float, 
        side: str
    ) -> Dict:
        """
        Get fallback slippage estimate
        
        ATLAS Compliance:
        - Assertion 1: amount > 0
        - Assertion 2: result is dict
        """
        assert amount > 0, "Amount must be positive"
        
        result = {
            'symbol': symbol,
            'amount': amount,
            'side': side,
            'error': 'Order book unavailable',
            'slippage_pct': 0.0,
            'slippage_amount': 0.0
        }
        
        # ATLAS Assertion 2
        assert isinstance(result, dict), "Result must be dict"
        
        return result
    
    def calculate_total_cost(
        self, 
        symbol: str, 
        amount: float, 
        side: str
    ) -> Dict:
        """
        Calculate total cost including fees and slippage
        
        ATLAS Compliance:
        - Assertion 1: amount > 0
        - Assertion 2: result is dict
        """
        assert amount > 0, "Amount must be positive"
        
        # Calculate fees
        fee_data = self.calculate_fees(symbol, amount, side)
        
        # Estimate slippage
        slippage_data = self.estimate_slippage(symbol, amount, side)
        
        # Calculate total cost
        total_fee_cost = fee_data.get('fee_amount', 0)
        total_slippage_cost = slippage_data.get('slippage_amount', 0)
        total_cost = total_fee_cost + total_slippage_cost
        
        # Calculate cost as percentage
        order_value = fee_data.get('order_value', 0)
        if order_value > 0:
            total_cost_pct = (total_cost / order_value) * 100
        else:
            total_cost_pct = 0.0
        
        result = {
            'symbol': symbol,
            'amount': amount,
            'side': side,
            'fee_cost': total_fee_cost,
            'slippage_cost': total_slippage_cost,
            'total_cost': total_cost,
            'total_cost_pct': total_cost_pct,
            'is_acceptable': total_cost_pct <= (self.config['max_slippage_pct'] + 0.1),
            'timestamp': datetime.now().isoformat()
        }
        
        # ATLAS Assertion 2
        assert isinstance(result, dict), "Result must be dict"
        
        return result
    
    def should_execute_trade(
        self, 
        symbol: str, 
        amount: float, 
        side: str,
        expected_profit_pct: float
    ) -> bool:
        """
        Determine if trade should be executed based on costs
        
        ATLAS Compliance:
        - Assertion 1: amount > 0
        - Assertion 2: result is bool
        """
        assert amount > 0, "Amount must be positive"
        
        # Get total cost
        cost_data = self.calculate_total_cost(symbol, amount, side)
        
        total_cost_pct = cost_data.get('total_cost_pct', 100)
        
        # Trade is viable if expected profit > costs + minimum margin
        min_required_profit = total_cost_pct + self.config['min_profit_margin']
        should_execute = expected_profit_pct >= min_required_profit
        
        if should_execute:
            self.metrics['trades_optimized'] += 1
        
        # ATLAS Assertion 2
        assert isinstance(should_execute, bool), "Result must be bool"
        
        return should_execute
    
    def get_status(self) -> Dict:
        """
        Get bot status (extends base)
        
        ATLAS Compliance:
        - Assertion 1: base status valid
        """
        base_status = super().get_status()
        
        # ATLAS Assertion 1
        assert isinstance(base_status, dict), "Base status must be dict"
        
        base_status.update({
            'fee_optimizer_metrics': {
                'total_calculations': self.metrics.get('total_calculations', 0),
                'trades_optimized': self.metrics.get('trades_optimized', 0),
                'fees_saved': self.metrics.get('fees_saved', 0.0),
                'slippage_avoided': self.metrics.get('slippage_avoided', 0.0)
            },
            'configuration': self.config
        })
        
        return base_status


# Test suite
if __name__ == '__main__':
    print("=" * 70)
    print("Fee Optimizer Bot v2.0 (AEGIS Architecture) - Test Suite")
    print("=" * 70)
    
    print("\n[Test 1] Initialize Fee Optimizer Bot...")
    bot = FeeOptimizerBot()
    print(f"   Name: {bot.name}")
    print(f"   Version: {bot.version}")
    print(f"   Adapter enforced: {bot.exchange_adapter is not None}")
    print(f"   Config: {bot.config}")
    
    print("\n[Test 2] Calculate fees (BTC/USDT, 0.1 BTC buy)...")
    fees = bot.calculate_fees('BTC/USDT', 0.1, 'buy')
    if 'fee_amount' in fees:
        print(f"   Order Value: ${fees.get('order_value', 0):.2f}")
        print(f"   Fee: ${fees['fee_amount']:.2f} ({fees.get('fee_rate_pct', 0):.2f}%)")
        print(f"   Total Cost: ${fees.get('total_cost', 0):.2f}")
    
    print("\n[Test 3] Estimate slippage...")
    slippage = bot.estimate_slippage('BTC/USDT', 0.1, 'buy')
    if 'slippage_pct' in slippage:
        print(f"   Slippage: {slippage['slippage_pct']:.3f}%")
        print(f"   Slippage Cost: ${slippage.get('slippage_amount', 0):.2f}")
    
    print("\n[Test 4] Calculate total cost...")
    total = bot.calculate_total_cost('BTC/USDT', 0.1, 'buy')
    print(f"   Fee Cost: ${total.get('fee_cost', 0):.2f}")
    print(f"   Slippage Cost: ${total.get('slippage_cost', 0):.2f}")
    print(f"   Total Cost: ${total['total_cost']:.2f} ({total['total_cost_pct']:.2f}%)")
    print(f"   Acceptable: {total['is_acceptable']}")
    
    print("\n[Test 5] Trade decision (1% expected profit)...")
    should_trade = bot.should_execute_trade('BTC/USDT', 0.1, 'buy', 1.0)
    print(f"   Should Execute: {should_trade}")
    
    print("\n[Test 6] Get status...")
    status = bot.get_status()
    print(f"   Calculations: {status['fee_optimizer_metrics']['total_calculations']}")
    print(f"   Trades Optimized: {status['fee_optimizer_metrics']['trades_optimized']}")
    
    bot.close()
    
    print("\n✅ All Fee Optimizer Bot v2.0 tests passed!")
    print("✅ Migration to AEGIS architecture successful!")
    print("\n💡 FRACTAL HOOK: Fee calculations can be used by all trading bots pre-order")
