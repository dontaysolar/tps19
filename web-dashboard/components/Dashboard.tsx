'use client'

import { useEffect, useState } from 'react'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalProfit: '+$2,456.78',
    totalTrades: 156,
    winRate: '67.3%',
    activeBots: 3,
  })

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Profit"
          value={stats.totalProfit}
          change="+12.5%"
          positive
        />
        <StatCard
          title="Total Trades"
          value={stats.totalTrades}
          change="+5"
          positive
        />
        <StatCard
          title="Win Rate"
          value={stats.winRate}
          change="+2.1%"
          positive
        />
        <StatCard
          title="Active Bots"
          value={stats.activeBots}
          change="3/10"
          positive={false}
        />
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="btn-primary">Start Bot</button>
          <button className="btn-success">New Trade</button>
          <button className="btn-danger">Stop All</button>
          <button className="bg-slate-700 hover:bg-slate-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors">
            View Logs
          </button>
        </div>
      </div>

      {/* Performance Chart */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Performance (7 Days)</h2>
        <div className="h-64 flex items-center justify-center bg-slate-900 rounded">
          <p className="text-gray-500">Chart visualization goes here</p>
          <p className="text-sm text-gray-600 mt-2">(Install recharts for charts)</p>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-3">
          <ActivityItem
            type="trade"
            message="Bought 0.125 BTC/USDT @ $48,500"
            time="2 minutes ago"
          />
          <ActivityItem
            type="signal"
            message="Strong buy signal detected on ETH/USDT"
            time="5 minutes ago"
          />
          <ActivityItem
            type="bot"
            message="Trend Follower bot started successfully"
            time="15 minutes ago"
          />
          <ActivityItem
            type="profit"
            message="Realized profit: +$87.50 on BTC/USDT"
            time="23 minutes ago"
          />
        </div>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">System Health</h2>
          <div className="space-y-3">
            <HealthBar label="CPU Usage" value={15} color="success" />
            <HealthBar label="Memory" value={32} color="success" />
            <HealthBar label="API Calls" value={65} color="warning" />
            <HealthBar label="Network" value={10} color="success" />
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Active Signals</h2>
          <div className="space-y-2">
            <SignalItem pair="BTC/USDT" signal="BUY" confidence="85%" />
            <SignalItem pair="ETH/USDT" signal="HOLD" confidence="45%" />
            <SignalItem pair="SOL/USDT" signal="SELL" confidence="72%" />
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, change, positive }: any) {
  return (
    <div className="card">
      <h3 className="text-sm text-gray-400 mb-2">{title}</h3>
      <div className="flex items-end justify-between">
        <p className="text-2xl font-bold">{value}</p>
        <span className={`text-sm ${positive ? 'text-success' : 'text-gray-400'}`}>
          {change}
        </span>
      </div>
    </div>
  )
}

function ActivityItem({ type, message, time }: any) {
  const icons: any = {
    trade: '💰',
    signal: '📊',
    bot: '🤖',
    profit: '📈',
  }

  return (
    <div className="flex items-start gap-3 p-3 bg-slate-900 rounded">
      <span className="text-xl">{icons[type]}</span>
      <div className="flex-1">
        <p className="text-sm">{message}</p>
        <p className="text-xs text-gray-500 mt-1">{time}</p>
      </div>
    </div>
  )
}

function HealthBar({ label, value, color }: any) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-400">{label}</span>
        <span>{value}%</span>
      </div>
      <div className="w-full bg-slate-700 rounded-full h-2">
        <div
          className={`bg-${color} h-2 rounded-full transition-all`}
          style={{ width: `${value}%` }}
        ></div>
      </div>
    </div>
  )
}

function SignalItem({ pair, signal, confidence }: any) {
  const signalColor = signal === 'BUY' ? 'success' : signal === 'SELL' ? 'danger' : 'warning'
  
  return (
    <div className="flex items-center justify-between p-3 bg-slate-900 rounded">
      <span className="font-medium">{pair}</span>
      <div className="flex items-center gap-3">
        <span className={`badge-${signalColor}`}>{signal}</span>
        <span className="text-sm text-gray-400">{confidence}</span>
      </div>
    </div>
  )
}
