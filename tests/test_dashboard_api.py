#!/usr/bin/env python3
import json
import pytest
from flask.testing import FlaskClient

import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import dashboard_api as m

@pytest.fixture()
def client():
    m.app.config.update({ 'TESTING': True })
    return m.app.test_client()

class TestAPI:
    def test_health(self, client: FlaskClient):
        r = client.get('/api/health')
        assert r.status_code == 200
        data = r.get_json()
        assert 'status' in data

    def test_status(self, client: FlaskClient):
        r = client.get('/api/status')
        assert r.status_code == 200
        data = r.get_json()
        for k in ['trading_enabled','balance','total_trades','winning_trades','total_profit']:
            assert k in data

    def test_trades(self, client: FlaskClient):
        r = client.get('/api/trades?timeframe=24h')
        assert r.status_code == 200
        data = r.get_json()
        assert 'trades' in data

    def test_performance(self, client: FlaskClient):
        r = client.get('/api/performance')
        assert r.status_code == 200
        data = r.get_json()
        for k in ['total_trades','total_profit','win_rate','avg_profit','best_trade','worst_trade']:
            assert k in data

    def test_positions(self, client: FlaskClient):
        r = client.get('/api/positions')
        assert r.status_code == 200
        data = r.get_json()
        assert 'positions' in data

    def test_sentiment(self, client: FlaskClient):
        r = client.get('/api/sentiment')
        assert r.status_code == 200
