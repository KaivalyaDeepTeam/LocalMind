"""
LocalMind Local LLM Provider

Local LLM implementation using llama-cpp-python for offline inference.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any, AsyncGenerator
import asyncio

from localmind.llm.base import (
    BaseLLMProvider, LLMMessage, LLMResponse, LLMConfig, LLMRole,
)


# Model configurations
LOCAL_MODELS = {
    "phi-3.5-mini": {
        "repo": "bartowski/Phi-3.5-mini-instruct-GGUF",
        "filename": "Phi-3.5-mini-instruct-Q4_K_M.gguf",
        "context_length": 4096,
        "chat_format": "chatml",
    },
    "llama-3.2-3b": {
        "repo": "hugging-quants/Llama-3.2-3B-Instruct-Q4_K_M-GGUF",
        "filename": "llama-3.2-3b-instruct-q4_k_m.gguf",
        "context_length": 4096,
        "chat_format": "llama-3",
    },
    "qwen-2.5-3b": {
        "repo": "Qwen/Qwen2.5-3B-Instruct-GGUF",
        "filename": "qwen2.5-3b-instruct-q4_k_m.gguf",
        "context_length": 4096,
        "chat_format": "chatml",
    },
}


def get_models_directory() -> Path:
    """Get the directory for storing local models."""
    import platform

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


class LocalProvider(BaseLLMProvider):
    """Local LLM provider using llama-cpp-python."""

    def __init__(
        self,
        model: str = "phi-3.5-mini",
        n_ctx: Optional[int] = None,
        n_gpu_layers: int = -1,
        verbose: bool = False,
    ):
        """Initialize local LLM provider.

        Args:
            model: Model name from LOCAL_MODELS or path to GGUF file.
            n_ctx: Context window size (uses model default if None).
            n_gpu_layers: Number of layers to offload to GPU (-1 for all).
            verbose: Whether to print llama.cpp logs.
        """
        super().__init__(model)
        self._n_ctx = n_ctx
        self._n_gpu_layers = n_gpu_layers
        self._verbose = verbose
        self._llm = None
        self._model_path: Optional[Path] = None

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "local"

    def _get_model_config(self) -> Dict[str, Any]:
        """Get configuration for the model."""
        if self._model in LOCAL_MODELS:
            return LOCAL_MODELS[self._model]

        # Assume it's a custom model path
        return {
            "context_length": 4096,
            "chat_format": "chatml",
        }

    def _get_model_path(self) -> Path:
        """Get the path to the model file."""
        if self._model_path:
            return self._model_path

        # Check if model is a direct path
        if Path(self._model).exists():
            self._model_path = Path(self._model)
            return self._model_path

        # Look for model in models directory
        if self._model in LOCAL_MODELS:
            config = LOCAL_MODELS[self._model]
            models_dir = get_models_directory()
            self._model_path = models_dir / config["filename"]
            return self._model_path

        raise ValueError(f"Unknown model: {self._model}")

    def is_model_downloaded(self) -> bool:
        """Check if the model is downloaded."""
        try:
            path = self._get_model_path()
            return path.exists()
        except ValueError:
            return False

    async def download_model(
        self,
        progress_callback: Optional[callable] = None,
    ) -> Path:
        """Download the model from Hugging Face.

        Args:
            progress_callback: Optional callback for progress updates.

        Returns:
            Path to the downloaded model.
        """
        if self._model not in LOCAL_MODELS:
            raise ValueError(f"Cannot download unknown model: {self._model}")

        config = LOCAL_MODELS[self._model]
        models_dir = get_models_directory()
        model_path = models_dir / config["filename"]

        if model_path.exists():
            return model_path

        try:
            from huggingface_hub import hf_hub_download
        except ImportError:
            raise ImportError(
                "huggingface_hub not installed. Install with: pip install huggingface_hub"
            )

        # Download in a thread to not block
        def do_download():
            return hf_hub_download(
                repo_id=config["repo"],
                filename=config["filename"],
                local_dir=str(models_dir),
                local_dir_use_symlinks=False,
            )

        downloaded_path = await asyncio.to_thread(do_download)
        self._model_path = Path(downloaded_path)
        return self._model_path

    async def initialize(self) -> None:
        """Initialize the local LLM."""
        if self._is_initialized:
            return

        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError(
                "llama-cpp-python not installed. Install with: "
                "pip install llama-cpp-python"
            )

        model_path = self._get_model_path()
        if not model_path.exists():
            # Auto-download model if it doesn't exist
            if self._model in LOCAL_MODELS:
                print(f"Model not found locally. Downloading {self._model}...")
                try:
                    model_path = await self.download_model()
                    print(f"Model downloaded successfully to: {model_path}")
                except Exception as e:
                    raise FileNotFoundError(
                        f"Failed to download model {self._model}: {e}\n"
                        f"Please download manually or use an API provider (OpenAI/Anthropic)."
                    )
            else:
                raise FileNotFoundError(
                    f"Model not found: {model_path}. "
                    f"Call download_model() first or provide a valid path."
                )

        config = self._get_model_config()
        n_ctx = self._n_ctx or config.get("context_length", 4096)

        # Initialize in a thread to not block
        def load_model():
            return Llama(
                model_path=str(model_path),
                n_ctx=n_ctx,
                n_gpu_layers=self._n_gpu_layers,
                verbose=self._verbose,
                chat_format=config.get("chat_format", "chatml"),
            )

        self._llm = await asyncio.to_thread(load_model)
        self._is_initialized = True

    async def generate(
        self,
        messages: List[LLMMessage],
        config: Optional[LLMConfig] = None,
    ) -> LLMResponse:
        """Generate a response using local LLM."""
        if not self._is_initialized:
            await self.initialize()

        if config is None:
            config = LLMConfig()

        # Convert messages to llama.cpp format
        llama_messages = [msg.to_dict() for msg in messages]

        # Generate in a thread to not block
        def do_generate():
            response = self._llm.create_chat_completion(
                messages=llama_messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                stop=config.stop_sequences,
            )
            return response

        response = await asyncio.to_thread(do_generate)

        # Extract response data
        choice = response["choices"][0]
        content = choice["message"]["content"]
        usage = response.get("usage", {})

        return LLMResponse(
            content=content,
            model=self._model,
            provider=self.provider_name,
            usage={
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
            },
            finish_reason=choice.get("finish_reason"),
            raw_response=response,
        )

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        config: Optional[LLMConfig] = None,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response using local LLM."""
        if not self._is_initialized:
            await self.initialize()

        if config is None:
            config = LLMConfig()

        # Convert messages to llama.cpp format
        llama_messages = [msg.to_dict() for msg in messages]

        # Create streaming generator
        def create_stream():
            return self._llm.create_chat_completion(
                messages=llama_messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                stop=config.stop_sequences,
                stream=True,
            )

        stream = await asyncio.to_thread(create_stream)

        # Yield chunks from stream
        for chunk in stream:
            if "choices" in chunk and chunk["choices"]:
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta and delta["content"]:
                    yield delta["content"]

    async def close(self) -> None:
        """Clean up local LLM resources."""
        if self._llm:
            # llama-cpp-python handles cleanup automatically
            self._llm = None
            self._is_initialized = False
