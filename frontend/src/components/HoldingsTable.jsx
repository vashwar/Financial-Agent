import React from 'react'

export default function HoldingsTable({ holdings, ticker }) {
  if (!holdings || holdings.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Top Holdings — {ticker}
        </h2>
        <p className="text-gray-500">No holdings data available for this ETF.</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">
        Top 10 Holdings — {ticker}
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b-2 border-gray-200">
              <th className="py-3 px-4 text-sm font-semibold text-gray-600 w-12">#</th>
              <th className="py-3 px-4 text-sm font-semibold text-gray-600">Symbol</th>
              <th className="py-3 px-4 text-sm font-semibold text-gray-600">Name</th>
              <th className="py-3 px-4 text-sm font-semibold text-gray-600 text-right">Weight (%)</th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((h, idx) => (
              <tr
                key={h.symbol}
                className={idx % 2 === 0 ? 'bg-gray-50' : 'bg-white'}
              >
                <td className="py-3 px-4 text-sm text-gray-500">{idx + 1}</td>
                <td className="py-3 px-4 text-sm font-semibold text-blue-700">{h.symbol}</td>
                <td className="py-3 px-4 text-sm text-gray-800">{h.name}</td>
                <td className="py-3 px-4 text-sm text-gray-800 text-right font-mono">
                  {h.weight.toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
