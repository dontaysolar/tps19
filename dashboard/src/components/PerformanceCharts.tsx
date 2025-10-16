'use client'

import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { TrendingUp, Activity } from 'lucide-react'

interface Props {
  data: any
}

export default function PerformanceCharts({ data }: Props) {
  // Generate sample equity curve data
  const equityData = generateEquityCurve(data?.total_pnl || 0)
  const drawdownData = generateDrawdownData()

  return (
    <div className="card">
      <div className="card-header">
        <Activity className="w-6 h-6 text-primary-400" />
        <span>Performance Metrics</span>
      </div>

      {/* Equity Curve */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-gray-400 mb-3">Equity Curve</h3>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={equityData}>
            <defs>
              <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} />
            <YAxis stroke="#9ca3af" fontSize={12} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1f2937', 
                border: '1px solid #374151',
                borderRadius: '8px'
              }}
            />
            <Area 
              type="monotone" 
              dataKey="equity" 
              stroke="#0ea5e9" 
              fillOpacity={1} 
              fill="url(#colorEquity)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Drawdown Chart */}
      <div>
        <h3 className="text-sm font-semibold text-gray-400 mb-3">Drawdown</h3>
        <ResponsiveContainer width="100%" height={150}>
          <AreaChart data={drawdownData}>
            <defs>
              <linearGradient id="colorDrawdown" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} />
            <YAxis stroke="#9ca3af" fontSize={12} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1f2937', 
                border: '1px solid #374151',
                borderRadius: '8px'
              }}
            />
            <Area 
              type="monotone" 
              dataKey="drawdown" 
              stroke="#ef4444" 
              fillOpacity={1} 
              fill="url(#colorDrawdown)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-800">
        <MetricBox 
          label="Sharpe Ratio"
          value={data?.sharpe_ratio?.toFixed(2) || '0.00'}
          color="blue"
        />
        <MetricBox 
          label="Max DD"
          value={`${((data?.max_drawdown || 0) * 100).toFixed(1)}%`}
          color="red"
        />
        <MetricBox 
          label="Total Trades"
          value={data?.total_trades || 0}
          color="green"
        />
      </div>
    </div>
  )
}

function MetricBox({ label, value, color }: any) {
  const colors = {
    blue: 'text-blue-400',
    red: 'text-red-400',
    green: 'text-green-400',
  }

  return (
    <div className="text-center">
      <div className="text-xs text-gray-500 mb-1">{label}</div>
      <div className={`text-xl font-bold ${colors[color]}`}>{value}</div>
    </div>
  )
}

// Helper functions
function generateEquityCurve(totalPnl: number) {
  const points = 30
  const data = []
  let equity = 500
  
  for (let i = 0; i < points; i++) {
    equity += (Math.random() - 0.4) * 10 + (totalPnl / points)
    data.push({
      time: `${i}d`,
      equity: Math.max(equity, 400)
    })
  }
  
  return data
}

function generateDrawdownData() {
  const points = 30
  const data = []
  
  for (let i = 0; i < points; i++) {
    const drawdown = Math.random() * -8
    data.push({
      time: `${i}d`,
      drawdown: drawdown
    })
  }
  
  return data
}
