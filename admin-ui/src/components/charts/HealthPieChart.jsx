import React from 'react'
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip
} from 'recharts'
import { HEALTH_COLORS } from '../../utils/colorMaps'

export default function HealthPieChart({ data, isLoading }) {
  if (isLoading) {
    return (
      <div className="card h-80 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600"></div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="card h-80 flex items-center justify-center text-slate-400">
        No health data available
      </div>
    )
  }

  /**
   * IMPORTANT:
   * Filter out zero or negative values
   * This prevents Recharts from rendering
   * paddingAngle artifacts (ghost slices)
   */
  const chartData = Object.entries(data)
    .filter(([_, value]) => value > 0)
    .map(([key, value]) => ({
      name: key,
      value,
      color: HEALTH_COLORS[key]?.chart || '#6b7280'
    }))

  if (chartData.length === 0) {
    return (
      <div className="card h-80 flex items-center justify-center text-slate-400">
        No issues to display
      </div>
    )
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900/95 border border-cyan-500/50 rounded-lg px-3 py-2 shadow-2xl shadow-cyan-500/20">
          <p className="text-cyan-300 font-semibold text-sm">
            {payload[0].name}
          </p>
          <p className="text-white font-bold text-base">
            {payload[0].value} issues
          </p>
        </div>
      )
    }
    return null
  }

  const renderLabel = ({ name, value, x, y, cx, cy }) => {
    // Always show label for all sections, regardless of size
    // Calculate position to ensure it's visible and not overlapped
    const angle = Math.atan2(y - cy, x - cx)
    
    return (
      <text
        x={x}
        y={y}
        fill="white"
        fontSize={12}
        fontWeight="bold"
        textAnchor="middle"
        dominantBaseline="central"
        className="pointer-events-none drop-shadow-lg"
        style={{
          textShadow: '0 0 3px rgba(0,0,0,0.8)',
          filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.5))'
        }}
      >
        {name}
      </text>
    )
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-4">
        Issue Health Distribution
      </h3>

      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey="value"
            label={renderLabel}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color}
              />
            ))}
          </Pie>

          <Tooltip content={<CustomTooltip />} />

          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="circle"
            formatter={(value) => (
              <span className="text-white text-sm font-medium">
                {value} 
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
