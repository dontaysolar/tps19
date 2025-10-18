#!/usr/bin/env python3
"""
Backtesting Engine
Tests trading strategies on historical data
Part of APEX AI Trading System
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Callable

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
    import numpy as np
    import pandas as pd
except ImportError:
    os.system("pip3 install --break-system-packages ccxt numpy pandas -q")
    import ccxt
    import numpy as np
    import pandas as pd

class BacktestingEngine:
    """Backtests trading strategies on historical market data"""
    
    def __init__(self, exchange_config=None):
        self.name = "BacktestingEngine"
        self.version = "1.0.0"
        
        if exchange_config:
            self.exchange = ccxt.cryptocom(exchange_config)
        else:
            from dotenv import load_dotenv
            load_dotenv()
            self.exchange = ccxt.cryptocom({
                'apiKey': os.getenv('EXCHANGE_API_KEY'),
                'secret': os.getenv('EXCHANGE_API_SECRET'),
                'enableRateLimit': True
            })
        
        self.results = {}
    
    def fetch_historical_data(self, symbol: str, timeframe: str, days: int = 30) -> pd.DataFrame:
        """Fetch historical OHLCV data"""
        try:
            since = self.exchange.parse8601((datetime.now() - timedelta(days=days)).isoformat())
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
            
        except Exception as e:
            print(f"❌ Data fetch error: {e}")
            return pd.DataFrame()
    
    def backtest_strategy(self, symbol: str, strategy_func: Callable, initial_balance: float = 3.0, 
                         days: int = 30, timeframe: str = '1h') -> Dict:
        """
        Backtest a trading strategy
        
        Args:
            symbol: Trading pair
            strategy_func: Function(df) -> List[Dict] returning trade signals
            initial_balance: Starting balance in USDT
            days: Days of historical data
            timeframe: Candlestick timeframe
            
        Returns:
            Backtest results dictionary
        """
        print(f"🔍 Backtesting {symbol} - {days} days - {timeframe}")
        
        # Fetch data
        df = self.fetch_historical_data(symbol, timeframe, days)
        
        if df.empty:
            return {'error': 'No data'}
        
        # Run strategy
        signals = strategy_func(df)
        
        # Simulate trades
        balance = initial_balance
        position = None
        trades = []
        
        for signal in signals:
            if signal['action'] == 'buy' and position is None:
                # Enter long position
                amount = (balance * signal.get('size', 0.9)) / signal['price']
                position = {
                    'type': 'long',
                    'entry_price': signal['price'],
                    'amount': amount,
                    'entry_time': signal['timestamp']
                }
                balance -= amount * signal['price']
                
            elif signal['action'] == 'sell' and position is not None:
                # Close position
                exit_value = position['amount'] * signal['price']
                profit = exit_value - (position['amount'] * position['entry_price'])
                profit_pct = (profit / (position['amount'] * position['entry_price'])) * 100
                
                trades.append({
                    'entry_price': position['entry_price'],
                    'exit_price': signal['price'],
                    'amount': position['amount'],
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'entry_time': position['entry_time'],
                    'exit_time': signal['timestamp']
                })
                
                balance += exit_value
                position = None
        
        # Close any open position at last price
        if position is not None:
            last_price = df.iloc[-1]['close']
            exit_value = position['amount'] * last_price
            profit = exit_value - (position['amount'] * position['entry_price'])
            
            trades.append({
                'entry_price': position['entry_price'],
                'exit_price': last_price,
                'amount': position['amount'],
                'profit': profit,
                'profit_pct': (profit / (position['amount'] * position['entry_price'])) * 100,
                'entry_time': position['entry_time'],
                'exit_time': df.iloc[-1]['timestamp'],
                'status': 'open_at_end'
            })
            
            balance += exit_value
        
        # Calculate metrics
        if not trades:
            return {'error': 'No trades generated'}
        
        total_profit = sum(t['profit'] for t in trades)
        wins = [t for t in trades if t['profit'] > 0]
        losses = [t for t in trades if t['profit'] <= 0]
        
        win_rate = (len(wins) / len(trades)) * 100 if trades else 0
        avg_win = sum(t['profit'] for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t['profit'] for t in losses) / len(losses) if losses else 0
        profit_factor = abs(sum(t['profit'] for t in wins) / sum(t['profit'] for t in losses)) if losses and sum(t['profit'] for t in losses) != 0 else 0
        
        max_drawdown = 0
        peak = initial_balance
        
        running_balance = initial_balance
        for trade in trades:
            running_balance += trade['profit']
            if running_balance > peak:
                peak = running_balance
            drawdown = ((peak - running_balance) / peak) * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        final_balance = balance
        roi = ((final_balance - initial_balance) / initial_balance) * 100
        
        result = {
            'symbol': symbol,
            'timeframe': timeframe,
            'period_days': days,
            'initial_balance': initial_balance,
            'final_balance': final_balance,
            'total_profit': total_profit,
            'roi': roi,
            'total_trades': len(trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'trades': trades,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results[f"{symbol}_{timeframe}_{days}d"] = result
        
        return result
    
    def compare_strategies(self, symbol: str, strategies: Dict[str, Callable], days: int = 30) -> Dict:
        """Compare multiple strategies"""
        results = {}
        
        for name, strategy in strategies.items():
            print(f"\n📊 Testing strategy: {name}")
            result = self.backtest_strategy(symbol, strategy, days=days)
            results[name] = result
        
        # Rank by ROI
        rankings = sorted(results.items(), key=lambda x: x[1].get('roi', 0), reverse=True)
        
        return {
            'symbol': symbol,
            'strategies_tested': len(strategies),
            'results': results,
            'rankings': [(name, r.get('roi', 0)) for name, r in rankings],
            'best_strategy': rankings[0][0] if rankings else None
        }
    
    def save_results(self, filepath: str = 'data/backtest_results.json'):
        """Save backtest results"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            'name': self.name,
            'version': self.version,
            'tests_run': len(self.results)
        }

