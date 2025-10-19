#!/usr/bin/env python3
"""
Principalities AI - Regional & Exchange Optimization
Manages trading across different exchanges and regions
Optimizes for local market conditions
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class PrincipalitiesAI:
    def __init__(self):
        self.name = "Principalities_AI"
        self.version = "1.0.0"
        self.enabled = True
        self.power_level = 87
        
        self.regions = {
            'US': {'timezone': 'America/New_York', 'active_hours': (9, 16)},
            'EU': {'timezone': 'Europe/London', 'active_hours': (8, 16)},
            'ASIA': {'timezone': 'Asia/Tokyo', 'active_hours': (9, 15)}
        }
        
        self.exchanges = {}
        
        self.metrics = {
            'exchanges_monitored': 0,
            'arbitrage_opportunities': 0,
            'regional_optimizations': 0
        }
    
    def register_exchange(self, exchange_name: str, region: str, fees: Dict):
        """Register an exchange for monitoring"""
        self.exchanges[exchange_name] = {
            'region': region,
            'fees': fees,
            'performance': {},
            'active': True
        }
        self.metrics['exchanges_monitored'] += 1
    
    def find_arbitrage_opportunities(self, prices_by_exchange: Dict[str, float]) -> Dict:
        """
        Find arbitrage opportunities across exchanges
        
        Args:
            prices_by_exchange: {exchange_name: price}
        """
        if len(prices_by_exchange) < 2:
            return {'opportunities': []}
        
        opportunities = []
        
        # Compare all exchange pairs
        exchanges = list(prices_by_exchange.keys())
        for i, exchange1 in enumerate(exchanges):
            for exchange2 in exchanges[i+1:]:
                price1 = prices_by_exchange[exchange1]
                price2 = prices_by_exchange[exchange2]
                
                # Calculate spread
                spread_pct = abs(price1 - price2) / min(price1, price2) * 100
                
                # Get fees
                fees1 = self.exchanges.get(exchange1, {}).get('fees', {}).get('taker', 0.001)
                fees2 = self.exchanges.get(exchange2, {}).get('fees', {}).get('taker', 0.001)
                total_fees = (fees1 + fees2) * 100
                
                # Net profit after fees
                net_profit = spread_pct - total_fees
                
                if net_profit > 0.1:  # Profitable after fees
                    buy_exchange = exchange1 if price1 < price2 else exchange2
                    sell_exchange = exchange2 if price1 < price2 else exchange1
                    
                    opportunities.append({
                        'buy_exchange': buy_exchange,
                        'sell_exchange': sell_exchange,
                        'buy_price': min(price1, price2),
                        'sell_price': max(price1, price2),
                        'spread_pct': spread_pct,
                        'fees_pct': total_fees,
                        'net_profit_pct': net_profit,
                        'profitability': 'HIGH' if net_profit > 0.5 else 'MEDIUM' if net_profit > 0.2 else 'LOW'
                    })
                    
                    self.metrics['arbitrage_opportunities'] += 1
        
        # Sort by profitability
        opportunities.sort(key=lambda x: x['net_profit_pct'], reverse=True)
        
        return {
            'opportunities': opportunities,
            'count': len(opportunities),
            'best_opportunity': opportunities[0] if opportunities else None,
            'timestamp': datetime.now().isoformat()
        }
    
    def optimize_for_region(self, region: str, current_hour: int) -> Dict:
        """
        Optimize trading for specific region
        """
        if region not in self.regions:
            return {'error': f'Unknown region: {region}'}
        
        region_info = self.regions[region]
        active_start, active_end = region_info['active_hours']
        
        # Check if within active hours
        is_active_hours = active_start <= current_hour < active_end
        
        # Calculate market activity score
        if is_active_hours:
            # Peak hours (middle of session)
            mid_point = (active_start + active_end) / 2
            distance_from_peak = abs(current_hour - mid_point)
            activity_score = 100 - (distance_from_peak / (active_end - active_start) * 50)
        else:
            # Off hours
            activity_score = 20
        
        # Generate recommendations
        if activity_score >= 80:
            intensity = 'MAXIMUM'
            position_size = 'FULL'
            strategy = 'AGGRESSIVE'
        elif activity_score >= 60:
            intensity = 'HIGH'
            position_size = 'NORMAL'
            strategy = 'MODERATE'
        elif activity_score >= 40:
            intensity = 'MEDIUM'
            position_size = 'REDUCED'
            strategy = 'CONSERVATIVE'
        else:
            intensity = 'LOW'
            position_size = 'MINIMAL'
            strategy = 'DEFENSIVE'
        
        self.metrics['regional_optimizations'] += 1
        
        return {
            'region': region,
            'current_hour': current_hour,
            'is_active_hours': is_active_hours,
            'activity_score': activity_score,
            'intensity': intensity,
            'recommended_position_size': position_size,
            'recommended_strategy': strategy,
            'timezone': region_info['timezone'],
            'timestamp': datetime.now().isoformat()
        }
    
    def select_best_exchange(self, asset_pair: str, order_size: float) -> Dict:
        """
        Select optimal exchange for trading
        """
        if not self.exchanges:
            return {'error': 'No exchanges registered'}
        
        scores = {}
        
        for exchange_name, info in self.exchanges.items():
            if not info.get('active', True):
                continue
            
            score = 100
            
            # Fee consideration (lower is better)
            taker_fee = info['fees'].get('taker', 0.001)
            score -= taker_fee * 1000  # Penalty for high fees
            
            # Performance consideration
            performance = info.get('performance', {})
            uptime = performance.get('uptime', 95)
            score += (uptime - 95) * 2  # Bonus for high uptime
            
            latency = performance.get('latency_ms', 100)
            score -= latency / 10  # Penalty for high latency
            
            scores[exchange_name] = max(0, score)
        
        # Select best
        best_exchange = max(scores.items(), key=lambda x: x[1]) if scores else None
        
        return {
            'best_exchange': best_exchange[0] if best_exchange else None,
            'score': best_exchange[1] if best_exchange else 0,
            'all_scores': scores,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'power_level': self.power_level,
            'regions': list(self.regions.keys()),
            'exchanges': list(self.exchanges.keys()),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    ai = PrincipalitiesAI()
    print(f"✅ {ai.name} v{ai.version} - Power Level: {ai.power_level}")
