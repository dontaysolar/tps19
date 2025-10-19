#!/usr/bin/env python3
"""
Correlation Matrix Bot
Analyzes correlations between assets for:
- Portfolio diversification
- Pair trading opportunities
- Risk management
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class CorrelationMatrixBot:
    def __init__(self):
        self.name = "Correlation_Matrix"
        self.version = "1.0.0"
        self.enabled = True
        
        self.lookback = 30
        
        self.metrics = {
            'correlations_calculated': 0,
            'pairs_identified': 0,
            'diversification_checks': 0
        }
    
    def calculate_correlations(self, asset_prices: Dict[str, List[float]]) -> Dict:
        """
        Calculate correlation matrix for multiple assets
        
        Args:
            asset_prices: {'BTC': [prices], 'ETH': [prices], ...}
        """
        if len(asset_prices) < 2:
            return {'error': 'Need at least 2 assets'}
        
        # Calculate returns for each asset
        returns_data = {}
        for asset, prices in asset_prices.items():
            if len(prices) < 2:
                continue
            returns = np.diff(prices) / prices[:-1]
            returns_data[asset] = returns[-self.lookback:]
        
        # Build correlation matrix
        assets = list(returns_data.keys())
        n = len(assets)
        corr_matrix = np.zeros((n, n))
        
        for i, asset1 in enumerate(assets):
            for j, asset2 in enumerate(assets):
                if i == j:
                    corr_matrix[i][j] = 1.0
                else:
                    corr = np.corrcoef(returns_data[asset1], returns_data[asset2])[0, 1]
                    corr_matrix[i][j] = corr
        
        # Find pair trading opportunities
        pairs = self._find_pair_opportunities(corr_matrix, assets)
        
        # Calculate diversification score
        div_score = self._calculate_diversification_score(corr_matrix)
        
        self.metrics['correlations_calculated'] += 1
        self.metrics['pairs_identified'] += len(pairs)
        self.metrics['diversification_checks'] += 1
        
        return {
            'assets': assets,
            'correlation_matrix': corr_matrix.tolist(),
            'pair_opportunities': pairs,
            'diversification_score': div_score,
            'highly_correlated': self._find_highly_correlated(corr_matrix, assets),
            'negatively_correlated': self._find_negatively_correlated(corr_matrix, assets),
            'timestamp': datetime.now().isoformat()
        }
    
    def _find_pair_opportunities(self, corr_matrix, assets) -> List[Dict]:
        """Find pair trading opportunities (high correlation)"""
        pairs = []
        n = len(assets)
        
        for i in range(n):
            for j in range(i + 1, n):
                corr = corr_matrix[i][j]
                
                # High positive correlation = pair trade opportunity
                if abs(corr) > 0.8:
                    pairs.append({
                        'asset1': assets[i],
                        'asset2': assets[j],
                        'correlation': corr,
                        'type': 'POSITIVE' if corr > 0 else 'NEGATIVE',
                        'strength': abs(corr)
                    })
        
        return sorted(pairs, key=lambda x: x['strength'], reverse=True)
    
    def _calculate_diversification_score(self, corr_matrix) -> float:
        """Calculate portfolio diversification score (0-100)"""
        n = corr_matrix.shape[0]
        
        # Average correlation (excluding diagonal)
        mask = ~np.eye(n, dtype=bool)
        avg_corr = np.abs(corr_matrix[mask]).mean()
        
        # Lower correlation = better diversification
        div_score = (1 - avg_corr) * 100
        
        return div_score
    
    def _find_highly_correlated(self, corr_matrix, assets, threshold=0.7) -> List[Dict]:
        """Find highly correlated asset pairs"""
        pairs = []
        n = len(assets)
        
        for i in range(n):
            for j in range(i + 1, n):
                if corr_matrix[i][j] > threshold:
                    pairs.append({
                        'asset1': assets[i],
                        'asset2': assets[j],
                        'correlation': corr_matrix[i][j]
                    })
        
        return pairs
    
    def _find_negatively_correlated(self, corr_matrix, assets, threshold=-0.5) -> List[Dict]:
        """Find negatively correlated assets (good for hedging)"""
        pairs = []
        n = len(assets)
        
        for i in range(n):
            for j in range(i + 1, n):
                if corr_matrix[i][j] < threshold:
                    pairs.append({
                        'asset1': assets[i],
                        'asset2': assets[j],
                        'correlation': corr_matrix[i][j],
                        'hedge_potential': abs(corr_matrix[i][j])
                    })
        
        return pairs
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'lookback_period': self.lookback,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = CorrelationMatrixBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
