#!/usr/bin/env python3
"""
UNIFIED BOT REGISTRY
Central registry for all 51+ APEX bots with auto-discovery
Provides unified interface to all trading capabilities
"""

import os
import sys
import json
import importlib
from datetime import datetime
from typing import Dict, List, Optional

class BotRegistry:
    """Central registry for all APEX bots"""
    
    def __init__(self):
        self.name = "APEX_Bot_Registry"
        self.version = "2.0.0"
        
        self.bots = {}
        self.bot_categories = {
            'GOD_LEVEL': [],      # GOD, KING, Oracle, Prophet, Seraphim, Cherubim, HiveMind, Navigator
            'COUNCIL': [],        # Council AI x5
            'ATN_TRADERS': [],    # Momentum, Snipe, Arbitrage, Flash, Short, Continuity x3
            'CORE_APEX': [],      # Dynamic SL, Fee Opt, Whale Mon, Crash Shield, Capital Rot
            'STRATEGY': [],       # Backtesting, Time Filter, DCA, Pattern Recognition
            'PROTECTION': [],     # Profit Lock, Liquidity Wave, Rug Shield, Profit Magnet
            'INFRASTRUCTURE': [], # Yield Farm, API Guard, Conflict Res, Emergency Pause
            'EVOLUTION': [],      # Bot Evolution, AI Clone, Crash Recovery
            'QUEENS': [],         # Queen Bots x5
            'THRONES': []         # Thrones AI
        }
        
        self.metrics = {
            'total_bots': 0,
            'active_bots': 0,
            'failed_bots': 0,
            'auto_discoveries': 0
        }
    
    def auto_discover_bots(self, bots_dir: str = 'bots') -> Dict:
        """Auto-discover all bot modules in bots/ directory"""
        discovered = []
        
        # Get all .py files in bots directory
        bots_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), bots_dir)
        
        if not os.path.exists(bots_path):
            return {'discovered': 0, 'error': f'Bots directory not found: {bots_path}'}
        
        sys.path.insert(0, bots_path)
        
        for filename in os.listdir(bots_path):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                
                try:
                    # Import module
                    module = importlib.import_module(module_name)
                    
                    # Find bot class (assume class name is PascalCase version of module)
                    class_name = self._get_class_name(module_name)
                    
                    if hasattr(module, class_name):
                        bot_class = getattr(module, class_name)
                        
                        # Try to instantiate
                        try:
                            bot_instance = bot_class()
                            bot_info = {
                                'module': module_name,
                                'class': class_name,
                                'instance': bot_instance,
                                'status': bot_instance.get_status() if hasattr(bot_instance, 'get_status') else {},
                                'discovered_at': datetime.now().isoformat()
                            }
                            
                            self.bots[module_name] = bot_info
                            discovered.append(module_name)
                            
                            # Categorize
                            self._categorize_bot(module_name, bot_info)
                            
                        except Exception as e:
                            print(f"⚠️ Could not instantiate {class_name}: {e}")
                    
                except Exception as e:
                    print(f"⚠️ Could not import {module_name}: {e}")
        
        self.metrics['total_bots'] = len(self.bots)
        self.metrics['active_bots'] = len(discovered)
        self.metrics['auto_discoveries'] += 1
        
        return {
            'discovered': len(discovered),
            'bots': discovered,
            'total_registered': len(self.bots),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_class_name(self, module_name: str) -> str:
        """Convert module_name to expected class name"""
        # god_bot -> GODBot, king_bot -> KINGBot, momentum_rider_bot -> MomentumRiderBot
        parts = module_name.split('_')
        
        # Handle special cases
        if module_name.startswith('god_'):
            return 'GODBot'
        elif module_name.startswith('king_'):
            return 'KINGBot'
        elif module_name.endswith('_ai'):
            # oracle_ai -> OracleAI, prophet_ai -> ProphetAI
            return ''.join(p.capitalize() for p in parts[:-1]) + 'AI'
        elif 'council' in module_name:
            # council_ai_1 -> CouncilAI_1
            return 'CouncilAI_' + parts[-1]
        elif 'queen' in module_name:
            # queen_bot_1 -> QueenBot1
            return 'QueenBot' + parts[-1]
        else:
            # Standard: momentum_rider_bot -> MomentumRiderBot
            return ''.join(p.capitalize() for p in parts)
    
    def _categorize_bot(self, bot_name: str, bot_info: Dict) -> None:
        """Categorize bot into appropriate group"""
        if 'god' in bot_name or 'king' in bot_name or bot_name.endswith('_ai'):
            if 'council' not in bot_name:
                self.bot_categories['GOD_LEVEL'].append(bot_name)
        
        elif 'council' in bot_name:
            self.bot_categories['COUNCIL'].append(bot_name)
        
        elif any(x in bot_name for x in ['momentum', 'snipe', 'arbitrage', 'flash', 'short', 'continuity']):
            self.bot_categories['ATN_TRADERS'].append(bot_name)
        
        elif any(x in bot_name for x in ['dynamic_stoploss', 'fee_optimizer', 'whale_monitor', 'crash_shield', 'capital_rotator']):
            self.bot_categories['CORE_APEX'].append(bot_name)
        
        elif any(x in bot_name for x in ['backtesting', 'time_filter', 'dca_strategy', 'pattern_recognition']):
            self.bot_categories['STRATEGY'].append(bot_name)
        
        elif any(x in bot_name for x in ['profit_lock', 'liquidity_wave', 'rug_shield', 'profit_magnet']):
            self.bot_categories['PROTECTION'].append(bot_name)
        
        elif any(x in bot_name for x in ['yield_farmer', 'api_guardian', 'conflict_resolver', 'emergency_pause']):
            self.bot_categories['INFRASTRUCTURE'].append(bot_name)
        
        elif any(x in bot_name for x in ['bot_evolution', 'ai_clone', 'crash_recovery']):
            self.bot_categories['EVOLUTION'].append(bot_name)
        
        elif 'queen' in bot_name:
            self.bot_categories['QUEENS'].append(bot_name)
        
        elif 'thrones' in bot_name:
            self.bot_categories['THRONES'].append(bot_name)
    
    def get_bot(self, bot_name: str) -> Optional[object]:
        """Get bot instance by name"""
        if bot_name in self.bots:
            return self.bots[bot_name]['instance']
        return None
    
    def get_bots_by_category(self, category: str) -> List[str]:
        """Get all bots in a category"""
        return self.bot_categories.get(category, [])
    
    def get_all_active_bots(self) -> List[str]:
        """Get list of all active bot names"""
        return list(self.bots.keys())
    
    def get_registry_status(self) -> Dict:
        """Get comprehensive registry status"""
        category_counts = {cat: len(bots) for cat, bots in self.bot_categories.items() if bots}
        
        return {
            'name': self.name,
            'version': self.version,
            'total_bots': len(self.bots),
            'categories': category_counts,
            'metrics': self.metrics,
            'timestamp': datetime.now().isoformat()
        }

if __name__ == '__main__':
    registry = BotRegistry()
    print("🎯 APEX Bot Registry v2.0.0\n")
    
    result = registry.auto_discover_bots()
    print(f"✅ Discovered {result['discovered']} bots")
    print(f"📊 Total registered: {result['total_registered']}")
    
    status = registry.get_registry_status()
    print(f"\n📋 Categories:")
    for cat, count in status['categories'].items():
        print(f"  {cat}: {count} bots")
