'use client'

import { useState } from 'react'

export default function TradeHistory() {
  const [filter, setFilter] = useState('all')
  const [trades] = useState([
    {
      id: 1,
      time: '2024-01-15 14:32:15',
      symbol: 'BTC/USDT',
      side: 'BUY',
      amount: 0.125,
      price: 48500,
      total: 6062.50,
      fee: 6.06,
      pnl: 87.50,
      pnlPct: 1.44,
      strategy: 'Trend Follower Pro',
      status: 'Filled',
    },
    {
      id: 2,
      time: '2024-01-15 13:15:42',
      symbol: 'ETH/USDT',
      side: 'SELL',
      amount: 2.5,
      price: 2920,
      total: 7300,
      fee: 7.30,
      pnl: 175.00,
      pnlPct: 2.46,
      strategy: 'Mean Reversion Master',
      status: 'Filled',
    },
    {
      id: 3,
      time: '2024-01-15 12:05:33',
      symbol: 'SOL/USDT',
      side: 'BUY',
      amount: 50,
      price: 98,
      total: 4900,
      fee: 4.90,
      pnl: -45.00,
      pnlPct: -0.92,
      strategy: 'Breakout Hunter',
      status: 'Filled',
    },
    {
      id: 4,
      time: '2024-01-15 11:20:11',
      symbol: 'BTC/USDT',
      side: 'SELL',
      amount: 0.1,
      price: 48300,
      total: 4830,
      fee: 4.83,
      pnl: 120.00,
      pnlPct: 2.55,
      strategy: 'Wyckoff Analyzer',
      status: 'Filled',
    },
    {
      id: 5,
      time: '2024-01-15 10:45:22',
      symbol: 'ETH/USDT',
      side: 'BUY',
      amount: 3.0,
      price: 2800,
      total: 8400,
      fee: 8.40,
      pnl: 0,
      pnlPct: 0,
      strategy: 'Ichimoku Cloud',
      status: 'Open',
    },
  ])

  const filteredTrades = trades.filter((t) => {
    if (filter === 'all') return true
    if (filter === 'profitable') return t.pnl > 0
    if (filter === 'losses') return t.pnl < 0
    if (filter === 'buy') return t.side === 'BUY'
    if (filter === 'sell') return t.side === 'SELL'
    return true
  })

  const stats = {
    total: trades.length,
    profitable: trades.filter((t) => t.pnl > 0).length,
    losses: trades.filter((t) => t.pnl < 0).length,
    totalPnl: trades.reduce((sum, t) => sum + t.pnl, 0),
    totalVolume: trades.reduce((sum, t) => sum + t.total, 0),
    avgPnl: trades.reduce((sum, t) => sum + t.pnl, 0) / trades.length,
    winRate: (trades.filter((t) => t.pnl > 0).length / trades.length) * 100,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Trade History</h1>
          <p className="text-gray-400 mt-1">Complete trading activity log</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
            📥 Export CSV
          </button>
          <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors">
            📊 Generate Report
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <p className="text-sm text-gray-400 mb-2">Total Trades</p>
          <p className="text-3xl font-bold text-white">{stats.total}</p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <p className="text-sm text-gray-400 mb-2">Win Rate</p>
          <p className="text-3xl font-bold text-green-400">{stats.winRate.toFixed(1)}%</p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <p className="text-sm text-gray-400 mb-2">Total P&L</p>
          <p className={`text-3xl font-bold ${stats.totalPnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {stats.totalPnl >= 0 ? '+' : ''}${stats.totalPnl.toFixed(2)}
          </p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <p className="text-sm text-gray-400 mb-2">Avg P&L</p>
          <p className={`text-3xl font-bold ${stats.avgPnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {stats.avgPnl >= 0 ? '+' : ''}${stats.avgPnl.toFixed(2)}
          </p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <p className="text-sm text-gray-400 mb-2">Total Volume</p>
          <p className="text-3xl font-bold text-blue-400">${stats.totalVolume.toLocaleString()}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 overflow-x-auto pb-2">
        {[
          { value: 'all', label: 'All Trades', count: trades.length },
          { value: 'profitable', label: 'Profitable', count: stats.profitable },
          { value: 'losses', label: 'Losses', count: stats.losses },
          { value: 'buy', label: 'Buy Only', count: trades.filter(t => t.side === 'BUY').length },
          { value: 'sell', label: 'Sell Only', count: trades.filter(t => t.side === 'SELL').length },
        ].map((f) => (
          <button
            key={f.value}
            onClick={() => setFilter(f.value)}
            className={`px-4 py-2 rounded-lg font-semibold transition-all whitespace-nowrap ${
              filter === f.value
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-gray-300 hover:bg-slate-700'
            }`}
          >
            {f.label} ({f.count})
          </button>
        ))}
      </div>

      {/* Trade Table */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-900">
              <tr>
                <th className="text-left py-4 px-6 text-gray-400 font-semibold">Time</th>
                <th className="text-left py-4 px-6 text-gray-400 font-semibold">Symbol</th>
                <th className="text-left py-4 px-6 text-gray-400 font-semibold">Side</th>
                <th className="text-left py-4 px-6 text-gray-400 font-semibold">Strategy</th>
                <th className="text-right py-4 px-6 text-gray-400 font-semibold">Amount</th>
                <th className="text-right py-4 px-6 text-gray-400 font-semibold">Price</th>
                <th className="text-right py-4 px-6 text-gray-400 font-semibold">Total</th>
                <th className="text-right py-4 px-6 text-gray-400 font-semibold">Fee</th>
                <th className="text-right py-4 px-6 text-gray-400 font-semibold">P&L</th>
                <th className="text-center py-4 px-6 text-gray-400 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredTrades.map((trade) => (
                <tr key={trade.id} className="border-t border-slate-700 hover:bg-slate-700/30 transition-colors">
                  <td className="py-4 px-6 text-gray-400 text-sm">{trade.time}</td>
                  <td className="px-6">
                    <span className="font-semibold text-white">{trade.symbol}</span>
                  </td>
                  <td className="px-6">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        trade.side === 'BUY'
                          ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                          : 'bg-red-500/20 text-red-400 border border-red-500/30'
                      }`}
                    >
                      {trade.side}
                    </span>
                  </td>
                  <td className="px-6 text-sm text-gray-400">{trade.strategy}</td>
                  <td className="text-right px-6 text-gray-300">{trade.amount}</td>
                  <td className="text-right px-6 text-white">${trade.price.toLocaleString()}</td>
                  <td className="text-right px-6 text-white font-medium">${trade.total.toLocaleString()}</td>
                  <td className="text-right px-6 text-gray-400">${trade.fee.toFixed(2)}</td>
                  <td className="text-right px-6">
                    {trade.pnl !== 0 && (
                      <div className={trade.pnl > 0 ? 'text-green-400' : 'text-red-400'}>
                        <p className="font-semibold">{trade.pnl > 0 ? '+' : ''}{trade.pnlPct.toFixed(2)}%</p>
                        <p className="text-sm">{trade.pnl > 0 ? '+' : ''}${trade.pnl.toFixed(2)}</p>
                      </div>
                    )}
                    {trade.pnl === 0 && <span className="text-gray-500">-</span>}
                  </td>
                  <td className="text-center px-6">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        trade.status === 'Filled'
                          ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                          : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                      }`}
                    >
                      {trade.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
