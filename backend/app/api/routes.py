from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.schemas import (
    AnalyzeRequest, AnalyzeResponse, PricePoint,
    ComparisonDataPoint, MetricsData, LLMSynthesis,
    TranscriptUploadResponse, YouTubeTranscriptRequest, YouTubeTranscriptResponse,
    ProcessTranscriptRequest, ProcessTranscriptResponse
)
from app.services.yfinance_service import YFinanceService
from app.services.analytics import AnalyticsService
from app.services.llm_service import LLMService
from app.services.transcript_service import TranscriptService

router = APIRouter()


@router.get("/test-yfinance/{ticker}")
async def test_yfinance(ticker: str):
    """Test yfinance directly."""
    try:
        yf_service = YFinanceService()
        prices = yf_service.get_historical_prices(ticker)
        return {
            "status": "success",
            "ticker": ticker,
            "price_records": len(prices),
            "first_date": str(prices.iloc[0]["date"]),
            "last_date": str(prices.iloc[-1]["date"]),
            "sample_prices": prices.tail(3).to_dict("records")
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "type": type(e).__name__}


@router.post("/transcript/upload", response_model=TranscriptUploadResponse)
async def upload_transcript(file: UploadFile = File(...)) -> TranscriptUploadResponse:
    """
    Upload a transcript file (TXT format).

    Args:
        file: Text file containing transcript

    Returns:
        Transcript content and validation status
    """
    try:
        # Read the uploaded file
        content = await file.read()
        transcript_text = content.decode('utf-8')

        # Validate the transcript
        if TranscriptService.validate_transcript(transcript_text):
            return TranscriptUploadResponse(
                success=True,
                message="Transcript uploaded successfully",
                transcript=transcript_text,
                length=len(transcript_text)
            )
        else:
            return TranscriptUploadResponse(
                success=False,
                message="Transcript validation failed. Minimum 500 characters required.",
                length=len(transcript_text)
            )

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing transcript file: {str(e)}")


