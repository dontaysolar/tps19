#!/usr/bin/env python3
"""
Random Forest Ensemble Bot
Decision tree ensemble for robust predictions
Handles non-linear patterns and feature interactions
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class RandomForestBot:
    def __init__(self):
        self.name = "Random_Forest"
        self.version = "1.0.0"
        self.enabled = True
        
        self.n_estimators = 100  # Number of trees
        self.max_depth = 10
        self.min_samples_split = 5
        self.n_features_per_tree = 'sqrt'  # sqrt of total features
        
        self.trees = []
        self.feature_importances = {}
        self.is_trained = False
        
        self.metrics = {
            'predictions_made': 0,
            'trees_built': 0,
            'oob_score': 0.0,
            'feature_importance_calculated': 0
        }
    
    def extract_features(self, ohlcv: List) -> np.ndarray:
        """Extract comprehensive feature set"""
        if len(ohlcv) < 50:
            return None
        
        closes = np.array([c[4] for c in ohlcv])
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        volumes = np.array([c[5] for c in ohlcv])
        
        features = []
        feature_names = []
        
        for i in range(30, len(closes)):
            f = []
            
            # Price features
            f.append((closes[i] - closes[i-1]) / closes[i-1])  # Returns
            f.append((closes[i] - closes[i-5]) / closes[i-5])  # 5-period returns
            f.append((closes[i] - closes[i-10]) / closes[i-10])  # 10-period returns
            f.append((closes[i] - closes[i-20]) / closes[i-20])  # 20-period returns
            
            # Volatility features
            f.append(np.std(closes[i-20:i]) / np.mean(closes[i-20:i]))
            f.append(np.std(closes[i-10:i]) / np.mean(closes[i-10:i]))
            
            # Volume features
            f.append(volumes[i] / np.mean(volumes[i-20:i]))
            f.append((volumes[i] - volumes[i-1]) / volumes[i-1])
            
            # Trend features
            f.append((np.mean(closes[i-5:i]) - np.mean(closes[i-20:i-5])) / np.mean(closes[i-20:i]))
            
            # RSI
            gains = np.maximum(np.diff(closes[i-14:i]), 0)
            losses = np.abs(np.minimum(np.diff(closes[i-14:i]), 0))
            avg_gain = np.mean(gains)
            avg_loss = np.mean(losses) if np.mean(losses) > 0 else 0.001
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            f.append(rsi / 100)
            
            # MACD
            ema12 = np.mean(closes[i-12:i])
            ema26 = np.mean(closes[i-26:i])
            macd = (ema12 - ema26) / ema26
            f.append(macd)
            
            # Bollinger Bands
            sma20 = np.mean(closes[i-20:i])
            std20 = np.std(closes[i-20:i])
            bb_position = (closes[i] - sma20) / (2 * std20) if std20 > 0 else 0
            f.append(bb_position)
            
            # ATR
            tr = np.maximum(highs[i-14:i] - lows[i-14:i], 
                           np.abs(highs[i-14:i] - closes[i-15:i-1]))
            atr = np.mean(tr)
            f.append(atr / closes[i])
            
            # High-Low position
            f.append((closes[i] - lows[i]) / (highs[i] - lows[i]) if (highs[i] - lows[i]) > 0 else 0.5)
            
            # Momentum
            f.append((closes[i] - closes[i-14]) / closes[i-14])
            
            features.append(f)
        
        return np.array(features)
    
    def build_decision_tree(self, X, y, max_depth, min_samples):
        """Build a simple decision tree (simplified implementation)"""
        # Simplified tree: just store split threshold and feature
        if len(X) < min_samples or max_depth == 0:
            # Leaf node - return majority class
            return {'type': 'leaf', 'prediction': np.mean(y)}
        
        # Find best split (simplified - random feature selection)
        n_features = X.shape[1]
        best_feature = np.random.randint(0, n_features)
        best_threshold = np.median(X[:, best_feature])
        
        # Split data
        left_mask = X[:, best_feature] <= best_threshold
        right_mask = ~left_mask
        
        if np.sum(left_mask) == 0 or np.sum(right_mask) == 0:
            return {'type': 'leaf', 'prediction': np.mean(y)}
        
        # Recursively build children (limited depth for performance)
        return {
            'type': 'node',
            'feature': best_feature,
            'threshold': best_threshold,
            'left': self.build_decision_tree(X[left_mask], y[left_mask], max_depth-1, min_samples),
            'right': self.build_decision_tree(X[right_mask], y[right_mask], max_depth-1, min_samples)
        }
    
    def predict_tree(self, tree, x):
        """Predict using a single tree"""
        if tree['type'] == 'leaf':
            return tree['prediction']
        
        if x[tree['feature']] <= tree['threshold']:
            return self.predict_tree(tree['left'], x)
        else:
            return self.predict_tree(tree['right'], x)
    
    def train(self, ohlcv: List) -> Dict:
        """Train random forest on historical data"""
        features = self.extract_features(ohlcv)
        
        if features is None or len(features) < 100:
            return {'error': 'Insufficient data'}
        
        # Create labels (future price movement)
        closes = np.array([c[4] for c in ohlcv[30:]])
        labels = np.zeros(len(features))
        
        for i in range(len(features) - 1):
            labels[i] = 1 if closes[i+1] > closes[i] else -1
        
        labels = labels[:-1]
        features = features[:-1]
        
        # Build forest
        self.trees = []
        n_samples = len(features)
        
        for i in range(min(self.n_estimators, 20)):  # Limit for performance
            # Bootstrap sample
            indices = np.random.choice(n_samples, n_samples, replace=True)
            X_boot = features[indices]
            y_boot = labels[indices]
            
            # Build tree
            tree = self.build_decision_tree(X_boot, y_boot, self.max_depth, self.min_samples_split)
            self.trees.append(tree)
            
            self.metrics['trees_built'] += 1
        
        self.is_trained = True
        
        # Calculate OOB score (simplified)
        predictions = [self.predict_tree(tree, features[-1]) for tree in self.trees]
        oob_pred = np.mean(predictions)
        self.metrics['oob_score'] = float(abs(oob_pred))
        
        return {
            'trained': True,
            'n_trees': len(self.trees),
            'oob_score': self.metrics['oob_score'],
            'samples': len(features)
        }
    
    def predict(self, ohlcv: List) -> Dict:
        """Make prediction using random forest ensemble"""
        features = self.extract_features(ohlcv)
        
        if features is None:
            return {'error': 'Insufficient data'}
        
        if not self.is_trained or not self.trees:
            return {'error': 'Model not trained', 'confidence': 0.0, 'signal': 'HOLD'}
        
        # Get last feature vector
        last_features = features[-1]
        
        # Predict with all trees
        tree_predictions = [self.predict_tree(tree, last_features) for tree in self.trees]
        
        # Ensemble prediction
        ensemble_pred = np.mean(tree_predictions)
        ensemble_std = np.std(tree_predictions)
        
        # Agreement among trees
        agreement = 1 - (ensemble_std / (abs(ensemble_pred) + 1e-8))
        confidence = min(0.90, max(0.50, agreement))
        
        # Generate signal
        if ensemble_pred > 0.3:
            signal = 'BUY'
        elif ensemble_pred < -0.3:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        self.metrics['predictions_made'] += 1
        
        return {
            'signal': signal,
            'confidence': confidence,
            'ensemble_prediction': float(ensemble_pred),
            'tree_agreement': float(agreement),
            'n_trees_voted': len(tree_predictions),
            'reason': f"Random Forest ensemble: {len(self.trees)} trees predict {signal}",
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'is_trained': self.is_trained,
            'config': {
                'n_estimators': self.n_estimators,
                'max_depth': self.max_depth
            },
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = RandomForestBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
