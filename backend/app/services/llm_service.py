import os
import json
from typing import Dict, Any, Optional
import google.generativeai as genai


class LLMService:
    """Gemini LLM integration for earnings call analysis."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in environment variables")

        genai.configure(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.model = genai.GenerativeModel(model_name)

    def summarize_earnings(self, transcript: str, metrics: Dict[str, Any]) -> Dict[str, str]:
        """
        Analyze earnings call transcript and generate structured summary.

        Args:
            transcript: Raw earnings call transcript text
            metrics: Dictionary of calculated financial metrics

        Returns:
            Dictionary with 8 sections of structured analysis
        """
        if not transcript:
            return self._default_synthesis()

        # Format metrics for inclusion in prompt
        metrics_str = self._format_metrics(metrics)

        # Construct detailed prompt
        prompt = f"""You are a financial analyst reviewing an earnings call transcript.
Analyze the provided transcript and metrics, then provide a structured analysis in exactly 8 sections.

EARNINGS CALL TRANSCRIPT:
{transcript[:5000]}...

FINANCIAL METRICS:
{metrics_str}

Please provide a structured analysis with the following EXACT 8 sections. Each section should be 2-3 sentences.

1. Quarterly Performance - Key results and how they compare to expectations
2. Forward Guidance - Management's outlook and guidance for future quarters
3. Challenges - Key challenges and risks mentioned by management
4. Positive Signs - Positive indicators and opportunities discussed
5. Analyst Q&A Focus - What analysts focused on during Q&A
6. Strategic Initiatives & Capital Allocation - New initiatives and capital spending plans
7. Management Tone - Overall tone (optimistic, cautious, defensive, etc.)
8. Conclusion - Key takeaway for investors

Format your response as JSON with keys: quarterly_performance, forward_guidance, challenges, positive_signs, analyst_qa_focus, strategic_initiatives, management_tone, conclusion"""

        try:
            response = self.model.generate_content(prompt)
            return self._parse_llm_response(response.text)
        except Exception as e:
            print(f"LLM Service Error: {str(e)}")
            return self._default_synthesis()

    def summarize_etf(self, ticker: str, holdings: list, etf_info: Dict[str, Any]) -> str:
        """
        Generate a single-paragraph AI summary for an ETF.

        Returns a plain string describing what the ETF is known for
        and whether it tracks a specific index.
        """
        holdings_str = ", ".join(
            f"{h['symbol']} ({h['weight']}%)"
            for h in holdings[:5]
        ) or "N/A"

        prompt = f"""Write a single concise paragraph (3-5 sentences) about the ETF "{ticker}" ({etf_info.get('name', ticker)}).

Category: {etf_info.get('category', 'N/A')}
Top holdings: {holdings_str}

