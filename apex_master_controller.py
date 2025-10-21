#!/usr/bin/env python3
"""
APEX Master Controller
Orchestrates all 5 bots + Phase 1 features into unified trading system
Part of APEX AI Trading System
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from typing import Dict, List

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bots'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

# Import all bots
from dynamic_stoploss_bot import DynamicStopLossBot
from fee_optimizer_bot import FeeOptimizerBot
from whale_monitor_bot import WhaleMonitorBot
from crash_shield_bot import CrashShieldBot
from capital_rotator_bot import CapitalRotatorBot

# Import Phase 1 features
from sentiment_analyzer import SentimentAnalyzer
from multi_coin_trader import MultiCoinTrader
from trailing_stoploss import TrailingStopLoss
from enhanced_notifications import EnhancedNotifications

class APEXMasterController:
    """
    Master controller coordinating all APEX bots and features
    
    Architecture:
    - Central NEXUS pattern
    - Autonomous bot coordination
    - Real-time market monitoring
    - Integrated risk management
    """
    
    def __init__(self):
        self.name = "APEX_Master_Controller"
        self.version = "1.0.0"
        self.running = False
        
        print(f"🚀 Initializing {self.name} v{self.version}")
        
        # Initialize all bots
        print("📦 Loading bots...")
        self.bots = {
            'dynamic_sl': DynamicStopLossBot(),
            'fee_optimizer': FeeOptimizerBot(),
            'whale_monitor': WhaleMonitorBot(),
            'crash_shield': CrashShieldBot(),
            'capital_rotator': CapitalRotatorBot()
        }
        
        # Initialize Phase 1 features
        print("📦 Loading Phase 1 features...")
        self.features = {
            'sentiment': SentimentAnalyzer(),
            'trader': MultiCoinTrader(),
            'trailing_sl': TrailingStopLoss(),
            'notifications': EnhancedNotifications()
        }
        
        # Trading configuration
        self.config = {
            'trading_pairs': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT'],
            'max_position_size': 0.50,  # $0.50 per trade
            'sentiment_threshold': 0.3,  # Minimum sentiment for trade
            'check_interval': 60,        # Check every 60 seconds
            'rebalance_interval': 21600  # Rebalance every 6 hours
        }
        
        # System state
        self.state = {
            'trading_enabled': True,
            'positions': {},
            'last_sentiment_check': None,
            'last_rebalance': None,
            'cycle_count': 0
        }
        
        # Metrics
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_profit': 0.0,
            'bot_actions': {bot: 0 for bot in self.bots.keys()},
            'start_time': datetime.now().isoformat()
        }
        
        print("✅ APEX Master Controller initialized")
    
    def trading_cycle(self):
        """Main trading cycle - runs continuously"""
        print(f"\n🔄 CYCLE #{self.state['cycle_count'] + 1} - {datetime.now()}")
        
        try:
            # STEP 1: Check for market crash
            crash_status = self.bots['crash_shield'].monitor_market(self.config['trading_pairs'])
            
            if crash_status['trading_paused']:
                print(f"🛑 Trading paused: {crash_status['pause_reason']}")
                self.state['trading_enabled'] = False
                return
            else:
                self.state['trading_enabled'] = True
            
            # STEP 2: Monitor for whale activity
            for symbol in self.config['trading_pairs']:
                whale_data = self.bots['whale_monitor'].monitor_symbol(symbol)
                
                if whale_data['alert_level'] != "NORMAL":
                    print(f"🐋 {symbol}: {whale_data['alert_level']}")
                    self.features['notifications'].send_message(
                        f"🐋 *Whale Alert*\n{symbol}: {whale_data['alert_level']}"
                    )
            
            # STEP 3: Get sentiment for all pairs
            sentiments = self.features['sentiment'].get_all_sentiments()
            self.state['last_sentiment_check'] = datetime.now().isoformat()
            
            print(f"\n🧠 Sentiment Analysis:")
            for coin, score in sentiments.items():
                signal, confidence = self.features['sentiment'].get_signal(coin)
                print(f"   {coin}: {score:+.2f} → {signal}")
            
            # STEP 4: Check if capital rebalancing needed
            rebalance_result = self.bots['capital_rotator'].rebalance_capital(
                self.config['trading_pairs']
            )
            
            if rebalance_result.get('rebalanced'):
                print(f"\n🔄 Capital rebalanced:")
                for symbol, alloc in rebalance_result['new_allocations'].items():
                    print(f"   {symbol}: {alloc*100:.1f}%")
                
                self.state['last_rebalance'] = datetime.now().isoformat()
            
            # STEP 5: Evaluate trading opportunities
            for symbol in self.config['trading_pairs']:
                coin = symbol.split('/')[0]
                sentiment = sentiments.get(coin, 0)
                
                # Only trade if sentiment strong enough
                if abs(sentiment) < self.config['sentiment_threshold']:
                    continue
                
                # Calculate position size
                amount = self.features['trader'].calculate_position_size(
                    symbol,
                    self.bots['capital_rotator'].allocations.get(symbol, 0.25)
                )
                
                if amount == 0:
                    continue
                
                # Optimize trade (check fees & slippage)
                side = 'buy' if sentiment > 0 else 'sell'
                optimization = self.bots['fee_optimizer'].optimize_order(symbol, amount, side)
                
                if not optimization:
                    continue
                
                # Check if optimization recommends execution
                if optimization['recommendation'] == "HIGH_COST_WARNING":
                    print(f"⚠️  {symbol}: High cost ({optimization['total_cost_pct']:.2f}%), skipping")
                    continue
                
                print(f"\n💰 Trade Opportunity: {symbol}")
                print(f"   Sentiment: {sentiment:+.2f}")
                print(f"   Side: {side.upper()}")
                print(f"   Amount: {amount:.6f}")
                print(f"   Total Cost: {optimization['total_cost_pct']:.2f}%")
                
                # Execute trade (would place real order here)
                # For now, just log and notify
                self.features['notifications'].trade_entry_alert(
                    symbol, side, amount,
                    optimization['order_value'] / amount,
                    sentiment=sentiment,
                    strategy="APEX_Sentiment_Driven"
                )
                
                # Add to tracked positions with dynamic stop-loss
                pos_id = self.bots['dynamic_sl'].add_position(
                    symbol,
                    optimization['order_value'] / amount,
                    amount,
                    'long' if side == 'buy' else 'short'
                )
                
                self.state['positions'][symbol] = pos_id
                self.metrics['total_trades'] += 1
            
            # STEP 6: Monitor existing positions
            for symbol, pos_id in list(self.state['positions'].items()):
                # Update stop-loss based on current price
                try:
                    ticker = self.features['trader'].exchange.fetch_ticker(symbol)
                    current_price = ticker['last']
                    
                    close_data = self.bots['dynamic_sl'].update_stop_loss(pos_id, current_price)
                    
                    if close_data:
                        # Position closed
                        print(f"\n🛑 Position closed: {symbol}")
                        print(f"   P&L: ${close_data['profit']:.2f} ({close_data['profit_pct']:+.2f}%)")
                        
                        # Update metrics
                        if close_data['profit'] > 0:
                            self.metrics['winning_trades'] += 1
                        self.metrics['total_profit'] += close_data['profit']
                        
                        # Notify
                        self.features['notifications'].trade_exit_alert(
                            symbol,
                            'sell' if close_data['side'] == 'long' else 'buy',
                            close_data['amount'],
                            close_data['entry'],
                            close_data['exit'],
                            close_data['profit'],
                            close_data['profit_pct'],
                            close_data['reason']
                        )
                        
                        # Remove from tracking
                        del self.state['positions'][symbol]
                        
                except Exception as e:
                    print(f"❌ Position monitoring error for {symbol}: {e}")
            
            self.state['cycle_count'] += 1
            
        except Exception as e:
            print(f"❌ Trading cycle error: {e}")
            import traceback
            traceback.print_exc()
    
    def start(self):
        """Start the master controller"""
        print("\n" + "="*70)
        print(f"🚀 STARTING {self.name}")
        print("="*70)
        
        self.running = True
        
        # Send startup notification
        self.features['notifications'].send_message(
            f"🚀 *APEX System Online*\n\n"
            f"Version: {self.version}\n"
            f"Bots Active: {len(self.bots)}\n"
            f"Trading Pairs: {len(self.config['trading_pairs'])}\n"
            f"Max Position: ${self.config['max_position_size']:.2f}\n\n"
            f"Ready to trade! 💰"
        )
        
        try:
            while self.running:
                self.trading_cycle()
                
                # Wait for next cycle
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping APEX Controller...")
            self.stop()
    
    def stop(self):
        """Stop the master controller"""
        self.running = False
        
        # Generate final report
        win_rate = (self.metrics['winning_trades'] / self.metrics['total_trades'] * 100) if self.metrics['total_trades'] > 0 else 0
        
        report = f"""
📊 *APEX System Shutdown Report*

*Performance:*
Total Trades: {self.metrics['total_trades']}
Winning Trades: {self.metrics['winning_trades']}
Win Rate: {win_rate:.1f}%
Total P&L: ${self.metrics['total_profit']:+.2f}

*Runtime:*
Cycles Completed: {self.state['cycle_count']}
Start Time: {self.metrics['start_time']}
End Time: {datetime.now().isoformat()}

System stopped gracefully. 👋
"""
        
        self.features['notifications'].send_message(report)
        
        print("\n✅ APEX Controller stopped")
    
    def get_status(self) -> Dict:
        """Get comprehensive system status"""
        bot_statuses = {name: bot.get_status() for name, bot in self.bots.items()}
        
        return {
            'name': self.name,
            'version': self.version,
            'running': self.running,
            'state': self.state,
            'metrics': self.metrics,
            'config': self.config,
            'bots': bot_statuses
        }

if __name__ == '__main__':
    # Create and start APEX controller
    controller = APEXMasterController()
    
    try:
        controller.start()
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        controller.stop()
