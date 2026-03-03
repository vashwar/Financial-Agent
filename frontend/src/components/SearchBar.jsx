import React, { useState } from 'react'

export default function SearchBar({ onAnalyze, isLoading }) {
  const [ticker, setTicker] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')

    if (!ticker.trim()) {
      setError('Please enter a stock ticker')
      return
    }

    if (ticker.length > 5) {
      setError('Ticker must be 5 characters or less')
      return
    }

    onAnalyze(ticker.trim())
  }

  return (
    <div className="w-full bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Financial Analysis Engine
        </h1>

        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={ticker}
            onChange={(e) => {
              setTicker(e.target.value.toUpperCase())
              setError('')
            }}
            placeholder="Enter stock ticker (e.g., AAPL)"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
            disabled={isLoading}
          />
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
