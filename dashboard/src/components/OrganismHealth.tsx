'use client'

import { Heart, Brain, Activity, Shield } from 'lucide-react'

interface Props {
  data: any
}

export default function OrganismHealth({ data }: Props) {
  if (!data) return <LoadingSkeleton />

  const healthScore = data.health_score || 0
  const consciousness = data.consciousness || 0
  const status = data.status || 'UNKNOWN'

  const getHealthColor = (score: number) => {
    if (score >= 90) return 'text-green-400'
    if (score >= 70) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getHealthGlow = (score: number) => {
    if (score >= 90) return 'glow-green'
    if (score >= 70) return 'glow-yellow'
    return 'glow-red'
  }

  return (
    <div className="card">
      <div className="card-header">
        <Heart className={`w-6 h-6 ${getHealthColor(healthScore)} animate-heartbeat`} />
        <span>Organism Health</span>
      </div>

      {/* Health Score Circle */}
      <div className="flex justify-center mb-6">
        <div className="relative w-40 h-40">
          <svg className="transform -rotate-90 w-40 h-40">
            <circle
              cx="80"
              cy="80"
              r="70"
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              className="text-gray-800"
            />
            <circle
              cx="80"
              cy="80"
              r="70"
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              strokeDasharray={`${2 * Math.PI * 70}`}
              strokeDashoffset={`${2 * Math.PI * 70 * (1 - healthScore / 100)}`}
              className={getHealthColor(healthScore)}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-4xl font-bold ${getHealthColor(healthScore)}`}>
              {healthScore}
            </span>
            <span className="text-sm text-gray-400">Health</span>
          </div>
        </div>
      </div>

      {/* Status Indicators */}
      <div className="space-y-3">
        <HealthMetric
          icon={<Brain className="w-5 h-5" />}
          label="Consciousness"
          value={`${(consciousness * 100).toFixed(0)}%`}
          percentage={consciousness * 100}
          color="blue"
        />
        
        <HealthMetric
          icon={<Activity className="w-5 h-5" />}
          label="Metabolic Rate"
          value="1.0x"
          percentage={100}
          color="green"
        />
        
        <HealthMetric
          icon={<Shield className="w-5 h-5" />}
          label="Immune System"
          value="Active"
          percentage={100}
          color="purple"
        />
      </div>

      {/* Status Badge */}
      <div className="mt-6 pt-4 border-t border-gray-800">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400">Status</span>
          <span className={`status-badge ${
            status === 'ALIVE' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          }`}>
            {status}
          </span>
        </div>
      </div>
    </div>
  )
}

function HealthMetric({ icon, label, value, percentage, color }: any) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2 text-gray-400">
          {icon}
          <span className="text-sm">{label}</span>
        </div>
        <span className="text-sm font-medium">{value}</span>
      </div>
      <div className="w-full bg-gray-800 rounded-full h-2">
        <div
          className={`${colorClasses[color]} h-2 rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="h-6 bg-gray-800 rounded w-1/3 mb-6" />
      <div className="flex justify-center mb-6">
        <div className="w-40 h-40 bg-gray-800 rounded-full" />
      </div>
      <div className="space-y-4">
        <div className="h-12 bg-gray-800 rounded" />
        <div className="h-12 bg-gray-800 rounded" />
        <div className="h-12 bg-gray-800 rounded" />
      </div>
    </div>
  )
}
