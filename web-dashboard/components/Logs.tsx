'use client'

import { useState } from 'react'

export default function Logs() {
  const [filter, setFilter] = useState('all')
  const [logs] = useState([
    { id: 1, time: '2024-01-15 14:32:15.234', level: 'INFO', component: 'ExecutionLayer', message: 'Order executed: BUY 0.125 BTC/USDT @ $48,500' },
    { id: 2, time: '2024-01-15 14:32:12.123', level: 'INFO', component: 'SignalLayer', message: 'Generated signal: BUY BTC/USDT (confidence: 85%)' },
    { id: 3, time: '2024-01-15 14:32:10.456', level: 'DEBUG', component: 'MarketAnalysis', message: 'Calculated RSI: 62.5, MACD: bullish crossover' },
    { id: 4, time: '2024-01-15 14:32:08.789', level: 'INFO', component: 'RiskLayer', message: 'Position size validated: 8.5% of portfolio' },
    { id: 5, time: '2024-01-15 14:31:55.234', level: 'WARNING', component: 'InfrastructureLayer', message: 'API rate limit approaching: 95/100 requests used' },
    { id: 6, time: '2024-01-15 14:31:50.567', level: 'INFO', component: 'AIMLLayer', message: 'LSTM prediction: BTC/USDT +2.3% (next 4h)' },
    { id: 7, time: '2024-01-15 14:31:45.123', level: 'ERROR', component: 'Exchange', message: 'Connection timeout, retrying... (attempt 1/3)' },
    { id: 8, time: '2024-01-15 14:31:40.890', level: 'INFO', component: 'ExecutionLayer', message: 'Order filled: SELL 2.5 ETH/USDT @ $2,920' },
    { id: 9, time: '2024-01-15 14:31:35.456', level: 'INFO', component: 'PortfolioLayer', message: 'Portfolio rebalanced: BTC 45%, ETH 35%, SOL 20%' },
    { id: 10, time: '2024-01-15 14:31:30.123', level: 'DEBUG', component: 'SentimentLayer', message: 'Social sentiment score: 72/100 (bullish)' },
  ])

  const filteredLogs = logs.filter((log) => {
    if (filter === 'all') return true
    return log.level.toLowerCase() === filter
  })

  const levelCounts = {
    info: logs.filter(l => l.level === 'INFO').length,
    warning: logs.filter(l => l.level === 'WARNING').length,
    error: logs.filter(l => l.level === 'ERROR').length,
    debug: logs.filter(l => l.level === 'DEBUG').length,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">System Logs</h1>
          <p className="text-gray-400 mt-1">Real-time system activity and debugging</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
            📥 Export Logs
          </button>
          <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors">
            🔄 Refresh
          </button>
          <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors">
            🗑️ Clear
          </button>
        </div>
      </div>

      {/* Log Level Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-blue-400 font-semibold">INFO</span>
            <span className="text-2xl">ℹ️</span>
          </div>
          <p className="text-3xl font-bold text-white">{levelCounts.info}</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-yellow-400 font-semibold">WARNING</span>
            <span className="text-2xl">⚠️</span>
          </div>
          <p className="text-3xl font-bold text-white">{levelCounts.warning}</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-red-400 font-semibold">ERROR</span>
            <span className="text-2xl">❌</span>
          </div>
          <p className="text-3xl font-bold text-white">{levelCounts.error}</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 font-semibold">DEBUG</span>
            <span className="text-2xl">🔍</span>
          </div>
          <p className="text-3xl font-bold text-white">{levelCounts.debug}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        {[
          { value: 'all', label: 'All Logs', count: logs.length },
          { value: 'info', label: 'Info', count: levelCounts.info },
          { value: 'warning', label: 'Warnings', count: levelCounts.warning },
          { value: 'error', label: 'Errors', count: levelCounts.error },
          { value: 'debug', label: 'Debug', count: levelCounts.debug },
        ].map((f) => (
          <button
            key={f.value}
            onClick={() => setFilter(f.value)}
            className={`px-4 py-2 rounded-lg font-semibold transition-all ${
              filter === f.value
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-gray-300 hover:bg-slate-700'
            }`}
          >
            {f.label} ({f.count})
          </button>
        ))}
      </div>

      {/* Logs Table */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full font-mono text-sm">
            <thead className="bg-slate-900">
              <tr>
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Time</th>
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Level</th>
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Component</th>
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Message</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map((log) => (
                <LogRow key={log.id} {...log} />
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Auto-scroll notice */}
      <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
        <span>Auto-scrolling enabled • Showing last 1000 entries</span>
      </div>
    </div>
  )
}

function LogRow({ time, level, component, message }: any) {
  const levelColors = {
    INFO: 'text-blue-400 bg-blue-500/10',
    WARNING: 'text-yellow-400 bg-yellow-500/10',
    ERROR: 'text-red-400 bg-red-500/10',
    DEBUG: 'text-gray-400 bg-gray-500/10',
  }

  return (
    <tr className="border-t border-slate-700 hover:bg-slate-700/30 transition-colors">
      <td className="py-3 px-4 text-gray-400 whitespace-nowrap">{time}</td>
      <td className="px-4">
        <span
          className={`px-2 py-1 rounded text-xs font-semibold ${
            levelColors[level as keyof typeof levelColors]
          }`}
        >
          {level}
        </span>
      </td>
      <td className="px-4 text-cyan-400">{component}</td>
      <td className="px-4 text-gray-300">{message}</td>
    </tr>
  )
}
