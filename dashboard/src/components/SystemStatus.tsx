'use client'

import { Server, Cpu, HardDrive, Wifi } from 'lucide-react'

interface Props {
  data: any
}

export default function SystemStatus({ data }: Props) {
  const uptime = data?.uptime || '0h 0m'
  const status = data?.status || 'unknown'
  
  return (
    <div className="card">
      <div className="card-header">
        <Server className="w-6 h-6 text-primary-400" />
        <span>System Status</span>
      </div>

      {/* Status Badge */}
      <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg mb-4">
        <span className="text-gray-400">Status</span>
        <div className={`flex items-center gap-2 ${
          status === 'ALIVE' ? 'text-green-400' : 'text-red-400'
        }`}>
          <div className={`w-2 h-2 rounded-full ${
            status === 'ALIVE' ? 'bg-green-400 animate-pulse' : 'bg-red-400'
          }`} />
          <span className="font-semibold">{status}</span>
        </div>
      </div>

      {/* System Metrics */}
      <div className="space-y-3">
        <SystemMetric
          icon={<Cpu className="w-4 h-4" />}
          label="Uptime"
          value={uptime}
        />
        <SystemMetric
          icon={<Activity className="w-4 h-4" />}
          label="Health"
          value={`${data?.health_score || 0}/100`}
        />
        <SystemMetric
          icon={<HardDrive className="w-4 h-4" />}
          label="Memory"
          value="Normal"
        />
        <SystemMetric
          icon={<Wifi className="w-4 h-4" />}
          label="Connection"
          value="Stable"
        />
      </div>

      {/* Quick Actions */}
      <div className="mt-4 pt-4 border-t border-gray-800">
        <button className="w-full btn-secondary text-sm">
          View Logs
        </button>
      </div>
    </div>
  )
}

function SystemMetric({ icon, label, value }: any) {
  return (
    <div className="flex items-center justify-between text-sm">
      <div className="flex items-center gap-2 text-gray-400">
        {icon}
        <span>{label}</span>
      </div>
      <span className="font-medium">{value}</span>
    </div>
  )
}
