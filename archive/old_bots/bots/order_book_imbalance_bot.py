#!/usr/bin/env python3
"""Order Book Imbalance - Bid/ask pressure analysis"""
from datetime import datetime
from typing import Dict

class OrderBookImbalanceBot:
    def __init__(self):
        self.name = "Order_Book_Imbalance"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'analyses': 0, 'strong_signals': 0}
    
    def analyze_imbalance(self, bid_volume: float, ask_volume: float, 
                         bid_orders: int, ask_orders: int) -> Dict:
        """Analyze order book imbalance"""
        total_volume = bid_volume + ask_volume
        
        if total_volume == 0:
            return {'error': 'No volume data'}
        
        # Volume imbalance ratio
        imbalance_ratio = (bid_volume - ask_volume) / total_volume
        
        # Order count imbalance
        total_orders = bid_orders + ask_orders
        order_imbalance = (bid_orders - ask_orders) / total_orders if total_orders > 0 else 0
        
        # Average order sizes
        avg_bid_size = bid_volume / bid_orders if bid_orders > 0 else 0
        avg_ask_size = ask_volume / ask_orders if ask_orders > 0 else 0
        
        # Strong imbalance > 20%
        if imbalance_ratio > 0.20:
            signal, confidence = 'BUY', 0.80
            reason = f"Strong buy pressure - {imbalance_ratio*100:.1f}% bid imbalance"
            self.metrics['strong_signals'] += 1
        elif imbalance_ratio < -0.20:
            signal, confidence = 'SELL', 0.80
            reason = f"Strong sell pressure - {abs(imbalance_ratio)*100:.1f}% ask imbalance"
            self.metrics['strong_signals'] += 1
        elif imbalance_ratio > 0.10:
            signal, confidence = 'BUY', 0.65
            reason = "Moderate buy pressure"
        elif imbalance_ratio < -0.10:
            signal, confidence = 'SELL', 0.65
            reason = "Moderate sell pressure"
        else:
            signal, confidence = 'HOLD', 0.50
            reason = "Balanced order book"
        
        self.metrics['analyses'] += 1
        
        return {
            'bid_volume': bid_volume,
            'ask_volume': ask_volume,
            'imbalance_ratio': imbalance_ratio,
            'order_imbalance': order_imbalance,
            'avg_bid_size': avg_bid_size,
            'avg_ask_size': avg_ask_size,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = OrderBookImbalanceBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