# Example strategies
def simple_ma_crossover_strategy(df: pd.DataFrame) -> List[Dict]:
    """Simple moving average crossover strategy"""
    df['MA_short'] = df['close'].rolling(window=7).mean()
    df['MA_long'] = df['close'].rolling(window=25).mean()
    
    signals = []
    
    for i in range(1, len(df)):
        # Golden cross - buy
        if df.iloc[i-1]['MA_short'] <= df.iloc[i-1]['MA_long'] and df.iloc[i]['MA_short'] > df.iloc[i]['MA_long']:
            signals.append({
                'action': 'buy',
                'price': df.iloc[i]['close'],
                'timestamp': df.iloc[i]['timestamp'],
                'size': 0.9
            })
        
        # Death cross - sell
        elif df.iloc[i-1]['MA_short'] >= df.iloc[i-1]['MA_long'] and df.iloc[i]['MA_short'] < df.iloc[i]['MA_long']:
            signals.append({
                'action': 'sell',
                'price': df.iloc[i]['close'],
                'timestamp': df.iloc[i]['timestamp']
            })
    
    return signals

def rsi_strategy(df: pd.DataFrame) -> List[Dict]:
    """RSI-based mean reversion strategy"""
    # Calculate RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    signals = []
    in_position = False
    
    for i in range(14, len(df)):
        # Oversold - buy
        if df.iloc[i]['RSI'] < 30 and not in_position:
            signals.append({
                'action': 'buy',
                'price': df.iloc[i]['close'],
                'timestamp': df.iloc[i]['timestamp'],
                'size': 0.9
            })
            in_position = True
        
        # Overbought - sell
        elif df.iloc[i]['RSI'] > 70 and in_position:
            signals.append({
                'action': 'sell',
                'price': df.iloc[i]['close'],
                'timestamp': df.iloc[i]['timestamp']
            })
            in_position = False
    
    return signals

if __name__ == '__main__':
    engine = BacktestingEngine()
    
    print("🧪 Backtesting Engine - Test Mode\n")
    
    # Test MA crossover
    result = engine.backtest_strategy('BTC/USDT', simple_ma_crossover_strategy, days=30)
    
    print(f"\n📊 Results:")
    print(f"   ROI: {result.get('roi', 0):.2f}%")
    print(f"   Trades: {result.get('total_trades', 0)}")
    print(f"   Win Rate: {result.get('win_rate', 0):.1f}%")
    print(f"   Profit Factor: {result.get('profit_factor', 0):.2f}")
    print(f"   Max Drawdown: {result.get('max_drawdown', 0):.2f}%")
    
    engine.save_results()
