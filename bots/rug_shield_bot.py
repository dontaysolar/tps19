#!/usr/bin/env python3
"""
Rug Shield AI Bot
Filters scam/low-liquidity assets
Part of APEX AI Trading System
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
except ImportError:
    os.system("pip3 install --break-system-packages ccxt -q")
    import ccxt

class RugShieldBot:
    """Protects against scams and low-liquidity assets"""
    
    def __init__(self, exchange_config: Dict = None):
        self.name = "RugShieldBot"
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
        
        self.config = {
            'min_liquidity_usd': 1000000,    # $1M minimum liquidity
            'min_volume_24h_usd': 100000,    # $100k minimum 24h volume
            'max_spread_pct': 1.0,           # Max 1% spread
            'min_age_days': 30,              # Minimum 30 days old
            'blacklist': []                  # Manually blacklisted symbols
        }
        
        self.safe_assets = {}
        self.blocked_assets = {}
        
        self.metrics = {
            'assets_checked': 0,
            'assets_blocked': 0,
            'scams_prevented': 0
        }
    
    def check_liquidity(self, symbol: str) -> Dict:
        """Check if asset has sufficient liquidity"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            orderbook = self.exchange.fetch_order_book(symbol, limit=20)
            
            # Calculate bid/ask spread
            spread_pct = ((ticker['ask'] - ticker['bid']) / ticker['bid']) * 100 if ticker['bid'] > 0 else 100
            
            # Calculate 24h volume
            volume_24h_usd = ticker.get('quoteVolume', 0)
            
            # Calculate order book depth
            bid_depth = sum(order[1] if isinstance(order, (list, tuple)) and len(order) > 1 else 0 
                           for order in orderbook['bids'][:10])
            ask_depth = sum(order[1] if isinstance(order, (list, tuple)) and len(order) > 1 else 0 
                           for order in orderbook['asks'][:10])
            total_depth_usd = ((bid_depth + ask_depth) / 2) * ticker['last']
            
            self.metrics['assets_checked'] += 1
            
            return {
                'symbol': symbol,
                'spread_pct': spread_pct,
                'volume_24h_usd': volume_24h_usd,
                'liquidity_usd': total_depth_usd,
                'bid_depth': bid_depth,
                'ask_depth': ask_depth,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Liquidity check error: {e}")
            return {}
    
    def is_safe_asset(self, symbol: str) -> Dict:
        """Comprehensive safety check for an asset"""
        # Check blacklist
        if symbol in self.config['blacklist']:
            self.metrics['assets_blocked'] += 1
            return {
                'safe': False,
                'symbol': symbol,
                'reason': 'Blacklisted',
                'risk_level': 'CRITICAL'
            }
        
        # Check liquidity
        liquidity = self.check_liquidity(symbol)
        
        if not liquidity:
            return {
                'safe': False,
                'symbol': symbol,
                'reason': 'Liquidity check failed',
                'risk_level': 'HIGH'
            }
        
        # Evaluate safety
        issues = []
        risk_score = 0
        
        # Check spread
        if liquidity['spread_pct'] > self.config['max_spread_pct']:
            issues.append(f"High spread: {liquidity['spread_pct']:.2f}%")
            risk_score += 30
        
        # Check volume (handle None)
        volume_24h = liquidity.get('volume_24h_usd', 0) or 0
        if volume_24h < self.config['min_volume_24h_usd']:
            issues.append(f"Low volume: ${volume_24h:,.0f}")
            risk_score += 40
        
        # Check liquidity (handle None)
        liquidity_usd = liquidity.get('liquidity_usd', 0) or 0
        if liquidity_usd < self.config['min_liquidity_usd']:
            issues.append(f"Low liquidity: ${liquidity_usd:,.0f}")
            risk_score += 30
        
        # Determine safety
        is_safe = risk_score < 50
        
        if not is_safe:
            self.metrics['assets_blocked'] += 1
            self.blocked_assets[symbol] = datetime.now().isoformat()
        else:
            self.safe_assets[symbol] = datetime.now().isoformat()
        
        risk_level = 'LOW' if risk_score < 30 else 'MEDIUM' if risk_score < 50 else 'HIGH' if risk_score < 80 else 'CRITICAL'
        
        return {
            'safe': is_safe,
            'symbol': symbol,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'issues': issues,
            'liquidity_data': liquidity,
            'timestamp': datetime.now().isoformat()
        }
    
    def filter_safe_pairs(self, symbols: List[str]) -> List[str]:
        """Filter list to only safe trading pairs"""
        safe = []
        
        for symbol in symbols:
            check = self.is_safe_asset(symbol)
            if check['safe']:
                safe.append(symbol)
            else:
                print(f"🚫 Blocked {symbol}: {', '.join(check['issues'])}")
        
        return safe
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'safe_assets': len(self.safe_assets),
            'blocked_assets': len(self.blocked_assets),
            'metrics': self.metrics,
            'config': self.config
        }

if __name__ == '__main__':
    bot = RugShieldBot()
    print("🛡️ Rug Shield Bot - Test Mode\n")
    
    result = bot.is_safe_asset('BTC/USDT')
    print(f"Asset: {result['symbol']}")
    print(f"Safe: {result['safe']}")
    print(f"Risk Level: {result['risk_level']}")
