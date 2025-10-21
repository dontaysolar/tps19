#!/usr/bin/env python3
"""
Advanced Trading Strategies for APEX Trading System
Multiple sophisticated trading strategies with AI integration
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod
import statistics

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
except ImportError:
    os.system("pip3 install --break-system-packages ccxt scikit-learn -q")
    import ccxt
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression

class TradingStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.is_active = False
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'win_rate': 0.0
        }
    
    @abstractmethod
    def generate_signal(self, market_data: Dict) -> Dict:
        """Generate trading signal based on market data"""
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: Dict, account_balance: float) -> float:
        """Calculate position size based on signal and account balance"""
        pass
    
    def update_performance(self, trade_result: Dict):
        """Update strategy performance metrics"""
        self.performance_metrics['total_trades'] += 1
        
        if trade_result.get('profit', 0) > 0:
            self.performance_metrics['winning_trades'] += 1
        else:
            self.performance_metrics['losing_trades'] += 1
        
        self.performance_metrics['total_profit'] += trade_result.get('profit', 0)
        self.performance_metrics['win_rate'] = (
            self.performance_metrics['winning_trades'] / 
            self.performance_metrics['total_trades'] * 100
        )
    
    def get_performance(self) -> Dict:
        """Get strategy performance metrics"""
        return self.performance_metrics.copy()


class ScalpingStrategy(TradingStrategy):
    """
    High-frequency scalping strategy
    Features:
    - Quick in/out trades
    - Small profit targets
    - Tight stop losses
    - Order book analysis
    """
    
    def __init__(self, config: Dict = None):
        default_config = {
            'profit_target_pct': 0.1,      # 0.1% profit target
            'stop_loss_pct': 0.05,         # 0.05% stop loss
            'max_position_size': 0.1,      # 10% of account
            'min_volume_threshold': 1000,  # Minimum volume
            'max_spread_pct': 0.02,        # Max 0.02% spread
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'ma_period': 5
        }
        
        if config:
            default_config.update(config)
        
        super().__init__("ScalpingStrategy", default_config)
    
    def generate_signal(self, market_data: Dict) -> Dict:
        """Generate scalping signal"""
        try:
            symbol = market_data.get('symbol', '')
            price = market_data.get('price', 0)
            volume = market_data.get('volume', 0)
            ohlcv = market_data.get('ohlcv', [])
            
            if not ohlcv or len(ohlcv) < self.config['ma_period']:
                return {'signal': 'HOLD', 'confidence': 0.0}
            
            # Calculate technical indicators
            closes = [candle[4] for candle in ohlcv]
            volumes = [candle[5] for candle in ohlcv]
            
            # Moving average
            ma = np.mean(closes[-self.config['ma_period']:])
            
            # RSI calculation
            rsi = self._calculate_rsi(closes)
            
            # Volume analysis
            avg_volume = np.mean(volumes[-10:]) if len(volumes) >= 10 else volume
            
            # Spread analysis
            spread_pct = market_data.get('spread_pct', 0)
            
            # Generate signal
            signal = 'HOLD'
            confidence = 0.0
            
            # Buy conditions
            if (price < ma and 
                rsi < self.config['rsi_oversold'] and 
                volume > avg_volume * 1.5 and
                spread_pct < self.config['max_spread_pct']):
                signal = 'BUY'
                confidence = min(0.9, (self.config['rsi_oversold'] - rsi) / 10)
            
            # Sell conditions
            elif (price > ma and 
                  rsi > self.config['rsi_overbought'] and 
                  volume > avg_volume * 1.5 and
                  spread_pct < self.config['max_spread_pct']):
                signal = 'SELL'
                confidence = min(0.9, (rsi - self.config['rsi_overbought']) / 10)
            
            return {
                'signal': signal,
                'confidence': confidence,
                'price': price,
                'rsi': rsi,
                'ma': ma,
                'volume_ratio': volume / avg_volume if avg_volume > 0 else 1,
                'spread_pct': spread_pct
            }
            
        except Exception as e:
            print(f"❌ Scalping signal error: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0}
    
    def calculate_position_size(self, signal: Dict, account_balance: float) -> float:
        """Calculate position size for scalping"""
        if signal['signal'] == 'HOLD':
            return 0.0
        
        # Base position size
        base_size = account_balance * self.config['max_position_size']
        
        # Adjust based on confidence
        confidence_multiplier = signal['confidence']
        
        # Adjust based on volume
        volume_multiplier = min(1.0, signal.get('volume_ratio', 1) / 2)
        
        position_size = base_size * confidence_multiplier * volume_multiplier
        
        return min(position_size, account_balance * 0.2)  # Cap at 20%
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi


class TrendFollowingStrategy(TradingStrategy):
    """
    Trend following strategy using multiple timeframes
    Features:
    - Multi-timeframe analysis
    - Trend strength measurement
    - Momentum confirmation
    - Dynamic position sizing
    """
    
    def __init__(self, config: Dict = None):
        default_config = {
            'short_ma_period': 10,
            'long_ma_period': 30,
            'trend_confirmation_periods': 3,
            'momentum_period': 14,
            'max_position_size': 0.2,
            'min_trend_strength': 0.6,
            'stop_loss_atr_multiplier': 2.0,
            'take_profit_atr_multiplier': 3.0
        }
        
        if config:
            default_config.update(config)
        
        super().__init__("TrendFollowingStrategy", default_config)
    
    def generate_signal(self, market_data: Dict) -> Dict:
        """Generate trend following signal"""
        try:
            symbol = market_data.get('symbol', '')
            ohlcv = market_data.get('ohlcv', [])
            
            if len(ohlcv) < self.config['long_ma_period']:
                return {'signal': 'HOLD', 'confidence': 0.0}
            
            # Extract price data
            closes = [candle[4] for candle in ohlcv]
            highs = [candle[2] for candle in ohlcv]
            lows = [candle[3] for candle in ohlcv]
            
            # Calculate moving averages
            short_ma = np.mean(closes[-self.config['short_ma_period']:])
            long_ma = np.mean(closes[-self.config['long_ma_period']:])
            
            # Calculate trend strength
            trend_strength = self._calculate_trend_strength(closes)
            
            # Calculate momentum
            momentum = self._calculate_momentum(closes)
            
            # Calculate ATR for stop loss/take profit
            atr = self._calculate_atr(highs, lows, closes)
            
            # Generate signal
            signal = 'HOLD'
            confidence = 0.0
            
            # Bullish trend
            if (short_ma > long_ma and 
                trend_strength > self.config['min_trend_strength'] and
                momentum > 0):
                signal = 'BUY'
                confidence = min(0.9, trend_strength * momentum)
            
            # Bearish trend
            elif (short_ma < long_ma and 
                  trend_strength > self.config['min_trend_strength'] and
                  momentum < 0):
                signal = 'SELL'
                confidence = min(0.9, trend_strength * abs(momentum))
            
            return {
                'signal': signal,
                'confidence': confidence,
                'short_ma': short_ma,
                'long_ma': long_ma,
                'trend_strength': trend_strength,
                'momentum': momentum,
                'atr': atr,
                'current_price': closes[-1]
            }
            
        except Exception as e:
            print(f"❌ Trend following signal error: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0}
    
    def calculate_position_size(self, signal: Dict, account_balance: float) -> float:
        """Calculate position size for trend following"""
        if signal['signal'] == 'HOLD':
            return 0.0
        
        # Base position size
        base_size = account_balance * self.config['max_position_size']
        
        # Adjust based on trend strength and confidence
        trend_multiplier = signal.get('trend_strength', 0.5)
        confidence_multiplier = signal['confidence']
        
        position_size = base_size * trend_multiplier * confidence_multiplier
        
        return min(position_size, account_balance * 0.3)  # Cap at 30%
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """Calculate trend strength using linear regression"""
        if len(prices) < 10:
            return 0.0
        
        x = np.arange(len(prices))
        y = np.array(prices)
        
        # Linear regression
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        
        # Normalize slope to 0-1 range
        price_range = max(prices) - min(prices)
        if price_range == 0:
            return 0.0
        
        trend_strength = abs(slope) / (price_range / len(prices))
        return min(1.0, trend_strength)
    
    def _calculate_momentum(self, prices: List[float]) -> float:
        """Calculate price momentum"""
        if len(prices) < self.config['momentum_period']:
            return 0.0
        
        current_price = prices[-1]
        past_price = prices[-self.config['momentum_period']]
        
        return (current_price - past_price) / past_price
    
    def _calculate_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(highs) < period + 1:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(highs)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            
            true_range = max(high_low, high_close, low_close)
            true_ranges.append(true_range)
        
        return np.mean(true_ranges[-period:])


class MeanReversionStrategy(TradingStrategy):
    """
    Mean reversion strategy using statistical analysis
    Features:
    - Bollinger Bands
    - Z-score analysis
    - Statistical arbitrage
    - Volatility-based position sizing
    """
    
    def __init__(self, config: Dict = None):
        default_config = {
            'bb_period': 20,
            'bb_std_dev': 2.0,
            'z_score_threshold': 2.0,
            'max_position_size': 0.15,
            'min_volatility': 0.01,
            'max_volatility': 0.1,
            'reversion_period': 5
        }
        
        if config:
            default_config.update(config)
        
        super().__init__("MeanReversionStrategy", default_config)
    
    def generate_signal(self, market_data: Dict) -> Dict:
        """Generate mean reversion signal"""
        try:
            symbol = market_data.get('symbol', '')
            ohlcv = market_data.get('ohlcv', [])
            
            if len(ohlcv) < self.config['bb_period']:
                return {'signal': 'HOLD', 'confidence': 0.0}
            
            # Extract price data
            closes = [candle[4] for candle in ohlcv]
            
            # Calculate Bollinger Bands
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(closes)
            
            # Calculate Z-score
            z_score = self._calculate_z_score(closes)
            
            # Calculate volatility
            volatility = self._calculate_volatility(closes)
            
            # Generate signal
            signal = 'HOLD'
            confidence = 0.0
            
            current_price = closes[-1]
            
            # Oversold condition (buy)
            if (current_price <= bb_lower and 
                z_score < -self.config['z_score_threshold'] and
                self.config['min_volatility'] < volatility < self.config['max_volatility']):
                signal = 'BUY'
                confidence = min(0.9, abs(z_score) / self.config['z_score_threshold'])
            
            # Overbought condition (sell)
            elif (current_price >= bb_upper and 
                  z_score > self.config['z_score_threshold'] and
                  self.config['min_volatility'] < volatility < self.config['max_volatility']):
                signal = 'SELL'
                confidence = min(0.9, abs(z_score) / self.config['z_score_threshold'])
            
            return {
                'signal': signal,
                'confidence': confidence,
                'current_price': current_price,
                'bb_upper': bb_upper,
                'bb_middle': bb_middle,
                'bb_lower': bb_lower,
                'z_score': z_score,
                'volatility': volatility
            }
            
        except Exception as e:
            print(f"❌ Mean reversion signal error: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0}
    
    def calculate_position_size(self, signal: Dict, account_balance: float) -> float:
        """Calculate position size for mean reversion"""
        if signal['signal'] == 'HOLD':
            return 0.0
        
        # Base position size
        base_size = account_balance * self.config['max_position_size']
        
        # Adjust based on Z-score (stronger deviation = larger position)
        z_score_multiplier = min(1.0, abs(signal.get('z_score', 0)) / self.config['z_score_threshold'])
        
        # Adjust based on volatility (higher volatility = smaller position)
        volatility = signal.get('volatility', 0.05)
        volatility_multiplier = max(0.5, 1.0 - (volatility - self.config['min_volatility']) / 
                                   (self.config['max_volatility'] - self.config['min_volatility']))
        
        position_size = base_size * z_score_multiplier * volatility_multiplier
        
        return min(position_size, account_balance * 0.2)  # Cap at 20%
    
    def _calculate_bollinger_bands(self, prices: List[float]) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < self.config['bb_period']:
            return 0.0, 0.0, 0.0
        
        recent_prices = prices[-self.config['bb_period']:]
        middle = np.mean(recent_prices)
        std = np.std(recent_prices)
        
        upper = middle + (std * self.config['bb_std_dev'])
        lower = middle - (std * self.config['bb_std_dev'])
        
        return upper, middle, lower
    
    def _calculate_z_score(self, prices: List[float]) -> float:
        """Calculate Z-score for mean reversion"""
        if len(prices) < self.config['bb_period']:
            return 0.0
        
        recent_prices = prices[-self.config['bb_period']:]
        mean = np.mean(recent_prices)
        std = np.std(recent_prices)
        
        if std == 0:
            return 0.0
        
        current_price = prices[-1]
        z_score = (current_price - mean) / std
        
        return z_score
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility"""
        if len(prices) < 2:
            return 0.0
        
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns)
        
        return volatility


