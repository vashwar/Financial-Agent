import React, { useState, useEffect, useRef, useCallback } from 'react'
import { searchTickers } from '../services/api'

const PERIOD_OPTIONS = [1, 2, 3, 5]

export default function MultiTickerSearch({ onCompare, isLoading }) {
  const [query, setQuery] = useState('')
  const [selectedTickers, setSelectedTickers] = useState([])
  const [years, setYears] = useState(5)
  const [suggestions, setSuggestions] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)
  const dropdownRef = useRef(null)
  const inputRef = useRef(null)
  const debounceRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const fetchSuggestions = useCallback(async (q) => {
    if (q.length < 2) {
      setSuggestions([])
      setShowDropdown(false)
      return
    }
    try {
      const data = await searchTickers(q)
      const filtered = (data.suggestions || []).filter(
        (s) => !selectedTickers.includes(s.symbol)
      )
      setSuggestions(filtered)
      setShowDropdown(filtered.length > 0)
    } catch {
      setSuggestions([])
      setShowDropdown(false)
    }
  }, [selectedTickers])

  const handleInputChange = (e) => {
    const value = e.target.value
    setQuery(value)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      fetchSuggestions(value.trim())
    }, 300)
  }

  const handleSelect = (suggestion) => {
    if (selectedTickers.length >= 10) return
    setSelectedTickers((prev) => [...prev, suggestion.symbol])
    setQuery('')
    setSuggestions([])
    setShowDropdown(false)
    inputRef.current?.focus()
  }

  const handleRemove = (ticker) => {
    setSelectedTickers((prev) => prev.filter((t) => t !== ticker))
  }

  const handleCompare = () => {
    if (selectedTickers.length === 0) return
    onCompare(selectedTickers, years)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="bg-white rounded-lg shadow p-6">
        {/* Selected ticker chips */}
        {selectedTickers.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {selectedTickers.map((t) => (
              <span
                key={t}
                className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
              >
                {t}
                <button
                  onClick={() => handleRemove(t)}
                  className="ml-1 text-blue-500 hover:text-blue-700 font-bold"
                  aria-label={`Remove ${t}`}
                >
                  &times;
                </button>
              </span>
            ))}
          </div>
        )}

        {/* Search input */}
        <div className="flex gap-3">
          <div className="relative flex-1" ref={dropdownRef}>
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={handleInputChange}
              placeholder={
                selectedTickers.length >= 10
                  ? 'Maximum 10 tickers reached'
                  : 'Search and add tickers (e.g., AAPL, MSFT, GOOGL)'
              }
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
              disabled={isLoading || selectedTickers.length >= 10}
              autoComplete="off"
            />

            {showDropdown && suggestions.length > 0 && (
              <ul className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-72 overflow-y-auto">
                {suggestions.map((s, idx) => (
                  <li
                    key={`${s.symbol}-${idx}`}
                    onClick={() => handleSelect(s)}
                    className="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                  >
                    <span className="font-semibold text-blue-700">{s.symbol}</span>
                    <span className="text-gray-600"> — {s.name}</span>
                    {s.exchange && (
                      <span className="text-gray-400 text-sm ml-2">({s.exchange})</span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Period selector + Compare button */}
        <div className="flex items-center gap-4 mt-4">
          <span className="text-sm font-medium text-gray-700">Period:</span>
          <div className="flex gap-1">
            {PERIOD_OPTIONS.map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => setYears(p)}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  years === p
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                } ${p === 1 ? 'rounded-l-lg' : ''} ${p === 5 ? 'rounded-r-lg' : ''}`}
              >
                {p}Y
              </button>
            ))}
          </div>

          <button
            type="button"
            onClick={handleCompare}
            disabled={isLoading || selectedTickers.length === 0}
            className="ml-auto px-8 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Comparing...' : 'Compare'}
          </button>
        </div>

        <p className="mt-3 text-xs text-gray-400">
          S&P 500 (SPY) is automatically included as a baseline. Up to 10 tickers.
        </p>
      </div>
    </div>
  )
}
