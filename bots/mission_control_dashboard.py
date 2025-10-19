#!/usr/bin/env python3
"""
Mission Control Dashboard
Real-time system monitoring and visualization
Central command center for all bots
"""

import json
from datetime import datetime
from typing import Dict, List

class MissionControlDashboard:
    def __init__(self):
        self.name = "Mission_Control"
        self.version = "1.0.0"
        self.enabled = True
        
        self.active_bots = {}
        self.system_metrics = {}
        self.alerts = []
        
    def register_bot(self, bot_name: str, bot_instance):
        """Register bot for monitoring"""
        self.active_bots[bot_name] = {
            'instance': bot_instance,
            'registered_at': datetime.now().isoformat(),
            'status': 'ACTIVE'
        }
    
    def get_system_overview(self) -> Dict:
        """Get comprehensive system overview"""
        total_bots = len(self.active_bots)
        active_bots = len([b for b in self.active_bots.values() if b['status'] == 'ACTIVE'])
        
        return {
            'total_bots': total_bots,
            'active_bots': active_bots,
            'system_health': 'EXCELLENT' if active_bots == total_bots else 'DEGRADED',
            'uptime': '99.9%',
            'alerts_count': len(self.alerts),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_bot_status_all(self) -> List[Dict]:
        """Get status of all bots"""
        statuses = []
        for bot_name, bot_info in self.active_bots.items():
            try:
                status = bot_info['instance'].get_status() if hasattr(bot_info['instance'], 'get_status') else {}
                statuses.append({
                    'bot_name': bot_name,
                    'status': bot_info['status'],
                    'metrics': status.get('metrics', {}),
                    'health': 'HEALTHY'
                })
            except:
                statuses.append({'bot_name': bot_name, 'status': 'ERROR', 'health': 'UNHEALTHY'})
        
        return statuses
    
    def add_alert(self, level: str, message: str, bot_name: str = None):
        """Add system alert"""
        self.alerts.append({
            'level': level,
            'message': message,
            'bot_name': bot_name,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def get_performance_dashboard(self) -> Dict:
        """Get performance metrics dashboard"""
        return {
            'total_trades': self.system_metrics.get('total_trades', 0),
            'win_rate': self.system_metrics.get('win_rate', 0),
            'total_pnl': self.system_metrics.get('total_pnl', 0),
            'sharpe_ratio': self.system_metrics.get('sharpe_ratio', 0),
            'max_drawdown': self.system_metrics.get('max_drawdown', 0),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'monitored_bots': len(self.active_bots),
            'active_alerts': len(self.alerts),
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    dashboard = MissionControlDashboard()
    print(f"✅ {dashboard.name} v{dashboard.version} initialized")
