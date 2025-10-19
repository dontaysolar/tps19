#!/usr/bin/env python3
"""
APEX NEXUS INTEGRATED - Full 200 Bot System
Complete integration of all bots with proper coordination
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, List
import ccxt

# Load environment
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v

# Import core systems
from bot_registry import BotRegistry
sys.path.insert(0, 'bots')

# Import NEXUS coordination layer
from nexus_central_coordinator import NexusCentralCoordinator
from strategy_hub_coordinator import StrategyHubCoordinator
from market_intelligence_hub import MarketIntelligenceHub
from performance_optimization_hub import PerformanceOptimizationHub

# Import critical infrastructure
from rate_limiter_bot import RateLimiterBot
from circuit_breaker_bot import CircuitBreakerBot
from health_monitor_bot import HealthMonitorBot
from log_manager_bot import LogManagerBot
from metrics_aggregator_bot import MetricsAggregatorBot

# Import notifications
from telegram_notifier_bot import TelegramNotifierBot
from discord_notifier_bot import DiscordNotifierBot

class APEXNexusIntegrated:
    def __init__(self):
        print("=" * 80)
        print("🚀 APEX NEXUS INTEGRATED - 200 Bot System Loading...")
        print("=" * 80)
        
        # Initialize infrastructure
        self.logger = LogManagerBot()
        self.logger.info("System initialization started", "SYSTEM")
        
        self.rate_limiter = RateLimiterBot()
        self.circuit_breaker = CircuitBreakerBot()
        self.health_monitor = HealthMonitorBot()
        self.metrics = MetricsAggregatorBot()
        
        # Initialize exchange
        try:
            self.exchange = ccxt.cryptocom({
                'apiKey': os.environ.get('EXCHANGE_API_KEY', ''),
                'secret': os.environ.get('EXCHANGE_API_SECRET', ''),
                'enableRateLimit': True
            })
            self.logger.info("Exchange connected", "EXCHANGE")
        except Exception as e:
            self.logger.error(f"Exchange connection failed: {e}", "EXCHANGE")
            self.exchange = None
        
        # Initialize bot registry and discover all bots
        print("\n📋 Discovering bots...")
        self.registry = BotRegistry()
        discovery = self.registry.auto_discover_bots('bots')
        
        discovered_count = discovery.get('discovered', 0)
        print(f"✅ Discovered {discovered_count} bots")
        self.logger.info(f"Bot discovery: {discovered_count} bots found", "REGISTRY")
        
        # Initialize NEXUS coordination layer
        print("\n🎯 Initializing NEXUS Coordination...")
        self.nexus = NexusCentralCoordinator()
        self.strategy_hub = StrategyHubCoordinator()
        self.intelligence_hub = MarketIntelligenceHub()
        self.optimization_hub = PerformanceOptimizationHub()
        
        # Register all discovered bots with NEXUS
        for bot_name, bot_info in self.registry.bots.items():
            try:
                instance = bot_info['instance']
                category = self._determine_category(bot_name)
                self.nexus.register_bot(bot_name, instance, category)
                self.logger.info(f"Registered with NEXUS: {bot_name}", "NEXUS")
            except Exception as e:
                self.logger.error(f"Failed to register {bot_name}: {e}", "NEXUS")
        
        print(f"✅ NEXUS Coordinator: {len(self.nexus.registered_bots)} bots registered")
        
        # Initialize notifications
        print("\n📢 Setting up notifications...")
        self.telegram = TelegramNotifierBot()
        self.discord = DiscordNotifierBot()
        
        if os.environ.get('TELEGRAM_BOT_TOKEN'):
            self.telegram.configure(
                bot_token=os.environ['TELEGRAM_BOT_TOKEN'],
                chat_id=os.environ.get('TELEGRAM_CHAT_ID', '')
            )
            self.telegram.send_alert("🚀 APEX Nexus Integrated starting up!", priority='HIGH')
        
        # System configuration
        self.config = {
            'trading_enabled': False,  # Start in safe mode
            'pairs': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'],
            'update_interval': 60,  # seconds
            'max_memory_mb': 4096
        }
        
        self.state = {
            'cycle': 0,
            'start_time': datetime.now(),
            'last_health_check': None
        }
        
        print("\n" + "=" * 80)
        print("✅ APEX NEXUS INTEGRATED - READY")
        print(f"   Bots Loaded: {discovered_count}")
        print(f"   NEXUS Registered: {len(self.nexus.registered_bots)}")
        print(f"   Trading Mode: {'ENABLED' if self.config['trading_enabled'] else 'MONITORING ONLY'}")
        print("=" * 80 + "\n")
        
        self.logger.info("System initialization complete", "SYSTEM")
    
    def _determine_category(self, bot_name: str) -> str:
        """Categorize bot by name"""
        if any(x in bot_name for x in ['lstm', 'gan', 'transformer', 'random_forest', 'xgboost', 'reinforcement']):
            return 'AI_ML'
        elif any(x in bot_name for x in ['grid', 'market_making', 'arbitrage', 'pairs']):
            return 'STRATEGY'
        elif any(x in bot_name for x in ['vwap', 'twap', 'iceberg', 'sniper']):
            return 'EXECUTION'
        elif any(x in bot_name for x in ['var', 'cvar', 'monte_carlo', 'black_swan']):
            return 'RISK'
        elif any(x in bot_name for x in ['rsi', 'macd', 'bollinger', 'ichimoku', 'fibonacci']):
            return 'INDICATOR'
        else:
            return 'GENERAL'
    
    def fetch_market_data(self, symbol: str) -> Dict:
        """Fetch market data with rate limiting and error handling"""
        
        # Check circuit breaker
        circuit_status = self.circuit_breaker.check_circuit()
        if not circuit_status['trading_allowed']:
            self.logger.warning("Circuit breaker open - skipping data fetch", "EXCHANGE")
            return {}
        
        # Check rate limit
        rate_check = self.rate_limiter.check_rate_limit()
        if not rate_check['allowed']:
            self.logger.warning(f"Rate limit hit - waiting {rate_check.get('wait_seconds', 1)}s", "EXCHANGE")
            time.sleep(rate_check.get('wait_seconds', 1))
            return {}
        
        # Fetch data
        try:
            if not self.exchange:
                return {}
            
            ticker = self.exchange.fetch_ticker(symbol)
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1m', limit=100)
            
            return {
                'symbol': symbol,
                'price': ticker['last'],
                'volume': ticker['volume'],
                'ohlcv': ohlcv,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Data fetch failed for {symbol}: {e}", "EXCHANGE")
            self.circuit_breaker.record_failure(f"fetch_{symbol}")
            return {}
    
    def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        self.state['cycle'] += 1
        cycle = self.state['cycle']
        
        print(f"\n{'='*80}")
        print(f"CYCLE #{cycle} - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")
        
        # Health check every 10 cycles
        if cycle % 10 == 0:
            health = self.health_monitor.check_system_health()
            print(f"💓 System Health: {health['status']}")
            print(f"   CPU: {health.get('cpu_percent', 0):.1f}%")
            print(f"   Memory: {health.get('memory_percent', 0):.1f}%")
            
            if health['status'] in ['WARNING', 'CRITICAL']:
                self.telegram.send_alert(f"⚠️ System Health: {health['status']}", priority='HIGH')
        
        # Fetch market data
        market_data = {}
        for symbol in self.config['pairs']:
            data = self.fetch_market_data(symbol)
            if data:
                market_data[symbol] = data
                print(f"📊 {symbol}: ${data['price']:.2f}")
        
        # Gather intelligence (if we have data)
        if market_data:
            intel = self.intelligence_hub.gather_intelligence(market_data)
            print(f"🔍 Intelligence sources consulted: {intel.get('sources_consulted', 0)}")
        
        # Get coordinated decision from NEXUS
        if market_data:
            decision = self.nexus.orchestrate_decision(market_data)
            print(f"🎯 NEXUS Decision: {decision.get('final_signal', 'HOLD')}")
            print(f"   Confidence: {decision.get('confidence', 0)*100:.1f}%")
            print(f"   Bots Consulted: {decision.get('signals_collected', 0)}")
        
        # Performance check every 30 cycles
        if cycle % 30 == 0:
            bottlenecks = self.optimization_hub.analyze_performance_bottlenecks({
                'avg_latency_ms': 50,
                'requests_per_sec': 10,
                'error_rate_pct': 0.1
            })
            if bottlenecks['total'] > 0:
                print(f"⚡ Performance: {bottlenecks['total']} bottlenecks detected")
        
        # Status update
        registry_status = self.registry.get_registry_status()
        print(f"\n📋 System Status:")
        print(f"   Total Bots: {registry_status['total_bots']}")
        print(f"   NEXUS Active: {len(self.nexus.registered_bots)}")
        print(f"   Trading: {'ENABLED' if self.config['trading_enabled'] else 'MONITORING'}")
        
        # Telegram update every 60 cycles
        if cycle % 60 == 0:
            uptime = (datetime.now() - self.state['start_time']).seconds // 60
            self.telegram.send_alert(
                f"💓 APEX Running\n\nCycle: {cycle}\nUptime: {uptime}min\nBots: {registry_status['total_bots']}\nMode: Monitoring",
                priority='NORMAL'
            )
        
        print(f"✅ Cycle complete\n")
    
    def run(self):
        """Main monitoring loop"""
        print("\n🔄 Starting monitoring loop (Press Ctrl+C to stop)...\n")
        
        try:
            while True:
                try:
                    self.run_monitoring_cycle()
                    time.sleep(self.config['update_interval'])
                
                except KeyboardInterrupt:
                    raise
                
                except Exception as e:
                    self.logger.error(f"Cycle error: {e}", "SYSTEM")
                    print(f"❌ Cycle error: {e}")
                    time.sleep(self.config['update_interval'])
        
        except KeyboardInterrupt:
            print("\n\n🛑 Shutdown requested...")
            self.telegram.send_alert("🛑 APEX Nexus shutting down", priority='HIGH')
            self.logger.info("System shutdown initiated", "SYSTEM")
            print("✅ Shutdown complete")

if __name__ == '__main__':
    try:
        nexus = APEXNexusIntegrated()
        nexus.run()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
