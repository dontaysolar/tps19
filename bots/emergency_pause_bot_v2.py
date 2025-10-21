#!/usr/bin/env python3
"""Emergency Pause Bot v2.0 - Event-Based Trading Halt | AEGIS"""
import os, sys
from datetime import datetime, timedelta
from typing import Dict, List
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from trading_bot_base import TradingBotBase

class EmergencyPauseBot(TradingBotBase):
    def __init__(self):
        super().__init__(bot_name="EMERGENCY_PAUSE_BOT", bot_version="2.0.0", exchange_name='mock', enable_psm=False, enable_logging=False)
        self.config = {'critical_events': ['FOMC', 'CPI', 'NFP', 'GDP'], 'pause_before_minutes': 60, 'pause_after_minutes': 30}
        self.state = {'paused': False, 'pause_reason': None, 'pause_until': None}
        self.upcoming_events = []
        self.metrics.update({'pauses_triggered': 0, 'events_detected': 0})
    
    def fetch_economic_calendar(self) -> List[Dict]:
        mock_events = [
            {'name': 'FOMC Meeting', 'date': (datetime.now() + timedelta(days=7)).isoformat(), 'impact': 'HIGH', 'type': 'FOMC'},
            {'name': 'CPI Report', 'date': (datetime.now() + timedelta(days=14)).isoformat(), 'impact': 'HIGH', 'type': 'CPI'}
        ]
        return mock_events
    
    def check_upcoming_events(self) -> Dict:
        assert isinstance(self.config['critical_events'], list), "Events must be list"
        events = self.fetch_economic_calendar()
        now = datetime.now()
        critical_upcoming = []
        for event in events[:10]:  # ATLAS: Fixed bound
            event_time = datetime.fromisoformat(event['date'])
            time_until = (event_time - now).total_seconds() / 60
            if 0 < time_until <= self.config['pause_before_minutes']:
                if event['type'] in self.config['critical_events']:
                    critical_upcoming.append({**event, 'minutes_until': time_until})
        if critical_upcoming:
            self.metrics['events_detected'] += len(critical_upcoming)
        result = {'critical_events': critical_upcoming, 'should_pause': len(critical_upcoming) > 0, 'timestamp': datetime.now().isoformat()}
        assert isinstance(result, dict), "Result must be dict"
        return result
    
    def trigger_pause(self, reason: str) -> Dict:
        assert len(reason) > 0, "Reason required"
        self.state['paused'] = True
        self.state['pause_reason'] = reason
        self.state['pause_until'] = (datetime.now() + timedelta(minutes=self.config['pause_after_minutes'])).isoformat()
        self.metrics['pauses_triggered'] += 1
        result = {'paused': True, 'reason': reason, 'pause_until': self.state['pause_until']}
        assert isinstance(result, dict), "Result must be dict"
        return result
    
    def resume_trading(self) -> Dict:
        self.state['paused'] = False
        self.state['pause_reason'] = None
        self.state['pause_until'] = None
        return {'resumed': True}

if __name__ == '__main__':
    bot = EmergencyPauseBot()
    check = bot.check_upcoming_events()
    print(f"Should pause: {check['should_pause']}")
    bot.close()
    print("✅ Emergency Pause Bot v2.0 complete!")
