'use client'

import { useState } from 'react'
import Dashboard from '@/components/Dashboard'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard')

  return (
    <div className="flex h-screen bg-slate-900">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-slate-900 p-6">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'bots' && <BotManagement />}
          {activeTab === 'positions' && <Positions />}
          {activeTab === 'history' && <TradeHistory />}
          {activeTab === 'analytics' && <Analytics />}
          {activeTab === 'settings' && <Settings />}
        </main>
      </div>
    </div>
  )
}

function BotManagement() {
  const [bots, setBots] = useState([
    { id: 1, name: 'Trend Follower', status: 'running', profit: '+12.5%', trades: 45, pairs: ['BTC/USDT', 'ETH/USDT'] },
    { id: 2, name: 'Mean Reversion', status: 'running', profit: '+8.3%', trades: 32, pairs: ['BTC/USDT'] },
    { id: 3, name: 'Breakout Trader', status: 'paused', profit: '+5.2%', trades: 18, pairs: ['SOL/USDT'] },
    { id: 4, name: 'Wyckoff Analyzer', status: 'running', profit: '+15.7%', trades: 28, pairs: ['BTC/USDT', 'ETH/USDT'] },
    { id: 5, name: 'Ichimoku Cloud', status: 'running', profit: '+6.9%', trades: 22, pairs: ['ETH/USDT'] },
    { id: 6, name: 'Order Flow Bot', status: 'paused', profit: '+3.1%', trades: 12, pairs: ['BTC/USDT'] },
  ])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Bot Management</h1>
          <p className="text-gray-400 mt-1">Manage your trading strategies</p>
        </div>
        <button className="btn-primary">+ Create New Bot</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {bots.map(bot => (
          <BotCard key={bot.id} {...bot} />
        ))}
      </div>
    </div>
  )
}

function BotCard({ name, status, profit, trades, pairs }: any) {
  const isRunning = status === 'running'
  const isProfitable = profit.startsWith('+')

  return (
    <div className="card hover:border-primary-500 transition-all cursor-pointer">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold">{name}</h3>
          <p className="text-xs text-gray-500 mt-1">{pairs.join(', ')}</p>
        </div>
        <span className={`badge-${isRunning ? 'success' : 'warning'}`}>
          {status}
        </span>
      </div>
      
      <div className="space-y-3 mb-4">
        <div className="flex justify-between items-center">
          <span className="text-gray-400 text-sm">Profit/Loss</span>
          <span className={`font-bold text-lg ${isProfitable ? 'text-success' : 'text-danger'}`}>
            {profit}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-400 text-sm">Total Trades</span>
          <span className="font-semibold">{trades}</span>
        </div>
      </div>

      <div className="flex gap-2">
        <button className={`flex-1 text-sm font-semibold py-2 px-3 rounded-lg transition-colors ${
          isRunning 
            ? 'bg-yellow-600 hover:bg-yellow-700 text-white' 
            : 'bg-green-600 hover:bg-green-700 text-white'
        }`}>
          {isRunning ? 'Pause' : 'Start'}
        </button>
        <button className="flex-1 btn-primary text-sm">Settings</button>
      </div>
    </div>
  )
}

