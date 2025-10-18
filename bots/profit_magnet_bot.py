#!/usr/bin/env python3
"""
Profit Magnet AI Bot
Identifies high-profit altcoin opportunities
Part of APEX AI Trading System
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
    import numpy as np
except ImportError:
    os.system("pip3 install --break-system-packages ccxt numpy -q")
    import ccxt
    import numpy as np

class ProfitMagnetBot:
    """Discovers high-profit trading opportunities"""
    
    def __init__(self, exchange_config: Dict = None):
        self.name = "ProfitMagnetBot"
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
            'min_profit_potential_pct': 5.0,   # Min 5% profit potential
            'min_volume_usd': 50000,            # Min $50k 24h volume
            'volatility_sweet_spot': (0.03, 0.15),  # 3-15% volatility
            'momentum_threshold': 0.02          # 2% momentum
        }
        
        self.opportunities = []
        
        self.metrics = {
            'scans_performed': 0,
            'opportunities_found': 0,
            'avg_profit_potential': 0.0
        }
    
    def calculate_volatility(self, symbol: str, periods: int = 24) -> float:
        """Calculate recent volatility"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=periods)
            
            if len(ohlcv) < periods:
                return 0.0
            
            closes = [candle[4] for candle in ohlcv]
            returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
            
            volatility = np.std(returns)
            
            return volatility
            
        except Exception as e:
            print(f"❌ Volatility calculation error: {e}")
            return 0.0
    
    def calculate_momentum(self, symbol: str) -> float:
        """Calculate price momentum"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=24)
            
            if len(ohlcv) < 24:
                return 0.0
            
            price_start = ohlcv[0][1]
            price_end = ohlcv[-1][4]
            
            momentum = (price_end - price_start) / price_start
            
            return momentum
            
        except Exception as e:
            print(f"❌ Momentum calculation error: {e}")
            return 0.0
    
    def estimate_profit_potential(self, symbol: str) -> Dict:
        """Estimate profit potential for a symbol"""
        try:
            # Get ticker
            ticker = self.exchange.fetch_ticker(symbol)
            
            # Calculate metrics
            volatility = self.calculate_volatility(symbol)
            momentum = self.calculate_momentum(symbol)
            volume_24h = ticker.get('quoteVolume', 0)
            
            # Calculate profit potential score
            # Higher volatility + positive momentum = higher potential
            profit_potential = (volatility * 100 * (1 + momentum)) if momentum > 0 else 0
            
            # Check if meets criteria
            meets_criteria = (
                profit_potential >= self.config['min_profit_potential_pct'] and
                volume_24h >= self.config['min_volume_usd'] and
                self.config['volatility_sweet_spot'][0] <= volatility <= self.config['volatility_sweet_spot'][1] and
                momentum >= self.config['momentum_threshold']
            )
            
            return {
                'symbol': symbol,
                'profit_potential_pct': profit_potential,
                'volatility': volatility,
                'momentum': momentum,
                'volume_24h_usd': volume_24h,
                'current_price': ticker['last'],
                'meets_criteria': meets_criteria,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Profit potential error: {e}")
            return {}
    
    def scan_opportunities(self, symbols: List[str]) -> List[Dict]:
        """Scan multiple symbols for opportunities"""
        opportunities = []
        
        self.metrics['scans_performed'] += 1
        
        for symbol in symbols:
            potential = self.estimate_profit_potential(symbol)
            
            if potential.get('meets_criteria'):
                opportunities.append(potential)
                self.metrics['opportunities_found'] += 1
        
        # Sort by profit potential
        opportunities.sort(key=lambda x: x['profit_potential_pct'], reverse=True)
        
        # Update average
        if opportunities:
            self.metrics['avg_profit_potential'] = sum(o['profit_potential_pct'] for o in opportunities) / len(opportunities)
        
        return opportunities
    
    def get_top_opportunities(self, limit: int = 5) -> List[Dict]:
        """Get top profit opportunities"""
        if not self.opportunities:
            return []
        
        return self.opportunities[:limit]
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'opportunities_found': len(self.opportunities),
            'metrics': self.metrics,
            'config': self.config
        }

if __name__ == '__main__':
    bot = ProfitMagnetBot()
    print("🧲 Profit Magnet Bot - Test Mode\n")
    
    opportunities = bot.scan_opportunities(['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT'])
    print(f"Opportunities found: {len(opportunities)}")
    for opp in opportunities:
        print(f"  {opp['symbol']}: {opp['profit_potential_pct']:.2f}% potential")
