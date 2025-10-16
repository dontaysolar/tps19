#!/usr/bin/env python3
"""
TPS19 APEX - API Server for Dashboard
Exposes organism data via REST API and WebSocket
"""

import sys
sys.path.insert(0, '/workspace')

from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime, timedelta

from modules.organism.orchestrator import trading_organism
from modules.organism.brain import organism_brain
from modules.organism.immune_system import immune_system
from modules.organism.evolution import evolution_engine

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store start time
start_time = datetime.now()

def get_organism_vitals():
    """Get complete organism status"""
    try:
        vitals = trading_organism.get_vital_signs()
        brain_state = organism_brain.get_consciousness_state()
        evolution_stats = evolution_engine.get_evolution_stats()
        
        # Calculate uptime
        uptime = datetime.now() - start_time
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        
        return {
            # Health metrics
            'health_score': vitals.get('health_score', 0),
            'consciousness': vitals.get('consciousness', 0),
            'status': vitals.get('status', 'unknown'),
            
            # Trading metrics
            'total_trades': vitals.get('total_trades', 0),
            'winning_trades': vitals.get('winning_trades', 0),
            'win_rate': vitals.get('win_rate', 0),
            'total_pnl': vitals.get('total_pnl', 0),
            'daily_pnl': vitals.get('daily_pnl', 0),
            
            # Positions
            'positions': vitals.get('active_positions', []),
            'active_positions': len(vitals.get('active_positions', [])),
            
            # Performance
            'sharpe_ratio': vitals.get('sharpe_ratio', 0),
            'max_drawdown': vitals.get('max_drawdown', 0),
            'current_drawdown': vitals.get('current_drawdown', 0),
            
            # AI metrics
            'ml_confidence': 0.78,  # Placeholder
            'brain_signals': [],
            'model_weights': {
                'ml_prediction': 0.35,
                'technical_signals': 0.25,
                'market_regime': 0.20,
                'volume_analysis': 0.10,
                'momentum': 0.10,
            },
            
            # System
            'uptime': f"{hours}h {minutes}m",
            'total_decisions': vitals.get('total_decisions', 0),
            'trades_blocked': vitals.get('trades_blocked', 0),
            'avg_decision_time': 23,  # Placeholder
            
            # Strategies
            'strategies': [],
            
            # Brain state
            'brain': {
                'status': brain_state.get('status', 'unknown'),
                'active_modules': brain_state.get('active_modules', 0),
                'consciousness_level': brain_state.get('consciousness', 0),
            },
            
            # Evolution
            'evolution': {
                'generation': evolution_stats.get('generation', 0),
                'population_size': evolution_stats.get('population_size', 0),
                'best_fitness': evolution_stats.get('best_fitness', 0),
            },
            
            # Timestamp
            'timestamp': datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"Error getting vitals: {e}")
        return {
            'error': str(e),
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
        }

@app.route('/api/vitals', methods=['GET'])
def get_vitals():
    """Get organism vital signs"""
    return jsonify(get_organism_vitals())

@app.route('/api/health', methods=['GET'])
def get_health():
    """Get organism health status"""
    vitals = get_organism_vitals()
    return jsonify({
        'health_score': vitals.get('health_score', 0),
        'consciousness': vitals.get('consciousness', 0),
        'status': vitals.get('status', 'unknown'),
        'alive': vitals.get('status') == 'alive',
    })

@app.route('/api/trading', methods=['GET'])
def get_trading():
    """Get trading status"""
    vitals = get_organism_vitals()
    return jsonify({
        'positions': vitals.get('positions', []),
        'active_positions': vitals.get('active_positions', 0),
        'total_pnl': vitals.get('total_pnl', 0),
        'daily_pnl': vitals.get('daily_pnl', 0),
        'win_rate': vitals.get('win_rate', 0),
    })

@app.route('/api/performance', methods=['GET'])
def get_performance():
    """Get performance metrics"""
    vitals = get_organism_vitals()
    return jsonify({
        'total_trades': vitals.get('total_trades', 0),
        'winning_trades': vitals.get('winning_trades', 0),
        'win_rate': vitals.get('win_rate', 0),
        'sharpe_ratio': vitals.get('sharpe_ratio', 0),
        'max_drawdown': vitals.get('max_drawdown', 0),
        'current_drawdown': vitals.get('current_drawdown', 0),
    })

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get strategy performance"""
    # Placeholder - would come from trading engine
    return jsonify({
        'strategies': [
            {'name': 'Trend Following', 'trades': 45, 'win_rate': 0.62, 'pnl': 34.20},
            {'name': 'Mean Reversion', 'trades': 52, 'win_rate': 0.67, 'pnl': 41.80},
            {'name': 'Breakout', 'trades': 18, 'win_rate': 0.44, 'pnl': 8.30},
            {'name': 'Momentum', 'trades': 12, 'win_rate': 0.58, 'pnl': 5.20},
        ]
    })

# WebSocket handlers
@socketio.on('connect')
def handle_connect():
    """Client connected"""
    print('Client connected')
    emit('connected', {'message': 'Connected to TPS19 APEX Organism'})

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print('Client disconnected')

@socketio.on('request_update')
def handle_request_update():
    """Client requested data update"""
    emit('organism_update', get_organism_vitals())

# Background thread to send periodic updates
def background_updates():
    """Send periodic updates to all connected clients"""
    while True:
        time.sleep(2)  # Update every 2 seconds
        try:
            vitals = get_organism_vitals()
            socketio.emit('organism_update', vitals)
        except Exception as e:
            print(f"Error sending update: {e}")

# Start background thread
update_thread = threading.Thread(target=background_updates, daemon=True)
update_thread.start()

if __name__ == '__main__':
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║   TPS19 APEX - API Server Starting                           ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    print("API Server: http://localhost:5000")
    print("WebSocket: ws://localhost:5000")
    print()
    print("Endpoints:")
    print("  GET /api/vitals       - Complete organism status")
    print("  GET /api/health       - Health metrics")
    print("  GET /api/trading      - Trading status")
    print("  GET /api/performance  - Performance metrics")
    print("  GET /api/strategies   - Strategy comparison")
    print()
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
