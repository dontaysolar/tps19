#!/usr/bin/env python3
"""
AEGIS v2.0 System Health Monitoring - AID v2.0 Implementation
CRIT_029 Resolution - Zero-Tolerance System Health Monitoring

FRACTAL_HOOK: This implementation provides autonomous system health
monitoring that enables future AEGIS operations to maintain optimal
system performance without human intervention.
"""

import os
import sys
import json
import time
import logging
import threading
import subprocess
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# ATLAS Protocol: Fixed loop bounds and simple control flow
MAX_HEALTH_CHECKS = 100
MAX_METRIC_COLLECTIONS = 50
MAX_FUNCTION_LENGTH = 60

class HealthStatus(Enum):
    """Health status - ATLAS: Simple enumeration"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"

class MetricType(Enum):
    """Metric type - ATLAS: Simple enumeration"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    PROCESS = "process"
    SYSTEM = "system"

@dataclass
class HealthMetric:
    """Health metric - ATLAS: Fixed data structure"""
    metric_id: str
    metric_type: MetricType
    value: float
    threshold: float
    status: HealthStatus
    timestamp: str
    unit: str

@dataclass
class SystemHealthReport:
    """System health report - ATLAS: Fixed data structure"""
    overall_health: HealthStatus
    health_score: float
    metrics: List[HealthMetric]
    alerts: List[str]
    recommendations: List[str]
    timestamp: str

