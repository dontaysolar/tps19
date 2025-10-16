#!/usr/bin/env python3
"""
Advanced Brain - Enhanced AI Decision Making
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from modules.intelligence.ml_predictor import ml_predictor
from modules.intelligence.market_regime import regime_detector
from modules.utils.logger import get_logger

logger = get_logger(__name__)


class AdvancedBrain:
    """
    Enhanced AI brain with multi-model decision fusion
    """
    
    def __init__(self):
        self.ml_predictor = ml_predictor
        self.regime_detector = regime_detector
        
        # Decision weights based on model performance
        self.model_weights = {
            'ml_prediction': 0.35,
            'technical_signals': 0.25,
            'market_regime': 0.20,
            'volume_analysis': 0.10,
            'momentum': 0.10
        }
        
        # Performance tracking for adaptive weighting
        self.model_performance = {
            'ml_prediction': {'correct': 0, 'total': 0},
            'technical_signals': {'correct': 0, 'total': 0},
            'market_regime': {'correct': 0, 'total': 0},
        }
        
        self.decision_history = []
        
    def analyze_and_decide(self, market_data: pd.DataFrame, 
                          portfolio: Dict) -> Optional[Dict]:
        """
        Advanced multi-model decision making
        
        Args:
            market_data: Recent OHLCV data
            portfolio: Current portfolio state
            
        Returns:
            Trading decision or None
        """
        if len(market_data) < 100:
            logger.warning("Insufficient data for advanced analysis")
            return None
        
        # 1. ML Prediction
        ml_result = self._get_ml_prediction(market_data)
        
        # 2. Technical Analysis
        technical_result = self._analyze_technicals(market_data)
        
        # 3. Market Regime
        regime_result = self._analyze_regime(market_data)
        
        # 4. Volume Analysis
        volume_result = self._analyze_volume(market_data)
        
        # 5. Momentum Analysis
        momentum_result = self._analyze_momentum(market_data)
        
        # Fuse all signals
        decision = self._fuse_signals({
            'ml_prediction': ml_result,
            'technical_signals': technical_result,
            'market_regime': regime_result,
            'volume_analysis': volume_result,
            'momentum': momentum_result
        })
        
        if decision:
            # Add context
            decision['analysis'] = {
                'ml': ml_result,
                'technical': technical_result,
                'regime': regime_result,
                'volume': volume_result,
                'momentum': momentum_result
            }
            
            # Store for learning
            self.decision_history.append({
                'timestamp': datetime.now(),
                'decision': decision,
                'market_price': market_data['close'].iloc[-1]
            })
        
        return decision
    
    def _get_ml_prediction(self, df: pd.DataFrame) -> Dict:
        """Get ML model prediction"""
        try:
            prediction = self.ml_predictor.predict(df)
            
            return {
                'signal': prediction['direction'],
                'confidence': prediction['confidence'],
                'strength': prediction['confidence'],
                'details': prediction
            }
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return {'signal': 'NEUTRAL', 'confidence': 0.5, 'strength': 0.5}
    
    def _analyze_technicals(self, df: pd.DataFrame) -> Dict:
        """Technical indicator analysis"""
        latest = df.iloc[-1]
        
        # Calculate indicators
        ma20 = df['close'].rolling(20).mean().iloc[-1]
        ma50 = df['close'].rolling(50).mean().iloc[-1]
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-10)
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # MACD
        ema12 = df['close'].ewm(span=12).mean().iloc[-1]
        ema26 = df['close'].ewm(span=26).mean().iloc[-1]
        macd = ema12 - ema26
        
        # Bollinger Bands
        bb_ma = df['close'].rolling(20).mean().iloc[-1]
        bb_std = df['close'].rolling(20).std().iloc[-1]
        bb_upper = bb_ma + (2 * bb_std)
        bb_lower = bb_ma - (2 * bb_std)
        
        # Score each indicator
        scores = []
        
        # MA trend
        if ma20 > ma50:
            scores.append(1)  # Bullish
        elif ma20 < ma50:
            scores.append(-1)  # Bearish
        else:
            scores.append(0)
        
        # Price vs MA
        if latest['close'] > ma20:
            scores.append(1)
        elif latest['close'] < ma20:
            scores.append(-1)
        else:
            scores.append(0)
        
        # RSI
        if rsi < 30:
            scores.append(1)  # Oversold, bullish
        elif rsi > 70:
            scores.append(-1)  # Overbought, bearish
        else:
            scores.append(0)
        
        # MACD
        if macd > 0:
            scores.append(1)
        else:
            scores.append(-1)
        
        # BB position
        if latest['close'] < bb_lower:
            scores.append(1)  # Below lower band, bullish
        elif latest['close'] > bb_upper:
            scores.append(-1)  # Above upper band, bearish
        else:
            scores.append(0)
        
        # Aggregate
        total_score = sum(scores)
        signal = 'UP' if total_score > 0 else 'DOWN' if total_score < 0 else 'NEUTRAL'
        strength = abs(total_score) / len(scores)
        
        return {
            'signal': signal,
            'confidence': 0.5 + (strength * 0.3),  # 0.5 to 0.8
            'strength': strength,
            'indicators': {
                'rsi': rsi,
                'macd': macd,
                'bb_position': (latest['close'] - bb_lower) / (bb_upper - bb_lower),
                'ma_trend': 'bullish' if ma20 > ma50 else 'bearish'
            }
        }
    
    def _analyze_regime(self, df: pd.DataFrame) -> Dict:
        """Market regime analysis"""
        regime = self.regime_detector.detect(df)
        
        # Strategy preferences by regime
        regime_signals = {
            'STRONG_TREND': {'signal': 'FOLLOW_TREND', 'confidence': 0.8},
            'WEAK_TREND': {'signal': 'FOLLOW_TREND', 'confidence': 0.6},
            'RANGING': {'signal': 'MEAN_REVERT', 'confidence': 0.7},
            'BREAKOUT_SETUP': {'signal': 'WAIT_BREAKOUT', 'confidence': 0.6},
            'HIGH_VOLATILITY': {'signal': 'REDUCE_SIZE', 'confidence': 0.9},
            'UNCERTAIN': {'signal': 'NEUTRAL', 'confidence': 0.5}
        }
        
        result = regime_signals.get(regime.name, {'signal': 'NEUTRAL', 'confidence': 0.5})
        result['regime'] = regime.name
        result['strength'] = result['confidence']
        
        return result
    
    def _analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Volume-based analysis"""
        latest_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].rolling(20).mean().iloc[-1]
        
        volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 1
        
        # Volume trend
        volume_trend = df['volume'].rolling(5).mean().iloc[-1] / df['volume'].rolling(20).mean().iloc[-1]
        
        # Price-volume correlation
        price_change = df['close'].pct_change().iloc[-5:].sum()
        volume_change = df['volume'].pct_change().iloc[-5:].sum()
        
        # Signal logic
        if volume_ratio > 1.5 and price_change > 0:
            signal = 'UP'
            confidence = min(0.8, 0.5 + (volume_ratio - 1) * 0.2)
        elif volume_ratio > 1.5 and price_change < 0:
            signal = 'DOWN'
            confidence = min(0.8, 0.5 + (volume_ratio - 1) * 0.2)
        else:
            signal = 'NEUTRAL'
            confidence = 0.5
        
        return {
            'signal': signal,
            'confidence': confidence,
            'strength': confidence - 0.5,
            'volume_ratio': volume_ratio,
            'volume_trend': volume_trend
        }
    
    def _analyze_momentum(self, df: pd.DataFrame) -> Dict:
        """Momentum analysis"""
        # Recent returns
        returns_1h = df['close'].pct_change(12).iloc[-1]  # 12 * 5min
        returns_4h = df['close'].pct_change(48).iloc[-1]
        returns_24h = df['close'].pct_change(288).iloc[-1]
        
        # Consecutive candles
        recent_closes = df['close'].iloc[-5:]
        consecutive_up = all(recent_closes.diff()[1:] > 0)
        consecutive_down = all(recent_closes.diff()[1:] < 0)
        
        # Momentum score
        momentum_score = (
            returns_1h * 3 +
            returns_4h * 2 +
            returns_24h * 1
        ) / 6
        
        if consecutive_up or momentum_score > 0.02:
            signal = 'UP'
            confidence = min(0.8, 0.5 + abs(momentum_score) * 10)
        elif consecutive_down or momentum_score < -0.02:
            signal = 'DOWN'
            confidence = min(0.8, 0.5 + abs(momentum_score) * 10)
        else:
            signal = 'NEUTRAL'
            confidence = 0.5
        
        return {
            'signal': signal,
            'confidence': confidence,
            'strength': abs(momentum_score),
            'momentum_score': momentum_score,
            'consecutive_up': consecutive_up,
            'consecutive_down': consecutive_down
        }
    
    def _fuse_signals(self, signals: Dict[str, Dict]) -> Optional[Dict]:
        """
        Fuse all signals using weighted voting
        """
        # Calculate weighted scores for UP and DOWN
        up_score = 0
        down_score = 0
        total_weight = 0
        
        for model_name, signal_data in signals.items():
            weight = self.model_weights.get(model_name, 0)
            confidence = signal_data.get('confidence', 0.5)
            signal = signal_data.get('signal', 'NEUTRAL')
            
            if signal == 'UP' or signal == 'FOLLOW_TREND':
                up_score += weight * confidence
            elif signal == 'DOWN':
                down_score += weight * confidence
            # NEUTRAL or other signals don't add to either
            
            total_weight += weight
        
        # Normalize
        if total_weight > 0:
            up_score /= total_weight
            down_score /= total_weight
        
        # Decision threshold
        threshold = 0.6  # Need 60%+ confidence
        
        if up_score > threshold and up_score > down_score:
            return {
                'action': 'BUY',
                'confidence': up_score,
                'reasoning': 'Multi-model consensus: BUY',
                'scores': {'up': up_score, 'down': down_score}
            }
        elif down_score > threshold and down_score > up_score:
            return {
                'action': 'SELL',
                'confidence': down_score,
                'reasoning': 'Multi-model consensus: SELL',
                'scores': {'up': up_score, 'down': down_score}
            }
        
        return None  # No clear signal
    
    def update_performance(self, decision_id: int, actual_outcome: float):
        """
        Update model performance for adaptive weighting
        
        Args:
            decision_id: Index in decision_history
            actual_outcome: Actual price change (positive = up, negative = down)
        """
        if decision_id >= len(self.decision_history):
            return
        
        decision_record = self.decision_history[decision_id]
        predicted_direction = decision_record['decision']['action']
        
        # Check if prediction was correct
        correct = (
            (predicted_direction == 'BUY' and actual_outcome > 0) or
            (predicted_direction == 'SELL' and actual_outcome < 0)
        )
        
        # Update each model's performance
        analysis = decision_record['decision'].get('analysis', {})
        for model_name in self.model_performance.keys():
            if model_name in analysis:
                self.model_performance[model_name]['total'] += 1
                if correct:
                    self.model_performance[model_name]['correct'] += 1
        
        # Adapt weights based on performance
        self._adapt_weights()
    
    def _adapt_weights(self):
        """Adapt model weights based on performance"""
        # Calculate accuracy for each model
        accuracies = {}
        for model_name, perf in self.model_performance.items():
            if perf['total'] > 10:  # Need minimum samples
                accuracy = perf['correct'] / perf['total']
                accuracies[model_name] = accuracy
        
        if not accuracies:
            return
        
        # Adjust weights proportionally to accuracy
        total_accuracy = sum(accuracies.values())
        if total_accuracy > 0:
            for model_name, accuracy in accuracies.items():
                # Gradually adjust (don't change too fast)
                target_weight = accuracy / total_accuracy
                current_weight = self.model_weights.get(model_name, 0.2)
                new_weight = current_weight * 0.9 + target_weight * 0.1
                self.model_weights[model_name] = new_weight
            
            # Normalize
            total_weight = sum(self.model_weights.values())
            for key in self.model_weights:
                self.model_weights[key] /= total_weight
            
            logger.info(f"Adapted model weights: {self.model_weights}")


# Global instance
advanced_brain = AdvancedBrain()
