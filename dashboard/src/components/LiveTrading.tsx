'use client'

import { TrendingUp, TrendingDown, DollarSign, Clock } from 'lucide-react'

interface Props {
  data: any
}

export default function LiveTrading({ data }: Props) {
  if (!data) return <LoadingSkeleton />

  const positions = data.positions || []
  const dailyPnL = data.daily_pnl || 0
  const totalPnL = data.total_pnl || 0

  return (
    <div className="card">
      <div className="card-header">
        <TrendingUp className="w-6 h-6 text-primary-400" />
        <span>Live Trading</span>
      </div>

      {/* P&L Summary */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <PnLCard
          label="Daily P&L"
          value={dailyPnL}
          icon={<Clock className="w-5 h-5" />}
        />
        <PnLCard
          label="Total P&L"
          value={totalPnL}
          icon={<DollarSign className="w-5 h-5" />}
        />
      </div>

      {/* Active Positions */}
      <div>
        <h3 className="text-sm font-semibold text-gray-400 mb-3">
          Active Positions ({positions.length})
        </h3>
        
        {positions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No active positions
          </div>
        ) : (
          <div className="space-y-3">
            {positions.map((position: any, index: number) => (
              <PositionCard key={index} position={position} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function PnLCard({ label, value, icon }: any) {
  const isPositive = value >= 0
  const color = isPositive ? 'text-green-400' : 'text-red-400'
  const bgColor = isPositive ? 'bg-green-500/10' : 'bg-red-500/10'

  return (
    <div className={`${bgColor} rounded-lg p-4`}>
      <div className="flex items-center gap-2 text-gray-400 mb-1">
        {icon}
        <span className="text-xs font-medium">{label}</span>
      </div>
      <div className={`text-2xl font-bold ${color}`}>
        {isPositive ? '+' : ''}${value.toFixed(2)}
      </div>
    </div>
  )
}

function PositionCard({ position }: any) {
  const pnl = position.pnl || 0
  const pnlPercent = ((position.current_price - position.entry_price) / position.entry_price) * 100
  const isPositive = pnl >= 0

  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 hover:border-gray-600 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div>
          <div className="font-semibold text-lg">{position.symbol}</div>
          <div className="text-sm text-gray-400 capitalize">{position.side}</div>
        </div>
        <div className={`flex items-center gap-1 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
          {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
          <span className="font-semibold">
            {isPositive ? '+' : ''}{pnlPercent.toFixed(2)}%
          </span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 text-sm">
        <div>
          <div className="text-gray-500 text-xs">Entry</div>
          <div className="font-mono">${position.entry_price.toLocaleString()}</div>
        </div>
        <div>
          <div className="text-gray-500 text-xs">Current</div>
          <div className="font-mono">${position.current_price.toLocaleString()}</div>
        </div>
        <div>
          <div className="text-gray-500 text-xs">P&L</div>
          <div className={`font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
            ${Math.abs(pnl).toFixed(2)}
          </div>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-gray-400">
        <span>Size: {position.size}</span>
        <span>Value: ${(position.size * position.current_price).toFixed(2)}</span>
      </div>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="h-6 bg-gray-800 rounded w-1/4 mb-6" />
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="h-24 bg-gray-800 rounded" />
        <div className="h-24 bg-gray-800 rounded" />
      </div>
      <div className="space-y-3">
        <div className="h-32 bg-gray-800 rounded" />
        <div className="h-32 bg-gray-800 rounded" />
      </div>
    </div>
  )
}
