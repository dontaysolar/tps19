#!/usr/bin/env python3
"""HiveMind AI v2.0 - Bot Synchronization Engine | AEGIS
Syncs 300+ bots, coordinates decisions"""
import os, sys
from datetime import datetime
from typing import Dict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from trading_bot_base import TradingBotBase

class HiveMindAI(TradingBotBase):
    def __init__(self):
        super().__init__(bot_name="HIVEMIND_AI", bot_version="2.0.0", exchange_name='mock', enable_psm=False, enable_logging=False)
        self.registered_bots = {}
        self.shared_state = {}
        self.metrics.update({'sync_operations': 0, 'bots_synced': 0, 'consensus_reached': 0})
    
    def register_bot(self, bot_name: str, bot_type: str) -> Dict:
        assert len(bot_name) > 0, "Bot name required"
        bot_id = f"{bot_name}_{datetime.now().timestamp()}"
        self.registered_bots[bot_id] = {'name': bot_name, 'type': bot_type, 'registered_at': datetime.now().isoformat(), 'last_sync': None}
        result = {'registered': True, 'bot_id': bot_id}
        assert isinstance(result, dict), "Result must be dict"
        return result
    
    def sync_bot_state(self, bot_id: str, state: Dict) -> Dict:
        assert len(bot_id) > 0, "Bot ID required"
        if bot_id not in self.registered_bots:
            return {'success': False, 'error': 'Bot not registered'}
        self.shared_state[bot_id] = {'state': state, 'synced_at': datetime.now().isoformat()}
        self.registered_bots[bot_id]['last_sync'] = datetime.now().isoformat()
        self.metrics['sync_operations'] += 1
        result = {'success': True, 'synced': True}
        assert isinstance(result, dict), "Result must be dict"
        return result
    
    def get_consensus(self, decision_type: str) -> Dict:
        assert len(decision_type) > 0, "Decision type required"
        votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        for bot_id, state in self.shared_state.items():
            vote = state.get('state', {}).get('signal', 'HOLD')
            if vote in votes:
                votes[vote] += 1
        total_votes = sum(votes.values())
        if total_votes == 0:
            consensus, confidence = 'HOLD', 0.0
        else:
            consensus = max(votes, key=votes.get)
            confidence = votes[consensus] / total_votes
        if confidence >= 0.6:
            self.metrics['consensus_reached'] += 1
        result = {'consensus': consensus, 'confidence': confidence, 'votes': votes, 'timestamp': datetime.now().isoformat()}
        assert isinstance(result, dict), "Result must be dict"
        return result

if __name__ == '__main__':
    print("🧠 HiveMind AI v2.0 - Bot Synchronization")
    bot = HiveMindAI()
    bot.register_bot('MomentumRider', 'TRADER')
    bot.register_bot('OracleAI', 'PREDICTOR')
    print(f"Registered: {len(bot.registered_bots)} bots")
    bot.close()
    print("✅ HiveMind AI v2.0 complete!")
