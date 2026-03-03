import React from 'react'
import Plot from 'react-plotly.js'

export default function ComparisonChart({ data, ticker, isLoading }) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 h-96 flex items-center justify-center">
        <div className="text-gray-500">Loading chart...</div>
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 h-96 flex items-center justify-center">
        <div className="text-gray-500">No data available</div>
      </div>
    )
  }

  const dates = data.map(d => d.date)
  const stockChanges = data.map(d => d.stock_change * 100) // Convert to percentage display
  const sp500Changes = data.map(d => d.sp500_change * 100) // Convert to percentage display

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">
        {ticker} vs S&P 500 - Normalized Comparison
      </h2>
      <p className="text-sm text-gray-600 mb-4">Both normalized to Day 1 = 0%</p>
      <Plot
        data={[
          {
            x: dates,
            y: stockChanges,
            mode: 'lines',
            line: { color: '#3B82F6', width: 2 },
            name: ticker,
            hovertemplate: '<b>%{fullData.name}</b><br>Date: %{x}<br>Change: %{y:+.2f}%<extra></extra>',
          },
          {
            x: dates,
            y: sp500Changes,
            mode: 'lines',
            line: { color: '#10B981', width: 2 },
            name: 'S&P 500',
            hovertemplate: '<b>%{fullData.name}</b><br>Date: %{x}<br>Change: %{y:+.2f}%<extra></extra>',
          }
        ]}
        layout={{
          title: '',
          xaxis: { title: 'Date', gridcolor: '#e5e7eb' },
          yaxis: { title: 'Percentage Change (%)', gridcolor: '#e5e7eb' },
          hovermode: 'x unified',
          plot_bgcolor: '#f9fafb',
          paper_bgcolor: '#ffffff',
          font: { family: 'system-ui, sans-serif', size: 12, color: '#6b7280' },
          legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255, 255, 255, 0.8)' },
          margin: { l: 60, r: 20, t: 20, b: 40 },
        }}
        style={{ width: '100%', height: '400px' }}
        responsive={true}
      />
    </div>
  )
}
