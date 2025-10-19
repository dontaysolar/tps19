#!/usr/bin/env python3
"""Auto-Rebalance Scheduler - Automated portfolio rebalancing"""
from datetime import datetime, timedelta
from typing import Dict

class AutoRebalanceSchedulerBot:
    def __init__(self):
        self.name = "Auto_Rebalance_Scheduler"
        self.version = "1.0.0"
        self.enabled = True
        
        self.rebalance_frequency_days = 7
        self.last_rebalance = None
        self.next_rebalance = None
        
        self.metrics = {'rebalances_scheduled': 0, 'rebalances_executed': 0}
    
    def schedule_next_rebalance(self) -> Dict:
        """Schedule next rebalancing"""
        if self.last_rebalance:
            next_time = datetime.fromisoformat(self.last_rebalance) + timedelta(days=self.rebalance_frequency_days)
        else:
            next_time = datetime.now() + timedelta(days=self.rebalance_frequency_days)
        
        self.next_rebalance = next_time.isoformat()
        self.metrics['rebalances_scheduled'] += 1
        
        return {
            'scheduled': True,
            'next_rebalance': self.next_rebalance,
            'days_until': self.rebalance_frequency_days,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_rebalance_due(self) -> Dict:
        """Check if rebalance is due"""
        if not self.next_rebalance:
            self.schedule_next_rebalance()
            return {'due': False, 'message': 'First rebalance scheduled'}
        
        next_time = datetime.fromisoformat(self.next_rebalance)
        is_due = datetime.now() >= next_time
        
        if is_due:
            hours_overdue = (datetime.now() - next_time).total_seconds() / 3600
            return {
                'due': True,
                'hours_overdue': hours_overdue,
                'next_rebalance': self.next_rebalance
            }
        
        time_remaining = next_time - datetime.now()
        
        return {
            'due': False,
            'hours_remaining': time_remaining.total_seconds() / 3600,
            'next_rebalance': self.next_rebalance
        }
    
    def execute_rebalance(self, portfolio_data: Dict) -> Dict:
        """Execute portfolio rebalancing"""
        self.last_rebalance = datetime.now().isoformat()
        self.metrics['rebalances_executed'] += 1
        
        # Schedule next
        self.schedule_next_rebalance()
        
        return {
            'executed': True,
            'execution_time': self.last_rebalance,
            'next_scheduled': self.next_rebalance,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'frequency_days': self.rebalance_frequency_days,
            'last_rebalance': self.last_rebalance,
            'next_rebalance': self.next_rebalance,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = AutoRebalanceSchedulerBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
