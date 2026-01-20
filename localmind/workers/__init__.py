"""LocalMind background worker threads."""

from localmind.workers.audit_worker import (
    DEFAULT_PARAMETERS,
    AuditResult,
    AuditWorker,
    ParameterScore,
)
from localmind.workers.base import BaseWorker, WorkerState
from localmind.workers.hindi_transcription_worker import (
    DualChannelHindiSTTWorker,
    HindiSTTWorker,
)
from localmind.workers.merge_worker import MergedSegment, MergeResult, MergeWorker
from localmind.workers.model_download_worker import (
    AVAILABLE_MODELS,
    ModelDownloadWorker,
    ModelInfo,
    ModelType,
    SetupWizardData,
    get_models_directory,
    is_model_downloaded,
)
from localmind.workers.orchestrator import ProcessingOrchestrator, ProcessingResult
from localmind.workers.transcription_worker import (
    DualChannelTranscriptionWorker,
    TranscriptionResult,
    TranscriptionSegment,
    TranscriptionWorker,
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
    # Hindi Transcription
    "HindiSTTWorker",
    "DualChannelHindiSTTWorker",
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
