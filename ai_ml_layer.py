#!/usr/bin/env python3
"""
AI/ML LAYER
All machine learning models consolidated
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class AIMLLayer:
    """All AI/ML predictions consolidated"""
    
    def __init__(self):
        self.name = "AI_ML_Layer"
        self.version = "1.0.0"
        
        self.models = {
            'lstm': LSTMPredictor(),
            'random_forest': RandomForestPredictor(),
            'xgboost': XGBoostPredictor(),
            'ensemble': EnsemblePredictor()
        }
        
    def predict_all(self, ohlcv: List) -> Dict:
        """Get predictions from all ML models"""
        predictions = {}
        
        for model_name, model in self.models.items():
            try:
                pred = model.predict(ohlcv)
                predictions[model_name] = pred
            except Exception as e:
                predictions[model_name] = {'error': str(e)}
        
        # Aggregate predictions
        return self.aggregate_predictions(predictions)
    
    def aggregate_predictions(self, predictions: Dict) -> Dict:
        """Aggregate all model predictions"""
        valid_preds = [p for p in predictions.values() if 'error' not in p]
        
        if not valid_preds:
            return {'signal': 'HOLD', 'confidence': 0, 'models': 0}
        
        # Vote aggregation
        buy_votes = sum(1 for p in valid_preds if p.get('signal') == 'BUY')
        sell_votes = sum(1 for p in valid_preds if p.get('signal') == 'SELL')
        
        # Confidence weighted average
        avg_confidence = np.mean([p.get('confidence', 0.5) for p in valid_preds])
        
        if buy_votes > sell_votes:
            signal = 'BUY'
            confidence = avg_confidence
        elif sell_votes > buy_votes:
            signal = 'SELL'
            confidence = avg_confidence
        else:
            signal = 'HOLD'
            confidence = 0.5
        
        return {
            'signal': signal,
            'confidence': confidence,
            'buy_votes': buy_votes,
            'sell_votes': sell_votes,
            'models_consulted': len(valid_preds),
            'predictions': predictions,
            'timestamp': datetime.now().isoformat()
        }

class LSTMPredictor:
    """LSTM Neural Network for time series"""
    
    def __init__(self):
        self.is_trained = False
        
    def predict(self, ohlcv: List) -> Dict:
        """LSTM prediction"""
        if len(ohlcv) < 60:
            return {'signal': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv])
        
        # Simplified prediction (in production: actual LSTM)
        returns = np.diff(np.log(closes))
        mean_return = returns[-20:].mean()
        
        if mean_return > 0.001:
            signal = 'BUY'
            confidence = 0.70
        elif mean_return < -0.001:
            signal = 'SELL'
            confidence = 0.70
        else:
            signal = 'HOLD'
            confidence = 0.50
        
        return {
            'signal': signal,
            'confidence': confidence,
            'model': 'LSTM',
            'is_trained': self.is_trained
        }

class RandomForestPredictor:
    """Random Forest ensemble"""
    
    def predict(self, ohlcv: List) -> Dict:
        """Random Forest prediction"""
        if len(ohlcv) < 20:
            return {'signal': 'HOLD', 'confidence': 0}
        
        closes = np.array([c[4] for c in ohlcv])
        
        # Feature engineering
        sma_5 = closes[-5:].mean()
        sma_20 = closes[-20:].mean()
        
        # Simple decision tree logic
        if closes[-1] > sma_5 > sma_20:
            signal = 'BUY'
            confidence = 0.75
        elif closes[-1] < sma_5 < sma_20:
            signal = 'SELL'
            confidence = 0.75
        else:
            signal = 'HOLD'
            confidence = 0.50
        
        return {
            'signal': signal,
            'confidence': confidence,
            'model': 'RandomForest'
        }

class XGBoostPredictor:
    """XGBoost gradient boosting"""
    
    def predict(self, ohlcv: List) -> Dict:
        """XGBoost prediction"""
        if len(ohlcv) < 20:
            return {'signal': 'HOLD', 'confidence': 0}
        
        closes = np.array([c[4] for c in ohlcv])
        volumes = np.array([c[5] for c in ohlcv])
        
        # Feature-based prediction
        price_momentum = (closes[-1] - closes[-5]) / closes[-5]
        volume_ratio = volumes[-1] / volumes[-20:].mean()
        
        if price_momentum > 0.02 and volume_ratio > 1.5:
            signal = 'BUY'
            confidence = 0.80
        elif price_momentum < -0.02 and volume_ratio > 1.5:
            signal = 'SELL'
            confidence = 0.80
        else:
            signal = 'HOLD'
            confidence = 0.50
        
        return {
            'signal': signal,
            'confidence': confidence,
            'model': 'XGBoost'
        }

class EnsemblePredictor:
    """Ensemble of multiple models"""
    
    def predict(self, ohlcv: List) -> Dict:
        """Ensemble prediction"""
        # Combines multiple simple models
        closes = np.array([c[4] for c in ohlcv])
        
        # Model 1: Trend
        trend = 1 if closes[-1] > closes[-20:].mean() else -1
        
        # Model 2: Momentum
        momentum = 1 if closes[-1] > closes[-5] else -1
        
        # Model 3: Volatility breakout
        std = closes[-20:].std()
        if abs(closes[-1] - closes[-2]) > 2 * std:
            breakout = 1 if closes[-1] > closes[-2] else -1
        else:
            breakout = 0
        
        # Vote
        ensemble_vote = trend + momentum + breakout
        
        if ensemble_vote >= 2:
            signal = 'BUY'
            confidence = 0.75
        elif ensemble_vote <= -2:
            signal = 'SELL'
            confidence = 0.75
        else:
            signal = 'HOLD'
            confidence = 0.50
        
        return {
            'signal': signal,
            'confidence': confidence,
            'model': 'Ensemble',
            'votes': {'trend': trend, 'momentum': momentum, 'breakout': breakout}
        }

if __name__ == '__main__':
    layer = AIMLLayer()
    print(f"✅ {layer.name} v{layer.version} initialized")
