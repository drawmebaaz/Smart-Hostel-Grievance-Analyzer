import React from 'react'
import { Activity, RefreshCw } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function Header({ lastUpdated, onRefresh, isRefreshing }) {
  return (
    <header className="
      top-0 z-50
      bg-black/50 backdrop-blur-xl backdrop-saturate-150
      border-b border-white/10
      shadow-[0_8px_30px_rgba(0,0,0,0.6)]
    ">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          
          {/* Left */}
          <div className="flex items-center gap-4">
            <div className="
              p-2.5 rounded-xl
              bg-blue-500/10
              border border-blue-500/20
              shadow-[0_0_20px_rgba(59,130,246,0.25)]
            ">
              <Activity className="w-6 h-6 text-blue-400" />
            </div>

            <div>
              <h1 className="
                text-xl sm:text-2xl
                font-semibold tracking-tight
                text-white
              ">
                Smart Grievance Admin
              </h1>

              <p className="
                text-xs sm:text-sm
                text-gray-400
              ">
                Last updated:{' '}
                {lastUpdated
                  ? formatDistanceToNow(new Date(lastUpdated), { addSuffix: true })
                  : 'Never'}
              </p>
            </div>
          </div>

          {/* Right */}
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="
              flex items-center gap-2
              px-4 py-2 rounded-lg
              text-sm font-medium
              text-gray-200
              bg-white/5
              border border-white/10
              backdrop-blur-md
              transition-all
              hover:bg-white/10 hover:border-white/20
              active:scale-95
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            <RefreshCw
              className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`}
            />
            Refresh
          </button>

        </div>
      </div>
    </header>
  )
}
