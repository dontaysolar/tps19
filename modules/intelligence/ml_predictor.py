#!/usr/bin/env python3
"""
Machine Learning Price Predictor - Enhanced AI
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import TimeSeriesSplit
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class MLPredictor:
    """
    Machine Learning price direction predictor
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.trained = False
        
        if HAS_SKLEARN:
            self._init_models()
        else:
            logger.warning("scikit-learn not installed, ML features disabled")
    
    def _init_models(self):
        """Initialize ML models"""
        # Random Forest - good for feature importance
        self.models['random_forest'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=20,
            random_state=42,
            n_jobs=-1
        )
        
        # Gradient Boosting - often best performance
        self.models['gradient_boost'] = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        # Ensemble weights
        self.ensemble_weights = {
            'random_forest': 0.4,
            'gradient_boost': 0.6
        }
    
    def train(self, historical_data: pd.DataFrame, horizon: int = 12):
        """
        Train models on historical data
        
        Args:
            historical_data: OHLCV DataFrame
            horizon: Prediction horizon in periods (default 12 = 1 hour for 5min bars)
        """
        if not HAS_SKLEARN:
            logger.warning("Cannot train: scikit-learn not installed")
            return
        
        logger.info(f"Training ML models on {len(historical_data)} candles...")
        
        # Create features
        features_df = self.create_features(historical_data)
        
        # Create target (1 if price up in next N periods, 0 otherwise)
        features_df['target'] = (
            historical_data['close'].shift(-horizon) > historical_data['close']
        ).astype(int)
        
        # Remove NaN
        features_df = features_df.dropna()
        
        if len(features_df) < 100:
            logger.warning("Not enough data for training")
            return
        
        # Split features and target
        feature_columns = [col for col in features_df.columns if col != 'target']
        X = features_df[feature_columns]
        y = features_df['target']
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['main'] = scaler
        self.feature_names = feature_columns
        
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=5)
        
        # Train each model
        for name, model in self.models.items():
            logger.info(f"Training {name}...")
            
            scores = []
            for train_idx, val_idx in tscv.split(X_scaled):
                X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                
                model.fit(X_train, y_train)
                score = model.score(X_val, y_val)
                scores.append(score)
            
            avg_score = np.mean(scores)
            logger.info(f"{name} average CV score: {avg_score:.4f}")
            
            # Final training on all data
            model.fit(X_scaled, y)
            
            # Feature importance
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = dict(zip(
                    feature_columns,
                    model.feature_importances_
                ))
        
        self.trained = True
        logger.info("✅ ML models trained successfully")
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create 50+ features for ML
        """
        features = pd.DataFrame(index=df.index)
        
        # ===== PRICE FEATURES =====
        # Returns at multiple timeframes
        for periods in [1, 3, 6, 12, 24, 48, 96]:
            features[f'return_{periods}p'] = df['close'].pct_change(periods)
        
        # Price position in recent range
        for window in [12, 24, 48, 96]:
            rolling_max = df['high'].rolling(window).max()
            rolling_min = df['low'].rolling(window).min()
            features[f'price_position_{window}p'] = (
                (df['close'] - rolling_min) / (rolling_max - rolling_min + 1e-10)
            )
        
        # ===== VOLATILITY FEATURES =====
        for window in [12, 24, 48]:
            # Historical volatility
            features[f'volatility_{window}p'] = (
                df['close'].pct_change().rolling(window).std()
            )
            
            # ATR (Average True Range)
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            features[f'atr_{window}p'] = true_range.rolling(window).mean()
        
        # Volatility trend
        vol_short = df['close'].pct_change().rolling(12).std()
        vol_long = df['close'].pct_change().rolling(48).std()
        features['volatility_trend'] = vol_short / (vol_long + 1e-10)
        
        # ===== VOLUME FEATURES =====
        # Volume trend
        features['volume_ma_ratio'] = df['volume'] / df['volume'].rolling(48).mean()
        
        # Volume momentum
        for window in [12, 24]:
            features[f'volume_momentum_{window}p'] = (
                df['volume'].rolling(window).mean() / 
                df['volume'].rolling(window*2).mean()
            )
        
        # Price-volume correlation
        for window in [24, 48]:
            features[f'price_volume_corr_{window}p'] = (
                df['close'].rolling(window).corr(df['volume'])
            )
        
        # ===== TECHNICAL INDICATORS =====
        # Moving averages
        for period in [10, 20, 50]:
            ma = df['close'].rolling(period).mean()
            features[f'ma_{period}'] = df['close'] / (ma + 1e-10) - 1
        
        # MA crossovers
        ma_fast = df['close'].rolling(10).mean()
        ma_slow = df['close'].rolling(50).mean()
        features['ma_crossover'] = (ma_fast > ma_slow).astype(int)
        
        # RSI (Relative Strength Index)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-10)
        features['rsi'] = 100 - (100 / (1 + rs))
        features['rsi_oversold'] = (features['rsi'] < 30).astype(int)
        features['rsi_overbought'] = (features['rsi'] > 70).astype(int)
        
        # MACD
        ema_fast = df['close'].ewm(span=12).mean()
        ema_slow = df['close'].ewm(span=26).mean()
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=9).mean()
        features['macd'] = macd / (df['close'] + 1e-10)
        features['macd_signal'] = signal / (df['close'] + 1e-10)
        features['macd_histogram'] = (macd - signal) / (df['close'] + 1e-10)
        
        # Bollinger Bands
        bb_ma = df['close'].rolling(20).mean()
        bb_std = df['close'].rolling(20).std()
        bb_upper = bb_ma + (2 * bb_std)
        bb_lower = bb_ma - (2 * bb_std)
        features['bb_position'] = (df['close'] - bb_lower) / (bb_upper - bb_lower + 1e-10)
        features['bb_width'] = (bb_upper - bb_lower) / (bb_ma + 1e-10)
        
        # ===== MOMENTUM FEATURES =====
        # Rate of change
        for periods in [12, 24, 48]:
            features[f'roc_{periods}p'] = (
                (df['close'] - df['close'].shift(periods)) / 
                (df['close'].shift(periods) + 1e-10)
            )
        
        # Consecutive gains/losses
        returns = df['close'].pct_change()
        features['consecutive_gains'] = (
            returns.gt(0).astype(int).groupby(
                (returns.le(0)).cumsum()
            ).cumsum()
        )
        features['consecutive_losses'] = (
            returns.lt(0).astype(int).groupby(
                (returns.ge(0)).cumsum()
            ).cumsum()
        )
        
        # ===== TIME FEATURES =====
        features['hour'] = df.index.hour
        features['day_of_week'] = df.index.dayofweek
        features['is_weekend'] = (df.index.dayofweek >= 5).astype(int)
        features['is_market_hours'] = (
            (df.index.hour >= 8) & (df.index.hour <= 18)
        ).astype(int)
        
        # ===== CANDLE PATTERNS =====
        # Candle body size
        features['candle_body'] = np.abs(df['close'] - df['open']) / (df['open'] + 1e-10)
        
        # Upper/lower wicks
        features['upper_wick'] = (df['high'] - df[['close', 'open']].max(axis=1)) / (df['high'] + 1e-10)
        features['lower_wick'] = (df[['close', 'open']].min(axis=1) - df['low']) / (df['low'] + 1e-10)
        
        # Doji detection (small body)
        features['is_doji'] = (features['candle_body'] < 0.001).astype(int)
        
        return features
    
    def predict(self, current_data: pd.DataFrame) -> Dict:
        """
        Predict price direction and confidence
        
        Args:
            current_data: Recent OHLCV data
            
        Returns:
            Prediction dict with direction, confidence, probabilities
        """
        if not self.trained:
            return {
                'direction': 'NEUTRAL',
                'confidence': 0.5,
                'up_probability': 0.5,
                'down_probability': 0.5,
                'ready': False
            }
        
        # Create features for latest data point
        features_df = self.create_features(current_data)
        
        # Get last row
        X = features_df[self.feature_names].iloc[-1:]]
        
        # Scale
        X_scaled = self.scalers['main'].transform(X)
        
        # Get predictions from each model
        predictions = {}
        for name, model in self.models.items():
            prob = model.predict_proba(X_scaled)[0]
            predictions[name] = {
                'down_prob': prob[0],
                'up_prob': prob[1]
            }
        
        # Ensemble prediction (weighted average)
        up_prob = sum(
            predictions[name]['up_prob'] * self.ensemble_weights[name]
            for name in self.models.keys()
        )
        down_prob = 1 - up_prob
        
        # Determine direction and confidence
        direction = 'UP' if up_prob > 0.5 else 'DOWN'
        confidence = max(up_prob, down_prob)
        
        return {
            'direction': direction,
            'confidence': confidence,
            'up_probability': up_prob,
            'down_probability': down_prob,
            'models': predictions,
            'ready': True
        }
    
    def get_feature_importance(self, top_n: int = 10) -> Dict:
        """Get most important features across models"""
        if not self.feature_importance:
            return {}
        
        # Average importance across models
        all_features = set()
        for importance_dict in self.feature_importance.values():
            all_features.update(importance_dict.keys())
        
        avg_importance = {}
        for feature in all_features:
            importances = [
                self.feature_importance[model].get(feature, 0)
                for model in self.feature_importance.keys()
            ]
            avg_importance[feature] = np.mean(importances)
        
        # Sort and get top N
        sorted_features = sorted(
            avg_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        return dict(sorted_features)


# Global instance
ml_predictor = MLPredictor()
