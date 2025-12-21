import axios from 'axios'

const dashboardClient = axios.create({
  baseURL: '/admin/dashboard',
  timeout: 10000,
})

const issuesClient = axios.create({
  baseURL: '/issues',
  timeout: 10000,
})

// Request interceptor for logging
dashboardClient.interceptors.request.use(
  (config) => {
    console.log(`[Dashboard API] ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => Promise.reject(error)
)

issuesClient.interceptors.request.use(
  (config) => {
    console.log(`[Issues API] ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
dashboardClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('[Dashboard API Error]', error.response?.data || error.message)
    throw error
  }
)

issuesClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('[Issues API Error]', error.response?.data || error.message)
    throw error
  }
)

export const dashboardApi = {
  /**
   * Get health summary - system-wide health distribution
   * Returns: { total_issues, health_distribution, severity_distribution, sla_risk_distribution }
   */
  getHealth: () => dashboardClient.get('/health-summary'),
  
  /**
   * Get priority issues - main work queue sorted by priority
   * Returns: { generated_at, count, issues[] }
   */
  getIssues: (params = {}) => dashboardClient.get('/priority-issues', { params }),
  
  /**
   * Get SLA timers - issues breaching or at risk of breaching SLA
   * Returns: { breaching[], warning[] }
   */
  getSLATimers: () => dashboardClient.get('/sla-timers'),
  
  /**
   * Get trends - complaint and issue trends over time window
   * Returns: { window, complaints, new_issues, resolved_issues }
   */
  getTrends: (window = '24h') => dashboardClient.get('/trends', { params: { window } }),
  
  /**
   * Get full issue details with intelligence signals
   * Fetches the issue from priority queue to get all enriched data
   * Returns: enriched issue object with priority, severity, health, sla, complaints
   */
  getIssueDetails: async (issueId) => {
    try {
      // Try to get from priority queue first (has all enriched data)
      // Note: limit is capped at 200 by backend validation
      const response = await dashboardClient.get('/priority-issues', { params: { limit: 200 } })
      
      if (!response || !response.issues) {
        console.warn('[Dashboard API] Invalid response from priority-issues', response)
        throw new Error('Invalid response structure')
      }
      
      const issue = response.issues.find(i => i.issue_id === issueId)
      if (issue) {
        console.debug('[Dashboard API] Found issue in priority queue:', issueId)
        // Fetch full complaints list from plain API
        const fullIssue = await issuesClient.get(`/${issueId}`)
        return {
          ...issue,
          complaints_list: fullIssue.complaints || []
        }
      } else {
        console.debug('[Dashboard API] Issue not found in priority queue:', issueId)
        throw new Error(`Issue ${issueId} not found in priority queue`)
      }
    } catch (err) {
      console.warn('[Dashboard API] Could not fetch from priority queue, falling back to plain API', {
        issueId,
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      })
    }
    
    // Fallback: fetch from plain API
    return issuesClient.get(`/${issueId}`)
  }
}

const adminClient = axios.create({
  baseURL: '/admin',
  timeout: 10000,
})

adminClient.interceptors.request.use(
  (config) => {
    console.log(`[Admin API] ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => Promise.reject(error)
)

adminClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('[Admin API Error]', error.response?.data || error.message)
    throw error
  }
)

export const issueApi = {
  /**
   * Get issue details - full issue with all complaints
   * Returns: { issue_id, hostel, category, status, ... }
   */
  getIssue: (issueId) => issuesClient.get(`/${issueId}`),

  /**
   * Update issue status - admin action to change issue lifecycle status
   * Statuses: OPEN, IN_PROGRESS, RESOLVED, REOPENED
   */
  updateStatus: (issueId, status) => adminClient.put(`/issues/${issueId}/status`, { status }),
}

export default dashboardApi