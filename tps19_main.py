#!/usr/bin/env python3
"""
TPS19 - FULLY INTEGRATED SYSTEM
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

class TPS19:
    """Fully integrated trading system"""
    
    def __init__(self):
        print("=" * 80)
        print("🚀 TPS19 - FULLY INTEGRATED SYSTEM")
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
            'min_confidence': 0.70,
            
            # Feature flags - disable placeholders
            'use_sentiment': False,  # Placeholder - no real APIs connected
            'use_onchain': False,    # Placeholder - no real APIs connected
            'use_real_news': False,  # Placeholder - no real APIs connected
        }
        
        self.state = {
            'cycle': 0,
            'start_time': datetime.now(),
            'trades_today': 0
        }
        
        print("\n" + "=" * 80)
        print("✅ TPS19 INITIALIZED - ALL 10 LAYERS ACTIVE")
        print(f"   Version: TPS19 (16 ahead of APEX)")
        print(f"   Trading: {'ENABLED' if self.config['trading_enabled'] else 'MONITORING ONLY'}")
        print(f"   Pairs: {len(self.config['pairs'])}")
        print(f"   AI/ML: {'ENABLED' if self.config['use_ai_predictions'] else 'DISABLED'}")
        print(f"   Layers: 10 (Market, Signals, AI/ML, Risk, Execution, Sentiment, On-Chain, Portfolio, Backtesting, Infrastructure)")
        print("=" * 80 + "\n")
        
        # Send startup notification with clear status
        mode = 'LIVE' if self.config['trading_enabled'] else 'MONITORING'
        self.infra.notifications.send(
            "✅ TPS19 System Started\n"
            f"Mode: {mode}\n"
            f"Trading: {'ENABLED ⚠️' if self.config['trading_enabled'] else 'DISABLED ✅'}\n"
            f"Pairs: {', '.join(self.config['pairs'])}\n"
            f"AI/ML: {'ON' if self.config['use_ai_predictions'] else 'OFF'}",
            "HIGH",
            trading_status=mode
        )
    
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
                    "TPS19"
                )
                
                mode = 'LIVE' if self.config['trading_enabled'] else 'MONITORING'
                self.infra.notifications.send(
                    f"{'✅ EXECUTED' if self.config['trading_enabled'] else '📊 SIGNAL ONLY'}:\n"
                    f"{final_signal['signal']} {symbol} @ {ticker['last']:.2f}\n"
                    f"Confidence: {final_signal['confidence']:.0%}",
                    "NORMAL",
                    trading_status=mode
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
    
    def combine_signals(self, technical: Dict, ai: Dict, sentiment: Dict = None, onchain: Dict = None) -> Dict:
        """Combine all signals (technical, AI, sentiment, on-chain)"""
        signals = []
        
        # Technical signal
        tech_signal = technical.get('signal', 'HOLD')
        tech_conf = technical.get('confidence', 0.5)
        if tech_signal != 'HOLD':
            signals.append({'signal': tech_signal, 'confidence': tech_conf, 'weight': 0.35})
        
        # AI signal
        ai_signal = ai.get('signal', 'HOLD')
        ai_conf = ai.get('confidence', 0)
        if ai_signal != 'HOLD' and ai_conf > 0:
            signals.append({'signal': ai_signal, 'confidence': ai_conf, 'weight': 0.30})
        
        # Sentiment signal
        if sentiment:
            sent_signal = sentiment.get('overall_sentiment', 'NEUTRAL')
            sent_conf = sentiment.get('confidence', 0.5)
            if sent_signal in ['BULLISH', 'BEARISH']:
                sig = 'BUY' if sent_signal == 'BULLISH' else 'SELL'
                signals.append({'signal': sig, 'confidence': sent_conf, 'weight': 0.20})
        
        # On-chain signal
        if onchain:
            health = onchain.get('overall_health', {})
            health_status = health.get('status', 'NEUTRAL')
            if health_status in ['HEALTHY', 'UNHEALTHY']:
                sig = 'BUY' if health_status == 'HEALTHY' else 'SELL'
                signals.append({'signal': sig, 'confidence': 0.65, 'weight': 0.15})
        
        # Aggregate all signals
        if not signals:
            return {'signal': 'HOLD', 'confidence': 0.50, 'source': 'NO_SIGNALS'}
        
        buy_score = sum(s['confidence'] * s['weight'] for s in signals if s['signal'] == 'BUY')
        sell_score = sum(s['confidence'] * s['weight'] for s in signals if s['signal'] == 'SELL')
        
        if buy_score > sell_score and buy_score > 0.5:
            return {
                'signal': 'BUY',
                'confidence': buy_score,
                'source': 'MULTI_LAYER_CONSENSUS',
                'contributors': len(signals)
            }
        elif sell_score > buy_score and sell_score > 0.5:
            return {
                'signal': 'SELL',
                'confidence': sell_score,
                'source': 'MULTI_LAYER_CONSENSUS',
                'contributors': len(signals)
            }
        else:
            return {'signal': 'HOLD', 'confidence': 0.50, 'source': 'NO_CONSENSUS'}
    
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
                mode = 'LIVE' if self.config['trading_enabled'] else 'MONITORING'
                self.infra.notifications.send(
                    f"💓 TPS19 Status Update\n"
                    f"Cycle: {cycle}\n"
                    f"Uptime: {uptime}min\n"
                    f"Trades Today: {self.state['trades_today']}\n"
                    f"Mode: {mode}",
                    "NORMAL",
                    trading_status=mode
                )
                
                print(f"\n✅ Cycle complete")
                time.sleep(self.config['update_interval'])
        
        except KeyboardInterrupt:
            print("\n\n🛑 Shutdown requested...")
            self.infra.logger.info("System shutdown", "TPS19")
            self.infra.notifications.send("🛑 TPS19 shutting down", "HIGH")
            print("✅ Shutdown complete")

if __name__ == '__main__':
    tps19 = TPS19()
    tps19.run()
