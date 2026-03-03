import React from 'react'

const formatValue = (value, type = 'default') => {
  if (value === null || value === undefined) {
    return 'N/A'
  }

  switch (type) {
    case 'currency':
      return `$${(value / 1e9).toFixed(2)}B`
    case 'percent':
      return `${(value * 100).toFixed(2)}%`
    case 'ratio':
      return value.toFixed(2)
    case 'pe':
      return value.toFixed(1)
    default:
      return value.toFixed(2)
  }
}

export default function MetricsTable({ metrics, ticker, isLoading }) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center text-gray-500">Loading metrics...</div>
      </div>
    )
  }

  if (!metrics) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center text-gray-500">No metrics available</div>
      </div>
    )
  }

  const metricsData = [
    {
      category: 'Income Statement',
      items: [
        { label: 'Net Income (Latest)', value: metrics.latest_net_income, type: 'currency' },
        { label: 'EBIT (Latest)', value: metrics.latest_ebit, type: 'currency' },
        { label: 'EBITDA (Latest)', value: metrics.latest_ebitda, type: 'currency' },
        { label: 'FCF (Latest)', value: metrics.latest_fcf, type: 'currency' },
      ]
    },
    {
      category: 'Profitability',
      items: [
        { label: 'Operating Margin', value: metrics.latest_operating_margin, type: 'percent' },
        { label: 'Gross Margin', value: metrics.latest_gross_margin, type: 'percent' },
        { label: 'ROIC', value: metrics.latest_roic, type: 'percent' },
      ]
    },
    {
      category: 'Leverage',
      items: [
        { label: 'Debt-to-Equity Ratio', value: metrics.latest_debt_to_equity, type: 'ratio' },
        { label: 'Interest Coverage', value: metrics.latest_interest_coverage, type: 'ratio' },
      ]
    },
    {
      category: 'Valuation',
      items: [
        { label: 'P/E Ratio', value: metrics.latest_pe_ratio, type: 'pe' },
      ]
    },
  ]

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-6">
        {ticker} - Quantitative Metrics
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {metricsData.map((section, idx) => (
          <div key={idx}>
            <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
              {section.category}
            </h3>
            <div className="space-y-3">
              {section.items.map((item, itemIdx) => (
                <div key={itemIdx} className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-gray-700">{item.label}</span>
                  <span className="font-semibold text-gray-900">
                    {formatValue(item.value, item.type)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 text-xs text-gray-500 italic">
        All values are for the most recent quarter. B = Billions, x = times
      </div>
    </div>
  )
}
