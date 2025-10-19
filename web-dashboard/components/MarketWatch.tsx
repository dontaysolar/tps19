'use client'

import { useState, useEffect } from 'react'

export default function MarketWatch() {
  const [markets] = useState([
    { symbol: 'BTC/USDT', price: 49200, change: 2.45, volume: '24.5B', high: 49800, low: 47500, signal: 'BUY', confidence: 85 },
    { symbol: 'ETH/USDT', price: 2920, change: 1.82, volume: '12.3B', high: 2980, low: 2850, signal: 'BUY', confidence: 78 },
    { symbol: 'SOL/USDT', price: 95, change: -3.06, volume: '1.2B', high: 102, low: 94, signal: 'SELL', confidence: 72 },
    { symbol: 'BNB/USDT', price: 315, change: 0.85, volume: '2.1B', high: 320, low: 310, signal: 'HOLD', confidence: 45 },
    { symbol: 'XRP/USDT', price: 0.62, change: 4.20, volume: '3.5B', high: 0.65, low: 0.59, signal: 'BUY', confidence: 82 },
    { symbol: 'ADA/USDT', price: 0.48, change: -1.52, volume: '980M', high: 0.50, low: 0.47, signal: 'HOLD', confidence: 38 },
  ])

  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Market Watch</h1>
          <p className="text-gray-400 mt-1">Real-time market data and trading signals</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-sm text-gray-400">Live Updates</span>
          </div>
          <span className="text-sm text-gray-400">{time.toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <p className="text-sm text-gray-400 mb-2">Market Cap</p>
          <p className="text-3xl font-bold text-white">$2.45T</p>
          <p className="text-sm text-green-400 mt-1">+2.1% (24h)</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <p className="text-sm text-gray-400 mb-2">24h Volume</p>
          <p className="text-3xl font-bold text-white">$98.5B</p>
          <p className="text-sm text-blue-400 mt-1">Above average</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <p className="text-sm text-gray-400 mb-2">BTC Dominance</p>
          <p className="text-3xl font-bold text-white">52.3%</p>
          <p className="text-sm text-gray-400 mt-1">-0.3% (24h)</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <p className="text-sm text-gray-400 mb-2">Fear & Greed</p>
          <p className="text-3xl font-bold text-green-400">72</p>
          <p className="text-sm text-green-400 mt-1">Greed</p>
        </div>
      </div>

      {/* Market Table */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-900">
            <tr>
              <th className="text-left py-4 px-6 text-gray-400 font-semibold">Symbol</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">Price</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">24h Change</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">24h High</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">24h Low</th>
              <th className="text-right py-4 px-6 text-gray-400 font-semibold">Volume</th>
              <th className="text-center py-4 px-6 text-gray-400 font-semibold">AI Signal</th>
              <th className="text-center py-4 px-6 text-gray-400 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {markets.map((market) => (
              <tr key={market.symbol} className="border-t border-slate-700 hover:bg-slate-700/30 transition-colors">
                <td className="py-4 px-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center text-white font-bold">
                      {market.symbol.split('/')[0].charAt(0)}
                    </div>
                    <span className="font-semibold text-white">{market.symbol}</span>
                  </div>
                </td>
                <td className="text-right px-6 text-white font-bold text-lg">
                  ${market.price.toLocaleString()}
                </td>
                <td className="text-right px-6">
                  <span className={`font-semibold ${market.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {market.change >= 0 ? '+' : ''}{market.change}%
                  </span>
                </td>
                <td className="text-right px-6 text-gray-300">${market.high.toLocaleString()}</td>
                <td className="text-right px-6 text-gray-300">${market.low.toLocaleString()}</td>
                <td className="text-right px-6 text-gray-300">{market.volume}</td>
                <td className="text-center px-6">
                  <div className="inline-flex flex-col items-center">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        market.signal === 'BUY'
                          ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                          : market.signal === 'SELL'
                          ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                          : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                      }`}
                    >
                      {market.signal}
                    </span>
                    <span className="text-xs text-gray-400 mt-1">{market.confidence}%</span>
                  </div>
                </td>
                <td className="text-center px-6">
                  <div className="flex items-center gap-2 justify-center">
                    <button className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-sm font-semibold rounded transition-colors">
                      Buy
                    </button>
                    <button className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-sm font-semibold rounded transition-colors">
                      Sell
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Chart Placeholder */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-semibold text-white mb-4">Price Chart</h2>
        <div className="h-96 flex items-center justify-center bg-slate-900 rounded-lg">
          <div className="text-center">
            <p className="text-gray-500 text-2xl mb-2">📈</p>
            <p className="text-gray-400">TradingView chart integration</p>
            <p className="text-sm text-gray-600 mt-1">Connect TradingView or use Recharts</p>
          </div>
        </div>
      </div>
    </div>
  )
}
