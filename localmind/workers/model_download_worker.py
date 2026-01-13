"""
LocalMind Model Download Worker

Background worker for downloading AI models on first run.
"""

from pathlib import Path
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass
from enum import Enum, auto

from PySide6.QtCore import QThread, Signal


class ModelType(Enum):
    """Types of downloadable models."""
    WHISPER = auto()
    LOCAL_LLM = auto()


@dataclass
class ModelInfo:
    """Information about a downloadable model."""
    name: str
    display_name: str
    model_type: ModelType
    size_gb: float
    repo_id: str
    filename: str
    description: str
    required: bool = False


# Available models for download
AVAILABLE_MODELS = [
    ModelInfo(
        name="whisper-large-v3",
        display_name="Whisper Large V3",
        model_type=ModelType.WHISPER,
        size_gb=3.0,
        repo_id="openai/whisper-large-v3",
        filename="model.safetensors",
        description="Best quality transcription model",
        required=True,
    ),
    ModelInfo(
        name="whisper-medium",
        display_name="Whisper Medium",
        model_type=ModelType.WHISPER,
        size_gb=1.5,
        repo_id="openai/whisper-medium",
        filename="model.safetensors",
        description="Good quality, faster transcription",
        required=False,
    ),
    ModelInfo(
        name="phi-3.5-mini",
        display_name="Phi-3.5 Mini (Local LLM)",
        model_type=ModelType.LOCAL_LLM,
        size_gb=2.4,
        repo_id="microsoft/Phi-3.5-mini-instruct-gguf",
        filename="Phi-3.5-mini-instruct-Q4_K_M.gguf",
        description="Recommended local LLM for offline auditing",
        required=False,
    ),
    ModelInfo(
        name="llama-3.2-3b",
        display_name="Llama 3.2 3B (Local LLM)",
        model_type=ModelType.LOCAL_LLM,
        size_gb=2.0,
        repo_id="hugging-quants/Llama-3.2-3B-Instruct-Q4_K_M-GGUF",
        filename="llama-3.2-3b-instruct-q4_k_m.gguf",
        description="Alternative local LLM",
        required=False,
    ),
]


def get_models_directory() -> Path:
    """Get the directory for storing models."""
    import platform
    import os

    system = platform.system()
    if system == "Darwin":
        base = Path.home() / "Library" / "Application Support" / "LocalMind"
    elif system == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home())) / "LocalMind"
    else:
        base = Path.home() / ".local" / "share" / "localmind"

    models_dir = base / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


def get_model_path(model: ModelInfo) -> Path:
    """Get the path where a model will be stored."""
    models_dir = get_models_directory()
    return models_dir / model.filename


def is_model_downloaded(model: ModelInfo) -> bool:
    """Check if a model is already downloaded."""
    return get_model_path(model).exists()


class ModelDownloadWorker(QThread):
    """Worker for downloading models from Hugging Face.

    Signals:
        started_download: Emitted when download starts (model_name).
        progress: Emitted with progress updates (model_name, percent, speed_mbps).
        finished_download: Emitted when a model finishes (model_name, success, message).
        all_complete: Emitted when all downloads complete.
        error: Emitted on error (error_message).
    """

    started_download = Signal(str)
    progress = Signal(str, int, float)  # model_name, percent, speed_mbps
    finished_download = Signal(str, bool, str)  # model_name, success, message
    all_complete = Signal()
    error = Signal(str)

    def __init__(
        self,
        models: Optional[List[ModelInfo]] = None,
        parent=None,
    ):
        """Initialize download worker.

        Args:
            models: List of models to download. If None, downloads required models.
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._models = models or [m for m in AVAILABLE_MODELS if m.required]
        self._should_stop = False
        self._current_model: Optional[str] = None

    def stop(self) -> None:
        """Stop downloading."""
        self._should_stop = True

    def run(self) -> None:
        """Download all specified models."""
        try:
            from huggingface_hub import hf_hub_download, HfApi
            from huggingface_hub.utils import RepositoryNotFoundError
        except ImportError:
            self.error.emit(
                "huggingface_hub not installed. Install with: pip install huggingface_hub"
            )
            return

        models_dir = get_models_directory()
        total_models = len(self._models)

        for i, model in enumerate(self._models):
            if self._should_stop:
                break

            self._current_model = model.name
            model_path = get_model_path(model)

            # Skip if already downloaded
            if model_path.exists():
                self.finished_download.emit(model.name, True, "Already downloaded")
                continue

            self.started_download.emit(model.name)

            try:
                # Download with progress
                downloaded_path = hf_hub_download(
                    repo_id=model.repo_id,
                    filename=model.filename,
                    local_dir=str(models_dir),
                    local_dir_use_symlinks=False,
                )

                self.finished_download.emit(model.name, True, str(downloaded_path))

            except RepositoryNotFoundError:
                self.finished_download.emit(
                    model.name, False, f"Repository not found: {model.repo_id}"
                )
            except Exception as e:
                self.finished_download.emit(model.name, False, str(e))

        self._current_model = None
        self.all_complete.emit()


class SetupWizardData:
    """Data class for setup wizard selections."""

    def __init__(self):
        self.whisper_model: str = "whisper-large-v3"
        self.download_local_llm: bool = False
        self.local_llm_model: str = "phi-3.5-mini"
        self.use_gpu: bool = True

    def get_models_to_download(self) -> List[ModelInfo]:
        """Get list of models to download based on selections."""
        models = []

        # Find selected Whisper model
        for model in AVAILABLE_MODELS:
            if model.name == self.whisper_model:
                models.append(model)
                break

        # Add local LLM if selected
        if self.download_local_llm:
            for model in AVAILABLE_MODELS:
                if model.name == self.local_llm_model:
                    models.append(model)
                    break

        return models

    def get_total_download_size(self) -> float:
        """Get total download size in GB."""
        return sum(m.size_gb for m in self.get_models_to_download())


def get_required_download_size() -> float:
    """Get size of required downloads in GB."""
    return sum(m.size_gb for m in AVAILABLE_MODELS if m.required and not is_model_downloaded(m))


def get_optional_download_size() -> float:
    """Get size of optional downloads in GB."""
    return sum(m.size_gb for m in AVAILABLE_MODELS if not m.required and not is_model_downloaded(m))
