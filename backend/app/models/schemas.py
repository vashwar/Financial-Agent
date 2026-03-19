from pydantic import BaseModel, field_validator
from typing import List, Dict, Any, Optional, Literal


class AnalyzeRequest(BaseModel):
    ticker: str
    transcript: Optional[str] = None  # Optional user-provided transcript


class PricePoint(BaseModel):
    date: str
    close: float


class ComparisonDataPoint(BaseModel):
    date: str
    stock_change: float  # percentage change
    sp500_change: float  # percentage change


class MetricsData(BaseModel):
    latest_net_income: Optional[float] = None
    latest_ebit: Optional[float] = None
    latest_ebitda: Optional[float] = None
    latest_fcf: Optional[float] = None
    latest_debt_to_equity: Optional[float] = None
    latest_interest_coverage: Optional[float] = None
    latest_gross_margin: Optional[float] = None
    latest_operating_margin: Optional[float] = None
    latest_roic: Optional[float] = None
    latest_pe_ratio: Optional[float] = None
    time_series: Optional[Dict[str, Any]] = None


class LLMSynthesis(BaseModel):
    quarterly_performance: str
    forward_guidance: str
    challenges: str
    positive_signs: str
    analyst_qa_focus: str
    strategic_initiatives: str
    management_tone: str
    conclusion: str


class AnalyzeResponse(BaseModel):
    ticker: str
    price_chart_data: List[PricePoint]
    comparison_chart_data: List[ComparisonDataPoint]
    metrics: MetricsData
    llm_synthesis: LLMSynthesis


class TranscriptUploadResponse(BaseModel):
    success: bool
    message: str
    transcript: Optional[str] = None
    length: Optional[int] = None


class YouTubeTranscriptRequest(BaseModel):
    youtube_url: str


class YouTubeTranscriptResponse(BaseModel):
    success: bool
    message: str
    transcript: Optional[str] = None
    length: Optional[int] = None


class ProcessTranscriptRequest(BaseModel):
    transcript: str


class ProcessTranscriptResponse(BaseModel):
    success: bool
    synthesis: LLMSynthesis


# --- Search schemas ---

class SearchSuggestion(BaseModel):
    symbol: str
    name: str
    exchange: str
    quote_type: str


class SearchResponse(BaseModel):
    query: str
    suggestions: List[SearchSuggestion]


# --- ETF schemas ---

class ETFHolding(BaseModel):
    symbol: str
    name: str
    weight: float


class ETFAnalyzeRequest(BaseModel):
    ticker: str


class ETFAnalyzeResponse(BaseModel):
    ticker: str
    name: str
    price_chart_data: List[PricePoint]
    comparison_chart_data: List[ComparisonDataPoint]
    holdings: List[ETFHolding]
    summary: str


# --- Comparison schemas ---

class CompareRequest(BaseModel):
    tickers: List[str]
    years: Literal[1, 2, 3, 5] = 5

    @field_validator("tickers")
    @classmethod
    def validate_tickers(cls, v):
        if len(v) < 1 or len(v) > 10:
            raise ValueError("Must provide between 1 and 10 tickers")
        return [t.upper() for t in v]


class CompareSeriesPoint(BaseModel):
    date: str
    values: Dict[str, float]


class CompareResponse(BaseModel):
    tickers: List[str]
    years: int
    data: List[CompareSeriesPoint]
