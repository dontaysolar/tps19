#!/usr/bin/env python3
"""Dashboard API - Real-time status endpoint"""
from flask import Flask, jsonify
import os, json, glob
from datetime import datetime

app = Flask(__name__)

@app.route('/api/status')
def status():
    # Get running processes
    import subprocess
    procs = subprocess.check_output(['ps', 'aux']).decode()
    trader_running = 'simple_trader' in procs
    telegram_running = 'telegram_controller' in procs
    
    # Get latest log
    logs = glob.glob('/workspace/logs/trader_*.log')
    last_log = max(logs, key=os.path.getctime) if logs else None
    
    if last_log:
        with open(last_log) as f:
            lines = f.readlines()
            latest = lines[-1] if lines else "No data"
    else:
        latest = "No logs"
    
    return jsonify({
        'status': 'OPERATIONAL',
        'trader_running': trader_running,
        'telegram_running': telegram_running,
        'latest_log': latest,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'OK', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
