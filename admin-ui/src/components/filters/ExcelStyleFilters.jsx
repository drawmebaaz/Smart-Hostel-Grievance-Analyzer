// components/filters/ExcelStyleFilters.jsx
import React, { useState, useEffect, useRef } from 'react'
import { Filter, X, ChevronDown, Search, Check } from 'lucide-react'

export default function ExcelStyleFilters({ issues = [], onFiltersChange }) {
  const [isOpen, setIsOpen] = useState(false)
  const [activeFilter, setActiveFilter] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filters, setFilters] = useState({
    priority: [],
    severity: [],
    health: [],
    category: [],
    hostel: [],
    slaStatus: []
  })

  const filterPanelRef = useRef(null)
  const filterButtonRef = useRef(null)
  const searchInputRef = useRef(null)

  /* -------------------- Close on Outside Click -------------------- */
  useEffect(() => {
    function handleClickOutside(event) {
      if (
        filterPanelRef.current &&
        !filterPanelRef.current.contains(event.target) &&
        filterButtonRef.current &&
        !filterButtonRef.current.contains(event.target)
      ) {
        setIsOpen(false)
        setActiveFilter(null)
        setSearchTerm('')
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  /* -------------------- Auto Focus Search -------------------- */
  useEffect(() => {
    if (activeFilter && searchInputRef.current) {
      searchInputRef.current.focus()
    }
  }, [activeFilter])

  /* -------------------- Filter Metadata -------------------- */
  const filterCategories = [
    { key: 'priority', label: 'Priority', icon: '⚡', color: 'from-purple-500/20 to-purple-600/20' },
    { key: 'severity', label: 'Severity', icon: '⚠️', color: 'from-orange-500/20 to-orange-600/20' },
    { key: 'health', label: 'Health', icon: '❤️', color: 'from-green-500/20 to-green-600/20' },
    { key: 'category', label: 'Category', icon: '📋', color: 'from-blue-500/20 to-blue-600/20' },
    { key: 'hostel', label: 'Hostel', icon: '🏠', color: 'from-cyan-500/20 to-cyan-600/20' },
    { key: 'slaStatus', label: 'SLA Status', icon: '⏰', color: 'from-red-500/20 to-red-600/20' }
  ]

  /* -------------------- Helpers -------------------- */
  const getUniqueValues = (key) => {
    if (!issues.length) return []

    const values = new Set()

    issues.forEach(issue => {
      let value
      switch (key) {
        case 'priority': value = issue.priority?.label; break
        case 'severity': value = issue.severity?.label; break
        case 'health': value = issue.health?.label; break
        case 'category': value = issue.category; break
        case 'hostel': value = issue.hostel; break
        case 'slaStatus': value = issue.sla?.risk; break
        default: return
      }
      if (value) values.add(value)
    })

    return [...values].sort()
  }

  const getFilterValues = () => {
    if (!activeFilter) return []

    const allValues = getUniqueValues(activeFilter)
    if (!searchTerm) return allValues

    return allValues.filter(v =>
      v.toLowerCase().includes(searchTerm.toLowerCase())
    )
  }

  /* -------------------- Actions -------------------- */
  const handleFilterToggle = (key) => {
    setActiveFilter(prev => (prev === key ? null : key))
    setSearchTerm('')
  }

  const handleValueToggle = (value, e) => {
    e.stopPropagation()
    if (!activeFilter) return

    setFilters(prev => {
      const current = prev[activeFilter]
      const exists = current.includes(value)
      const newFilters = {
        ...prev,
        [activeFilter]: exists
          ? current.filter(v => v !== value)
          : [...current, value]
      }
      
      // Immediately notify parent of filter change
      onFiltersChange(newFilters)
      return newFilters
    })
  }

  const handleSelectAll = (e) => {
    e.stopPropagation()
    if (!activeFilter) return

    const allValues = getUniqueValues(activeFilter)
    const newFilters = {
      ...filters,
      [activeFilter]: allValues
    }
    
    setFilters(newFilters)
    onFiltersChange(newFilters)
  }

  const handleSelectNone = (e) => {
    e.stopPropagation()
    if (!activeFilter) return

    const newFilters = {
      ...filters,
      [activeFilter]: []
    }
    
    setFilters(newFilters)
    onFiltersChange(newFilters)
  }

  const handleApplyFilters = () => {
    onFiltersChange(filters)
    setIsOpen(false)
    setActiveFilter(null)
    setSearchTerm('')
  }

  const handleClearAllFilters = () => {
    const empty = {
      priority: [],
      severity: [],
      health: [],
      category: [],
      hostel: [],
      slaStatus: []
    }
    setFilters(empty)
    onFiltersChange(empty)
    setIsOpen(false)
    setActiveFilter(null)
    setSearchTerm('')
  }

  const handleRemoveFilter = (key, value) => {
    const newFilters = {
      ...filters,
      [key]: filters[key].filter(v => v !== value)
    }
    
    setFilters(newFilters)
    onFiltersChange(newFilters)
  }

  const getFilterDisplayText = (key) => {
    const selected = filters[key].length
    const total = getUniqueValues(key).length
    if (selected === 0) return 'All'
    if (selected === total) return 'All selected'
    return `${selected} selected`
  }

  const activeFilterCount = Object.values(filters).reduce(
    (sum, arr) => sum + arr.length,
    0
  )

  const handleKeyDown = (e, value) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleValueToggle(value, e)
    }
  }

  /* -------------------- UI -------------------- */
  return (
    <div className="relative">
      {/* Filter Button */}
      <button
        ref={filterButtonRef}
        onClick={() => setIsOpen(prev => !prev)}
        className={`
          flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium border transition-all
          ${activeFilterCount
            ? 'bg-blue-500/20 border-blue-400/50 text-blue-300'
            : 'bg-white/10 border-white/20 text-white/90'
          }
          hover:bg-blue-500/30 hover:border-blue-400/70
          hover:scale-[1.02]
        `}
      >
        <Filter className="w-4 h-4" />
        Filter
        {activeFilterCount > 0 && (
          <span className="px-2 py-0.5 text-xs bg-blue-500/40 rounded-full">
            {activeFilterCount}
          </span>
        )}
        <ChevronDown className={`w-4 h-4 transition ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Filter Panel */}
      {isOpen && (
        <div
          ref={filterPanelRef}
          className="absolute top-full right-0 mt-2 w-96 bg-slate-800 border border-white/20 rounded-lg shadow-xl z-50"
        >
          {/* Header */}
          <div className="flex justify-between items-center px-4 py-3 border-b border-white/10">
            <h3 className="font-semibold text-white">Filter Issues</h3>
            {activeFilterCount > 0 && (
              <button
                onClick={handleClearAllFilters}
                className="text-xs text-white/70 hover:text-white"
              >
                Clear all
              </button>
            )}
          </div>

          {/* Body */}
          <div className="p-4">
            {/* Categories */}
            <div className="grid grid-cols-2 gap-2 mb-4">
              {filterCategories.map(cat => (
                <button
                  key={cat.key}
                  onClick={() => handleFilterToggle(cat.key)}
                  className={`p-3 rounded-lg border text-center ${
                    activeFilter === cat.key
                      ? 'border-blue-400 bg-blue-500/20'
                      : 'border-white/10 bg-white/5'
                  }`}
                >
                  <div className="text-2xl">{cat.icon}</div>
                  <div className="text-xs mt-1">{cat.label}</div>
                  <div className="text-xs opacity-60">
                    {getFilterDisplayText(cat.key)}
                  </div>
                </button>
              ))}
            </div>

            {/* Values */}
            {activeFilter && (
              <>
                <div className="flex justify-between mb-2">
                  <button onClick={handleSelectAll} className="text-xs hover:text-blue-400 transition-colors">
                    Select all
                  </button>
                  <button onClick={handleSelectNone} className="text-xs hover:text-red-400 transition-colors">
                    Clear
                  </button>
                </div>

                <input
                  ref={searchInputRef}
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  placeholder="Search..."
                  className="w-full mb-2 px-3 py-2 bg-white/5 border border-white/10 rounded text-white placeholder-white/50 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />

                <div className="max-h-48 overflow-y-auto border border-white/10 rounded">
                  {getFilterValues().map(value => {
                    const selected = filters[activeFilter].includes(value)
                    return (
                      <div
                        key={value}
                        tabIndex={0}
                        onClick={(e) => handleValueToggle(value, e)}
                        onKeyDown={(e) => handleKeyDown(e, value)}
                        className={`px-4 py-2 cursor-pointer flex gap-2 items-center ${
                          selected 
                            ? 'bg-blue-500/20 text-blue-300' 
                            : 'hover:bg-white/10 text-white'
                        }`}
                      >
                        {selected && <Check className="w-4 h-4 flex-shrink-0" />}
                        <span className={`${selected ? 'font-medium' : ''}`}>{value}</span>
                      </div>
                    )
                  })}
                </div>
              </>
            )}

            {/* Apply */}
            <button
              onClick={handleApplyFilters}
              disabled={!activeFilterCount}
              className="mt-4 w-full py-2 rounded bg-blue-500 hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium text-white"
            >
              Apply Filters
            </button>
          </div>
        </div>
      )}

      {/* Active Filter Chips */}
      {activeFilterCount > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {Object.entries(filters).map(([key, values]) =>
            values.map(v => (
              <span
                key={`${key}-${v}`}
                className="px-3 py-1 bg-blue-500/20 rounded-full flex items-center gap-2 text-sm"
              >
                <span className="text-white/70 text-xs">{filterCategories.find(f => f.key === key)?.icon}</span>
                <span className="text-white">{v}</span>
                <button 
                  onClick={() => handleRemoveFilter(key, v)}
                  className="hover:bg-white/20 rounded-full p-0.5 transition-colors"
                >
                  <X className="w-3 h-3 text-white/70 hover:text-white" />
                </button>
              </span>
            ))
          )}
        </div>
      )}
    </div>
  )
}