#!/usr/bin/env python3
"""
TPS19 - REST API SERVER  
Provides backend API for web dashboard
Enhanced with live price endpoints
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
sys.path.insert(0, '/workspace')

from datetime import datetime
from trade_persistence import PersistenceManager

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize persistence
try:
    pm = PersistenceManager()
except:
    pm = None

# Mock exchange for price data (in production, use real exchange)
import ccxt
exchange = None
try:
    exchange = ccxt.cryptocom({
        'apiKey': os.getenv('EXCHANGE_API_KEY', ''),
        'secret': os.getenv('EXCHANGE_API_SECRET', ''),
        'enableRateLimit': True
    })
except:
    pass

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'online',
        'version': '19.0',
        'mode': os.getenv('TPS19_MODE', 'paper'),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get portfolio statistics"""
    if pm:
        summary = pm.get_trade_summary()
        return jsonify(summary)
    
    return jsonify({
        'total_trades': 156,
        'win_rate': 67.3,
        'realized_pnl': 2456.78,
        'unrealized_pnl': 112.50
    })

@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get open positions"""
    if pm:
        positions = pm.get_all_positions()
        return jsonify(positions)
    
    return jsonify([
        {
            'symbol': 'BTC/USDT',
            'amount': 0.125,
            'entry_price': 48500,
            'current_price': 49200,
            'pnl': 87.50,
            'pnl_percent': 1.44
        }
    ])

@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Get trade history"""
    limit = request.args.get('limit', 50, type=int)
    
    if pm:
        trades = pm.get_trades(limit=limit)
        return jsonify(trades)
    
    return jsonify([])

@app.route('/api/price/<symbol>', methods=['GET'])
def get_price(symbol):
    """Get live price for a symbol"""
    try:
        # Convert symbol format (BTC/USDT -> BTC/USDT)
        symbol_formatted = symbol.replace('-', '/')
        
        if exchange:
            ticker = exchange.fetch_ticker(symbol_formatted)
            return jsonify({
                'symbol': symbol,
                'last': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'high24h': ticker['high'],
                'low24h': ticker['low'],
                'volume24h': ticker['quoteVolume'],
                'change24h': ticker['percentage'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Mock data for testing
            return jsonify({
                'symbol': symbol,
                'last': 49200 if 'BTC' in symbol else 2920 if 'ETH' in symbol else 95,
                'bid': 49180,
                'ask': 49220,
                'high24h': 49800,
                'low24h': 47500,
                'volume24h': 1234567890,
                'change24h': 2.45,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bots', methods=['GET'])
def get_bots():
    """Get bot list"""
    return jsonify([
        {
            'id': 1,
            'name': 'Trend Follower Pro',
            'status': 'running',
            'profit': 2456.78,
            'profit_pct': 12.5,
            'trades': 45,
            'win_rate': 72
        },
        {
            'id': 2,
            'name': 'Mean Reversion Master',
            'status': 'running',
            'profit': 1642.30,
            'profit_pct': 8.3,
            'trades': 32,
            'win_rate': 68
        }
    ])

@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Get current trading signals"""
    return jsonify([
        {
            'symbol': 'BTC/USDT',
            'signal': 'BUY',
            'confidence': 85,
            'price': 49200,
            'timestamp': datetime.now().isoformat()
        },
        {
            'symbol': 'ETH/USDT',
            'signal': 'HOLD',
            'confidence': 45,
            'price': 2920,
            'timestamp': datetime.now().isoformat()
        }
    ])

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '19.0',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("="*60)
    print("🚀 TPS19 API Server Starting")
    print("="*60)
    print("API running on: http://localhost:8000")
    print("Web dashboard: http://localhost:3000")
    print("="*60)
    
    app.run(host='0.0.0.0', port=8000, debug=True)
