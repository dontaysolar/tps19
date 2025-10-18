#!/usr/bin/env python3
"""
KING BOT - Master Commander & Personality Engine
Central command for ATN, activates trading profiles (Gorilla, Fox, Scholar, Guardian)
Part of APEX AI Trading System - God-Level Layer
"""

import os, sys, json
from datetime import datetime
from typing import Dict, List
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

class KINGBot:
    """Master Commander - Orchestrates ATN, switches trading modes"""
    
    def __init__(self):
        self.name, self.version = "KING_BOT", "1.0.0"
        
        self.profiles = {
            'GORILLA': {'risk': 'HIGH', 'volume': 'MAX', 'confidence_min': 0.95, 'description': 'High-volume blitz mode'},
            'FOX': {'risk': 'LOW', 'volume': 'MIN', 'confidence_min': 0.98, 'description': 'Flash crash sniper'},
            'SCHOLAR': {'risk': 'ZERO', 'volume': 'ZERO', 'confidence_min': 1.0, 'description': 'Learning mode - no trades'},
            'GUARDIAN': {'risk': 'LOW', 'volume': 'LOW', 'confidence_min': 0.85, 'description': 'Defensive bear market'}
        }
        
        self.active_profile = 'GUARDIAN'  # Start conservative
        self.bot_assignments = {}
        
        self.metrics = {
            'profile_switches': 0,
            'commands_executed': 0,
            'bots_deployed': 0
        }
    
    def switch_profile(self, new_profile: str, reason: str = '') -> Dict:
        """Switch trading profile based on market conditions"""
        if new_profile not in self.profiles:
            return {'success': False, 'error': f'Invalid profile: {new_profile}'}
        
        old_profile = self.active_profile
        self.active_profile = new_profile
        self.metrics['profile_switches'] += 1
        
        return {
            'success': True,
            'old_profile': old_profile,
            'new_profile': new_profile,
            'reason': reason,
            'config': self.profiles[new_profile],
            'timestamp': datetime.now().isoformat()
        }
    
    def deploy_bot(self, bot_name: str, symbol: str, profile: str = None) -> Dict:
        """Deploy a specific bot to trade a pair"""
        target_profile = profile or self.active_profile
        
        self.bot_assignments[symbol] = {
            'bot': bot_name,
            'profile': target_profile,
            'deployed_at': datetime.now().isoformat()
        }
        
        self.metrics['bots_deployed'] += 1
        
        return {
            'deployed': True,
            'bot': bot_name,
            'symbol': symbol,
            'profile': target_profile,
            'config': self.profiles[target_profile]
        }
    
    def get_active_bots(self) -> Dict:
        """Get all active bot assignments"""
        return {
            'active_profile': self.active_profile,
            'assignments': self.bot_assignments,
            'total_active': len(self.bot_assignments)
        }
    
    def execute_command(self, command: str, params: Dict = {}) -> Dict:
        """Execute system-wide commands"""
        self.metrics['commands_executed'] += 1
        
        commands = {
            'HALT_ALL': {'action': 'Stop all trading immediately', 'critical': True},
            'RESUME_ALL': {'action': 'Resume all trading', 'critical': True},
            'SWITCH_PROFILE': {'action': 'Change trading profile', 'critical': False},
            'EMERGENCY_EXIT': {'action': 'Close all positions and halt', 'critical': True}
        }
        
        if command not in commands:
            return {'success': False, 'error': f'Unknown command: {command}'}
        
        return {
            'success': True,
            'command': command,
            'action': commands[command]['action'],
            'critical': commands[command]['critical'],
            'params': params,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        """Get KING BOT status"""
        return {
            'name': self.name,
            'version': self.version,
            'active_profile': self.active_profile,
            'active_bots': len(self.bot_assignments),
            'metrics': self.metrics,
            'available_profiles': list(self.profiles.keys())
        }

if __name__ == '__main__':
    bot = KINGBot()
    print("👑 KING BOT - Master Commander\n")
    
    print(f"Active Profile: {bot.active_profile}")
    print(f"Profile Config: {bot.profiles[bot.active_profile]}")
    
    # Test profile switch
    result = bot.switch_profile('GORILLA', 'Strong bullish momentum')
    print(f"\nProfile Switch: {result['old_profile']} → {result['new_profile']}")
    
    # Test bot deployment
    deployment = bot.deploy_bot('MomentumRider', 'BTC/USDT')
    print(f"Bot Deployed: {deployment['bot']} on {deployment['symbol']}")
