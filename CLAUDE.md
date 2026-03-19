# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## App Name

**VibeFinQuant** — a full-stack financial analysis tool combining quantitative stock/ETF analysis with AI-powered insights via Google Gemini.

## Development Commands

### Backend (FastAPI, port 9001)
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 9001          # start
python -m uvicorn app.main:app --host 127.0.0.1 --port 9001 --reload # start with hot-reload
```
Requires `GEMINI_API_KEY` in `backend/.env`. Model defaults to `gemini-2.0-flash`.

### Frontend (React + Vite, port 5173)
```bash
cd frontend
npm run dev       # start dev server
npm run build     # production build
npm run lint      # ESLint
```

### Both at once
```bash
./run.sh    # starts backend + frontend, Ctrl+C to stop
./setup.sh  # first-time setup (venv, pip install, npm install, .env)
```

## Architecture

### Backend (`backend/app/`)

FastAPI app in `main.py` mounts all routes under `/api` prefix via `api/routes.py`. CORS allows any `localhost` port.

**Service layer** (all in `services/`):
- **YFinanceService** — all Yahoo Finance data: historical prices, fundamentals, ticker search (autocomplete API), ETF holdings (`funds_data.top_holdings`), ETF info, earnings transcripts (via `earningscall` library)
- **AnalyticsService** — deterministic financial calculations with Pandas/NumPy. Price normalization (Day 1 = 0%), 10 fundamental metrics (margins, ratios, ROIC, P/E), multi-ticker normalized comparison
- **LLMService** — Gemini integration. `summarize_earnings()` returns 8-section JSON for stocks; `summarize_etf()` returns a single paragraph. Includes JSON parsing with text-extraction fallback
- **TranscriptService** — YouTube transcript extraction via yt-dlp with disk caching (`transcript_cache/`), plus file upload validation

**Schemas** (`models/schemas.py`): Pydantic models for all request/response types. `LLMSynthesis` has 8 fixed string fields. `ETFAnalyzeResponse` uses a plain `summary` string instead. `CompareRequest`/`CompareResponse` use `Dict[str, float]` for dynamic N-ticker values.

### Frontend (`frontend/src/`)

Single-page React 18 app. State lives in `App.jsx` — no external state management.

**Key data flow:**
1. `SearchBar` fires debounced typeahead queries → `api.searchTickers()` → dropdown
2. User clicks Analyze → `App.handleAnalyze()` branches on `analysisMode` (stock / etf / comparison)
3. Stock: `api.analyzeStock()` → renders PriceChart + ComparisonChart + MetricsTable + LLMSynthesis
4. ETF: `api.analyzeETF()` → renders PriceChart + ComparisonChart + HoldingsTable + AI Insight paragraph
5. Comparison: `MultiTickerSearch` collects up to 10 tickers + period → `api.compareTickers()` → `MultiComparisonChart` (N-line Plotly chart with SPY baseline)
6. Transcript section (stock mode only): upload/YouTube → `api.processTranscript()` → LLMSynthesis

**API client** (`services/api.js`): Axios with no-cache headers and cache-busting `_t` param. Base URL from `VITE_API_URL` env var, defaults to `http://127.0.0.1:9001`.

**Styling**: Tailwind CSS. Components use `bg-white rounded-lg shadow p-6` card pattern consistently.

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/search?q=` | Ticker/company typeahead search |
| POST | `/api/analyze` | Full stock analysis (charts + metrics + LLM) |
| POST | `/api/analyze-etf` | ETF analysis (charts + holdings + summary) |
| POST | `/api/process-transcript` | Standalone transcript AI analysis |
| POST | `/api/transcript/upload` | Upload .txt transcript file |
| POST | `/api/transcript/youtube` | Extract transcript from YouTube URL |
| POST | `/api/compare` | Multi-ticker normalized return comparison |

## Key Conventions

- Stock mode uses the 8-section `LLMSynthesis` accordion; ETF mode uses a single summary paragraph — these are intentionally different
- The S&P 500 comparison always uses SPY as proxy (`get_sp500_prices()` calls `get_historical_prices("SPY")`)
- Ticker search hits Yahoo Finance autocomplete API directly (`query2.finance.yahoo.com/v1/finance/search`), not yfinance library
- ETF holdings come from `yf.Ticker(t).funds_data.top_holdings`, weights are multiplied by 100 for percentage display
- All financial calculations are deterministic (no randomness) — Pandas/NumPy only
- Comparison mode uses `MultiTickerSearch` (chip-based multi-select with period buttons) and `MultiComparisonChart` (dynamic N-line Plotly chart); SPY is always auto-included as a green dotted baseline
- Transcript section is hidden in ETF and comparison modes; only shown in stock mode
- `handleModeChange()` clears `results`, `etfResults`, and `compareResults` to reset the UI