@router.post("/transcript/youtube", response_model=YouTubeTranscriptResponse)
async def get_youtube_transcript(request: YouTubeTranscriptRequest) -> YouTubeTranscriptResponse:
    """
    Extract transcript from a YouTube video URL.

    Args:
        request: YouTubeTranscriptRequest with youtube_url

    Returns:
        Transcript content and validation status
    """
    try:
        # Extract transcript from YouTube URL
        transcript = TranscriptService.get_youtube_transcript(request.youtube_url)

        if transcript and TranscriptService.validate_transcript(transcript):
            return YouTubeTranscriptResponse(
                success=True,
                message="Transcript extracted successfully from YouTube",
                transcript=transcript,
                length=len(transcript)
            )
        else:
            return YouTubeTranscriptResponse(
                success=False,
                message="Failed to extract transcript. YouTube may be rate-limiting requests from this IP. Please try again in a few minutes or use the file upload option instead."
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting YouTube transcript: {str(e)}")


@router.post("/process-transcript", response_model=ProcessTranscriptResponse)
async def process_transcript(request: ProcessTranscriptRequest) -> ProcessTranscriptResponse:
    """
    Process a transcript independently using Gemini AI.

    Takes raw transcript text and returns an 8-section AI synthesis
    without requiring a stock ticker or financial metrics.
    """
    try:
        llm = LLMService()
        synthesis_dict = llm.summarize_earnings(request.transcript, {})

        synthesis = LLMSynthesis(
            quarterly_performance=synthesis_dict.get("quarterly_performance", ""),
            forward_guidance=synthesis_dict.get("forward_guidance", ""),
            challenges=synthesis_dict.get("challenges", ""),
            positive_signs=synthesis_dict.get("positive_signs", ""),
            analyst_qa_focus=synthesis_dict.get("analyst_qa_focus", ""),
            strategic_initiatives=synthesis_dict.get("strategic_initiatives", ""),
            management_tone=synthesis_dict.get("management_tone", ""),
            conclusion=synthesis_dict.get("conclusion", ""),
        )

        return ProcessTranscriptResponse(success=True, synthesis=synthesis)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcript processing failed: {str(e)}")


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_stock(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze a stock ticker and return comprehensive financial analysis.

    Process:
    1. Fetch historical prices (stock + S&P 500)
    2. Calculate price charts data
    3. Fetch fundamentals
    4. Calculate all metrics
    5. Fetch earnings transcript
    6. Generate LLM summary
    """
    ticker = request.ticker.upper()

    try:
        # Initialize services
        yf_service = YFinanceService()
        analytics = AnalyticsService()
        llm = LLMService()

        # 1. Fetch historical prices
        stock_prices = yf_service.get_historical_prices(ticker)
        sp500_prices = yf_service.get_sp500_prices()

        # 2. Calculate price chart data (Chart 1: absolute prices)
        price_metrics = analytics.calculate_price_metrics(stock_prices)
        price_chart_data = [
            PricePoint(date=str(row["date"].date()), close=float(row["close"]))
            for _, row in price_metrics.iterrows()
        ]

        # 3. Calculate normalized comparison (Chart 2: % change)
        stock_normalized, sp500_normalized = analytics.calculate_normalized_comparison(
            stock_prices, sp500_prices
        )

        # Merge the normalized data
        merged_normalized = stock_normalized.merge(
            sp500_normalized,
            on="date",
            suffixes=("_stock", "_sp500")
        )

        comparison_chart_data = [
            ComparisonDataPoint(
                date=str(row["date"].date()),
                stock_change=float(row["percent_change_stock"]),
                sp500_change=float(row["percent_change_sp500"])
            )
            for _, row in merged_normalized.iterrows()
        ]

        # 4. Fetch fundamentals and calculate metrics
        fundamentals = yf_service.get_fundamentals(ticker)
        current_price = yf_service.get_current_price(ticker)

        # Get EPS for P/E ratio calculation
        eps_data = yf_service.get_eps_and_shares(ticker)
        eps = eps_data.get('eps')

        metrics_dict = analytics.calculate_fundamental_metrics(fundamentals, current_price, eps=eps)

        metrics = MetricsData(
            latest_net_income=metrics_dict.get("latest_net_income"),
            latest_ebit=metrics_dict.get("latest_ebit"),
            latest_ebitda=metrics_dict.get("latest_ebitda"),
            latest_fcf=metrics_dict.get("latest_fcf"),
            latest_debt_to_equity=metrics_dict.get("latest_debt_to_equity"),
            latest_interest_coverage=metrics_dict.get("latest_interest_coverage"),
            latest_gross_margin=metrics_dict.get("latest_gross_margin"),
            latest_operating_margin=metrics_dict.get("latest_operating_margin"),
            latest_roic=metrics_dict.get("latest_roic"),
            latest_pe_ratio=metrics_dict.get("latest_pe_ratio"),
            time_series=metrics_dict.get("time_series")
        )

        # 5. Get earnings transcript (use provided or fetch automatically)
        if request.transcript:
            # Use user-provided transcript
            transcript = request.transcript
        else:
            # Auto-fetch from earnings call
            transcript = yf_service.get_earnings_transcript(ticker)

        # 6. Generate LLM summary
        synthesis_dict = llm.summarize_earnings(transcript or "", metrics_dict)

        llm_synthesis = LLMSynthesis(
            quarterly_performance=synthesis_dict.get("quarterly_performance", ""),
            forward_guidance=synthesis_dict.get("forward_guidance", ""),
            challenges=synthesis_dict.get("challenges", ""),
            positive_signs=synthesis_dict.get("positive_signs", ""),
            analyst_qa_focus=synthesis_dict.get("analyst_qa_focus", ""),
            strategic_initiatives=synthesis_dict.get("strategic_initiatives", ""),
            management_tone=synthesis_dict.get("management_tone", ""),
            conclusion=synthesis_dict.get("conclusion", "")
        )

        return AnalyzeResponse(
            ticker=ticker,
            price_chart_data=price_chart_data,
            comparison_chart_data=comparison_chart_data,
            metrics=metrics,
            llm_synthesis=llm_synthesis
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
