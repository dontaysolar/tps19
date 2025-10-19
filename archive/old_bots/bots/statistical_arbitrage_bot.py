#!/usr/bin/env python3
"""
Statistical Arbitrage Bot
Identifies and exploits mean-reversion in correlated pairs
Uses cointegration and z-score analysis
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple

class StatisticalArbitrageBot:
    def __init__(self):
        self.name = "Statistical_Arbitrage"
        self.version = "1.0.0"
        self.enabled = True
        
        self.entry_zscore = 2.0  # Enter when z-score exceeds this
        self.exit_zscore = 0.5   # Exit when z-score returns to this
        self.lookback_period = 60
        
        self.metrics = {
            'pairs_analyzed': 0,
            'opportunities_found': 0,
            'mean_reversions': 0
        }
    
    def calculate_spread(self, asset1_prices: List[float], asset2_prices: List[float]) -> np.ndarray:
        """Calculate spread between two assets"""
        prices1 = np.array(asset1_prices)
        prices2 = np.array(asset2_prices)
        
        # Calculate hedge ratio using linear regression
        hedge_ratio = np.cov(prices1, prices2)[0,1] / np.var(prices2) if np.var(prices2) > 0 else 1
        
        # Calculate spread
        spread = prices1 - hedge_ratio * prices2
        
        return spread, hedge_ratio
    
    def calculate_zscore(self, spread: np.ndarray) -> float:
        """Calculate z-score of current spread"""
        mean = np.mean(spread[:-1])  # Exclude current
        std = np.std(spread[:-1])
        
        if std == 0:
            return 0
        
        zscore = (spread[-1] - mean) / std
        return zscore
    
    def find_cointegrated_pairs(self, assets_data: Dict[str, List[float]]) -> List[Dict]:
        """
        Find cointegrated asset pairs
        
        Args:
            assets_data: {asset_name: [prices]}
        """
        pairs = []
        asset_names = list(assets_data.keys())
        
        for i, asset1 in enumerate(asset_names):
            for asset2 in asset_names[i+1:]:
                prices1 = assets_data[asset1][-self.lookback_period:]
                prices2 = assets_data[asset2][-self.lookback_period:]
                
                if len(prices1) < self.lookback_period or len(prices2) < self.lookback_period:
                    continue
                
                # Calculate correlation
                correlation = np.corrcoef(prices1, prices2)[0,1]
                
                # Check for high correlation
                if abs(correlation) > 0.7:
                    spread, hedge_ratio = self.calculate_spread(prices1, prices2)
                    zscore = self.calculate_zscore(spread)
                    
                    # Test for mean reversion
                    half_life = self._calculate_half_life(spread)
                    
                    if half_life > 0 and half_life < 30:  # Mean-reverting
                        pairs.append({
                            'asset1': asset1,
                            'asset2': asset2,
                            'correlation': correlation,
                            'hedge_ratio': hedge_ratio,
                            'current_zscore': zscore,
                            'half_life': half_life,
                            'spread_std': np.std(spread)
                        })
                        
                        self.metrics['pairs_analyzed'] += 1
        
        # Sort by absolute z-score (most extreme)
        pairs.sort(key=lambda x: abs(x['current_zscore']), reverse=True)
        
        return pairs
    
    def _calculate_half_life(self, spread: np.ndarray) -> float:
        """Calculate mean reversion half-life"""
        spread_lag = spread[:-1]
        spread_diff = np.diff(spread)
        
        if len(spread_lag) == 0 or np.var(spread_lag) == 0:
            return -1
        
        # AR(1) model
        beta = np.cov(spread_diff, spread_lag)[0,1] / np.var(spread_lag)
        
        if beta >= 0:
            return -1  # Not mean reverting
        
        half_life = -np.log(2) / beta
        return half_life
    
    def generate_pair_trade_signal(self, pair_info: Dict) -> Dict:
        """
        Generate trading signal for a pair
        """
        zscore = pair_info['current_zscore']
        
        # Entry signals
        if zscore > self.entry_zscore:
            # Spread too high - short spread (short asset1, long asset2)
            signal = 'SHORT_SPREAD'
            action = {
                'asset1': 'SELL',
                'asset2': 'BUY',
                'ratio': pair_info['hedge_ratio']
            }
            confidence = min(0.90, 0.70 + (zscore - self.entry_zscore) * 0.05)
            self.metrics['opportunities_found'] += 1
            
        elif zscore < -self.entry_zscore:
            # Spread too low - long spread (long asset1, short asset2)
            signal = 'LONG_SPREAD'
            action = {
                'asset1': 'BUY',
                'asset2': 'SELL',
                'ratio': pair_info['hedge_ratio']
            }
            confidence = min(0.90, 0.70 + (abs(zscore) - self.entry_zscore) * 0.05)
            self.metrics['opportunities_found'] += 1
            
        # Exit signals
        elif abs(zscore) < self.exit_zscore:
            signal = 'CLOSE_SPREAD'
            action = {
                'asset1': 'FLATTEN',
                'asset2': 'FLATTEN'
            }
            confidence = 0.80
            self.metrics['mean_reversions'] += 1
            
        else:
            signal = 'HOLD'
            action = None
            confidence = 0.0
        
        return {
            'signal': signal,
            'action': action,
            'confidence': confidence,
            'zscore': zscore,
            'pair': f"{pair_info['asset1']}/{pair_info['asset2']}",
            'hedge_ratio': pair_info['hedge_ratio'],
            'expected_reversion_time': pair_info.get('half_life', 0),
            'reason': f"Z-score: {zscore:.2f}, Half-life: {pair_info.get('half_life', 0):.1f}",
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'entry_zscore': self.entry_zscore,
            'exit_zscore': self.exit_zscore,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = StatisticalArbitrageBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
