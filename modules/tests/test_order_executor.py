#!/usr/bin/env python3
import os
import unittest

from modules.paper_trading import PaperTradingEngine
from modules.order_executor import OrderExecutor, ExecutorConfig


class TestOrderExecutor(unittest.TestCase):
    def test_paper_buy_sell(self):
        paper = PaperTradingEngine(starting_balance=100.0)
        ex = OrderExecutor(ExecutorConfig(mode='paper', min_amount=0.0), exchange=None, paper_engine=paper)
        res_buy = ex.execute_buy('BTC/USDT', amount=0.001, price_hint=10000.0)
        self.assertEqual(res_buy.get('status'), 'filled')
        res_sell = ex.execute_sell('BTC/USDT', amount=0.001, price_hint=10100.0)
        self.assertEqual(res_sell.get('status'), 'filled')

    def test_reject_below_min(self):
        paper = PaperTradingEngine(starting_balance=100.0)
        ex = OrderExecutor(ExecutorConfig(mode='paper', min_amount=0.01), exchange=None, paper_engine=paper)
        res = ex.execute_buy('BTC/USDT', amount=0.001, price_hint=10000.0)
        self.assertEqual(res.get('status'), 'rejected')


if __name__ == '__main__':
    unittest.main()
