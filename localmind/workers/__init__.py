"""LocalMind background worker threads."""

from localmind.workers.base import BaseWorker, WorkerState
from localmind.workers.transcription_worker import (
    TranscriptionWorker,
    DualChannelTranscriptionWorker,
    TranscriptionResult,
    TranscriptionSegment,
)
from localmind.workers.merge_worker import MergeWorker, MergeResult, MergedSegment
from localmind.workers.audit_worker import (
    AuditWorker,
    AuditResult,
    ParameterScore,
    DEFAULT_PARAMETERS,
)
from localmind.workers.orchestrator import ProcessingOrchestrator, ProcessingResult

__all__ = [
    # Base
    "BaseWorker",
    "WorkerState",
    # Transcription
    "TranscriptionWorker",
    "DualChannelTranscriptionWorker",
    "TranscriptionResult",
    "TranscriptionSegment",
    # Merge
    "MergeWorker",
    "MergeResult",
    "MergedSegment",
    # Audit
    "AuditWorker",
    "AuditResult",
    "ParameterScore",
    "DEFAULT_PARAMETERS",
    # Orchestrator
    "ProcessingOrchestrator",
    "ProcessingResult",
]
