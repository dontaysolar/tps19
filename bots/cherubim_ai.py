#!/usr/bin/env python3
"""
Cherubim AI - Security and Anomaly Detection Bot
Advanced security monitoring and threat detection
Part of APEX AI Trading System - God-Level Layer
"""

import os
import sys
import json
import time
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
    import numpy as np
except ImportError:
    os.system("pip3 install --break-system-packages ccxt numpy -q")
    import ccxt
    import numpy as np

class CherubimAI:
    """
    Security and anomaly detection AI
    Features:
    - Real-time threat detection
    - Behavioral analysis
    - API security monitoring
    - Fraud prevention
    - System integrity checks
    """
    
    def __init__(self, exchange_config=None):
        self.name = "Cherubim_AI"
        self.version = "1.0.0"
        
        if exchange_config:
            self.exchange = ccxt.cryptocom(exchange_config)
        else:
            from dotenv import load_dotenv
            load_dotenv()
            self.exchange = ccxt.cryptocom({
                'apiKey': os.getenv('EXCHANGE_API_KEY'),
                'secret': os.getenv('EXCHANGE_API_SECRET'),
                'enableRateLimit': True
            })
        
        # Security configuration
        self.config = {
            'anomaly_threshold': 3.0,          # 3 standard deviations
            'max_failed_attempts': 5,           # Max failed API calls
            'suspicious_activity_window': 300,  # 5 minutes
            'api_key_rotation_days': 30,        # Rotate API keys every 30 days
            'unusual_volume_threshold': 5.0,    # 5x normal volume
            'price_manipulation_threshold': 0.1 # 10% price manipulation
        }
        
        # Security state
        self.security_state = {
            'failed_attempts': 0,
            'last_failed_attempt': None,
            'suspicious_activities': [],
            'api_key_age': 0,
            'last_security_check': None,
            'threat_level': 'LOW'
        }
        
        # Behavioral patterns
        self.behavioral_patterns = {
            'normal_volume': {},
            'normal_price_movements': {},
            'normal_trading_times': [],
            'api_usage_patterns': {}
        }
        
        # Security metrics
        self.metrics = {
            'threats_detected': 0,
            'anomalies_found': 0,
            'security_blocks': 0,
            'false_positives': 0,
            'api_key_rotations': 0,
            'last_security_scan': None
        }
        
        # Initialize security monitoring
        self._initialize_security_monitoring()
    
    def _initialize_security_monitoring(self):
        """Initialize security monitoring systems"""
        print(f"🛡️ {self.name} security monitoring initialized")
        
        # Set up baseline patterns
        self._establish_baseline_patterns()
        
        # Start continuous monitoring
        self._start_continuous_monitoring()
    
    def _establish_baseline_patterns(self):
        """Establish baseline behavioral patterns"""
        try:
            # Analyze historical data to establish baselines
            symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT']
            
            for symbol in symbols:
                # Get historical volume data
                ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=168)  # 1 week
                
                if len(ohlcv) > 0:
                    volumes = [candle[5] for candle in ohlcv]
                    prices = [candle[4] for candle in ohlcv]
                    
                    # Calculate baseline statistics
                    self.behavioral_patterns['normal_volume'][symbol] = {
                        'mean': statistics.mean(volumes),
                        'std': statistics.stdev(volumes) if len(volumes) > 1 else 0,
                        'percentile_95': np.percentile(volumes, 95) if len(volumes) > 0 else 0
                    }
                    
                    # Calculate price movement patterns
                    price_changes = [abs(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                    self.behavioral_patterns['normal_price_movements'][symbol] = {
                        'mean': statistics.mean(price_changes) if price_changes else 0,
                        'std': statistics.stdev(price_changes) if len(price_changes) > 1 else 0,
                        'max': max(price_changes) if price_changes else 0
                    }
            
            print("✅ Baseline patterns established")
            
        except Exception as e:
            print(f"❌ Error establishing baseline patterns: {e}")
    
    def _start_continuous_monitoring(self):
        """Start continuous security monitoring"""
        # This would run in a separate thread in production
        pass
    
    def detect_anomalies(self, symbol: str, data: Dict) -> List[Dict]:
        """Detect anomalies in trading data"""
        anomalies = []
        
        try:
            # Volume anomaly detection
            volume_anomaly = self._detect_volume_anomaly(symbol, data.get('volume', 0))
            if volume_anomaly:
                anomalies.append(volume_anomaly)
            
            # Price manipulation detection
            price_anomaly = self._detect_price_manipulation(symbol, data.get('price', 0))
            if price_anomaly:
                anomalies.append(price_anomaly)
            
            # Trading pattern anomaly
            pattern_anomaly = self._detect_trading_pattern_anomaly(symbol, data)
            if pattern_anomaly:
                anomalies.append(pattern_anomaly)
            
            # API usage anomaly
            api_anomaly = self._detect_api_anomaly(data)
            if api_anomaly:
                anomalies.append(api_anomaly)
            
            # Update metrics
            if anomalies:
                self.metrics['anomalies_found'] += len(anomalies)
                self.metrics['threats_detected'] += 1
            
        except Exception as e:
            print(f"❌ Anomaly detection error: {e}")
        
        return anomalies
    
    def _detect_volume_anomaly(self, symbol: str, volume: float) -> Optional[Dict]:
        """Detect unusual volume patterns"""
        if symbol not in self.behavioral_patterns['normal_volume']:
            return None
        
        baseline = self.behavioral_patterns['normal_volume'][symbol]
        
        # Check if volume exceeds normal range
        if volume > baseline['percentile_95'] * self.config['unusual_volume_threshold']:
            return {
                'type': 'volume_anomaly',
                'symbol': symbol,
                'severity': 'HIGH',
                'description': f'Unusual volume detected: {volume:.2f} vs normal {baseline["mean"]:.2f}',
                'volume': volume,
                'normal_mean': baseline['mean'],
                'threshold_exceeded': volume / baseline['mean'],
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def _detect_price_manipulation(self, symbol: str, price: float) -> Optional[Dict]:
        """Detect potential price manipulation"""
        if symbol not in self.behavioral_patterns['normal_price_movements']:
            return None
        
        # Get recent price data for comparison
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1m', limit=10)
            if len(ohlcv) < 2:
                return None
            
            recent_prices = [candle[4] for candle in ohlcv]
            price_changes = [abs(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] for i in range(1, len(recent_prices))]
            
            if not price_changes:
                return None
            
            avg_change = statistics.mean(price_changes)
            baseline = self.behavioral_patterns['normal_price_movements'][symbol]
            
            # Check for manipulation patterns
            if avg_change > baseline['mean'] * (1 + self.config['price_manipulation_threshold']):
                return {
                    'type': 'price_manipulation',
                    'symbol': symbol,
                    'severity': 'HIGH',
                    'description': f'Potential price manipulation detected',
                    'current_change': avg_change,
                    'normal_change': baseline['mean'],
                    'manipulation_ratio': avg_change / baseline['mean'],
                    'timestamp': datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"❌ Price manipulation detection error: {e}")
        
        return None
    
    def _detect_trading_pattern_anomaly(self, symbol: str, data: Dict) -> Optional[Dict]:
        """Detect unusual trading patterns"""
        # Check for rapid-fire trading
        current_time = datetime.now()
        
        # Add to suspicious activities
        self.security_state['suspicious_activities'].append({
            'symbol': symbol,
            'timestamp': current_time,
            'data': data
        })
        
        # Clean old activities
        cutoff_time = current_time - timedelta(seconds=self.config['suspicious_activity_window'])
        self.security_state['suspicious_activities'] = [
            activity for activity in self.security_state['suspicious_activities']
            if activity['timestamp'] > cutoff_time
        ]
        
        # Check for rapid trading
        recent_activities = [
            activity for activity in self.security_state['suspicious_activities']
            if activity['symbol'] == symbol
        ]
        
        if len(recent_activities) > 10:  # More than 10 trades in 5 minutes
            return {
                'type': 'rapid_trading',
                'symbol': symbol,
                'severity': 'MEDIUM',
                'description': f'Rapid trading detected: {len(recent_activities)} trades in {self.config["suspicious_activity_window"]}s',
                'trade_count': len(recent_activities),
                'time_window': self.config['suspicious_activity_window'],
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def _detect_api_anomaly(self, data: Dict) -> Optional[Dict]:
        """Detect API usage anomalies"""
        # Check for excessive API calls
        current_time = datetime.now()
        
        # Track API usage patterns
        if 'api_usage' not in self.behavioral_patterns:
            self.behavioral_patterns['api_usage'] = []
        
        self.behavioral_patterns['api_usage'].append(current_time)
        
        # Clean old API usage data
        cutoff_time = current_time - timedelta(minutes=1)
        self.behavioral_patterns['api_usage'] = [
            usage_time for usage_time in self.behavioral_patterns['api_usage']
            if usage_time > cutoff_time
        ]
        
        # Check for excessive API calls
        if len(self.behavioral_patterns['api_usage']) > 100:  # More than 100 calls per minute
            return {
                'type': 'api_abuse',
                'severity': 'HIGH',
                'description': f'Excessive API usage detected: {len(self.behavioral_patterns["api_usage"])} calls per minute',
                'api_calls_per_minute': len(self.behavioral_patterns['api_usage']),
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def monitor_api_security(self) -> Dict:
        """Monitor API security and key health"""
        security_status = {
            'api_key_health': 'GOOD',
            'rate_limiting': 'NORMAL',
            'authentication': 'VALID',
            'threats': []
        }
        
        try:
            # Check API key age
            if self.security_state['api_key_age'] > self.config['api_key_rotation_days']:
                security_status['api_key_health'] = 'NEEDS_ROTATION'
                security_status['threats'].append({
                    'type': 'api_key_aging',
                    'severity': 'MEDIUM',
                    'description': f'API key is {self.security_state["api_key_age"]} days old'
                })
            
            # Check for failed authentication attempts
            if self.security_state['failed_attempts'] > self.config['max_failed_attempts']:
                security_status['authentication'] = 'COMPROMISED'
                security_status['threats'].append({
                    'type': 'auth_failure',
                    'severity': 'HIGH',
                    'description': f'{self.security_state["failed_attempts"]} failed authentication attempts'
                })
            
            # Check rate limiting
            if len(self.behavioral_patterns.get('api_usage', [])) > 50:
                security_status['rate_limiting'] = 'HIGH'
                security_status['threats'].append({
                    'type': 'rate_limit_exceeded',
                    'severity': 'MEDIUM',
                    'description': 'API rate limit approaching'
                })
            
        except Exception as e:
            print(f"❌ API security monitoring error: {e}")
            security_status['api_key_health'] = 'ERROR'
        
        return security_status
    
    def generate_security_report(self) -> Dict:
        """Generate comprehensive security report"""
        try:
            # Get current threat level
            threat_level = self._calculate_threat_level()
            
            # Get recent anomalies
            recent_anomalies = self._get_recent_anomalies()
            
            # Get API security status
            api_security = self.monitor_api_security()
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'threat_level': threat_level,
                'security_metrics': self.metrics,
                'recent_anomalies': recent_anomalies,
                'api_security': api_security,
                'recommendations': self._generate_security_recommendations(threat_level),
                'system_status': self._get_system_status()
            }
            
            return report
            
        except Exception as e:
            print(f"❌ Security report generation error: {e}")
            return {}
    
    def _calculate_threat_level(self) -> str:
        """Calculate current threat level"""
        threat_score = 0
        
        # Factor in recent anomalies
        threat_score += self.metrics['anomalies_found'] * 2
        
        # Factor in failed attempts
        threat_score += self.security_state['failed_attempts'] * 3
        
        # Factor in suspicious activities
        threat_score += len(self.security_state['suspicious_activities']) * 1
        
        # Determine threat level
        if threat_score >= 20:
            return 'CRITICAL'
        elif threat_score >= 10:
            return 'HIGH'
        elif threat_score >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_recent_anomalies(self) -> List[Dict]:
        """Get recent security anomalies"""
        # This would return recent anomalies from the security log
        return []
    
    def _generate_security_recommendations(self, threat_level: str) -> List[str]:
        """Generate security recommendations based on threat level"""
        recommendations = []
        
        if threat_level == 'CRITICAL':
            recommendations.extend([
                'Immediately halt all trading activities',
                'Rotate all API keys',
                'Review all recent transactions',
                'Enable additional security monitoring'
            ])
        elif threat_level == 'HIGH':
            recommendations.extend([
                'Increase monitoring frequency',
                'Review API usage patterns',
                'Consider rotating API keys',
                'Implement additional authentication'
            ])
        elif threat_level == 'MEDIUM':
            recommendations.extend([
                'Monitor for additional anomalies',
                'Review trading patterns',
                'Update security configurations'
            ])
        else:
            recommendations.extend([
                'Continue normal monitoring',
                'Regular security maintenance'
            ])
        
        return recommendations
    
    def _get_system_status(self) -> Dict:
        """Get overall system security status"""
        return {
            'monitoring_active': True,
            'last_scan': self.metrics['last_security_scan'],
            'threats_blocked': self.metrics['security_blocks'],
            'false_positive_rate': self.metrics['false_positives'] / max(self.metrics['anomalies_found'], 1),
            'uptime': '100%'  # This would be calculated in production
        }
    
    def get_status(self) -> Dict:
        """Get Cherubim AI status"""
        return {
            'name': self.name,
            'version': self.version,
            'threat_level': self._calculate_threat_level(),
            'metrics': self.metrics,
            'security_state': self.security_state,
            'config': self.config
        }


if __name__ == '__main__':
    bot = CherubimAI()
    print("🛡️ Cherubim AI - Security Bot\n")
    
    # Test anomaly detection
    test_data = {
        'symbol': 'BTC/USDT',
        'volume': 1000000,  # Unusually high volume
        'price': 50000,
        'api_usage': True
    }
    
    anomalies = bot.detect_anomalies('BTC/USDT', test_data)
    print(f"Anomalies detected: {len(anomalies)}")
    for anomaly in anomalies:
        print(f"  {anomaly['type']}: {anomaly['description']}")
    
    # Test API security monitoring
    api_security = bot.monitor_api_security()
    print(f"\nAPI Security Status: {api_security['api_key_health']}")
    
    # Generate security report
    report = bot.generate_security_report()
    print(f"\nThreat Level: {report['threat_level']}")
    print(f"Recommendations: {len(report['recommendations'])}")
    
    # Show status
    status = bot.get_status()
    print(f"\nSecurity Metrics:")
    print(f"  Threats Detected: {status['metrics']['threats_detected']}")
    print(f"  Anomalies Found: {status['metrics']['anomalies_found']}")
    print(f"  Security Blocks: {status['metrics']['security_blocks']}")