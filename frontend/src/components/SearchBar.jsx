import React, { useState, useEffect, useRef, useCallback } from 'react'
import { searchTickers } from '../services/api'

export default function SearchBar({ onAnalyze, isLoading, analysisMode, onModeChange }) {
  const [ticker, setTicker] = useState('')
  const [error, setError] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)
  const dropdownRef = useRef(null)
  const inputRef = useRef(null)
  const debounceRef = useRef(null)

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const fetchSuggestions = useCallback(async (query) => {
    if (query.length < 2) {
      setSuggestions([])
      setShowDropdown(false)
      return
    }
    try {
      const data = await searchTickers(query)
      setSuggestions(data.suggestions || [])
      setShowDropdown(data.suggestions?.length > 0)
    } catch {
      setSuggestions([])
      setShowDropdown(false)
    }
  }, [])

  const handleInputChange = (e) => {
    const value = e.target.value
    setTicker(value)
    setError('')

    // Debounced search
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      fetchSuggestions(value.trim())
    }, 300)
  }

  const handleSelectSuggestion = (suggestion) => {
    setTicker(suggestion.symbol)
    setSuggestions([])
    setShowDropdown(false)
    inputRef.current?.focus()
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    setShowDropdown(false)

    if (!ticker.trim()) {
      setError('Please enter a ticker symbol')
      return
    }

    onAnalyze(ticker.trim().toUpperCase())
  }

  const placeholder = analysisMode === 'etf'
    ? 'Enter ETF ticker or name (e.g., SPY or S&P 500)'
    : 'Enter ticker or company name (e.g., AAPL or Apple)'

  return (
    <div className="w-full bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          VibeFinQuant
        </h1>

        {/* Stock / ETF Toggle */}
        <div className="flex gap-1 mb-4">
          <button
            type="button"
            onClick={() => onModeChange('stock')}
            className={`px-5 py-2 rounded-l-lg font-medium text-sm transition-colors ${
              analysisMode === 'stock'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Stock
          </button>
          <button
            type="button"
            onClick={() => onModeChange('etf')}
            className={`px-5 py-2 rounded-r-lg font-medium text-sm transition-colors ${
              analysisMode === 'etf'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            ETF
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex gap-3">
          <div className="relative flex-1" ref={dropdownRef}>
            <input
              ref={inputRef}
              type="text"
              value={ticker}
              onChange={handleInputChange}
              placeholder={placeholder}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
              disabled={isLoading}
              autoComplete="off"
            />

            {/* Typeahead dropdown */}
            {showDropdown && suggestions.length > 0 && (
              <ul className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-72 overflow-y-auto">
                {suggestions.map((s, idx) => (
                  <li
                    key={`${s.symbol}-${idx}`}
                    onClick={() => handleSelectSuggestion(s)}
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

          <button
            type="submit"
            disabled={isLoading}
            className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Analyzing...' : 'Analyze'}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}
      </div>
    </div>
  )
}
