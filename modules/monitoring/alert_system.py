#!/usr/bin/env python3
"""
Alert System - Multi-channel intelligent alerts
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class AlertPriority(Enum):
    """Alert priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AlertChannel(Enum):
    """Alert delivery channels"""
    LOG = 'log'
    TELEGRAM = 'telegram'
    EMAIL = 'email'
    SMS = 'sms'
    DISCORD = 'discord'


class AlertSystem:
    """
    Intelligent multi-channel alert system
    """
    
    def __init__(self):
        self.channels = {}
        self.alert_history = []
        self.milestone_alerted = {}
        
        # Rate limiting (avoid spam)
        self.last_alert_time = {}
        self.min_alert_interval = timedelta(minutes=5)
        
        # Initialize channels
        self._init_channels()
        
    def _init_channels(self):
        """Initialize alert channels"""
        # Telegram
        telegram_token = None  # Load from env
        telegram_chat_id = None  # Load from env
        if telegram_token and telegram_chat_id:
            self.channels[AlertChannel.TELEGRAM] = TelegramNotifier(
                telegram_token, telegram_chat_id
            )
        
        # Email (placeholder)
        self.channels[AlertChannel.EMAIL] = EmailNotifier()
        
        # Log (always available)
        self.channels[AlertChannel.LOG] = LogNotifier()
        
        # Discord (placeholder)
        self.channels[AlertChannel.DISCORD] = DiscordNotifier()
    
    def send_alert(self, alert_type: str, message: str, 
                   channels: List[str] = None,
                   priority: AlertPriority = AlertPriority.MEDIUM,
                   data: Optional[Dict] = None):
        """
        Send alert to specified channels
        
        Args:
            alert_type: Type of alert (WARNING, CRITICAL, SUCCESS, etc.)
            message: Alert message
            channels: List of channel names
            priority: Alert priority level
            data: Additional data to include
        """
        # Rate limiting check
        rate_key = f"{alert_type}_{message[:20]}"
        if rate_key in self.last_alert_time:
            time_since = datetime.now() - self.last_alert_time[rate_key]
            if time_since < self.min_alert_interval:
                logger.debug(f"Alert rate-limited: {alert_type}")
                return
        
        # Default to log channel
        if channels is None:
            channels = ['log']
        
        # Format message with emoji
        formatted_message = self._format_message(alert_type, message, priority)
        
        # Send to each channel
        for channel_name in channels:
            try:
                channel_enum = AlertChannel[channel_name.upper()]
                if channel_enum in self.channels:
                    self.channels[channel_enum].send(formatted_message, priority, data)
                else:
                    logger.warning(f"Channel {channel_name} not configured")
            except Exception as e:
                logger.error(f"Alert send error ({channel_name}): {e}")
        
        # Record alert
        self.alert_history.append({
            'timestamp': datetime.now(),
            'type': alert_type,
            'message': message,
            'priority': priority.name,
            'channels': channels
        })
        
        # Update rate limiting
        self.last_alert_time[rate_key] = datetime.now()
    
    def check_and_alert(self, vitals: Dict, positions: List):
        """
        Check organism vitals and send appropriate alerts
        
        Args:
            vitals: Organism vital signs
            positions: Active positions
        """
        # HEALTH ALERTS
        health_score = vitals.get('health_score', 100)
        if health_score < 70:
            self.send_alert(
                'WARNING',
                f"Health score low: {health_score:.1f}/100",
                channels=['log', 'telegram'],
                priority=AlertPriority.HIGH
            )
        
        if health_score < 50:
            self.send_alert(
                'CRITICAL',
                f"CRITICAL: Health score {health_score:.1f}/100 - System may enter hibernation",
                channels=['log', 'telegram', 'email'],
                priority=AlertPriority.CRITICAL
            )
        
        # DRAWDOWN ALERTS
        current_drawdown = vitals.get('current_drawdown', 0)
        if current_drawdown > 0.10:  # 10% drawdown
            self.send_alert(
                'CRITICAL',
                f"Drawdown at {current_drawdown:.1%} - Approaching limit",
                channels=['log', 'telegram', 'email'],
                priority=AlertPriority.CRITICAL
            )
        elif current_drawdown > 0.05:  # 5% drawdown
            self.send_alert(
                'WARNING',
                f"Drawdown at {current_drawdown:.1%}",
                channels=['log', 'telegram'],
                priority=AlertPriority.HIGH
            )
        
        # POSITION ALERTS
        for position in positions:
            pnl_pct = getattr(position, 'unrealized_pnl_pct', 0)
            
            # Large profit
            if pnl_pct > 0.10:  # 10%+ profit
                self.send_alert(
                    'SUCCESS',
                    f"Position in profit: {position.symbol} +{pnl_pct:.1%}",
                    channels=['log', 'telegram'],
                    priority=AlertPriority.LOW
                )
            
            # Large loss
            elif pnl_pct < -0.015:  # -1.5% loss (approaching -2% stop)
                self.send_alert(
                    'WARNING',
                    f"Position approaching stop: {position.symbol} {pnl_pct:.1%}",
                    channels=['log', 'telegram'],
                    priority=AlertPriority.HIGH
                )
        
        # PERFORMANCE MILESTONES
        total_profit = vitals.get('total_pnl', 0)
        
        milestones = [100, 250, 500, 1000, 2500, 5000]
        for milestone in milestones:
            milestone_key = f"{milestone}"
            if total_profit >= milestone and not self.milestone_alerted.get(milestone_key):
                self.send_alert(
                    'MILESTONE',
                    f"🎉 £{milestone} profit milestone reached! Total: £{total_profit:.2f}",
                    channels=['log', 'telegram', 'email'],
                    priority=AlertPriority.LOW
                )
                self.milestone_alerted[milestone_key] = True
        
        # CONSECUTIVE LOSSES
        consecutive_losses = vitals.get('consecutive_losses', 0)
        if consecutive_losses >= 3:
            self.send_alert(
                'WARNING',
                f"Consecutive losses: {consecutive_losses} - Reducing risk",
                channels=['log', 'telegram'],
                priority=AlertPriority.HIGH
            )
        
        # DAILY SUMMARY (once per day)
        if self._should_send_daily_summary():
            self._send_daily_summary(vitals)
    
    def _format_message(self, alert_type: str, message: str, 
                       priority: AlertPriority) -> str:
        """Format message with emoji and priority"""
        emoji_map = {
            'SUCCESS': '✅',
            'MILESTONE': '🎉',
            'WARNING': '⚠️',
            'CRITICAL': '🚨',
            'INFO': 'ℹ️',
            'TRADE': '📊'
        }
        
        emoji = emoji_map.get(alert_type, '📢')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        return f"{emoji} [{timestamp}] {alert_type}: {message}"
    
    def _should_send_daily_summary(self) -> bool:
        """Check if daily summary should be sent"""
        last_summary = self.last_alert_time.get('daily_summary')
        if last_summary is None:
            return True
        
        # Send if more than 20 hours since last summary
        return (datetime.now() - last_summary) > timedelta(hours=20)
    
    def _send_daily_summary(self, vitals: Dict):
        """Send daily performance summary"""
        summary = f"""
📊 TPS19 APEX Daily Summary

Health: {vitals.get('health_score', 0):.1f}/100
Total Trades: {vitals.get('total_trades', 0)}
Win Rate: {vitals.get('win_rate', 0):.1%}
Daily P&L: £{vitals.get('daily_pnl', 0):.2f}
Total P&L: £{vitals.get('total_pnl', 0):.2f}

Status: {vitals.get('status', 'Unknown')}
"""
        
        self.send_alert(
            'INFO',
            summary,
            channels=['log', 'telegram'],
            priority=AlertPriority.LOW
        )
        
        self.last_alert_time['daily_summary'] = datetime.now()


