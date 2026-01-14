"""
Anthropic LLM Provider for CallScore Desktop

Uses Claude models for merging and auditing.
Configure API key in Settings → LLM Provider when ready.
"""

import logging
from typing import Optional, Dict, Any

from desktop.llm.base_provider import (
    BaseLLMProvider,
    MergeResult,
    AuditResult,
    QualityParameter,
)

logger = logging.getLogger(__name__)


# Prompts for Anthropic (same logic as OpenAI, optimized for Claude)
MERGE_PROMPT = """You are an expert transcription merger. Given two transcripts of the same audio from different models, create a single accurate merged transcript.

TRANSCRIPT 1 (Whisper Large V3 - better for clear English):
{whisper_v3}

TRANSCRIPT 2 (Hindi2Hinglish - better for Hindi/English mixed speech):
{h2h}

Audio Duration: {duration:.1f} seconds

Instructions:
1. Identify speakers (Counselor/Caller)
2. Merge the best parts from both transcripts
3. Fix obvious transcription errors using context
4. Format as a clean conversation with speaker labels

Output the merged transcript only, no explanations."""

AUDIT_PROMPT = """You are a call quality auditor for sales calls. Analyze this transcript and provide a quality assessment.

TRANSCRIPT:
{transcript}

Rate the call on these parameters (score/max):
1. Call Opening (0-2)
2. Probing/Profiling (0-5)
3. Need Generated (0-5)
4. Product Justification (0-10)
5. Features & Benefits (0-8)
6. Information Accuracy (0-2)
7. Competitor Benchmarking (0-5)
8. Sales Driven (0-6)
9. Educator Credibility (0-10)
10. EMI Discussion (0-5)
11. Objection Handling (0-6)
12. Query Resolution (0-2)
13. Urgency Creation (0-5)
14. Communication (0-3)
15. Enthusiasm (0-5)
16. Referral Pitch (0-2)
17. Notes Quality (0-2)
18. Lead Stage (0-4)
19. Closing (0-5)
20. Up-Selling (0-3)
21. Call Control (0-5)

Provide JSON response:
{{
    "total_score": <0-100>,
    "grade": "<A/B/C/D/F>",
    "parameters": [
        {{"name": "...", "score": X, "max_score": Y, "verdict": "met|partial|not_met", "evidence": "..."}}
    ],
    "strengths": ["..."],
    "improvements": ["..."],
    "zt_violations": [],
    "ra_violations": [],
    "recommendation": "..."
}}"""


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic provider using Claude models.

    Set API key in Settings to enable.
    """

    AVAILABLE_MODELS = [
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514",
        "claude-3-5-sonnet-20241022",
    ]

    def __init__(self, api_key: str = "", model: str = ""):
        super().__init__(api_key, model)
        self._client = None

    @property
    def name(self) -> str:
        return "Anthropic"

    @property
    def default_model(self) -> str:
        return "claude-sonnet-4-20250514"

    def _get_client(self):
        """Lazy-load Anthropic client."""
        if self._client is None and self.is_configured:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self._api_key)
            except ImportError:
                logger.error("anthropic package not installed")
            except Exception as e:
                logger.error(f"Failed to create Anthropic client: {e}")
        return self._client

    def _call_claude(self, prompt: str, max_tokens: int = 4096) -> Optional[str]:
        """Make API call to Claude."""
        client = self._get_client()
        if client is None:
            return None

        try:
            response = client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return None

    def merge_transcripts(
        self,
        whisper_v3_text: str,
        hindi2hinglish_text: str,
        audio_duration: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MergeResult:
        """Merge transcripts using Claude."""

        if not self.is_configured:
            logger.info("Anthropic not configured, using Hindi2Hinglish transcript")
            return MergeResult(
                merged_transcript=hindi2hinglish_text,
                confidence=0.8,
                model_used="fallback",
            )

        prompt = MERGE_PROMPT.format(
            whisper_v3=whisper_v3_text,
            h2h=hindi2hinglish_text,
            duration=audio_duration,
        )

        result = self._call_claude(prompt, max_tokens=8192)

        if result:
            return MergeResult(
                merged_transcript=result,
                confidence=1.0,
                model_used=self._model,
            )

        return MergeResult(
            merged_transcript=hindi2hinglish_text,
            confidence=0.7,
            model_used="fallback",
        )

    def audit_call(
        self,
        transcript: str,
        audio_duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditResult:
        """Audit call using Claude."""

        if not self.is_configured:
            return self._placeholder_audit()

        prompt = AUDIT_PROMPT.format(transcript=transcript)
        result = self._call_claude(prompt, max_tokens=4096)

        if result:
            return self._parse_audit_response(result)

        return self._placeholder_audit("API call failed")

    def _parse_audit_response(self, response: str) -> AuditResult:
        """Parse Claude's JSON response into AuditResult."""
        import json

        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])

                parameters = [
                    QualityParameter(
                        name=p["name"],
                        score=p["score"],
                        max_score=p["max_score"],
                        verdict=p.get("verdict", "partial"),
                        evidence=p.get("evidence", ""),
                    )
                    for p in data.get("parameters", [])
                ]

                return AuditResult(
                    total_score=data.get("total_score", 0),
                    grade=data.get("grade", "N/A"),
                    parameters=parameters,
                    strengths=data.get("strengths", []),
                    improvements=data.get("improvements", []),
                    has_zt_violation=len(data.get("zt_violations", [])) > 0,
                    has_ra_violation=len(data.get("ra_violations", [])) > 0,
                    zt_violations=data.get("zt_violations", []),
                    ra_violations=data.get("ra_violations", []),
                    overall_recommendation=data.get("recommendation", ""),
                    model_used=self._model,
                )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse audit response: {e}")

        return self._placeholder_audit("Failed to parse response")

    def _placeholder_audit(self, error: str = "") -> AuditResult:
        """Return placeholder when API not available."""
        msg = error if error else "Configure Anthropic API key in Settings to enable auditing"
        return AuditResult(
            total_score=0,
            grade="N/A",
            parameters=[],
            strengths=[],
            improvements=[msg],
            overall_recommendation="Please configure an LLM provider to enable quality auditing.",
            model_used="none",
        )
