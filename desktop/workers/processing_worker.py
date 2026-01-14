"""
Processing Worker for CallScore Desktop

Handles the complete audio processing pipeline:
Audio → Preprocess → Transcribe → Merge → Audit → Results
"""

import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass

from PySide6.QtCore import Slot

from desktop.workers.base_worker import BaseWorker, ProcessingStage
from desktop.workers.memory_manager import MemoryManager, MemoryMonitor

if TYPE_CHECKING:
    from desktop.config.user_settings import UserSettings

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result from processing pipeline."""
    audio_file: str
    audio_duration: float
    transcription: Dict[str, Any]
    audit: Optional[Dict[str, Any]]
    processing_time: float
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for UI consumption."""
        return {
            "audio_file": self.audio_file,
            "audio_duration": self.audio_duration,
            "transcription": self.transcription,
            "audit": self.audit,
            "processing_time": self.processing_time,
            "error": self.error,
        }


class ProcessingWorker(BaseWorker):
    """
    Complete processing pipeline worker.

    Stages:
    1. LOADING_MODELS (0%): Load Whisper models
    2. PREPROCESSING (10%): Audio preprocessing & diarization
    3. DIARIZATION (20%): Speaker identification
    4. TRANSCRIPTION_V3 (30%): Whisper Large V3 transcription
    5. TRANSCRIPTION_H2H (50%): Hindi2Hinglish transcription
    6. MERGING (70%): LLM-based transcript merge
    7. AUDITING (85%): Quality scoring
    8. COMPLETE (100%): Done
    """

    def __init__(
        self,
        audio_path: str,
        settings: "UserSettings",
        run_audit: bool = True,
        models_dir: Optional[str] = None,
    ):
        """
        Initialize processing worker.

        Args:
            audio_path: Path to audio file to process
            settings: User settings with LLM config
            run_audit: Whether to run audit after transcription
            models_dir: Override default models directory
        """
        super().__init__()
        self.audio_path = audio_path
        self.settings = settings
        self.run_audit = run_audit
        self.models_dir = models_dir

        # Will be set during processing
        self._transcriber = None
        self._merger = None
        self._auditor = None

    def _get_models_dir(self) -> Path:
        """Get models directory from settings or default."""
        if self.models_dir:
            return Path(self.models_dir)

        # Import here to avoid circular imports
        from desktop.config.user_settings import SettingsManager
        return SettingsManager.get_models_dir()

    def _create_transcriber(self):
        """Create and configure the DualTranscriber."""
        from src.transcription.dual_transcriber import DualTranscriber

        models_dir = self._get_models_dir()

        return DualTranscriber(
            models_dir=str(models_dir / "whisper"),
            device=self.settings.transcription.device,
            enable_preprocessing=True,
            enable_diarization=self.settings.transcription.enable_diarization,
            memory_efficient=True,
        )

    def _get_llm_provider(self):
        """Get the configured LLM provider."""
        from desktop.llm import get_provider
        return get_provider(self.settings)

    @Slot()
    def run(self) -> None:
        """Execute the processing pipeline."""
        start_time = time.time()

        try:
            self.signals.started.emit()

            # Verify audio file exists
            if not Path(self.audio_path).exists():
                raise FileNotFoundError(f"Audio file not found: {self.audio_path}")

            # Check memory before starting
            can_proceed, memory_msg = MemoryManager.check_model_memory("whisper-large-v3")
            if not can_proceed:
                raise MemoryError(memory_msg)

            # === Stage 1: Loading Models ===
            self._set_stage(ProcessingStage.LOADING_MODELS, "Initializing AI models...")

            if self.is_cancelled():
                self.signals.cancelled.emit()
                return

            with MemoryMonitor("Model Loading"):
                self._transcriber = self._create_transcriber()

            # === Stage 2-5: Transcription ===
            self._set_stage(ProcessingStage.PREPROCESSING, "Preparing audio for transcription...")

            if self.is_cancelled():
                self.signals.cancelled.emit()
                return

            # Run transcription with progress callback
            def on_stage_update(stage: str, progress: float):
                """Update progress during transcription."""
                if stage == "preprocessing":
                    self._emit_progress(15, "Preprocessing audio...")
                elif stage == "diarization":
                    self._set_stage(ProcessingStage.DIARIZATION, "Identifying speakers...")
                elif stage == "whisper_v3":
                    self._set_stage(ProcessingStage.TRANSCRIPTION_V3, f"Transcribing with Whisper V3... {progress:.0f}%")
                    # Map 0-100% to 30-50%
                    mapped = int(30 + (progress * 0.2))
                    self._emit_progress(mapped, f"Whisper V3: {progress:.0f}%")
                elif stage == "hindi2hinglish":
                    self._set_stage(ProcessingStage.TRANSCRIPTION_H2H, f"Transcribing with Hindi2Hinglish... {progress:.0f}%")
                    # Map 0-100% to 50-70%
                    mapped = int(50 + (progress * 0.2))
                    self._emit_progress(mapped, f"Hindi2Hinglish: {progress:.0f}%")

            # Run the transcription
            with MemoryMonitor("Transcription"):
                dual_result = self._transcriber.transcribe(
                    audio_path=self.audio_path,
                    language=self.settings.transcription.language,
                    romanize=self.settings.transcription.romanize,
                )

            if self.is_cancelled():
                MemoryManager.force_cleanup()
                self.signals.cancelled.emit()
                return

            # Clean up transcription models
            self._transcriber = None
            MemoryManager.force_cleanup()

            # === Stage 6: Merging ===
            self._set_stage(ProcessingStage.MERGING, "Merging transcripts with AI...")

            llm_provider = self._get_llm_provider()

            with MemoryMonitor("Merging"):
                merge_result = llm_provider.merge_transcripts(
                    whisper_v3_text=dual_result.whisper_v3.text,
                    hindi2hinglish_text=dual_result.hindi2hinglish.text,
                    audio_duration=dual_result.whisper_v3.duration,
                )
                merged_transcript = merge_result.merged_transcript

            if self.is_cancelled():
                self.signals.cancelled.emit()
                return

            # Prepare transcription result
            transcription_result = {
                "merged_transcript": merged_transcript,
                "whisper_v3_text": dual_result.whisper_v3.text,
                "hindi2hinglish_text": dual_result.hindi2hinglish.text,
                "audio_duration_seconds": dual_result.whisper_v3.duration,
                "preprocessing_applied": dual_result.preprocessing_applied,
                "diarization_applied": dual_result.diarization_applied,
                "speaker_stats": dual_result.speaker_stats,
            }

            # === Stage 7: Auditing ===
            audit_result = None

            if self.run_audit:
                self._set_stage(ProcessingStage.AUDITING, "Analyzing call quality...")

                with MemoryMonitor("Auditing"):
                    audit_output = llm_provider.audit_call(
                        transcript=merged_transcript,
                        audio_duration=dual_result.whisper_v3.duration,
                    )

                # Convert to dict format expected by UI
                audit_result = {
                    "quality": {
                        "total_score": audit_output.total_score,
                        "grade": audit_output.grade,
                        "parameters": [
                            {
                                "name": p.name,
                                "score": p.score,
                                "max_score": p.max_score,
                                "verdict": p.verdict,
                                "evidence": p.evidence,
                            }
                            for p in audit_output.parameters
                        ],
                        "strengths": audit_output.strengths,
                        "improvements": audit_output.improvements,
                    },
                    "razt": {
                        "has_zt_violation": audit_output.has_zt_violation,
                        "has_ra_violation": audit_output.has_ra_violation,
                        "zt_violations": audit_output.zt_violations,
                        "ra_violations": audit_output.ra_violations,
                    },
                    "overall_recommendation": audit_output.overall_recommendation,
                }

            # === Stage 8: Complete ===
            self._set_stage(ProcessingStage.COMPLETE, "Processing complete!")

            processing_time = time.time() - start_time

            result = ProcessingResult(
                audio_file=self.audio_path,
                audio_duration=dual_result.whisper_v3.duration,
                transcription=transcription_result,
                audit=audit_result,
                processing_time=processing_time,
            )

            self.signals.finished.emit(result.to_dict())

        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            self.signals.error.emit("FileNotFoundError", str(e))

        except MemoryError as e:
            logger.error(f"Memory error: {e}")
            MemoryManager.force_cleanup()
            self.signals.error.emit("MemoryError", str(e))

        except Exception as e:
            logger.exception(f"Processing error: {e}")
            self.signals.error.emit(type(e).__name__, str(e))

        finally:
            # Cleanup
            self._transcriber = None
            MemoryManager.force_cleanup()


class TranscriptionOnlyWorker(BaseWorker):
    """
    Worker that only runs transcription (no audit).

    Useful for quick transcription jobs.
    """

    def __init__(
        self,
        audio_path: str,
        settings: "UserSettings",
        models_dir: Optional[str] = None,
    ):
        super().__init__()
        self.audio_path = audio_path
        self.settings = settings
        self.models_dir = models_dir

    @Slot()
    def run(self) -> None:
        """Run transcription only."""
        # Delegate to ProcessingWorker with audit disabled
        worker = ProcessingWorker(
            audio_path=self.audio_path,
            settings=self.settings,
            run_audit=False,
            models_dir=self.models_dir,
        )

        # Forward signals
        worker.signals.started.connect(self.signals.started.emit)
        worker.signals.progress.connect(self.signals.progress.emit)
        worker.signals.stage_changed.connect(self.signals.stage_changed.emit)
        worker.signals.finished.connect(self.signals.finished.emit)
        worker.signals.error.connect(self.signals.error.emit)
        worker.signals.cancelled.connect(self.signals.cancelled.emit)

        # Run it
        worker.run()
