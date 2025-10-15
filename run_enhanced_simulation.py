#!/usr/bin/env python3
"""
Run Enhanced TPS19 Simulation
Demonstrates the new realistic simulation capabilities
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from simulation.market_simulator import MarketSimulator, MarketCondition
from simulation.backtesting_engine import BacktestingEngine
from modules.enhanced_trading_engine import EnhancedTradingEngine, TradingMode
from config.settings import settings
from core.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(log_level="INFO", log_format="text")
logger = get_logger(__name__)


async def run_market_simulation():
    """Run a market simulation demonstration"""
    print("\n" + "="*60)
    print("TPS19 ENHANCED MARKET SIMULATION")
    print("="*60 + "\n")
    
    # Create market simulator
    simulator = MarketSimulator()
    
    # Demonstrate different market conditions
    conditions = [
        (MarketCondition.LOW_VOLATILITY, "Calm market with low volatility"),
        (MarketCondition.BULL_RUN, "Bull market - prices trending up"),
        (MarketCondition.HIGH_VOLATILITY, "High volatility - large price swings"),
        (MarketCondition.FLASH_CRASH, "Flash crash - sudden drop"),
        (MarketCondition.RECOVERY, "Recovery phase after crash")
    ]
    
    for condition, description in conditions:
        print(f"\n📊 Simulating: {description}")
        print("-" * 40)
        
        simulator.set_market_condition(condition)
        
        # Run for 10 updates
        for i in range(10):
            prices = simulator.update_prices()
            
            # Show BTC and ETH prices
            btc_price = prices.get("BTC_USDT", 0)
            eth_price = prices.get("ETH_USDT", 0)
            
            # Get stats
            btc_stats = simulator.get_market_stats("BTC_USDT")
            
            print(f"Update {i+1:2d}: BTC ${btc_price:,.2f} ({btc_stats['change_24h']:+.2f}%) | "
                  f"ETH ${eth_price:,.2f} | RSI: {btc_stats['rsi']:.1f}")
            
            await asyncio.sleep(0.1)
    
    print("\n✅ Market simulation complete!")
    return simulator


async def run_backtesting_demo(simulator: MarketSimulator):
    """Run a backtesting demonstration"""
    print("\n" + "="*60)
    print("BACKTESTING DEMONSTRATION")
    print("="*60 + "\n")
    
    # Create backtesting engine
    engine = BacktestingEngine(
        initial_capital=10000,
        commission_rate=0.001,
        max_positions=3
    )
    
    # Set the market simulator
    engine.set_market_simulator(simulator)
    
    # Define a simple strategy
    def trend_following_strategy(market_data, portfolio, timestamp):
        """Simple trend following strategy"""
        signals = []
        
        for symbol, data in market_data.items():
            stats = data["stats"]
            price = data["price"]
            
            # Only trade BTC and ETH
            if symbol not in ["BTC_USDT", "ETH_USDT"]:
                continue
            
            has_position = symbol in portfolio["positions"]
            
            # Entry signal: price above SMA20 and RSI < 70
            if not has_position and price > stats["sma_20"] and stats["rsi"] < 70:
                # Size position as 20% of equity
                position_size = (portfolio["equity"] * 0.2) / price
                
                signals.append({
                    "action": "buy",
                    "symbol": symbol,
                    "quantity": position_size
                })
            
            # Exit signal: price below SMA20 or RSI > 80
            elif has_position and (price < stats["sma_20"] or stats["rsi"] > 80):
                position = portfolio["positions"][symbol]
                
                signals.append({
                    "action": "sell",
                    "symbol": symbol,
                    "quantity": position.quantity
                })
        
        return signals
    
    print("Running backtest with trend following strategy...")
    print("Initial capital: $10,000")
    print("Commission: 0.1%")
    print("Max positions: 3")
    print("\nSimulating 7 days of trading...")
    
    # Run backtest
    results = engine.run_backtest(
        strategy=trend_following_strategy,
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now(),
        symbols=["BTC_USDT", "ETH_USDT"],
        timeframe="5m"
    )
    
    # Display results
    print("\n" + "="*40)
    print("BACKTEST RESULTS")
    print("="*40)
    print(f"Total Return: {results.total_return:+.2%}")
    print(f"Final Capital: ${results.final_capital:,.2f}")
    print(f"Net Profit: ${results.net_profit:,.2f}")
    print(f"\nTotal Trades: {results.total_trades}")
    print(f"Winning Trades: {results.winning_trades}")
    print(f"Losing Trades: {results.losing_trades}")
    print(f"Win Rate: {results.win_rate:.1%}")
    print(f"\nProfit Factor: {results.profit_factor:.2f}")
    print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
    print(f"Max Drawdown: {results.max_drawdown:.2%}")
    print(f"Max Drawdown Duration: {results.max_drawdown_duration}")
    print(f"\nAverage Win: ${results.avg_win:.2f}")
    print(f"Average Loss: ${results.avg_loss:.2f}")
    print(f"Largest Win: ${results.largest_win:.2f}")
    print(f"Largest Loss: ${results.largest_loss:.2f}")
    print(f"\nTotal Commission Paid: ${results.total_commission:.2f}")
    print(f"Exposure Time: {results.exposure_time:.1%}")
    
    return results


async def run_trading_engine_demo():
    """Run trading engine demonstration"""
    print("\n" + "="*60)
    print("ENHANCED TRADING ENGINE DEMONSTRATION")
    print("="*60 + "\n")
    
    # Create trading engine in simulation mode
    engine = EnhancedTradingEngine(mode=TradingMode.SIMULATION)
    
    print("Starting trading engine in SIMULATION mode...")
    await engine.start()
    
    # Let it run for a bit
    print("\nPlacing some test orders...")
    
    # Place a market buy order
    order_id = await engine.place_order(
        symbol="BTC_USDT",
        side="buy",
        quantity=0.001,
        order_type="market"
    )
    print(f"✅ Market buy order placed: {order_id}")
    
    # Place a limit sell order
    current_price = engine.get_current_price("BTC_USDT")
    limit_price = current_price * 1.02  # 2% above current
    
    order_id = await engine.place_order(
        symbol="BTC_USDT",
        side="sell",
        quantity=0.001,
        order_type="limit",
        price=limit_price
    )
    print(f"✅ Limit sell order placed at ${limit_price:.2f}: {order_id}")
    
    # Get order book
    orderbook = engine.get_order_book("BTC_USDT", depth=5)
    print(f"\nOrder Book Spread: ${orderbook['spread']:.2f}")
    print(f"Best Bid: ${orderbook['bids'][0][0]:.2f}" if orderbook['bids'] else "No bids")
    print(f"Best Ask: ${orderbook['asks'][0][0]:.2f}" if orderbook['asks'] else "No asks")
    
    # Let it run for 10 seconds
    print("\nRunning for 10 seconds...")
    await asyncio.sleep(10)
    
    # Get stats
    stats = await engine.get_stats()
    print(f"\nTrading Engine Stats:")
    print(f"- Total Trades: {stats['total_trades']}")
    print(f"- Win Rate: {stats['win_rate']:.1%}")
    print(f"- Active Orders: {stats['active_orders']}")
    print(f"- Open Positions: {stats['open_positions']}")
    
    # Stop engine
    await engine.stop()
    print("\n✅ Trading engine stopped")


async def main():
    """Main demonstration function"""
    print("\n🚀 Starting TPS19 Enhanced Simulation Demo\n")
    
    try:
        # 1. Run market simulation
        simulator = await run_market_simulation()
        
        # 2. Run backtesting demo
        await run_backtesting_demo(simulator)
        
        # 3. Run trading engine demo
        await run_trading_engine_demo()
        
        print("\n" + "="*60)
        print("✨ SIMULATION DEMO COMPLETE! ✨")
        print("="*60)
        print("\nThe enhanced simulation provides:")
        print("✅ Realistic market price movements")
        print("✅ Multiple market conditions (bull, bear, volatile, etc.)")
        print("✅ Market events and their impact")
        print("✅ Order book simulation")
        print("✅ Technical indicators (SMA, RSI)")
        print("✅ Comprehensive backtesting")
        print("✅ Performance metrics")
        print("\nTo run the web dashboard:")
        print("python simulation/simulation_dashboard.py")
        print("\nThen open http://localhost:8000 in your browser")
        
    except Exception as e:
        logger.error(f"Error in demo: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()