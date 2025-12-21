/**
 * Issue Detail Page
 * Displays comprehensive issue information with intelligence signals
 * Includes SLA tracking, priority scoring, health metrics
 */

import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Clock,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  MessageSquare,
  RefreshCw,
  Zap,
  Edit3,
  X,
  Home,
  ExternalLink
} from 'lucide-react'
import { formatDate, formatRelativeDate } from '../utils/formatters'
import {
  SeverityBadge,
  HealthBadge,
  SLABadge,
  StatusBadge,
  CategoryBadge,
  DuplicateBadge
} from '../components/BadgeComponents'
import { IssueDetailSkeleton } from '../components/SkeletonLoaders'
import { dashboardApi, issueApi } from '../api/dashboardApi'

export default function IssueDetail() {
  const { issueId } = useParams()
  const navigate = useNavigate()
  const [issue, setIssue] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isFetching, setIsFetching] = useState(false)
  const [error, setError] = useState(null)
  const [isStatusModalOpen, setIsStatusModalOpen] = useState(false)
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false)
  const [statusError, setStatusError] = useState(null)
  const [statusSuccess, setStatusSuccess] = useState(false)

  useEffect(() => {
    fetchIssueDetails()
  }, [issueId])

  const fetchIssueDetails = async () => {
    try {
      if (!isFetching) setIsLoading(true)
      setError(null)

      const data = await dashboardApi.getIssueDetails(issueId)
      setIssue(data)
    } catch (err) {
      console.error('Failed to fetch issue:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to load issue details')
    } finally {
      setIsLoading(false)
      setIsFetching(false)
    }
  }

  const handleRefresh = async () => {
    setIsFetching(true)
    await fetchIssueDetails()
  }

  const handleStatusUpdate = async (newStatus) => {
    setIsUpdatingStatus(true)
    setStatusError(null)
    setStatusSuccess(false)

    try {
      const result = await issueApi.updateStatus(issueId, newStatus)
      
      // Update local state
      setIssue(prev => ({
        ...prev,
        status: newStatus,
        resolved_at: newStatus === 'RESOLVED' ? new Date().toISOString() : prev.resolved_at
      }))
      
      setStatusSuccess(true)
      setIsStatusModalOpen(false)
      
      // Clear success message after 3 seconds
      setTimeout(() => setStatusSuccess(false), 3000)
      
      console.log('Status updated successfully:', result)
    } catch (err) {
      console.error('Failed to update status:', err)
      setStatusError(err.response?.data?.detail || err.message || 'Failed to update issue status')
    } finally {
      setIsUpdatingStatus(false)
    }
  }

  const getErrorMessage = () => {
    if (error?.includes('not found') || error?.includes('404')) {
      return 'The requested issue was not found. It may have been deleted or the ID is incorrect.'
    }
    if (error?.includes('network') || error?.includes('connection')) {
      return 'Network connection error. Please check your internet connection and try again.'
    }
    if (error?.includes('timeout')) {
      return 'Request timeout. The server is taking too long to respond.'
    }
    if (error?.includes('500') || error?.includes('server')) {
      return 'Server error. Please try again later or contact support.'
    }
    return error || 'The requested issue could not be loaded'
  }

  const handleBackToDashboard = () => {
    navigate('/dashboard')
  }

  if (isLoading) {
    return <IssueDetailSkeleton />
  }

  if (error || !issue) {
    const errorMessage = getErrorMessage()
    const isNotFound = errorMessage.toLowerCase().includes('not found')
    const isNetworkError = errorMessage.toLowerCase().includes('network') || errorMessage.toLowerCase().includes('connection')
    const isServerError = errorMessage.toLowerCase().includes('server') || errorMessage.toLowerCase().includes('500')

    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="card-premium text-center p-8">
            {/* Error Icon */}
            <div className="mb-6">
              {isNotFound && (
                <div className="relative">
                  <XCircle className="w-20 h-20 text-red-400 mx-auto opacity-80" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl font-bold text-white">404</span>
                  </div>
                </div>
              )}
              {isNetworkError && (
                <div className="relative">
                  <AlertTriangle className="w-20 h-20 text-yellow-400 mx-auto opacity-80" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <RefreshCw className="w-10 h-10 text-white animate-spin" />
                  </div>
                </div>
              )}
              {isServerError && (
                <div className="relative">
                  <XCircle className="w-20 h-20 text-orange-400 mx-auto opacity-80" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl font-bold text-white">500</span>
                  </div>
                </div>
              )}
              {!isNotFound && !isNetworkError && !isServerError && (
                <XCircle className="w-20 h-20 text-red-400 mx-auto opacity-80" />
              )}
            </div>

            {/* Error Title */}
            <h2 className="text-2xl font-bold text-white mb-3">
              {isNotFound ? 'Issue Not Found' : 
               isNetworkError ? 'Connection Error' :
               isServerError ? 'Server Error' : 'Error Loading Issue'}
            </h2>

            {/* Error Message */}
            <div className="bg-black/30 rounded-lg p-4 mb-6">
              <p className="text-white/90 text-sm leading-relaxed">
                {errorMessage}
              </p>
              
              {/* Issue ID Reference */}
              {issueId && (
                <div className="mt-3 pt-3 border-t border-white/10">
                  <p className="text-xs text-white/60 font-mono break-all">
                    Issue ID: {issueId}
                  </p>
                </div>
              )}
            </div>

            {/* Troubleshooting Tips */}
            {(isNetworkError || isServerError) && (
              <div className="bg-white/5 rounded-lg p-4 mb-6 text-left">
                <h4 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-yellow-400" />
                  Troubleshooting Tips:
                </h4>
                <ul className="text-xs text-white/70 space-y-1">
                  {isNetworkError && (
                    <>
                      <li className="flex items-start gap-2">
                        <span className="text-yellow-400 mt-0.5">•</span>
                        Check your internet connection
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-yellow-400 mt-0.5">•</span>
                        Verify network settings
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-yellow-400 mt-0.5">•</span>
                        Try refreshing the page
                      </li>
                    </>
                  )}
                  {isServerError && (
                    <>
                      <li className="flex items-start gap-2">
                        <span className="text-orange-400 mt-0.5">•</span>
                        Server may be temporarily unavailable
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-orange-400 mt-0.5">•</span>
                        Try again in a few minutes
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-orange-400 mt-0.5">•</span>
                        Contact system administrator
                      </li>
                    </>
                  )}
                </ul>
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-3">
              <button
                onClick={handleRefresh}
                disabled={isFetching}
                className="btn btn-secondary w-full flex items-center justify-center gap-2 transition-all hover:scale-[1.02]"
              >
                <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
                {isFetching ? 'Retrying...' : 'Try Again'}
              </button>
              
              <button
                onClick={handleBackToDashboard}
                className="btn btn-primary w-full flex items-center justify-center gap-2 transition-all hover:scale-[1.02]"
              >
                <Home className="w-4 h-4" />
                Back to Dashboard
              </button>

              {/* Report Issue Link for persistent errors */}
              {(isNetworkError || isServerError) && (
                <button
                  onClick={() => window.location.href = 'mailto:support@example.com?subject=Issue%20Loading%20Error'}
                  className="btn btn-primary-outline w-full flex items-center justify-center gap-2 text-sm"
                >
                  <ExternalLink className="w-3 h-3" />
                  Report Persistent Issue
                </button>
              )}
            </div>

            {/* Footer Note */}
            <div className="mt-6 pt-4 border-t border-white/10">
              <p className="text-xs text-white/40">
                If the problem persists, please contact support
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Sticky Header */}
      <div className="bg-white/10 backdrop-blur-md border-b border-white/20 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          {/* Back Button */}
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-white/70 hover:text-white mb-4 transition-colors group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            Back to Dashboard
          </button>

          {/* Title Section */}
          <div className="flex items-start justify-between gap-4 mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 flex-wrap mb-2">
                <h1 className="text-3xl font-bold text-white">
                  {issue.category} in {issue.hostel}
                </h1>
                <StatusBadge status={issue.status} size="lg" />
              </div>
              <p className="text-sm text-white/60 font-mono">{issue.issue_id}</p>
            </div>

            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={isFetching}
              className="btn btn-icon"
              title="Refresh"
            >
              <RefreshCw className={`w-5 h-5 ${isFetching ? 'animate-spin' : ''}`} />
            </button>
          </div>

          {/* Status Badges Row */}
          <div className="flex items-center gap-2 flex-wrap">
            <CategoryBadge category={issue.category} size="sm" />
            {issue.severity && <SeverityBadge severity={issue.severity} size="sm" />}
            {issue.health && <HealthBadge health={issue.health} size="sm" />}
            {issue.sla && <SLABadge sla={issue.sla} size="sm" />}
          </div>

          {/* Success Message */}
          {statusSuccess && (
            <div className="mt-4 px-4 py-3 bg-green-500/20 border border-green-400/50 rounded-lg flex items-center gap-2 text-green-300 text-sm animate-fade-in">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              <span>Status updated successfully</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Issue Details & Timeline */}
          <div className="lg:col-span-2 space-y-6">
            {/* Issue Metadata */}
            <div className="card-premium">
              <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-blue-400" />
                Issue Information
              </h3>

              <div className="grid grid-cols-2 gap-6">
                {/* Hostel */}
                <div>
                  <p className="text-sm font-medium text-white/70 mb-1">Hostel</p>
                  <p className="text-base font-semibold text-white">{issue.hostel}</p>
                </div>

                {/* Category */}
                <div>
                  <p className="text-sm font-medium text-white/70 mb-1">Category</p>
                  <CategoryBadge category={issue.category} size="sm" />
                </div>

                {/* Created Date */}
                <div>
                  <p className="text-sm font-medium text-white/70 mb-1">Created</p>
                  <p className="text-sm text-white/90">
                    {formatDate(issue.timestamps?.created_at || issue.created_at, 'PPp')}
                  </p>
                </div>

                {/* Last Updated */}
                <div>
                  <p className="text-sm font-medium text-white/70 mb-1">Last Updated</p>
                  <p className="text-sm text-white/90">
                    {formatRelativeDate(
                      issue.timestamps?.last_updated || issue.last_updated
                    )}
                  </p>
                </div>

                {/* Total Complaints */}
                <div>
                  <p className="text-sm font-medium text-white/70 mb-1">Total Complaints</p>
                  <p className="text-2xl font-bold text-white">
                    {issue.complaints?.total || issue.complaint_count || 0}
                  </p>
                </div>

                {/* Unique Complaints */}
                <div>
                  <p className="text-sm font-medium text-white/70 mb-1">Breakdown</p>
                  <p className="text-sm text-white/90">
                    <span className="font-semibold text-green-400">
                      {issue.complaints?.unique || issue.unique_complaint_count || 0} unique
                    </span>
                    {' • '}
                    <span className="font-semibold text-yellow-400">
                      {issue.complaints?.duplicates || 0} duplicates
                    </span>
                  </p>
                </div>
              </div>
            </div>

            {/* Complaint Timeline */}
            <div className="card-premium">
              <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                <Clock className="w-5 h-5 text-cyan-400" />
                Complaint Timeline ({issue.complaints_list?.length || 0})
              </h3>

              {issue.complaints_list && issue.complaints_list.length > 0 ? (
                <div className="space-y-4">
                  {issue.complaints_list.map((complaint, index) => (
                    <div
                      key={complaint.id || index}
                      className={`border-l-4 pl-4 py-3 rounded transition-all duration-200 ${
                        complaint.is_duplicate
                          ? 'border-yellow-400/50 bg-yellow-400/5 opacity-75'
                          : 'border-blue-400 bg-blue-400/5 hover:bg-blue-400/10'
                      }`}
                    >
                      {/* Header Row */}
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-mono text-white/80">{complaint.id}</span>
                          {complaint.is_duplicate && <DuplicateBadge />}
                        </div>
                        <span className="text-xs text-white/60 whitespace-nowrap">
                          {formatDate(complaint.created_at, 'PPp')}
                        </span>
                      </div>

                      {/* Complaint Text */}
                      <p className="text-sm text-white/90 mb-3 leading-relaxed">
                        {complaint.text}
                      </p>

                      {/* Metadata Footer */}
                      <div className="flex items-center gap-4 flex-wrap text-xs text-white/70">
                        <span className="flex items-center gap-1">
                          <Zap className="w-3 h-3 text-yellow-400" />
                          Urgency: <span className="font-semibold">{complaint.urgency}</span>
                        </span>

                        {complaint.similarity_score !== undefined && (
                          <span className="flex items-center gap-1">
                            Similarity:{' '}
                            <span className="font-semibold">
                              {(complaint.similarity_score * 100).toFixed(1)}%
                            </span>
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-white/60">
                  <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-40" />
                  <p>No complaints recorded yet</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Intelligence & Actions */}
          <div className="space-y-6">
            {/* SLA Card */}
            {issue.sla && (
              <div className={`card-premium border ${
                issue.sla?.is_breached
                  ? 'border-red-400/50 bg-gradient-to-br from-red-500/10 to-red-500/5'
                  : 'border-white/30'
              }`}>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  SLA Status
                </h3>

                <div className="space-y-4">
                  <SLABadge sla={issue.sla} size="lg" />

                  <div>
                    <p className="text-sm font-medium text-white/70 mb-1">Time Remaining</p>
                    <p className="text-3xl font-bold">
                      {issue.sla?.is_breached ? (
                        <span className="text-red-400">
                          {Math.abs(issue.sla.time_remaining_minutes)}m overdue
                        </span>
                      ) : (
                        <span className="text-green-400">
                          {Math.floor(issue.sla.time_remaining_minutes / 60)}h{' '}
                          {issue.sla.time_remaining_minutes % 60}m
                        </span>
                      )}
                    </p>
                  </div>

                  {issue.sla?.is_breached && (
                    <div className="bg-red-500/20 border border-red-400/50 rounded-lg p-3">
                      <div className="flex items-center gap-2 text-red-300 font-medium mb-1">
                        <AlertTriangle className="w-4 h-4" />
                        SLA Breached
                      </div>
                      <p className="text-xs text-red-300/90">
                        Immediate action required to resolve this issue
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Health Score Card */}
            {issue.health && (
              <div className="card-premium">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-orange-400" />
                  Health Score
                </h3>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-4xl font-bold text-white">{issue.health.score}</span>
                    <HealthBadge health={issue.health} size="lg" />
                  </div>

                  <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 transition-all duration-500"
                      style={{ width: `${issue.health.score}%` }}
                    />
                  </div>

                  <p className="text-xs text-white/60">
                    Score 0-100 • Higher = worse health
                  </p>
                </div>
              </div>
            )}

            {/* Priority Score Card */}
            {issue.priority && (
              <div className="card-premium">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-yellow-400" />
                  Priority Score
                </h3>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-4xl font-bold text-white">
                      {issue.priority.score.toFixed(1)}
                    </span>
                  </div>

                  <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
                      style={{ width: `${(issue.priority.score / 100) * 100}%` }}
                    />
                  </div>

                  <p className="text-xs text-white/60">
                    Weighted multi-signal priority ranking
                  </p>
                </div>
              </div>
            )}

            {/* Severity Card */}
            {issue.severity && (
              <div className="card-premium">
                <h3 className="text-lg font-semibold text-white mb-4">Severity</h3>

                <div className="space-y-3">
                  <SeverityBadge severity={issue.severity} size="lg" />

                  <div>
                    <p className="text-sm text-white/70">
                      Classification based on issue impact and urgency patterns
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Resolved Status */}
            {issue.status === 'RESOLVED' && (
              <div className="card-premium bg-gradient-to-br from-green-500/10 to-green-500/5 border-green-400/50">
                <div className="flex items-center gap-3 text-green-300">
                  <CheckCircle2 className="w-6 h-6 flex-shrink-0" />
                  <div>
                    <p className="font-semibold">Issue Resolved</p>
                    {issue.resolved_at && (
                      <p className="text-sm text-green-300/80">
                        {formatRelativeDate(issue.resolved_at)}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Update Status Button */}
            <button
              onClick={() => setIsStatusModalOpen(true)}
              className="btn btn-secondary w-full flex items-center justify-center gap-2 transition-all hover:scale-[1.02]"
            >
              <Edit3 className="w-4 h-4" />
              Change Status
            </button>

            {/* Status Update Modal */}
            {isStatusModalOpen && (
              <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                <div className="card-premium w-full max-w-md">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                      <Edit3 className="w-5 h-5 text-blue-400" />
                      Update Issue Status
                    </h3>
                    <button
                      onClick={() => setIsStatusModalOpen(false)}
                      disabled={isUpdatingStatus}
                      className="p-1 hover:bg-white/10 rounded transition-colors"
                    >
                      <X className="w-5 h-5 text-white/60" />
                    </button>
                  </div>

                  {/* Current Status */}
                  <div className="mb-6 p-4 bg-white/5 rounded-lg border border-white/10">
                    <p className="text-sm text-white/70 mb-2">Current Status</p>
                    <StatusBadge status={issue.status} size="lg" />
                  </div>

                  {/* Status Error */}
                  {statusError && (
                    <div className="mb-4 p-3 bg-red-500/20 border border-red-400/50 rounded-lg animate-fade-in">
                      <p className="text-sm text-red-300">{statusError}</p>
                    </div>
                  )}

                  {/* Status Options */}
                  <div className="space-y-2 mb-6">
                    {['OPEN', 'IN_PROGRESS', 'RESOLVED', 'REOPENED'].map((status) => (
                      <button
                        key={status}
                        onClick={() => handleStatusUpdate(status)}
                        disabled={isUpdatingStatus || status === issue.status}
                        className={`w-full px-4 py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-between ${
                          status === issue.status
                            ? 'bg-white/10 text-white/50 cursor-not-allowed'
                            : 'bg-white/10 hover:bg-white/20 text-white hover:text-white active:scale-95'
                        } ${
                          isUpdatingStatus ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                      >
                        <span>
                          {status === 'OPEN' && '🔴 Open'}
                          {status === 'IN_PROGRESS' && '🟡 In Progress'}
                          {status === 'RESOLVED' && '🟢 Resolved'}
                          {status === 'REOPENED' && '🔵 Reopened'}
                        </span>
                        {status === issue.status && (
                          <CheckCircle2 className="w-4 h-4 text-green-400" />
                        )}
                      </button>
                    ))}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-3">
                    <button
                      onClick={() => setIsStatusModalOpen(false)}
                      disabled={isUpdatingStatus}
                      className="flex-1 btn btn-primary-outline"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}