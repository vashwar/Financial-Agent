# VibeFinQuant Frontend

React-based frontend for VibeFinQuant — quantitative financial analysis with AI-powered insights.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Build

To build for production:
```bash
npm run build
```

## Project Structure

- `src/App.jsx` — Main application component (state management, mode routing)
- `src/components/`
  - `SearchBar.jsx` — Ticker input with typeahead + Stock/ETF/Comparison mode toggle
  - `PriceChart.jsx` — 5-year absolute price chart
  - `ComparisonChart.jsx` — Single-ticker normalized comparison vs S&P 500
  - `MultiTickerSearch.jsx` — Multi-select typeahead with chips + period selector (Comparison mode)
  - `MultiComparisonChart.jsx` — N-line normalized return chart with dynamic colors (Comparison mode)
  - `MetricsTable.jsx` — Quantitative metrics display
  - `HoldingsTable.jsx` — ETF top holdings table
  - `LLMSynthesis.jsx` — Earnings call AI analysis accordion
  - `TranscriptInput.jsx` — Transcript upload/YouTube input
- `src/services/api.js` — Backend API integration (Axios)

## Configuration

The frontend connects to the backend at `http://127.0.0.1:9001` by default.
Set the `VITE_API_URL` environment variable to override.

## Dependencies

- React 18
- Plotly.js for charting
- Axios for API calls
- Tailwind CSS for styling
