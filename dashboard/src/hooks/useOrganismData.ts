import { useEffect, useState, useCallback } from 'react'
import io, { Socket } from 'socket.io-client'

interface OrganismData {
  // Health metrics
  health_score: number
  consciousness: number
  status: string
  
  // Trading metrics
  total_trades: number
  winning_trades: number
  win_rate: number
  total_pnl: number
  daily_pnl: number
  
  // Positions
  positions: any[]
  active_positions: number
  
  // Performance
  sharpe_ratio: number
  max_drawdown: number
  current_drawdown: number
  
  // AI metrics
  ml_confidence: number
  brain_signals: any[]
  model_weights: any
  
  // System
  uptime: string
  total_decisions: number
  trades_blocked: number
  avg_decision_time: number
  
  // Strategies
  strategies: any[]
}

export function useOrganismData() {
  const [data, setData] = useState<OrganismData | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [socket, setSocket] = useState<Socket | null>(null)

  // Fetch initial data
  const fetchData = useCallback(async () => {
    try {
      const response = await fetch('/api/organism/vitals')
      if (!response.ok) {
        throw new Error('Failed to fetch organism data')
      }
      const json = await response.json()
      setData(json)
      setError(null)
    } catch (err) {
      console.error('Fetch error:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
      
      // Fallback to mock data if API not available
      setData(getMockData())
    }
  }, [])

  // Setup WebSocket connection
  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8765'
    
    const newSocket = io(wsUrl, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10,
    })

    newSocket.on('connect', () => {
      console.log('WebSocket connected')
      setIsConnected(true)
      setError(null)
    })

    newSocket.on('disconnect', () => {
      console.log('WebSocket disconnected')
      setIsConnected(false)
    })

    newSocket.on('organism_update', (update: Partial<OrganismData>) => {
      setData(prev => prev ? { ...prev, ...update } : null)
    })

    newSocket.on('error', (err: any) => {
      console.error('WebSocket error:', err)
      setError('WebSocket connection error')
    })

    setSocket(newSocket)

    // Initial data fetch
    fetchData()
    
    // Fallback polling if WebSocket fails
    const pollInterval = setInterval(() => {
      if (!isConnected) {
        fetchData()
      }
    }, 5000)

    return () => {
      newSocket.close()
      clearInterval(pollInterval)
    }
  }, [fetchData, isConnected])

  return { data, isConnected, error, refresh: fetchData }
}

// Mock data for development
function getMockData(): OrganismData {
  return {
    health_score: 95,
    consciousness: 1.0,
    status: 'ALIVE',
    total_trades: 127,
    winning_trades: 76,
    win_rate: 0.598,
    total_pnl: 89.50,
    daily_pnl: 12.30,
    positions: [
      { symbol: 'BTC/USDT', side: 'LONG', size: 0.05, entry_price: 43250, current_price: 43580, pnl: 16.50 },
      { symbol: 'ETH/USDT', side: 'LONG', size: 0.8, entry_price: 2340, current_price: 2365, pnl: 20.00 },
    ],
    active_positions: 2,
    sharpe_ratio: 1.85,
    max_drawdown: 0.08,
    current_drawdown: 0.02,
    ml_confidence: 0.78,
    brain_signals: [],
    model_weights: {
      ml_prediction: 0.35,
      technical_signals: 0.25,
      market_regime: 0.20,
      volume_analysis: 0.10,
      momentum: 0.10,
    },
    uptime: '12h 34m',
    total_decisions: 1847,
    trades_blocked: 34,
    avg_decision_time: 23,
    strategies: [
      { name: 'Trend Following', trades: 45, win_rate: 0.62, pnl: 34.20 },
      { name: 'Mean Reversion', trades: 52, win_rate: 0.67, pnl: 41.80 },
      { name: 'Breakout', trades: 18, win_rate: 0.44, pnl: 8.30 },
      { name: 'Momentum', trades: 12, win_rate: 0.58, pnl: 5.20 },
    ],
  }
}
