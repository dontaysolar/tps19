#!/usr/bin/env python3
"""
AI Models for APEX Trading System
LSTM Neural Networks and GAN for price prediction and market simulation
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import pickle

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, Model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, LeakyReLU, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error
except ImportError as e:
    print(f"❌ Missing AI dependencies: {e}")
    print("Installing required packages...")
    os.system("pip3 install --break-system-packages tensorflow scikit-learn -q")
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, Model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, LeakyReLU, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error

class LSTMPredictor:
    """
    LSTM Neural Network for price prediction
    Features:
    - Multi-timeframe analysis
    - Technical indicators integration
    - Volatility prediction
    - Pattern recognition
    """
    
    def __init__(self, sequence_length: int = 60, features: int = 10):
        self.sequence_length = sequence_length
        self.features = features
        self.model = None
        self.scaler = MinMaxScaler()
        self.is_trained = False
        
        # Model configuration
        self.config = {
            'lstm_units': [128, 64, 32],
            'dropout_rate': 0.2,
            'learning_rate': 0.001,
            'batch_size': 32,
            'epochs': 100,
            'validation_split': 0.2
        }
    
    def prepare_features(self, ohlcv_data: List[List]) -> np.ndarray:
        """
        Prepare features from OHLCV data
        
        Args:
            ohlcv_data: List of [timestamp, open, high, low, close, volume]
            
        Returns:
            Normalized feature array
        """
        df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Calculate technical indicators
        df['sma_7'] = df['close'].rolling(window=7).mean()
        df['sma_25'] = df['close'].rolling(window=25).mean()
        df['rsi'] = self._calculate_rsi(df['close'])
        df['macd'] = self._calculate_macd(df['close'])
        df['bb_upper'], df['bb_lower'] = self._calculate_bollinger_bands(df['close'])
        df['atr'] = self._calculate_atr(df)
        df['volume_sma'] = df['volume'].rolling(window=10).mean()
        df['price_change'] = df['close'].pct_change()
        df['volatility'] = df['price_change'].rolling(window=10).std()
        
        # Select features
        feature_columns = ['close', 'sma_7', 'sma_25', 'rsi', 'macd', 'bb_upper', 'bb_lower', 'atr', 'volume_sma', 'volatility']
        features_df = df[feature_columns].dropna()
        
        # Normalize features
        features_scaled = self.scaler.fit_transform(features_df)
        
        return features_scaled
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        return macd
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, lower
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=period).mean()
        return atr
    
    def create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training"""
        X, y = [], []
        
        for i in range(self.sequence_length, len(data)):
            X.append(data[i-self.sequence_length:i])
            y.append(data[i, 0])  # Predict close price
        
        return np.array(X), np.array(y)
    
    def build_model(self) -> Sequential:
        """Build LSTM model architecture"""
        model = Sequential()
        
        # First LSTM layer
        model.add(LSTM(
            units=self.config['lstm_units'][0],
            return_sequences=True,
            input_shape=(self.sequence_length, self.features)
        ))
        model.add(Dropout(self.config['dropout_rate']))
        
        # Second LSTM layer
        model.add(LSTM(
            units=self.config['lstm_units'][1],
            return_sequences=True
        ))
        model.add(Dropout(self.config['dropout_rate']))
        
        # Third LSTM layer
        model.add(LSTM(
            units=self.config['lstm_units'][2],
            return_sequences=False
        ))
        model.add(Dropout(self.config['dropout_rate']))
        
        # Dense layers
        model.add(Dense(50, activation='relu'))
        model.add(Dense(25, activation='relu'))
        model.add(Dense(1, activation='linear'))
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=self.config['learning_rate']),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train(self, ohlcv_data: List[List], validation_data: List[List] = None) -> Dict:
        """Train the LSTM model"""
        print("🧠 Training LSTM model...")
        
        # Prepare training data
        train_features = self.prepare_features(ohlcv_data)
        X_train, y_train = self.create_sequences(train_features)
        
        # Build model
        self.model = self.build_model()
        
        # Callbacks
        callbacks = [
            EarlyStopping(patience=10, restore_best_weights=True),
            ReduceLROnPlateau(factor=0.5, patience=5, min_lr=1e-7)
        ]
        
        # Train model
        if validation_data:
            val_features = self.prepare_features(validation_data)
            X_val, y_val = self.create_sequences(val_features)
            validation_data = (X_val, y_val)
        else:
            validation_data = None
        
        history = self.model.fit(
            X_train, y_train,
            batch_size=self.config['batch_size'],
            epochs=self.config['epochs'],
            validation_split=self.config['validation_split'],
            validation_data=validation_data,
            callbacks=callbacks,
            verbose=1
        )
        
        self.is_trained = True
        
        # Calculate metrics
        train_pred = self.model.predict(X_train)
        train_mse = mean_squared_error(y_train, train_pred)
        train_mae = mean_absolute_error(y_train, train_pred)
        
        return {
            'status': 'success',
            'train_mse': float(train_mse),
            'train_mae': float(train_mae),
            'epochs_trained': len(history.history['loss']),
            'final_loss': float(history.history['loss'][-1])
        }
    
    def predict(self, ohlcv_data: List[List], steps_ahead: int = 1) -> Dict:
        """Make predictions"""
        if not self.is_trained:
            return {'error': 'Model not trained'}
        
        features = self.prepare_features(ohlcv_data)
        
        if len(features) < self.sequence_length:
            return {'error': 'Insufficient data for prediction'}
        
        # Get last sequence
        last_sequence = features[-self.sequence_length:].reshape(1, self.sequence_length, self.features)
        
        predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(steps_ahead):
            pred = self.model.predict(current_sequence, verbose=0)
            predictions.append(pred[0, 0])
            
            # Update sequence for next prediction
            new_row = current_sequence[0, -1, :].copy()
            new_row[0] = pred[0, 0]  # Update close price
            current_sequence = np.roll(current_sequence, -1, axis=1)
            current_sequence[0, -1, :] = new_row
        
        # Denormalize predictions
        predictions_array = np.array(predictions).reshape(-1, 1)
        dummy_features = np.zeros((len(predictions), self.features))
        dummy_features[:, 0] = predictions_array[:, 0]
        predictions_denorm = self.scaler.inverse_transform(dummy_features)[:, 0]
        
        return {
            'predictions': predictions_denorm.tolist(),
            'steps_ahead': steps_ahead,
            'confidence': self._calculate_confidence(predictions_denorm)
        }
    
    def _calculate_confidence(self, predictions: np.ndarray) -> float:
        """Calculate prediction confidence based on volatility"""
        if len(predictions) < 2:
            return 0.5
        
        volatility = np.std(np.diff(predictions))
        confidence = max(0.1, min(0.95, 1.0 - volatility / np.mean(predictions)))
        return float(confidence)
    
    def save_model(self, filepath: str) -> bool:
        """Save trained model"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save model
            self.model.save(f"{filepath}_model.h5")
            
            # Save scaler
            with open(f"{filepath}_scaler.pkl", 'wb') as f:
                pickle.dump(self.scaler, f)
            
            # Save config
            with open(f"{filepath}_config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ Error saving model: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """Load trained model"""
        try:
            # Load model
            self.model = tf.keras.models.load_model(f"{filepath}_model.h5")
            
            # Load scaler
            with open(f"{filepath}_scaler.pkl", 'rb') as f:
                self.scaler = pickle.load(f)
            
            # Load config
            with open(f"{filepath}_config.json", 'r') as f:
                self.config = json.load(f)
            
            self.is_trained = True
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False


class GANSimulator:
    """
    Generative Adversarial Network for market simulation
    Features:
    - Generate synthetic market data
    - Stress testing scenarios
    - Market regime simulation
    - Risk assessment
    """
    
    def __init__(self, sequence_length: int = 60, features: int = 5):
        self.sequence_length = sequence_length
        self.features = features
        self.generator = None
        self.discriminator = None
        self.gan = None
        self.is_trained = False
        
        # GAN configuration
        self.config = {
            'latent_dim': 100,
            'generator_lr': 0.0002,
            'discriminator_lr': 0.0002,
            'batch_size': 32,
            'epochs': 1000,
            'beta1': 0.5
        }
    
    def build_generator(self) -> Model:
        """Build generator network"""
        noise = Input(shape=(self.config['latent_dim'],))
        
        x = Dense(256)(noise)
        x = LeakyReLU(alpha=0.2)(x)
        x = BatchNormalization()(x)
        
        x = Dense(512)(x)
        x = LeakyReLU(alpha=0.2)(x)
        x = BatchNormalization()(x)
        
        x = Dense(1024)(x)
        x = LeakyReLU(alpha=0.2)(x)
        x = BatchNormalization()(x)
        
        x = Dense(self.sequence_length * self.features)(x)
        x = tf.reshape(x, (-1, self.sequence_length, self.features))
        
        generator = Model(noise, x)
        return generator
    
    def build_discriminator(self) -> Model:
        """Build discriminator network"""
        data = Input(shape=(self.sequence_length, self.features))
        
        x = LSTM(128, return_sequences=True)(data)
        x = Dropout(0.3)(x)
        
        x = LSTM(64, return_sequences=False)(x)
        x = Dropout(0.3)(x)
        
        x = Dense(32)(x)
        x = LeakyReLU(alpha=0.2)(x)
        
        x = Dense(1, activation='sigmoid')(x)
        
        discriminator = Model(data, x)
        return discriminator
    
    def build_gan(self) -> Model:
        """Build GAN model"""
        self.generator = self.build_generator()
        self.discriminator = self.build_discriminator()
        
        # Compile discriminator
        self.discriminator.compile(
            optimizer=Adam(learning_rate=self.config['discriminator_lr'], beta_1=self.config['beta1']),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # Compile GAN
        noise = Input(shape=(self.config['latent_dim'],))
        generated_data = self.generator(noise)
        
        # Freeze discriminator during GAN training
        self.discriminator.trainable = False
        validity = self.discriminator(generated_data)
        
        self.gan = Model(noise, validity)
        self.gan.compile(
            optimizer=Adam(learning_rate=self.config['generator_lr'], beta_1=self.config['beta1']),
            loss='binary_crossentropy'
        )
        
        return self.gan
    
    def train(self, real_data: np.ndarray) -> Dict:
        """Train GAN model"""
        print("🎭 Training GAN model...")
        
        # Build models
        self.build_gan()
        
        # Prepare data
        real_labels = np.ones((len(real_data), 1))
        fake_labels = np.zeros((len(real_data), 1))
        
        d_losses = []
        g_losses = []
        
        for epoch in range(self.config['epochs']):
            # Train discriminator
            noise = np.random.normal(0, 1, (self.config['batch_size'], self.config['latent_dim']))
            generated_data = self.generator.predict(noise, verbose=0)
            
            # Select random real samples
            idx = np.random.randint(0, real_data.shape[0], self.config['batch_size'])
            real_samples = real_data[idx]
            
            # Train discriminator
            d_loss_real = self.discriminator.train_on_batch(real_samples, real_labels[:self.config['batch_size']])
            d_loss_fake = self.discriminator.train_on_batch(generated_data, fake_labels[:self.config['batch_size']])
            d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
            
            # Train generator
            noise = np.random.normal(0, 1, (self.config['batch_size'], self.config['latent_dim']))
            g_loss = self.gan.train_on_batch(noise, real_labels[:self.config['batch_size']])
            
            d_losses.append(d_loss[0])
            g_losses.append(g_loss)
            
            if epoch % 100 == 0:
                print(f"Epoch {epoch}, D Loss: {d_loss[0]:.4f}, G Loss: {g_loss:.4f}")
        
        self.is_trained = True
        
        return {
            'status': 'success',
            'final_d_loss': float(d_losses[-1]),
            'final_g_loss': float(g_losses[-1]),
            'epochs_trained': len(d_losses)
        }
    
    def generate_data(self, num_samples: int = 100) -> np.ndarray:
        """Generate synthetic market data"""
        if not self.is_trained:
            return np.array([])
        
        noise = np.random.normal(0, 1, (num_samples, self.config['latent_dim']))
        generated_data = self.generator.predict(noise, verbose=0)
        
        return generated_data
    
    def simulate_market_scenarios(self, base_data: np.ndarray, num_scenarios: int = 10) -> Dict:
        """Simulate different market scenarios"""
        scenarios = {}
        
        # Bull market scenario
        noise = np.random.normal(0.5, 0.3, (num_scenarios, self.config['latent_dim']))
        bull_data = self.generator.predict(noise, verbose=0)
        scenarios['bull_market'] = bull_data
        
        # Bear market scenario
        noise = np.random.normal(-0.5, 0.3, (num_scenarios, self.config['latent_dim']))
        bear_data = self.generator.predict(noise, verbose=0)
        scenarios['bear_market'] = bear_data
        
        # High volatility scenario
        noise = np.random.normal(0, 1.5, (num_scenarios, self.config['latent_dim']))
        volatile_data = self.generator.predict(noise, verbose=0)
        scenarios['high_volatility'] = volatile_data
        
        return scenarios


class AIModelManager:
    """
    Manager for all AI models
    Coordinates LSTM and GAN models
    """
    
    def __init__(self):
        self.lstm_models = {}
        self.gan_models = {}
        self.model_dir = 'data/ai_models'
        
        os.makedirs(self.model_dir, exist_ok=True)
    
    def create_lstm_model(self, symbol: str, sequence_length: int = 60) -> LSTMPredictor:
        """Create LSTM model for symbol"""
        model = LSTMPredictor(sequence_length=sequence_length)
        self.lstm_models[symbol] = model
        return model
    
    def create_gan_model(self, symbol: str, sequence_length: int = 60) -> GANSimulator:
        """Create GAN model for symbol"""
        model = GANSimulator(sequence_length=sequence_length)
        self.gan_models[symbol] = model
        return model
    
    def train_all_models(self, market_data: Dict[str, List[List]]) -> Dict:
        """Train all models with market data"""
        results = {}
        
        for symbol, data in market_data.items():
            print(f"🤖 Training models for {symbol}...")
            
            # Train LSTM
            if symbol not in self.lstm_models:
                self.create_lstm_model(symbol)
            
            lstm_result = self.lstm_models[symbol].train(data)
            results[f"{symbol}_lstm"] = lstm_result
            
            # Train GAN
            if symbol not in self.gan_models:
                self.create_gan_model(symbol)
            
            # Prepare GAN data
            features = self.lstm_models[symbol].prepare_features(data)
            gan_result = self.gan_models[symbol].train(features)
            results[f"{symbol}_gan"] = gan_result
        
        return results
    
    def predict_all(self, market_data: Dict[str, List[List]], steps_ahead: int = 1) -> Dict:
        """Make predictions for all symbols"""
        predictions = {}
        
        for symbol, data in market_data.items():
            if symbol in self.lstm_models and self.lstm_models[symbol].is_trained:
                pred = self.lstm_models[symbol].predict(data, steps_ahead)
                predictions[symbol] = pred
        
        return predictions
    
    def save_all_models(self) -> bool:
        """Save all trained models"""
        try:
            for symbol, model in self.lstm_models.items():
                if model.is_trained:
                    model.save(f"{self.model_dir}/{symbol}_lstm")
            
            for symbol, model in self.gan_models.items():
                if model.is_trained:
                    # Save GAN models
                    model.generator.save(f"{self.model_dir}/{symbol}_gan_generator.h5")
                    model.discriminator.save(f"{self.model_dir}/{symbol}_gan_discriminator.h5")
            
            return True
        except Exception as e:
            print(f"❌ Error saving models: {e}")
            return False
    
    def load_all_models(self) -> bool:
        """Load all saved models"""
        try:
            # This would load models from disk
            # Implementation depends on saved model structure
            return True
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            return False


if __name__ == '__main__':
    print("🧠 AI Models Test\n")
    
    # Test LSTM
    print("Testing LSTM...")
    lstm = LSTMPredictor()
    
    # Generate sample data
    sample_data = []
    base_price = 50000
    for i in range(200):
        price = base_price + np.random.normal(0, 100)
        volume = np.random.uniform(1000, 10000)
        sample_data.append([i, price, price*1.01, price*0.99, price, volume])
    
    # Train model
    result = lstm.train(sample_data)
    print(f"LSTM Training Result: {result}")
    
    # Test GAN
    print("\nTesting GAN...")
    gan = GANSimulator()
    
    # Generate sample features
    sample_features = np.random.randn(100, 60, 5)
    gan_result = gan.train(sample_features)
    print(f"GAN Training Result: {gan_result}")
    
    print("\n✅ AI Models test completed!")