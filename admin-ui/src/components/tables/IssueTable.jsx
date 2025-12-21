import React, { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Clock, AlertTriangle, ChevronRight, ChevronLeft, ChevronsLeft, ChevronsRight } from 'lucide-react'
import { formatRelativeDate, formatNumber } from '../../utils/formatters'
import {
  PriorityBadge,
  SeverityBadge,
  HealthBadge,
  SLABadge,
  StatusBadge,
  CategoryBadge
} from '../BadgeComponents'
import { TableSkeleton } from '../SkeletonLoaders'

export default function IssueTable({ issues, isLoading, filters = {} }) {
  const navigate = useNavigate()
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 20

  // Filter issues based on applied filters using useMemo for performance
  const filteredIssues = useMemo(() => {
    if (!issues || issues.length === 0) return []

    return issues.filter(issue => {
      // Filter out resolved issues
      if (issue.status === 'RESOLVED') return false

      // Apply priority filter
      if (filters.priority?.length > 0) {
        const priorityLabel = issue.priority?.label
        if (!priorityLabel || !filters.priority.includes(priorityLabel)) return false
      }

      // Apply severity filter
      if (filters.severity?.length > 0) {
        const severityLabel = issue.severity?.label
        if (!severityLabel || !filters.severity.includes(severityLabel)) return false
      }

      // Apply health filter
      if (filters.health?.length > 0) {
        const healthLabel = issue.health?.label
        if (!healthLabel || !filters.health.includes(healthLabel)) return false
      }

      // Apply category filter
      if (filters.category?.length > 0) {
        const category = issue.category
        if (!category || !filters.category.includes(category)) return false
      }

      // Apply hostel filter
      if (filters.hostel?.length > 0) {
        const hostel = issue.hostel
        if (!hostel || !filters.hostel.includes(hostel)) return false
      }

      // Apply SLA status filter
      if (filters.slaStatus?.length > 0) {
        const slaRisk = issue.sla?.risk
        if (!slaRisk || !filters.slaStatus.includes(slaRisk)) return false
      }

      return true
    })
  }, [issues, filters])

  // Calculate pagination values
  const totalPages = Math.ceil(filteredIssues.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentItems = filteredIssues.slice(startIndex, endIndex)

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [filters])

  const handleRowClick = (issueId) => {
    navigate(`/issues/${issueId}`)
  }

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page)
    }
  }

  // Generate pagination numbers
  const paginationNumbers = useMemo(() => {
    const numbers = []
    const maxVisible = 5
    
    if (totalPages <= maxVisible) {
      // Show all pages
      for (let i = 1; i <= totalPages; i++) {
        numbers.push(i)
      }
    } else if (currentPage <= 3) {
      // Near the start
      for (let i = 1; i <= maxVisible; i++) {
        numbers.push(i)
      }
    } else if (currentPage >= totalPages - 2) {
      // Near the end
      for (let i = totalPages - maxVisible + 1; i <= totalPages; i++) {
        numbers.push(i)
      }
    } else {
      // In the middle
      for (let i = currentPage - 2; i <= currentPage + 2; i++) {
        numbers.push(i)
      }
    }
    
    return numbers
  }, [currentPage, totalPages])

  if (isLoading) {
    return <TableSkeleton rows={8} />
  }

  if (!issues || issues.length === 0) {
    return (
      <div className="card-premium text-center py-12">
        <div className="text-green-400 text-5xl mb-4">🟢</div>
        <h3 className="text-lg font-semibold text-white mb-2">No Active Issues</h3>
        <p className="text-white/80">
          The system is running smoothly. New complaints will appear here automatically.
        </p>
      </div>
    )
  }

  if (filteredIssues.length === 0) {
    return (
      <div className="card-premium text-center py-12">
        <div className="text-yellow-400 text-5xl mb-4">⚠️</div>
        <h3 className="text-lg font-semibold text-white mb-2">No Matching Issues</h3>
        <p className="text-white/80">
          No issues match the current filters. Try adjusting your filter criteria.
          {Object.values(filters).some(arr => arr.length > 0) && (
            <button 
              onClick={() => window.location.reload()}
              className="block mx-auto mt-4 px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 rounded-lg transition-colors text-sm"
            >
              Clear all filters
            </button>
          )}
        </p>
      </div>
    )
  }

  return (
    <div className="card-premium overflow-hidden p-0">
      {/* Header */}
      <div className="px-6 py-4 border-b border-white/20 bg-white/5">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            Priority Issues
            <span className="text-sm font-normal text-white/80 ml-2">
              ({filteredIssues.length} active issues)
            </span>
          </h3>
          <div className="flex items-center gap-4">
            <span className="text-sm text-white/80">
              Showing {startIndex + 1}-{Math.min(endIndex, filteredIssues.length)} of {filteredIssues.length}
            </span>
            <span className="text-xs text-white/60 px-2 py-1 bg-white/5 rounded">
              Page {currentPage}/{totalPages}
            </span>
          </div>
        </div>
      </div>

      {/* Table Container with Mobile Scroll */}
      <div className="overflow-x-auto -mx-6 px-6 sm:mx-0 sm:px-0">
        <table className="min-w-full">
          <thead>
            <tr className="border-b border-white/10 bg-white/5">
              <th className="px-6 py-3 text-left text-xs font-semibold text-white/80 uppercase tracking-wider">
                Hostel
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-white/80 uppercase tracking-wider">
                Category
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-white/80 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-white/80 uppercase tracking-wider">
                Priority
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-white/80 uppercase tracking-wider">
                Severity
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-white/80 uppercase tracking-wider">
                Health
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-white/80 uppercase tracking-wider">
                SLA
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-white/80 uppercase tracking-wider">
                Complaints
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-white/80 uppercase tracking-wider">
                Updated
              </th>
              <th className="relative px-6 py-3">
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {currentItems.map((issue) => {
              const isCritical = issue.priority?.label === 'CRITICAL'
              const isHigh = issue.priority?.label === 'HIGH'
              const rowBg = isCritical ? 'bg-red-500/10' : 'hover:bg-white/5'

              return (
                <tr
                  key={issue.issue_id}
                  className={`
                    ${rowBg} 
                    transition-all duration-200 
                    cursor-pointer 
                    group
                    hover:bg-blue-500/10
                    hover:ring-1 hover:ring-blue-400/30
                    relative
                    focus-within:ring-2 focus-within:ring-blue-500
                    focus-within:outline-none
                  `}
                  onClick={() => handleRowClick(issue.issue_id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault()
                      handleRowClick(issue.issue_id)
                    }
                  }}
                  tabIndex={0}
                  aria-label={`View issue ${issue.issue_id} in ${issue.hostel}`}
                >
                  {/* Column 1: Hostel with Priority Indicator */}
                  <td className="px-6 py-4 whitespace-nowrap relative">
                    {/* Priority Indicator - now inside the td */}
                    {(isCritical || isHigh) && (
                      <div className={`
                        absolute left-0 top-0 bottom-0 w-1
                        ${isCritical ? 'bg-red-500' : 'bg-orange-500'}
                        ${isCritical ? 'animate-pulse' : ''}
                      `} />
                    )}
                    <div className="text-sm font-medium text-white pl-3">{issue.hostel}</div>
                  </td>

                  {/* Column 2: Category */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <CategoryBadge category={issue.category} size="sm" />
                  </td>

                  {/* Column 3: Status */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <StatusBadge status={issue.status} size="sm" />
                  </td>

                  {/* Column 4: Priority */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <PriorityBadge priority={issue.priority} size="sm" />
                      <div className="text-xs text-white/80 mt-1">
                        {issue.priority?.score?.toFixed(1) || 'N/A'}
                      </div>
                    </div>
                  </td>

                  {/* Column 5: Severity */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <SeverityBadge severity={issue.severity} size="sm" />
                  </td>

                  {/* Column 6: Health */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <HealthBadge health={issue.health} size="sm" />
                      <div className="text-xs text-white/80 mt-1">
                        {issue.health?.score || 'N/A'}
                      </div>
                    </div>
                  </td>

                  {/* Column 7: SLA */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="space-y-1">
                      <SLABadge sla={issue.sla} size="sm" />
                      {issue.sla?.time_remaining_minutes !== undefined && (
                        <div className="flex items-center gap-1 text-xs text-white/80">
                          <Clock className="w-3 h-3" />
                          {issue.sla?.is_breached ? (
                            <span className="text-red-400 font-medium">
                              {Math.abs(issue.sla.time_remaining_minutes)}m overdue
                            </span>
                          ) : (
                            <span>{issue.sla.time_remaining_minutes}m left</span>
                          )}
                        </div>
                      )}
                    </div>
                  </td>

                  {/* Column 8: Complaints */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-white">
                      {formatNumber(issue.complaints?.total || 0)}
                      <span className="text-white/80 text-xs ml-1">
                        ({formatNumber(issue.complaints?.unique || 0)} unique)
                      </span>
                    </div>
                  </td>

                  {/* Column 9: Updated */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-white/80">
                    {formatRelativeDate(
                      issue.timestamps?.last_updated || issue.last_updated
                    )}
                  </td>

                  {/* Column 10: Action */}
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <ChevronRight className="w-4 h-4 text-white/60 group-hover:text-white transition-colors" />
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="px-6 py-4 border-t border-white/10 bg-white/5 flex items-center justify-between">
        <div className="text-xs text-white/80">
          Page {currentPage} of {totalPages} • {filteredIssues.length} active issues
        </div>
        
        <div className="flex items-center gap-2">
          {/* First Page */}
          <button
            onClick={() => goToPage(1)}
            disabled={currentPage === 1}
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="First page"
          >
            <ChevronsLeft className="w-4 h-4" />
          </button>

          {/* Previous Page */}
          <button
            onClick={() => goToPage(currentPage - 1)}
            disabled={currentPage === 1}
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Previous page"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          {/* Page Numbers */}
          <div className="flex items-center gap-1">
            {paginationNumbers.map(pageNum => (
              <button
                key={pageNum}
                onClick={() => goToPage(pageNum)}
                className={`w-8 h-8 rounded-lg text-sm font-medium transition-all ${
                  currentPage === pageNum
                    ? 'bg-blue-500/30 text-blue-300 border border-blue-400/50'
                    : 'bg-white/5 hover:bg-white/10 text-white/90'
                }`}
              >
                {pageNum}
              </button>
            ))}
          </div>

          {/* Next Page */}
          <button
            onClick={() => goToPage(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Next page"
          >
            <ChevronRight className="w-4 h-4" />
          </button>

          {/* Last Page */}
          <button
            onClick={() => goToPage(totalPages)}
            disabled={currentPage === totalPages}
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Last page"
          >
            <ChevronsRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}