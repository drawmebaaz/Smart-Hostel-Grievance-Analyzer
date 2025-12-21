// pages/Dashboard.jsx - Fixed error handling

import React, { useState, useEffect } from 'react'
import { AlertCircle, Activity, Clock, MessageSquare, RefreshCw, TrendingUp, TrendingDown } from 'lucide-react'
import Header from '../components/layout/Header'
import StatCard from '../components/cards/StatCard'
import HealthPieChart from '../components/charts/HealthPieChart'
import SeverityBarChart from '../components/charts/SeverityBarChart'
import IssueTable from '../components/tables/IssueTable'
import IssueTableFilters from '../components/filters/ExcelStyleFilters'
import ResolvedIssuesSection from '../components/cards/ResolvedIssuesSection'
import { StatCardsGridSkeleton, ChartSkeleton, TableSkeleton } from '../components/SkeletonLoaders'
import { dashboardApi } from '../api/dashboardApi'

// Enhanced Table Skeleton Component
const TableSkeletonEnhanced = ({ rows = 8, columns = 7 }) => {
  return (
    <div className="card-premium animate-pulse">
      {/* Table header skeleton */}
      <div className="px-4 sm:px-6 py-4 border-b border-white/10">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="h-6 bg-white/10 rounded w-48"></div>
          <div className="flex flex-wrap gap-2">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-8 bg-white/10 rounded-lg w-24"></div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Table body skeleton */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-white/10">
          <thead>
            <tr>
              {[...Array(columns)].map((_, i) => (
                <th key={i} className="px-4 sm:px-6 py-3">
                  <div className="h-4 bg-white/10 rounded w-full"></div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {[...Array(rows)].map((_, rowIndex) => (
              <tr key={rowIndex}>
                {[...Array(columns)].map((_, colIndex) => (
                  <td key={colIndex} className="px-4 sm:px-6 py-4">
                    <div className={`h-3 bg-white/10 rounded ${
                      colIndex === 0 ? 'w-32' : 
                      colIndex === 1 ? 'w-24' :
                      colIndex === 2 ? 'w-20' :
                      colIndex === 3 ? 'w-16' :
                      'w-28'
                    }`}></div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Table footer skeleton */}
      <div className="px-4 sm:px-6 py-4 border-t border-white/10">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="h-4 bg-white/10 rounded w-40"></div>
          <div className="flex gap-2">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-8 bg-white/10 rounded-lg w-10"></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState({
    health: null,
    issues: null,
    slaTimers: null,
    trends: null
  })
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [error, setError] = useState(null)
  const [tableFilters, setTableFilters] = useState({})

  // Summary stats state
  const [summaryStats, setSummaryStats] = useState({
    active_issues: 0,
    critical_issues: 0,
    sla_risk_issues: 0,
    complaints_today: 0,
    trend: {
      critical_change: 0,
      complaints_change: 0
    }
  })

  const fetchDashboardData = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setIsRefreshing(true)
      } else {
        setIsLoading(true)
      }
      setError(null)

      // Fetch all data in parallel
      const [healthData, issuesData, slaData, trendsData] = await Promise.all([
        dashboardApi.getHealth(),
        dashboardApi.getIssues({ limit: 200 }),
        dashboardApi.getSLATimers(),
        dashboardApi.getTrends('24h')
      ])

      // Validate data before setting state
      if (!issuesData) {
        throw new Error('No issues data received from server')
      }

      setDashboardData({
        health: healthData || null,
        issues: issuesData || null,
        slaTimers: slaData || null,
        trends: trendsData || null
      })
      
      // Calculate summary stats
      calculateSummaryStats(healthData, issuesData, slaData, trendsData)
      
      setLastUpdated(new Date().toISOString())
    } catch (err) {
      console.error('Dashboard fetch error:', err)
      
      // Clear existing data on error
      setDashboardData({
        health: null,
        issues: null,
        slaTimers: null,
        trends: null
      })
      
      // Reset summary stats
      setSummaryStats({
        active_issues: 0,
        critical_issues: 0,
        sla_risk_issues: 0,
        complaints_today: 0,
        trend: {
          critical_change: 0,
          complaints_change: 0
        }
      })
      
      // Set user-friendly error message
      if (err.message === 'No issues data received from server') {
        setError('Server returned empty data. Please try again.')
      } else if (err.response?.status === 404) {
        setError('Dashboard endpoint not found. Please check configuration.')
      } else if (err.response?.status === 500) {
        setError('Server error. Please try again later.')
      } else if (err.message?.includes('Network Error')) {
        setError('Network connection failed. Please check your internet.')
      } else {
        setError('Failed to load dashboard data. Please refresh or try again later.')
      }
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }

  const calculateSummaryStats = (healthData, issuesData, slaData, trendsData) => {
    try {
      // Safely get all issues with null checking
      const allIssues = issuesData?.issues || []
      
      // Filter active issues (not resolved)
      const activeIssues = allIssues.filter(issue => issue?.status !== 'RESOLVED')
      
      // Calculate stats with safe access
      const activeIssuesCount = activeIssues.length
      
      const criticalIssuesCount = activeIssues.filter(issue => {
        const priority = issue?.priority;
        return priority?.label === 'CRITICAL' || priority === 'CRITICAL';
      }).length
      
      // SLA Risk count - check each active issue with safe access
      const slaRiskCount = activeIssues.filter(issue => {
        const slaRisk = issue?.sla?.risk;
        return slaRisk === 'WARNING' || slaRisk === 'BREACHING';
      }).length
      
      // Total complaints from active issues with safe access
      const totalComplaints = activeIssues.reduce((sum, issue) => {
        const complaints = issue?.complaints?.total || issue?.complaint_count || 0;
        return sum + (typeof complaints === 'number' ? complaints : 0);
      }, 0)
      
      // Get trends from API or calculate
      let criticalTrend = 0
      let complaintsTrend = 0
      
      if (trendsData) {
        // Use API trends if available
        criticalTrend = trendsData.critical_change || 0
        complaintsTrend = trendsData.complaints_change || 0
      }
      
      setSummaryStats({
        active_issues: activeIssuesCount,
        critical_issues: criticalIssuesCount,
        sla_risk_issues: slaRiskCount,
        complaints_today: totalComplaints,
        trend: {
          critical_change: criticalTrend,
          complaints_change: complaintsTrend
        }
      })
      
    } catch (error) {
      console.error('Error calculating summary stats:', error)
      // Don't throw here, just log and use default values
    }
  }

  useEffect(() => {
    fetchDashboardData()

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchDashboardData(true)
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  // Safely get issues with null checking
  const allIssues = dashboardData.issues?.issues || []
  const activeIssues = allIssues.filter(i => i?.status !== 'RESOLVED')
  const resolvedIssues = allIssues.filter(i => i?.status === 'RESOLVED')

  return (
    <div className="min-h-screen bg-black">
      <Header
        lastUpdated={lastUpdated}
        onRefresh={() => fetchDashboardData(true)}
        isRefreshing={isRefreshing}
      />

      <main className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
        {/* Error Banner */}
        {error && (
          <div className="mb-4 sm:mb-6 bg-red-500/20 backdrop-blur-md border border-red-400/50 rounded-xl sm:rounded-2xl p-3 sm:p-4 flex items-center justify-between">
            <div className="flex items-center gap-2 sm:gap-3">
              <AlertCircle className="w-4 h-4 sm:w-5 sm:h-5 text-red-300 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="font-medium text-red-200 text-sm sm:text-base truncate">{error}</p>
                <p className="text-xs sm:text-sm text-red-300 truncate">Please refresh or try again later</p>
              </div>
            </div>
            <button
              onClick={() => fetchDashboardData(true)}
              disabled={isRefreshing}
              className="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg bg-red-400/20 hover:bg-red-400/30 text-red-200 text-xs sm:text-sm font-medium transition-colors whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
              title="Retry"
            >
              <RefreshCw className={`w-3 h-3 sm:w-4 sm:h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              <span className="hidden xs:inline">Retry</span>
            </button>
          </div>
        )}

        {/* Loading State */}
        {isLoading ? (
          <div className="space-y-6">
            {/* Stat Cards Skeleton */}
            <StatCardsGridSkeleton />
            
            {/* Charts Row Skeleton */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
              <ChartSkeleton />
              <ChartSkeleton />
            </div>
            
            {/* Priority Issues Section Skeleton */}
            <div>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-0 mb-4 sm:mb-6">
                <div className="h-7 bg-white/10 rounded-lg w-48 animate-pulse"></div>
                <div className="flex gap-2">
                  {[...Array(4)].map((_, i) => (
                    <div key={i} className="h-10 bg-white/10 rounded-lg w-24 animate-pulse"></div>
                  ))}
                </div>
              </div>
              <TableSkeletonEnhanced rows={8} columns={7} />
            </div>
          </div>
        ) : error ? (
          // Error state - show empty state with retry option
          <div className="text-center py-12 sm:py-16 px-4">
            <div className="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-red-500/20 mb-4 sm:mb-6">
              <AlertCircle className="w-8 h-8 sm:w-10 sm:h-10 text-red-400" />
            </div>
            <h3 className="text-lg sm:text-xl font-semibold text-white mb-2">Unable to Load Dashboard</h3>
            <p className="text-white/70 mb-6 sm:mb-8 max-w-md mx-auto text-sm sm:text-base">
              {error}
            </p>
            <button
              onClick={() => fetchDashboardData(true)}
              disabled={isRefreshing}
              className="inline-flex items-center gap-2 px-4 sm:px-6 py-2.5 sm:py-3 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw className={`w-4 h-4 sm:w-5 sm:h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
              {isRefreshing ? 'Retrying...' : 'Retry Loading Dashboard'}
            </button>
          </div>
        ) : (
          <>
            {/* Stat Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6 sm:mb-8">
              <StatCard
                title="Active Issues"
                value={summaryStats.active_issues}
                icon={Activity}
                variant="normal"
              />
              <StatCard
                title="Critical Issues"
                value={summaryStats.critical_issues}
                trend={summaryStats.trend.critical_change}
                icon={AlertCircle}
                variant="danger"
              />
              <StatCard
                title="SLA Risk"
                value={summaryStats.sla_risk_issues}
                icon={Clock}
                variant="warning"
              />
              <StatCard
                title="Total Complaints"
                value={summaryStats.complaints_today}
                trend={summaryStats.trend.complaints_change}
                icon={MessageSquare}
                variant="normal"
              />
            </div>

            {/* Charts Row - Only show if we have health data */}
            {dashboardData.health && activeIssues.length > 0 && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mb-6 sm:mb-8">
                <HealthPieChart 
                  data={dashboardData.health?.health_distribution} 
                  isLoading={false}
                />
                <SeverityBarChart 
                  data={dashboardData.health?.severity_distribution} 
                  isLoading={false}
                />
              </div>
            )}

            {/* Priority Issues Section */}
            <div className="mb-6 sm:mb-8">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-0 mb-4 sm:mb-6">
                <h2 className="text-lg sm:text-xl font-bold text-white">Priority Issues</h2>
                {activeIssues.length > 0 && (
                  <IssueTableFilters
                    issues={activeIssues}
                    onFiltersChange={setTableFilters}
                  />
                )}
              </div>
              
              {activeIssues.length === 0 ? (
                <div className="card-premium text-center py-8 sm:py-12 px-4">
                  <div className="text-green-400 text-4xl sm:text-5xl mb-3 sm:mb-4">🎉</div>
                  <h3 className="text-base sm:text-lg font-semibold text-white mb-2">No Active Issues</h3>
                  <p className="text-white/70 text-sm sm:text-base">
                    All issues are resolved. The system is running smoothly.
                  </p>
                </div>
              ) : (
                <IssueTable 
                  issues={activeIssues}
                  isLoading={false}
                  filters={tableFilters}
                />
              )}
            </div>

            {/* Resolved Issues Section */}
            {resolvedIssues.length > 0 && (
              <div className="mt-8 sm:mt-12">
                <h2 className="text-lg sm:text-xl font-bold text-white mb-4 sm:mb-6">Recently Resolved Issues</h2>
                <ResolvedIssuesSection 
                  resolvedIssues={resolvedIssues}
                />
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}