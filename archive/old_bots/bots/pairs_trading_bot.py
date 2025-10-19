#!/usr/bin/env python3
"""
Pairs Trading Bot
Long/short strategy on correlated assets
Beta-neutral market exposure
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class PairsTradingBot:
    def __init__(self):
        self.name = "Pairs_Trading"
        self.version = "1.0.0"
        self.enabled = True
        
        self.correlation_threshold = 0.75
        self.divergence_threshold = 0.02  # 2%
        
        self.metrics = {
            'pairs_traded': 0,
            'successful_convergences': 0,
            'beta_neutral_trades': 0
        }
    
    def calculate_beta(self, asset_returns: np.ndarray, market_returns: np.ndarray) -> float:
        """Calculate beta of asset vs market"""
        covariance = np.cov(asset_returns, market_returns)[0,1]
        market_variance = np.var(market_returns)
        return covariance / market_variance if market_variance > 0 else 1.0
    
    def find_pairs(self, assets: Dict[str, List[float]]) -> List[Dict]:
        """Find suitable pairs for trading"""
        pairs = []
        names = list(assets.keys())
        
        for i, asset1 in enumerate(names):
            for asset2 in names[i+1:]:
                prices1 = np.array(assets[asset1][-50:])
                prices2 = np.array(assets[asset2][-50:])
                
                if len(prices1) < 50 or len(prices2) < 50:
                    continue
                
                # Calculate returns
                returns1 = np.diff(prices1) / prices1[:-1]
                returns2 = np.diff(prices2) / prices2[:-1]
                
                # Correlation
                correlation = np.corrcoef(returns1, returns2)[0,1]
                
                if correlation > self.correlation_threshold:
                    # Calculate price ratio
                    ratio = prices1 / prices2
                    ratio_mean = np.mean(ratio)
                    ratio_std = np.std(ratio)
                    current_ratio = ratio[-1]
                    
                    # Divergence from mean
                    divergence = (current_ratio - ratio_mean) / ratio_mean
                    
                    pairs.append({
                        'asset1': asset1,
                        'asset2': asset2,
                        'correlation': correlation,
                        'ratio_mean': ratio_mean,
                        'ratio_std': ratio_std,
                        'current_ratio': current_ratio,
                        'divergence': divergence,
                        'z_score': (current_ratio - ratio_mean) / ratio_std if ratio_std > 0 else 0
                    })
        
        return sorted(pairs, key=lambda x: abs(x['divergence']), reverse=True)
    
    def generate_signal(self, pair: Dict) -> Dict:
        """Generate pair trade signal"""
        z_score = pair['z_score']
        
        if z_score > 2.0:
            # Asset1 relatively expensive - short asset1, long asset2
            signal = 'SHORT_LONG'
            action = {'asset1': 'SELL', 'asset2': 'BUY'}
            confidence = min(0.90, 0.70 + (z_score - 2.0) * 0.05)
            self.metrics['pairs_traded'] += 1
            
        elif z_score < -2.0:
            # Asset1 relatively cheap - long asset1, short asset2
            signal = 'LONG_SHORT'
            action = {'asset1': 'BUY', 'asset2': 'SELL'}
            confidence = min(0.90, 0.70 + (abs(z_score) - 2.0) * 0.05)
            self.metrics['pairs_traded'] += 1
            
        elif abs(z_score) < 0.5:
            # Converged - close positions
            signal = 'CLOSE'
            action = {'asset1': 'CLOSE', 'asset2': 'CLOSE'}
            confidence = 0.85
            self.metrics['successful_convergences'] += 1
        else:
            signal = 'HOLD'
            action = None
            confidence = 0.0
        
        return {
            'signal': signal,
            'action': action,
            'confidence': confidence,
            'z_score': z_score,
            'pair': f"{pair['asset1']}/{pair['asset2']}",
            'correlation': pair['correlation'],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = PairsTradingBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
