#!/usr/bin/env python3
"""Adaptive Strategy Selector - Auto-selects best strategy for market regime"""
from datetime import datetime
from typing import Dict, List

class AdaptiveStrategySelector:
    def __init__(self):
        self.name = "Adaptive_Strategy_Selector"
        self.version = "1.0.0"
        self.enabled = True
        
        self.strategy_performance = {}
        self.current_regime = 'UNKNOWN'
        
        self.metrics = {'regime_changes': 0, 'strategy_switches': 0}
    
    def detect_market_regime(self, ohlcv: List) -> str:
        """Detect current market regime"""
        if len(ohlcv) < 50:
            return 'UNKNOWN'
        
        import numpy as np
        closes = np.array([c[4] for c in ohlcv[-50:]])
        
        # Calculate metrics
        volatility = np.std(closes) / np.mean(closes)
        trend = (closes[-1] - closes[0]) / closes[0]
        
        # Classify regime
        if abs(trend) > 0.10 and volatility < 0.03:
            regime = 'TRENDING'
        elif abs(trend) < 0.05 and volatility < 0.02:
            regime = 'RANGING'
        elif volatility > 0.05:
            regime = 'VOLATILE'
        else:
            regime = 'TRANSITIONING'
        
        if regime != self.current_regime:
            self.metrics['regime_changes'] += 1
            self.current_regime = regime
        
        return regime
    
    def select_strategy(self, regime: str, available_strategies: Dict) -> Dict:
        """Select best strategy for regime"""
        strategy_recommendations = {
            'TRENDING': 'trend_following',
            'RANGING': 'mean_reversion',
            'VOLATILE': 'breakout',
            'TRANSITIONING': 'conservative'
        }
        
        recommended = strategy_recommendations.get(regime, 'conservative')
        
        # Check if strategy exists and its performance
        if recommended in available_strategies:
            strategy = available_strategies[recommended]
            performance = self.strategy_performance.get(recommended, {})
            
            self.metrics['strategy_switches'] += 1
            
            return {
                'selected_strategy': recommended,
                'regime': regime,
                'confidence': 0.80,
                'past_performance': performance,
                'timestamp': datetime.now().isoformat()
            }
        
        return {'selected_strategy': 'conservative', 'regime': regime, 'confidence': 0.50}
    
    def update_performance(self, strategy_name: str, metrics: Dict):
        """Update strategy performance"""
        self.strategy_performance[strategy_name] = metrics
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'current_regime': self.current_regime,
            'tracked_strategies': len(self.strategy_performance),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    selector = AdaptiveStrategySelector()
    print(f"✅ {selector.name} v{selector.version} initialized")
