#!/usr/bin/env python3
"""
Virtues AI - Quality Control & Performance Monitoring
Ensures all systems operate at peak quality
Monitors and validates all bot performance
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class VirtuesAI:
    def __init__(self):
        self.name = "Virtues_AI"
        self.version = "1.0.0"
        self.enabled = True
        self.power_level = 89
        
        self.quality_standards = {
            'min_win_rate': 0.55,
            'min_profit_factor': 1.5,
            'max_drawdown': 15,
            'min_sharpe': 1.0
        }
        
        self.bot_evaluations = {}
        
        self.metrics = {
            'bots_evaluated': 0,
            'quality_checks': 0,
            'failures_detected': 0,
            'avg_quality_score': 0
        }
    
    def evaluate_bot_quality(self, bot_name: str, performance: Dict) -> Dict:
        """
        Evaluate bot performance against quality standards
        """
        evaluation = {
            'bot_name': bot_name,
            'quality_score': 0,
            'checks_passed': 0,
            'checks_failed': 0,
            'issues': [],
            'strengths': [],
            'recommendations': []
        }
        
        total_checks = 0
        passed_checks = 0
        
        # Check 1: Win Rate
        win_rate = performance.get('win_rate', 0)
        total_checks += 1
        if win_rate >= self.quality_standards['min_win_rate']:
            passed_checks += 1
            evaluation['strengths'].append(f"Good win rate: {win_rate:.1%}")
        else:
            evaluation['issues'].append(f"Low win rate: {win_rate:.1%} (target: {self.quality_standards['min_win_rate']:.1%})")
            evaluation['recommendations'].append("Review entry/exit criteria")
        
        # Check 2: Profit Factor
        profit_factor = performance.get('profit_factor', 0)
        total_checks += 1
        if profit_factor >= self.quality_standards['min_profit_factor']:
            passed_checks += 1
            evaluation['strengths'].append(f"Strong profit factor: {profit_factor:.2f}")
        else:
            evaluation['issues'].append(f"Weak profit factor: {profit_factor:.2f} (target: {self.quality_standards['min_profit_factor']:.2f})")
            evaluation['recommendations'].append("Optimize profit targets and stop losses")
        
        # Check 3: Max Drawdown
        max_dd = performance.get('max_drawdown_pct', 100)
        total_checks += 1
        if max_dd <= self.quality_standards['max_drawdown']:
            passed_checks += 1
            evaluation['strengths'].append(f"Acceptable drawdown: {max_dd:.1f}%")
        else:
            evaluation['issues'].append(f"High drawdown: {max_dd:.1f}% (limit: {self.quality_standards['max_drawdown']:.1f}%)")
            evaluation['recommendations'].append("Implement tighter risk controls")
            self.metrics['failures_detected'] += 1
        
        # Check 4: Sharpe Ratio
        sharpe = performance.get('sharpe_ratio', 0)
        total_checks += 1
        if sharpe >= self.quality_standards['min_sharpe']:
            passed_checks += 1
            evaluation['strengths'].append(f"Good risk-adjusted returns: Sharpe {sharpe:.2f}")
        else:
            evaluation['issues'].append(f"Poor risk-adjusted returns: Sharpe {sharpe:.2f} (target: {self.quality_standards['min_sharpe']:.2f})")
            evaluation['recommendations'].append("Reduce volatility or increase returns")
        
        # Check 5: Trade Frequency
        n_trades = performance.get('n_trades', 0)
        total_checks += 1
        if n_trades >= 20:
            passed_checks += 1
            evaluation['strengths'].append(f"Sufficient sample size: {n_trades} trades")
        else:
            evaluation['issues'].append(f"Insufficient trades: {n_trades} (need 20+)")
            evaluation['recommendations'].append("Collect more data before deployment")
        
        # Calculate quality score
        evaluation['quality_score'] = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        evaluation['checks_passed'] = passed_checks
        evaluation['checks_failed'] = total_checks - passed_checks
        
        # Overall assessment
        if evaluation['quality_score'] >= 80:
            evaluation['assessment'] = 'EXCELLENT'
            evaluation['deployment_ready'] = True
        elif evaluation['quality_score'] >= 60:
            evaluation['assessment'] = 'GOOD'
            evaluation['deployment_ready'] = True
        elif evaluation['quality_score'] >= 40:
            evaluation['assessment'] = 'FAIR'
            evaluation['deployment_ready'] = False
        else:
            evaluation['assessment'] = 'POOR'
            evaluation['deployment_ready'] = False
        
        # Store evaluation
        self.bot_evaluations[bot_name] = evaluation
        self.metrics['bots_evaluated'] += 1
        self.metrics['quality_checks'] += total_checks
        
        # Update average quality
        all_scores = [e['quality_score'] for e in self.bot_evaluations.values()]
        self.metrics['avg_quality_score'] = np.mean(all_scores) if all_scores else 0
        
        evaluation['timestamp'] = datetime.now().isoformat()
        return evaluation
    
    def monitor_system_health(self, system_metrics: Dict) -> Dict:
        """Monitor overall system health"""
        health_score = 100
        issues = []
        
        # Check CPU usage
        cpu_usage = system_metrics.get('cpu_percent', 0)
        if cpu_usage > 90:
            health_score -= 20
            issues.append(f"High CPU usage: {cpu_usage}%")
        elif cpu_usage > 75:
            health_score -= 10
            issues.append(f"Elevated CPU usage: {cpu_usage}%")
        
        # Check memory
        memory_usage = system_metrics.get('memory_percent', 0)
        if memory_usage > 90:
            health_score -= 20
            issues.append(f"High memory usage: {memory_usage}%")
        elif memory_usage > 75:
            health_score -= 10
            issues.append(f"Elevated memory usage: {memory_usage}%")
        
        # Check error rate
        error_rate = system_metrics.get('error_rate', 0)
        if error_rate > 0.05:
            health_score -= 25
            issues.append(f"High error rate: {error_rate:.1%}")
        elif error_rate > 0.02:
            health_score -= 10
            issues.append(f"Elevated error rate: {error_rate:.1%}")
        
        # Check API latency
        api_latency = system_metrics.get('api_latency_ms', 0)
        if api_latency > 1000:
            health_score -= 15
            issues.append(f"High API latency: {api_latency}ms")
        
        health_score = max(0, health_score)
        
        return {
            'health_score': health_score,
            'status': self._get_health_status(health_score),
            'issues': issues,
            'recommendations': self._get_health_recommendations(issues),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_health_status(self, score: float) -> str:
        if score >= 90:
            return 'EXCELLENT'
        elif score >= 75:
            return 'GOOD'
        elif score >= 60:
            return 'FAIR'
        elif score >= 40:
            return 'POOR'
        else:
            return 'CRITICAL'
    
    def _get_health_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        
        if any('CPU' in issue for issue in issues):
            recommendations.append("Optimize CPU-intensive operations")
            recommendations.append("Consider scaling horizontally")
        
        if any('memory' in issue for issue in issues):
            recommendations.append("Investigate memory leaks")
            recommendations.append("Implement garbage collection")
        
        if any('error' in issue for issue in issues):
            recommendations.append("Review error logs")
            recommendations.append("Implement better error handling")
        
        if any('latency' in issue for issue in issues):
            recommendations.append("Check network connectivity")
            recommendations.append("Optimize API calls")
        
        return recommendations
    
    def get_bot_rankings(self) -> List[Dict]:
        """Get bots ranked by quality score"""
        rankings = []
        
        for bot_name, evaluation in self.bot_evaluations.items():
            rankings.append({
                'bot_name': bot_name,
                'quality_score': evaluation['quality_score'],
                'assessment': evaluation['assessment'],
                'deployment_ready': evaluation['deployment_ready']
            })
        
        rankings.sort(key=lambda x: x['quality_score'], reverse=True)
        return rankings
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'power_level': self.power_level,
            'bots_under_supervision': len(self.bot_evaluations),
            'metrics': self.metrics,
            'quality_standards': self.quality_standards,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    ai = VirtuesAI()
    print(f"✅ {ai.name} v{ai.version} - Power Level: {ai.power_level}")
