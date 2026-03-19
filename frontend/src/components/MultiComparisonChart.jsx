import React from 'react'
import Plot from 'react-plotly.js'

const COLORS = [
  '#3B82F6', // blue
  '#EF4444', // red
  '#F59E0B', // amber
  '#8B5CF6', // violet
  '#EC4899', // pink
  '#14B8A6', // teal
  '#F97316', // orange
  '#6366F1', // indigo
  '#84CC16', // lime
  '#06B6D4', // cyan
  '#A855F7', // purple
  '#E11D48', // rose
]

export default function MultiComparisonChart({ data, tickers, years }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 h-96 flex items-center justify-center">
        <div className="text-gray-500">No comparison data available</div>
      </div>
    )
  }

  const dates = data.map((d) => d.date)

  // Build one trace per ticker
  const traces = tickers.map((ticker, i) => {
    const isSPY = ticker === 'SPY'
    return {
      x: dates,
      y: data.map((d) => (d.values[ticker] != null ? d.values[ticker] * 100 : null)),
      mode: 'lines',
      name: isSPY ? 'S&P 500 (SPY)' : ticker,
      line: {
        color: isSPY ? '#10B981' : COLORS[i % COLORS.length],
        width: isSPY ? 2 : 2.5,
        dash: isSPY ? 'dot' : 'solid',
      },
      hovertemplate:
        '<b>%{fullData.name}</b><br>Date: %{x}<br>Change: %{y:+.2f}%<extra></extra>',
    }
  })

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-2">
        Multi-Ticker Comparison — {years}Y Normalized Returns
      </h2>
      <p className="text-sm text-gray-600 mb-4">All normalized to Day 1 = 0%</p>
      <Plot
        data={traces}
        layout={{
          xaxis: { title: 'Date', gridcolor: '#e5e7eb' },
          yaxis: { title: 'Percentage Change (%)', gridcolor: '#e5e7eb' },
          hovermode: 'x unified',
          plot_bgcolor: '#f9fafb',
          paper_bgcolor: '#ffffff',
          font: { family: 'system-ui, sans-serif', size: 12, color: '#6b7280' },
          legend: { orientation: 'h', y: -0.2 },
          margin: { l: 60, r: 20, t: 10, b: 40 },
        }}
        style={{ width: '100%', height: '500px' }}
        config={{ responsive: true }}
      />
    </div>
  )
}
