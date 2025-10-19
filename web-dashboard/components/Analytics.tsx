'use client'

export default function Analytics() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Performance Analytics</h1>
        <p className="text-gray-400 mt-1">Deep insights into your trading performance</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard title="Sharpe Ratio" value="2.34" status="excellent" description="Risk-adjusted returns" />
        <MetricCard title="Max Drawdown" value="-8.5%" status="warning" description="Peak to trough decline" />
        <MetricCard title="Profit Factor" value="3.2" status="excellent" description="Gross profit / Gross loss" />
        <MetricCard title="Sortino Ratio" value="3.1" status="excellent" description="Downside risk adjusted" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Equity Curve */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-xl font-semibold text-white mb-4">Equity Curve</h2>
          <div className="h-64 flex items-center justify-center bg-slate-900 rounded-lg">
            <div className="text-center">
              <p className="text-gray-500 text-lg mb-2">📈</p>
              <p className="text-sm text-gray-600">Portfolio value over time</p>
            </div>
          </div>
        </div>

        {/* Drawdown Chart */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-xl font-semibold text-white mb-4">Drawdown Analysis</h2>
          <div className="h-64 flex items-center justify-center bg-slate-900 rounded-lg">
            <div className="text-center">
              <p className="text-gray-500 text-lg mb-2">📉</p>
              <p className="text-sm text-gray-600">Underwater equity</p>
            </div>
          </div>
        </div>
      </div>

      {/* Strategy Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-xl font-semibold text-white mb-4">Strategy Performance</h2>
          <div className="space-y-4">
            <StrategyBar strategy="Trend Following" winRate={72} trades={45} profit="+$2,456.78" profitPct={12.5} />
            <StrategyBar strategy="Mean Reversion" winRate={68} trades={32} profit="+$1,642.30" profitPct={8.3} />
            <StrategyBar strategy="Breakout" winRate={55} trades={18} profit="+$1,028.50" profitPct={5.2} />
            <StrategyBar strategy="Wyckoff" winRate={75} trades={28} profit="+$3,102.45" profitPct={15.7} />
            <StrategyBar strategy="Ichimoku" winRate={64} trades={22} profit="+$1,365.90" profitPct={6.9} />
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-xl font-semibold text-white mb-4">Risk Metrics</h2>
          <div className="space-y-4">
            <RiskMetric label="Position Size" current="8.5%" limit="10%" status="good" />
            <RiskMetric label="Daily Loss" current="1.2%" limit="5%" status="good" />
            <RiskMetric label="Max Drawdown" current="8.5%" limit="20%" status="good" />
            <RiskMetric label="Leverage Used" current="1.0x" limit="3.0x" status="good" />
            <RiskMetric label="Portfolio Heat" current="24%" limit="50%" status="good" />
          </div>
        </div>
      </div>

      {/* Trade Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-xl font-semibold text-white mb-4">Win/Loss Distribution</h2>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-400">Wins (105)</span>
                <span className="text-green-400">67.3%</span>
              </div>
              <div className="w-full h-3 bg-slate-700 rounded-full overflow-hidden">
                <div className="h-full bg-green-500 rounded-full" style={{ width: '67.3%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-400">Losses (51)</span>
                <span className="text-red-400">32.7%</span>
              </div>
              <div className="w-full h-3 bg-slate-700 rounded-full overflow-hidden">
                <div className="h-full bg-red-500 rounded-full" style={{ width: '32.7%' }}></div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-xl font-semibold text-white mb-4">Trade Duration</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Avg Hold Time</span>
              <span className="text-white font-semibold">4.2 hours</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Shortest</span>
              <span className="text-white font-semibold">12 min</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Longest</span>
              <span className="text-white font-semibold">2.3 days</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-xl font-semibold text-white mb-4">Best/Worst</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Best Trade</span>
              <span className="text-green-400 font-semibold">+$524.30</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Worst Trade</span>
              <span className="text-red-400 font-semibold">-$186.50</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Avg Win</span>
              <span className="text-green-400 font-semibold">+$142.50</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Avg Loss</span>
              <span className="text-red-400 font-semibold">-$65.30</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function MetricCard({ title, value, status, description }: any) {
  const colors = {
    excellent: 'text-green-400',
    good: 'text-blue-400',
    warning: 'text-yellow-400',
    danger: 'text-red-400',
  }

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <p className="text-sm text-gray-400 mb-2">{title}</p>
      <p className={`text-3xl font-bold ${colors[status as keyof typeof colors]}`}>{value}</p>
      <p className="text-sm text-gray-500 mt-1">{description}</p>
    </div>
  )
}

function StrategyBar({ strategy, winRate, trades, profit, profitPct }: any) {
  return (
    <div className="p-4 bg-slate-900 rounded-lg">
      <div className="flex justify-between items-center mb-3">
        <span className="font-medium text-white">{strategy}</span>
        <span className="text-green-400 font-semibold">{profit} (+{profitPct}%)</span>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <div className="w-full bg-slate-700 rounded-full h-2.5">
            <div
              className="bg-gradient-to-r from-green-500 to-green-400 h-2.5 rounded-full"
              style={{ width: `${winRate}%` }}
            ></div>
          </div>
        </div>
        <span className="text-sm text-gray-400 whitespace-nowrap">
          {winRate}% • {trades} trades
        </span>
      </div>
    </div>
  )
}

function RiskMetric({ label, current, limit, status }: any) {
  const currentNum = parseFloat(current)
  const limitNum = parseFloat(limit)
  const percentage = (currentNum / limitNum) * 100

  const color = percentage < 50 ? 'green' : percentage < 80 ? 'yellow' : 'red'

  return (
    <div>
      <div className="flex justify-between text-sm mb-2">
        <span className="text-gray-400">{label}</span>
        <span className="text-white font-medium">
          {current} / {limit}
        </span>
      </div>
      <div className="w-full bg-slate-700 rounded-full h-2.5">
        <div
          className={`bg-${color}-500 h-2.5 rounded-full transition-all`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        ></div>
      </div>
    </div>
  )
}
