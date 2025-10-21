#!/usr/bin/env python3
"""Bot Evolution Engine v2.0 - Genetic Algorithm Optimizer | AEGIS
Merges/retires underperforming bots"""
import os, sys
from datetime import datetime
from typing import Dict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from trading_bot_base import TradingBotBase

try:
    import numpy as np
except ImportError:
    np = None

class BotEvolutionEngine(TradingBotBase):
    def __init__(self):
        super().__init__(bot_name="BOT_EVOLUTION_ENGINE", bot_version="2.0.0", exchange_name='mock', enable_psm=False, enable_logging=False)
        self.bot_population = {}
        self.metrics.update({'evolutions': 0, 'retirements': 0, 'merges': 0})
    
    def evaluate_fitness(self, bot_performance: Dict) -> float:
        assert isinstance(bot_performance, dict), "Performance must be dict"
        win_rate = bot_performance.get('win_rate', 0)
        profit_factor = bot_performance.get('profit_factor', 0)
        sharpe = bot_performance.get('sharpe_ratio', 0)
        fitness = (win_rate * 0.4) + (min(profit_factor / 2, 1.0) * 0.4) + (min(sharpe, 1.0) * 0.2)
        assert 0 <= fitness <= 1, "Fitness must be in [0, 1]"
        return fitness
    
    def evolve_bot(self, bot_id: str, performance: Dict) -> Dict:
        assert len(bot_id) > 0, "Bot ID required"
        fitness = self.evaluate_fitness(performance)
        
        if fitness < 0.3:
            self.metrics['retirements'] += 1
            result = {'action': 'RETIRE', 'bot_id': bot_id, 'fitness': fitness}
        elif fitness < 0.6:
            if np:
                mutation = {'risk_adj': 1.0 + np.random.uniform(-0.2, 0.2)}
            else:
                mutation = {'risk_adj': 1.0}
            self.metrics['evolutions'] += 1
            result = {'action': 'MUTATE', 'bot_id': bot_id, 'mutation': mutation, 'fitness': fitness}
        else:
            result = {'action': 'CLONE', 'bot_id': bot_id, 'fitness': fitness}
        
        assert isinstance(result, dict), "Result must be dict"
        return result
    
    def merge_bots(self, bot1_id: str, bot2_id: str) -> Dict:
        assert len(bot1_id) > 0 and len(bot2_id) > 0, "Bot IDs required"
        self.metrics['merges'] += 1
        result = {'merged': True, 'parent_1': bot1_id, 'parent_2': bot2_id, 'child_id': f'merged_{datetime.now().timestamp()}'}
        assert isinstance(result, dict), "Result must be dict"
        return result

if __name__ == '__main__':
    print("🧩 Bot Evolution Engine v2.0")
    bot = BotEvolutionEngine()
    perf = {'win_rate': 0.7, 'profit_factor': 1.5, 'sharpe_ratio': 0.8}
    result = bot.evolve_bot('TestBot', perf)
    print(f"Action: {result['action']}, Fitness: {result['fitness']:.2f}")
    bot.close()
    print("✅ Bot Evolution Engine v2.0 complete!")
