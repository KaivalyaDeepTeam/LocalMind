"""
Base LLM Provider Interface for CallScore Desktop

Production-ready architecture - configure API keys in Settings when ready.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


@dataclass
class MergeResult:
    """Result from transcript merging."""
    merged_transcript: str
    confidence: float = 1.0
    model_used: str = ""


@dataclass
class QualityParameter:
    """Individual quality parameter score."""
    name: str
    score: int
    max_score: int
    verdict: str  # "met", "partial", "not_met"
    evidence: str = ""


@dataclass
class AuditResult:
    """Result from call auditing."""
    total_score: int
    grade: str
    parameters: List[QualityParameter] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    has_zt_violation: bool = False
    has_ra_violation: bool = False
    zt_violations: List[Dict[str, Any]] = field(default_factory=list)
    ra_violations: List[Dict[str, Any]] = field(default_factory=list)
    overall_recommendation: str = ""
    model_used: str = ""


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    def __init__(self, api_key: str = "", model: str = ""):
        self._api_key = api_key
        self._model = model or self.default_model

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider display name."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model identifier."""
        pass

    @property
    def model(self) -> str:
        return self._model

    @property
    def is_configured(self) -> bool:
        """Check if API key is set (for cloud providers)."""
        return bool(self._api_key)

    @abstractmethod
    def merge_transcripts(
        self,
        whisper_v3_text: str,
        hindi2hinglish_text: str,
        audio_duration: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MergeResult:
        """Merge dual transcripts into single coherent transcript."""
        pass

    @abstractmethod
    def audit_call(
        self,
        transcript: str,
        audio_duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditResult:
        """Audit call transcript for quality scoring."""
        pass
