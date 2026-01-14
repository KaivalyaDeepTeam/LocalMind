"""
LocalMind Processing Orchestrator

Coordinates the full processing pipeline: transcription -> merge -> audit.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal, Slot

from localmind.workers.base import WorkerState
from localmind.workers.transcription_worker import (
    TranscriptionWorker, DualChannelTranscriptionWorker, TranscriptionResult,
)
from localmind.workers.hindi_transcription_worker import (
    HindiSTTWorker, DualChannelHindiSTTWorker,
)
from localmind.workers.merge_worker import MergeWorker, MergeResult
from localmind.workers.audit_worker import AuditWorker, AuditResult


@dataclass
class ProcessingResult:
    """Complete processing result."""
    transcription: Optional[TranscriptionResult] = None
    merge: Optional[MergeResult] = None
    audit: Optional[AuditResult] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        if self.transcription:
            result["transcription"] = self.transcription.to_dict()
        if self.merge:
            result["merge"] = self.merge.to_dict()
        if self.audit:
            result.update(self.audit.to_dict())
        if self.error:
            result["error"] = self.error
        return result


class ProcessingOrchestrator(QObject):
    """Orchestrates the full processing pipeline.

    Signals:
        stage_started: Emitted when a stage starts (stage_name).
        stage_progress: Emitted with progress (stage_name, percent, message).
        stage_completed: Emitted when a stage completes (stage_name).
        stage_error: Emitted on stage error (stage_name, error_message).
        processing_complete: Emitted when all processing is done (result).
        processing_error: Emitted on fatal error (error_message).
    """

    stage_started = Signal(str)
    stage_progress = Signal(str, int, str)
    stage_completed = Signal(str)
    stage_error = Signal(str, str)
    processing_complete = Signal(object)
    processing_error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._audio_path: Optional[Path] = None
        self._is_processing = False
        self._should_stop = False

        # Workers
        self._transcription_worker: Optional[TranscriptionWorker] = None
        self._merge_worker: Optional[MergeWorker] = None
        self._audit_worker: Optional[AuditWorker] = None

        # Results
        self._result = ProcessingResult()

        # Settings
        self._whisper_model = "large-v3"
        self._language: Optional[str] = None
        self._use_gpu = True
        self._dual_channel = True
        self._use_hindi_stt = False  # Use HindiSTT for Hindi-English
        self._parameters: Optional[List[Dict[str, Any]]] = None

    @property
    def is_processing(self) -> bool:
        """Check if processing is in progress."""
        return self._is_processing

    def configure(
        self,
        whisper_model: str = "large-v3",
        language: Optional[str] = None,
        use_gpu: bool = True,
        dual_channel: bool = True,
        use_hindi_stt: bool = False,
        scoring_parameters: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Configure processing settings.

        Args:
            whisper_model: Whisper model name.
            language: Language code or None for auto-detect.
            use_gpu: Whether to use GPU acceleration.
            dual_channel: Whether to process as dual-channel audio.
            use_hindi_stt: Use HindiSTT model for Hindi-English transcription.
            scoring_parameters: Custom scoring parameters.
        """
        self._whisper_model = whisper_model
        self._language = language
        self._use_gpu = use_gpu
        self._dual_channel = dual_channel
        self._use_hindi_stt = use_hindi_stt
        self._parameters = scoring_parameters

    def start(self, audio_path: str) -> None:
        """Start processing an audio file.

        Args:
            audio_path: Path to the audio file.
        """
        if self._is_processing:
            return

        self._audio_path = Path(audio_path)
        if not self._audio_path.exists():
            self.processing_error.emit(f"File not found: {audio_path}")
            return

        self._is_processing = True
        self._should_stop = False
        self._result = ProcessingResult()

        # Start transcription
        self._start_transcription()

    def stop(self) -> None:
        """Stop all processing."""
        self._should_stop = True

        if self._transcription_worker and self._transcription_worker.isRunning():
            self._transcription_worker.stop()
            self._transcription_worker.wait()

        if self._merge_worker and self._merge_worker.isRunning():
            self._merge_worker.stop()
            self._merge_worker.wait()

        if self._audit_worker and self._audit_worker.isRunning():
            self._audit_worker.stop()
            self._audit_worker.wait()

        self._is_processing = False

    def _start_transcription(self) -> None:
        """Start the transcription stage."""
        self.stage_started.emit("transcription")

        # Choose worker based on Hindi mode
        if self._use_hindi_stt:
            # Use HindiSTT for Hindi-English (Hinglish) transcription
            if self._dual_channel:
                self._transcription_worker = DualChannelHindiSTTWorker(
                    audio_path=str(self._audio_path),
                    use_gpu=self._use_gpu,
                )
            else:
                self._transcription_worker = HindiSTTWorker(
                    audio_path=str(self._audio_path),
                    use_gpu=self._use_gpu,
                )
        else:
            # Use standard Whisper
            if self._dual_channel:
                self._transcription_worker = DualChannelTranscriptionWorker(
                    audio_path=str(self._audio_path),
                    model_name=self._whisper_model,
                    language=self._language,
                    use_gpu=self._use_gpu,
                )
            else:
                self._transcription_worker = TranscriptionWorker(
                    audio_path=str(self._audio_path),
                    model_name=self._whisper_model,
                    language=self._language,
                    use_gpu=self._use_gpu,
                )

        self._transcription_worker.progress.connect(
            lambda p, m: self.stage_progress.emit("transcription", p, m)
        )
        self._transcription_worker.finished_work.connect(self._on_transcription_complete)
        self._transcription_worker.error.connect(
            lambda e: self._on_stage_error("transcription", e)
        )

        self._transcription_worker.start()

    @Slot(object)
    def _on_transcription_complete(self, result: TranscriptionResult) -> None:
        """Handle transcription completion."""
        if self._should_stop:
            self._is_processing = False
            return

        self._result.transcription = result
        self.stage_completed.emit("transcription")

        # Start merge
        self._start_merge()

    def _start_merge(self) -> None:
        """Start the merge stage."""
        self.stage_started.emit("merge")

        self._merge_worker = MergeWorker(
            transcription=self._result.transcription,
        )

        self._merge_worker.progress.connect(
            lambda p, m: self.stage_progress.emit("merge", p, m)
        )
        self._merge_worker.finished_work.connect(self._on_merge_complete)
        self._merge_worker.error.connect(
            lambda e: self._on_stage_error("merge", e)
        )

        self._merge_worker.start()

    @Slot(object)
    def _on_merge_complete(self, result: MergeResult) -> None:
        """Handle merge completion."""
        if self._should_stop:
            self._is_processing = False
            return

        self._result.merge = result
        self.stage_completed.emit("merge")

        # Start audit
        self._start_audit()

    def _start_audit(self) -> None:
        """Start the audit stage."""
        self.stage_started.emit("audit")

        self._audit_worker = AuditWorker(
            merge_result=self._result.merge,
            parameters=self._parameters,
        )

        self._audit_worker.progress.connect(
            lambda p, m: self.stage_progress.emit("audit", p, m)
        )
        self._audit_worker.finished_work.connect(self._on_audit_complete)
        self._audit_worker.error.connect(
            lambda e: self._on_stage_error("audit", e)
        )

        self._audit_worker.start()

    @Slot(object)
    def _on_audit_complete(self, result: AuditResult) -> None:
        """Handle audit completion."""
        if self._should_stop:
            self._is_processing = False
            return

        self._result.audit = result
        self.stage_completed.emit("audit")

        # All done
        self._is_processing = False
        self.processing_complete.emit(self._result)

    def _on_stage_error(self, stage: str, error: str) -> None:
        """Handle stage error."""
        self._result.error = f"{stage}: {error}"
        self._is_processing = False
        self.stage_error.emit(stage, error)
        self.processing_error.emit(error)
