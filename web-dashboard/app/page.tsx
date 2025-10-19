'use client'

import { useState, useEffect } from 'react'
import Dashboard from '@/components/Dashboard'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'

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
          {activeTab === 'settings' && <Settings />}
        </main>
      </div>
    </div>
  )
}

function BotManagement() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Bot Management</h1>
        <button className="btn-primary">Create Bot</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <BotCard
          name="Trend Follower"
          status="running"
          profit="+12.5%"
          trades={45}
        />
        <BotCard
          name="Mean Reversion"
          status="running"
          profit="+8.3%"
          trades={32}
        />
        <BotCard
          name="Breakout Trader"
          status="paused"
          profit="+5.2%"
          trades={18}
        />
      </div>
    </div>
  )
}

function BotCard({ name, status, profit, trades }: any) {
  return (
    <div className="card">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold">{name}</h3>
        <span className={`badge-${status === 'running' ? 'success' : 'warning'}`}>
          {status}
        </span>
      </div>
      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-gray-400">Profit</span>
          <span className="text-success font-semibold">{profit}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Trades</span>
          <span>{trades}</span>
        </div>
      </div>
      <div className="mt-4 flex gap-2">
        <button className="flex-1 btn-primary text-sm">Edit</button>
        <button className="flex-1 btn-danger text-sm">Stop</button>
      </div>
    </div>
  )
}

function Positions() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Open Positions</h1>
      <div className="card">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left py-3">Symbol</th>
              <th className="text-right py-3">Amount</th>
              <th className="text-right py-3">Entry Price</th>
              <th className="text-right py-3">Current Price</th>
              <th className="text-right py-3">P&L</th>
              <th className="text-right py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            <PositionRow
              symbol="BTC/USDT"
              amount="0.125"
              entry="48,500"
              current="49,200"
              pnl="+1.44%"
            />
            <PositionRow
              symbol="ETH/USDT"
              amount="2.5"
              entry="2,850"
              current="2,920"
              pnl="+2.46%"
            />
          </tbody>
        </table>
      </div>
    </div>
  )
}

function PositionRow({ symbol, amount, entry, current, pnl }: any) {
  const isProfit = pnl.startsWith('+')
  return (
    <tr className="border-b border-slate-700/50">
      <td className="py-4">{symbol}</td>
      <td className="text-right">{amount}</td>
      <td className="text-right">${entry}</td>
      <td className="text-right">${current}</td>
      <td className={`text-right ${isProfit ? 'text-success' : 'text-danger'}`}>
        {pnl}
      </td>
      <td className="text-right">
        <button className="btn-danger text-sm">Close</button>
      </td>
    </tr>
  )
}

function TradeHistory() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Trade History</h1>
      <div className="card">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left py-3">Time</th>
              <th className="text-left py-3">Symbol</th>
              <th className="text-left py-3">Side</th>
              <th className="text-right py-3">Amount</th>
              <th className="text-right py-3">Price</th>
              <th className="text-right py-3">P&L</th>
            </tr>
          </thead>
          <tbody>
            <TradeRow
              time="2024-01-15 14:32"
              symbol="BTC/USDT"
              side="BUY"
              amount="0.125"
              price="48,500"
              pnl="+$87.50"
            />
            <TradeRow
              time="2024-01-15 13:15"
              symbol="ETH/USDT"
              side="SELL"
              amount="2.5"
              price="2,920"
              pnl="+$175.00"
            />
          </tbody>
        </table>
      </div>
    </div>
  )
}

function TradeRow({ time, symbol, side, amount, price, pnl }: any) {
  return (
    <tr className="border-b border-slate-700/50">
      <td className="py-4 text-gray-400">{time}</td>
      <td>{symbol}</td>
      <td>
        <span className={`badge-${side === 'BUY' ? 'success' : 'danger'}`}>
          {side}
        </span>
      </td>
      <td className="text-right">{amount}</td>
      <td className="text-right">${price}</td>
      <td className="text-right text-success">{pnl}</td>
    </tr>
  )
}

function Settings() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Settings</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">API Configuration</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Exchange</label>
              <select className="input w-full">
                <option>Crypto.com</option>
                <option>Binance</option>
                <option>Coinbase</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">API Key</label>
              <input type="password" className="input w-full" placeholder="Your API key" />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">API Secret</label>
              <input type="password" className="input w-full" placeholder="Your API secret" />
            </div>
            <button className="btn-primary w-full">Save Configuration</button>
          </div>
        </div>
        
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Risk Settings</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Max Position Size (%)</label>
              <input type="number" className="input w-full" defaultValue="10" />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Daily Loss Limit (%)</label>
              <input type="number" className="input w-full" defaultValue="5" />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Stop Loss (%)</label>
              <input type="number" className="input w-full" defaultValue="2" />
            </div>
            <button className="btn-primary w-full">Update Risk Settings</button>
          </div>
        </div>
      </div>
    </div>
  )
}
