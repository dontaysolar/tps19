'use client'

import { useState } from 'react'

export default function BotManagement() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [bots, setBots] = useState([
    {
      id: 1,
      name: 'Trend Follower Pro',
      strategy: 'Trend Following + ML',
      status: 'running',
      profit: 2456.78,
      profitPct: 12.5,
      trades: 45,
      winRate: 72,
      pairs: ['BTC/USDT', 'ETH/USDT'],
      risk: 'Medium',
      maxDrawdown: -3.2,
      sharpe: 2.8,
      uptime: '15d 4h',
    },
    {
      id: 2,
      name: 'Mean Reversion Master',
      strategy: 'Mean Reversion + RSI',
      status: 'running',
      profit: 1642.30,
      profitPct: 8.3,
      trades: 32,
      winRate: 68,
      pairs: ['BTC/USDT'],
      risk: 'Low',
      maxDrawdown: -1.8,
      sharpe: 3.1,
      uptime: '15d 4h',
    },
    {
      id: 3,
      name: 'Breakout Hunter',
      strategy: 'Breakout + Volume',
      status: 'paused',
      profit: 1028.50,
      profitPct: 5.2,
      trades: 18,
      winRate: 55,
      pairs: ['SOL/USDT'],
      risk: 'High',
      maxDrawdown: -6.5,
      sharpe: 1.9,
      uptime: '12d 8h',
    },
    {
      id: 4,
      name: 'Wyckoff Analyzer',
      strategy: 'Wyckoff Method',
      status: 'running',
      profit: 3102.45,
      profitPct: 15.7,
      trades: 28,
      winRate: 75,
      pairs: ['BTC/USDT', 'ETH/USDT'],
      risk: 'Medium',
      maxDrawdown: -2.1,
      sharpe: 3.5,
      uptime: '18d 2h',
    },
    {
      id: 5,
      name: 'Ichimoku Cloud',
      strategy: 'Ichimoku + Trend',
      status: 'running',
      profit: 1365.90,
      profitPct: 6.9,
      trades: 22,
      winRate: 64,
      pairs: ['ETH/USDT'],
      risk: 'Low',
      maxDrawdown: -2.8,
      sharpe: 2.4,
      uptime: '10d 6h',
    },
    {
      id: 6,
      name: 'Order Flow Pro',
      strategy: 'Order Flow Analysis',
      status: 'paused',
      profit: 612.80,
      profitPct: 3.1,
      trades: 12,
      winRate: 58,
      pairs: ['BTC/USDT'],
      risk: 'High',
      maxDrawdown: -4.2,
      sharpe: 1.7,
      uptime: '5d 12h',
    },
  ])

  const totalProfit = bots.reduce((sum, bot) => sum + bot.profit, 0)
  const avgWinRate = bots.reduce((sum, bot) => sum + bot.winRate, 0) / bots.length
  const runningBots = bots.filter(b => b.status === 'running').length

  return (
    <div className="space-y-6">
      {/* Header & Stats */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Bot Management</h1>
          <p className="text-gray-400 mt-1">Manage and monitor your trading strategies</p>
        </div>
        <button 
          onClick={() => setShowCreateModal(true)}
          className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold rounded-lg shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2"
        >
          <span className="text-xl">+</span>
          <span>Create New Bot</span>
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Total Bots</span>
            <span className="text-2xl">🤖</span>
          </div>
          <p className="text-3xl font-bold text-white">{bots.length}</p>
          <p className="text-sm text-gray-400 mt-1">{runningBots} running</p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Total Profit</span>
            <span className="text-2xl">💰</span>
          </div>
          <p className="text-3xl font-bold text-green-400">+${totalProfit.toFixed(2)}</p>
          <p className="text-sm text-gray-400 mt-1">All time</p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Avg Win Rate</span>
            <span className="text-2xl">🎯</span>
          </div>
          <p className="text-3xl font-bold text-cyan-400">{avgWinRate.toFixed(1)}%</p>
          <p className="text-sm text-gray-400 mt-1">Across all bots</p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Total Trades</span>
            <span className="text-2xl">📊</span>
          </div>
          <p className="text-3xl font-bold text-blue-400">{bots.reduce((sum, b) => sum + b.trades, 0)}</p>
          <p className="text-sm text-gray-400 mt-1">Executed</p>
        </div>
      </div>

      {/* Bots Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {bots.map((bot) => (
          <BotCard key={bot.id} bot={bot} setBots={setBots} />
        ))}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <CreateBotModal onClose={() => setShowCreateModal(false)} setBots={setBots} />
      )}
    </div>
  )
}

function BotCard({ bot, setBots }: any) {
  const [showDetails, setShowDetails] = useState(false)
  const isRunning = bot.status === 'running'

  const toggleBot = () => {
    setBots((prev: any) =>
      prev.map((b: any) =>
        b.id === bot.id ? { ...b, status: isRunning ? 'paused' : 'running' } : b
      )
    )
  }

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-blue-500/50 transition-all">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-white mb-1">{bot.name}</h3>
          <p className="text-sm text-gray-400">{bot.strategy}</p>
          <div className="flex items-center gap-2 mt-2">
            {bot.pairs.map((pair: string) => (
              <span key={pair} className="text-xs px-2 py-1 bg-slate-700 text-gray-300 rounded">
                {pair}
              </span>
            ))}
          </div>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-xs font-semibold ${
            isRunning
              ? 'bg-green-500/20 text-green-400 border border-green-500/30'
              : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
          }`}
        >
          {isRunning ? '● Running' : '⏸ Paused'}
        </span>
      </div>

      {/* Stats */}
      <div className="space-y-3 mb-4">
        <div className="flex items-center justify-between">
          <span className="text-gray-400 text-sm">Profit/Loss</span>
          <span className="text-green-400 font-bold text-lg">
            +${bot.profit.toFixed(2)} ({bot.profitPct >= 0 ? '+' : ''}{bot.profitPct}%)
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-gray-400 text-sm">Win Rate</span>
          <div className="flex items-center gap-2">
            <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full"
                style={{ width: `${bot.winRate}%` }}
              ></div>
            </div>
            <span className="text-white font-semibold text-sm">{bot.winRate}%</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-gray-400 text-sm">Total Trades</span>
          <span className="text-white font-semibold">{bot.trades}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-gray-400 text-sm">Sharpe Ratio</span>
          <span className="text-cyan-400 font-semibold">{bot.sharpe}</span>
        </div>
      </div>

      {/* Details Expander */}
      {showDetails && (
        <div className="mb-4 p-3 bg-slate-900 rounded-lg space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">Max Drawdown</span>
            <span className="text-red-400">{bot.maxDrawdown}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Risk Level</span>
            <span
              className={
                bot.risk === 'Low'
                  ? 'text-green-400'
                  : bot.risk === 'Medium'
                  ? 'text-yellow-400'
                  : 'text-red-400'
              }
            >
              {bot.risk}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Uptime</span>
            <span className="text-white">{bot.uptime}</span>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={toggleBot}
          className={`flex-1 py-2 px-3 rounded-lg font-semibold transition-colors ${
            isRunning
              ? 'bg-yellow-600 hover:bg-yellow-700 text-white'
              : 'bg-green-600 hover:bg-green-700 text-white'
          }`}
        >
          {isRunning ? '⏸ Pause' : '▶ Start'}
        </button>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="flex-1 py-2 px-3 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors"
        >
          {showDetails ? 'Hide' : 'Details'}
        </button>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
          ⚙️
        </button>
      </div>
    </div>
  )
}

function CreateBotModal({ onClose, setBots }: any) {
  const [formData, setFormData] = useState({
    name: '',
    strategy: 'trend_following',
    pairs: ['BTC/USDT'],
    risk: 'medium',
  })

  const strategies = [
    { value: 'trend_following', label: 'Trend Following + ML' },
    { value: 'mean_reversion', label: 'Mean Reversion + RSI' },
    { value: 'breakout', label: 'Breakout + Volume' },
    { value: 'wyckoff', label: 'Wyckoff Method' },
    { value: 'ichimoku', label: 'Ichimoku Cloud' },
    { value: 'order_flow', label: 'Order Flow Analysis' },
  ]

  const handleCreate = () => {
    const newBot = {
      id: Date.now(),
      name: formData.name || 'New Bot',
      strategy: strategies.find(s => s.value === formData.strategy)?.label || 'Custom',
      status: 'paused',
      profit: 0,
      profitPct: 0,
      trades: 0,
      winRate: 0,
      pairs: formData.pairs,
      risk: formData.risk.charAt(0).toUpperCase() + formData.risk.slice(1),
      maxDrawdown: 0,
      sharpe: 0,
      uptime: '0d 0h',
    }
    setBots((prev: any) => [...prev, newBot])
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg p-8 max-w-2xl w-full mx-4 border border-slate-700">
        <h2 className="text-2xl font-bold text-white mb-6">Create New Bot</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Bot Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              placeholder="My Trading Bot"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Strategy</label>
            <select
              value={formData.strategy}
              onChange={(e) => setFormData({ ...formData, strategy: e.target.value })}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              {strategies.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Trading Pairs</label>
            <div className="grid grid-cols-3 gap-2">
              {['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT'].map(
                (pair) => (
                  <label key={pair} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.pairs.includes(pair)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setFormData({ ...formData, pairs: [...formData.pairs, pair] })
                        } else {
                          setFormData({
                            ...formData,
                            pairs: formData.pairs.filter((p) => p !== pair),
                          })
                        }
                      }}
                      className="w-4 h-4"
                    />
                    <span className="text-white text-sm">{pair}</span>
                  </label>
                )
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Risk Level</label>
            <div className="flex gap-3">
              {['low', 'medium', 'high'].map((risk) => (
                <button
                  key={risk}
                  onClick={() => setFormData({ ...formData, risk })}
                  className={`flex-1 py-2 px-4 rounded-lg font-semibold transition-colors ${
                    formData.risk === risk
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-900 text-gray-400 hover:bg-slate-700'
                  }`}
                >
                  {risk.charAt(0).toUpperCase() + risk.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex gap-3 mt-8">
          <button
            onClick={onClose}
            className="flex-1 py-3 px-4 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleCreate}
            className="flex-1 py-3 px-4 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold rounded-lg transition-colors"
          >
            Create Bot
          </button>
        </div>
      </div>
    </div>
  )
}
