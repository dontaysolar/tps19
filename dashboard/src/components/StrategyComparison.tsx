'use client'

import { Target, TrendingUp, Award } from 'lucide-react'

interface Props {
  data: any
}

export default function StrategyComparison({ data }: Props) {
  const strategies = data?.strategies || []

  // Sort by P&L
  const sortedStrategies = [...strategies].sort((a, b) => b.pnl - a.pnl)

  return (
    <div className="card">
      <div className="card-header">
        <Target className="w-6 h-6 text-primary-400" />
        <span>Strategy Performance</span>
      </div>

      <div className="space-y-3">
        {sortedStrategies.map((strategy, index) => (
          <StrategyCard 
            key={strategy.name}
            strategy={strategy}
            rank={index + 1}
          />
        ))}
      </div>

      {strategies.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No strategy data available
        </div>
      )}
    </div>
  )
}

function StrategyCard({ strategy, rank }: any) {
  const winRatePercent = (strategy.win_rate * 100).toFixed(0)
  const isPositive = strategy.pnl >= 0

  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 hover:border-gray-600 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          {rank === 1 && <Award className="w-4 h-4 text-yellow-400" />}
          <span className="font-semibold">{strategy.name}</span>
        </div>
        <div className={`text-sm font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
          {isPositive ? '+' : ''}${strategy.pnl.toFixed(2)}
        </div>
      </div>

      {/* Win Rate Bar */}
      <div className="mb-2">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Win Rate</span>
          <span>{winRatePercent}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              strategy.win_rate >= 0.6 ? 'bg-green-500' : 
              strategy.win_rate >= 0.5 ? 'bg-yellow-500' : 
              'bg-red-500'
            }`}
            style={{ width: `${winRatePercent}%` }}
          />
        </div>
      </div>

      {/* Stats */}
      <div className="flex justify-between text-xs text-gray-400">
        <span>{strategy.trades} trades</span>
        <span>Rank #{rank}</span>
      </div>
    </div>
  )
}
