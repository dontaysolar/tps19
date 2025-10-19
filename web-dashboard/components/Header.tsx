'use client'

import { useState, useEffect } from 'react'

export default function Header() {
  const [time, setTime] = useState(new Date())
  const [balance, setBalance] = useState({ total: 125640.50, change: 2456.78, changePct: 1.99 })

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left: Portfolio Value */}
        <div className="flex items-center gap-8">
          <div>
            <p className="text-sm text-gray-400 mb-1">Total Portfolio Value</p>
            <div className="flex items-baseline gap-3">
              <h2 className="text-3xl font-bold text-white">
                ${balance.total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </h2>
              <span className="text-green-400 text-lg font-semibold">
                +${balance.change.toFixed(2)} (+{balance.changePct}%)
              </span>
            </div>
          </div>

          <div className="h-12 w-px bg-slate-700"></div>

          {/* Quick Stats */}
          <div className="flex gap-6">
            <div>
              <p className="text-xs text-gray-400 mb-1">24h Volume</p>
              <p className="text-lg font-semibold text-white">$45,230</p>
            </div>
            <div>
              <p className="text-xs text-gray-400 mb-1">Win Rate</p>
              <p className="text-lg font-semibold text-green-400">67.3%</p>
            </div>
            <div>
              <p className="text-xs text-gray-400 mb-1">Active Bots</p>
              <p className="text-lg font-semibold text-blue-400">6 / 10</p>
            </div>
          </div>
        </div>

        {/* Right: Actions & Time */}
        <div className="flex items-center gap-4">
          {/* Quick Actions */}
          <button className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors flex items-center gap-2">
            <span>🚀</span>
            <span>Start Bot</span>
          </button>

          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors flex items-center gap-2">
            <span>💱</span>
            <span>New Trade</span>
          </button>

          <div className="h-8 w-px bg-slate-700"></div>

          {/* Notifications */}
          <button className="relative p-2 hover:bg-slate-700 rounded-lg transition-colors">
            <span className="text-2xl">🔔</span>
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* Time */}
          <div className="text-right">
            <p className="text-sm font-semibold text-white">
              {time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </p>
            <p className="text-xs text-gray-400">
              {time.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
            </p>
          </div>
        </div>
      </div>
    </header>
  )
}
