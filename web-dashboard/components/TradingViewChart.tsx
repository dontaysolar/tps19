'use client'

import { useEffect, useRef } from 'react'

interface TradingViewChartProps {
  symbol: string
  interval?: string
  theme?: 'light' | 'dark'
  height?: number
}

export default function TradingViewChart({ 
  symbol = 'BTCUSDT', 
  interval = '15',
  theme = 'dark',
  height = 500 
}: TradingViewChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    // Load TradingView widget script
    const script = document.createElement('script')
    script.src = 'https://s3.tradingview.com/tv.js'
    script.async = true
    script.onload = () => {
      if (typeof (window as any).TradingView !== 'undefined' && containerRef.current) {
        // Clear previous widget
        containerRef.current.innerHTML = ''
        
        // Create new widget
        new (window as any).TradingView.widget({
          autosize: true,
          symbol: `CRYPTO:${symbol}`,
          interval: interval,
          timezone: 'Etc/UTC',
          theme: theme,
          style: '1',
          locale: 'en',
          toolbar_bg: '#0f172a',
          enable_publishing: false,
          hide_side_toolbar: false,
          allow_symbol_change: true,
          container_id: containerRef.current.id,
          studies: [
            'RSI@tv-basicstudies',
            'MACD@tv-basicstudies',
            'Volume@tv-basicstudies'
          ],
          disabled_features: [
            'use_localstorage_for_settings',
            'header_symbol_search',
            'header_compare'
          ],
          enabled_features: [
            'study_templates'
          ],
          overrides: {
            'mainSeriesProperties.candleStyle.upColor': '#22c55e',
            'mainSeriesProperties.candleStyle.downColor': '#ef4444',
            'mainSeriesProperties.candleStyle.borderUpColor': '#22c55e',
            'mainSeriesProperties.candleStyle.borderDownColor': '#ef4444',
            'mainSeriesProperties.candleStyle.wickUpColor': '#22c55e',
            'mainSeriesProperties.candleStyle.wickDownColor': '#ef4444',
          }
        })
      }
    }
    
    document.head.appendChild(script)
    
    return () => {
      if (document.head.contains(script)) {
        document.head.removeChild(script)
      }
    }
  }, [symbol, interval, theme])
  
  return (
    <div className="w-full" style={{ height: `${height}px` }}>
      <div 
        id={`tradingview_${symbol}`}
        ref={containerRef}
        className="w-full h-full rounded-lg overflow-hidden"
      />
    </div>
  )
}
