# VibeFinQuant Backend

FastAPI-based backend for VibeFinQuant — quantitative financial analysis with AI-powered insights.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your API keys:
```bash
cp .env.example .env
# Edit .env with your GEMINI_API_KEY
```

4. Run the server:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 9001 --reload
```

The API will be available at `http://127.0.0.1:9001`

## API Endpoints

- `GET /health` — Health check
- `GET /api/search?q=` — Ticker/company typeahead search
- `POST /api/analyze` — Full stock analysis (charts + metrics + LLM)
- `POST /api/analyze-etf` — ETF analysis (charts + holdings + summary)
- `POST /api/compare` — Multi-ticker normalized return comparison
- `POST /api/process-transcript` — Standalone transcript AI analysis
- `POST /api/transcript/upload` — Upload .txt transcript file
- `POST /api/transcript/youtube` — Extract transcript from YouTube URL

## Project Structure

- `app/main.py` — FastAPI application entry point
- `app/api/routes.py` — API endpoint definitions
- `app/services/yfinance_service.py` — Yahoo Finance data integration
- `app/services/analytics.py` — Quantitative analysis calculations (price normalization, fundamental metrics, multi-ticker comparison)
- `app/services/llm_service.py` — Google Gemini LLM integration
- `app/services/transcript_service.py` — YouTube transcript extraction and file upload validation
- `app/models/schemas.py` — Pydantic request/response schemas
