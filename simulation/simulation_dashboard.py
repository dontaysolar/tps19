"""
Simulation Dashboard
Real-time visualization and control for market simulation
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import statistics

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from simulation.market_simulator import MarketSimulator, MarketCondition, EventType, MarketEvent
from simulation.backtesting_engine import BacktestingEngine, BacktestResult
from core.logging_config import get_logger


logger = get_logger(__name__)


class SimulationDashboard:
    """
    Web-based dashboard for market simulation
    Features:
    - Real-time price updates
    - Market condition control
    - Event injection
    - Backtest results visualization
    - Performance metrics
    """
    
    def __init__(self):
        self.app = FastAPI(title="TPS19 Simulation Dashboard")
        self.market_simulator = MarketSimulator()
        self.backtesting_engine = BacktestingEngine()
        self.active_connections: List[WebSocket] = []
        self.simulation_running = False
        
        # Setup routes
        self._setup_routes()
        
        # Simulation state
        self.current_backtest_result: Optional[BacktestResult] = None
        
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def get_dashboard():
            """Serve the dashboard HTML"""
            return HTMLResponse(content=self._get_dashboard_html())
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                while True:
                    # Receive commands from client
                    data = await websocket.receive_text()
                    command = json.loads(data)
                    
                    response = await self._handle_command(command)
                    await websocket.send_text(json.dumps(response))
                    
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
        
        @self.app.get("/api/market/status")
        async def get_market_status():
            """Get current market status"""
            status = {
                "condition": self.market_simulator.market_condition.value,
                "volatility": self.market_simulator.volatility,
                "trend_strength": self.market_simulator.trend_strength,
                "prices": self.market_simulator.current_prices,
                "events": [
                    {
                        "timestamp": e.timestamp.isoformat(),
                        "type": e.event_type.value,
                        "impact": e.impact,
                        "description": e.description
                    }
                    for e in self.market_simulator.events
                ]
            }
            return status
        
        @self.app.post("/api/market/condition")
        async def set_market_condition(condition: str):
            """Set market condition"""
            try:
                market_condition = MarketCondition(condition)
                self.market_simulator.set_market_condition(market_condition)
                return {"status": "success", "condition": condition}
            except ValueError:
                return {"status": "error", "message": f"Invalid condition: {condition}"}
        
        @self.app.post("/api/market/event")
        async def add_market_event(event_type: str, impact: float, duration_minutes: int = 60):
            """Add a market event"""
            try:
                event = MarketEvent(
                    timestamp=datetime.now(),
                    event_type=EventType(event_type),
                    impact=impact,
                    duration_minutes=duration_minutes,
                    description=f"Manual {event_type} event"
                )
                self.market_simulator.add_market_event(event)
                return {"status": "success", "event": event_type}
            except ValueError:
                return {"status": "error", "message": f"Invalid event type: {event_type}"}
        
        @self.app.post("/api/simulation/start")
        async def start_simulation():
            """Start market simulation"""
            if not self.simulation_running:
                self.simulation_running = True
                asyncio.create_task(self._run_simulation())
                return {"status": "started"}
            return {"status": "already_running"}
        
        @self.app.post("/api/simulation/stop")
        async def stop_simulation():
            """Stop market simulation"""
            self.simulation_running = False
            return {"status": "stopped"}
        
        @self.app.get("/api/backtest/results")
        async def get_backtest_results():
            """Get latest backtest results"""
            if self.current_backtest_result:
                return {
                    "total_return": self.current_backtest_result.total_return,
                    "sharpe_ratio": self.current_backtest_result.sharpe_ratio,
                    "max_drawdown": self.current_backtest_result.max_drawdown,
                    "win_rate": self.current_backtest_result.win_rate,
                    "total_trades": self.current_backtest_result.total_trades,
                    "profit_factor": self.current_backtest_result.profit_factor,
                    "equity_curve": self.current_backtest_result.equity_curve[-100:]  # Last 100 points
                }
            return {"status": "no_results"}
    
    async def _handle_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WebSocket commands"""
        cmd_type = command.get("type")
        
        if cmd_type == "get_prices":
            return {
                "type": "prices",
                "data": self.market_simulator.current_prices
            }
        
        elif cmd_type == "get_stats":
            stats = {}
            for symbol in self.market_simulator.current_prices:
                stats[symbol] = self.market_simulator.get_market_stats(symbol)
            return {
                "type": "stats",
                "data": stats
            }
        
        elif cmd_type == "get_orderbook":
            symbol = command.get("symbol", "BTC_USDT")
            orderbook = self.market_simulator.get_order_book(symbol)
            return {
                "type": "orderbook",
                "symbol": symbol,
                "data": orderbook
            }
        
        elif cmd_type == "run_backtest":
            # Run a quick backtest
            from simulation.backtesting_engine import example_momentum_strategy
            
            self.backtesting_engine = BacktestingEngine()
            self.backtesting_engine.set_market_simulator(self.market_simulator)
            
            result = self.backtesting_engine.run_backtest(
                strategy=example_momentum_strategy,
                start_date=datetime.now() - timedelta(days=7),
                end_date=datetime.now(),
                symbols=["BTC_USDT", "ETH_USDT"]
            )
            
            self.current_backtest_result = result
            
            return {
                "type": "backtest_complete",
                "data": {
                    "total_return": result.total_return,
                    "sharpe_ratio": result.sharpe_ratio,
                    "trades": result.total_trades
                }
            }
        
        return {"type": "error", "message": "Unknown command"}
    
    async def _run_simulation(self):
        """Run the market simulation loop"""
        logger.info("Starting market simulation")
        
        while self.simulation_running:
            # Update prices
            self.market_simulator.update_prices()
            
            # Broadcast updates to all connected clients
            update_data = {
                "type": "market_update",
                "timestamp": datetime.now().isoformat(),
                "prices": self.market_simulator.current_prices,
                "condition": self.market_simulator.market_condition.value,
                "volatility": self.market_simulator.volatility
            }
            
            # Send to all WebSocket connections
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(json.dumps(update_data))
                except:
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for conn in disconnected:
                self.active_connections.remove(conn)
            
            # Wait before next update
            await asyncio.sleep(1)  # 1 second updates
        
        logger.info("Market simulation stopped")
    
    def _get_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>TPS19 Simulation Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
                .container {
                    max-width: 1400px;
                    margin: 0 auto;
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .card {
                    background-color: #2a2a2a;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                }
                .price-card {
                    text-align: center;
                }
                .symbol {
                    font-size: 18px;
                    color: #888;
                    margin-bottom: 10px;
                }
                .price {
                    font-size: 28px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .change {
                    font-size: 16px;
                }
                .positive { color: #4caf50; }
                .negative { color: #f44336; }
                .controls {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                    flex-wrap: wrap;
                }
                button {
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    padding: 10px 20px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    cursor: pointer;
                    border-radius: 4px;
                }
                button:hover {
                    background-color: #45a049;
                }
                .stop-btn {
                    background-color: #f44336;
                }
                .stop-btn:hover {
                    background-color: #da190b;
                }
                select {
                    padding: 10px;
                    font-size: 16px;
                    background-color: #3a3a3a;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 4px;
                }
                .chart-container {
                    position: relative;
                    height: 400px;
                    margin-top: 30px;
                }
                .metrics {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                }
                .metric {
                    background-color: #3a3a3a;
                    padding: 15px;
                    border-radius: 4px;
                    text-align: center;
                }
                .metric-label {
                    font-size: 14px;
                    color: #888;
                    margin-bottom: 5px;
                }
                .metric-value {
                    font-size: 24px;
                    font-weight: bold;
                }
                #status {
                    padding: 10px;
                    background-color: #3a3a3a;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>TPS19 Market Simulation Dashboard</h1>
                    <div id="status">Status: Disconnected</div>
                </div>
                
                <div class="controls">
                    <button onclick="startSimulation()">Start Simulation</button>
                    <button class="stop-btn" onclick="stopSimulation()">Stop Simulation</button>
                    <select id="marketCondition" onchange="setMarketCondition()">
                        <option value="">Select Market Condition</option>
                        <option value="bull_run">Bull Run</option>
                        <option value="bear_market">Bear Market</option>
                        <option value="sideways">Sideways</option>
                        <option value="high_volatility">High Volatility</option>
                        <option value="low_volatility">Low Volatility</option>
                        <option value="flash_crash">Flash Crash</option>
                        <option value="recovery">Recovery</option>
                    </select>
                    <button onclick="runBacktest()">Run Backtest</button>
                    <button onclick="addRandomEvent()">Add Random Event</button>
                </div>
                
                <div class="metrics" id="metrics">
                    <div class="metric">
                        <div class="metric-label">Market Condition</div>
                        <div class="metric-value" id="marketConditionDisplay">-</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Volatility</div>
                        <div class="metric-value" id="volatilityDisplay">-</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Active Events</div>
                        <div class="metric-value" id="eventsDisplay">0</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Simulation Time</div>
                        <div class="metric-value" id="simTimeDisplay">00:00:00</div>
                    </div>
                </div>
                
                <div class="grid" id="priceGrid">
                    <!-- Price cards will be inserted here -->
                </div>
                
                <div class="card">
                    <h2>Price Chart</h2>
                    <div class="chart-container">
                        <canvas id="priceChart"></canvas>
                    </div>
                </div>
                
                <div class="card" id="backtestResults" style="display: none;">
                    <h2>Backtest Results</h2>
                    <div class="metrics" id="backtestMetrics">
                        <!-- Backtest metrics will be inserted here -->
                    </div>
                </div>
            </div>
            
            <script>
                let ws = null;
                let priceHistory = {};
                let chart = null;
                let startTime = null;
                let simulationTimer = null;
                
                // Initialize WebSocket connection
                function connect() {
                    ws = new WebSocket('ws://localhost:8000/ws');
                    
                    ws.onopen = function() {
                        document.getElementById('status').textContent = 'Status: Connected';
                        document.getElementById('status').style.backgroundColor = '#4CAF50';
                        requestPrices();
                    };
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        handleMessage(data);
                    };
                    
                    ws.onclose = function() {
                        document.getElementById('status').textContent = 'Status: Disconnected';
                        document.getElementById('status').style.backgroundColor = '#f44336';
                        setTimeout(connect, 5000); // Reconnect after 5 seconds
                    };
                    
                    ws.onerror = function(error) {
                        console.error('WebSocket error:', error);
                    };
                }
                
                function handleMessage(data) {
                    switch(data.type) {
                        case 'market_update':
                            updatePrices(data.prices);
                            updateMetrics(data);
                            break;
                        case 'prices':
                            updatePrices(data.data);
                            break;
                        case 'stats':
                            updateStats(data.data);
                            break;
                        case 'backtest_complete':
                            showBacktestResults(data.data);
                            break;
                    }
                }
                
                function updatePrices(prices) {
                    const grid = document.getElementById('priceGrid');
                    
                    for (const [symbol, price] of Object.entries(prices)) {
                        let card = document.getElementById(`price-${symbol}`);
                        
                        if (!card) {
                            card = createPriceCard(symbol);
                            grid.appendChild(card);
                        }
                        
                        const priceElement = card.querySelector('.price');
                        const oldPrice = parseFloat(priceElement.textContent.replace('$', '').replace(',', ''));
                        priceElement.textContent = '$' + price.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                        
                        // Update change indicator
                        const changeElement = card.querySelector('.change');
                        if (!isNaN(oldPrice) && oldPrice > 0) {
                            const change = ((price - oldPrice) / oldPrice) * 100;
                            changeElement.textContent = (change >= 0 ? '+' : '') + change.toFixed(2) + '%';
                            changeElement.className = 'change ' + (change >= 0 ? 'positive' : 'negative');
                        }
                        
                        // Update price history
                        if (!priceHistory[symbol]) {
                            priceHistory[symbol] = [];
                        }
                        priceHistory[symbol].push(price);
                        if (priceHistory[symbol].length > 100) {
                            priceHistory[symbol].shift();
                        }
                    }
                    
                    updateChart();
                }
                
                function updateMetrics(data) {
                    document.getElementById('marketConditionDisplay').textContent = data.condition || '-';
                    document.getElementById('volatilityDisplay').textContent = (data.volatility * 100).toFixed(1) + '%';
                }
                
                function createPriceCard(symbol) {
                    const card = document.createElement('div');
                    card.className = 'card price-card';
                    card.id = `price-${symbol}`;
                    card.innerHTML = `
                        <div class="symbol">${symbol}</div>
                        <div class="price">$0.00</div>
                        <div class="change">0.00%</div>
                    `;
                    return card;
                }
                
                function updateChart() {
                    if (!chart) {
                        const ctx = document.getElementById('priceChart').getContext('2d');
                        chart = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: [],
                                datasets: []
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                scales: {
                                    x: {
                                        display: false
                                    },
                                    y: {
                                        position: 'right',
                                        grid: {
                                            color: '#444'
                                        }
                                    }
                                },
                                plugins: {
                                    legend: {
                                        position: 'top'
                                    }
                                }
                            }
                        });
                    }
                    
                    // Update chart data
                    const datasets = [];
                    const colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336'];
                    let colorIndex = 0;
                    
                    for (const [symbol, history] of Object.entries(priceHistory)) {
                        if (history.length > 0) {
                            datasets.push({
                                label: symbol,
                                data: history,
                                borderColor: colors[colorIndex % colors.length],
                                backgroundColor: 'transparent',
                                borderWidth: 2,
                                pointRadius: 0
                            });
                            colorIndex++;
                        }
                    }
                    
                    chart.data.labels = Array(Math.max(...Object.values(priceHistory).map(h => h.length))).fill('');
                    chart.data.datasets = datasets;
                    chart.update('none'); // Update without animation
                }
                
                function requestPrices() {
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({type: 'get_prices'}));
                    }
                }
                
                async function startSimulation() {
                    const response = await fetch('/api/simulation/start', {method: 'POST'});
                    const data = await response.json();
                    if (data.status === 'started' || data.status === 'already_running') {
                        startTime = new Date();
                        updateSimulationTime();
                        simulationTimer = setInterval(updateSimulationTime, 1000);
                    }
                }
                
                async function stopSimulation() {
                    const response = await fetch('/api/simulation/stop', {method: 'POST'});
                    if (simulationTimer) {
                        clearInterval(simulationTimer);
                        simulationTimer = null;
                    }
                }
                
                async function setMarketCondition() {
                    const condition = document.getElementById('marketCondition').value;
                    if (condition) {
                        await fetch('/api/market/condition', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({condition})
                        });
                    }
                }
                
                async function runBacktest() {
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({type: 'run_backtest'}));
                    }
                }
                
                async function addRandomEvent() {
                    const eventTypes = ['news_positive', 'news_negative', 'whale_buy', 'whale_sell'];
                    const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
                    const impact = (Math.random() - 0.5) * 0.1; // -5% to +5%
                    
                    await fetch('/api/market/event', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            event_type: eventType,
                            impact: impact,
                            duration_minutes: 60
                        })
                    });
                }
                
                function showBacktestResults(results) {
                    document.getElementById('backtestResults').style.display = 'block';
                    const metricsDiv = document.getElementById('backtestMetrics');
                    metricsDiv.innerHTML = `
                        <div class="metric">
                            <div class="metric-label">Total Return</div>
                            <div class="metric-value ${results.total_return >= 0 ? 'positive' : 'negative'}">
                                ${(results.total_return * 100).toFixed(2)}%
                            </div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Sharpe Ratio</div>
                            <div class="metric-value">${results.sharpe_ratio.toFixed(2)}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Total Trades</div>
                            <div class="metric-value">${results.trades}</div>
                        </div>
                    `;
                }
                
                function updateSimulationTime() {
                    if (startTime) {
                        const elapsed = new Date() - startTime;
                        const hours = Math.floor(elapsed / 3600000);
                        const minutes = Math.floor((elapsed % 3600000) / 60000);
                        const seconds = Math.floor((elapsed % 60000) / 1000);
                        
                        document.getElementById('simTimeDisplay').textContent = 
                            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                    }
                }
                
                // Connect on load
                connect();
                
                // Update active events count periodically
                setInterval(async () => {
                    try {
                        const response = await fetch('/api/market/status');
                        const data = await response.json();
                        document.getElementById('eventsDisplay').textContent = data.events.length;
                    } catch (error) {
                        console.error('Failed to fetch market status:', error);
                    }
                }, 5000);
            </script>
        </body>
        </html>
        """
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the dashboard server"""
        uvicorn.run(self.app, host=host, port=port)


if __name__ == "__main__":
    dashboard = SimulationDashboard()
    dashboard.run()