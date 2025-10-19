#!/usr/bin/env python3
"""
Ensemble Learning Bot
Combines predictions from multiple ML models
Uses voting, stacking, and blending techniques
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class EnsembleLearningBot:
    def __init__(self):
        self.name = "Ensemble_Learning"
        self.version = "1.0.0"
        self.enabled = True
        
        # Ensemble configuration
        self.ensemble_method = 'weighted_voting'  # weighted_voting, stacking, blending
        self.model_weights = {}
        
        # Model predictions storage
        self.model_predictions = {}
        
        self.is_trained = False
        
        self.metrics = {
            'ensemble_predictions': 0,
            'models_in_ensemble': 0,
            'ensemble_accuracy': 0.0,
            'individual_accuracies': {}
        }
    
    def register_model(self, model_name: str, weight: float = 1.0):
        """Register a model in the ensemble"""
        self.model_weights[model_name] = weight
        self.metrics['models_in_ensemble'] += 1
    
    def weighted_voting(self, predictions: Dict[str, Dict]) -> Dict:
        """
        Combine predictions using weighted voting
        
        Args:
            predictions: Dict of {model_name: {signal, confidence}}
        """
        if not predictions:
            return {'signal': 'HOLD', 'confidence': 0.0}
        
        # Convert signals to numerical votes
        vote_values = {'BUY': 1, 'SELL': -1, 'HOLD': 0}
        
        weighted_sum = 0
        total_weight = 0
        confidence_sum = 0
        
        for model_name, pred in predictions.items():
            weight = self.model_weights.get(model_name, 1.0)
            signal = pred.get('signal', 'HOLD')
            confidence = pred.get('confidence', 0.5)
            
            vote = vote_values.get(signal, 0)
            weighted_sum += vote * weight * confidence
            total_weight += weight
            confidence_sum += confidence * weight
        
        # Determine ensemble signal
        if total_weight > 0:
            ensemble_vote = weighted_sum / total_weight
            ensemble_confidence = confidence_sum / total_weight
        else:
            ensemble_vote = 0
            ensemble_confidence = 0.5
        
        # Convert back to signal
        if ensemble_vote > 0.2:
            signal = 'BUY'
        elif ensemble_vote < -0.2:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        return {
            'signal': signal,
            'confidence': min(0.95, ensemble_confidence),
            'ensemble_vote': float(ensemble_vote),
            'models_agreed': len(predictions)
        }
    
    def stacking(self, predictions: Dict[str, Dict], ohlcv: List) -> Dict:
        """
        Stacking: Use meta-learner on model predictions
        """
        # Extract predictions as features
        features = []
        
        for model_name, pred in predictions.items():
            signal_encoding = {'BUY': 1, 'SELL': -1, 'HOLD': 0}
            features.append(signal_encoding.get(pred.get('signal', 'HOLD'), 0))
            features.append(pred.get('confidence', 0.5))
        
        if not features:
            return {'signal': 'HOLD', 'confidence': 0.0}
        
        features = np.array(features)
        
        # Simple meta-learner: weighted average with learned weights
        # In production, this would be a trained model
        meta_prediction = np.mean(features[::2])  # Average signal encodings
        meta_confidence = np.mean(features[1::2])  # Average confidences
        
        if meta_prediction > 0.3:
            signal = 'BUY'
        elif meta_prediction < -0.3:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        return {
            'signal': signal,
            'confidence': min(0.90, meta_confidence),
            'meta_prediction': float(meta_prediction)
        }
    
    def blending(self, predictions: Dict[str, Dict]) -> Dict:
        """
        Blending: Combine predictions with holdout-based weights
        """
        if not predictions:
            return {'signal': 'HOLD', 'confidence': 0.0}
        
        # Use model accuracies as blend weights
        total_accuracy = sum(self.metrics['individual_accuracies'].get(name, 0.5) 
                           for name in predictions.keys())
        
        if total_accuracy == 0:
            return self.weighted_voting(predictions)
        
        vote_sum = 0
        confidence_sum = 0
        
        for model_name, pred in predictions.items():
            accuracy = self.metrics['individual_accuracies'].get(model_name, 0.5)
            weight = accuracy / total_accuracy
            
            signal_value = {'BUY': 1, 'SELL': -1, 'HOLD': 0}.get(pred.get('signal', 'HOLD'), 0)
            vote_sum += signal_value * weight
            confidence_sum += pred.get('confidence', 0.5) * weight
        
        if vote_sum > 0.3:
            signal = 'BUY'
        elif vote_sum < -0.3:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        return {
            'signal': signal,
            'confidence': min(0.90, confidence_sum),
            'blend_score': float(vote_sum)
        }
    
    def ensemble_predict(self, model_predictions: Dict[str, Dict], ohlcv: List = None) -> Dict:
        """
        Make ensemble prediction from multiple models
        
        Args:
            model_predictions: {model_name: {signal, confidence, ...}}
            ohlcv: Optional market data for stacking
        """
        if not model_predictions:
            return {
                'error': 'No model predictions provided',
                'signal': 'HOLD',
                'confidence': 0.0
            }
        
        # Store predictions
        self.model_predictions = model_predictions
        
        # Apply ensemble method
        if self.ensemble_method == 'weighted_voting':
            result = self.weighted_voting(model_predictions)
        elif self.ensemble_method == 'stacking' and ohlcv:
            result = self.stacking(model_predictions, ohlcv)
        elif self.ensemble_method == 'blending':
            result = self.blending(model_predictions)
        else:
            result = self.weighted_voting(model_predictions)  # Default
        
        # Add diversity metrics
        signals = [p.get('signal', 'HOLD') for p in model_predictions.values()]
        unique_signals = len(set(signals))
        agreement = signals.count(result['signal']) / len(signals) if signals else 0
        
        # Adjust confidence based on agreement
        adjusted_confidence = result['confidence'] * (0.7 + 0.3 * agreement)
        
        self.metrics['ensemble_predictions'] += 1
        
        return {
            'signal': result['signal'],
            'confidence': min(0.95, adjusted_confidence),
            'ensemble_method': self.ensemble_method,
            'models_consulted': len(model_predictions),
            'model_agreement': agreement,
            'signal_diversity': unique_signals,
            'individual_signals': {name: pred.get('signal') for name, pred in model_predictions.items()},
            'reason': f"Ensemble of {len(model_predictions)} models using {self.ensemble_method}",
            'timestamp': datetime.now().isoformat()
        }
    
    def update_model_accuracy(self, model_name: str, accuracy: float):
        """Update tracked accuracy for a model"""
        self.metrics['individual_accuracies'][model_name] = accuracy
    
    def set_ensemble_method(self, method: str):
        """Change ensemble method"""
        valid_methods = ['weighted_voting', 'stacking', 'blending']
        if method in valid_methods:
            self.ensemble_method = method
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'ensemble_method': self.ensemble_method,
            'registered_models': list(self.model_weights.keys()),
            'model_weights': self.model_weights,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = EnsembleLearningBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
    
    # Example usage
    bot.register_model('LSTM', weight=1.5)
    bot.register_model('RandomForest', weight=1.2)
    bot.register_model('XGBoost', weight=1.3)
    print(f"📊 Ensemble with {bot.metrics['models_in_ensemble']} models")
