'use client'

import { Brain, Zap, Activity, TrendingUp } from 'lucide-react'

interface Props {
  data: any
}

export default function AIIntelligence({ data }: Props) {
  const mlConfidence = data?.ml_confidence || 0
  const modelWeights = data?.model_weights || {}

  return (
    <div className="card">
      <div className="card-header">
        <Brain className="w-6 h-6 text-purple-400 animate-pulse-slow" />
        <span>AI Intelligence</span>
      </div>

      {/* ML Confidence */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">ML Confidence</span>
          <span className="text-lg font-bold text-purple-400">
            {(mlConfidence * 100).toFixed(0)}%
          </span>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-purple-600 to-purple-400 h-3 rounded-full transition-all"
            style={{ width: `${mlConfidence * 100}%` }}
          />
        </div>
      </div>

      {/* Model Weights */}
      <div>
        <h3 className="text-sm font-semibold text-gray-400 mb-3">Model Weights</h3>
        <div className="space-y-2">
          {Object.entries(modelWeights).map(([model, weight]: [string, any]) => (
            <ModelWeight 
              key={model}
              name={formatModelName(model)}
              weight={weight}
            />
          ))}
        </div>
      </div>

      {/* Brain Status */}
      <div className="mt-6 pt-4 border-t border-gray-800">
        <div className="grid grid-cols-2 gap-3 text-center">
          <StatusCard
            icon={<Zap className="w-4 h-4" />}
            label="Decisions"
            value={data?.total_decisions || 0}
          />
          <StatusCard
            icon={<Activity className="w-4 h-4" />}
            label="Avg Speed"
            value={`${data?.avg_decision_time || 0}ms`}
          />
        </div>
      </div>
    </div>
  )
}

function ModelWeight({ name, weight }: { name: string; weight: number }) {
  const percentage = (weight * 100).toFixed(0)
  
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-400">{name}</span>
        <span className="text-gray-300">{percentage}%</span>
      </div>
      <div className="w-full bg-gray-800 rounded-full h-2">
        <div
          className="bg-purple-500 h-2 rounded-full transition-all"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

function StatusCard({ icon, label, value }: any) {
  return (
    <div className="bg-gray-800/50 rounded-lg p-3">
      <div className="flex items-center justify-center gap-1 text-gray-400 mb-1">
        {icon}
        <span className="text-xs">{label}</span>
      </div>
      <div className="text-lg font-bold">{value}</div>
    </div>
  )
}

function formatModelName(name: string): string {
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
