#!/usr/bin/env python3
"""
Emergency Pause Engine
Halts trading during major events (FOMC, CPI, etc.)
Part of APEX AI Trading System
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

class EmergencyPauseBot:
    """Pauses trading during high-impact economic events"""
    
    def __init__(self):
        self.name = "EmergencyPauseBot"
        self.version = "1.0.0"
        
        self.config = {
            'critical_events': [
                'FOMC', 'CPI', 'NFP', 'GDP', 'UNEMPLOYMENT',
                'FED_RATE', 'INFLATION', 'PCE'
            ],
            'pause_before_minutes': 60,       # Pause 1h before event
            'pause_after_minutes': 30,        # Resume 30min after
            'check_interval': 3600            # Check every hour
        }
        
        self.state = {
            'paused': False,
            'pause_reason': None,
            'pause_until': None
        }
        
        self.upcoming_events = []
        
        self.metrics = {
            'pauses_triggered': 0,
            'events_detected': 0,
            'trading_hours_paused': 0.0
        }
    
    def fetch_economic_calendar(self) -> List[Dict]:
        """Fetch upcoming economic events"""
        # Note: Would use real economic calendar API in production
        # For now, simulate with hardcoded events
        
        mock_events = [
            {
                'name': 'FOMC Meeting',
                'date': (datetime.now() + timedelta(days=7)).isoformat(),
                'impact': 'HIGH',
                'type': 'FOMC'
            },
            {
                'name': 'CPI Report',
                'date': (datetime.now() + timedelta(days=14)).isoformat(),
                'impact': 'HIGH',
                'type': 'CPI'
            }
        ]
        
        return mock_events
    
    def check_upcoming_events(self) -> Dict:
        """Check for upcoming critical events"""
        events = self.fetch_economic_calendar()
        now = datetime.now()
        
        critical_upcoming = []
        
        for event in events:
            event_time = datetime.fromisoformat(event['date'])
            time_until = (event_time - now).total_seconds() / 60  # Minutes
            
            # Check if within pause window
            if 0 < time_until <= self.config['pause_before_minutes']:
                if event['type'] in self.config['critical_events']:
                    critical_upcoming.append({
                        **event,
                        'minutes_until': time_until
                    })
        
        if critical_upcoming:
            self.metrics['events_detected'] += len(critical_upcoming)
        
        return {
            'critical_events': critical_upcoming,
            'should_pause': len(critical_upcoming) > 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def evaluate_pause_status(self) -> Dict:
        """Evaluate if trading should be paused"""
        # Check if currently paused
        if self.state['paused']:
            # Check if pause should end
            if self.state['pause_until']:
                pause_end = datetime.fromisoformat(self.state['pause_until'])
                if datetime.now() >= pause_end:
                    self.resume_trading()
                    return {
                        'action': 'RESUMED',
                        'reason': 'Pause period ended'
                    }
            
            return {
                'action': 'PAUSED',
                'reason': self.state['pause_reason'],
                'until': self.state['pause_until']
            }
        
        # Check for new events
        events = self.check_upcoming_events()
        
        if events['should_pause']:
            self.pause_trading(events['critical_events'])
            return {
                'action': 'PAUSED',
                'reason': 'Critical event detected',
                'events': events['critical_events']
            }
        
        return {'action': 'ACTIVE'}
    
    def pause_trading(self, events: List[Dict]) -> None:
        """Pause trading due to events"""
        if not self.state['paused']:
            # Find earliest event
            earliest = min(events, key=lambda e: e['minutes_until'])
            
            # Calculate pause duration
            pause_minutes = earliest['minutes_until'] + self.config['pause_after_minutes']
            pause_until = datetime.now() + timedelta(minutes=pause_minutes)
            
            self.state['paused'] = True
            self.state['pause_reason'] = f"{earliest['name']} in {earliest['minutes_until']:.0f} minutes"
            self.state['pause_until'] = pause_until.isoformat()
            
            self.metrics['pauses_triggered'] += 1
            self.metrics['trading_hours_paused'] += pause_minutes / 60
            
            print(f"🛑 TRADING PAUSED: {self.state['pause_reason']}")
            print(f"   Resuming at: {pause_until}")
    
    def resume_trading(self) -> None:
        """Resume trading after event"""
        if self.state['paused']:
            self.state['paused'] = False
            self.state['pause_reason'] = None
            self.state['pause_until'] = None
            
            print(f"✅ TRADING RESUMED")
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'state': self.state,
            'upcoming_events': len(self.upcoming_events),
            'metrics': self.metrics,
            'config': self.config
        }

if __name__ == '__main__':
    bot = EmergencyPauseBot()
    print("🚨 Emergency Pause Bot - Test Mode\n")
    
    status = bot.evaluate_pause_status()
    print(f"Current action: {status['action']}")
    
    if status['action'] == 'PAUSED':
        print(f"Reason: {status['reason']}")
