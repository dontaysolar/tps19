'use client'

import { useState } from 'react'

export default function Settings() {
  const [activeTab, setActiveTab] = useState('api')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Settings</h1>
        <p className="text-gray-400 mt-1">Configure your trading system</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-700">
        {[
          { id: 'api', label: 'API Configuration', icon: '🔌' },
          { id: 'risk', label: 'Risk Management', icon: '🛡️' },
          { id: 'trading', label: 'Trading Pairs', icon: '💱' },
          { id: 'notifications', label: 'Notifications', icon: '🔔' },
          { id: 'advanced', label: 'Advanced', icon: '⚙️' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-3 font-semibold transition-all ${
              activeTab === tab.id
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="min-h-[600px]">
        {activeTab === 'api' && <APISettings />}
        {activeTab === 'risk' && <RiskSettings />}
        {activeTab === 'trading' && <TradingPairs />}
        {activeTab === 'notifications' && <NotificationSettings />}
        {activeTab === 'advanced' && <AdvancedSettings />}
      </div>
    </div>
  )
}

function APISettings() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-semibold text-white mb-4">Exchange API</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Exchange</label>
            <select className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500">
              <option>Crypto.com</option>
              <option>Binance</option>
              <option>Coinbase</option>
              <option>Kraken</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">API Key</label>
            <input
              type="password"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              placeholder="••••••••••••••••"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">API Secret</label>
            <input
              type="password"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              placeholder="••••••••••••••••"
            />
          </div>
          <button className="w-full py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors">
            ✅ Save & Test Connection
          </button>
        </div>
      </div>

      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-semibold text-white mb-4">Telegram Notifications</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Bot Token</label>
            <input
              type="password"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              placeholder="Bot token from @BotFather"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">Chat ID</label>
            <input
              type="text"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              placeholder="Your Telegram chat ID"
            />
          </div>
          <button className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
            💬 Send Test Message
          </button>
        </div>
      </div>
    </div>
  )
}

function RiskSettings() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-semibold text-white mb-4">Position Limits</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Max Position Size (%)</label>
            <input
              type="number"
              defaultValue="10"
              min="1"
              max="100"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Maximum % of capital per position</p>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">Max Open Positions</label>
            <input
              type="number"
              defaultValue="10"
              min="1"
              max="50"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">Max Leverage</label>
            <input
              type="number"
              defaultValue="1"
              min="1"
              max="10"
              step="0.1"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-semibold text-white mb-4">Stop Loss & Take Profit</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Default Stop Loss (%)</label>
            <input
              type="number"
              defaultValue="2"
              min="0.5"
              max="20"
              step="0.5"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">Default Take Profit (%)</label>
            <input
              type="number"
              defaultValue="5"
              min="1"
              max="50"
              step="0.5"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">Daily Loss Limit (%)</label>
            <input
              type="number"
              defaultValue="5"
              min="1"
              max="50"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">System pauses if reached</p>
          </div>
        </div>
      </div>

      <div className="lg:col-span-2">
        <button className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
          💾 Save Risk Settings
        </button>
      </div>
    </div>
  )
}

function TradingPairs() {
  const [pairs, setPairs] = useState([
    { symbol: 'BTC/USDT', enabled: true, minSize: 0.001, maxSize: 1.0 },
    { symbol: 'ETH/USDT', enabled: true, minSize: 0.01, maxSize: 10.0 },
    { symbol: 'SOL/USDT', enabled: true, minSize: 1, maxSize: 100 },
    { symbol: 'BNB/USDT', enabled: false, minSize: 0.1, maxSize: 50 },
    { symbol: 'XRP/USDT', enabled: false, minSize: 10, maxSize: 1000 },
    { symbol: 'ADA/USDT', enabled: false, minSize: 10, maxSize: 1000 },
  ])

  return (
    <div className="space-y-6">
      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-900">
            <tr>
              <th className="text-left py-4 px-6 text-gray-400 font-semibold">Pair</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">Min Size</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">Max Size</th>
              <th className="text-center py-4 px-6 text-gray-400 font-semibold">Status</th>
            </tr>
          </thead>
          <tbody>
            {pairs.map((pair) => (
              <tr key={pair.symbol} className="border-t border-slate-700">
                <td className="py-4 px-6">
                  <span className="font-semibold text-white">{pair.symbol}</span>
                </td>
                <td className="text-right px-6 text-gray-300">{pair.minSize}</td>
                <td className="text-right px-6 text-gray-300">{pair.maxSize}</td>
                <td className="text-center px-6">
                  <button
                    onClick={() =>
                      setPairs(
                        pairs.map((p) =>
                          p.symbol === pair.symbol ? { ...p, enabled: !p.enabled } : p
                        )
                      )
                    }
                    className={`px-4 py-1.5 rounded-full text-sm font-semibold transition-colors ${
                      pair.enabled
                        ? 'bg-green-600 hover:bg-green-700 text-white'
                        : 'bg-slate-700 hover:bg-slate-600 text-gray-300'
                    }`}
                  >
                    {pair.enabled ? 'Enabled' : 'Disabled'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
        💾 Save Trading Pairs
      </button>
    </div>
  )
}

function NotificationSettings() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {[
        { title: 'Trading Enabled', description: 'Allow system to execute trades', enabled: false },
        { title: 'AI/ML Predictions', description: 'Use ML models for signals', enabled: true },
        { title: 'Telegram Notifications', description: 'Send alerts to Telegram', enabled: true },
        { title: 'Trade Notifications', description: 'Alert on every trade', enabled: true },
        { title: 'Profit Notifications', description: 'Alert on profitable closes', enabled: true },
        { title: 'Loss Notifications', description: 'Alert on losing trades', enabled: true },
        { title: 'Daily Report', description: 'Send daily performance summary', enabled: true },
        { title: 'Error Notifications', description: 'Alert on system errors', enabled: true },
      ].map((setting) => (
        <div key={setting.title} className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <p className="font-semibold text-white mb-1">{setting.title}</p>
              <p className="text-sm text-gray-400">{setting.description}</p>
            </div>
            <ToggleSwitch enabled={setting.enabled} />
          </div>
        </div>
      ))}
    </div>
  )
}

function AdvancedSettings() {
  return (
    <div className="space-y-6">
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-semibold text-white mb-4">System Performance</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Update Interval (seconds)</label>
            <input
              type="number"
              defaultValue="60"
              min="5"
              max="300"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">API Rate Limit (req/min)</label>
            <input
              type="number"
              defaultValue="120"
              min="10"
              max="1000"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-semibold text-white mb-4">Data Management</h2>
        <div className="space-y-3">
          <button className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
            📥 Export All Data (JSON)
          </button>
          <button className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
            📊 Export Trade History (CSV)
          </button>
          <button className="w-full py-3 bg-yellow-600 hover:bg-yellow-700 text-white font-semibold rounded-lg transition-colors">
            🔄 Reset Statistics
          </button>
          <button className="w-full py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors">
            🗑️ Clear All Data
          </button>
        </div>
      </div>
    </div>
  )
}

function ToggleSwitch({ enabled }: any) {
  return (
    <button
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        enabled ? 'bg-green-500' : 'bg-slate-600'
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
