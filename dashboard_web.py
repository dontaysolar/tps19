#!/usr/bin/env python3
"""
APEX Trading System - Web Dashboard
Real-time monitoring and control interface
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bots'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from flask import Flask, render_template, jsonify, request, send_from_directory
    from flask_socketio import SocketIO, emit
    import plotly.graph_objs as go
    import plotly.utils
except ImportError:
    print("Installing dashboard dependencies...")
    os.system("pip3 install --break-system-packages flask flask-socketio plotly -q")
    from flask import Flask, render_template, jsonify, request, send_from_directory
    from flask_socketio import SocketIO, emit
    import plotly.graph_objs as go
    import plotly.utils

# Import APEX components
from apex_nexus_v2 import APEXNexusV2
from database_handler import DatabaseManager
from google_sheets_handler import SheetsManager
from trading_strategies import StrategyManager
from ai_models import AIModelManager

class APEXDashboard:
    """
    Comprehensive web dashboard for APEX Trading System
    Features:
    - Real-time monitoring
    - Interactive charts
    - Bot control
    - Performance analytics
    - Alert management
    """
    
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'apex_trading_system_2025'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize APEX components
        self.nexus = None
        self.db_manager = DatabaseManager()
        self.sheets_manager = None
        self.strategy_manager = StrategyManager()
        self.ai_manager = AIModelManager()
        
        # Dashboard state
        self.dashboard_state = {
            'system_status': 'OFFLINE',
            'trading_enabled': False,
            'active_bots': 0,
            'total_trades': 0,
            'total_profit': 0.0,
            'win_rate': 0.0,
            'last_update': None
        }
        
        # Real-time data
        self.real_time_data = {
            'prices': {},
            'volumes': {},
            'signals': {},
            'alerts': [],
            'bot_statuses': {}
        }
        
        # Setup routes and socket events
        self._setup_routes()
        self._setup_socket_events()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template('dashboard.html')
        
        @self.app.route('/api/status')
        def api_status():
            return jsonify(self.dashboard_state)
        
        @self.app.route('/api/trades')
        def api_trades():
            limit = request.args.get('limit', 50, type=int)
            trades = self.db_manager.redis_handler.get_recent_trades(limit)
            return jsonify(trades)
        
        @self.app.route('/api/positions')
        def api_positions():
            positions = self.db_manager.redis_handler.get_all_positions()
            return jsonify(positions)
        
        @self.app.route('/api/performance')
        def api_performance():
            summary = self.db_manager.get_trading_summary()
            return jsonify(summary)
        
        @self.app.route('/api/bots')
        def api_bots():
            bot_performance = self.db_manager.get_bot_performance()
            return jsonify(bot_performance)
        
        @self.app.route('/api/market-data')
        def api_market_data():
            symbols = request.args.get('symbols', 'BTC/USDT,ETH/USDT,SOL/USDT,ADA/USDT').split(',')
            market_data = {}
            
            for symbol in symbols:
                data = self.db_manager.redis_handler.get_market_data(symbol.strip())
                if data:
                    market_data[symbol.strip()] = data
            
            return jsonify(market_data)
        
        @self.app.route('/api/charts/price/<symbol>')
        def api_price_chart(symbol):
            # Generate price chart data
            chart_data = self._generate_price_chart(symbol)
            return jsonify(chart_data)
        
        @self.app.route('/api/charts/volume/<symbol>')
        def api_volume_chart(symbol):
            # Generate volume chart data
            chart_data = self._generate_volume_chart(symbol)
            return jsonify(chart_data)
        
        @self.app.route('/api/charts/performance')
        def api_performance_chart():
            # Generate performance chart data
            chart_data = self._generate_performance_chart()
            return jsonify(chart_data)
        
        @self.app.route('/api/control/start')
        def api_start_system():
            try:
                if not self.nexus:
                    self.nexus = APEXNexusV2()
                
                # Start system in background thread
                threading.Thread(target=self.nexus.run, daemon=True).start()
                
                self.dashboard_state['system_status'] = 'ONLINE'
                self.dashboard_state['trading_enabled'] = True
                
                return jsonify({'status': 'success', 'message': 'System started'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
        
        @self.app.route('/api/control/stop')
        def api_stop_system():
            try:
                if self.nexus:
                    self.nexus.state['trading_enabled'] = False
                
                self.dashboard_state['system_status'] = 'OFFLINE'
                self.dashboard_state['trading_enabled'] = False
                
                return jsonify({'status': 'success', 'message': 'System stopped'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
        
        @self.app.route('/api/control/toggle-trading')
        def api_toggle_trading():
            try:
                if self.nexus:
                    self.nexus.state['trading_enabled'] = not self.nexus.state['trading_enabled']
                    self.dashboard_state['trading_enabled'] = self.nexus.state['trading_enabled']
                
                return jsonify({
                    'status': 'success', 
                    'trading_enabled': self.dashboard_state['trading_enabled']
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
        
        @self.app.route('/api/alerts')
        def api_alerts():
            alerts = self.db_manager.redis_handler.get_recent_alerts(50)
            return jsonify(alerts)
        
        @self.app.route('/api/strategies')
        def api_strategies():
            performance = self.strategy_manager.get_strategy_performance()
            return jsonify(performance)
    
    def _setup_socket_events(self):
        """Setup SocketIO events for real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print(f"Client connected: {request.sid}")
            emit('status', self.dashboard_state)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('request_update')
        def handle_update_request():
            emit('status', self.dashboard_state)
            emit('market_data', self.real_time_data)
    
    def _start_background_tasks(self):
        """Start background tasks for real-time updates"""
        def update_dashboard():
            while True:
                try:
                    self._update_dashboard_state()
                    self._update_real_time_data()
                    
                    # Emit updates to connected clients
                    self.socketio.emit('status', self.dashboard_state)
                    self.socketio.emit('market_data', self.real_time_data)
                    
                    time.sleep(5)  # Update every 5 seconds
                except Exception as e:
                    print(f"❌ Dashboard update error: {e}")
                    time.sleep(10)
        
        # Start background thread
        threading.Thread(target=update_dashboard, daemon=True).start()
    
    def _update_dashboard_state(self):
        """Update dashboard state"""
        try:
            # Get system status
            if self.nexus:
                self.dashboard_state['system_status'] = 'ONLINE'
                self.dashboard_state['trading_enabled'] = self.nexus.state.get('trading_enabled', False)
                self.dashboard_state['active_bots'] = len(self.nexus.state.get('positions', {}))
            else:
                self.dashboard_state['system_status'] = 'OFFLINE'
                self.dashboard_state['trading_enabled'] = False
                self.dashboard_state['active_bots'] = 0
            
            # Get trading summary
            summary = self.db_manager.get_trading_summary()
            if summary:
                self.dashboard_state['total_trades'] = summary.get('total_trades', 0)
                self.dashboard_state['total_profit'] = summary.get('total_profit', 0.0)
                
                # Calculate win rate
                total_trades = summary.get('total_trades', 0)
                if total_trades > 0:
                    winning_trades = summary.get('winning_trades', 0)
                    self.dashboard_state['win_rate'] = (winning_trades / total_trades) * 100
            
            self.dashboard_state['last_update'] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"❌ Dashboard state update error: {e}")
    
    def _update_real_time_data(self):
        """Update real-time data"""
        try:
            # Update market data
            symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT']
            for symbol in symbols:
                data = self.db_manager.redis_handler.get_market_data(symbol)
                if data:
                    self.real_time_data['prices'][symbol] = data.get('price', 0)
                    self.real_time_data['volumes'][symbol] = data.get('volume', 0)
            
            # Update bot statuses
            bot_performance = self.db_manager.get_bot_performance()
            self.real_time_data['bot_statuses'] = bot_performance
            
            # Update alerts
            alerts = self.db_manager.redis_handler.get_recent_alerts(10)
            self.real_time_data['alerts'] = alerts
            
        except Exception as e:
            print(f"❌ Real-time data update error: {e}")
    
    def _generate_price_chart(self, symbol: str) -> Dict:
        """Generate price chart data"""
        try:
            # Get historical data (simplified - in production would use real data)
            data = self.db_manager.redis_handler.get_market_data(symbol)
            
            if not data:
                return {'error': 'No data available'}
            
            # Generate sample chart data
            timestamps = []
            prices = []
            
            current_time = datetime.now()
            base_price = data.get('price', 50000)
            
            for i in range(24):  # Last 24 hours
                timestamp = current_time - timedelta(hours=i)
                timestamps.append(timestamp.isoformat())
                
                # Simulate price movement
                price_change = np.random.normal(0, 0.02)  # 2% volatility
                price = base_price * (1 + price_change)
                prices.append(price)
            
            return {
                'timestamps': timestamps[::-1],  # Reverse to show chronological order
                'prices': prices[::-1],
                'symbol': symbol
            }
            
        except Exception as e:
            print(f"❌ Price chart generation error: {e}")
            return {'error': str(e)}
    
    def _generate_volume_chart(self, symbol: str) -> Dict:
        """Generate volume chart data"""
        try:
            # Similar to price chart but for volume
            data = self.db_manager.redis_handler.get_market_data(symbol)
            
            if not data:
                return {'error': 'No data available'}
            
            timestamps = []
            volumes = []
            
            current_time = datetime.now()
            base_volume = data.get('volume', 1000)
            
            for i in range(24):
                timestamp = current_time - timedelta(hours=i)
                timestamps.append(timestamp.isoformat())
                
                # Simulate volume variation
                volume_change = np.random.uniform(0.5, 2.0)
                volume = base_volume * volume_change
                volumes.append(volume)
            
            return {
                'timestamps': timestamps[::-1],
                'volumes': volumes[::-1],
                'symbol': symbol
            }
            
        except Exception as e:
            print(f"❌ Volume chart generation error: {e}")
            return {'error': str(e)}
    
    def _generate_performance_chart(self) -> Dict:
        """Generate performance chart data"""
        try:
            # Get performance data from database
            trades = self.db_manager.redis_handler.get_recent_trades(100)
            
            if not trades:
                return {'error': 'No trades available'}
            
            # Calculate cumulative profit
            timestamps = []
            cumulative_profit = []
            current_profit = 0
            
            for trade in trades:
                timestamp = trade.get('timestamp', '')
                profit = trade.get('profit', 0)
                
                if timestamp:
                    timestamps.append(timestamp)
                    current_profit += profit
                    cumulative_profit.append(current_profit)
            
            return {
                'timestamps': timestamps,
                'cumulative_profit': cumulative_profit
            }
            
        except Exception as e:
            print(f"❌ Performance chart generation error: {e}")
            return {'error': str(e)}
    
    def run(self):
        """Run the dashboard server"""
        print(f"🚀 Starting APEX Dashboard on {self.host}:{self.port}")
        print(f"📊 Dashboard URL: http://{self.host}:{self.port}")
        
        try:
            self.socketio.run(self.app, host=self.host, port=self.port, debug=False)
        except Exception as e:
            print(f"❌ Dashboard startup error: {e}")


