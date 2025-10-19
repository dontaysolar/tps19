#!/usr/bin/env python3
"""Health Monitor - System health monitoring"""
import psutil
from datetime import datetime
from typing import Dict

class HealthMonitorBot:
    def __init__(self):
        self.name = "Health_Monitor"
        self.version = "1.0.0"
        self.enabled = True
        
        self.health_checks = []
        self.alerts = []
        
        self.thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90
        }
        
        self.metrics = {'checks_performed': 0, 'alerts_raised': 0}
    
    def check_system_health(self) -> Dict:
        """Perform comprehensive health check"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Check thresholds
            issues = []
            if cpu_percent > self.thresholds['cpu_percent']:
                issues.append(f"High CPU: {cpu_percent:.1f}%")
            
            if memory_percent > self.thresholds['memory_percent']:
                issues.append(f"High Memory: {memory_percent:.1f}%")
            
            if disk_percent > self.thresholds['disk_percent']:
                issues.append(f"High Disk: {disk_percent:.1f}%")
            
            health_status = 'HEALTHY' if not issues else 'WARNING' if len(issues) < 2 else 'CRITICAL'
            
            if issues:
                self.metrics['alerts_raised'] += 1
                self.alerts.append({
                    'timestamp': datetime.now().isoformat(),
                    'issues': issues
                })
            
            self.metrics['checks_performed'] += 1
            
            return {
                'status': health_status,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk_percent,
                'disk_free_gb': disk.free / (1024**3),
                'issues': issues,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_bot_health(self, bot_instance) -> Dict:
        """Check individual bot health"""
        try:
            status = bot_instance.get_status()
            
            is_healthy = status.get('enabled', False)
            
            return {
                'bot_name': status.get('name', 'UNKNOWN'),
                'healthy': is_healthy,
                'status': status,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def get_recent_alerts(self, n: int = 10) -> list:
        """Get recent health alerts"""
        return self.alerts[-n:]
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'thresholds': self.thresholds,
            'total_alerts': len(self.alerts),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = HealthMonitorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
