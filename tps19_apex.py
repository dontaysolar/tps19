#!/usr/bin/env python3
"""
TPS19 APEX Organism - Main Entry Point

Brings the organism to life and coordinates all systems
"""

import sys
import time
from datetime import datetime
import pandas as pd
import numpy as np

from modules.organism.orchestrator import trading_organism
from modules.strategies.trend_following import TrendFollowingStrategy
from modules.strategies.mean_reversion import MeanReversionStrategy
from modules.strategies.breakout import BreakoutStrategy
from modules.strategies.momentum import MomentumStrategy
from modules.trading_engine import trading_engine, OrderSide
from modules.exchanges.crypto_com import crypto_com_exchange
from modules.utils.logger import get_logger
from modules.utils.config import config

logger = get_logger(__name__)


class TPS19APEX:
    """The complete organism in action"""
    
    def __init__(self):
        self.organism = trading_organism
        self.engine = trading_engine
        self.exchange = crypto_com_exchange
        self.running = False
        
        # Initialize strategies
        self.strategies = {
            'trend_following': TrendFollowingStrategy(),
            'mean_reversion': MeanReversionStrategy(),
            'breakout': BreakoutStrategy(),
            'momentum': MomentumStrategy(),
        }
        
        logger.info("🧬 TPS19 APEX initialized")
        
    def start(self):
        """Bring organism to life"""
        logger.info("═" * 60)
        logger.info("🧬 TPS19 APEX ORGANISM - AWAKENING")
        logger.info("═" * 60)
        
        # Connect to exchange
        if not self.exchange.connect():
            logger.error("Failed to connect to exchange")
            return
        
        self.running = True
        
        # Log organism birth
        vitals = self.organism.get_vital_signs()
        logger.info(f"💓 Birth: Health {vitals['health_score']:.1f}/100, Status: {vitals['status']}")
        
        try:
            cycle_count = 0
            
            while self.running and self.organism.state['alive']:
                cycle_count += 1
                
                # Heartbeat
                logger.info(f"\n{'='*60}")
                logger.info(f"💓 HEARTBEAT #{cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*60}")
                
                # Get market data for active pairs
                for symbol in ['BTC/USDT', 'ETH/USDT']:
                    self.process_symbol(symbol)
                
                # Monitor organism health
                self.monitor_health()
                
                # Check for weekly evolution
                if self.should_evolve_weekly():
                    logger.info("🧬 Weekly evolution cycle starting...")
                    self.organism.weekly_evolution()
                
                # Sleep between heartbeats
                time.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Organism shutdown initiated...")
            self.shutdown()
        except Exception as e:
            logger.error(f"❌ Critical error: {e}", exc_info=True)
            self.emergency_shutdown()
    
    def process_symbol(self, symbol: str):
        """Process one trading pair"""
        try:
            # Get market data
            market_data = self.get_market_data(symbol)
            if not market_data:
                return
            
            # Get portfolio state
            portfolio = self.get_portfolio_state()
            
            # Organism decides
            decision = self.organism.process_market_cycle(market_data, portfolio)
            
            if decision:
                # Execute
                result = self.execute_decision(decision)
                
                if result and result.get('executed'):
                    # Organism learns
                    self.organism.learn_from_trade(result)
                    
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
    
    def get_market_data(self, symbol: str) -> Dict:
        """Get current market data"""
        try:
            # Get real-time data from exchange
            market_info = self.exchange.get_market_data(symbol)
            
            if not market_info:
                return None
            
            # Generate OHLCV data for strategy analysis
            # In real implementation, fetch historical OHLCV
            df = self.generate_sample_ohlcv(symbol, periods=200)
            
            # Analyze with all strategies
            signals = []
            for strategy_name, strategy in self.strategies.items():
                signal = strategy.analyze(df)
                if signal:
                    signal['symbol'] = symbol
                    signals.append(signal)
            
            return {
                'symbol': symbol,
                'price': market_info['price'],
                'volume': market_info['volume'],
                'volume_24h': market_info['volume_24h'],
                'spread_pct': market_info['spread_pct'],
                'volatility': self.calculate_volatility(df),
                'trend_strength': self.calculate_trend_strength(df),
                'regime': 'trending',  # TODO: Detect regime
                'signals': signals,
                'price_change_10m': 0.01,  # TODO: Calculate real
            }
            
        except Exception as e:
            logger.error(f"Market data error for {symbol}: {e}")
            return None
    
    def generate_sample_ohlcv(self, symbol: str, periods: int = 200) -> pd.DataFrame:
        """Generate sample OHLCV for testing"""
        # TODO: Replace with real historical data fetch
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='5min')
        
        # Simulate price movement
        base_price = 50000 if symbol == 'BTC/USDT' else 3000
        returns = np.random.normal(0.0001, 0.02, periods)
        prices = base_price * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices * np.random.uniform(0.99, 1.01, periods),
            'high': prices * np.random.uniform(1.00, 1.02, periods),
            'low': prices * np.random.uniform(0.98, 1.00, periods),
            'close': prices,
            'volume': np.random.uniform(800, 1200, periods)
        })
        
        return df
    
    def calculate_volatility(self, df: pd.DataFrame) -> float:
        """Calculate volatility"""
        returns = df['close'].pct_change()
        return returns.std() if len(returns) > 1 else 0.05
    
    def calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """Calculate trend strength (0-1)"""
        if len(df) < 50:
            return 0.5
        
        ma20 = df['close'].rolling(20).mean().iloc[-1]
        ma50 = df['close'].rolling(50).mean().iloc[-1]
        
        if pd.isna(ma20) or pd.isna(ma50):
            return 0.5
        
        # Strength based on MA alignment
        diff = abs(ma20 - ma50) / ma50 if ma50 > 0 else 0
        strength = min(diff * 10, 1.0)  # Normalize to 0-1
        
        return strength
    
    def get_portfolio_state(self) -> Dict:
        """Get current portfolio state"""
        portfolio_value = self.engine.get_portfolio_value()
        positions = self.engine.get_all_positions()
        
        # Calculate daily P&L (simplified)
        total_value = portfolio_value.get('total_value', 500)
        
        return {
            'total_value': total_value,
            'available_capital': total_value * 0.8,  # 80% available
            'positions': positions,
            'daily_pnl': 0,  # TODO: Calculate from trades
            'weekly_pnl': 0,
            'current_drawdown': 0,
            'starting_capital': 500,
            'consecutive_losses': 0,
        }
    
    def execute_decision(self, decision: Dict) -> Dict:
        """Execute organism's decision"""
        try:
            symbol = decision['symbol']
            action = OrderSide.BUY if decision['action'] == 'BUY' else OrderSide.SELL
            size_usdt = decision['size_usdt']
            
            logger.info(f"🎯 EXECUTING: {action.value} {symbol} - ${size_usdt:.2f}")
            
            # Place order
            result = self.engine.place_order(
                symbol=symbol,
                side=action,
                amount=size_usdt,
                metadata={
                    'organism': True,
                    'confidence': decision['confidence'],
                    'strategy': decision['strategy'],
                    'health_score': decision.get('health_score', 0)
                }
            )
            
            return {
                'executed': result.get('status') == 'success',
                'pnl': 0,  # Will be calculated later
                'trade_id': result.get('trade_id'),
                'symbol': symbol,
                'action': action.value
            }
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {'executed': False, 'error': str(e)}
    
    def monitor_health(self):
        """Monitor organism health"""
        vitals = self.organism.get_vital_signs()
        
        logger.info(f"\n💚 VITAL SIGNS:")
        logger.info(f"   Health: {vitals['health_score']:.1f}/100")
        logger.info(f"   Consciousness: {vitals['consciousness']:.2f}")
        logger.info(f"   Win Rate: {vitals['win_rate']:.2%}")
        logger.info(f"   Sharpe: {vitals['sharpe_ratio']:.2f}")
        logger.info(f"   Age: {vitals['age_hours']:.1f}h")
        logger.info(f"   Generation: {vitals['generation']}")
        
        if vitals['health_score'] < 70:
            logger.warning(f"⚠️ LOW HEALTH: {vitals['health_score']:.1f}")
        
        if vitals['status'] != 'alive':
            logger.critical(f"🚨 Organism status: {vitals['status']}")
    
    def should_evolve_weekly(self) -> bool:
        """Check if time for weekly evolution"""
        now = datetime.now()
        # Evolve every Sunday at midnight
        return now.weekday() == 6 and now.hour == 0 and now.minute < 1
    
    def shutdown(self):
        """Graceful shutdown"""
        logger.info("🌙 Organism entering planned shutdown...")
        self.running = False
        
        vitals = self.organism.get_vital_signs()
        logger.info(f"Final vitals: Health {vitals['health_score']:.1f}/100, "
                   f"Age {vitals['age_hours']:.1f}h")
    
    def emergency_shutdown(self):
        """Emergency shutdown"""
        logger.critical("🚨 EMERGENCY SHUTDOWN INITIATED")
        self.running = False


if __name__ == "__main__":
    logger.info("🚀 Starting TPS19 APEX Organism...")
    
    system = TPS19APEX()
    system.start()
