"""
LocalMind Hindi STT Worker

Background worker for Hindi-English (Hinglish) transcription using
the fine-tuned Whisper model from Svetozar1993/HindiSTT.

Features:
- Romanized Hindi output (Hinglish)
- Noise resistant
- Low hallucination
- Optimized for Indian call centers
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from localmind.workers.base import BaseWorker
from localmind.workers.transcription_worker import TranscriptionSegment, TranscriptionResult


class HindiSTTWorker(BaseWorker):
    """Worker for Hindi-English transcription using HindiSTT model."""

    MODEL_ID = "Svetozar1993/HindiSTT"

    def __init__(
        self,
        audio_path: str,
        use_gpu: bool = True,
        use_flash_attention: bool = False,
        parent=None,
    ):
        """Initialize Hindi STT worker.

        Args:
            audio_path: Path to audio file.
            use_gpu: Whether to use GPU acceleration.
            use_flash_attention: Use Flash Attention 2 for faster inference.
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._audio_path = Path(audio_path)
        self._use_gpu = use_gpu
        self._use_flash_attention = use_flash_attention
        self._pipe = None

    def do_work(self) -> TranscriptionResult:
        """Perform Hindi-English transcription."""
        self.report_progress(0, "Loading HindiSTT model...")

        if self.check_stop():
            return None

        # Load model
        self._load_model()

        self.report_progress(30, "Transcribing Hindi-English audio...")
        self.check_pause()

        if self.check_stop():
            return None

        # Transcribe
        result = self._transcribe()

        self.report_progress(90, "Processing results...")

        # Build result with segments if available
        segments = []
        if "chunks" in result:
            for chunk in result["chunks"]:
                segments.append(TranscriptionSegment(
                    start=chunk.get("timestamp", [0, 0])[0] or 0,
                    end=chunk.get("timestamp", [0, 0])[1] or 0,
                    text=chunk.get("text", "").strip(),
                ))

        transcription = TranscriptionResult(
            text=result["text"].strip(),
            segments=segments,
            language="hi-en",  # Hindi-English mixed
        )

        self.report_progress(100, "Hindi-English transcription complete")
        return transcription

    def _load_model(self) -> None:
        """Load the HindiSTT model."""
        import os

        try:
            import torch
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
        except ImportError:
            raise ImportError(
                "transformers not installed. Install with: pip install transformers torch"
            )

        # Determine device and dtype
        if self._use_gpu:
            if torch.cuda.is_available():
                device = "cuda:0"
                torch_dtype = torch.float16
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"  # Apple Silicon GPU
                torch_dtype = torch.float16
            else:
                device = "cpu"
                torch_dtype = torch.float32
        else:
            device = "cpu"
            torch_dtype = torch.float32

        self.report_progress(10, f"Loading model on {device}...")

        # Patch torch.load to handle CUDA-saved models on non-CUDA devices
        original_load = torch.load
        target_device = "cpu" if device == "mps" else device
        def patched_load(*args, **kwargs):
            if 'map_location' not in kwargs:
                kwargs['map_location'] = torch.device(target_device)
            return original_load(*args, **kwargs)
        torch.load = patched_load

        try:
            model_kwargs = {
                "torch_dtype": torch_dtype,
                "low_cpu_mem_usage": True,
            }

            if self._use_flash_attention and device not in ("cpu", "mps"):
                try:
                    model_kwargs["attn_implementation"] = "flash_attention_2"
                except Exception:
                    pass

            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                self.MODEL_ID,
                **model_kwargs
            )
            model.to(device)

            processor = AutoProcessor.from_pretrained(self.MODEL_ID)

            self._pipe = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor,
                torch_dtype=torch_dtype,
                device=device,
                generate_kwargs={"task": "transcribe", "language": "en"},
            )
        finally:
            torch.load = original_load

        self.report_progress(25, "Model loaded successfully")

    def _transcribe(self) -> Dict[str, Any]:
        """Transcribe audio file."""
        result = self._pipe(
            str(self._audio_path),
            return_timestamps=True,
        )
        return result


