#!/usr/bin/env python3
"""
Deep Learning Module - Neural network for advanced prediction
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    tf = None

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class DeepLearningPredictor:
    """
    LSTM-based deep learning for price prediction
    """
    
    def __init__(self):
        self.model = None
        self.sequence_length = 60  # Use 60 time periods for prediction
        self.trained = False
        self.scaler = None
        
        if HAS_TENSORFLOW:
            self._build_model()
        else:
            logger.warning("TensorFlow not installed, deep learning disabled")
    
    def _build_model(self):
        """Build LSTM neural network"""
        if not HAS_TENSORFLOW:
            return
        
        # LSTM model for time series prediction
        self.model = models.Sequential([
            # First LSTM layer
            layers.LSTM(128, return_sequences=True, input_shape=(self.sequence_length, 5)),
            layers.Dropout(0.2),
            
            # Second LSTM layer
            layers.LSTM(64, return_sequences=True),
            layers.Dropout(0.2),
            
            # Third LSTM layer
            layers.LSTM(32, return_sequences=False),
            layers.Dropout(0.2),
            
            # Dense layers
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            
            # Output layer (3 classes: DOWN, NEUTRAL, UP)
            layers.Dense(3, activation='softmax')
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info("🧠 LSTM model built - Ready for training")
    
    def prepare_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare sequential data for LSTM
        
        Args:
            data: OHLCV data array (N, 5)
            
        Returns:
            X, y arrays for training
        """
        X, y = [], []
        
        for i in range(self.sequence_length, len(data) - 1):
            # Input sequence
            X.append(data[i - self.sequence_length:i])
            
            # Target (price direction in next period)
            next_close = data[i + 1, 3]  # Next close price
            current_close = data[i, 3]
            
            # Classify: 0=down, 1=neutral, 2=up
            change_pct = (next_close - current_close) / current_close
            if change_pct < -0.002:  # -0.2% = down
                y.append([1, 0, 0])
            elif change_pct > 0.002:  # +0.2% = up
                y.append([0, 0, 1])
            else:  # neutral
                y.append([0, 1, 0])
        
        return np.array(X), np.array(y)
    
    def train(self, historical_data: np.ndarray, epochs: int = 50, 
             batch_size: int = 32):
        """
        Train LSTM model
        
        Args:
            historical_data: OHLCV numpy array (N, 5)
            epochs: Training epochs
            batch_size: Batch size
        """
        if not HAS_TENSORFLOW:
            logger.warning("Cannot train: TensorFlow not installed")
            return
        
        logger.info(f"Training LSTM on {len(historical_data)} candles...")
        
        # Normalize data
        from sklearn.preprocessing import MinMaxScaler
        self.scaler = MinMaxScaler()
        normalized_data = self.scaler.fit_transform(historical_data)
        
        # Prepare sequences
        X, y = self.prepare_sequences(normalized_data)
        
        if len(X) < 100:
            logger.warning("Insufficient data for training")
            return
        
        # Split train/validation
        split = int(len(X) * 0.8)
        X_train, X_val = X[:split], X[split:]
        y_train, y_val = y[:split], y[split:]
        
        # Train
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=0,
            callbacks=[
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True
                )
            ]
        )
        
        # Evaluate
        val_loss, val_accuracy = self.model.evaluate(X_val, y_val, verbose=0)
        
        logger.info(f"✅ LSTM trained - Validation accuracy: {val_accuracy:.4f}")
        self.trained = True
    
    def predict(self, recent_data: np.ndarray) -> Dict:
        """
        Predict price direction
        
        Args:
            recent_data: Recent OHLCV data (at least sequence_length rows)
            
        Returns:
            Prediction dict
        """
        if not HAS_TENSORFLOW or not self.trained:
            return {
                'direction': 'NEUTRAL',
                'confidence': 0.5,
                'probabilities': {'down': 0.33, 'neutral': 0.34, 'up': 0.33},
                'ready': False
            }
        
        # Normalize
        if self.scaler is None:
            return {'direction': 'NEUTRAL', 'confidence': 0.5, 'ready': False}
        
        normalized = self.scaler.transform(recent_data[-self.sequence_length:])
        
        # Reshape for LSTM
        X = normalized.reshape(1, self.sequence_length, 5)
        
        # Predict
        prediction = self.model.predict(X, verbose=0)[0]
        
        # Extract probabilities
        down_prob, neutral_prob, up_prob = prediction
        
        # Determine direction
        if up_prob > down_prob and up_prob > neutral_prob:
            direction = 'UP'
            confidence = float(up_prob)
        elif down_prob > up_prob and down_prob > neutral_prob:
            direction = 'DOWN'
            confidence = float(down_prob)
        else:
            direction = 'NEUTRAL'
            confidence = float(neutral_prob)
        
        return {
            'direction': direction,
            'confidence': confidence,
            'probabilities': {
                'down': float(down_prob),
                'neutral': float(neutral_prob),
                'up': float(up_prob)
            },
            'ready': True,
            'model': 'LSTM'
        }
    
    def save_model(self, path: str = 'models/lstm_predictor.h5'):
        """Save trained model"""
        if self.model and self.trained:
            self.model.save(path)
            logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str = 'models/lstm_predictor.h5'):
        """Load pre-trained model"""
        if not HAS_TENSORFLOW:
            return
        
        try:
            self.model = keras.models.load_model(path)
            self.trained = True
            logger.info(f"Model loaded from {path}")
        except Exception as e:
            logger.error(f"Model load error: {e}")


# Global instance
deep_learning_predictor = DeepLearningPredictor()