def create_dashboard_template():
    """Create HTML template for dashboard"""
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APEX Trading System Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #0a0a0a;
            color: #ffffff;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .status-card h3 {
            margin: 0 0 10px 0;
            color: #667eea;
        }
        .status-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .chart-container {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .control-panel {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .btn.danger {
            background: #e74c3c;
        }
        .btn.success {
            background: #27ae60;
        }
        .alerts {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            max-height: 300px;
            overflow-y: auto;
        }
        .alert {
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 4px solid #f39c12;
        }
        .alert.high {
            border-left-color: #e74c3c;
        }
        .alert.medium {
            border-left-color: #f39c12;
        }
        .alert.low {
            border-left-color: #27ae60;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 APEX Trading System Dashboard</h1>
        <p>Real-time AI Trading System Monitoring</p>
    </div>

    <div class="status-grid">
        <div class="status-card">
            <h3>System Status</h3>
            <div class="status-value" id="system-status">OFFLINE</div>
            <p>Trading: <span id="trading-status">Disabled</span></p>
        </div>
        <div class="status-card">
            <h3>Total Trades</h3>
            <div class="status-value" id="total-trades">0</div>
            <p>Active Bots: <span id="active-bots">0</span></p>
        </div>
        <div class="status-card">
            <h3>Total Profit</h3>
            <div class="status-value" id="total-profit">$0.00</div>
            <p>Win Rate: <span id="win-rate">0%</span></p>
        </div>
        <div class="status-card">
            <h3>Last Update</h3>
            <div class="status-value" id="last-update">Never</div>
            <p>System Uptime: <span id="uptime">0h 0m</span></p>
        </div>
    </div>

    <div class="control-panel">
        <h3>System Control</h3>
        <button class="btn success" onclick="startSystem()">Start System</button>
        <button class="btn danger" onclick="stopSystem()">Stop System</button>
        <button class="btn" onclick="toggleTrading()">Toggle Trading</button>
        <button class="btn" onclick="refreshData()">Refresh Data</button>
    </div>

    <div class="chart-container">
        <h3>Price Charts</h3>
        <div id="price-chart" style="height: 400px;"></div>
    </div>

    <div class="chart-container">
        <h3>Performance Chart</h3>
        <div id="performance-chart" style="height: 300px;"></div>
    </div>

    <div class="alerts">
        <h3>Recent Alerts</h3>
        <div id="alerts-list">
            <p>No alerts available</p>
        </div>
    </div>

    <script>
        // Initialize Socket.IO connection
        const socket = io();
        
        // Dashboard state
        let dashboardState = {};
        let charts = {};

        // Socket event handlers
        socket.on('connect', function() {
            console.log('Connected to dashboard');
            requestUpdate();
        });

        socket.on('status', function(data) {
            dashboardState = data;
            updateStatusDisplay();
        });

        socket.on('market_data', function(data) {
            updateCharts(data);
        });

        // Update status display
        function updateStatusDisplay() {
            document.getElementById('system-status').textContent = dashboardState.system_status || 'OFFLINE';
            document.getElementById('trading-status').textContent = dashboardState.trading_enabled ? 'Enabled' : 'Disabled';
            document.getElementById('total-trades').textContent = dashboardState.total_trades || 0;
            document.getElementById('active-bots').textContent = dashboardState.active_bots || 0;
            document.getElementById('total-profit').textContent = '$' + (dashboardState.total_profit || 0).toFixed(2);
            document.getElementById('win-rate').textContent = (dashboardState.win_rate || 0).toFixed(1) + '%';
            document.getElementById('last-update').textContent = dashboardState.last_update || 'Never';
        }

        // Update charts
        function updateCharts(data) {
            // Update price chart
            if (data.prices) {
                updatePriceChart(data.prices);
            }
            
            // Update alerts
            if (data.alerts) {
                updateAlerts(data.alerts);
            }
        }

        // Update price chart
        function updatePriceChart(prices) {
            const symbols = Object.keys(prices);
            const traces = symbols.map(symbol => ({
                x: [new Date().toISOString()],
                y: [prices[symbol]],
                type: 'scatter',
                mode: 'lines+markers',
                name: symbol,
                line: { color: getRandomColor() }
            }));

            const layout = {
                title: 'Real-time Prices',
                xaxis: { title: 'Time' },
                yaxis: { title: 'Price (USDT)' },
                paper_bgcolor: '#1a1a1a',
                plot_bgcolor: '#1a1a1a',
                font: { color: '#ffffff' }
            };

            Plotly.newPlot('price-chart', traces, layout);
        }

        // Update alerts
        function updateAlerts(alerts) {
            const alertsList = document.getElementById('alerts-list');
            alertsList.innerHTML = '';

            if (alerts.length === 0) {
                alertsList.innerHTML = '<p>No alerts available</p>';
                return;
            }

            alerts.forEach(alert => {
                const alertDiv = document.createElement('div');
                alertDiv.className = `alert ${alert.severity || 'low'}`;
                alertDiv.innerHTML = `
                    <strong>${alert.type || 'Alert'}</strong><br>
                    ${alert.message || 'No message'}<br>
                    <small>${alert.timestamp || 'Unknown time'}</small>
                `;
                alertsList.appendChild(alertDiv);
            });
        }

        // Control functions
        function startSystem() {
            fetch('/api/control/start')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('System started successfully');
                        requestUpdate();
                    } else {
                        alert('Error: ' + data.message);
                    }
                });
        }

        function stopSystem() {
            fetch('/api/control/stop')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('System stopped successfully');
                        requestUpdate();
                    } else {
                        alert('Error: ' + data.message);
                    }
                });
        }

        function toggleTrading() {
            fetch('/api/control/toggle-trading')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('Trading ' + (data.trading_enabled ? 'enabled' : 'disabled'));
                        requestUpdate();
                    } else {
                        alert('Error: ' + data.message);
                    }
                });
        }

        function refreshData() {
            requestUpdate();
        }

        function requestUpdate() {
            socket.emit('request_update');
        }

        function getRandomColor() {
            const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];
            return colors[Math.floor(Math.random() * colors.length)];
        }

        // Auto-refresh every 30 seconds
        setInterval(requestUpdate, 30000);
    </script>
</body>
</html>
    """
    
    template_path = os.path.join(template_dir, 'dashboard.html')
    with open(template_path, 'w') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard template created: {template_path}")


if __name__ == '__main__':
    print("🚀 APEX Trading System Dashboard\n")
    
    # Create dashboard template
    create_dashboard_template()
    
    # Create and run dashboard
    dashboard = APEXDashboard(host='0.0.0.0', port=5000)
    dashboard.run()