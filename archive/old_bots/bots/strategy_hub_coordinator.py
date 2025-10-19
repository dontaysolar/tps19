#!/usr/bin/env python3
"""Strategy Hub Coordinator - Manages and coordinates all trading strategies"""
from datetime import datetime
from typing import Dict, List

class StrategyHubCoordinator:
    def __init__(self):
        self.name = "Strategy_Hub_Coordinator"
        self.version = "1.0.0"
        self.enabled = True
        
        self.registered_strategies = {}
        self.strategy_performance = {}
        
        self.metrics = {'strategies_managed': 0, 'signals_aggregated': 0}
    
    def register_strategy(self, strategy_name: str, strategy_instance, weight: float = 1.0):
        """Register a trading strategy"""
        self.registered_strategies[strategy_name] = {
            'instance': strategy_instance,
            'weight': weight,
            'enabled': True,
            'signals_generated': 0,
            'registered_at': datetime.now().isoformat()
        }
        
        self.metrics['strategies_managed'] += 1
    
    def get_all_signals(self, market_data: Dict) -> Dict:
        """Get signals from all enabled strategies"""
        signals = {}
        
        for strategy_name, strategy_info in self.registered_strategies.items():
            if not strategy_info['enabled']:
                continue
            
            try:
                instance = strategy_info['instance']
                
                # Try different method names
                if hasattr(instance, 'analyze'):
                    signal = instance.analyze(market_data)
                elif hasattr(instance, 'predict'):
                    signal = instance.predict(market_data)
                elif hasattr(instance, 'calculate'):
                    signal = instance.calculate(market_data)
                else:
                    signal = {'signal': 'HOLD'}
                
                signals[strategy_name] = {
                    'signal': signal.get('signal', 'HOLD'),
                    'confidence': signal.get('confidence', 0.5),
                    'weight': strategy_info['weight'],
                    'reason': signal.get('reason', '')
                }
                
                strategy_info['signals_generated'] += 1
                
            except Exception as e:
                signals[strategy_name] = {
                    'signal': 'ERROR',
                    'error': str(e)
                }
        
        self.metrics['signals_aggregated'] += 1
        
        return {
            'signals': signals,
            'total_strategies': len(signals),
            'timestamp': datetime.now().isoformat()
        }
    
    def aggregate_signals(self, signals: Dict) -> Dict:
        """Aggregate signals into unified decision"""
        buy_score = 0
        sell_score = 0
        total_weight = 0
        
        for strategy_name, signal_data in signals.items():
            if signal_data.get('signal') == 'ERROR':
                continue
            
            signal = signal_data.get('signal', 'HOLD')
            confidence = signal_data.get('confidence', 0.5)
            weight = signal_data.get('weight', 1.0)
            
            weighted_confidence = confidence * weight
            
            if signal == 'BUY':
                buy_score += weighted_confidence
            elif signal == 'SELL':
                sell_score += weighted_confidence
            
            total_weight += weight
        
        if total_weight == 0:
            return {'final_signal': 'HOLD', 'confidence': 0, 'reason': 'No valid signals'}
        
        buy_pct = buy_score / total_weight if total_weight > 0 else 0
        sell_pct = sell_score / total_weight if total_weight > 0 else 0
        
        if buy_pct > 0.6:
            final_signal = 'BUY'
            confidence = buy_pct
        elif sell_pct > 0.6:
            final_signal = 'SELL'
            confidence = sell_pct
        else:
            final_signal = 'HOLD'
            confidence = 0.5
        
        return {
            'final_signal': final_signal,
            'confidence': confidence,
            'buy_score': buy_pct,
            'sell_score': sell_pct,
            'strategies_consulted': len(signals),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'total_strategies': len(self.registered_strategies),
            'enabled_strategies': sum([1 for s in self.registered_strategies.values() if s['enabled']]),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    hub = StrategyHubCoordinator()
    print(f"✅ {hub.name} v{hub.version} initialized")
