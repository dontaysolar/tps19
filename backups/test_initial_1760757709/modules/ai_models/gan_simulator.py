#!/usr/bin/env python3
"""GAN (Generative Adversarial Network) Market Simulator - TPS19"""

import numpy as np
import pandas as pd
from datetime import datetime
import json
import pickle
import os

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential, Model, load_model
    from tensorflow.keras.layers import Dense, LSTM, Dropout, Input, Reshape, Flatten
    from tensorflow.keras.optimizers import Adam
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️ TensorFlow not available. Install with: pip install tensorflow")


class GANSimulator:
    """GAN for generating realistic market scenarios"""
    
    def __init__(self, model_dir=None):
        """Initialize GAN Simulator
        
        Args:
            model_dir: Directory to save/load models
        """
        if model_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_dir = os.path.join(base_dir, 'data', 'models')
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.generator = None
        self.discriminator = None
        self.gan = None
        
        self.latent_dim = 100  # Noise dimension for generator
        self.sequence_length = 60
        self.n_features = 5  # OHLCV
        
        self.config = {
            'generator_layers': [256, 512, 256],
            'discriminator_layers': [256, 128],
            'dropout_rate': 0.3,
            'learning_rate': 0.0002,
            'batch_size': 64,
            'epochs': 100
        }
        
        self.metrics = {
            'generator_loss': [],
            'discriminator_loss': [],
            'last_training': None,
            'simulations_run': 0
        }
        
    def build_generator(self):
        """Build generator model"""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow required for GAN")
            
        model = Sequential([
            Dense(self.config['generator_layers'][0], input_dim=self.latent_dim),
            keras.layers.LeakyReLU(alpha=0.2),
            Dropout(self.config['dropout_rate']),
            
            Dense(self.config['generator_layers'][1]),
            keras.layers.LeakyReLU(alpha=0.2),
            Dropout(self.config['dropout_rate']),
            
            Dense(self.config['generator_layers'][2]),
            keras.layers.LeakyReLU(alpha=0.2),
            
            Dense(self.sequence_length * self.n_features, activation='tanh'),
            Reshape((self.sequence_length, self.n_features))
        ])
        
        return model
        
    def build_discriminator(self):
        """Build discriminator model"""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow required for GAN")
            
        model = Sequential([
            Flatten(input_shape=(self.sequence_length, self.n_features)),
            
            Dense(self.config['discriminator_layers'][0]),
            keras.layers.LeakyReLU(alpha=0.2),
            Dropout(self.config['dropout_rate']),
            
            Dense(self.config['discriminator_layers'][1]),
            keras.layers.LeakyReLU(alpha=0.2),
            Dropout(self.config['dropout_rate']),
            
            Dense(1, activation='sigmoid')
        ])
        
        # Compile discriminator
        model.compile(
            optimizer=Adam(learning_rate=self.config['learning_rate']),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
        
    def build_gan(self):
        """Build complete GAN model"""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow required for GAN")
            
        # Build components
        self.generator = self.build_generator()
        self.discriminator = self.build_discriminator()
        
        # Make discriminator non-trainable for combined model
        self.discriminator.trainable = False
        
        # Build GAN
        gan_input = Input(shape=(self.latent_dim,))
        generated_sequence = self.generator(gan_input)
        gan_output = self.discriminator(generated_sequence)
        
        self.gan = Model(gan_input, gan_output)
        self.gan.compile(
            optimizer=Adam(learning_rate=self.config['learning_rate']),
            loss='binary_crossentropy'
        )
        
        return self.gan
        
    def prepare_data(self, data):
        """Prepare real market data for training
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Normalized sequences
        """
        # Extract OHLCV values
        data_values = data[['open', 'high', 'low', 'close', 'volume']].values
        
        # Normalize to [-1, 1] range (tanh activation)
        min_val = data_values.min(axis=0)
        max_val = data_values.max(axis=0)
        normalized = 2 * (data_values - min_val) / (max_val - min_val + 1e-8) - 1
        
        # Create sequences
        sequences = []
        for i in range(len(normalized) - self.sequence_length + 1):
            sequences.append(normalized[i:i+self.sequence_length])
            
        return np.array(sequences), min_val, max_val
        
    def train(self, data, epochs=None):
        """Train GAN on historical market data
        
        Args:
            data: DataFrame with OHLCV data
            epochs: Number of training epochs
            
        Returns:
            Training history
        """
        if not TENSORFLOW_AVAILABLE:
            print("⚠️ TensorFlow not available, skipping training")
            return None
            
        print("🎭 Training GAN Market Simulator...")
        
        # Build GAN if not exists
        if self.gan is None:
            self.build_gan()
            
        # Prepare data
        X_train, self.min_val, self.max_val = self.prepare_data(data)
        
        epochs = epochs or self.config['epochs']
        batch_size = self.config['batch_size']
        
        # Training loop
        for epoch in range(epochs):
            # Train discriminator
            # Select random batch of real sequences
            idx = np.random.randint(0, X_train.shape[0], batch_size)
            real_sequences = X_train[idx]
            
            # Generate fake sequences
            noise = np.random.normal(0, 1, (batch_size, self.latent_dim))
            fake_sequences = self.generator.predict(noise, verbose=0)
            
            # Train discriminator on real and fake
            d_loss_real = self.discriminator.train_on_batch(
                real_sequences,
                np.ones((batch_size, 1))
            )
            d_loss_fake = self.discriminator.train_on_batch(
                fake_sequences,
                np.zeros((batch_size, 1))
            )
            d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
            
            # Train generator
            noise = np.random.normal(0, 1, (batch_size, self.latent_dim))
            g_loss = self.gan.train_on_batch(noise, np.ones((batch_size, 1)))
            
            # Save metrics
            self.metrics['discriminator_loss'].append(float(d_loss[0]))
            self.metrics['generator_loss'].append(float(g_loss))
            
            # Print progress
            if epoch % 10 == 0:
                print(f"Epoch {epoch}/{epochs} - D Loss: {d_loss[0]:.4f}, G Loss: {g_loss:.4f}")
                
        self.metrics['last_training'] = datetime.now().isoformat()
        
        # Save models
        self.save()
        
        print(f"✅ GAN training completed")
        return self.metrics
        
    def generate_scenarios(self, n_scenarios=10, scenario_type='normal'):
        """Generate market scenarios
        
        Args:
            n_scenarios: Number of scenarios to generate
            scenario_type: Type of scenario ('normal', 'volatile', 'crash', 'rally')
            
        Returns:
            Generated market scenarios
        """
        if self.generator is None:
            if not self.load():
                raise ValueError("No trained generator available")
                
        # Generate noise with different characteristics
        if scenario_type == 'normal':
            noise = np.random.normal(0, 1, (n_scenarios, self.latent_dim))
        elif scenario_type == 'volatile':
            noise = np.random.normal(0, 2, (n_scenarios, self.latent_dim))
        elif scenario_type == 'crash':
            noise = np.random.normal(-1, 1.5, (n_scenarios, self.latent_dim))
        elif scenario_type == 'rally':
            noise = np.random.normal(1, 1.5, (n_scenarios, self.latent_dim))
        else:
            noise = np.random.normal(0, 1, (n_scenarios, self.latent_dim))
            
        # Generate scenarios
        generated = self.generator.predict(noise, verbose=0)
        
        # Denormalize
        denormalized = (generated + 1) / 2 * (self.max_val - self.min_val) + self.min_val
        
        self.metrics['simulations_run'] += n_scenarios
        
        return denormalized
        
    def simulate_trade(self, strategy, n_simulations=100):
        """Simulate strategy performance across multiple scenarios
        
        Args:
            strategy: Trading strategy function
            n_simulations: Number of simulations
            
        Returns:
            Simulation results
        """
        results = {
            'profits': [],
            'max_drawdowns': [],
            'win_rates': [],
            'sharpe_ratios': []
        }
        
        for _ in range(n_simulations):
            # Generate scenario
            scenario = self.generate_scenarios(n_scenarios=1)[0]
            
            # Convert to DataFrame
            scenario_df = pd.DataFrame(scenario, columns=['open', 'high', 'low', 'close', 'volume'])
            
            # Run strategy (simplified)
            try:
                strategy_result = strategy(scenario_df)
                results['profits'].append(strategy_result.get('profit', 0))
                results['max_drawdowns'].append(strategy_result.get('max_drawdown', 0))
                results['win_rates'].append(strategy_result.get('win_rate', 0))
                results['sharpe_ratios'].append(strategy_result.get('sharpe_ratio', 0))
            except Exception as e:
                print(f"⚠️ Strategy simulation error: {e}")
                
        # Calculate statistics
        return {
            'avg_profit': np.mean(results['profits']),
            'std_profit': np.std(results['profits']),
            'avg_max_drawdown': np.mean(results['max_drawdowns']),
            'avg_win_rate': np.mean(results['win_rates']),
            'avg_sharpe': np.mean(results['sharpe_ratios']),
            'worst_case': np.percentile(results['profits'], 5),
            'best_case': np.percentile(results['profits'], 95),
            'n_simulations': n_simulations
        }
        
    def stress_test(self, current_position, n_scenarios=1000):
        """Stress test current position across scenarios
        
        Args:
            current_position: Current trading position details
            n_scenarios: Number of stress test scenarios
            
        Returns:
            Stress test results
        """
        scenarios = self.generate_scenarios(n_scenarios)
        
        # Test different scenario types
        crash_scenarios = self.generate_scenarios(n_scenarios // 4, 'crash')
        volatile_scenarios = self.generate_scenarios(n_scenarios // 4, 'volatile')
        
        results = {
            'normal': self._test_position(current_position, scenarios),
            'crash': self._test_position(current_position, crash_scenarios),
            'volatile': self._test_position(current_position, volatile_scenarios)
        }
        
        return results
        
    def _test_position(self, position, scenarios):
        """Test position against scenarios"""
        pnls = []
        
        for scenario in scenarios:
            # Calculate P&L for this scenario
            final_price = scenario[-1, 3]  # Last close price
            entry_price = position.get('entry_price', final_price)
            size = position.get('size', 1.0)
            side = position.get('side', 'long')
            
            if side == 'long':
                pnl = (final_price - entry_price) * size
            else:
                pnl = (entry_price - final_price) * size
                
            pnls.append(pnl)
            
        return {
            'avg_pnl': np.mean(pnls),
            'std_pnl': np.std(pnls),
            'var_95': np.percentile(pnls, 5),  # Value at Risk
            'best_case': np.max(pnls),
            'worst_case': np.min(pnls)
        }
        
    def save(self):
        """Save generator and discriminator"""
        if self.generator is None or self.discriminator is None:
            return False
            
        try:
            self.generator.save(os.path.join(self.model_dir, 'gan_generator.h5'))
            self.discriminator.save(os.path.join(self.model_dir, 'gan_discriminator.h5'))
            
            # Save metrics
            with open(os.path.join(self.model_dir, 'gan_metrics.pkl'), 'wb') as f:
                pickle.dump({
                    'metrics': self.metrics,
                    'config': self.config,
                    'min_val': self.min_val,
                    'max_val': self.max_val
                }, f)
                
            return True
        except Exception as e:
            print(f"❌ Error saving GAN: {e}")
            return False
            
    def load(self):
        """Load generator and discriminator"""
        gen_path = os.path.join(self.model_dir, 'gan_generator.h5')
        disc_path = os.path.join(self.model_dir, 'gan_discriminator.h5')
        metrics_path = os.path.join(self.model_dir, 'gan_metrics.pkl')
        
        if not os.path.exists(gen_path) or not os.path.exists(disc_path):
            return False
            
        try:
            self.generator = load_model(gen_path)
            self.discriminator = load_model(disc_path)
            
            if os.path.exists(metrics_path):
                with open(metrics_path, 'rb') as f:
                    data = pickle.load(f)
                    self.metrics = data['metrics']
                    self.config = data['config']
                    self.min_val = data['min_val']
                    self.max_val = data['max_val']
                    
            return True
        except Exception as e:
            print(f"❌ Error loading GAN: {e}")
            return False
            
    def get_status(self):
        """Get GAN status"""
        return {
            'generator_loaded': self.generator is not None,
            'discriminator_loaded': self.discriminator is not None,
            'tensorflow_available': TENSORFLOW_AVAILABLE,
            'metrics': self.metrics,
            'config': self.config
        }


# Test functionality
def test_gan():
    """Test GAN simulator"""
    print("🧪 Testing GAN Simulator...")
    
    simulator = GANSimulator()
    
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
    
    if TENSORFLOW_AVAILABLE:
        # Train
        simulator.train(data, epochs=5)
        
        # Generate scenarios
        scenarios = simulator.generate_scenarios(n_scenarios=5)
        print(f"✅ Generated {len(scenarios)} scenarios")
        
        # Stress test
        position = {'entry_price': 26000, 'size': 1.0, 'side': 'long'}
        stress_results = simulator.stress_test(position, n_scenarios=10)
        print(f"✅ Stress test results: {stress_results}")
    else:
        print("⚠️ TensorFlow not available, skipping training")
        
    print(f"✅ Status: {simulator.get_status()}")


if __name__ == '__main__':
    test_gan()
