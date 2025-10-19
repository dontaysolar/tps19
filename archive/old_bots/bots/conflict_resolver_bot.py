#!/usr/bin/env python3
"""
Conflict Resolver Bot
Prevents overlapping signals and bot conflicts
Part of APEX AI Trading System
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

class ConflictResolverBot:
    """Resolves conflicts between bot signals"""
    
    def __init__(self):
        self.name = "ConflictResolverBot"
        self.version = "1.0.0"
        
        self.config = {
            'max_concurrent_positions': 4,    # Max 4 positions at once
            'min_signal_agreement': 0.6,      # 60% bots must agree
            'position_priority': {            # Priority order
                'BTC/USDT': 1,
                'ETH/USDT': 2,
                'SOL/USDT': 3,
                'ADA/USDT': 4
            }
        }
        
        self.active_signals = {}
        self.active_positions = {}
        
        self.metrics = {
            'conflicts_detected': 0,
            'conflicts_resolved': 0,
            'signals_blocked': 0
        }
    
    def register_signal(self, bot_name: str, symbol: str, signal: str, confidence: float) -> str:
        """Register a trading signal from a bot"""
        signal_id = f"{bot_name}_{symbol}_{datetime.now().timestamp()}"
        
        if symbol not in self.active_signals:
            self.active_signals[symbol] = []
        
        self.active_signals[symbol].append({
            'signal_id': signal_id,
            'bot': bot_name,
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        })
        
        return signal_id
    
    def check_conflicts(self, symbol: str) -> Dict:
        """Check for conflicting signals on a symbol"""
        if symbol not in self.active_signals or not self.active_signals[symbol]:
            return {'conflict': False}
        
        signals = self.active_signals[symbol]
        
        # Count BUY vs SELL signals
        buy_signals = [s for s in signals if s['signal'] == 'BUY']
        sell_signals = [s for s in signals if s['signal'] == 'SELL']
        
        # Check for conflict
        if buy_signals and sell_signals:
            self.metrics['conflicts_detected'] += 1
            
            # Resolve by confidence
            buy_confidence = sum(s['confidence'] for s in buy_signals) / len(buy_signals)
            sell_confidence = sum(s['confidence'] for s in sell_signals) / len(sell_signals)
            
            if abs(buy_confidence - sell_confidence) < 0.1:
                # Too close, block trade
                return {
                    'conflict': True,
                    'resolution': 'BLOCK',
                    'reason': 'Signals too conflicted',
                    'buy_confidence': buy_confidence,
                    'sell_confidence': sell_confidence
                }
            
            # Use higher confidence
            resolution = 'BUY' if buy_confidence > sell_confidence else 'SELL'
            self.metrics['conflicts_resolved'] += 1
            
            return {
                'conflict': True,
                'resolution': resolution,
                'buy_confidence': buy_confidence,
                'sell_confidence': sell_confidence
            }
        
        return {'conflict': False}
    
    def can_open_position(self, symbol: str) -> Dict:
        """Check if new position can be opened"""
        # Check max concurrent positions
        if len(self.active_positions) >= self.config['max_concurrent_positions']:
            self.metrics['signals_blocked'] += 1
            return {
                'allowed': False,
                'reason': f"Max concurrent positions ({self.config['max_concurrent_positions']}) reached"
            }
        
        # Check if position already exists
        if symbol in self.active_positions:
            self.metrics['signals_blocked'] += 1
            return {
                'allowed': False,
                'reason': f'Position already open for {symbol}'
            }
        
        # Check for conflicts
        conflict_check = self.check_conflicts(symbol)
        if conflict_check.get('conflict') and conflict_check.get('resolution') == 'BLOCK':
            self.metrics['signals_blocked'] += 1
            return {
                'allowed': False,
                'reason': 'Signal conflict detected',
                'conflict_details': conflict_check
            }
        
        return {'allowed': True}
    
    def open_position(self, symbol: str, details: Dict) -> None:
        """Register an opened position"""
        self.active_positions[symbol] = {
            **details,
            'opened_at': datetime.now().isoformat()
        }
    
    def close_position(self, symbol: str) -> None:
        """Unregister a closed position"""
        if symbol in self.active_positions:
            del self.active_positions[symbol]
    
    def clear_old_signals(self, max_age_seconds: int = 300) -> None:
        """Clear signals older than max_age"""
        cutoff = datetime.now() - timedelta(seconds=max_age_seconds)
        
        for symbol in list(self.active_signals.keys()):
            self.active_signals[symbol] = [
                s for s in self.active_signals[symbol]
                if datetime.fromisoformat(s['timestamp']) > cutoff
            ]
            
            if not self.active_signals[symbol]:
                del self.active_signals[symbol]
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'active_positions': len(self.active_positions),
            'active_signals': sum(len(signals) for signals in self.active_signals.values()),
            'metrics': self.metrics,
            'config': self.config
        }

if __name__ == '__main__':
    bot = ConflictResolverBot()
    print("⚖️ Conflict Resolver Bot - Test Mode\n")
    
    # Simulate conflicting signals
    bot.register_signal('Bot1', 'BTC/USDT', 'BUY', 0.8)
    bot.register_signal('Bot2', 'BTC/USDT', 'SELL', 0.7)
    
    conflict = bot.check_conflicts('BTC/USDT')
    print(f"Conflict detected: {conflict['conflict']}")
    if conflict['conflict']:
        print(f"Resolution: {conflict['resolution']}")
    
    can_open = bot.can_open_position('BTC/USDT')
    print(f"\nCan open position: {can_open['allowed']}")
    if not can_open['allowed']:
        print(f"Reason: {can_open['reason']}")
