'use client'

import { useState, useEffect } from 'react'

interface LivePriceCardProps {
  symbol: string
}

export default function LivePriceCard({ symbol }: LivePriceCardProps) {
  const [price, setPrice] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch initial price
    fetchPrice()
    
    // Update every 2 seconds
    const interval = setInterval(fetchPrice, 2000)
    
    return () => clearInterval(interval)
  }, [symbol])

  const fetchPrice = async () => {
    try {
      // In production, this would connect to your WebSocket API
      // For now, fetch from API
      const response = await fetch(`http://localhost:8000/api/price/${symbol}`)
      if (response.ok) {
        const data = await response.json()
        setPrice(data)
      }
      setLoading(false)
    } catch (error) {
      console.error('Error fetching price:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 animate-pulse">
        <div className="h-6 bg-slate-700 rounded w-24 mb-2"></div>
        <div className="h-8 bg-slate-700 rounded w-32"></div>
      </div>
    )
  }

  const changePercent = price?.change24h || 0
  const isPositive = changePercent >= 0

  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 hover:border-blue-500/50 transition-all">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm font-medium">{symbol}</span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          <span className="text-xs text-gray-500">LIVE</span>
        </span>
      </div>
      
      <div className="flex items-baseline gap-3">
        <span className="text-2xl font-bold text-white">
          ${price?.last?.toLocaleString() || '0.00'}
        </span>
        <span className={`text-sm font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
          {isPositive ? '+' : ''}{changePercent.toFixed(2)}%
        </span>
      </div>
      
      <div className="mt-3 pt-3 border-t border-slate-700 grid grid-cols-2 gap-2 text-xs">
        <div>
          <span className="text-gray-500">24h High</span>
          <p className="text-white font-medium">${price?.high24h?.toLocaleString() || '-'}</p>
        </div>
        <div>
          <span className="text-gray-500">24h Low</span>
          <p className="text-white font-medium">${price?.low24h?.toLocaleString() || '-'}</p>
        </div>
      </div>
    </div>
  )
}
