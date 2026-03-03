import React from 'react'
import Plot from 'react-plotly.js'

export default function PriceChart({ data, ticker, isLoading }) {
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
  const prices = data.map(d => d.close)

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">
        {ticker} - 5 Year Price History
      </h2>
      <Plot
        data={[
          {
            x: dates,
            y: prices,
            mode: 'lines',
            line: { color: '#3B82F6', width: 2 },
            fill: 'tozeroy',
            fillcolor: 'rgba(59, 130, 246, 0.1)',
            name: ticker,
            hovertemplate: '<b>%{fullData.name}</b><br>Date: %{x}<br>Price: $%{y:,.2f}<extra></extra>',
          }
        ]}
        layout={{
          title: '',
          xaxis: { title: 'Date', gridcolor: '#e5e7eb' },
          yaxis: { title: 'Price ($)', gridcolor: '#e5e7eb' },
          hovermode: 'x unified',
          plot_bgcolor: '#f9fafb',
          paper_bgcolor: '#ffffff',
          font: { family: 'system-ui, sans-serif', size: 12, color: '#6b7280' },
          margin: { l: 60, r: 20, t: 20, b: 40 },
        }}
        style={{ width: '100%', height: '400px' }}
        responsive={true}
      />
    </div>
  )
}
