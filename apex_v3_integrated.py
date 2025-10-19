#!/usr/bin/env python3
"""
APEX V3 - FULLY INTEGRATED SYSTEM
All features in proper layers - NO isolated bots
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict
import ccxt

# Load environment
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v

# Import integrated layers
from market_analysis_layer import MarketAnalysisLayer
from signal_generation_layer import SignalGenerationLayer
from risk_management_layer import RiskManagementLayer
from execution_layer import ExecutionLayer
from ai_ml_layer import AIMLLayer
from infrastructure_layer import InfrastructureLayer

class APEXV3:
    """Fully integrated trading system"""
    
    def __init__(self):
        print("=" * 80)
        print("🚀 APEX V3 - FULLY INTEGRATED SYSTEM")
        print("=" * 80)
        
        # Initialize infrastructure
        print("\n📦 Initializing Infrastructure...")
        self.infra = InfrastructureLayer()
        self.infra.logger.info("System starting", "APEX")
        
        # Initialize exchange
        print("🔗 Connecting to exchange...")
        try:
            self.exchange = ccxt.cryptocom({
                'apiKey': os.environ.get('EXCHANGE_API_KEY', ''),
                'secret': os.environ.get('EXCHANGE_API_SECRET', ''),
                'enableRateLimit': True
            })
            self.exchange.load_markets()
            self.infra.logger.info("Exchange connected", "EXCHANGE")
        except Exception as e:
            self.infra.logger.error(f"Exchange connection failed: {e}", "EXCHANGE")
            self.exchange = None
        
        # Initialize analysis layers
        print("🔍 Initializing Analysis Layer...")
        self.analysis = MarketAnalysisLayer()
        
        print("🎯 Initializing Signal Generation...")
        self.signals = SignalGenerationLayer()
        
        print("🤖 Initializing AI/ML Models...")
        self.ai = AIMLLayer()
        
        print("🛡️ Initializing Risk Management...")
        self.risk = RiskManagementLayer()
        
        print("⚡ Initializing Execution Layer...")
        self.execution = ExecutionLayer(self.exchange) if self.exchange else None
        
        # Configuration
        self.config = {
            'trading_enabled': False,  # Start safe
            'pairs': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'],
            'update_interval': 60,
            'use_ai_predictions': True,
            'min_confidence': 0.70
        }
        
        self.state = {
            'cycle': 0,
            'start_time': datetime.now(),
            'trades_today': 0
        }
        
        print("\n" + "=" * 80)
        print("✅ APEX V3 INITIALIZED - ALL LAYERS ACTIVE")
        print(f"   Trading: {'ENABLED' if self.config['trading_enabled'] else 'MONITORING ONLY'}")
        print(f"   Pairs: {len(self.config['pairs'])}")
        print(f"   AI/ML: {'ENABLED' if self.config['use_ai_predictions'] else 'DISABLED'}")
        print("=" * 80 + "\n")
        
        self.infra.notifications.send("✅ APEX V3 Online - All layers integrated", "HIGH")
    
    def process_symbol(self, symbol: str) -> Dict:
        """Process one symbol through all layers"""
        
        # Check circuit breaker
        circuit_status = self.infra.circuit_breaker.check()
        if not circuit_status['allowed']:
            return {'action': 'SKIP', 'reason': 'Circuit breaker open'}
        
        # Check rate limit
        rate_check = self.infra.rate_limiter.check()
        if not rate_check['allowed']:
            time.sleep(rate_check.get('wait_seconds', 1))
            return {'action': 'SKIP', 'reason': 'Rate limited'}
        
        try:
            # Fetch market data
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1m', limit=200)
            ticker = self.exchange.fetch_ticker(symbol)
            
            # Cache data
            self.infra.cache.set(f'{symbol}_ohlcv', ohlcv, ttl=60)
            self.infra.cache.set(f'{symbol}_ticker', ticker, ttl=30)
            
            # Layer 1: Market Analysis
            analysis = self.analysis.analyze_comprehensive(ohlcv)
            
            # Layer 2: Technical Signals
            technical_signal = self.signals.generate_unified_signal(analysis)
            
            # Layer 3: AI/ML Predictions (optional)
            if self.config['use_ai_predictions']:
                ai_prediction = self.ai.predict_all(ohlcv)
            else:
                ai_prediction = {'signal': 'HOLD', 'confidence': 0}
            
            # Combine technical + AI
            final_signal = self.combine_signals(technical_signal, ai_prediction)
            
            # Layer 4: Risk Validation
            risk_check = self.risk.validate_trade(final_signal, analysis, symbol)
            
            # Layer 5: Execution (if approved and trading enabled)
            if risk_check['approved'] and self.config['trading_enabled']:
                execution_result = self.execution.execute_trade(symbol, final_signal, risk_check)
                
                self.infra.logger.info(
                    f"Trade executed: {symbol} {final_signal['signal']}", 
                    "EXECUTION"
                )
                
                self.infra.notifications.send(
                    f"✅ {final_signal['signal']} {symbol} @ {ticker['last']:.2f}",
                    "NORMAL"
                )
                
                return execution_result
            
            # Just monitoring
            return {
                'action': 'MONITOR',
                'symbol': symbol,
                'price': ticker['last'],
                'signal': final_signal,
                'risk_check': risk_check,
                'analysis': {
                    'trend': analysis['trend']['direction'],
                    'momentum_rsi': analysis['momentum']['rsi'],
                    'volatility': analysis['volatility']['regime']
                }
            }
        
        except Exception as e:
            self.infra.logger.error(f"Error processing {symbol}: {e}", "PROCESSING")
            self.infra.circuit_breaker.record_failure(f"process_{symbol}")
            return {'action': 'ERROR', 'error': str(e)}
    
    def combine_signals(self, technical: Dict, ai: Dict) -> Dict:
        """Combine technical and AI signals"""
        tech_signal = technical.get('signal', 'HOLD')
        tech_conf = technical.get('confidence', 0.5)
        
        ai_signal = ai.get('signal', 'HOLD')
        ai_conf = ai.get('confidence', 0)
        
        # Both agree = high confidence
        if tech_signal == ai_signal and tech_signal != 'HOLD':
            return {
                'signal': tech_signal,
                'confidence': min(0.95, (tech_conf + ai_conf) / 2 + 0.15),
                'source': 'TECHNICAL_AI_CONSENSUS'
            }
        
        # Technical higher confidence
        elif tech_conf > ai_conf:
            return {
                'signal': tech_signal,
                'confidence': tech_conf,
                'source': 'TECHNICAL'
            }
        
        # AI higher confidence
        elif ai_conf > tech_conf:
            return {
                'signal': ai_signal,
                'confidence': ai_conf,
                'source': 'AI'
            }
        
        # Default to hold
        else:
            return {
                'signal': 'HOLD',
                'confidence': 0.50,
                'source': 'NO_CONSENSUS'
            }
    
    def run(self):
        """Main trading loop"""
        print("\n🔄 Starting main loop...\n")
        
        try:
            while True:
                self.state['cycle'] += 1
                cycle = self.state['cycle']
                
                print(f"\n{'='*80}")
                print(f"CYCLE #{cycle} - {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*80}")
                
                # Health check every 10 cycles
                if cycle % 10 == 0:
                    health = self.infra.health_monitor.check_health()
                    print(f"💓 System Health: {health['status']}")
                    if 'cpu_percent' in health:
                        print(f"   CPU: {health['cpu_percent']:.1f}%")
                        print(f"   Memory: {health['memory_percent']:.1f}%")
                
                # Process each symbol
                for symbol in self.config['pairs']:
                    result = self.process_symbol(symbol)
                    
                    if result.get('action') == 'MONITOR':
                        sig = result['signal']
                        print(f"\n📊 {symbol}:")
                        print(f"   Price: ${result['price']:.2f}")
                        print(f"   Signal: {sig['signal']} ({sig['confidence']*100:.0f}%)")
                        print(f"   Trend: {result['analysis']['trend']}")
                        print(f"   RSI: {result['analysis']['momentum_rsi']:.1f}")
                        print(f"   Vol: {result['analysis']['volatility']}")
                
                # Status update every 30 cycles
                if cycle % 30 == 0:
                    uptime = (datetime.now() - self.state['start_time']).seconds // 60
                    self.infra.notifications.send(
                        f"💓 APEX V3 Running\nCycle: {cycle}\nUptime: {uptime}min\nMode: {'Trading' if self.config['trading_enabled'] else 'Monitoring'}",
                        "NORMAL"
                    )
                
                print(f"\n✅ Cycle complete")
                time.sleep(self.config['update_interval'])
        
        except KeyboardInterrupt:
            print("\n\n🛑 Shutdown requested...")
            self.infra.logger.info("System shutdown", "APEX")
            self.infra.notifications.send("🛑 APEX V3 shutting down", "HIGH")
            print("✅ Shutdown complete")

if __name__ == '__main__':
    apex = APEXV3()
    apex.run()
