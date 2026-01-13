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
from localmind.workers.model_download_worker import (
    ModelDownloadWorker,
    ModelInfo,
    ModelType,
    SetupWizardData,
    AVAILABLE_MODELS,
    get_models_directory,
    is_model_downloaded,
)

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
    # Model Download
    "ModelDownloadWorker",
    "ModelInfo",
    "ModelType",
    "SetupWizardData",
    "AVAILABLE_MODELS",
    "get_models_directory",
    "is_model_downloaded",
]
