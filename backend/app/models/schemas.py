from pydantic import BaseModel
from typing import List, Dict, Any, Optional


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
