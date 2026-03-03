# Deterministic Strategic Analysis Engine (DSAE)

A full-stack financial analysis tool that combines quantitative stock analysis with AI-powered earnings call insights. Enter a stock ticker and get 5-year price history, S&P 500 comparison, 10+ financial metrics, and an AI-generated earnings call synthesis.

## Tech Stack

**Backend:** FastAPI, Python, Pandas, NumPy, yfinance, Google Gemini AI
**Frontend:** React 18, Vite, Plotly.js, Tailwind CSS, Axios

## Features

- **5-Year Price Chart** - Historical daily stock prices
- **S&P 500 Comparison** - Normalized performance comparison (Day 1 = 0%)
- **Financial Metrics** - Net Income, EBIT, EBITDA, FCF, Gross Margin, Operating Margin, D/E Ratio, Interest Coverage, ROIC, P/E Ratio
- **AI Earnings Synthesis** - 8-section structured analysis powered by Google Gemini
- **Transcript Input** - Upload a .txt transcript file or paste a YouTube earnings call link
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
│   │       ├── yfinance_service.py  # Stock data (yfinance)
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
│   │   │   ├── SearchBar.jsx
│   │   │   ├── PriceChart.jsx
│   │   │   ├── ComparisonChart.jsx
│   │   │   ├── MetricsTable.jsx
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
| `POST` | `/api/analyze` | Analyze a stock ticker |
| `POST` | `/api/transcript/upload` | Upload transcript file |
| `POST` | `/api/transcript/youtube` | Extract YouTube transcript |
| `POST` | `/api/process-transcript` | Process transcript with AI independently |
| `GET` | `/health` | Health check |

### Analyze Request

```json
POST /api/analyze
{
  "ticker": "AAPL",
  "transcript": "optional transcript text..."
}
```

### Analyze Response

```json
{
  "ticker": "AAPL",
  "price_chart_data": [
    {"date": "2024-01-02", "close": 185.64}
  ],
  "comparison_chart_data": [
    {"date": "2024-01-02", "stock_change": 0.0, "sp500_change": 0.0}
  ],
  "metrics": {
    "latest_net_income": 99803000000,
    "latest_ebit": 130000000000,
    "latest_gross_margin": 0.4619,
    "latest_operating_margin": 0.35,
    "latest_debt_to_equity": 1.2,
    "latest_interest_coverage": 32.9,
    "latest_roic": 0.28,
    "latest_pe_ratio": 33.5
  },
  "llm_synthesis": {
    "quarterly_performance": "...",
    "forward_guidance": "...",
    "challenges": "...",
    "positive_signs": "...",
    "analyst_qa_focus": "...",
    "strategic_initiatives": "...",
    "management_tone": "...",
    "conclusion": "..."
  }
}
```

### YouTube Transcript Request

```json
POST /api/transcript/youtube
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

## How It Works

1. **Data Ingestion** - Fetches 5 years of daily prices and quarterly fundamentals via yfinance
2. **Calculations** - All metrics computed deterministically with Pandas/NumPy (no randomness)
3. **Transcript** - User provides an earnings call transcript via file upload or YouTube link
4. **AI Analysis** - Google Gemini generates an 8-section structured synthesis combining the transcript with calculated metrics

### Financial Metrics

| Metric | Formula |
|--------|---------|
| Gross Margin | (Revenue - COGS) / Revenue |
| Operating Margin | EBIT / Revenue |
| Debt-to-Equity | Total Debt / Total Equity |
| Interest Coverage | EBIT / Interest Expense |
| ROIC | EBIT / (Total Debt + Total Equity) |
| P/E Ratio | Current Price / Trailing EPS |

### AI Synthesis Sections

1. Quarterly Performance
2. Forward Guidance
3. Challenges
4. Positive Signs
5. Analyst Q&A Focus
6. Strategic Initiatives & Capital Allocation
7. Management Tone
8. Conclusion

## Data Sources

- **Stock Data**: Yahoo Finance via yfinance (no API key required)
- **Earnings Transcripts**: YouTube (via yt-dlp) or file upload
- **LLM Analysis**: Google Gemini AI

## Notes

- YouTube transcript extraction uses yt-dlp with caching and proxy fallback
- Cached transcripts are served instantly on repeat access
- YouTube may rate-limit requests from certain IPs; file upload is always available as an alternative
- All financial calculations are strictly deterministic
- Returns are already in percentage form (not multiplied by 100)
