#!/usr/bin/env python3
"""
Reinforcement Learning Bot
Q-Learning agent that learns optimal trading strategies
Learns from market interactions and maximizes reward
"""

import numpy as np
from datetime import datetime
from typing import Dict, List
import json

class ReinforcementLearningBot:
    def __init__(self):
        self.name = "Reinforcement_Learning"
        self.version = "1.0.0"
        self.enabled = True
        
        # RL parameters
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.2  # Exploration rate
        self.epsilon_decay = 0.995
        self.min_epsilon = 0.01
        
        # State space (simplified)
        self.n_states = 27  # 3^3 (trend, momentum, volatility = 3 levels each)
        self.n_actions = 3  # BUY, SELL, HOLD
        
        # Q-table
        self.q_table = np.zeros((self.n_states, self.n_actions))
        
        # Experience replay
        self.experiences = []
        self.max_experiences = 1000
        
        self.is_trained = False
        
        self.metrics = {
            'episodes_trained': 0,
            'total_reward': 0.0,
            'avg_reward': 0.0,
            'exploration_rate': self.epsilon,
            'actions_taken': {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        }
    
    def discretize_state(self, ohlcv: List) -> int:
        """Convert continuous market state to discrete state index"""
        if len(ohlcv) < 20:
            return 0
        
        closes = np.array([c[4] for c in ohlcv[-20:]])
        volumes = np.array([c[5] for c in ohlcv[-20:]])
        
        # Trend: -1 (down), 0 (sideways), 1 (up)
        sma_short = np.mean(closes[-5:])
        sma_long = np.mean(closes[-20:])
        trend = 1 if sma_short > sma_long * 1.02 else -1 if sma_short < sma_long * 0.98 else 0
        
        # Momentum: -1 (bearish), 0 (neutral), 1 (bullish)
        momentum_val = (closes[-1] - closes[-10]) / closes[-10]
        momentum = 1 if momentum_val > 0.02 else -1 if momentum_val < -0.02 else 0
        
        # Volatility: 0 (low), 1 (medium), 2 (high)
        volatility_val = np.std(closes) / np.mean(closes)
        volatility = 2 if volatility_val > 0.03 else 1 if volatility_val > 0.01 else 0
        
        # Convert to state index (3^0*trend + 3^1*momentum + 3^2*volatility)
        # Shift to positive indices
        state = (trend + 1) + (momentum + 1) * 3 + volatility * 9
        
        return min(state, self.n_states - 1)
    
    def choose_action(self, state: int, training: bool = False) -> int:
        """Choose action using epsilon-greedy policy"""
        if training and np.random.random() < self.epsilon:
            # Explore
            return np.random.randint(0, self.n_actions)
        else:
            # Exploit
            return np.argmax(self.q_table[state])
    
    def action_to_signal(self, action: int) -> str:
        """Convert action index to trading signal"""
        return ['BUY', 'SELL', 'HOLD'][action]
    
    def signal_to_action(self, signal: str) -> int:
        """Convert signal to action index"""
        return {'BUY': 0, 'SELL': 1, 'HOLD': 2}.get(signal, 2)
    
    def calculate_reward(self, action: int, price_change: float, volatility: float) -> float:
        """Calculate reward for action"""
        # Reward based on profitability
        if action == 0:  # BUY
            reward = price_change * 100  # Positive if price goes up
        elif action == 1:  # SELL
            reward = -price_change * 100  # Positive if price goes down
        else:  # HOLD
            reward = -0.01  # Small negative reward for inaction
        
        # Penalty for high volatility
        reward -= volatility * 10
        
        return reward
    
    def update_q_table(self, state: int, action: int, reward: float, next_state: int):
        """Update Q-table using Q-learning algorithm"""
        # Q-learning update rule
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.discount_factor * self.q_table[next_state, best_next_action]
        td_error = td_target - self.q_table[state, action]
        
        self.q_table[state, action] += self.learning_rate * td_error
    
    def train_on_historical_data(self, ohlcv: List, n_episodes: int = 50) -> Dict:
        """Train RL agent on historical market data"""
        if len(ohlcv) < 100:
            return {'error': 'Insufficient data'}
        
        total_rewards = []
        
        for episode in range(min(n_episodes, 20)):  # Limit for performance
            episode_reward = 0
            
            # Simulate trading on historical data
            for i in range(50, len(ohlcv) - 1):
                # Current state
                state = self.discretize_state(ohlcv[:i+1])
                
                # Choose action
                action = self.choose_action(state, training=True)
                
                # Execute action and observe reward
                current_price = ohlcv[i][4]
                next_price = ohlcv[i+1][4]
                price_change = (next_price - current_price) / current_price
                
                # Calculate volatility
                recent_closes = [c[4] for c in ohlcv[max(0, i-20):i+1]]
                volatility = np.std(recent_closes) / np.mean(recent_closes)
                
                # Calculate reward
                reward = self.calculate_reward(action, price_change, volatility)
                episode_reward += reward
                
                # Next state
                next_state = self.discretize_state(ohlcv[:i+2])
                
                # Update Q-table
                self.update_q_table(state, action, reward, next_state)
                
                # Store experience
                self.experiences.append({
                    'state': state,
                    'action': action,
                    'reward': reward,
                    'next_state': next_state
                })
                
                if len(self.experiences) > self.max_experiences:
                    self.experiences.pop(0)
            
            total_rewards.append(episode_reward)
            self.metrics['episodes_trained'] += 1
            
            # Decay epsilon
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        
        self.is_trained = True
        self.metrics['total_reward'] = float(np.sum(total_rewards))
        self.metrics['avg_reward'] = float(np.mean(total_rewards))
        self.metrics['exploration_rate'] = self.epsilon
        
        return {
            'trained': True,
            'episodes': len(total_rewards),
            'total_reward': self.metrics['total_reward'],
            'avg_reward': self.metrics['avg_reward'],
            'epsilon': self.epsilon,
            'experiences': len(self.experiences)
        }
    
    def predict(self, ohlcv: List) -> Dict:
        """Make trading decision using learned policy"""
        if len(ohlcv) < 20:
            return {'error': 'Insufficient data'}
        
        # Get current state
        state = self.discretize_state(ohlcv)
        
        # Choose best action (no exploration)
        action = self.choose_action(state, training=False)
        signal = self.action_to_signal(action)
        
        # Confidence based on Q-value
        q_values = self.q_table[state]
        best_q = q_values[action]
        q_range = np.max(q_values) - np.min(q_values)
        
        if q_range > 0:
            confidence = min(0.90, 0.60 + (best_q - np.min(q_values)) / q_range * 0.30)
        else:
            confidence = 0.60 if self.is_trained else 0.50
        
        # Update metrics
        self.metrics['actions_taken'][signal] += 1
        
        return {
            'signal': signal,
            'confidence': confidence,
            'q_value': float(best_q),
            'state': int(state),
            'is_trained': self.is_trained,
            'exploration_rate': self.epsilon,
            'reason': f"RL agent (Q-value: {best_q:.2f}) recommends {signal}",
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'is_trained': self.is_trained,
            'config': {
                'learning_rate': self.learning_rate,
                'discount_factor': self.discount_factor,
                'epsilon': self.epsilon
            },
            'metrics': self.metrics,
            'q_table_shape': self.q_table.shape,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = ReinforcementLearningBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
