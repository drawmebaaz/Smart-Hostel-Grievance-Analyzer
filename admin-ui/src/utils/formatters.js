/**
 * Utility functions for formatting data in UI
 * Handles dates, numbers, text consistently across the application
 */

import { format, formatDistanceToNow, isValid } from 'date-fns'

/**
 * Format date as readable string
 * @param {Date|string} date - The date to format
 * @param {string} formatStr - date-fns format string (default: 'PPpp')
 * @returns {string} Formatted date or 'N/A'
 */
export const formatDate = (date, formatStr = 'PPpp') => {
  if (!date) return 'N/A'
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date
    return isValid(dateObj) ? format(dateObj, formatStr) : 'N/A'
  } catch (e) {
    console.warn('Date formatting error:', e)
    return 'N/A'
  }
}

/**
 * Format date relative to now (e.g., "2 hours ago")
 * @param {Date|string} date - The date to format
 * @param {boolean} addSuffix - Include "ago" or "in" (default: true)
 * @returns {string } Relative date or 'N/A'
 */
export const formatRelativeDate = (date, addSuffix = true) => {
  if (!date) return 'N/A'
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date
    return isValid(dateObj) ? formatDistanceToNow(dateObj, { addSuffix }) : 'N/A'
  } catch (e) {
    console.warn('Relative date formatting error:', e)
    return 'N/A'
  }
}

/**
 * Format large numbers with thousand separators
 * @param {number} num - The number to format
 * @returns {string} Formatted number
 */
export const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  return parseInt(num, 10).toLocaleString()
}

/**
 * Format percentage with decimal places
 * @param {number} value - The value (0-100)
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {string} Formatted percentage
 */
export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined) return '0%'
  return (Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals)).toFixed(decimals) + '%'
}

/**
 * Truncate text with ellipsis
 * @param {string} text - The text to truncate
 * @param {number} length - Maximum length (default: 50)
 * @returns {string} Truncated text
 */
export const truncateText = (text, length = 50) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

/**
 * Format SLA time remaining
 * @param {number|string} milliseconds - Milliseconds remaining
 * @returns {string} Formatted time (e.g., "2h 30m", "5m")
 */
export const formatTimeRemaining = (milliseconds) => {
  if (!milliseconds || milliseconds <= 0) return 'Overdue'
  
  const totalSeconds = Math.floor(milliseconds / 1000)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

/**
 * Format complaint text for display
 * @param {string} text - The complaint text
 * @param {number} maxLength - Maximum length to display (default: 100)
 * @returns {string} Formatted complaint text
 */
export const formatComplaintText = (text, maxLength = 100) => {
  if (!text) return 'No description'
  return truncateText(text.trim(), maxLength)
}

/**
 * Get initials from name or ID
 * @param {string} str - The string to get initials from
 * @returns {string} Initials (up to 2 characters)
 */
export const getInitials = (str) => {
  if (!str) return '?'
  return str
    .split(' ')
    .slice(0, 2)
    .map(word => word[0])
    .join('')
    .toUpperCase()
}

/**
 * Capitalize first letter
 * @param {string} str - The string to capitalize
 * @returns {string} Capitalized string
 */
export const capitalize = (str) => {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

/**
 * Format status text for display
 * @param {string} status - The status string (e.g., 'IN_PROGRESS', 'sla_breaching')
 * @returns {string} Formatted status (e.g., 'In Progress', 'SLA Breaching')
 */
export const formatStatusText = (status) => {
  if (!status) return 'Unknown'
  return status
    .split('_')
    .map(word => capitalize(word))
    .join(' ')
}

/**
 * Get safe nested object value
 * @param {object} obj - The object to access
 * @param {string} path - Dot-notation path (e.g., 'user.profile.name')
 * @param {*} defaultValue - Default value if not found
 * @returns {*} The value or default
 */
export const getNestedValue = (obj, path, defaultValue = null) => {
  try {
    return path.split('.').reduce((current, prop) => current?.[prop], obj) ?? defaultValue
  } catch (e) {
    return defaultValue
  }
}

/**
 * Format SLA risk level with color coding
 * @param {string} risk - The risk level ('OK', 'WARNING', 'BREACHING')
 * @returns {object} Risk info with label and severity
 */
export const formatSLARisk = (risk) => {
  const riskMap = {
    OK: { label: 'On Track', severity: 'low', icon: '✓' },
    WARNING: { label: 'At Risk', severity: 'medium', icon: '⚠' },
    BREACHING: { label: 'Breached', severity: 'high', icon: '✕' }
  }
  return riskMap[risk] || riskMap.OK
}

export default {
  formatDate,
  formatRelativeDate,
  formatNumber,
  formatPercentage,
  truncateText,
  formatTimeRemaining,
  formatComplaintText,
  getInitials,
  capitalize,
  formatStatusText,
  getNestedValue,
  formatSLARisk
}
