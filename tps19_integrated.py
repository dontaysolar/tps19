#!/usr/bin/env python3
"""
TPS19 INTEGRATED - With Real-time, Advanced Orders, Paper Trading, News API
Complete production system with all new features
"""

import os
import sys
import time
import asyncio
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

# Import core layers
from market_analysis_layer import MarketAnalysisLayer
from signal_generation_layer import SignalGenerationLayer
from risk_management_layer import RiskManagementLayer
from execution_layer import ExecutionLayer
from ai_ml_layer import AIMLLayer
from infrastructure_layer import InfrastructureLayer

# Import NEW features
from websocket_layer import WebSocketLayer
from advanced_orders import AdvancedOrderManager
from paper_trading import PaperTradingEngine
from news_api_integration import NewsAPIIntegration


class TPS19Integrated:
    """TPS19 with all features integrated"""
    
    def __init__(self, mode='paper'):
        """
        Initialize TPS19 with mode selection
        
        Args:
            mode: 'monitoring', 'paper', or 'live'
        """
        print("=" * 80)
        print("🚀 TPS19 INTEGRATED - ALL FEATURES ACTIVE")
        print("=" * 80)
        
        # Validate mode
        if mode not in ['monitoring', 'paper', 'live']:
            raise ValueError(f"Invalid mode: {mode}. Must be 'monitoring', 'paper', or 'live'")
        
        self.mode = mode
        
        # Initialize infrastructure
        print("\n📦 Initializing Infrastructure...")
        self.infra = InfrastructureLayer()
        self.infra.logger.info(f"System starting in {mode.upper()} mode", "TPS19")
        
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
        
        # Initialize layers
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
        
        # Initialize NEW features
        print("\n🆕 Initializing New Features...")
        
        # WebSocket
        self.websocket = None
        print("  📡 WebSocket Layer")
        
        # Advanced Orders
        self.advanced_orders = AdvancedOrderManager(self.exchange) if self.exchange else None
        print("  📋 Advanced Orders (limit, stop, OCO, trailing)")
        
        # Paper Trading
        self.paper_trading = PaperTradingEngine(initial_balance=10000)
        print(f"  🧪 Paper Trading (${self.paper_trading.initial_balance:,.2f})")
        
        # News API
        self.news_api = NewsAPIIntegration()
        print(f"  📰 News API ({'ENABLED' if self.news_api.enabled['newsapi'] or self.news_api.enabled['cryptopanic'] else 'PLACEHOLDER'})")
        
        # Configuration
        self.config = {
            'mode': mode,
            'pairs': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'],
            'update_interval': 60,
            'use_ai_predictions': True,
            'min_confidence': 0.70,
            'use_websocket': True,
            'use_advanced_orders': True,
            'use_news_sentiment': True,
        }
        
        self.state = {
            'cycle': 0,
            'start_time': datetime.now(),
            'trades_today': 0
        }
        
        # Display configuration
        mode_display = {
            'monitoring': '📊 MONITORING ONLY',
            'paper': '🧪 PAPER TRADING',
            'live': '🔴 LIVE TRADING'
        }
        
        print("\n" + "=" * 80)
        print("✅ TPS19 READY")
        print(f"   Mode: {mode_display[mode]}")
        print(f"   Pairs: {', '.join(self.config['pairs'])}")
        print(f"   AI/ML: ON")
        print(f"   Real-time: {'ON' if self.config['use_websocket'] else 'OFF'}")
        print(f"   News API: {'ON' if self.config['use_news_sentiment'] else 'OFF'}")
        print(f"   Advanced Orders: {'ON' if self.config['use_advanced_orders'] else 'OFF'}")
        print("=" * 80 + "\n")
        
        # Send startup notification
        mode_telegram = mode.upper()
        self.infra.notifications.send(
            f"✅ TPS19 System Started\n"
            f"Mode: {mode_telegram}\n"
            f"Real-time: {'ON' if self.config['use_websocket'] else 'OFF'}\n"
            f"News API: {'ON' if self.config['use_news_sentiment'] else 'OFF'}\n"
            f"Pairs: {', '.join(self.config['pairs'])}",
            "HIGH",
            trading_status=mode_telegram
        )
    
    async def start_websocket(self):
        """Start WebSocket for real-time data"""
        if not self.config['use_websocket']:
            return
        
        try:
            self.websocket = WebSocketLayer()
            await self.websocket.connect('cryptocom')
            
            for symbol in self.config['pairs']:
                await self.websocket.subscribe_ticker(symbol)
            
            print("✅ WebSocket streaming active")
        except Exception as e:
            print(f"⚠️  WebSocket failed: {e}")
            self.config['use_websocket'] = False
    
    def get_price(self, symbol: str) -> float:
        """Get latest price (WebSocket or REST)"""
        if self.config['use_websocket'] and self.websocket:
            data = self.websocket.get_latest_price(symbol)
            if data:
                return data.get('last', 0)
        
        # Fallback to REST
        try:
            ticker = self.exchange.fetch_ticker(symbol) if self.exchange else {}
            return ticker.get('last', 0)
        except:
            return 0
    
    def execute_signal(self, symbol: str, signal: str, size: float, price: float) -> Dict:
        """Execute trading signal based on mode"""
        
        if self.mode == 'live':
            # LIVE TRADING
            if self.config['use_advanced_orders'] and self.advanced_orders:
                if signal == 'buy':
                    result = self.advanced_orders.place_limit_order(symbol, 'buy', size, price)
                    if result['success']:
                        # Add protective stops
                        self.advanced_orders.place_stop_loss(symbol, 'sell', size, price * 0.98)
                    return result
                else:
                    return self.advanced_orders.place_limit_order(symbol, 'sell', size, price)
            else:
                return self.execution.execute_market_order(symbol, signal, size)
        
        elif self.mode == 'paper':
            # PAPER TRADING
            return self.paper_trading.place_market_order(symbol, signal, size, price)
        
        else:
            # MONITORING
            return {'success': False, 'mode': 'monitoring', 'signal': signal}
    
    def process_symbol(self, symbol: str) -> Dict:
        """Process one symbol"""
        try:
            # Get market data
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1m', limit=100) if self.exchange else []
            if not ohlcv:
                return {'error': 'No data'}
            
            # Get current price
            price = self.get_price(symbol)
            
            # Market analysis
            analysis = self.analysis.analyze_comprehensive(ohlcv)
            
            # Get news sentiment
            if self.config['use_news_sentiment']:
                crypto = symbol.replace('/USDT', '')
                sentiment = self.news_api.get_sentiment_summary(crypto)
                analysis['news_sentiment'] = sentiment
            
            # Generate signal
            technical_signal = self.signals.generate_unified_signal(analysis)
            
            # AI prediction
            if self.config['use_ai_predictions']:
                ai_prediction = self.ai.predict_all(ohlcv)
            else:
                ai_prediction = {'signal': 'HOLD', 'confidence': 0}
            
            # Combine signals
            final_signal = self.combine_signals(technical_signal, ai_prediction)
            
            # Risk check
            risk_check = self.risk.validate_trade(final_signal, analysis, symbol)
            
            # Execute if approved
            if risk_check['approved'] and final_signal['confidence'] >= self.config['min_confidence']:
                result = self.execute_signal(
                    symbol,
                    final_signal['signal'],
                    risk_check['position_size'],
                    price
                )
                
                if result.get('success'):
                    self.state['trades_today'] += 1
                    
                    # Log and notify
                    mode_prefix = {
                        'monitoring': '📊 SIGNAL',
                        'paper': '🧪 PAPER',
                        'live': '✅ LIVE'
                    }[self.mode]
                    
                    self.infra.notifications.send(
                        f"{mode_prefix} TRADE:\n"
                        f"{final_signal['signal'].upper()} {symbol} @ ${price:.2f}\n"
                        f"Size: {risk_check['position_size']:.6f}\n"
                        f"Confidence: {final_signal['confidence']:.0%}",
                        "NORMAL",
                        trading_status=self.mode.upper()
                    )
                
                return result
            
            return {'action': 'HOLD', 'price': price, 'signal': final_signal}
        
        except Exception as e:
            self.infra.logger.error(f"Error processing {symbol}: {e}", "PROCESS")
            return {'error': str(e)}
    
    def combine_signals(self, technical: Dict, ai: Dict) -> Dict:
        """Combine technical and AI signals"""
        tech_signal = technical.get('signal', 'HOLD')
        ai_signal = ai.get('signal', 'HOLD')
        
        if tech_signal == ai_signal:
            return {
                'signal': tech_signal.lower(),
                'confidence': (technical.get('confidence', 0.5) + ai.get('confidence', 0.5)) / 2
            }
        else:
            return {'signal': 'hold', 'confidence': 0.4}
    
    async def run_async(self):
        """Main trading loop (async)"""
        print("🚀 TPS19 Trading System Active\n")
        
        # Start WebSocket
        if self.config['use_websocket']:
            await self.start_websocket()
        
        try:
            while True:
                self.state['cycle'] += 1
                cycle = self.state['cycle']
                
                print(f"\n{'='*60}")
                print(f"Cycle {cycle} | Mode: {self.mode.upper()}")
                print(f"{'='*60}")
                
                # Process each pair
                for symbol in self.config['pairs']:
                    result = self.process_symbol(symbol)
                    print(f"{symbol}: {result.get('action', result.get('signal', 'PROCESSED'))}")
                
                # Status update every 30 cycles
                if cycle % 30 == 0:
                    uptime = (datetime.now() - self.state['start_time']).seconds // 60
                    
                    extra = ""
                    if self.mode == 'paper':
                        prices = {s: self.get_price(s) for s in self.config['pairs']}
                        stats = self.paper_trading.get_portfolio_stats(prices)
                        extra = (
                            f"\n📊 Paper Stats:\n"
                            f"Equity: ${stats['total_equity']:.2f}\n"
                            f"P&L: ${stats['total_pnl']:.2f} ({stats['total_return_pct']:.2f}%)"
                        )
                    
                    self.infra.notifications.send(
                        f"💓 Status Update\n"
                        f"Cycle: {cycle} | Uptime: {uptime}min\n"
                        f"Trades: {self.state['trades_today']}"
                        f"{extra}",
                        "NORMAL",
                        trading_status=self.mode.upper()
                    )
                
                await asyncio.sleep(self.config['update_interval'])
        
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            
            if self.mode == 'paper':
                print("\n" + "="*60)
                print("📊 PAPER TRADING FINAL RESULTS")
                print("="*60)
                prices = {s: self.get_price(s) for s in self.config['pairs']}
                stats = self.paper_trading.get_portfolio_stats(prices)
                print(f"Initial: ${stats['initial_balance']:,.2f}")
                print(f"Final: ${stats['total_equity']:,.2f}")
                print(f"P&L: ${stats['total_pnl']:,.2f} ({stats['total_return_pct']:.2f}%)")
                print(f"Win Rate: {stats['win_rate']:.1f}%")
                print("="*60 + "\n")
            
            if self.websocket:
                await self.websocket.close()
            
            print("✅ Shutdown complete")
    
    def run(self):
        """Run the system"""
        asyncio.run(self.run_async())


if __name__ == '__main__':
    import sys
    
    # Get mode from command line or default to paper
    mode = sys.argv[1] if len(sys.argv) > 1 else 'paper'
    
    if mode not in ['monitoring', 'paper', 'live']:
        print(f"❌ Invalid mode: {mode}")
        print("Usage: python3 tps19_integrated.py [monitoring|paper|live]")
        print("\nDefaults to 'paper' if no mode specified")
        sys.exit(1)
    
    print(f"\n{'⚠️'*20}")
    if mode == 'live':
        print("⚠️  LIVE TRADING MODE - REAL MONEY AT RISK")
        print(f"{'⚠️'*20}\n")
        response = input("Are you sure? Type 'YES' to continue: ")
        if response != 'YES':
            print("Aborted.")
            sys.exit(0)
    
    tps19 = TPS19Integrated(mode=mode)
    tps19.run()
