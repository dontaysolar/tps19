'use client'

import { useState } from 'react'

export default function Positions() {
  const [positions, setPositions] = useState([
    {
      id: 1,
      symbol: 'BTC/USDT',
      amount: 0.125,
      entry: 48500,
      current: 49200,
      pnl: 87.50,
      pnlPct: 1.44,
      leverage: 1,
      margin: 6062.50,
      liquidation: 0,
      stopLoss: 47530,
      takeProfit: 50925,
      timestamp: '2024-01-15 14:32:15',
      bot: 'Trend Follower Pro',
    },
    {
      id: 2,
      symbol: 'ETH/USDT',
      amount: 2.5,
      entry: 2850,
      current: 2920,
      pnl: 175.00,
      pnlPct: 2.46,
      leverage: 1,
      margin: 7300,
      liquidation: 0,
      stopLoss: 2793,
      takeProfit: 2992,
      timestamp: '2024-01-15 13:15:42',
      bot: 'Wyckoff Analyzer',
    },
    {
      id: 3,
      symbol: 'SOL/USDT',
      amount: 50,
      entry: 98,
      current: 95,
      pnl: -150.00,
      pnlPct: -3.06,
      leverage: 1,
      margin: 4750,
      liquidation: 0,
      stopLoss: 96.04,
      takeProfit: 102.90,
      timestamp: '2024-01-15 12:05:33',
      bot: 'Breakout Hunter',
    },
  ])

  const totalPnl = positions.reduce((sum, p) => sum + p.pnl, 0)
  const totalValue = positions.reduce((sum, p) => sum + p.amount * p.current, 0)
  const totalMargin = positions.reduce((sum, p) => sum + p.margin, 0)

  const closePosition = (id: number) => {
    setPositions(positions.filter(p => p.id !== id))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Open Positions</h1>
          <p className="text-gray-400 mt-1">{positions.length} active positions</p>
        </div>
        <button className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors">
          Close All Positions
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <p className="text-sm text-gray-400 mb-2">Total Unrealized P&L</p>
          <p className={`text-3xl font-bold ${totalPnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(2)}
          </p>
          <p className="text-sm text-gray-400 mt-1">
            {((totalPnl / totalMargin) * 100).toFixed(2)}% of margin
          </p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <p className="text-sm text-gray-400 mb-2">Total Position Value</p>
          <p className="text-3xl font-bold text-white">${totalValue.toFixed(2)}</p>
          <p className="text-sm text-gray-400 mt-1">Current market value</p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <p className="text-sm text-gray-400 mb-2">Total Margin Used</p>
          <p className="text-3xl font-bold text-blue-400">${totalMargin.toFixed(2)}</p>
          <p className="text-sm text-gray-400 mt-1">Locked in trades</p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <p className="text-sm text-gray-400 mb-2">Avg Position Size</p>
          <p className="text-3xl font-bold text-cyan-400">${(totalMargin / positions.length).toFixed(2)}</p>
          <p className="text-sm text-gray-400 mt-1">Per position</p>
        </div>
      </div>

      {/* Positions Table */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-900">
              <tr>
                <th className="text-left py-4 px-6 text-gray-400 font-semibold">Symbol</th>
                <th className="text-left py-4 px-6 text-gray-400 font-semibold">Bot</th>
                <th className="text-right py-4 px-6 text-gray-400 font-semibold">Amount</th>
                <th className="text-right py-4 px-6 text-gray-400 font-semibold">Entry</th>
                <th className="text-right py-4 px-6 text-gray-400 font-semibold">Current</th>
                <th className="text-right py-4 px-6 text-gray-400 font-semibold">Stop Loss</th>
                <th className="text-right py-4 px-6 text-gray-400 font-semibold">Take Profit</th>
                <th className="text-right py-4 px-6 text-gray-400 font-semibold">P&L</th>
                <th className="text-right py-4 px-6 text-gray-400 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((pos) => (
                <tr key={pos.id} className="border-t border-slate-700 hover:bg-slate-700/30 transition-colors">
                  <td className="py-4 px-6">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                        {pos.symbol.split('/')[0].charAt(0)}
                      </div>
                      <div>
                        <p className="font-semibold text-white">{pos.symbol}</p>
                        <p className="text-xs text-gray-400">{pos.timestamp}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6">
                    <span className="text-sm text-gray-300 bg-slate-700 px-2 py-1 rounded">{pos.bot}</span>
                  </td>
                  <td className="text-right px-6 text-white font-medium">{pos.amount}</td>
                  <td className="text-right px-6 text-gray-300">${pos.entry.toLocaleString()}</td>
                  <td className="text-right px-6 text-white font-semibold">${pos.current.toLocaleString()}</td>
                  <td className="text-right px-6 text-red-400">${pos.stopLoss.toLocaleString()}</td>
                  <td className="text-right px-6 text-green-400">${pos.takeProfit.toLocaleString()}</td>
                  <td className="text-right px-6">
                    <div className={pos.pnl >= 0 ? 'text-green-400' : 'text-red-400'}>
                      <p className="font-bold text-lg">{pos.pnl >= 0 ? '+' : ''}{pos.pnlPct.toFixed(2)}%</p>
                      <p className="text-sm">{pos.pnl >= 0 ? '+' : ''}${Math.abs(pos.pnl).toFixed(2)}</p>
                    </div>
                  </td>
                  <td className="text-right px-6">
                    <div className="flex items-center gap-2 justify-end">
                      <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded transition-colors">
                        Edit
                      </button>
                      <button
                        onClick={() => closePosition(pos.id)}
                        className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm font-semibold rounded transition-colors"
                      >
                        Close
                      </button>
                    </div>
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
