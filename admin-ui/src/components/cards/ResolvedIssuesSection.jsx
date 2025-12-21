// components/cards/ResolvedIssuesSection.jsx
import React, { useState } from 'react'
import { CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react'
import { formatDate } from '../../utils/formatters'
import { CategoryBadge, SeverityBadge } from '../BadgeComponents'

export default function ResolvedIssuesSection({ resolvedIssues = [] }) {
  const [expandedHostels, setExpandedHostels] = useState({})

  if (!resolvedIssues || resolvedIssues.length === 0) {
    return (
      <div className="card-premium">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-green-400" />
            Resolved Issues
          </h3>
          <span className="text-sm text-white/60">0 issues resolved</span>
        </div>
        <div className="text-center py-12 text-white/60">
          <CheckCircle2 className="w-12 h-12 mx-auto mb-3 opacity-40" />
          <p>No resolved issues yet</p>
        </div>
      </div>
    )
  }

  // Group by hostel
  const groupedByHostel = resolvedIssues.reduce((acc, issue) => {
    const hostel = issue.hostel || 'Unknown'
    if (!acc[hostel]) {
      acc[hostel] = []
    }
    acc[hostel].push(issue)
    return acc
  }, {})

  // Calculate category distribution per hostel
  const getCategoryDistribution = (issues) => {
    return issues.reduce((acc, issue) => {
      const category = issue.category || 'Other'
      acc[category] = (acc[category] || 0) + 1
      return acc
    }, {})
  }

  const toggleHostelExpand = (hostel) => {
    setExpandedHostels(prev => ({
      ...prev,
      [hostel]: !prev[hostel]
    }))
  }

  return (
    <div className="card-premium">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-green-400" />
          Resolved Issues
        </h3>
        <span className="text-sm text-white/60">{resolvedIssues.length} issues resolved</span>
      </div>

      {/* Hostels List */}
      <div className="space-y-3">
        {Object.entries(groupedByHostel).map(([hostel, issues]) => {
          const isExpanded = expandedHostels[hostel]
          const categoryDist = getCategoryDistribution(issues)
          const totalIssues = issues.length

          return (
            <div
              key={hostel}
              className="border border-green-400/30 rounded-lg overflow-hidden hover:border-green-400/50 transition-colors"
            >
              {/* Hostel Header */}
              <button
                onClick={() => toggleHostelExpand(hostel)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleHostelExpand(hostel);
                  }
                }}
                className="w-full px-4 py-4 bg-green-500/10 hover:bg-green-500/15 transition-colors flex items-center justify-between group focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-offset-2 focus:ring-offset-black"
                tabIndex={0}
                aria-expanded={isExpanded}
                aria-label={`${isExpanded ? 'Collapse' : 'Expand'} resolved issues for ${hostel}`}
                aria-controls={`hostel-issues-${hostel.replace(/\s+/g, '-').toLowerCase()}`}
              >
                <div className="flex items-center gap-3 flex-1 text-left">
                  <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-white">{hostel}</p>
                    <p className="text-xs text-white/60">
                      {totalIssues} issue{totalIssues !== 1 ? 's' : ''} resolved
                    </p>
                  </div>
                </div>

                {/* Category Distribution */}
                <div className="flex items-center gap-4 mr-4">
                  <div className="flex gap-2 flex-wrap justify-end max-w-xs">
                    {Object.entries(categoryDist).map(([category, count]) => (
                      <span
                        key={category}
                        className="inline-flex items-center px-2 py-1 rounded-md bg-white/10 text-xs text-white/80 border border-white/20"
                      >
                        <span className="font-semibold text-green-400 mr-1">{count}</span>
                        <span>{category}</span>
                      </span>
                    ))}
                  </div>
                </div>

                {/* Expand Icon */}
                {isExpanded ? (
                  <ChevronUp className="w-5 h-5 text-white/60 group-hover:text-white transition-colors" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-white/60 group-hover:text-white transition-colors" />
                )}
              </button>

              {/* Issues List (Expanded) */}
              {isExpanded && (
                <div 
                  id={`hostel-issues-${hostel.replace(/\s+/g, '-').toLowerCase()}`}
                  className="bg-black/20 border-t border-green-400/30 divide-y divide-green-400/20"
                  role="region"
                  aria-label={`Resolved issues details for ${hostel}`}
                >
                  {issues.map((issue) => (
                    <div
                      key={issue.issue_id}
                      className="px-4 py-4 hover:bg-green-500/5 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <CategoryBadge category={issue.category} size="sm" />
                            {issue.severity && (
                              <SeverityBadge severity={issue.severity} size="sm" />
                            )}
                          </div>
                          <p className="text-sm text-white/90">{issue.category}</p>
                          <p className="text-xs text-white/60 mt-1 font-mono">
                            {issue.issue_id}
                          </p>
                        </div>

                        <div className="text-right text-sm text-white/70">
                          <p className="font-medium text-green-300">Resolved</p>
                          <p className="text-xs text-white/60 mt-1">
                            {issue.resolved_at
                              ? formatDate(issue.resolved_at, 'PP')
                              : 'N/A'}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}