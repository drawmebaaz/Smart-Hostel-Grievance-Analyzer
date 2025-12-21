/**
 * Loading Skeleton Components
 * Provides visual feedback during data loading
 * Improves perceived performance and UX
 */

import React from 'react'

/**
 * Generic skeleton loader with pulse animation
 * @param {string} className - Additional CSS classes
 * @param {number} count - Number of skeleton lines to show
 */
export function SkeletonLoader({ className = '', count = 3 }) {
  return (
    <div className={`space-y-3 ${className}`}>
      {[...Array(count)].map((_, i) => (
        <div
          key={i}
          className="h-4 bg-white/10 rounded-lg animate-pulse"
        />
      ))}
    </div>
  )
}

/**
 * Card skeleton - mimics StatCard layout
 */
export function CardSkeleton() {
  return (
    <div className="stat-card">
      <div className="space-y-4">
        <div className="h-4 bg-white/10 rounded-lg w-1/3 animate-pulse" />
        <div className="h-10 bg-white/10 rounded-lg w-1/2 animate-pulse" />
        <div className="h-3 bg-white/10 rounded-lg w-1/4 animate-pulse" />
      </div>
    </div>
  )
}

/**
 * Chart skeleton - mimics chart container
 */
export function ChartSkeleton() {
  return (
    <div className="card-premium">
      <div className="space-y-4">
        <div className="h-6 bg-white/10 rounded-lg w-1/3 animate-pulse" />
        <div className="flex items-end justify-around gap-4 h-64">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="flex-1 bg-white/10 rounded-lg animate-pulse"
              style={{
                height: `${Math.random() * 100 + 30}%`
              }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

/**
 * Table skeleton - mimics table rows
 */
export function TableSkeleton({ rows = 5 }) {
  return (
    <div className="card overflow-hidden p-0">
      <div className="px-6 py-4 border-b border-white/20">
        <div className="h-6 bg-white/10 rounded-lg w-1/4 animate-pulse" />
      </div>
      <div className="divide-y divide-white/10">
        {[...Array(rows)].map((_, i) => (
          <div key={i} className="px-6 py-4">
            <div className="space-y-3">
              <div className="h-4 bg-white/10 rounded-lg w-3/4 animate-pulse" />
              <div className="flex gap-4">
                <div className="h-3 bg-white/10 rounded-lg w-1/4 animate-pulse" />
                <div className="h-3 bg-white/10 rounded-lg w-1/5 animate-pulse" />
                <div className="h-3 bg-white/10 rounded-lg w-1/6 animate-pulse" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

/**
 * Enhanced table skeleton with staggered animation and customizable columns
 */
export function TableSkeletonEnhanced({ rows = 5, columns = 7 }) {
  return (
    <div className="card-premium overflow-hidden p-0">
      {/* Header skeleton */}
      <div className="px-6 py-4 border-b border-white/20 bg-white/5">
        <div className="h-6 bg-white/10 rounded-lg w-1/4 animate-pulse" />
      </div>
      
      {/* Rows skeleton */}
      <div className="divide-y divide-white/10">
        {[...Array(rows)].map((_, rowIndex) => (
          <div key={rowIndex} className="px-6 py-4">
            <div className="flex gap-4">
              {[...Array(columns)].map((_, colIndex) => (
                <div
                  key={colIndex}
                  className="h-4 bg-white/10 rounded-lg flex-1 animate-pulse"
                  style={{
                    animationDelay: `${rowIndex * 50 + colIndex * 10}ms`
                  }}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

/**
 * Stat cards grid skeleton
 */
export function StatCardsGridSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {[...Array(4)].map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  )
}

/**
 * Dashboard full page skeleton
 */
export function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header skeleton */}
        <div className="mb-8">
          <div className="h-8 bg-white/10 rounded-lg w-1/4 animate-pulse mb-2" />
          <div className="h-4 bg-white/10 rounded-lg w-1/3 animate-pulse" />
        </div>

        {/* Stats grid */}
        <div className="mb-8">
          <StatCardsGridSkeleton />
        </div>

        {/* Charts row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>

        {/* Table */}
        <TableSkeleton rows={8} />
      </div>
    </div>
  )
}

/**
 * Issue detail page skeleton
 */
export function IssueDetailSkeleton() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-white/10 backdrop-blur-md border-b border-white/20 p-4 mb-8">
        <div className="max-w-7xl mx-auto">
          <div className="h-8 bg-white/10 rounded-lg w-1/3 animate-pulse mb-4" />
          <div className="h-6 bg-white/10 rounded-lg w-1/2 animate-pulse" />
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column */}
          <div className="lg:col-span-2 space-y-6">
            <div className="card-premium">
              <SkeletonLoader count={8} />
            </div>
            <div className="card-premium">
              <SkeletonLoader count={6} />
            </div>
          </div>

          {/* Right sidebar */}
          <div className="space-y-6">
            <div className="card-premium">
              <SkeletonLoader count={4} />
            </div>
            <div className="card-premium">
              <SkeletonLoader count={3} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * Enhanced dashboard with premium table skeleton
 */
export function DashboardSkeletonEnhanced() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header skeleton */}
        <div className="mb-8">
          <div className="h-8 bg-white/10 rounded-lg w-1/4 animate-pulse mb-2" />
          <div className="h-4 bg-white/10 rounded-lg w-1/3 animate-pulse" />
        </div>

        {/* Stats grid */}
        <div className="mb-8">
          <StatCardsGridSkeleton />
        </div>

        {/* Charts row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>

        {/* Enhanced Table */}
        <TableSkeletonEnhanced rows={8} columns={6} />
      </div>
    </div>
  )
}

export default {
  SkeletonLoader,
  CardSkeleton,
  ChartSkeleton,
  TableSkeleton,
  TableSkeletonEnhanced,
  StatCardsGridSkeleton,
  DashboardSkeleton,
  DashboardSkeletonEnhanced,
  IssueDetailSkeleton
}