Explain what this ETF is known for, what index it tracks (if any), and its general investment strategy. Keep it simple and informative. Return ONLY the paragraph text, no headings or formatting."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"LLM ETF Service Error: {str(e)}")
            return f"Summary unavailable for {ticker}."

    @staticmethod
    def _format_metrics(metrics: Dict[str, Any]) -> str:
        """Format metrics dictionary for prompt injection."""
        lines = []

        if "latest_net_income" in metrics:
            lines.append(f"Net Income (Latest): ${metrics['latest_net_income']:,.0f}")

        if "latest_ebit" in metrics:
            lines.append(f"EBIT (Latest): ${metrics['latest_ebit']:,.0f}")

        if "latest_ebitda" in metrics:
            lines.append(f"EBITDA (Latest): ${metrics['latest_ebitda']:,.0f}")

        if "latest_operating_margin" in metrics:
            margin = metrics['latest_operating_margin'] * 100
            lines.append(f"Operating Margin (Latest): {margin:.2f}%")

        if "latest_debt_to_equity" in metrics:
            lines.append(f"Debt-to-Equity Ratio (Latest): {metrics['latest_debt_to_equity']:.2f}")

        if "latest_interest_coverage" in metrics:
            lines.append(f"Interest Coverage (Latest): {metrics['latest_interest_coverage']:.2f}x")

        if "latest_pe_ratio" in metrics:
            lines.append(f"P/E Ratio (Latest): {metrics['latest_pe_ratio']:.2f}")

        if "latest_roic" in metrics:
            roic = metrics['latest_roic'] * 100
            lines.append(f"ROIC (Latest): {roic:.2f}%")

        return "\n".join(lines) if lines else "No metrics available"

    @staticmethod
    def _parse_llm_response(response_text: str) -> Dict[str, str]:
        """
        Parse LLM response. Attempt JSON parsing first, then fallback to text extraction.
        """
        # Try JSON parsing
        try:
            # Find JSON block in response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed = json.loads(json_str)

                # Helper function to extract text value
                def get_value(val):
                    if isinstance(val, dict):
                        # Try different key names
                        if 'text' in val:
                            return val['text']
                        elif 'summary' in val:
                            return val['summary']
                        elif 'content' in val:
                            return val['content']
                        else:
                            # Return the dict as string if no known keys
                            return str(val)
                    elif isinstance(val, str):
                        return val
                    else:
                        return str(val) if val else ""

                # Map to expected keys
                return {
                    "quarterly_performance": get_value(parsed.get("quarterly_performance", "")),
                    "forward_guidance": get_value(parsed.get("forward_guidance", "")),
                    "challenges": get_value(parsed.get("challenges", "")),
                    "positive_signs": get_value(parsed.get("positive_signs", "")),
                    "analyst_qa_focus": get_value(parsed.get("analyst_qa_focus", "")),
                    "strategic_initiatives": get_value(parsed.get("strategic_initiatives", "")),
                    "management_tone": get_value(parsed.get("management_tone", "")),
                    "conclusion": get_value(parsed.get("conclusion", ""))
                }
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

        # Fallback: extract sections from text
        return LLMService._extract_sections_from_text(response_text)

    @staticmethod
    def _extract_sections_from_text(text: str) -> Dict[str, str]:
        """Extract sections from text response if JSON parsing fails."""
        sections = {
            "quarterly_performance": "",
            "forward_guidance": "",
            "challenges": "",
            "positive_signs": "",
            "analyst_qa_focus": "",
            "strategic_initiatives": "",
            "management_tone": "",
            "conclusion": ""
        }

        section_keywords = [
            ("quarterly_performance", ["1.", "Quarterly Performance"]),
            ("forward_guidance", ["2.", "Forward Guidance"]),
            ("challenges", ["3.", "Challenges"]),
            ("positive_signs", ["4.", "Positive Signs"]),
            ("analyst_qa_focus", ["5.", "Analyst Q&A"]),
            ("strategic_initiatives", ["6.", "Strategic Initiatives"]),
            ("management_tone", ["7.", "Management Tone"]),
            ("conclusion", ["8.", "Conclusion"])
        ]

        for key, keywords in section_keywords:
            for keyword in keywords:
                idx = text.find(keyword)
                if idx >= 0:
                    # Get text after keyword, up to next section
                    start = idx + len(keyword)
                    end = len(text)

                    # Find next section marker
                    for _, next_keywords in section_keywords:
                        for next_keyword in next_keywords:
                            next_idx = text.find(next_keyword, start)
                            if next_idx > start and next_idx < end:
                                end = next_idx

                    sections[key] = text[start:end].strip()
                    break

        # If sections are empty/dict format, provide defaults
        for key in sections:
            if isinstance(sections[key], dict):
                if 'text' in sections[key]:
                    sections[key] = sections[key]['text']
                elif 'summary' in sections[key]:
                    sections[key] = sections[key]['summary']
                elif 'content' in sections[key]:
                    sections[key] = sections[key]['content']
                else:
                    sections[key] = str(sections[key])
            elif not isinstance(sections[key], str):
                sections[key] = str(sections[key]) if sections[key] else ""

        return sections

    @staticmethod
    def _default_synthesis() -> Dict[str, str]:
        """Return default synthesis when transcript is unavailable."""
        return {
            "quarterly_performance": "Transcript data not available for analysis.",
            "forward_guidance": "Unable to assess forward guidance without transcript.",
            "challenges": "Transcript unavailable for challenges analysis.",
            "positive_signs": "Transcript unavailable for identifying positive signals.",
            "analyst_qa_focus": "Q&A transcript data unavailable.",
            "strategic_initiatives": "Strategic information not available.",
            "management_tone": "Unable to assess tone without transcript.",
            "conclusion": "Unable to provide comprehensive analysis without earnings transcript."
        }
