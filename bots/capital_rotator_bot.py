#!/usr/bin/env python3
"""
Capital Rotation Bot
Reallocates funds to highest ROI pairs dynamically
Part of APEX AI Trading System
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
except ImportError:
    os.system("pip3 install --break-system-packages ccxt -q")
    import ccxt

class CapitalRotatorBot:
    """Optimizes capital allocation across trading pairs"""
    
    def __init__(self, exchange_config: Dict = None):
        self.name = "CapitalRotatorBot"
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
            'reallocation_threshold': 20.0,   # 20% performance diff = reallocate
            'min_allocation_pct': 10.0,       # Min 10% per pair
            'max_allocation_pct': 40.0,       # Max 40% per pair
            'rebalance_interval_hours': 6     # Rebalance every 6 hours
        }
        
        self.allocations = {
            'BTC/USDT': 0.40,
            'ETH/USDT': 0.30,
            'SOL/USDT': 0.15,
            'ADA/USDT': 0.15
        }
        
        self.metrics = {
            'rotations_performed': 0,
            'total_roi_improvement': 0.0,
            'last_rotation': None
        }
        
        self.performance_history = {}
    
    def calculate_pair_roi(self, symbol: str, timeframe: str = '1d') -> float:
        """Calculate ROI for a trading pair over timeframe"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=2)
            
            if len(ohlcv) < 2:
                return 0.0
            
            open_price = ohlcv[0][1]
            close_price = ohlcv[-1][4]
            
            roi = ((close_price - open_price) / open_price) * 100
            
            # Store in history
            if symbol not in self.performance_history:
                self.performance_history[symbol] = []
            
            self.performance_history[symbol].append({
                'timestamp': datetime.now().isoformat(),
                'roi': roi
            })
            
            return roi
            
        except Exception as e:
            print(f"❌ ROI calculation error for {symbol}: {e}")
            return 0.0
    
    def rank_pairs_by_performance(self, symbols: List[str]) -> List[Tuple[str, float]]:
        """Rank pairs by ROI performance"""
        pairs_with_roi = []
        
        for symbol in symbols:
            roi = self.calculate_pair_roi(symbol)
            pairs_with_roi.append((symbol, roi))
        
        # Sort by ROI descending
        pairs_with_roi.sort(key=lambda x: x[1], reverse=True)
        
        return pairs_with_roi
    
    def calculate_optimal_allocation(self, ranked_pairs: List[Tuple[str, float]]) -> Dict[str, float]:
        """Calculate optimal capital allocation based on performance"""
        total_pairs = len(ranked_pairs)
        
        if total_pairs == 0:
            return {}
        
        # Start with equal allocation
        base_allocation = 1.0 / total_pairs
        
        # Adjust based on performance
        new_allocations = {}
        total_roi = sum(abs(roi) for _, roi in ranked_pairs)
        
        if total_roi == 0:
            # No performance data, use equal weights
            for symbol, _ in ranked_pairs:
                new_allocations[symbol] = base_allocation
        else:
            # Weight by ROI, with constraints
            for symbol, roi in ranked_pairs:
                # Convert ROI to positive weight
                weight = (abs(roi) / total_roi) if total_roi > 0 else base_allocation
                
                # Apply min/max constraints
                allocation = max(
                    self.config['min_allocation_pct'] / 100,
                    min(weight, self.config['max_allocation_pct'] / 100)
                )
                
                new_allocations[symbol] = allocation
            
            # Normalize to sum to 1.0
            total_allocation = sum(new_allocations.values())
            for symbol in new_allocations:
                new_allocations[symbol] /= total_allocation
        
        return new_allocations
    
    def should_rebalance(self) -> bool:
        """Check if rebalancing is needed"""
        if self.metrics['last_rotation'] is None:
            return True
        
        last_rotation = datetime.fromisoformat(self.metrics['last_rotation'])
        hours_since = (datetime.now() - last_rotation).total_seconds() / 3600
        
        return hours_since >= self.config['rebalance_interval_hours']
    
    def rebalance_capital(self, symbols: List[str] = None) -> Dict:
        """Perform capital rebalancing"""
        if symbols is None:
            symbols = list(self.allocations.keys())
        
        if not self.should_rebalance():
            return {
                'rebalanced': False,
                'reason': 'Too soon since last rebalance'
            }
        
        # Rank pairs by performance
        ranked_pairs = self.rank_pairs_by_performance(symbols)
        
        # Calculate optimal allocation
        new_allocations = self.calculate_optimal_allocation(ranked_pairs)
        
        # Calculate allocation changes
        changes = {}
        significant_change = False
        
        for symbol in symbols:
            old_alloc = self.allocations.get(symbol, 0)
            new_alloc = new_allocations.get(symbol, 0)
            change_pct = abs(new_alloc - old_alloc) * 100
            
            changes[symbol] = {
                'old': old_alloc,
                'new': new_alloc,
                'change_pct': change_pct
            }
            
            if change_pct >= self.config['reallocation_threshold']:
                significant_change = True
        
        if significant_change:
            # Update allocations
            self.allocations = new_allocations
            self.metrics['rotations_performed'] += 1
            self.metrics['last_rotation'] = datetime.now().isoformat()
            
            return {
                'rebalanced': True,
                'ranked_pairs': ranked_pairs,
                'new_allocations': new_allocations,
                'changes': changes,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'rebalanced': False,
                'reason': 'No significant changes needed',
                'changes': changes
            }
    
    def get_current_allocation(self) -> Dict:
        """Get current capital allocation"""
        return {
            'allocations': self.allocations,
            'last_update': self.metrics['last_rotation'],
            'total_rotations': self.metrics['rotations_performed']
        }
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'allocations': self.allocations,
            'metrics': self.metrics,
            'config': self.config
        }

if __name__ == '__main__':
    bot = CapitalRotatorBot()
    print("🔄 Capital Rotator Bot - Test Mode\n")
    
    result = bot.rebalance_capital()
    print(json.dumps(result, indent=2))
