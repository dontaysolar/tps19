#!/usr/bin/env python3
"""Metrics Aggregator - Collect and aggregate all bot metrics"""
from datetime import datetime
from typing import Dict, List

class MetricsAggregatorBot:
    def __init__(self):
        self.name = "Metrics_Aggregator"
        self.version = "1.0.0"
        self.enabled = True
        
        self.bot_metrics = {}
        self.system_metrics = []
        
        self.metrics = {'collections': 0, 'bots_tracked': 0}
    
    def collect_bot_metrics(self, bot_instance) -> Dict:
        """Collect metrics from a bot"""
        try:
            status = bot_instance.get_status()
            bot_name = status.get('name', 'UNKNOWN')
            
            metrics = status.get('metrics', {})
            
            if bot_name not in self.bot_metrics:
                self.bot_metrics[bot_name] = []
                self.metrics['bots_tracked'] += 1
            
            self.bot_metrics[bot_name].append({
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics,
                'enabled': status.get('enabled', False)
            })
            
            # Keep last 100 snapshots per bot
            self.bot_metrics[bot_name] = self.bot_metrics[bot_name][-100:]
            
            self.metrics['collections'] += 1
            
            return {
                'bot_name': bot_name,
                'collected': True,
                'metrics': metrics
            }
        
        except Exception as e:
            return {'collected': False, 'error': str(e)}
    
    def collect_all_metrics(self, bot_instances: List) -> Dict:
        """Collect metrics from multiple bots"""
        results = []
        
        for bot in bot_instances:
            result = self.collect_bot_metrics(bot)
            results.append(result)
        
        return {
            'total_bots': len(bot_instances),
            'successful': sum([1 for r in results if r.get('collected', False)]),
            'failed': sum([1 for r in results if not r.get('collected', False)]),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_bot_metrics_history(self, bot_name: str, n: int = 20) -> List:
        """Get historical metrics for a bot"""
        if bot_name not in self.bot_metrics:
            return []
        
        return self.bot_metrics[bot_name][-n:]
    
    def get_system_summary(self) -> Dict:
        """Get system-wide metrics summary"""
        total_bots = len(self.bot_metrics)
        
        # Get latest metrics for each bot
        latest_metrics = {}
        for bot_name, history in self.bot_metrics.items():
            if history:
                latest_metrics[bot_name] = history[-1]['metrics']
        
        return {
            'total_bots_tracked': total_bots,
            'latest_metrics': latest_metrics,
            'total_collections': self.metrics['collections'],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'metrics': self.metrics,
            'bots_tracked': len(self.bot_metrics),
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = MetricsAggregatorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
