// components/cards/StatCard.jsx
import React from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

export default function StatCard({ title, value, trend, variant = 'normal', icon: Icon }) {
  const variantStyles = {
    normal: 'from-cyan-600/25 to-blue-600/25 border-cyan-500/50 hover:border-cyan-500/70',
    warning: 'from-amber-600/25 to-orange-600/25 border-amber-500/50 hover:border-amber-500/70',
    danger: 'from-red-600/25 to-red-600/25 border-red-500/50 hover:border-red-500/70',
  }

  const iconBgVariant = {
    normal: 'bg-cyan-600/40 hover:bg-cyan-600/60',
    warning: 'bg-amber-600/40 hover:bg-amber-600/60',
    danger: 'bg-red-600/40 hover:bg-red-600/60',
  }

  const iconColorVariant = {
    normal: 'text-cyan-300',
    warning: 'text-amber-300',
    danger: 'text-red-300',
  }

  const getTrendIcon = () => {
    if (trend > 0) return <TrendingUp className="w-4 h-4 text-red-400" />
    if (trend < 0) return <TrendingDown className="w-4 h-4 text-emerald-400" />
    return <Minus className="w-4 h-4 text-white/40" />
  }

  const getTrendColor = () => {
    if (trend > 0) return 'text-red-400'
    if (trend < 0) return 'text-emerald-400'
    return 'text-white/60'
  }

  const formatTrendValue = (value) => {
    if (value > 0) return `+${value}`
    if (value < 0) return `${value}`
    return '0'
  }

  return (
    <div className={`stat-card bg-gradient-to-br ${variantStyles[variant]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-cyan-300/80">{title}</p>
          <p className="text-2xl sm:text-3xl font-bold text-white mt-2">{value}</p>
          
          {trend !== undefined && trend !== null && (
            <div className="flex items-center gap-1 mt-2">
              {getTrendIcon()}
              <span className={`text-sm font-medium ${getTrendColor()}`}>
                {formatTrendValue(trend)}
              </span>
              <span className="text-xs text-white/50">from yesterday</span>
            </div>
          )}
        </div>
        
        {Icon && (
          <div className={`p-3 rounded-lg ${iconBgVariant[variant]}`}>
            <Icon className={`w-8 h-8 ${iconColorVariant[variant]}`} />
          </div>
        )}
      </div>
    </div>
  )
}