class TelegramNotifier:
    """Telegram notification channel"""
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    def send(self, message: str, priority: AlertPriority, data: Optional[Dict] = None):
        """Send Telegram message"""
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(self.api_url, json=payload, timeout=5)
            if response.status_code == 200:
                logger.debug("Telegram alert sent")
            else:
                logger.error(f"Telegram error: {response.status_code}")
        except Exception as e:
            logger.error(f"Telegram send error: {e}")


class EmailNotifier:
    """Email notification channel (placeholder)"""
    
    def send(self, message: str, priority: AlertPriority, data: Optional[Dict] = None):
        """Send email (placeholder)"""
        logger.info(f"[EMAIL] {message}")
        # In production: Use SendGrid, AWS SES, or SMTP


class DiscordNotifier:
    """Discord webhook notification (placeholder)"""
    
    def send(self, message: str, priority: AlertPriority, data: Optional[Dict] = None):
        """Send Discord message (placeholder)"""
        logger.info(f"[DISCORD] {message}")
        # In production: Use Discord webhook


class LogNotifier:
    """Log-based notifications"""
    
    def send(self, message: str, priority: AlertPriority, data: Optional[Dict] = None):
        """Write to log"""
        if priority == AlertPriority.CRITICAL:
            logger.critical(message)
        elif priority == AlertPriority.HIGH:
            logger.warning(message)
        else:
            logger.info(message)


# Global instance
alert_system = AlertSystem()
