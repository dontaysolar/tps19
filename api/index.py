# Vercel serverless entry - Flask API bridge
from flask import Flask, jsonify, request
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import os
import sys

# Ensure project root on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Import existing Flask app from dashboard_api.py
# We adapt it to run under Vercel's serverless function
try:
    import dashboard_api as dashboard_module
    app = dashboard_module.app
except Exception as e:
    # Fallback minimal app to report import error (for logs)
    app = Flask(__name__)
    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'error',
            'reason': f'import_failed: {str(e)}'
        }), 500

# Vercel expects a WSGI callable named 'app'
# All routes already mounted under /api in dashboard_api
# For root path of the function, we provide an index
@app.route('/')
def index_root():
    return jsonify({'ok': True, 'service': 'tps19-dashboard-api'})
