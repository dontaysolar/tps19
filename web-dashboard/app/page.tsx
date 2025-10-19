'use client'

import { useState, useEffect } from 'react'
import Dashboard from '@/components/Dashboard'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import BotManagement from '@/components/BotManagement'
import Positions from '@/components/Positions'
import TradeHistory from '@/components/TradeHistory'
import Analytics from '@/components/Analytics'
import Settings from '@/components/Settings'
import MarketWatch from '@/components/MarketWatch'
import Alerts from '@/components/Alerts'
import Logs from '@/components/Logs'
import StrategyBuilder from '@/components/StrategyBuilder'

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard')

  return (
    <div className="flex h-screen bg-slate-900">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-slate-900 p-6">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'bots' && <BotManagement />}
          {activeTab === 'positions' && <Positions />}
          {activeTab === 'history' && <TradeHistory />}
          {activeTab === 'analytics' && <Analytics />}
          {activeTab === 'market' && <MarketWatch />}
          {activeTab === 'strategies' && <StrategyBuilder />}
          {activeTab === 'alerts' && <Alerts />}
          {activeTab === 'logs' && <Logs />}
          {activeTab === 'settings' && <Settings />}
        </main>
      </div>
    </div>
  )
}