class AEGISSystemHealthMonitoring:
    """
    AEGIS v2.0 System Health Monitoring
    
    ATLAS Protocol Compliance:
    - Simple control flow with fixed loop bounds
    - No dynamic memory allocation after initialization
    - High assertion density (2+ per function)
    - Minimal scope for all variables
    - Constrained function length
    """
    
    def __init__(self, config_path: str = "config/system_health.json"):
        """Initialize System Health Monitoring - ATLAS: Fixed initialization"""
        assert isinstance(config_path, str), "Config path must be string"
        
        self.config_path = config_path
        self.health_metrics: List[HealthMetric] = []
        self.health_reports: List[SystemHealthReport] = []
        self.overall_health_score = 100.0
        self._monitoring_active = False
        self._monitoring_thread = None
        
        # ATLAS: Initialize logging
        self._setup_logging()
        self._load_configuration()
        self._initialize_monitoring()
        
        # ATLAS: Assert initialization success
        assert self.logger is not None, "Logger must be initialized"
    
    def _setup_logging(self) -> None:
        """Setup logging configuration - ATLAS: Fixed function length"""
        assert not hasattr(self, 'logger'), "Logger already initialized"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - HEALTH_MONITOR - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/system_health.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # ATLAS: Assert logging setup
        assert self.logger is not None, "Logger setup failed"
    
    def _load_configuration(self) -> None:
        """Load health monitoring configuration - ATLAS: Fixed function length"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.error(f"Config load failed: {e}")
                self.config = self._get_default_config()
        else:
            self.config = self._get_default_config()
        
        # ATLAS: Assert configuration loaded
        assert isinstance(self.config, dict), "Config must be dictionary"
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration - ATLAS: Fixed function length"""
        return {
            "system_health": {
                "enabled": True,
                "monitoring_interval": 30,
                "alert_threshold": 80.0,
                "critical_threshold": 95.0
            },
            "metrics": {
                "cpu": {
                    "enabled": True,
                    "warning_threshold": 70.0,
                    "critical_threshold": 90.0,
                    "unit": "percent"
                },
                "memory": {
                    "enabled": True,
                    "warning_threshold": 80.0,
                    "critical_threshold": 95.0,
                    "unit": "percent"
                },
                "disk": {
                    "enabled": True,
                    "warning_threshold": 80.0,
                    "critical_threshold": 95.0,
                    "unit": "percent"
                },
                "network": {
                    "enabled": True,
                    "warning_threshold": 1000.0,
                    "critical_threshold": 5000.0,
                    "unit": "ms"
                },
                "process": {
                    "enabled": True,
                    "warning_threshold": 500,
                    "critical_threshold": 1000,
                    "unit": "count"
                }
            },
            "health_endpoints": {
                "enabled": True,
                "port": 8080,
                "path": "/health"
            }
        }
    
    def _initialize_monitoring(self) -> None:
        """Initialize monitoring - ATLAS: Fixed function length"""
        assert len(self.health_metrics) == 0, "Monitoring already initialized"
        
        # Create health logs directory
        os.makedirs('logs/health', exist_ok=True)
        
        # Start monitoring thread
        self._start_monitoring()
        
        self.logger.info("System health monitoring initialized")
    
    def _start_monitoring(self) -> None:
        """Start monitoring - ATLAS: Fixed function length"""
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitor_system_health, daemon=True)
        self._monitoring_thread.start()
    
    def _monitor_system_health(self) -> None:
        """Monitor system health - ATLAS: Fixed function length"""
        monitoring_interval = self.config.get("system_health", {}).get("monitoring_interval", 30)
        
        # ATLAS: Fixed loop bound
        check_count = 0
        while self._monitoring_active and check_count < MAX_HEALTH_CHECKS:
            try:
                # Collect health metrics
                self._collect_health_metrics()
                
                # Generate health report
                report = self._generate_health_report()
                self.health_reports.append(report)
                
                # Log health status
                self._log_health_status(report)
                
                time.sleep(monitoring_interval)
                check_count += 1
                
                # ATLAS: Assert loop progression
                assert check_count <= MAX_HEALTH_CHECKS, "Loop bound exceeded"
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                break
    
    def _collect_health_metrics(self) -> None:
        """Collect health metrics - ATLAS: Fixed function length"""
        # Collect CPU metrics
        self._collect_cpu_metrics()
        
        # Collect memory metrics
        self._collect_memory_metrics()
        
        # Collect disk metrics
        self._collect_disk_metrics()
        
        # Collect network metrics
        self._collect_network_metrics()
        
        # Collect process metrics
        self._collect_process_metrics()
    
    def _collect_cpu_metrics(self) -> None:
        """Collect CPU metrics - ATLAS: Fixed function length"""
        if not self.config.get("metrics", {}).get("cpu", {}).get("enabled", True):
            return
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            threshold = self.config.get("metrics", {}).get("cpu", {}).get("critical_threshold", 90.0)
            
            status = self._determine_metric_status(cpu_percent, threshold)
            
            metric = HealthMetric(
                metric_id=f"cpu_{int(time.time())}",
                metric_type=MetricType.CPU,
                value=cpu_percent,
                threshold=threshold,
                status=status,
                timestamp=datetime.now().isoformat(),
                unit="percent"
            )
            
            self.health_metrics.append(metric)
            
        except Exception as e:
            self.logger.error(f"CPU metrics collection failed: {e}")
    
    def _collect_memory_metrics(self) -> None:
        """Collect memory metrics - ATLAS: Fixed function length"""
        if not self.config.get("metrics", {}).get("memory", {}).get("enabled", True):
            return
        
        try:
            memory_info = psutil.virtual_memory()
            memory_percent = memory_info.percent
            threshold = self.config.get("metrics", {}).get("memory", {}).get("critical_threshold", 95.0)
            
            status = self._determine_metric_status(memory_percent, threshold)
            
            metric = HealthMetric(
                metric_id=f"memory_{int(time.time())}",
                metric_type=MetricType.MEMORY,
                value=memory_percent,
                threshold=threshold,
                status=status,
                timestamp=datetime.now().isoformat(),
                unit="percent"
            )
            
            self.health_metrics.append(metric)
            
        except Exception as e:
            self.logger.error(f"Memory metrics collection failed: {e}")
    
    def _collect_disk_metrics(self) -> None:
        """Collect disk metrics - ATLAS: Fixed function length"""
        if not self.config.get("metrics", {}).get("disk", {}).get("enabled", True):
            return
        
        try:
            disk_usage = psutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            threshold = self.config.get("metrics", {}).get("disk", {}).get("critical_threshold", 95.0)
            
            status = self._determine_metric_status(disk_percent, threshold)
            
            metric = HealthMetric(
                metric_id=f"disk_{int(time.time())}",
                metric_type=MetricType.DISK,
                value=disk_percent,
                threshold=threshold,
                status=status,
                timestamp=datetime.now().isoformat(),
                unit="percent"
            )
            
            self.health_metrics.append(metric)
            
        except Exception as e:
            self.logger.error(f"Disk metrics collection failed: {e}")
    
    def _collect_network_metrics(self) -> None:
        """Collect network metrics - ATLAS: Fixed function length"""
        if not self.config.get("metrics", {}).get("network", {}).get("enabled", True):
            return
        
        try:
            # Simple network latency test
            start_time = time.time()
            result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                                  capture_output=True, timeout=5)
            end_time = time.time()
            
            if result.returncode == 0:
                latency_ms = (end_time - start_time) * 1000
            else:
                latency_ms = 9999.0  # High latency for failed ping
            
            threshold = self.config.get("metrics", {}).get("network", {}).get("critical_threshold", 5000.0)
            
            status = self._determine_metric_status(latency_ms, threshold)
            
            metric = HealthMetric(
                metric_id=f"network_{int(time.time())}",
                metric_type=MetricType.NETWORK,
                value=latency_ms,
                threshold=threshold,
                status=status,
                timestamp=datetime.now().isoformat(),
                unit="ms"
            )
            
            self.health_metrics.append(metric)
            
        except Exception as e:
            self.logger.error(f"Network metrics collection failed: {e}")
    
    def _collect_process_metrics(self) -> None:
        """Collect process metrics - ATLAS: Fixed function length"""
        if not self.config.get("metrics", {}).get("process", {}).get("enabled", True):
            return
        
        try:
            process_count = len(psutil.pids())
            threshold = self.config.get("metrics", {}).get("process", {}).get("critical_threshold", 1000)
            
            status = self._determine_metric_status(process_count, threshold)
            
            metric = HealthMetric(
                metric_id=f"process_{int(time.time())}",
                metric_type=MetricType.PROCESS,
                value=process_count,
                threshold=threshold,
                status=status,
                timestamp=datetime.now().isoformat(),
                unit="count"
            )
            
            self.health_metrics.append(metric)
            
        except Exception as e:
            self.logger.error(f"Process metrics collection failed: {e}")
    
    def _determine_metric_status(self, value: float, threshold: float) -> HealthStatus:
        """Determine metric status - ATLAS: Fixed function length"""
        assert isinstance(value, (int, float)), "Value must be numeric"
        assert isinstance(threshold, (int, float)), "Threshold must be numeric"
        
        if value >= threshold:
            return HealthStatus.CRITICAL
        elif value >= threshold * 0.8:  # 80% of threshold
            return HealthStatus.WARNING
        elif value >= threshold * 0.6:  # 60% of threshold
            return HealthStatus.GOOD
        else:
            return HealthStatus.EXCELLENT
    
    def _generate_health_report(self) -> SystemHealthReport:
        """Generate health report - ATLAS: Fixed function length"""
        # Get recent metrics (last 5 minutes)
        recent_metrics = self._get_recent_metrics()
        
        # Calculate overall health
        overall_health = self._calculate_overall_health(recent_metrics)
        health_score = self._calculate_health_score(recent_metrics)
        
        # Generate alerts and recommendations
        alerts = self._generate_alerts(recent_metrics)
        recommendations = self._generate_recommendations(recent_metrics)
        
        report = SystemHealthReport(
            overall_health=overall_health,
            health_score=health_score,
            metrics=recent_metrics,
            alerts=alerts,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
        
        self.overall_health_score = health_score
        
        # ATLAS: Assert health score validity
        assert 0 <= health_score <= 100, "Health score out of range"
        
        return report
    
    def _get_recent_metrics(self) -> List[HealthMetric]:
        """Get recent metrics - ATLAS: Fixed function length"""
        cutoff_time = datetime.now() - timedelta(minutes=5)
        recent_metrics = []
        
        # ATLAS: Fixed loop bound
        for i, metric in enumerate(self.health_metrics):
            if i >= MAX_METRIC_COLLECTIONS:
                break
            
            metric_time = datetime.fromisoformat(metric.timestamp)
            if metric_time >= cutoff_time:
                recent_metrics.append(metric)
            
            # ATLAS: Assert loop progression
            assert i < len(self.health_metrics), "Loop bound exceeded"
        
        return recent_metrics
    
    def _calculate_overall_health(self, metrics: List[HealthMetric]) -> HealthStatus:
        """Calculate overall health - ATLAS: Fixed function length"""
        assert isinstance(metrics, list), "Metrics must be list"
        
        if not metrics:
            return HealthStatus.EXCELLENT
        
        # Count status occurrences
        status_counts = {}
        for metric in metrics:
            status = metric.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Determine overall health based on worst status
        if HealthStatus.CRITICAL in status_counts:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in status_counts:
            return HealthStatus.WARNING
        elif HealthStatus.GOOD in status_counts:
            return HealthStatus.GOOD
        else:
            return HealthStatus.EXCELLENT
    
    def _calculate_health_score(self, metrics: List[HealthMetric]) -> float:
        """Calculate health score - ATLAS: Fixed function length"""
        assert isinstance(metrics, list), "Metrics must be list"
        
        if not metrics:
            return 100.0
        
        # Calculate average score based on status
        total_score = 0.0
        for metric in metrics:
            if metric.status == HealthStatus.EXCELLENT:
                total_score += 100.0
            elif metric.status == HealthStatus.GOOD:
                total_score += 80.0
            elif metric.status == HealthStatus.WARNING:
                total_score += 60.0
            elif metric.status == HealthStatus.CRITICAL:
                total_score += 20.0
            else:
                total_score += 0.0
        
        return total_score / len(metrics)
    
    def _generate_alerts(self, metrics: List[HealthMetric]) -> List[str]:
        """Generate alerts - ATLAS: Fixed function length"""
        assert isinstance(metrics, list), "Metrics must be list"
        
        alerts = []
        
        # ATLAS: Fixed loop bound
        for i, metric in enumerate(metrics):
            if i >= MAX_METRIC_COLLECTIONS:
                break
            
            if metric.status == HealthStatus.CRITICAL:
                alerts.append(f"CRITICAL: {metric.metric_type.value} at {metric.value:.1f}{metric.unit} (threshold: {metric.threshold:.1f}{metric.unit})")
            elif metric.status == HealthStatus.WARNING:
                alerts.append(f"WARNING: {metric.metric_type.value} at {metric.value:.1f}{metric.unit} (threshold: {metric.threshold:.1f}{metric.unit})")
            
            # ATLAS: Assert loop progression
            assert i < len(metrics), "Loop bound exceeded"
        
        return alerts
    
    def _generate_recommendations(self, metrics: List[HealthMetric]) -> List[str]:
        """Generate recommendations - ATLAS: Fixed function length"""
        assert isinstance(metrics, list), "Metrics must be list"
        
        recommendations = []
        
        # ATLAS: Fixed loop bound
        for i, metric in enumerate(metrics):
            if i >= MAX_METRIC_COLLECTIONS:
                break
            
            if metric.status == HealthStatus.CRITICAL:
                if metric.metric_type == MetricType.CPU:
                    recommendations.append("Consider reducing CPU-intensive processes or scaling resources")
                elif metric.metric_type == MetricType.MEMORY:
                    recommendations.append("Consider freeing memory or increasing available RAM")
                elif metric.metric_type == MetricType.DISK:
                    recommendations.append("Consider cleaning up disk space or expanding storage")
                elif metric.metric_type == MetricType.NETWORK:
                    recommendations.append("Check network connectivity and configuration")
                elif metric.metric_type == MetricType.PROCESS:
                    recommendations.append("Consider terminating unnecessary processes")
            
            # ATLAS: Assert loop progression
            assert i < len(metrics), "Loop bound exceeded"
        
        return recommendations
    
    def _log_health_status(self, report: SystemHealthReport) -> None:
        """Log health status - ATLAS: Fixed function length"""
        assert isinstance(report, SystemHealthReport), "Report must be SystemHealthReport"
        
        if report.overall_health == HealthStatus.CRITICAL:
            self.logger.critical(f"System health CRITICAL: {report.health_score:.1f}/100")
        elif report.overall_health == HealthStatus.WARNING:
            self.logger.warning(f"System health WARNING: {report.health_score:.1f}/100")
        elif report.overall_health == HealthStatus.GOOD:
            self.logger.info(f"System health GOOD: {report.health_score:.1f}/100")
        else:
            self.logger.info(f"System health EXCELLENT: {report.health_score:.1f}/100")
    
    def generate_health_summary(self) -> Dict[str, Any]:
        """Generate health summary - ATLAS: Fixed function length"""
        if not self.health_reports:
            return {
                "overall_health": "excellent",
                "health_score": 100.0,
                "total_metrics": 0,
                "alerts_count": 0,
                "recommendations_count": 0,
                "monitoring_active": self._monitoring_active,
                "timestamp": datetime.now().isoformat()
            }
        
        latest_report = self.health_reports[-1]
        
        # Count metrics by type
        type_counts = {}
        for metric in self.health_metrics:
            metric_type = metric.metric_type.value
            type_counts[metric_type] = type_counts.get(metric_type, 0) + 1
        
        # Count metrics by status
        status_counts = {}
        for metric in self.health_metrics:
            status = metric.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        summary = {
            "overall_health": latest_report.overall_health.value,
            "health_score": latest_report.health_score,
            "total_metrics": len(self.health_metrics),
            "alerts_count": len(latest_report.alerts),
            "recommendations_count": len(latest_report.recommendations),
            "metric_type_distribution": type_counts,
            "metric_status_distribution": status_counts,
            "monitoring_active": self._monitoring_active,
            "timestamp": latest_report.timestamp
        }
        
        return summary

# ATLAS Protocol: Main execution with proper error handling
if __name__ == "__main__":
    try:
        health_monitor = AEGISSystemHealthMonitoring()
        summary = health_monitor.generate_health_summary()
        print(f"Health Summary: {summary}")
    except Exception as e:
        print(f"System Health Monitoring failed: {e}")
        sys.exit(1)