"""
OpenAI LLM Provider for CallScore Desktop

Wraps existing OpenAIMerger and SalesAuditor from core engine.
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


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI provider using GPT-4o/o1 models.

    Integrates with existing OpenAIMerger and SalesAuditor.
    Set API key in Settings to enable.
    """

    AVAILABLE_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "o1",
        "o1-mini",
    ]

    def __init__(self, api_key: str = "", model: str = ""):
        super().__init__(api_key, model)
        self._merger = None
        self._auditor = None

    @property
    def name(self) -> str:
        return "OpenAI"

    @property
    def default_model(self) -> str:
        return "gpt-4o"

    def _get_merger(self):
        """Lazy-load merger when API key is available."""
        if self._merger is None and self.is_configured:
            try:
                from src.merging.openai_merger import OpenAIMerger
                self._merger = OpenAIMerger(
                    api_key=self._api_key,
                    model=self._model,
                    thorough=True,
                )
            except Exception as e:
                logger.error(f"Failed to create OpenAI merger: {e}")
        return self._merger

    def _get_auditor(self):
        """Lazy-load auditor when API key is available."""
        if self._auditor is None and self.is_configured:
            try:
                from src.audit.sales_auditor import SalesAuditor
                self._auditor = SalesAuditor(
                    api_key=self._api_key,
                    model=self._model,
                )
            except Exception as e:
                logger.error(f"Failed to create OpenAI auditor: {e}")
        return self._auditor

    def merge_transcripts(
        self,
        whisper_v3_text: str,
        hindi2hinglish_text: str,
        audio_duration: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MergeResult:
        """Merge transcripts using OpenAI."""

        if not self.is_configured:
            # Return best available transcript when no API key
            logger.info("OpenAI not configured, using Hindi2Hinglish transcript")
            return MergeResult(
                merged_transcript=hindi2hinglish_text,
                confidence=0.8,
                model_used="fallback",
            )

        merger = self._get_merger()
        if merger is None:
            return MergeResult(
                merged_transcript=hindi2hinglish_text,
                confidence=0.8,
                model_used="fallback",
            )

        try:
            # Create a mock DualTranscriptResult for the merger
            from dataclasses import dataclass

            @dataclass
            class MockTranscript:
                text: str
                duration: float = 0.0

            @dataclass
            class MockDualResult:
                whisper_v3: MockTranscript
                hindi2hinglish: MockTranscript
                audio_path: str = ""
                total_time: float = 0.0

            dual_result = MockDualResult(
                whisper_v3=MockTranscript(whisper_v3_text, audio_duration),
                hindi2hinglish=MockTranscript(hindi2hinglish_text, audio_duration),
            )

            result = merger.merge(dual_result, metadata)

            return MergeResult(
                merged_transcript=result.final_transcript,
                confidence=1.0,
                model_used=self._model,
            )

        except Exception as e:
            logger.error(f"OpenAI merge failed: {e}")
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
        """Audit call using OpenAI."""

        if not self.is_configured:
            logger.info("OpenAI not configured, returning placeholder audit")
            return self._placeholder_audit()

        auditor = self._get_auditor()
        if auditor is None:
            return self._placeholder_audit()

        try:
            result = auditor.audit(
                transcript=transcript,
                call_duration=audio_duration,
                metadata=metadata,
            )

            # Convert to our format
            parameters = [
                QualityParameter(
                    name=p.name,
                    score=p.score,
                    max_score=p.max_score,
                    verdict=p.verdict.value if hasattr(p.verdict, 'value') else str(p.verdict),
                    evidence=p.evidence,
                )
                for p in result.quality.parameters
            ]

            return AuditResult(
                total_score=result.quality.total_score,
                grade=result.quality.grade,
                parameters=parameters,
                strengths=result.quality.strengths,
                improvements=result.quality.improvements,
                has_zt_violation=result.razt.has_zt_violation,
                has_ra_violation=result.razt.has_ra_violation,
                zt_violations=[
                    {"category": v.category, "evidence": v.evidence}
                    for v in result.razt.zt_violations
                ],
                ra_violations=[
                    {"category": v.category, "evidence": v.evidence}
                    for v in result.razt.ra_violations
                ],
                overall_recommendation=result.overall_recommendation,
                model_used=self._model,
            )

        except Exception as e:
            logger.error(f"OpenAI audit failed: {e}")
            return self._placeholder_audit(error=str(e))

    def _placeholder_audit(self, error: str = "") -> AuditResult:
        """Return placeholder when API not available."""
        msg = error if error else "Configure OpenAI API key in Settings to enable auditing"
        return AuditResult(
            total_score=0,
            grade="N/A",
            parameters=[],
            strengths=[],
            improvements=[msg],
            overall_recommendation="Please configure an LLM provider to enable quality auditing.",
            model_used="none",
        )
