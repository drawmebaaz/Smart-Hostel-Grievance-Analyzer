import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Cell } from 'recharts'
import { SEVERITY_COLORS } from '../../utils/colorMaps'

export default function SeverityBarChart({ data, isLoading }) {
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
        No severity data available
      </div>
    )
  }

  const chartData = Object.entries(data).map(([key, value]) => ({
    name: key,
    count: value,
    fill: SEVERITY_COLORS[key]?.chart || '#6b7280'
  }))

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900/95 border border-orange-500/50 rounded-lg px-3 py-2 shadow-2xl shadow-orange-500/20">
          <p className="text-orange-300 font-semibold text-sm">{payload[0].payload.name}</p>
          <p className="text-white font-bold text-base">{payload[0].value} issues</p>
        </div>
      )
    }
    return null
  }

  const CustomXAxisTick = (props) => {
    const { x, y, payload } = props
    return (
      <text
        x={x}
        y={y}
        textAnchor="middle"
        dominantBaseline="hanging"
        style={{ fill: '#ffffff', fontSize: '14px', fontWeight: 500 }}
      >
        {payload.value}
      </text>
    )
  }

  const CustomYAxisTick = (props) => {
    const { x, y, payload } = props
    return (
      <text
        x={x}
        y={y}
        textAnchor="end"
        dominantBaseline="middle"
        style={{ fill: '#ffffff', fontSize: '12px', fontWeight: 500 }}
      >
        {payload.value}
      </text>
    )
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-4">Severity Distribution</h3>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart 
          data={chartData}
          margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="rgba(148, 163, 184, 0.1)"
            vertical={false}
          />
          <XAxis 
            dataKey="name" 
            tick={<CustomXAxisTick />}
            axisLine={{ stroke: 'rgba(148, 163, 184, 0.2)' }}
            tickLine={{ stroke: 'rgba(0, 75, 180, 0.2)' }}
          />
          <YAxis 
            tick={<CustomYAxisTick />}
            axisLine={{ stroke: 'rgba(148, 163, 184, 0.2)' }}
            tickLine={{ stroke: 'rgba(148, 163, 184, 0.2)' }}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(34, 197, 94, 0.1)', radius: [8, 8, 0, 0] }} />
          <Bar 
            dataKey="count" 
            radius={[12, 12, 4, 4]}
            isAnimationActive={true}
            animationDuration={800}
          >
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.fill}
                className="hover:filter hover:brightness-125 transition-all duration-200"
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}