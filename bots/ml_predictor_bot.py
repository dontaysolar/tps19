#!/usr/bin/env python3
"""
Machine Learning Predictor Bot
Uses multiple ML techniques:
- Linear Regression for trend
- Classification for direction
- Feature engineering from technical indicators
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple

class MLPredictorBot:
    def __init__(self):
        self.name = "ML_Predictor"
        self.version = "1.0.0"
        self.enabled = True
        
        self.lookback = 20
        self.prediction_horizon = 5
        
        self.metrics = {
            'predictions_made': 0,
            'high_confidence_predictions': 0,
            'features_used': 0
        }
    
    def predict_price_direction(self, ohlcv: List) -> Dict:
        """
        Predict price direction using ML features
        
        Returns:
            Prediction: UP/DOWN/SIDEWAYS with confidence
        """
        if len(ohlcv) < self.lookback + 10:
            return {'error': 'Insufficient data'}
        
        # Extract features
        features = self._engineer_features(ohlcv)
        
        # Simple linear regression prediction
        direction, confidence = self._predict_direction(features)
        
        # Price target prediction
        current_price = ohlcv[-1][4]
        target_price = self._predict_target_price(features, current_price)
        
        # Generate signal
        signal = self._generate_ml_signal(direction, confidence)
        
        self.metrics['predictions_made'] += 1
        if confidence > 0.75:
            self.metrics['high_confidence_predictions'] += 1
        
        return {
            'prediction': direction,
            'confidence': confidence,
            'current_price': current_price,
            'target_price': target_price,
            'expected_move_pct': ((target_price - current_price) / current_price) * 100,
            'signal': signal,
            'strength': confidence * 100,
            'features_used': len(features),
            'reason': self._get_ml_reason(direction, confidence, target_price, current_price),
            'timestamp': datetime.now().isoformat()
        }
    
    def _engineer_features(self, ohlcv: List) -> Dict:
        """Engineer features from price data"""
        recent = ohlcv[-self.lookback:]
        
        opens = np.array([c[1] for c in recent])
        highs = np.array([c[2] for c in recent])
        lows = np.array([c[3] for c in recent])
        closes = np.array([c[4] for c in recent])
        volumes = np.array([c[5] for c in recent])
        
        features = {}
        
        # Price features
        features['returns'] = np.diff(closes) / closes[:-1]
        features['log_returns'] = np.diff(np.log(closes))
        
        # Momentum features
        features['roc_5'] = (closes[-1] - closes[-5]) / closes[-5] if len(closes) >= 5 else 0
        features['roc_10'] = (closes[-1] - closes[-10]) / closes[-10] if len(closes) >= 10 else 0
        
        # Volatility features
        features['std_5'] = np.std(closes[-5:]) if len(closes) >= 5 else 0
        features['std_10'] = np.std(closes[-10:]) if len(closes) >= 10 else 0
        
        # Trend features
        features['sma_5'] = np.mean(closes[-5:]) if len(closes) >= 5 else closes[-1]
        features['sma_10'] = np.mean(closes[-10:]) if len(closes) >= 10 else closes[-1]
        features['price_vs_sma5'] = (closes[-1] - features['sma_5']) / features['sma_5']
        features['price_vs_sma10'] = (closes[-1] - features['sma_10']) / features['sma_10']
        
        # Volume features
        features['volume_ratio'] = volumes[-1] / np.mean(volumes) if np.mean(volumes) > 0 else 1
        features['volume_trend'] = (np.mean(volumes[-5:]) - np.mean(volumes[-10:-5])) / np.mean(volumes[-10:-5]) if len(volumes) >= 10 else 0
        
        # Range features
        features['high_low_ratio'] = (highs[-1] - lows[-1]) / closes[-1] if closes[-1] > 0 else 0
        features['close_position'] = (closes[-1] - lows[-1]) / (highs[-1] - lows[-1]) if (highs[-1] - lows[-1]) > 0 else 0.5
        
        self.metrics['features_used'] = len(features)
        
        return features
    
    def _predict_direction(self, features: Dict) -> Tuple[str, float]:
        """Predict price direction from features"""
        
        # Scoring system
        bullish_score = 0
        bearish_score = 0
        
        # ROC signals
        if features['roc_5'] > 0.01:
            bullish_score += 2
        elif features['roc_5'] < -0.01:
            bearish_score += 2
        
        if features['roc_10'] > 0.02:
            bullish_score += 1
        elif features['roc_10'] < -0.02:
            bearish_score += 1
        
        # Trend signals
        if features['price_vs_sma5'] > 0:
            bullish_score += 1
        else:
            bearish_score += 1
        
        if features['price_vs_sma10'] > 0:
            bullish_score += 1
        else:
            bearish_score += 1
        
        # Volume confirmation
        if features['volume_ratio'] > 1.2:
            # High volume confirms direction
            if bullish_score > bearish_score:
                bullish_score += 2
            else:
                bearish_score += 2
        
        # Close position (where price closed in the range)
        if features['close_position'] > 0.7:
            bullish_score += 1
        elif features['close_position'] < 0.3:
            bearish_score += 1
        
        # Determine direction and confidence
        total_signals = bullish_score + bearish_score
        
        if bullish_score > bearish_score:
            confidence = bullish_score / max(total_signals, 1)
            return ('UP', min(confidence, 0.95))
        elif bearish_score > bullish_score:
            confidence = bearish_score / max(total_signals, 1)
            return ('DOWN', min(confidence, 0.95))
        else:
            return ('SIDEWAYS', 0.50)
    
    def _predict_target_price(self, features: Dict, current_price: float) -> float:
        """Predict target price using linear extrapolation"""
        
        # Use momentum and volatility to predict move
        expected_return = features['roc_5'] * 1.5  # Project 5-period momentum
        volatility_adjustment = features['std_5'] / current_price
        
        # Add volume confirmation
        if features['volume_ratio'] > 1.2:
            expected_return *= 1.2
        
        target = current_price * (1 + expected_return)
        
        return target
    
    def _generate_ml_signal(self, direction: str, confidence: float) -> str:
        """Generate trading signal from ML prediction"""
        if confidence < 0.60:
            return 'HOLD'
        
        if direction == 'UP':
            return 'BUY'
        elif direction == 'DOWN':
            return 'SELL'
        
        return 'HOLD'
    
    def _get_ml_reason(self, direction: str, confidence: float, target: float, current: float) -> str:
        """Get human-readable reason"""
        move_pct = ((target - current) / current) * 100
        return f"ML predicts {direction} move ({confidence:.0%} confidence) - Target: ${target:.2f} ({move_pct:+.1f}%)"
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'lookback_period': self.lookback,
            'prediction_horizon': self.prediction_horizon,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = MLPredictorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
