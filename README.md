# VibeFinQuant

A full-stack financial analysis tool that combines quantitative stock and ETF analysis with AI-powered insights. Search by company name or ticker, toggle between Stock and ETF modes, and get 5-year price history, S&P 500 comparison, financial metrics, holdings data, and AI-generated analysis.

## Tech Stack

**Backend:** FastAPI, Python, Pandas, NumPy, yfinance, Google Gemini AI
**Frontend:** React 18, Vite, Plotly.js, Tailwind CSS, Axios

## Features

- **Company Name Search** - Typeahead dropdown that searches Yahoo Finance as you type (works with tickers and company names)
- **Stock / ETF Toggle** - Switch between Stock and ETF analysis modes
- **5-Year Price Chart** - Historical daily prices
- **S&P 500 Comparison** - Normalized performance comparison (Day 1 = 0%)
- **Financial Metrics** (Stock mode) - Net Income, EBIT, EBITDA, FCF, Gross Margin, Operating Margin, D/E Ratio, Interest Coverage, ROIC, P/E Ratio
- **Top 10 Holdings** (ETF mode) - Table showing the ETF's top holdings with weights
- **AI Insight** (ETF mode) - Single-paragraph summary of what the ETF is known for and what index it tracks
- **AI Earnings Synthesis** (Stock mode) - 8-section structured analysis powered by Google Gemini
- **Transcript Input** (Stock mode) - Upload a .txt transcript file or paste a YouTube earnings call link
- **Process Transcript** - Independently analyze a transcript via Gemini AI without running full stock analysis

## Project Structure

```
FinancialAgent/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point
│   │   ├── api/routes.py            # API endpoints
│   │   ├── models/schemas.py        # Pydantic models
│   │   └── services/
│   │       ├── yfinance_service.py  # Stock/ETF data (yfinance)
│   │       ├── analytics.py         # Deterministic calculations
│   │       ├── llm_service.py       # Gemini integration
│   │       └── transcript_service.py # YouTube & file transcripts
│   ├── transcript_cache/            # Cached YouTube transcripts
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── SearchBar.jsx        # Typeahead search + Stock/ETF toggle
│   │   │   ├── PriceChart.jsx
│   │   │   ├── ComparisonChart.jsx
│   │   │   ├── MetricsTable.jsx
│   │   │   ├── HoldingsTable.jsx    # ETF top 10 holdings
│   │   │   ├── LLMSynthesis.jsx
│   │   │   └── TranscriptInput.jsx
│   │   └── services/api.js
│   ├── package.json
│   └── vite.config.js
├── setup.sh                         # One-time setup script
├── run.sh                           # Start the app
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Google Gemini API key

### 1. Setup

```bash
./setup.sh
```

This creates the Python virtual environment, installs all backend and frontend dependencies, and generates the `.env` file.

### 2. Configure API Key

Edit `backend/.env` and add your Gemini key:

```
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

### 3. Run

```bash
./run.sh
```

This starts both the backend (port 9001) and frontend (port 5173). Press `Ctrl+C` to stop.

Open http://localhost:5173 in your browser.

### Manual Setup (if not using scripts)

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 9001

# Frontend (in a separate terminal)
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/search?q=<query>` | Search tickers by company name or symbol |
| `POST` | `/api/analyze` | Analyze a stock ticker |
| `POST` | `/api/analyze-etf` | Analyze an ETF ticker |
| `POST` | `/api/transcript/upload` | Upload transcript file |
| `POST` | `/api/transcript/youtube` | Extract YouTube transcript |
| `POST` | `/api/process-transcript` | Process transcript with AI independently |
| `GET` | `/health` | Health check |

### Search Request

```
GET /api/search?q=apple
```

### Search Response

```json
{
  "query": "apple",
  "suggestions": [
    {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "quote_type": "EQUITY"}
  ]
}
```

### Analyze Stock Request

```json
POST /api/analyze
{
  "ticker": "AAPL",
  "transcript": "optional transcript text..."
}
```

### Analyze ETF Request

```json
POST /api/analyze-etf
{
  "ticker": "SPY"
}
```

### Analyze ETF Response

```json
{
  "ticker": "SPY",
  "name": "State Street SPDR S&P 500 ETF Trust",
  "price_chart_data": [...],
  "comparison_chart_data": [...],
  "holdings": [
    {"symbol": "NVDA", "name": "NVIDIA Corp", "weight": 7.83}
  ],
  "summary": "SPY tracks the S&P 500 index and is the largest ETF by AUM..."
}
```

## How It Works

1. **Search** - Typeahead queries Yahoo Finance autocomplete API as you type
2. **Data Ingestion** - Fetches 5 years of daily prices via yfinance; for stocks also fetches quarterly fundamentals
3. **Calculations** - All metrics computed deterministically with Pandas/NumPy (no randomness)
4. **ETF Holdings** - For ETFs, retrieves top 10 holdings with weights from yfinance funds data
5. **AI Analysis** - Google Gemini generates either an 8-section earnings synthesis (stocks) or a single-paragraph ETF summary

### Financial Metrics (Stock mode)

| Metric | Formula |
|--------|---------|
| Gross Margin | (Revenue - COGS) / Revenue |
| Operating Margin | EBIT / Revenue |
| Debt-to-Equity | Total Debt / Total Equity |
| Interest Coverage | EBIT / Interest Expense |
| ROIC | EBIT / (Total Debt + Total Equity) |
| P/E Ratio | Current Price / Trailing EPS |

### AI Synthesis Sections (Stock mode)

1. Quarterly Performance
2. Forward Guidance
3. Challenges
4. Positive Signs
5. Analyst Q&A Focus
6. Strategic Initiatives & Capital Allocation
7. Management Tone
8. Conclusion

## Data Sources

- **Stock & ETF Data**: Yahoo Finance via yfinance (no API key required)
- **Earnings Transcripts**: YouTube (via yt-dlp) or file upload
- **LLM Analysis**: Google Gemini AI

## Notes

- YouTube transcript extraction uses yt-dlp with caching and proxy fallback
- Cached transcripts are served instantly on repeat access
- YouTube may rate-limit requests from certain IPs; file upload is always available as an alternative
- All financial calculations are strictly deterministic
- Returns are already in percentage form (not multiplied by 100)
