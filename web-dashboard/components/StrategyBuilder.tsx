'use client'

import { useState } from 'react'

export default function StrategyBuilder() {
  const [strategy, setStrategy] = useState({
    name: '',
    description: '',
    indicators: [] as string[],
    conditions: [] as any[],
    riskSettings: {
      stopLoss: 2,
      takeProfit: 5,
      maxPosition: 10,
    },
  })

  const availableIndicators = [
    { id: 'rsi', name: 'RSI', category: 'Momentum' },
    { id: 'macd', name: 'MACD', category: 'Trend' },
    { id: 'ema', name: 'EMA', category: 'Trend' },
    { id: 'bollinger', name: 'Bollinger Bands', category: 'Volatility' },
    { id: 'stoch', name: 'Stochastic', category: 'Momentum' },
    { id: 'atr', name: 'ATR', category: 'Volatility' },
    { id: 'volume', name: 'Volume', category: 'Volume' },
    { id: 'obv', name: 'OBV', category: 'Volume' },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Strategy Builder</h1>
          <p className="text-gray-400 mt-1">Create custom trading strategies visually</p>
        </div>
        <div className="flex gap-2">
          <button className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors">
            📋 Load Template
          </button>
          <button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold rounded-lg shadow-lg shadow-blue-500/20 transition-all">
            💾 Save Strategy
          </button>
        </div>
      </div>

      {/* Strategy Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-xl font-semibold text-white mb-4">Strategy Details</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Strategy Name</label>
              <input
                type="text"
                value={strategy.name}
                onChange={(e) => setStrategy({ ...strategy, name: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                placeholder="My Custom Strategy"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Description</label>
              <textarea
                value={strategy.description}
                onChange={(e) => setStrategy({ ...strategy, description: e.target.value })}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500 resize-none"
                rows={3}
                placeholder="Describe your strategy..."
              />
            </div>
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-xl font-semibold text-white mb-4">Risk Settings</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Stop Loss (%)</label>
              <input
                type="number"
                value={strategy.riskSettings.stopLoss}
                onChange={(e) =>
                  setStrategy({
                    ...strategy,
                    riskSettings: { ...strategy.riskSettings, stopLoss: parseFloat(e.target.value) },
                  })
                }
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Take Profit (%)</label>
              <input
                type="number"
                value={strategy.riskSettings.takeProfit}
                onChange={(e) =>
                  setStrategy({
                    ...strategy,
                    riskSettings: { ...strategy.riskSettings, takeProfit: parseFloat(e.target.value) },
                  })
                }
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Max Position Size (%)</label>
              <input
                type="number"
                value={strategy.riskSettings.maxPosition}
                onChange={(e) =>
                  setStrategy({
                    ...strategy,
                    riskSettings: { ...strategy.riskSettings, maxPosition: parseFloat(e.target.value) },
                  })
                }
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Indicators */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-semibold text-white mb-4">Technical Indicators</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {availableIndicators.map((indicator) => (
            <button
              key={indicator.id}
              onClick={() => {
                if (strategy.indicators.includes(indicator.id)) {
                  setStrategy({
                    ...strategy,
                    indicators: strategy.indicators.filter((i) => i !== indicator.id),
                  })
                } else {
                  setStrategy({
                    ...strategy,
                    indicators: [...strategy.indicators, indicator.id],
                  })
                }
              }}
              className={`p-4 rounded-lg border-2 transition-all ${
                strategy.indicators.includes(indicator.id)
                  ? 'border-blue-500 bg-blue-500/10 text-blue-400'
                  : 'border-slate-700 bg-slate-900 text-gray-400 hover:border-slate-600'
              }`}
            >
              <p className="font-semibold mb-1">{indicator.name}</p>
              <p className="text-xs text-gray-500">{indicator.category}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Entry Conditions */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Entry Conditions</h2>
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
            + Add Condition
          </button>
        </div>

        <div className="space-y-3">
          <ConditionRow
            condition="RSI"
            operator="<"
            value="30"
            logic="AND"
          />
          <ConditionRow
            condition="MACD"
            operator="Bullish Crossover"
            value=""
            logic="AND"
          />
          <ConditionRow
            condition="Price"
            operator=">"
            value="EMA 50"
            logic=""
          />
        </div>
      </div>

      {/* Exit Conditions */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Exit Conditions</h2>
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
            + Add Condition
          </button>
        </div>

        <div className="space-y-3">
          <ConditionRow
            condition="RSI"
            operator=">"
            value="70"
            logic="OR"
          />
          <ConditionRow
            condition="Take Profit"
            operator="Hit"
            value="5%"
            logic="OR"
          />
          <ConditionRow
            condition="Stop Loss"
            operator="Hit"
            value="2%"
            logic=""
          />
        </div>
      </div>

      {/* Backtest */}
      <div className="bg-gradient-to-r from-blue-600/20 to-cyan-600/20 rounded-lg p-6 border border-blue-500/30">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white mb-2">Ready to Test?</h2>
            <p className="text-gray-300">Backtest your strategy before going live</p>
          </div>
          <button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold rounded-lg shadow-lg shadow-blue-500/20 transition-all">
            🧪 Run Backtest
          </button>
        </div>
      </div>
    </div>
  )
}

function ConditionRow({ condition, operator, value, logic }: any) {
  return (
    <div className="flex items-center gap-3 p-4 bg-slate-900 rounded-lg">
      {logic && (
        <span className="px-3 py-1 bg-blue-600 text-white text-sm font-semibold rounded">
          {logic}
        </span>
      )}
      <select className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500">
        <option>{condition}</option>
      </select>
      <select className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500">
        <option>{operator}</option>
      </select>
      {value && (
        <input
          type="text"
          value={value}
          className="flex-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
        />
      )}
      <button className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors">
        🗑️
      </button>
    </div>
  )
}
