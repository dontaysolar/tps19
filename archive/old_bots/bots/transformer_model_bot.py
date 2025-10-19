#!/usr/bin/env python3
"""
Transformer Model Bot
Attention-based architecture for market analysis
Multi-head self-attention for complex pattern recognition
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class TransformerModelBot:
    def __init__(self):
        self.name = "Transformer_Model"
        self.version = "1.0.0"
        self.enabled = True
        
        # Transformer config
        self.d_model = 128  # Model dimension
        self.n_heads = 8  # Attention heads
        self.n_layers = 4  # Transformer layers
        self.d_ff = 512  # Feed-forward dimension
        self.dropout = 0.1
        self.max_seq_length = 100
        
        self.is_trained = False
        self.attention_weights = None
        
        self.metrics = {
            'predictions_made': 0,
            'attention_patterns_detected': 0,
            'accuracy': 0.0
        }
    
    def scaled_dot_product_attention(self, Q, K, V):
        """Scaled dot-product attention mechanism"""
        d_k = Q.shape[-1]
        scores = (Q @ K.T) / np.sqrt(d_k)
        attention_weights = self._softmax(scores)
        output = attention_weights @ V
        return output, attention_weights
    
    def _softmax(self, x):
        """Softmax activation"""
        exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)
    
    def multi_head_attention(self, x):
        """Multi-head self-attention"""
        batch_size, seq_len, d_model = x.shape if len(x.shape) == 3 else (1, x.shape[0], x.shape[1])
        
        # Split into multiple heads (simplified)
        d_k = d_model // self.n_heads
        
        # For simplicity, use same x for Q, K, V
        attention_outputs = []
        all_attention_weights = []
        
        for h in range(self.n_heads):
            # Extract head-specific features
            start_idx = h * d_k
            end_idx = start_idx + d_k
            
            Q = x[:, :, start_idx:end_idx] if len(x.shape) == 3 else x[:, start_idx:end_idx]
            K = Q  # Self-attention
            V = Q
            
            # Attention
            output, weights = self.scaled_dot_product_attention(Q.reshape(-1, d_k), 
                                                                 K.reshape(-1, d_k),
                                                                 V.reshape(-1, d_k))
            attention_outputs.append(output)
            all_attention_weights.append(weights)
        
        # Concatenate heads
        multi_head_output = np.concatenate(attention_outputs, axis=-1)
        
        return multi_head_output, all_attention_weights
    
    def positional_encoding(self, seq_length, d_model):
        """Add positional information to input"""
        position = np.arange(seq_length)[:, np.newaxis]
        div_term = np.exp(np.arange(0, d_model, 2) * -(np.log(10000.0) / d_model))
        
        pos_encoding = np.zeros((seq_length, d_model))
        pos_encoding[:, 0::2] = np.sin(position * div_term)
        pos_encoding[:, 1::2] = np.cos(position * div_term)
        
        return pos_encoding
    
    def analyze_market_with_attention(self, ohlcv: List) -> Dict:
        """
        Analyze market using transformer attention mechanism
        Identifies which time periods are most important
        """
        if len(ohlcv) < 20:
            return {'error': 'Insufficient data'}
        
        # Extract features
        closes = np.array([c[4] for c in ohlcv[-min(self.max_seq_length, len(ohlcv)):]])
        volumes = np.array([c[5] for c in ohlcv[-min(self.max_seq_length, len(ohlcv)):]])
        
        # Normalize
        closes_norm = (closes - np.mean(closes)) / (np.std(closes) + 1e-8)
        volumes_norm = (volumes - np.mean(volumes)) / (np.std(volumes) + 1e-8)
        
        # Create feature matrix
        features = np.column_stack([
            closes_norm,
            volumes_norm,
            np.arange(len(closes)) / len(closes)  # Time feature
        ])
        
        # Pad to d_model dimensions
        if features.shape[1] < self.d_model:
            padding = np.zeros((features.shape[0], self.d_model - features.shape[1]))
            features = np.hstack([features, padding])
        
        # Add positional encoding
        pos_encoding = self.positional_encoding(len(features), self.d_model)
        features_with_pos = features[:self.d_model] + pos_encoding[:len(features)]
        
        # Multi-head attention
        attention_output, attention_weights = self.multi_head_attention(
            features_with_pos.reshape(1, -1, self.d_model)
        )
        
        # Analyze attention patterns
        # Find which time periods get most attention
        avg_attention = np.mean([w.mean(axis=0) for w in attention_weights], axis=0)
        important_periods = np.argsort(avg_attention)[-5:]  # Top 5 important periods
        
        # Generate prediction based on attention-weighted features
        weighted_closes = closes * avg_attention[:len(closes)]
        trend_strength = np.sum(weighted_closes[-10:] - weighted_closes[-20:-10]) / np.mean(closes)
        
        # Signal generation
        if trend_strength > 0.02:
            signal = 'BUY'
            confidence = min(0.85, 0.60 + abs(trend_strength) * 10)
        elif trend_strength < -0.02:
            signal = 'SELL'
            confidence = min(0.85, 0.60 + abs(trend_strength) * 10)
        else:
            signal = 'HOLD'
            confidence = 0.50
        
        self.metrics['predictions_made'] += 1
        self.metrics['attention_patterns_detected'] += len(important_periods)
        
        return {
            'signal': signal,
            'confidence': confidence,
            'trend_strength': float(trend_strength),
            'important_periods': important_periods.tolist(),
            'attention_focus': 'recent' if important_periods[-1] > len(closes) * 0.8 else 'historical',
            'reason': f"Transformer attention detects {signal} with {len(important_periods)} key periods",
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'config': {
                'd_model': self.d_model,
                'n_heads': self.n_heads,
                'n_layers': self.n_layers
            },
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = TransformerModelBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
