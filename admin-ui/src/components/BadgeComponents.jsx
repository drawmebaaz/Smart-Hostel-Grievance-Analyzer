/**
 * Status Badge Component
 * Consistent status display across the application
 * Handles multiple status types with appropriate colors and icons
 */

import React from 'react'
import {
  AlertTriangle,
  Clock,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  Minus,
  Zap,
  Shield
} from 'lucide-react'
import { HEALTH_COLORS, SEVERITY_COLORS, SLA_COLORS, PRIORITY_COLORS } from '../utils/colorMaps'
import { formatStatusText } from '../utils/formatters'

/**
 * Generic Badge Component
 */
export function Badge({ children, variant = 'default', className = '', tooltip = null }) {
  const variants = {
    default: 'bg-slate-700/50 text-slate-200 border-slate-500/50 hover:bg-slate-700/70 hover:border-slate-500/70',
    success: 'bg-emerald-700/50 text-emerald-200 border-emerald-500/50 hover:bg-emerald-700/70 hover:border-emerald-500/70',
    warning: 'bg-amber-700/50 text-amber-200 border-amber-500/50 hover:bg-amber-700/70 hover:border-amber-500/70',
    danger: 'bg-red-700/50 text-red-200 border-red-500/50 hover:bg-red-700/70 hover:border-red-500/70',
    info: 'bg-cyan-700/50 text-cyan-200 border-cyan-500/50 hover:bg-cyan-700/70 hover:border-cyan-500/70'
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold backdrop-blur-sm border transition-all duration-200 ${variants[variant]} ${className}`}
      title={tooltip}
    >
      {children}
    </span>
  )
}

/**
 * Health Status Badge
 * Shows issue health with appropriate color and icon
 */
export function HealthBadge({ health, showLabel = true, size = 'sm' }) {
  if (!health) return <Badge>Unknown</Badge>

  const colorMap = HEALTH_COLORS[health.label] || HEALTH_COLORS.MONITOR
  const sizeClass = size === 'lg' ? 'px-3 py-1.5 text-sm' : 'px-2.5 py-1 text-xs'

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-semibold backdrop-blur-sm border transition-all duration-200 ${colorMap.bg} ${colorMap.text} ${colorMap.border} border ${sizeClass}`}
      title={`Health: ${health.label}`}
    >
      <span className="w-2 h-2 rounded-full bg-current opacity-75" />
      {showLabel && health.label}
    </span>
  )
}

/**
 * Severity Badge
 * Shows issue severity with color coding
 */
export function SeverityBadge({ severity, showLabel = true, size = 'sm' }) {
  if (!severity) return <Badge>Unknown</Badge>

  const label = severity.label || severity
  const colorMap = SEVERITY_COLORS[label] || SEVERITY_COLORS['SEV-4']
  const sizeClass = size === 'lg' ? 'px-3 py-1.5 text-sm' : 'px-2.5 py-1 text-xs'

  const iconMap = {
    'SEV-1': <AlertTriangle className="w-3.5 h-3.5" />,
    'SEV-2': <AlertTriangle className="w-3.5 h-3.5" />,
    'SEV-3': <AlertCircle className="w-3.5 h-3.5" />,
    'SEV-4': <Minus className="w-3.5 h-3.5" />
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-semibold backdrop-blur-sm border transition-all duration-200 ${colorMap.bg} ${colorMap.text} ${colorMap.border} border ${sizeClass}`}
      title={`Severity: ${label}`}
    >
      {iconMap[label]}
      {showLabel && label}
    </span>
  )
}

/**
 * Priority Badge
 * Shows issue priority level
 */
export function PriorityBadge({ priority, showLabel = true, size = 'sm' }) {
  if (!priority) return <Badge>Unknown</Badge>

  const label = priority.label || priority
  const colorMap = PRIORITY_COLORS[label] || PRIORITY_COLORS.LOW
  const sizeClass = size === 'lg' ? 'px-3 py-1.5 text-sm' : 'px-2.5 py-1 text-xs'

  const iconMap = {
    CRITICAL: <Zap className="w-3.5 h-3.5" />,
    HIGH: <AlertTriangle className="w-3.5 h-3.5" />,
    MEDIUM: <AlertCircle className="w-3.5 h-3.5" />,
    LOW: <Minus className="w-3.5 h-3.5" />
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-semibold backdrop-blur-sm border transition-all duration-200 ${colorMap.bg} ${colorMap.text} ${colorMap.border} border ${sizeClass}`}
      title={`Priority: ${label}`}
    >
      {iconMap[label]}
      {showLabel && label}
    </span>
  )
}