class MLStrategy(TradingStrategy):
    """
    Machine Learning based trading strategy
    Features:
    - Feature engineering
    - Model training
    - Prediction confidence
    - Adaptive learning
    """
    
    def __init__(self, config: Dict = None):
        default_config = {
            'model_type': 'random_forest',  # 'random_forest' or 'logistic_regression'
            'feature_window': 20,
            'retrain_frequency': 100,  # Retrain every 100 trades
            'min_confidence': 0.6,
            'max_position_size': 0.25,
            'feature_importance_threshold': 0.1
        }
        
        if config:
            default_config.update(config)
        
        super().__init__("MLStrategy", default_config)
        
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = {}
        self.training_data = []
        self.is_trained = False
    
    def generate_signal(self, market_data: Dict) -> Dict:
        """Generate ML-based signal"""
        try:
            if not self.is_trained:
                return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'Model not trained'}
            
            # Extract features
            features = self._extract_features(market_data)
            if features is None:
                return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'Insufficient data'}
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            confidence = self.model.predict_proba(features_scaled)[0].max()
            
            # Convert prediction to signal
            if prediction == 1 and confidence >= self.config['min_confidence']:
                signal = 'BUY'
            elif prediction == 0 and confidence >= self.config['min_confidence']:
                signal = 'SELL'
            else:
                signal = 'HOLD'
            
            return {
                'signal': signal,
                'confidence': confidence,
                'prediction': prediction,
                'features': features,
                'feature_importance': self.feature_importance
            }
            
        except Exception as e:
            print(f"❌ ML strategy signal error: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0, 'reason': str(e)}
    
    def calculate_position_size(self, signal: Dict, account_balance: float) -> float:
        """Calculate position size for ML strategy"""
        if signal['signal'] == 'HOLD':
            return 0.0
        
        # Base position size
        base_size = account_balance * self.config['max_position_size']
        
        # Adjust based on confidence
        confidence_multiplier = signal['confidence']
        
        position_size = base_size * confidence_multiplier
        
        return min(position_size, account_balance * 0.3)  # Cap at 30%
    
    def train_model(self, training_data: List[Dict]) -> bool:
        """Train the ML model"""
        try:
            if len(training_data) < 50:
                print("❌ Insufficient training data")
                return False
            
            # Extract features and labels
            X, y = self._prepare_training_data(training_data)
            
            if X is None or y is None:
                return False
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            if self.config['model_type'] == 'random_forest':
                self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                self.model = LogisticRegression(random_state=42)
            
            self.model.fit(X_scaled, y)
            
            # Calculate feature importance
            if hasattr(self.model, 'feature_importances_'):
                self.feature_importance = dict(zip(
                    self._get_feature_names(),
                    self.model.feature_importances_
                ))
            
            self.is_trained = True
            print(f"✅ ML model trained with {len(training_data)} samples")
            return True
            
        except Exception as e:
            print(f"❌ Model training error: {e}")
            return False
    
    def _extract_features(self, market_data: Dict) -> Optional[List[float]]:
        """Extract features from market data"""
        try:
            ohlcv = market_data.get('ohlcv', [])
            if len(ohlcv) < self.config['feature_window']:
                return None
            
            closes = [candle[4] for candle in ohlcv]
            volumes = [candle[5] for candle in ohlcv]
            
            features = []
            
            # Price features
            features.extend([
                closes[-1],  # Current price
                np.mean(closes[-5:]),  # 5-period MA
                np.mean(closes[-10:]),  # 10-period MA
                np.mean(closes[-20:]),  # 20-period MA
                np.std(closes[-10:]),  # Price volatility
            ])
            
            # Volume features
            features.extend([
                volumes[-1],  # Current volume
                np.mean(volumes[-5:]),  # 5-period volume MA
                np.std(volumes[-10:]),  # Volume volatility
            ])
            
            # Technical indicators
            rsi = self._calculate_rsi(closes)
            features.append(rsi)
            
            # Price momentum
            momentum = (closes[-1] - closes[-5]) / closes[-5] if len(closes) >= 5 else 0
            features.append(momentum)
            
            # Bollinger Bands position
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(closes)
            bb_position = (closes[-1] - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
            features.append(bb_position)
            
            return features
            
        except Exception as e:
            print(f"❌ Feature extraction error: {e}")
            return None
    
    def _prepare_training_data(self, training_data: List[Dict]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Prepare training data for ML model"""
        try:
            X = []
            y = []
            
            for data in training_data:
                features = self._extract_features(data)
                if features is None:
                    continue
                
                X.append(features)
                
                # Create label based on future price movement
                future_price = data.get('future_price', 0)
                current_price = data.get('current_price', 0)
                
                if future_price > current_price * 1.001:  # 0.1% profit
                    y.append(1)  # Buy
                elif future_price < current_price * 0.999:  # 0.1% loss
                    y.append(0)  # Sell
                else:
                    y.append(1)  # Default to buy for neutral
            
            return np.array(X), np.array(y)
            
        except Exception as e:
            print(f"❌ Training data preparation error: {e}")
            return None, None
    
    def _get_feature_names(self) -> List[str]:
        """Get feature names for importance analysis"""
        return [
            'current_price', 'ma_5', 'ma_10', 'ma_20', 'price_volatility',
            'current_volume', 'volume_ma_5', 'volume_volatility',
            'rsi', 'momentum', 'bb_position'
        ]
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_bollinger_bands(self, prices: List[float]) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < 20:
            return 0.0, 0.0, 0.0
        
        recent_prices = prices[-20:]
        middle = np.mean(recent_prices)
        std = np.std(recent_prices)
        
        upper = middle + (std * 2)
        lower = middle - (std * 2)
        
        return upper, middle, lower


class StrategyManager:
    """
    Manager for all trading strategies
    Coordinates strategy selection and execution
    """
    
    def __init__(self):
        self.strategies = {}
        self.active_strategies = []
        self.strategy_performance = {}
        
        # Initialize default strategies
        self._initialize_default_strategies()
    
    def _initialize_default_strategies(self):
        """Initialize default trading strategies"""
        self.strategies = {
            'scalping': ScalpingStrategy(),
            'trend_following': TrendFollowingStrategy(),
            'mean_reversion': MeanReversionStrategy(),
            'ml_strategy': MLStrategy()
        }
        
        # Set initial active strategies
        self.active_strategies = ['scalping', 'trend_following', 'mean_reversion']
    
    def add_strategy(self, name: str, strategy: TradingStrategy):
        """Add a new strategy"""
        self.strategies[name] = strategy
    
    def remove_strategy(self, name: str):
        """Remove a strategy"""
        if name in self.strategies:
            del self.strategies[name]
        if name in self.active_strategies:
            self.active_strategies.remove(name)
    
    def set_active_strategies(self, strategy_names: List[str]):
        """Set active strategies"""
        self.active_strategies = [name for name in strategy_names if name in self.strategies]
    
    def generate_combined_signal(self, market_data: Dict) -> Dict:
        """Generate combined signal from all active strategies"""
        signals = {}
        total_confidence = 0.0
        signal_count = 0
        
        for strategy_name in self.active_strategies:
            if strategy_name not in self.strategies:
                continue
            
            strategy = self.strategies[strategy_name]
            signal = strategy.generate_signal(market_data)
            
            if signal['signal'] != 'HOLD':
                signals[strategy_name] = signal
                total_confidence += signal['confidence']
                signal_count += 1
        
        if signal_count == 0:
            return {'signal': 'HOLD', 'confidence': 0.0, 'strategies': {}}
        
        # Calculate combined signal
        avg_confidence = total_confidence / signal_count
        
        # Count buy vs sell signals
        buy_signals = sum(1 for s in signals.values() if s['signal'] == 'BUY')
        sell_signals = sum(1 for s in signals.values() if s['signal'] == 'SELL')
        
        if buy_signals > sell_signals:
            combined_signal = 'BUY'
        elif sell_signals > buy_signals:
            combined_signal = 'SELL'
        else:
            combined_signal = 'HOLD'
        
        return {
            'signal': combined_signal,
            'confidence': avg_confidence,
            'strategies': signals,
            'buy_count': buy_signals,
            'sell_count': sell_signals
        }
    
    def get_strategy_performance(self) -> Dict:
        """Get performance of all strategies"""
        performance = {}
        
        for name, strategy in self.strategies.items():
            performance[name] = strategy.get_performance()
        
        return performance
    
    def update_strategy_performance(self, strategy_name: str, trade_result: Dict):
        """Update strategy performance after trade"""
        if strategy_name in self.strategies:
            self.strategies[strategy_name].update_performance(trade_result)


if __name__ == '__main__':
    print("📈 Trading Strategies Test\n")
    
    # Test individual strategies
    scalping = ScalpingStrategy()
    trend_following = TrendFollowingStrategy()
    mean_reversion = MeanReversionStrategy()
    
    # Sample market data
    sample_data = {
        'symbol': 'BTC/USDT',
        'price': 50000,
        'volume': 1000,
        'ohlcv': [
            [0, 49000, 51000, 48000, 50000, 1000],
            [0, 50000, 52000, 49000, 51000, 1100],
            [0, 51000, 53000, 50000, 52000, 1200],
            [0, 52000, 54000, 51000, 53000, 1300],
            [0, 53000, 55000, 52000, 54000, 1400]
        ],
        'spread_pct': 0.01
    }
    
    # Test scalping strategy
    scalping_signal = scalping.generate_signal(sample_data)
    print(f"Scalping Signal: {scalping_signal['signal']} (confidence: {scalping_signal['confidence']:.2f})")
    
    # Test trend following strategy
    trend_signal = trend_following.generate_signal(sample_data)
    print(f"Trend Following Signal: {trend_signal['signal']} (confidence: {trend_signal['confidence']:.2f})")
    
    # Test mean reversion strategy
    mean_rev_signal = mean_reversion.generate_signal(sample_data)
    print(f"Mean Reversion Signal: {mean_rev_signal['signal']} (confidence: {mean_rev_signal['confidence']:.2f})")
    
    # Test strategy manager
    manager = StrategyManager()
    combined_signal = manager.generate_combined_signal(sample_data)
    print(f"\nCombined Signal: {combined_signal['signal']} (confidence: {combined_signal['confidence']:.2f})")
    print(f"Active Strategies: {len(combined_signal['strategies'])}")
    
    print("\n✅ Trading strategies test completed!")