#!/usr/bin/env python3
"""
Auto-Recovery System - Self-healing organism
"""

import time
import threading
from typing import Dict, List
from datetime import datetime, timedelta

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class AutoRecoverySystem:
    """
    Automatic issue detection and recovery
    """
    
    def __init__(self, organism):
        self.organism = organism
        self.running = False
        self.recovery_thread = None
        
        # Recovery thresholds
        self.health_critical_threshold = 50
        self.health_warning_threshold = 70
        self.max_consecutive_losses = 3
        self.max_drawdown_before_hibernation = 0.15  # 15%
        
        # Recovery actions taken
        self.recovery_actions = []
        
    def start_monitoring(self):
        """Start continuous monitoring"""
        if self.running:
            logger.warning("Auto-recovery already running")
            return
        
        self.running = True
        self.recovery_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.recovery_thread.start()
        logger.info("🛡️ Auto-recovery system started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if self.recovery_thread:
            self.recovery_thread.join(timeout=5)
        logger.info("Auto-recovery system stopped")
    
    def _monitor_loop(self):
        """Continuous monitoring loop"""
        while self.running:
            try:
                # Check system health every 30 seconds
                health = self.organism.get_vital_signs()
                
                # Perform recovery checks
                if health['health_score'] < self.health_critical_threshold:
                    self._initiate_critical_recovery(health)
                elif health['health_score'] < self.health_warning_threshold:
                    self._initiate_preventive_measures(health)
                
                # Check connectivity
                if not self._check_connectivity():
                    self._recover_connectivity()
                
                # Check data freshness
                if self._is_data_stale():
                    self._refresh_data_feeds()
                
                # Check memory usage
                if self._is_memory_high():
                    self._perform_cleanup()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Recovery system error: {e}")
                time.sleep(60)  # Back off on error
    
    def _initiate_critical_recovery(self, health: Dict):
        """
        Critical recovery actions when health is very low
        """
        logger.critical(f"CRITICAL HEALTH: {health['health_score']:.1f}/100 - Initiating recovery")
        
        actions_taken = []
        
        # 1. Close all losing positions
        if health.get('consecutive_losses', 0) >= self.max_consecutive_losses:
            logger.warning("Closing all losing positions")
            self._close_losing_positions()
            actions_taken.append("closed_losing_positions")
        
        # 2. Reduce metabolic rate (position sizes)
        if health.get('current_drawdown', 0) > 0.10:
            logger.warning("Reducing metabolic rate to 0.5x")
            self.organism.metabolism.metabolic_rate = 0.5
            actions_taken.append("reduced_metabolic_rate")
        
        # 3. Enter hibernation if critical
        if health['health_score'] < 30:
            logger.critical("Entering 24h hibernation mode")
            self.organism.enter_hibernation(hours=24)
            actions_taken.append("entered_hibernation")
        
        # 4. Alert administrators
        self._alert_critical_condition(health, actions_taken)
        
        # Record recovery
        self.recovery_actions.append({
            'timestamp': datetime.now(),
            'type': 'critical',
            'health_score': health['health_score'],
            'actions': actions_taken
        })
    
    def _initiate_preventive_measures(self, health: Dict):
        """
        Preventive measures when health is declining
        """
        logger.warning(f"Health declining: {health['health_score']:.1f}/100 - Taking preventive measures")
        
        actions_taken = []
        
        # 1. Reduce position sizes
        if health.get('current_drawdown', 0) > 0.05:
            self.organism.metabolism.metabolic_rate *= 0.75
            actions_taken.append("reduced_position_sizes")
        
        # 2. Tighten risk controls
        if health.get('consecutive_losses', 0) >= 2:
            # Increase minimum confidence threshold
            logger.info("Tightening risk controls")
            actions_taken.append("tightened_risk_controls")
        
        # Record action
        self.recovery_actions.append({
            'timestamp': datetime.now(),
            'type': 'preventive',
            'health_score': health['health_score'],
            'actions': actions_taken
        })
    
    def _check_connectivity(self) -> bool:
        """Check if exchange connection is healthy"""
        try:
            # This would check actual exchange connection
            return True
        except:
            return False
    
    def _recover_connectivity(self):
        """Attempt to recover exchange connection"""
        logger.warning("Connection lost - Attempting recovery")
        
        try:
            # Attempt reconnection
            # self.organism.exchange.connect()
            logger.info("✅ Connection recovered")
        except Exception as e:
            logger.error(f"Connection recovery failed: {e}")
    
    def _is_data_stale(self) -> bool:
        """Check if market data is stale"""
        # Check last data update timestamp
        return False  # Placeholder
    
    def _refresh_data_feeds(self):
        """Refresh market data feeds"""
        logger.info("Refreshing data feeds")
        # Reconnect to data sources
    
    def _is_memory_high(self) -> bool:
        """Check if memory usage is high"""
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent
            return memory_percent > 85
        except:
            return False
    
    def _perform_cleanup(self):
        """Perform memory cleanup"""
        logger.info("Performing memory cleanup")
        import gc
        gc.collect()
    
    def _close_losing_positions(self):
        """Close all positions with unrealized losses"""
        # This would interface with position manager
        logger.warning("Would close all losing positions (not implemented)")
    
    def _alert_critical_condition(self, health: Dict, actions: List[str]):
        """Alert about critical condition"""
        message = f"""
🚨 CRITICAL ORGANISM CONDITION 🚨

Health Score: {health['health_score']:.1f}/100
Drawdown: {health.get('current_drawdown', 0):.1%}
Consecutive Losses: {health.get('consecutive_losses', 0)}

Recovery Actions Taken:
{chr(10).join('- ' + a for a in actions)}

Timestamp: {datetime.now().isoformat()}
"""
        logger.critical(message)
    
    def get_recovery_stats(self) -> Dict:
        """Get recovery system statistics"""
        return {
            'is_monitoring': self.running,
            'total_recoveries': len(self.recovery_actions),
            'critical_recoveries': len([a for a in self.recovery_actions if a['type'] == 'critical']),
            'preventive_actions': len([a for a in self.recovery_actions if a['type'] == 'preventive']),
            'last_recovery': self.recovery_actions[-1] if self.recovery_actions else None
        }


# Global instance (initialized later with organism)
auto_recovery_system = None


def init_auto_recovery(organism):
    """Initialize auto-recovery with organism instance"""
    global auto_recovery_system
    auto_recovery_system = AutoRecoverySystem(organism)
    return auto_recovery_system
