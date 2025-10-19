'use client'

export default function Sidebar({ activeTab, setActiveTab }: any) {
  const menuItems = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard', badge: null },
    { id: 'bots', icon: '🤖', label: 'Bots', badge: '6' },
    { id: 'positions', icon: '💼', label: 'Positions', badge: '3' },
    { id: 'history', icon: '📜', label: 'Trade History', badge: null },
    { id: 'analytics', icon: '📈', label: 'Analytics', badge: null },
    { id: 'market', icon: '🌐', label: 'Market Watch', badge: 'LIVE' },
    { id: 'strategies', icon: '🎯', label: 'Strategy Builder', badge: 'NEW' },
    { id: 'alerts', icon: '🔔', label: 'Alerts', badge: '5' },
    { id: 'logs', icon: '📋', label: 'System Logs', badge: null },
    { id: 'settings', icon: '⚙️', label: 'Settings', badge: null },
  ]

  return (
    <div className="w-72 bg-slate-800 border-r border-slate-700 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-lg flex items-center justify-center">
            <span className="text-2xl">🚀</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
              TPS19
            </h1>
            <p className="text-xs text-gray-400">v19.0 Trading Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4">
        <div className="space-y-1">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-all ${
                activeTab === item.id
                  ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-blue-500/20'
                  : 'text-gray-300 hover:bg-slate-700 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-xl">{item.icon}</span>
                <span className="font-medium">{item.label}</span>
              </div>
              {item.badge && (
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  activeTab === item.id
                    ? 'bg-white/20 text-white'
                    : 'bg-slate-700 text-gray-300'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          ))}
        </div>
      </nav>

      {/* System Status */}
      <div className="p-4 border-t border-slate-700">
        <div className="bg-slate-900 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">System Status</span>
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-sm font-semibold text-green-400">Online</span>
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">Trading Mode</span>
            <span className="text-sm font-semibold text-yellow-400">Monitor</span>
          </div>
          
          <div className="pt-2 border-t border-slate-700">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>CPU</span>
              <span>24%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: '24%' }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>Memory</span>
              <span>48%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
              <div className="h-full bg-cyan-500 rounded-full" style={{ width: '48%' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
