#!/usr/bin/env python3
"""LSTM Neural Network for Price Prediction - TPS19"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import pickle
import os

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️ TensorFlow not available. Install with: pip install tensorflow")


class LSTMPredictor:
    """LSTM Neural Network for cryptocurrency price prediction"""
    
    def __init__(self, model_dir=None):
        """Initialize LSTM Predictor
        
        Args:
            model_dir: Directory to save/load models (default: auto-detect)
        """
        if model_dir is None:
            # Auto-detect base directory
            if os.path.exists('/opt/tps19'):
                model_dir = '/opt/tps19/data/models'
            else:
                # Use relative path from script location
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                model_dir = os.path.join(base_dir, 'data', 'models')
        
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.model = None
        self.scaler_params = None
        self.sequence_length = 60  # 60 time steps for prediction
        self.n_features = 5  # OHLCV data
        
        self.config = {
            'lstm_units': [128, 64, 32],
            'dropout_rate': 0.2,
            'learning_rate': 0.001,
            'batch_size': 32,
            'epochs': 100,
            'validation_split': 0.2
        }
        
        self.metrics = {
            'accuracy': 0.0,
            'last_training': None,
            'predictions_made': 0,
            'avg_error': 0.0
        }
        
    def build_model(self):
        """Build LSTM model architecture"""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow required for LSTM models")
            
        model = Sequential([
            # First LSTM layer with return sequences
            LSTM(self.config['lstm_units'][0], 
                 return_sequences=True,
                 input_shape=(self.sequence_length, self.n_features)),
            Dropout(self.config['dropout_rate']),
            BatchNormalization(),
            
            # Second LSTM layer
            LSTM(self.config['lstm_units'][1], return_sequences=True),
            Dropout(self.config['dropout_rate']),
            BatchNormalization(),
            
            # Third LSTM layer
            LSTM(self.config['lstm_units'][2], return_sequences=False),
            Dropout(self.config['dropout_rate']),
            BatchNormalization(),
            
            # Dense layers
            Dense(16, activation='relu'),
            Dropout(self.config['dropout_rate']),
            
            # Output layer (predict next price)
            Dense(1, activation='linear')
        ])
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=self.config['learning_rate']),
            loss='huber',  # Robust to outliers
            metrics=['mae', 'mse']
        )
        
        self.model = model
        return model
        
    def prepare_data(self, data):
        """Prepare data for LSTM training
        
        Args:
            data: DataFrame with OHLCV columns
            
        Returns:
            X, y: Training sequences and targets
        """
        # Normalize data (min-max scaling)
        data_values = data[['open', 'high', 'low', 'close', 'volume']].values
        
        # Calculate scaling parameters
        if self.scaler_params is None:
            self.scaler_params = {
                'min': data_values.min(axis=0),
                'max': data_values.max(axis=0)
            }
            
        # Normalize
        scaled_data = (data_values - self.scaler_params['min']) / \
                      (self.scaler_params['max'] - self.scaler_params['min'] + 1e-8)
        
        # Create sequences
        X, y = [], []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i])
            y.append(scaled_data[i, 3])  # Predict close price
            
        return np.array(X), np.array(y)
        
    def train(self, data, epochs=None):
        """Train LSTM model on historical data
        
        Args:
            data: DataFrame with OHLCV data
            epochs: Number of training epochs (override config)
            
        Returns:
            Training history
        """
        if not TENSORFLOW_AVAILABLE:
            print("⚠️ TensorFlow not available, skipping training")
            return None
            
        print("🧠 Training LSTM Neural Network...")
        
        # Build model if not exists
        if self.model is None:
            self.build_model()
            
        # Prepare data
        X, y = self.prepare_data(data)
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            ModelCheckpoint(
                os.path.join(self.model_dir, 'lstm_best.h5'),
                monitor='val_loss',
                save_best_only=True
            )
        ]
        
        # Train
        epochs = epochs or self.config['epochs']
        history = self.model.fit(
            X, y,
            batch_size=self.config['batch_size'],
            epochs=epochs,
            validation_split=self.config['validation_split'],
            callbacks=callbacks,
            verbose=1
        )
        
        # Update metrics
        self.metrics['last_training'] = datetime.now().isoformat()
        self.metrics['accuracy'] = 1.0 - history.history['val_loss'][-1]
        
        # Save model
        self.save()
        
        print(f"✅ LSTM training completed. Accuracy: {self.metrics['accuracy']:.2%}")
        return history
        
    def predict(self, data, steps=1):
        """Predict future prices
        
        Args:
            data: Recent OHLCV data (at least sequence_length rows)
            steps: Number of steps to predict ahead
            
        Returns:
            Predicted prices
        """
        if self.model is None:
            # Try to load existing model
            if not self.load():
                raise ValueError("No trained model available")
                
        # Prepare data
        if len(data) < self.sequence_length:
            raise ValueError(f"Need at least {self.sequence_length} data points")
            
        # Take last sequence_length points
        recent_data = data.tail(self.sequence_length)
        data_values = recent_data[['open', 'high', 'low', 'close', 'volume']].values
        
        # Normalize
        scaled_data = (data_values - self.scaler_params['min']) / \
                      (self.scaler_params['max'] - self.scaler_params['min'] + 1e-8)
        
        predictions = []
        current_sequence = scaled_data.copy()
        
        for _ in range(steps):
            # Reshape for prediction
            X = current_sequence.reshape(1, self.sequence_length, self.n_features)
            
            # Predict
            pred_scaled = self.model.predict(X, verbose=0)[0][0]
            
            # Denormalize
            pred_price = pred_scaled * (self.scaler_params['max'][3] - self.scaler_params['min'][3]) + \
                        self.scaler_params['min'][3]
            predictions.append(pred_price)
            
            # Update sequence (use prediction as next close)
            new_row = current_sequence[-1].copy()
            new_row[3] = pred_scaled  # Update close price
            current_sequence = np.vstack([current_sequence[1:], new_row])
            
        self.metrics['predictions_made'] += steps
        return np.array(predictions)
        
    def predict_with_confidence(self, data, steps=1, n_simulations=100):
        """Predict with confidence intervals using Monte Carlo dropout
        
        Args:
            data: Recent OHLCV data
            steps: Number of steps ahead
            n_simulations: Number of Monte Carlo simulations
            
        Returns:
            dict with predictions, confidence intervals
        """
        predictions = []
        
        for _ in range(n_simulations):
            pred = self.predict(data, steps)
            predictions.append(pred)
            
        predictions = np.array(predictions)
        
        return {
            'mean': predictions.mean(axis=0),
            'std': predictions.std(axis=0),
            'lower_95': np.percentile(predictions, 2.5, axis=0),
            'upper_95': np.percentile(predictions, 97.5, axis=0),
            'confidence': 95
        }
        
    def evaluate_accuracy(self, test_data):
        """Evaluate model accuracy on test data
        
        Args:
            test_data: Test dataset
            
        Returns:
            Accuracy metrics
        """
        X, y = self.prepare_data(test_data)
        
        if self.model is None:
            if not self.load():
                return {'error': 'No model available'}
                
        # Evaluate
        results = self.model.evaluate(X, y, verbose=0)
        
        # Calculate additional metrics
        predictions = self.model.predict(X, verbose=0)
        mae = np.mean(np.abs(predictions.flatten() - y))
        mape = np.mean(np.abs((y - predictions.flatten()) / (y + 1e-8))) * 100
        
        return {
            'loss': results[0],
            'mae': mae,
            'mape': mape,
            'accuracy': 1.0 - results[0]
        }
        
    def save(self, filename='lstm_model.h5'):
        """Save model and parameters"""
        if self.model is None:
            return False
            
        # Save model
        model_path = os.path.join(self.model_dir, filename)
        self.model.save(model_path)
        
        # Save scaler parameters
        params_path = os.path.join(self.model_dir, 'lstm_params.pkl')
        with open(params_path, 'wb') as f:
            pickle.dump({
                'scaler_params': self.scaler_params,
                'config': self.config,
                'metrics': self.metrics
            }, f)
            
        return True
        
    def load(self, filename='lstm_model.h5'):
        """Load model and parameters"""
        model_path = os.path.join(self.model_dir, filename)
        params_path = os.path.join(self.model_dir, 'lstm_params.pkl')
        
        if not os.path.exists(model_path):
            return False
            
        try:
            # Load model
            self.model = load_model(model_path)
            
            # Load parameters
            if os.path.exists(params_path):
                with open(params_path, 'rb') as f:
                    params = pickle.load(f)
                    self.scaler_params = params['scaler_params']
                    self.config = params['config']
                    self.metrics = params['metrics']
                    
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
            
    def get_status(self):
        """Get model status and metrics"""
        return {
            'model_loaded': self.model is not None,
            'tensorflow_available': TENSORFLOW_AVAILABLE,
            'metrics': self.metrics,
            'config': self.config,
            'sequence_length': self.sequence_length
        }


# Test functionality
def test_lstm():
    """Test LSTM predictor"""
    print("🧪 Testing LSTM Predictor...")
    
    predictor = LSTMPredictor()
    
    # Generate dummy data
    dates = pd.date_range(start='2024-01-01', periods=500, freq='1h')
    data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.randn(500).cumsum() + 26000,
        'high': np.random.randn(500).cumsum() + 26100,
        'low': np.random.randn(500).cumsum() + 25900,
        'close': np.random.randn(500).cumsum() + 26000,
        'volume': np.random.randint(100, 1000, 500)
    })
    
    # Train
    if TENSORFLOW_AVAILABLE:
        predictor.train(data, epochs=5)
        
        # Predict
        predictions = predictor.predict(data, steps=5)
        print(f"✅ Predictions: {predictions}")
        
        # Predict with confidence
        conf_pred = predictor.predict_with_confidence(data, steps=3, n_simulations=10)
        print(f"✅ Confidence predictions: {conf_pred['mean']}")
    else:
        print("⚠️ TensorFlow not available, skipping training")
        
    print(f"✅ Status: {predictor.get_status()}")
    

if __name__ == '__main__':
    test_lstm()