class DualChannelHindiSTTWorker(BaseWorker):
    """Worker for dual-channel Hindi-English transcription with speaker diarization."""

    MODEL_ID = "Svetozar1993/HindiSTT"

    def __init__(
        self,
        audio_path: str,
        use_gpu: bool = True,
        use_flash_attention: bool = False,
        agent_channel: int = 0,
        customer_channel: int = 1,
        parent=None,
    ):
        """Initialize dual-channel Hindi STT worker.

        Args:
            audio_path: Path to audio file.
            use_gpu: Whether to use GPU acceleration.
            use_flash_attention: Use Flash Attention 2 for faster inference.
            agent_channel: Channel index for agent audio.
            customer_channel: Channel index for customer audio.
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._audio_path = Path(audio_path)
        self._use_gpu = use_gpu
        self._use_flash_attention = use_flash_attention
        self._agent_channel = agent_channel
        self._customer_channel = customer_channel
        self._pipe = None

    def do_work(self) -> TranscriptionResult:
        """Perform dual-channel Hindi-English transcription."""
        self.report_progress(0, "Loading HindiSTT model...")

        if self.check_stop():
            return None

        # Load model
        self._load_model()

        self.report_progress(20, "Loading audio channels...")
        self.check_pause()

        if self.check_stop():
            return None

        # Load audio channels
        agent_audio, customer_audio = self._load_channels()

        # Transcribe agent channel
        self.report_progress(30, "Transcribing agent channel (Hindi-English)...")
        self.check_pause()

        if self.check_stop():
            return None

        agent_result = self._transcribe_audio(agent_audio)

        # Transcribe customer channel
        self.report_progress(60, "Transcribing customer channel (Hindi-English)...")
        self.check_pause()

        if self.check_stop():
            return None

        customer_result = self._transcribe_audio(customer_audio)

        # Merge and sort segments
        self.report_progress(85, "Merging transcripts...")

        all_segments = []

        # Process agent segments
        if "chunks" in agent_result:
            for chunk in agent_result["chunks"]:
                ts = chunk.get("timestamp", [0, 0])
                all_segments.append(TranscriptionSegment(
                    start=ts[0] or 0,
                    end=ts[1] or 0,
                    text=chunk.get("text", "").strip(),
                    speaker="Agent",
                ))
        else:
            all_segments.append(TranscriptionSegment(
                start=0,
                end=0,
                text=agent_result.get("text", "").strip(),
                speaker="Agent",
            ))

        # Process customer segments
        if "chunks" in customer_result:
            for chunk in customer_result["chunks"]:
                ts = chunk.get("timestamp", [0, 0])
                all_segments.append(TranscriptionSegment(
                    start=ts[0] or 0,
                    end=ts[1] or 0,
                    text=chunk.get("text", "").strip(),
                    speaker="Customer",
                ))
        else:
            all_segments.append(TranscriptionSegment(
                start=0,
                end=0,
                text=customer_result.get("text", "").strip(),
                speaker="Customer",
            ))

        # Sort by start time
        all_segments.sort(key=lambda s: s.start)

        # Build full text
        full_text = "\n".join(
            f"[{s.speaker}] {s.text}" for s in all_segments
        )

        transcription = TranscriptionResult(
            text=full_text,
            segments=all_segments,
            language="hi-en",
            channels=2,
        )

        self.report_progress(100, "Dual-channel Hindi-English transcription complete")
        return transcription

    def _load_model(self) -> None:
        """Load the HindiSTT model."""
        import os

        try:
            import torch
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
        except ImportError:
            raise ImportError(
                "transformers not installed. Install with: pip install transformers torch"
            )

        # Determine device and dtype
        if self._use_gpu:
            if torch.cuda.is_available():
                device = "cuda:0"
                torch_dtype = torch.float16
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"  # Apple Silicon GPU
                torch_dtype = torch.float16
            else:
                device = "cpu"
                torch_dtype = torch.float32
        else:
            device = "cpu"
            torch_dtype = torch.float32

        self.report_progress(10, f"Loading model on {device}...")

        # Patch torch.load to handle CUDA-saved models on non-CUDA devices
        original_load = torch.load
        target_device = "cpu" if device == "mps" else device
        def patched_load(*args, **kwargs):
            if 'map_location' not in kwargs:
                kwargs['map_location'] = torch.device(target_device)
            return original_load(*args, **kwargs)
        torch.load = patched_load

        try:
            model_kwargs = {
                "torch_dtype": torch_dtype,
                "low_cpu_mem_usage": True,
            }

            if self._use_flash_attention and device not in ("cpu", "mps"):
                try:
                    model_kwargs["attn_implementation"] = "flash_attention_2"
                except Exception:
                    pass

            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                self.MODEL_ID,
                **model_kwargs
            )
            model.to(device)

            processor = AutoProcessor.from_pretrained(self.MODEL_ID)

            self._pipe = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor,
                torch_dtype=torch_dtype,
                device=device,
                generate_kwargs={"task": "transcribe", "language": "en"},
            )
        finally:
            torch.load = original_load

        self.report_progress(18, "Model loaded successfully")

    def _load_channels(self):
        """Load separate audio channels."""
        try:
            import librosa
            import numpy as np
            import tempfile
            import soundfile as sf
        except ImportError:
            raise ImportError(
                "librosa and soundfile not installed. Install with: pip install librosa soundfile"
            )

        # Load stereo audio
        audio, sr = librosa.load(str(self._audio_path), sr=16000, mono=False)

        if audio.ndim == 1:
            # Mono audio - duplicate to both channels
            return str(self._audio_path), str(self._audio_path)

        # Extract channels and save to temp files
        agent_audio = audio[self._agent_channel]
        customer_audio = audio[self._customer_channel]

        # Save to temp files for the pipeline
        temp_dir = tempfile.gettempdir()
        agent_path = Path(temp_dir) / "agent_channel.wav"
        customer_path = Path(temp_dir) / "customer_channel.wav"

        sf.write(str(agent_path), agent_audio, sr)
        sf.write(str(customer_path), customer_audio, sr)

        return str(agent_path), str(customer_path)

    def _transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio file."""
        result = self._pipe(
            audio_path,
            return_timestamps=True,
        )
        return result
