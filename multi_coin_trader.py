#!/usr/bin/env python3
"""
Multi-Coin Trading Engine
Trades BTC, ETH, SOL, ADA simultaneously with position management
"""

import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

try:
    import ccxt
except ImportError:
    print("Installing ccxt...")
    os.system("pip3 install --break-system-packages ccxt -q")
    import ccxt

class MultiCoinTrader:
    """Manages trading across multiple coins"""
    
    def __init__(self):
        load_dotenv()
        
        # Initialize exchange
        self.exchange = ccxt.crypto_com({
            'apiKey': os.getenv('EXCHANGE_API_KEY'),
            'secret': os.getenv('EXCHANGE_API_SECRET'),
            'enableRateLimit': True
        })
        
        # Trading pairs
        self.pairs = {
            'BTC/USDT': {'weight': 0.40, 'min_size': 0.00001},
            'ETH/USDT': {'weight': 0.30, 'min_size': 0.0001},
            'SOL/USDT': {'weight': 0.15, 'min_size': 0.01},
            'ADA/USDT': {'weight': 0.15, 'min_size': 1.0}
        }
        
        self.positions = {}
        self.max_position_size = 0.5  # $0.50 per trade
        
    def get_balance(self):
        """Get USDT balance"""
        try:
            balance = self.exchange.fetch_balance()
            return balance['USDT']['free']
        except Exception as e:
            print(f"Balance error: {e}")
            return 0.0
    
    def calculate_position_size(self, symbol, price):
        """Calculate position size based on balance and weights"""
        try:
            balance = self.get_balance()
            
            # Allocate by weight
            allocated = balance * self.pairs[symbol]['weight']
            
            # Cap at max position size
            allocated = min(allocated, self.max_position_size)
            
            # Convert to coin amount
            amount = allocated / price
            
            # Check minimum
            if amount < self.pairs[symbol]['min_size']:
                return 0.0
            
            return amount
            
        except Exception as e:
            print(f"Position size error for {symbol}: {e}")
            return 0.0
    
    def place_order(self, symbol, side, amount):
        """Place market order"""
        try:
            if side == 'buy':
                order = self.exchange.create_market_buy_order(symbol, amount)
            else:
                order = self.exchange.create_market_sell_order(symbol, amount)
            
            print(f"✅ {side.upper()} {amount} {symbol} @ ${order.get('price', 0):.2f}")
            
            return order
            
        except Exception as e:
            print(f"Order error for {symbol}: {e}")
            return None
    
    def should_trade(self, symbol, sentiment_score):
        """Determine if should trade based on sentiment"""
        # Only trade if sentiment is strong enough
        if abs(sentiment_score) < 0.3:
            return False, None
        
        # Check if already have position
        if symbol in self.positions:
            return False, None
        
        # Determine side
        side = 'buy' if sentiment_score > 0 else 'sell'
        
        return True, side
    
    def execute_strategy(self, sentiments):
        """Execute trading strategy across all pairs"""
        for symbol in self.pairs.keys():
            coin = symbol.split('/')[0]
            sentiment = sentiments.get(coin, 0)
            
            should_trade, side = self.should_trade(symbol, sentiment)
            
            if not should_trade:
                continue
            
            # Get current price
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                price = ticker['last']
            except:
                continue
            
            # Calculate position size
            amount = self.calculate_position_size(symbol, price)
            
            if amount == 0:
                print(f"⚠️  {symbol}: Amount too small (${amount * price:.2f})")
                continue
            
            # Place order
            order = self.place_order(symbol, side, amount)
            
            if order:
                self.positions[symbol] = {
                    'side': side,
                    'amount': amount,
                    'entry_price': price,
                    'timestamp': datetime.now().isoformat()
                }
    
    def close_all_positions(self):
        """Close all open positions"""
        for symbol, pos in list(self.positions.items()):
            side = 'sell' if pos['side'] == 'buy' else 'buy'
            self.place_order(symbol, side, pos['amount'])
            del self.positions[symbol]

if __name__ == '__main__':
    # Test multi-coin trading
    trader = MultiCoinTrader()
    
    print("💰 Current Balance:")
    print(f"   USDT: ${trader.get_balance():.2f}")
    
    print("\n📊 Trading Pairs:")
    for symbol, config in trader.pairs.items():
        print(f"   {symbol}: {config['weight']*100:.0f}% allocation")
    
    # Simulate with dummy sentiment
    dummy_sentiment = {
        'BTC': 0.5,  # Bullish
        'ETH': 0.4,  # Moderately bullish
        'SOL': -0.2, # Neutral/bearish
        'ADA': 0.6   # Very bullish
    }
    
    print("\n🧠 Sentiment Scores:")
    for coin, score in dummy_sentiment.items():
        print(f"   {coin}: {score:+.2f}")
    
    print("\n🚀 Executing strategy...")
    trader.execute_strategy(dummy_sentiment)
