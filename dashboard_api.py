#!/usr/bin/env python3
"""
Flask API for TPS19 Dashboard
Serves live trade data, P&L, and system metrics
"""

import os
import sys
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Data storage paths
TRADES_FILE = 'data/trades_history.json'
STATUS_FILE = 'data/bot_status.json'

def load_trades():
    """Load trade history"""
    if not os.path.exists(TRADES_FILE):
        return []
    
    with open(TRADES_FILE, 'r') as f:
        return json.load(f)

def load_status():
    """Load bot status"""
    if not os.path.exists(STATUS_FILE):
        return {
            'trading_enabled': True,
            'balance': 3.0,
            'total_trades': 0,
            'winning_trades': 0,
            'total_profit': 0.0
        }
    
    with open(STATUS_FILE, 'r') as f:
        return json.load(f)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get bot status"""
    status = load_status()
    
    return jsonify({
        'trading_enabled': status['trading_enabled'],
        'balance': status['balance'],
        'total_trades': status['total_trades'],
        'winning_trades': status['winning_trades'],
        'losing_trades': status['total_trades'] - status['winning_trades'],
        'win_rate': (status['winning_trades'] / status['total_trades'] * 100) if status['total_trades'] > 0 else 0,
        'total_profit': status['total_profit'],
        'roi': ((status['balance'] - 3.0) / 3.0 * 100),
        'last_updated': status.get('last_update', datetime.now().isoformat())
    })

@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Get trade history"""
    trades = load_trades()
    
    # Filter by timeframe if provided
    timeframe = request.args.get('timeframe', '24h')
    
    if timeframe == '24h':
        cutoff = datetime.now() - timedelta(hours=24)
    elif timeframe == '7d':
        cutoff = datetime.now() - timedelta(days=7)
    elif timeframe == '30d':
        cutoff = datetime.now() - timedelta(days=30)
    else:
        cutoff = datetime.now() - timedelta(hours=24)
    
    filtered_trades = [
        trade for trade in trades
        if datetime.fromisoformat(trade.get('timestamp', '2000-01-01')) > cutoff
    ]
    
    return jsonify({
        'trades': filtered_trades,
        'count': len(filtered_trades),
        'timeframe': timeframe
    })

@app.route('/api/performance', methods=['GET'])
def get_performance():
    """Get performance metrics"""
    trades = load_trades()
    status = load_status()
    
    # Calculate metrics
    if not trades:
        return jsonify({
            'total_trades': 0,
            'total_profit': 0,
            'win_rate': 0,
            'avg_profit': 0,
            'best_trade': 0,
            'worst_trade': 0
        })
    
    profits = [trade.get('profit', 0) for trade in trades]
    wins = [p for p in profits if p > 0]
    
    return jsonify({
        'total_trades': len(trades),
        'total_profit': sum(profits),
        'win_rate': (len(wins) / len(trades) * 100) if trades else 0,
        'avg_profit': sum(profits) / len(trades) if trades else 0,
        'best_trade': max(profits) if profits else 0,
        'worst_trade': min(profits) if profits else 0,
        'sharpe_ratio': calculate_sharpe(profits) if len(profits) > 1 else 0
    })

@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get open positions"""
    # Load from trailing_stops.json
    stops_file = 'data/trailing_stops.json'
    
    if not os.path.exists(stops_file):
        return jsonify({'positions': []})
    
    with open(stops_file, 'r') as f:
        positions = json.load(f)
    
    return jsonify({
        'positions': list(positions.values()),
        'count': len(positions)
    })

@app.route('/api/sentiment', methods=['GET'])
def get_sentiment():
    """Get current sentiment scores"""
    # Load from sentiment cache if exists
    sentiment_file = 'data/sentiment_cache.json'
    
    if not os.path.exists(sentiment_file):
        return jsonify({
            'BTC': 0,
            'ETH': 0,
            'SOL': 0,
            'ADA': 0,
            'last_updated': datetime.now().isoformat()
        })
    
    with open(sentiment_file, 'r') as f:
        sentiment = json.load(f)
    
    return jsonify(sentiment)

@app.route('/api/chart/<symbol>', methods=['GET'])
def get_chart_data(symbol):
    """Get price chart data for a symbol"""
    # This would fetch from exchange in production
    # For now, return mock data
    return jsonify({
        'symbol': symbol,
        'timeframe': '1h',
        'data': [
            {'timestamp': '2025-10-17T00:00:00', 'price': 50000},
            {'timestamp': '2025-10-17T01:00:00', 'price': 50500},
            {'timestamp': '2025-10-17T02:00:00', 'price': 50200},
        ]
    })

def calculate_sharpe(profits):
    """Calculate Sharpe ratio"""
    if not profits:
        return 0
    
    import numpy as np
    returns = np.array(profits)
    return (np.mean(returns) / np.std(returns)) if np.std(returns) > 0 else 0

if __name__ == '__main__':
    print("🚀 Starting Dashboard API...")
    print("📊 Access at: http://localhost:5000")
    print("\nEndpoints:")
    print("  GET /api/health")
    print("  GET /api/status")
    print("  GET /api/trades?timeframe=24h")
    print("  GET /api/performance")
    print("  GET /api/positions")
    print("  GET /api/sentiment")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
