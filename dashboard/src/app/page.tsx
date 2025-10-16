'use client'

import { useEffect, useState } from 'react'
import OrganismHealth from '@/components/OrganismHealth'
import LiveTrading from '@/components/LiveTrading'
import PerformanceCharts from '@/components/PerformanceCharts'
import StrategyComparison from '@/components/StrategyComparison'
import AIIntelligence from '@/components/AIIntelligence'
import SystemStatus from '@/components/SystemStatus'
import { useOrganismData } from '@/hooks/useOrganismData'
import { Activity, Brain, TrendingUp, Shield, Zap } from 'lucide-react'

export default function Dashboard() {
  const { data, isConnected, error } = useOrganismData()
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <main className="min-h-screen p-4 lg:p-8">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
              TPS19 APEX ORGANISM
            </h1>
            <p className="text-gray-400 mt-1">Real-Time Monitoring Dashboard</p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-mono">
              {currentTime.toLocaleTimeString()}
            </div>
            <div className="text-sm text-gray-400">
              {currentTime.toLocaleDateString()}
            </div>
          </div>
        </div>
        
        {/* Connection Status */}
        <div className="flex items-center gap-4">
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            isConnected ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
          }`}>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
            <span className="text-sm font-medium">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          
          {error && (
            <div className="text-red-400 text-sm">
              Error: {error}
            </div>
          )}
        </div>
      </header>

      {/* Dashboard Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        {/* Left Column - Status & Health */}
        <div className="xl:col-span-3 space-y-6">
          <SystemStatus data={data} />
          <OrganismHealth data={data} />
        </div>

        {/* Center Column - Main Content */}
        <div className="xl:col-span-6 space-y-6">
          <LiveTrading data={data} />
          <PerformanceCharts data={data} />
        </div>

        {/* Right Column - Intelligence & Strategy */}
        <div className="xl:col-span-3 space-y-6">
          <AIIntelligence data={data} />
          <StrategyComparison data={data} />
        </div>
      </div>

      {/* Quick Stats Bar */}
      <div className="mt-8 grid grid-cols-2 md:grid-cols-5 gap-4">
        <QuickStat 
          icon={<Activity className="w-5 h-5" />}
          label="Uptime"
          value={data?.uptime || '0h 0m'}
          color="blue"
        />
        <QuickStat 
          icon={<TrendingUp className="w-5 h-5" />}
          label="Win Rate"
          value={`${((data?.win_rate || 0) * 100).toFixed(1)}%`}
          color="green"
        />
        <QuickStat 
          icon={<Brain className="w-5 h-5" />}
          label="Decisions"
          value={data?.total_decisions || 0}
          color="purple"
        />
        <QuickStat 
          icon={<Shield className="w-5 h-5" />}
          label="Protected"
          value={data?.trades_blocked || 0}
          color="yellow"
        />
        <QuickStat 
          icon={<Zap className="w-5 h-5" />}
          label="Avg Speed"
          value={`${data?.avg_decision_time || 0}ms`}
          color="cyan"
        />
      </div>
    </main>
  )
}

function QuickStat({ icon, label, value, color }: any) {
  const colorClasses = {
    blue: 'from-blue-500/20 to-blue-600/20 border-blue-500/30',
    green: 'from-green-500/20 to-green-600/20 border-green-500/30',
    purple: 'from-purple-500/20 to-purple-600/20 border-purple-500/30',
    yellow: 'from-yellow-500/20 to-yellow-600/20 border-yellow-500/30',
    cyan: 'from-cyan-500/20 to-cyan-600/20 border-cyan-500/30',
  }

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} border rounded-lg p-4`}>
      <div className="flex items-center gap-2 text-gray-400 mb-1">
        {icon}
        <span className="text-xs font-medium">{label}</span>
      </div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  )
}
