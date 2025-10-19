#!/usr/bin/env python3
"""
SIGNAL GENERATION LAYER
All trading strategies consolidated into unified signal generation
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class SignalGenerationLayer:
    """Generate unified trading signals from all strategies"""
    
    def __init__(self):
        self.name = "Signal_Generation_Layer"
        self.version = "1.0.0"
        
    def generate_unified_signal(self, analysis: Dict) -> Dict:
        """Combine all strategies into single signal"""
        
        signals = []
        
        # Strategy 1: Trend Following
        trend_signal = self.trend_following_strategy(analysis)
        signals.append(trend_signal)
        
        # Strategy 2: Mean Reversion
        reversion_signal = self.mean_reversion_strategy(analysis)
        signals.append(reversion_signal)
        
        # Strategy 3: Momentum
        momentum_signal = self.momentum_strategy(analysis)
        signals.append(momentum_signal)
        
        # Strategy 4: Breakout
        breakout_signal = self.breakout_strategy(analysis)
        signals.append(breakout_signal)
        
        # Strategy 5: Support/Resistance
        sr_signal = self.support_resistance_strategy(analysis)
        signals.append(sr_signal)
        
        # Strategy 6: Volume Analysis
        volume_signal = self.volume_strategy(analysis)
        signals.append(volume_signal)
        
        # Strategy 7: Wyckoff-based
        wyckoff_signal = self.wyckoff_strategy(analysis)
        signals.append(wyckoff_signal)
        
        # Strategy 8: Ichimoku-based
        ichimoku_signal = self.ichimoku_strategy(analysis)
        signals.append(ichimoku_signal)
        
        # Strategy 9: Order Flow
        order_flow_signal = self.order_flow_strategy(analysis)
        signals.append(order_flow_signal)
        
        # Aggregate all signals
        return self.aggregate_signals(signals)
    
    def trend_following_strategy(self, analysis: Dict) -> Dict:
        """Trend following signals"""
        trend = analysis.get('trend', {})
        
        if trend.get('direction') in ['STRONG_UPTREND', 'UPTREND']:
            if trend.get('adx', 0) > 25:
                return {'signal': 'BUY', 'confidence': 0.85, 'strategy': 'TREND', 'weight': 0.25}
            return {'signal': 'BUY', 'confidence': 0.70, 'strategy': 'TREND', 'weight': 0.20}
        
        elif trend.get('direction') in ['STRONG_DOWNTREND', 'DOWNTREND']:
            if trend.get('adx', 0) > 25:
                return {'signal': 'SELL', 'confidence': 0.85, 'strategy': 'TREND', 'weight': 0.25}
            return {'signal': 'SELL', 'confidence': 0.70, 'strategy': 'TREND', 'weight': 0.20}
        
        return {'signal': 'HOLD', 'confidence': 0.50, 'strategy': 'TREND', 'weight': 0.10}
    
    def mean_reversion_strategy(self, analysis: Dict) -> Dict:
        """Mean reversion signals"""
        momentum = analysis.get('momentum', {})
        volatility = analysis.get('volatility', {})
        
        rsi = momentum.get('rsi', 50)
        bb_position = volatility.get('bb_position', 0.5)
        
        # Oversold conditions
        if rsi < 30 and bb_position < 0.2:
            return {'signal': 'BUY', 'confidence': 0.80, 'strategy': 'REVERSION', 'weight': 0.20}
        
        # Overbought conditions
        elif rsi > 70 and bb_position > 0.8:
            return {'signal': 'SELL', 'confidence': 0.80, 'strategy': 'REVERSION', 'weight': 0.20}
        
        return {'signal': 'HOLD', 'confidence': 0.50, 'strategy': 'REVERSION', 'weight': 0.10}
    
    def momentum_strategy(self, analysis: Dict) -> Dict:
        """Momentum-based signals"""
        momentum = analysis.get('momentum', {})
        
        rsi = momentum.get('rsi', 50)
        macd = momentum.get('macd', 0)
        roc = momentum.get('roc', 0)
        
        # Strong momentum signals
        if rsi > 55 and macd > 0 and roc > 2:
            return {'signal': 'BUY', 'confidence': 0.85, 'strategy': 'MOMENTUM', 'weight': 0.20}
        
        elif rsi < 45 and macd < 0 and roc < -2:
            return {'signal': 'SELL', 'confidence': 0.85, 'strategy': 'MOMENTUM', 'weight': 0.20}
        
        return {'signal': 'HOLD', 'confidence': 0.50, 'strategy': 'MOMENTUM', 'weight': 0.10}
    
    def breakout_strategy(self, analysis: Dict) -> Dict:
        """Breakout detection"""
        levels = analysis.get('support_resistance', {})
        volume = analysis.get('volume', {})
        volatility = analysis.get('volatility', {})
        
        current = levels.get('current', 0)
        resistance = levels.get('resistance', 0)
        support = levels.get('support', 0)
        vol_ratio = volume.get('ratio', 1)
        
        # Breakout above resistance with volume
        if current > resistance and vol_ratio > 1.5:
            return {'signal': 'BUY', 'confidence': 0.85, 'strategy': 'BREAKOUT', 'weight': 0.25}
        
        # Breakdown below support with volume
        elif current < support and vol_ratio > 1.5:
            return {'signal': 'SELL', 'confidence': 0.85, 'strategy': 'BREAKOUT', 'weight': 0.25}
        
        # Squeeze (low volatility before breakout)
        elif volatility.get('squeeze', False):
            return {'signal': 'WAIT', 'confidence': 0.70, 'strategy': 'BREAKOUT', 'weight': 0.15}
        
        return {'signal': 'HOLD', 'confidence': 0.50, 'strategy': 'BREAKOUT', 'weight': 0.10}
    
    def support_resistance_strategy(self, analysis: Dict) -> Dict:
        """Support/Resistance bounces"""
        levels = analysis.get('support_resistance', {})
        price_action = analysis.get('price_action', {})
        
        near_support = levels.get('near_support', False)
        near_resistance = levels.get('near_resistance', False)
        structure = price_action.get('structure', '')
        
        # Bounce off support in uptrend
        if near_support and 'UPTREND' in structure:
            return {'signal': 'BUY', 'confidence': 0.80, 'strategy': 'SR', 'weight': 0.20}
        
        # Rejection at resistance in downtrend
        elif near_resistance and 'DOWNTREND' in structure:
            return {'signal': 'SELL', 'confidence': 0.80, 'strategy': 'SR', 'weight': 0.20}
        
        return {'signal': 'HOLD', 'confidence': 0.50, 'strategy': 'SR', 'weight': 0.10}
    
    def volume_strategy(self, analysis: Dict) -> Dict:
        """Volume-based signals"""
        volume = analysis.get('volume', {})
        momentum = analysis.get('momentum', {})
        
        vol_ratio = volume.get('ratio', 1)
        obv = volume.get('obv', 0)
        roc = momentum.get('roc', 0)
        
        # High volume with price increase
        if vol_ratio > 2 and roc > 2:
            return {'signal': 'BUY', 'confidence': 0.80, 'strategy': 'VOLUME', 'weight': 0.20}
        
        # High volume with price decrease
        elif vol_ratio > 2 and roc < -2:
            return {'signal': 'SELL', 'confidence': 0.80, 'strategy': 'VOLUME', 'weight': 0.20}
        
        # Climax volume (potential reversal)
        elif volume.get('climax', False):
            return {'signal': 'REVERSAL', 'confidence': 0.70, 'strategy': 'VOLUME', 'weight': 0.15}
        
        return {'signal': 'HOLD', 'confidence': 0.50, 'strategy': 'VOLUME', 'weight': 0.10}
    
    def wyckoff_strategy(self, analysis: Dict) -> Dict:
        """Wyckoff cycle-based strategy"""
        wyckoff = analysis.get('wyckoff', {})
        phase = wyckoff.get('phase', 'UNKNOWN')
        
        if phase == 'ACCUMULATION':
            return {'signal': 'BUY', 'confidence': 0.85, 'strategy': 'WYCKOFF', 'weight': 0.20}
        elif phase == 'MARKUP':
            return {'signal': 'BUY', 'confidence': 0.80, 'strategy': 'WYCKOFF', 'weight': 0.15}
        elif phase == 'DISTRIBUTION':
            return {'signal': 'SELL', 'confidence': 0.80, 'strategy': 'WYCKOFF', 'weight': 0.15}
        elif phase == 'MARKDOWN':
            return {'signal': 'SELL', 'confidence': 0.85, 'strategy': 'WYCKOFF', 'weight': 0.20}
        
        return {'signal': 'HOLD', 'confidence': 0.50, 'strategy': 'WYCKOFF', 'weight': 0.10}
    
    def ichimoku_strategy(self, analysis: Dict) -> Dict:
        """Ichimoku Cloud strategy"""
        ichimoku = analysis.get('ichimoku', {})
        signal = ichimoku.get('signal', 'NEUTRAL')
        position = ichimoku.get('price_vs_cloud', 'IN_CLOUD')
        
        if signal == 'BULLISH' and position == 'ABOVE':
            return {'signal': 'BUY', 'confidence': 0.80, 'strategy': 'ICHIMOKU', 'weight': 0.20}
        elif signal == 'BEARISH' and position == 'BELOW':
            return {'signal': 'SELL', 'confidence': 0.80, 'strategy': 'ICHIMOKU', 'weight': 0.20}
        
        return {'signal': 'HOLD', 'confidence': 0.50, 'strategy': 'ICHIMOKU', 'weight': 0.10}
    
    def order_flow_strategy(self, analysis: Dict) -> Dict:
        """Order flow-based strategy"""
        order_flow = analysis.get('order_flow', {})
        pressure = order_flow.get('pressure', 'NEUTRAL')
        cvd = order_flow.get('recent_cvd', 0)
        
        if pressure == 'BUYING' and cvd > 0:
            return {'signal': 'BUY', 'confidence': 0.75, 'strategy': 'ORDER_FLOW', 'weight': 0.15}
        elif pressure == 'SELLING' and cvd < 0:
            return {'signal': 'SELL', 'confidence': 0.75, 'strategy': 'ORDER_FLOW', 'weight': 0.15}
        
        return {'signal': 'HOLD', 'confidence': 0.50, 'strategy': 'ORDER_FLOW', 'weight': 0.10}
    
    def aggregate_signals(self, signals: List[Dict]) -> Dict:
        """Aggregate all strategy signals into one"""
        buy_score = 0
        sell_score = 0
        total_weight = 0
        
        strategy_votes = {'BUY': [], 'SELL': [], 'HOLD': []}
        
        for sig in signals:
            signal = sig.get('signal', 'HOLD')
            confidence = sig.get('confidence', 0.5)
            weight = sig.get('weight', 0.1)
            strategy = sig.get('strategy', 'UNKNOWN')
            
            weighted_confidence = confidence * weight
            
            if signal == 'BUY':
                buy_score += weighted_confidence
                strategy_votes['BUY'].append(strategy)
            elif signal == 'SELL':
                sell_score += weighted_confidence
                strategy_votes['SELL'].append(strategy)
            else:
                strategy_votes['HOLD'].append(strategy)
            
            total_weight += weight
        
        # Normalize scores
        buy_score = buy_score / total_weight if total_weight > 0 else 0
        sell_score = sell_score / total_weight if total_weight > 0 else 0
        
        # Determine final signal
        if buy_score > sell_score and buy_score > 0.65:
            final_signal = 'BUY'
            confidence = buy_score
            reason = f"Bullish - {len(strategy_votes['BUY'])} strategies agree"
        elif sell_score > buy_score and sell_score > 0.65:
            final_signal = 'SELL'
            confidence = sell_score
            reason = f"Bearish - {len(strategy_votes['SELL'])} strategies agree"
        else:
            final_signal = 'HOLD'
            confidence = 0.50
            reason = "No consensus - holding"
        
        return {
            'signal': final_signal,
            'confidence': confidence,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'strategies_consulted': len(signals),
            'buy_votes': len(strategy_votes['BUY']),
            'sell_votes': len(strategy_votes['SELL']),
            'hold_votes': len(strategy_votes['HOLD']),
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }

if __name__ == '__main__':
    layer = SignalGenerationLayer()
    print(f"✅ {layer.name} v{layer.version} initialized")
