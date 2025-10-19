#!/usr/bin/env python3
"""
Smart Order Router Bot
Routes orders to optimal execution venue
Considers: liquidity, fees, slippage, execution speed
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class SmartOrderRouterBot:
    def __init__(self):
        self.name = "Smart_Order_Router"
        self.version = "1.0.0"
        self.enabled = True
        
        self.venues = ['SPOT', 'FUTURES', 'DEX', 'OTC']
        
        self.metrics = {
            'orders_routed': 0,
            'optimal_venue_selected': 0,
            'fees_saved': 0
        }
    
    def find_optimal_venue(self,
                          order_size: float,
                          urgency: str = 'NORMAL',
                          venue_data: Dict = None) -> Dict:
        """
        Find optimal venue for order execution
        
        Args:
            order_size: Order size in USD
            urgency: 'LOW', 'NORMAL', 'HIGH', 'URGENT'
            venue_data: Real-time venue data
        """
        
        # Default venue characteristics
        default_venues = {
            'SPOT': {
                'liquidity': 100,
                'fee_pct': 0.1,
                'speed_ms': 100,
                'slippage_factor': 0.001
            },
            'FUTURES': {
                'liquidity': 150,
                'fee_pct': 0.05,
                'speed_ms': 50,
                'slippage_factor': 0.0015
            },
            'DEX': {
                'liquidity': 50,
                'fee_pct': 0.3,
                'speed_ms': 2000,
                'slippage_factor': 0.005
            },
            'OTC': {
                'liquidity': 200,
                'fee_pct': 0.02,
                'speed_ms': 5000,
                'slippage_factor': 0.0001
            }
        }
        
        venue_data = venue_data or default_venues
        
        # Score each venue
        venue_scores = {}
        
        for venue, data in venue_data.items():
            score = self._calculate_venue_score(
                order_size, data, urgency
            )
            venue_scores[venue] = score
        
        # Select best venue
        best_venue = max(venue_scores, key=venue_scores.get)
        best_score = venue_scores[best_venue]
        
        # Calculate expected costs
        costs = self._calculate_expected_costs(
            order_size, venue_data[best_venue]
        )
        
        self.metrics['orders_routed'] += 1
        self.metrics['optimal_venue_selected'] += 1
        
        return {
            'optimal_venue': best_venue,
            'score': best_score,
            'venue_scores': venue_scores,
            'expected_fee': costs['fee'],
            'expected_slippage': costs['slippage'],
            'total_cost': costs['total'],
            'execution_time_ms': venue_data[best_venue]['speed_ms'],
            'reason': self._get_routing_reason(best_venue, urgency, order_size),
            'timestamp': datetime.now().isoformat()
        }
    
    def split_order_across_venues(self,
                                  order_size: float,
                                  venue_data: Dict) -> Dict:
        """
        Split large order across multiple venues for optimal execution
        """
        allocations = {}
        
        # Calculate each venue's capacity
        total_liquidity = sum(v['liquidity'] for v in venue_data.values())
        
        for venue, data in venue_data.items():
            # Allocate proportional to liquidity, adjusted by fees
            liquidity_share = data['liquidity'] / total_liquidity
            fee_penalty = 1 - (data['fee_pct'] / 100)
            
            allocation_pct = liquidity_share * fee_penalty
            allocation_size = order_size * allocation_pct
            
            allocations[venue] = {
                'size': allocation_size,
                'percentage': allocation_pct * 100,
                'expected_fee': allocation_size * (data['fee_pct'] / 100),
                'expected_slippage': allocation_size * data['slippage_factor']
            }
        
        # Normalize allocations
        total_allocated = sum(a['size'] for a in allocations.values())
        for venue in allocations:
            allocations[venue]['size'] = (allocations[venue]['size'] / total_allocated) * order_size
        
        return {
            'split_order': True,
            'total_size': order_size,
            'num_venues': len(allocations),
            'allocations': allocations,
            'total_fees': sum(a['expected_fee'] for a in allocations.values()),
            'total_slippage': sum(a['expected_slippage'] for a in allocations.values()),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_venue_score(self,
                               order_size: float,
                               venue_data: Dict,
                               urgency: str) -> float:
        """Calculate venue suitability score"""
        
        # Liquidity score (important for large orders)
        liquidity_score = venue_data['liquidity'] / order_size if order_size > 0 else venue_data['liquidity']
        liquidity_score = min(liquidity_score, 100)
        
        # Fee score (lower is better)
        fee_score = 100 - (venue_data['fee_pct'] * 10)
        
        # Speed score (important for urgent orders)
        speed_score = 100 - (venue_data['speed_ms'] / 100)
        speed_score = max(speed_score, 0)
        
        # Slippage score (lower is better)
        slippage_score = 100 - (venue_data['slippage_factor'] * 10000)
        
        # Weight factors based on urgency
        if urgency == 'URGENT':
            weights = {'liquidity': 0.3, 'fee': 0.1, 'speed': 0.5, 'slippage': 0.1}
        elif urgency == 'HIGH':
            weights = {'liquidity': 0.3, 'fee': 0.2, 'speed': 0.3, 'slippage': 0.2}
        elif urgency == 'NORMAL':
            weights = {'liquidity': 0.3, 'fee': 0.3, 'speed': 0.2, 'slippage': 0.2}
        else:  # LOW
            weights = {'liquidity': 0.2, 'fee': 0.4, 'speed': 0.1, 'slippage': 0.3}
        
        total_score = (
            liquidity_score * weights['liquidity'] +
            fee_score * weights['fee'] +
            speed_score * weights['speed'] +
            slippage_score * weights['slippage']
        )
        
        return total_score
    
    def _calculate_expected_costs(self, order_size: float, venue_data: Dict) -> Dict:
        """Calculate expected execution costs"""
        fee = order_size * (venue_data['fee_pct'] / 100)
        slippage = order_size * venue_data['slippage_factor']
        total = fee + slippage
        
        return {
            'fee': fee,
            'slippage': slippage,
            'total': total,
            'total_pct': (total / order_size) * 100 if order_size > 0 else 0
        }
    
    def _get_routing_reason(self, venue: str, urgency: str, size: float) -> str:
        """Get human-readable routing reason"""
        reasons = {
            'SPOT': "Best liquidity and low fees for standard execution",
            'FUTURES': "Lowest fees and fast execution",
            'DEX': "Decentralized option with acceptable costs",
            'OTC': "Best for large orders with minimal slippage"
        }
        
        base_reason = reasons.get(venue, "Optimal venue selected")
        
        if urgency == 'URGENT':
            return f"{base_reason} - Prioritizing speed"
        elif size > 10000:
            return f"{base_reason} - Large order optimization"
        
        return base_reason
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'supported_venues': self.venues,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = SmartOrderRouterBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
