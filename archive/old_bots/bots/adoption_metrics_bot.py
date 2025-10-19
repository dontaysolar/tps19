#!/usr/bin/env python3
"""Adoption Metrics Bot - User growth, transaction growth, merchant adoption"""
from datetime import datetime
from typing import Dict

class AdoptionMetricsBot:
    def __init__(self):
        self.name = "Adoption_Metrics"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'metrics_calculated': 0}
    
    def analyze_adoption(self, metrics: Dict) -> Dict:
        """Analyze adoption metrics"""
        active_users = metrics.get('active_users_30d', 0)
        user_growth_pct = metrics.get('user_growth_pct', 0)
        transaction_growth_pct = metrics.get('transaction_growth_pct', 0)
        merchant_acceptance = metrics.get('merchant_count', 0)
        
        adoption_score = 0
        
        # User growth
        if user_growth_pct > 50:
            adoption_score += 40
        elif user_growth_pct > 20:
            adoption_score += 25
        elif user_growth_pct > 5:
            adoption_score += 10
        
        # Transaction growth
        if transaction_growth_pct > 30:
            adoption_score += 30
        elif transaction_growth_pct > 10:
            adoption_score += 20
        
        # Merchant adoption
        if merchant_acceptance > 10000:
            adoption_score += 30
        elif merchant_acceptance > 1000:
            adoption_score += 15
        
        # Generate signal
        if adoption_score >= 70:
            signal, confidence = 'BUY', 0.80
            status = 'RAPID_ADOPTION'
        elif adoption_score >= 40:
            signal, confidence = 'BUY', 0.65
            status = 'GROWING_ADOPTION'
        elif adoption_score >= 20:
            signal, confidence = 'HOLD', 0.50
            status = 'SLOW_ADOPTION'
        else:
            signal, confidence = 'SELL', 0.60
            status = 'DECLINING_ADOPTION'
        
        self.metrics['metrics_calculated'] += 1
        
        return {
            'adoption_score': adoption_score,
            'status': status,
            'active_users': active_users,
            'user_growth_pct': user_growth_pct,
            'transaction_growth_pct': transaction_growth_pct,
            'merchant_acceptance': merchant_acceptance,
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = AdoptionMetricsBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
