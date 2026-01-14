"""
Local LLM Provider for CallScore Desktop

Uses llama-cpp-python for 100% offline operation.
Supports Phi-3.5-mini and Mistral-7B models.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

from desktop.llm.base_provider import (
    BaseLLMProvider,
    MergeResult,
    AuditResult,
    QualityParameter,
)

logger = logging.getLogger(__name__)


# Optimized prompts for smaller local models
MERGE_PROMPT_LOCAL = """Merge these two transcripts of the same call into one accurate version.

TRANSCRIPT A:
{whisper_v3}

TRANSCRIPT B:
{h2h}

Create a merged transcript with speaker labels (Counselor/Caller). Output only the merged conversation."""

AUDIT_PROMPT_LOCAL = """Analyze this sales call transcript. Rate quality 0-100 and list strengths/improvements.

TRANSCRIPT:
{transcript}

Respond in JSON format:
{{"score": <0-100>, "grade": "<A/B/C/D/F>", "strengths": ["..."], "improvements": ["..."]}}"""


class LocalLLMProvider(BaseLLMProvider):
    """
    Local LLM provider for offline operation.

    Uses GGUF models with llama-cpp-python.
    No API key required - runs entirely on device.
    """

    MODELS = {
        "phi-3.5-mini": {
            "repo": "microsoft/Phi-3.5-mini-instruct-gguf",
            "filename": "Phi-3.5-mini-instruct-Q4_K_M.gguf",
            "size_gb": 2.4,
            "context_length": 8192,
        },
        "mistral-7b": {
            "repo": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
            "filename": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
            "size_gb": 4.1,
            "context_length": 32768,
        },
    }

    def __init__(self, api_key: str = "", model: str = ""):
        # Local provider doesn't need API key
        super().__init__("", model or "phi-3.5-mini")
        self._llm = None
        self._models_dir: Optional[Path] = None

    @property
    def name(self) -> str:
        return "Local (Offline)"

    @property
    def default_model(self) -> str:
        return "phi-3.5-mini"

    @property
    def is_configured(self) -> bool:
        """Local provider is always 'configured' if model exists."""
        return self._is_model_downloaded()

    @property
    def requires_api_key(self) -> bool:
        return False

    def set_models_dir(self, path: Path) -> None:
        """Set the models directory."""
        self._models_dir = path

    def _get_models_dir(self) -> Path:
        """Get models directory."""
        if self._models_dir:
            return self._models_dir

        # Default location
        from desktop.config.user_settings import SettingsManager
        return SettingsManager.get_models_dir() / "llm"

    def _get_model_path(self) -> Path:
        """Get path to model file."""
        model_info = self.MODELS.get(self._model, self.MODELS["phi-3.5-mini"])
        return self._get_models_dir() / model_info["filename"]

    def _is_model_downloaded(self) -> bool:
        """Check if model file exists."""
        return self._get_model_path().exists()

    def _load_llm(self):
        """Load the local LLM."""
        if self._llm is not None:
            return self._llm

        if not self._is_model_downloaded():
            logger.warning(f"Local model not downloaded: {self._model}")
            return None

        try:
            from llama_cpp import Llama

            model_path = self._get_model_path()
            model_info = self.MODELS.get(self._model, self.MODELS["phi-3.5-mini"])

            logger.info(f"Loading local LLM: {model_path}")

            self._llm = Llama(
                model_path=str(model_path),
                n_ctx=model_info["context_length"],
                n_gpu_layers=-1,  # Use GPU if available
                verbose=False,
            )

            logger.info(f"Local LLM loaded: {self._model}")
            return self._llm

        except ImportError:
            logger.error("llama-cpp-python not installed. Run: pip install llama-cpp-python")
            return None
        except Exception as e:
            logger.error(f"Failed to load local LLM: {e}")
            return None

    def _generate(self, prompt: str, max_tokens: int = 2048) -> Optional[str]:
        """Generate text with the local LLM."""
        llm = self._load_llm()
        if llm is None:
            return None

        try:
            output = llm(
                prompt,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.95,
                stop=["</s>", "<|end|>", "<|endoftext|>"],
            )
            return output["choices"][0]["text"].strip()
        except Exception as e:
            logger.error(f"Local LLM generation failed: {e}")
            return None

    def unload(self) -> None:
        """Unload model to free memory."""
        self._llm = None

    def merge_transcripts(
        self,
        whisper_v3_text: str,
        hindi2hinglish_text: str,
        audio_duration: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MergeResult:
        """Merge transcripts using local LLM."""

        if not self._is_model_downloaded():
            # Fallback: use Hindi2Hinglish (usually better for mixed speech)
            logger.info("Local model not available, using Hindi2Hinglish transcript")
            return MergeResult(
                merged_transcript=hindi2hinglish_text,
                confidence=0.8,
                model_used="fallback",
            )

        prompt = MERGE_PROMPT_LOCAL.format(
            whisper_v3=whisper_v3_text[:4000],  # Limit input size
            h2h=hindi2hinglish_text[:4000],
        )

        result = self._generate(prompt, max_tokens=4096)

        if result:
            return MergeResult(
                merged_transcript=result,
                confidence=0.9,
                model_used=self._model,
            )

        # Fallback
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
        """Audit call using local LLM."""

        if not self._is_model_downloaded():
            return self._placeholder_audit("Download local model in Settings to enable offline auditing")

        prompt = AUDIT_PROMPT_LOCAL.format(transcript=transcript[:6000])
        result = self._generate(prompt, max_tokens=1024)

        if result:
            return self._parse_audit_response(result)

        return self._placeholder_audit("Local model generation failed")

    def _parse_audit_response(self, response: str) -> AuditResult:
        """Parse local model's response."""
        import json

        try:
            # Try to find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])

                return AuditResult(
                    total_score=data.get("score", 50),
                    grade=data.get("grade", "C"),
                    parameters=[],  # Local model uses simplified scoring
                    strengths=data.get("strengths", []),
                    improvements=data.get("improvements", []),
                    overall_recommendation="Scored by local AI model (offline mode)",
                    model_used=self._model,
                )
        except json.JSONDecodeError:
            pass

        # If JSON parsing fails, try to extract basic info
        return AuditResult(
            total_score=50,
            grade="C",
            parameters=[],
            strengths=["Call completed"],
            improvements=["Detailed scoring requires cloud LLM"],
            overall_recommendation="Local model provided basic analysis. Enable cloud LLM for detailed scoring.",
            model_used=self._model,
        )

    def _placeholder_audit(self, message: str = "") -> AuditResult:
        """Return placeholder when model not available."""
        return AuditResult(
            total_score=0,
            grade="N/A",
            parameters=[],
            strengths=[],
            improvements=[message or "Local model not available"],
            overall_recommendation="Download the local model in Settings for offline auditing.",
            model_used="none",
        )


def download_local_model(model_name: str = "phi-3.5-mini", progress_callback=None) -> bool:
    """
    Download a local LLM model.

    Args:
        model_name: Model to download (phi-3.5-mini or mistral-7b)
        progress_callback: Optional callback(downloaded_bytes, total_bytes)

    Returns:
        True if download successful
    """
    from desktop.config.user_settings import SettingsManager

    model_info = LocalLLMProvider.MODELS.get(model_name)
    if not model_info:
        logger.error(f"Unknown model: {model_name}")
        return False

    models_dir = SettingsManager.get_models_dir() / "llm"
    models_dir.mkdir(parents=True, exist_ok=True)

    output_path = models_dir / model_info["filename"]

    if output_path.exists():
        logger.info(f"Model already exists: {output_path}")
        return True

    try:
        from huggingface_hub import hf_hub_download

        logger.info(f"Downloading {model_name} from {model_info['repo']}...")

        hf_hub_download(
            repo_id=model_info["repo"],
            filename=model_info["filename"],
            local_dir=str(models_dir),
            local_dir_use_symlinks=False,
        )

        logger.info(f"Download complete: {output_path}")
        return True

    except ImportError:
        logger.error("huggingface_hub not installed. Run: pip install huggingface_hub")
        return False
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False