/**
 * SLA Status Badge
 * Shows SLA risk level with indicator
 */
export function SLABadge({ sla, showLabel = true, size = 'sm' }) {
  if (!sla) return <Badge>Unknown</Badge>

  const risk = sla.risk || 'OK'
  const colorMap = SLA_COLORS[risk] || SLA_COLORS.OK
  const sizeClass = size === 'lg' ? 'px-3 py-1.5 text-sm' : 'px-2.5 py-1 text-xs'

  const iconMap = {
    OK: <CheckCircle2 className="w-3.5 h-3.5" />,
    WARNING: <AlertTriangle className="w-3.5 h-3.5" />,
    BREACHING: <AlertCircle className="w-3.5 h-3.5" />
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-semibold backdrop-blur-sm border transition-all duration-200 ${colorMap.bg} ${colorMap.text} ${colorMap.border} border ${sizeClass}`}
      title={`SLA: ${risk}`}
    >
      {iconMap[risk]}
      {showLabel && risk}
    </span>
  )
}

/**
 * Status Badge
 * Generic status display (OPEN, RESOLVED, IN_PROGRESS, etc.)
 */
export function StatusBadge({ status, showLabel = true, size = 'sm' }) {
  if (!status) return <Badge>Unknown</Badge>

  const statusStr = String(status).toUpperCase().replace(/_/g, ' ')
  const sizeClass = size === 'lg' ? 'px-3 py-1.5 text-sm' : 'px-2.5 py-1 text-xs'

  const variantMap = {
    OPEN: 'default',
    'IN PROGRESS': 'info',
    RESOLVED: 'success',
    CLOSED: 'success',
    PENDING: 'warning',
    DUPLICATE: 'warning',
    INVALID: 'danger'
  }

  const variant = variantMap[statusStr] || 'default'

  return (
    <Badge variant={variant} className={sizeClass}>
      {statusStr}
    </Badge>
  )
}

/**
 * Trend Badge
 * Shows trend with icon and value
 */
export function TrendBadge({ value, label = 'from yesterday' }) {
  if (!value || value === 0) {
    return (
      <div className="flex items-center gap-1 text-xs">
        <Minus className="w-3 h-3 text-white/40" />
        <span className="text-white/60">{label}</span>
      </div>
    )
  }

  const isPositive = value > 0
  const Icon = isPositive ? TrendingUp : TrendingDown
  const color = isPositive ? 'text-red-400' : 'text-green-400'

  return (
    <div className="flex items-center gap-1 text-xs">
      <Icon className={`w-3 h-3 ${color}`} />
      <span className={`font-medium ${color}`}>{Math.abs(value)}</span>
      <span className="text-white/50">{label}</span>
    </div>
  )
}

/**
 * Category Badge
 * Shows issue category
 */
export function CategoryBadge({ category, size = 'sm' }) {
  if (!category) return <Badge>Unknown</Badge>

  const sizeClass = size === 'lg' ? 'px-3 py-1.5 text-sm' : 'px-2.5 py-1 text-xs'

  const categoryColors = {
    Water: 'bg-blue-100/20 text-blue-300 border-blue-400/30',
    Electricity: 'bg-yellow-100/20 text-yellow-300 border-yellow-400/30',
    Internet: 'bg-purple-100/20 text-purple-300 border-purple-400/30',
    Hygiene: 'bg-pink-100/20 text-pink-300 border-pink-400/30',
    Mess: 'bg-orange-100/20 text-orange-300 border-orange-400/30',
    Admin: 'bg-gray-100/20 text-gray-300 border-gray-400/30',
    Other: 'bg-cyan-100/20 text-cyan-300 border-cyan-400/30'
  }

  const colors = categoryColors[category] || categoryColors.Other

  return (
    <span className={`inline-flex items-center rounded-full font-semibold backdrop-blur-sm border transition-all duration-200 ${colors} ${sizeClass}`}>
      {category}
    </span>
  )
}

/**
 * Duplicate Badge
 * Indicates duplicate complaint
 */
export function DuplicateBadge() {
  return (
    <Badge variant="warning" className="text-xs">
      Duplicate
    </Badge>
  )
}

export default {
  Badge,
  HealthBadge,
  SeverityBadge,
  PriorityBadge,
  SLABadge,
  StatusBadge,
  TrendBadge,
  CategoryBadge,
  DuplicateBadge
}
