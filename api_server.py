#!/usr/bin/env python3
"""
APEX V3 - REST API SERVER
Provides backend API for web dashboard
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
from datetime import datetime

# Add workspace to path
sys.path.insert(0, '/workspace')

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Import our trading system
try:
    from trade_persistence import PersistenceManager
    pm = PersistenceManager()
except:
    pm = None

@app.route('/api/status', methods=['GET'])
def get_status():
    """System status"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0.0',
        'trading_enabled': False,
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Dashboard statistics"""
    if pm:
        summary = pm.get_trade_summary()
        positions = pm.get_all_positions()
        
        return jsonify({
            'total_trades': summary.get('total_trades', 0),
            'realized_pnl': summary.get('realized_pnl', 0),
            'win_rate': summary.get('win_rate', 0),
            'active_positions': len(positions),
        })
    
    return jsonify({
        'total_trades': 0,
        'realized_pnl': 0,
        'win_rate': 0,
        'active_positions': 0,
    })

@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get open positions"""
    if pm:
        positions = pm.get_all_positions()
        return jsonify({'positions': positions})
    
    return jsonify({'positions': []})

@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Get trade history"""
    if pm:
        limit = request.args.get('limit', 50, type=int)
        trades = pm.get_trades(limit=limit)
        return jsonify({'trades': trades})
    
    return jsonify({'trades': []})

@app.route('/api/bots', methods=['GET'])
def get_bots():
    """Get active bots"""
    # Placeholder - integrate with bot registry
    return jsonify({
        'bots': [
            {
                'id': 1,
                'name': 'Trend Follower',
                'status': 'running',
                'profit': 12.5,
                'trades': 45
            },
            {
                'id': 2,
                'name': 'Mean Reversion',
                'status': 'running',
                'profit': 8.3,
                'trades': 32
            },
            {
                'id': 3,
                'name': 'Breakout Trader',
                'status': 'paused',
                'profit': 5.2,
                'trades': 18
            }
        ]
    })

@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Get current trading signals"""
    # Placeholder - integrate with signal layer
    return jsonify({
        'signals': [
            {'symbol': 'BTC/USDT', 'signal': 'BUY', 'confidence': 0.85},
            {'symbol': 'ETH/USDT', 'signal': 'HOLD', 'confidence': 0.45},
            {'symbol': 'SOL/USDT', 'signal': 'SELL', 'confidence': 0.72},
        ]
    })

@app.route('/api/health', methods=['GET'])
def get_health():
    """System health metrics"""
    import psutil
    
    return jsonify({
        'cpu': psutil.cpu_percent(interval=0.1),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent,
    })

if __name__ == '__main__':
    print("="*60)
    print("🚀 APEX V3 API Server Starting")
    print("="*60)
    print("API running on: http://localhost:8000")
    print("Web dashboard: http://localhost:3000")
    print("="*60)
    
    app.run(host='0.0.0.0', port=8000, debug=True)
