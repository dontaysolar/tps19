'use client'

import { useState, useEffect } from 'react'

export default function Header() {
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-success rounded-full animate-pulse"></div>
            <span className="text-sm font-medium">System Online</span>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="text-sm text-gray-400">
            {time.toLocaleTimeString()}
          </div>
          <button className="text-gray-400 hover:text-white">
            🔔
          </button>
        </div>
      </div>
    </header>
  )
}