function Positions() {
  const positions = [
    { symbol: 'BTC/USDT', amount: '0.125', entry: 48500, current: 49200, pnl: 87.50, pnlPct: '+1.44%' },
    { symbol: 'ETH/USDT', amount: '2.5', entry: 2850, current: 2920, pnl: 175.00, pnlPct: '+2.46%' },
    { symbol: 'SOL/USDT', amount: '50', entry: 98, current: 95, pnl: -150.00, pnlPct: '-3.06%' },
  ]

  const totalPnl = positions.reduce((sum, p) => sum + p.pnl, 0)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Open Positions</h1>
          <p className="text-gray-400 mt-1">{positions.length} active positions</p>
        </div>
        <div className="card !p-4">
          <p className="text-sm text-gray-400">Total Unrealized P&L</p>
          <p className={`text-2xl font-bold ${totalPnl > 0 ? 'text-success' : 'text-danger'}`}>
            {totalPnl > 0 ? '+' : ''}${totalPnl.toFixed(2)}
          </p>
        </div>
      </div>

      <div className="card overflow-hidden !p-0">
        <table className="w-full">
          <thead className="bg-slate-900">
            <tr>
              <th className="text-left py-4 px-6 text-gray-400 font-semibold">Symbol</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">Amount</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">Entry Price</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">Current Price</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">P&L</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((pos, idx) => (
              <PositionRow key={idx} {...pos} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function PositionRow({ symbol, amount, entry, current, pnl, pnlPct }: any) {
  const isProfit = pnl > 0
  
  return (
    <tr className="border-t border-slate-700/50 hover:bg-slate-700/20 transition-colors">
      <td className="py-4 px-6">
        <span className="font-semibold">{symbol}</span>
      </td>
      <td className="text-right px-6">{amount}</td>
      <td className="text-right px-6 text-gray-400">${entry.toLocaleString()}</td>
      <td className="text-right px-6">${current.toLocaleString()}</td>
      <td className="text-right px-6">
        <div className={isProfit ? 'text-success' : 'text-danger'}>
          <div className="font-semibold">{pnlPct}</div>
          <div className="text-sm">${Math.abs(pnl).toFixed(2)}</div>
        </div>
      </td>
      <td className="text-right px-6">
        <button className="btn-danger text-sm">Close Position</button>
      </td>
    </tr>
  )
}

function TradeHistory() {
  const trades = [
    { time: '2024-01-15 14:32:15', symbol: 'BTC/USDT', side: 'BUY', amount: '0.125', price: 48500, pnl: 87.50, strategy: 'Trend Follower' },
    { time: '2024-01-15 13:15:42', symbol: 'ETH/USDT', side: 'SELL', amount: '2.5', price: 2920, pnl: 175.00, strategy: 'Mean Reversion' },
    { time: '2024-01-15 12:05:33', symbol: 'SOL/USDT', side: 'BUY', amount: '50', price: 98, pnl: -45.00, strategy: 'Breakout Trader' },
    { time: '2024-01-15 11:20:11', symbol: 'BTC/USDT', side: 'SELL', amount: '0.1', price: 48300, pnl: 120.00, strategy: 'Wyckoff Analyzer' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Trade History</h1>
          <p className="text-gray-400 mt-1">Complete trading history</p>
        </div>
        <div className="flex gap-2">
          <button className="bg-slate-700 hover:bg-slate-600 text-white font-semibold py-2 px-4 rounded-lg">
            Export CSV
          </button>
          <button className="bg-slate-700 hover:bg-slate-600 text-white font-semibold py-2 px-4 rounded-lg">
            Filter
          </button>
        </div>
      </div>

      <div className="card overflow-hidden !p-0">
        <table className="w-full">
          <thead className="bg-slate-900">
            <tr>
              <th className="text-left py-4 px-6 text-gray-400 font-semibold">Time</th>
              <th className="text-left py-4 px-6 text-gray-400 font-semibold">Symbol</th>
              <th className="text-left py-4 px-6 text-gray-400 font-semibold">Side</th>
              <th className="text-left py-4 px-6 text-gray-400 font-semibold">Strategy</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">Amount</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">Price</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">P&L</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade, idx) => (
              <TradeRow key={idx} {...trade} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function TradeRow({ time, symbol, side, strategy, amount, price, pnl }: any) {
  return (
    <tr className="border-t border-slate-700/50 hover:bg-slate-700/20 transition-colors">
      <td className="py-4 px-6 text-gray-400 text-sm">{time}</td>
      <td className="px-6 font-semibold">{symbol}</td>
      <td className="px-6">
        <span className={`badge-${side === 'BUY' ? 'success' : 'danger'}`}>
          {side}
        </span>
      </td>
      <td className="px-6 text-sm text-gray-400">{strategy}</td>
      <td className="text-right px-6 text-gray-400">{amount}</td>
      <td className="text-right px-6">${price.toLocaleString()}</td>
      <td className={`text-right px-6 font-semibold ${pnl > 0 ? 'text-success' : 'text-danger'}`}>
        {pnl > 0 ? '+' : ''}${pnl.toFixed(2)}
      </td>
    </tr>
  )
}

function Analytics() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="text-gray-400 mt-1">Performance metrics and insights</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-sm text-gray-400 mb-2">Sharpe Ratio</h3>
          <p className="text-3xl font-bold text-success">2.34</p>
          <p className="text-sm text-gray-500 mt-1">Excellent risk-adjusted returns</p>
        </div>
        <div className="card">
          <h3 className="text-sm text-gray-400 mb-2">Max Drawdown</h3>
          <p className="text-3xl font-bold text-warning">-8.5%</p>
          <p className="text-sm text-gray-500 mt-1">Within acceptable limits</p>
        </div>
        <div className="card">
          <h3 className="text-sm text-gray-400 mb-2">Profit Factor</h3>
          <p className="text-3xl font-bold text-success">3.2</p>
          <p className="text-sm text-gray-500 mt-1">Strong profitability</p>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Equity Curve</h2>
        <div className="h-80 flex items-center justify-center bg-slate-900 rounded-lg">
          <div className="text-center">
            <p className="text-gray-500 text-lg mb-2">📈 Chart Area</p>
            <p className="text-sm text-gray-600">Performance visualization</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Strategy Performance</h2>
          <div className="space-y-3">
            <StrategyBar strategy="Trend Following" winRate={72} trades={45} profit="+12.5%" />
            <StrategyBar strategy="Mean Reversion" winRate={68} trades={32} profit="+8.3%" />
            <StrategyBar strategy="Breakout" winRate={55} trades={18} profit="+5.2%" />
            <StrategyBar strategy="Wyckoff" winRate={75} trades={28} profit="+15.7%" />
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Risk Metrics</h2>
          <div className="space-y-4">
            <RiskMetric label="Position Size" value="8.5%" limit="10%" />
            <RiskMetric label="Daily Loss" value="1.2%" limit="5%" />
            <RiskMetric label="Drawdown" value="8.5%" limit="20%" />
            <RiskMetric label="Leverage" value="1.0x" limit="3.0x" />
          </div>
        </div>
      </div>
    </div>
  )
}

function StrategyBar({ strategy, winRate, trades, profit }: any) {
  return (
    <div className="p-3 bg-slate-900 rounded">
      <div className="flex justify-between items-center mb-2">
        <span className="font-medium">{strategy}</span>
        <span className="text-success text-sm">{profit}</span>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <div className="w-full bg-slate-700 rounded-full h-2">
            <div className="bg-success h-2 rounded-full" style={{ width: `${winRate}%` }}></div>
          </div>
        </div>
        <span className="text-sm text-gray-400">{winRate}% • {trades} trades</span>
      </div>
    </div>
  )
}

function RiskMetric({ label, value, limit }: any) {
  const percentage = (parseFloat(value) / parseFloat(limit)) * 100
  const color = percentage < 50 ? 'success' : percentage < 80 ? 'warning' : 'danger'
  
  return (
    <div>
      <div className="flex justify-between text-sm mb-2">
        <span className="text-gray-400">{label}</span>
        <span>{value} / {limit}</span>
      </div>
      <div className="w-full bg-slate-700 rounded-full h-2">
        <div className={`bg-${color} h-2 rounded-full transition-all`} style={{ width: `${percentage}%` }}></div>
      </div>
    </div>
  )
}

function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-gray-400 mt-1">Configure your trading system</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">API Configuration</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Exchange</label>
              <select className="input w-full">
                <option>Crypto.com</option>
                <option>Binance</option>
                <option>Coinbase</option>
                <option>Kraken</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">API Key</label>
              <input type="password" className="input w-full" placeholder="••••••••••••••••" />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">API Secret</label>
              <input type="password" className="input w-full" placeholder="••••••••••••••••" />
            </div>
            <button className="btn-success w-full">✅ Save & Test Connection</button>
          </div>
        </div>
        
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Risk Management</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Max Position Size (%)</label>
              <input type="number" className="input w-full" defaultValue="10" min="1" max="100" />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Daily Loss Limit (%)</label>
              <input type="number" className="input w-full" defaultValue="5" min="1" max="50" />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Stop Loss (%)</label>
              <input type="number" className="input w-full" defaultValue="2" min="0.5" max="20" />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Take Profit (%)</label>
              <input type="number" className="input w-full" defaultValue="5" min="1" max="50" />
            </div>
            <button className="btn-primary w-full">Update Risk Settings</button>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Trading Pairs</h2>
          <div className="space-y-3 mb-4">
            <PairToggle pair="BTC/USDT" enabled={true} />
            <PairToggle pair="ETH/USDT" enabled={true} />
            <PairToggle pair="SOL/USDT" enabled={true} />
            <PairToggle pair="BNB/USDT" enabled={false} />
            <PairToggle pair="XRP/USDT" enabled={false} />
          </div>
          <button className="btn-primary w-full">+ Add New Pair</button>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">System Settings</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-slate-900 rounded">
              <div>
                <p className="font-medium">Trading Enabled</p>
                <p className="text-sm text-gray-400">Allow system to execute trades</p>
              </div>
              <ToggleSwitch enabled={false} />
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-900 rounded">
              <div>
                <p className="font-medium">AI/ML Predictions</p>
                <p className="text-sm text-gray-400">Use ML models for signals</p>
              </div>
              <ToggleSwitch enabled={true} />
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-900 rounded">
              <div>
                <p className="font-medium">Telegram Notifications</p>
                <p className="text-sm text-gray-400">Send alerts to Telegram</p>
              </div>
              <ToggleSwitch enabled={true} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function PairToggle({ pair, enabled }: any) {
  return (
    <div className="flex items-center justify-between p-3 bg-slate-900 rounded">
      <span className="font-medium">{pair}</span>
      <ToggleSwitch enabled={enabled} />
    </div>
  )
}

function ToggleSwitch({ enabled }: any) {
  return (
    <button
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        enabled ? 'bg-success' : 'bg-slate-600'
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          enabled ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  )
}
