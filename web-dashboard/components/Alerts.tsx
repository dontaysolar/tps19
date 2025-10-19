'use client'

import { useState } from 'react'

export default function Alerts() {
  const [alerts] = useState([
    {
      id: 1,
      type: 'trade',
      severity: 'success',
      title: 'Trade Executed',
      message: 'Bought 0.125 BTC/USDT @ $48,500',
      time: '2 minutes ago',
      read: false,
    },
    {
      id: 2,
      type: 'signal',
      severity: 'info',
      title: 'Strong Buy Signal',
      message: 'ETH/USDT showing strong buy signal (85% confidence)',
      time: '5 minutes ago',
      read: false,
    },
    {
      id: 3,
      type: 'risk',
      severity: 'warning',
      title: 'Position Size Warning',
      message: 'SOL/USDT position approaching max size limit (85%)',
      time: '12 minutes ago',
      read: false,
    },
    {
      id: 4,
      type: 'trade',
      severity: 'success',
      title: 'Profit Target Hit',
      message: 'Sold 2.5 ETH/USDT @ $2,920 (+2.46%)',
      time: '25 minutes ago',
      read: true,
    },
    {
      id: 5,
      type: 'system',
      severity: 'error',
      title: 'API Rate Limit',
      message: 'Exchange API rate limit reached, retrying in 60s',
      time: '1 hour ago',
      read: true,
    },
    {
      id: 6,
      type: 'bot',
      severity: 'info',
      title: 'Bot Started',
      message: 'Trend Follower Pro started trading BTC/USDT',
      time: '2 hours ago',
      read: true,
    },
  ])

  const unreadCount = alerts.filter(a => !a.read).length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Alerts & Notifications</h1>
          <p className="text-gray-400 mt-1">
            {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
          </p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
            Mark All Read
          </button>
          <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors">
            Clear All
          </button>
        </div>
      </div>

      {/* Alert Categories */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 text-center">
          <p className="text-3xl mb-2">💰</p>
          <p className="text-sm text-gray-400">Trades</p>
          <p className="text-2xl font-bold text-white">12</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 text-center">
          <p className="text-3xl mb-2">🎯</p>
          <p className="text-sm text-gray-400">Signals</p>
          <p className="text-2xl font-bold text-white">8</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 text-center">
          <p className="text-3xl mb-2">⚠️</p>
          <p className="text-sm text-gray-400">Warnings</p>
          <p className="text-2xl font-bold text-yellow-400">3</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 text-center">
          <p className="text-3xl mb-2">❌</p>
          <p className="text-sm text-gray-400">Errors</p>
          <p className="text-2xl font-bold text-red-400">1</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 text-center">
          <p className="text-3xl mb-2">🤖</p>
          <p className="text-sm text-gray-400">System</p>
          <p className="text-2xl font-bold text-white">6</p>
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {alerts.map((alert) => (
          <AlertCard key={alert.id} {...alert} />
        ))}
      </div>
    </div>
  )
}

function AlertCard({ type, severity, title, message, time, read }: any) {
  const icons = {
    trade: '💰',
    signal: '🎯',
    risk: '⚠️',
    system: '🔧',
    bot: '🤖',
    profit: '✅',
    loss: '❌',
  }

  const colors = {
    success: 'border-green-500/30 bg-green-500/10',
    info: 'border-blue-500/30 bg-blue-500/10',
    warning: 'border-yellow-500/30 bg-yellow-500/10',
    error: 'border-red-500/30 bg-red-500/10',
  }

  const textColors = {
    success: 'text-green-400',
    info: 'text-blue-400',
    warning: 'text-yellow-400',
    error: 'text-red-400',
  }

  return (
    <div
      className={`bg-slate-800 rounded-lg p-6 border transition-all hover:scale-[1.01] ${
        !read ? colors[severity as keyof typeof colors] + ' border-l-4' : 'border-slate-700'
      }`}
    >
      <div className="flex items-start gap-4">
        <div className="text-3xl">{icons[type as keyof typeof icons]}</div>
        <div className="flex-1">
          <div className="flex items-start justify-between mb-2">
            <div>
              <h3 className={`text-lg font-semibold ${textColors[severity as keyof typeof textColors]}`}>
                {title}
              </h3>
              <p className="text-gray-300 mt-1">{message}</p>
            </div>
            {!read && (
              <span className="w-3 h-3 bg-blue-500 rounded-full flex-shrink-0 animate-pulse"></span>
            )}
          </div>
          <div className="flex items-center justify-between mt-3">
            <span className="text-sm text-gray-500">{time}</span>
            <div className="flex gap-2">
              <button className="text-sm text-blue-400 hover:text-blue-300 font-medium">View</button>
              <button className="text-sm text-gray-400 hover:text-gray-300 font-medium">Dismiss</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
