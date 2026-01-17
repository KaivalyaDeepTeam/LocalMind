"""
LocalMind Hindi STT Worker

Background worker for Hindi-English (Hinglish) transcription using
Whisper-Hindi2Hinglish models from Oriserve.

Supported Models:
- Apex (default): 8x faster, better for noisy Indian audio, 0.8B params
- Prime: Higher accuracy on clean audio, 2B params

Features:
- Hinglish language support (reduces grammatical errors)
- 40%+ better performance than base Whisper Large V3
- Noise-resistant design for Indian environments
- Hallucination mitigation
- Optimized for call centers
"""

from pathlib import Path
from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass, field

from localmind.workers.base import BaseWorker
from localmind.workers.transcription_worker import TranscriptionSegment, TranscriptionResult

# Available Hindi models
HINDI_MODELS = {
    "apex": "Oriserve/Whisper-Hindi2Hinglish-Apex",    # Default: 8x faster, better for noisy audio
    "prime": "Oriserve/Whisper-Hindi2Hinglish-Prime",  # Higher accuracy on clean audio
}


class HindiSTTWorker(BaseWorker):
    """Worker for Hindi-English transcription using HindiSTT model."""

    def __init__(
        self,
        audio_path: str,
        use_gpu: bool = True,
        use_flash_attention: bool = False,
        model_variant: Literal["apex", "prime"] = "apex",
        num_speakers: Optional[int] = 2,
        use_preprocessing: bool = True,
        parent=None,
    ):
        """Initialize Hindi STT worker.

        Args:
            audio_path: Path to audio file.
            use_gpu: Whether to use GPU acceleration.
            use_flash_attention: Use Flash Attention 2 for faster inference.
            model_variant: Which model to use - "apex" (fast, noisy audio) or "prime" (accurate, clean audio).
            num_speakers: Expected number of speakers (None for auto-detection).
            use_preprocessing: Apply audio preprocessing (volume leveling, noise reduction).
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._audio_path = Path(audio_path)
        self._use_gpu = use_gpu
        self._use_flash_attention = use_flash_attention
        self._model_variant = model_variant
        self._model_id = HINDI_MODELS[model_variant]
        self._num_speakers = num_speakers
        self._use_preprocessing = use_preprocessing
        self._pipe = None

    def do_work(self) -> TranscriptionResult:
        """Perform Hindi-English transcription."""
        model_name = "Apex" if self._model_variant == "apex" else "Prime"
        self.report_progress(0, f"Loading Hindi model ({model_name})...")

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

        self.report_progress(60, "Processing transcription...")

        # Build single segment from chunked transcription
        full_text = result.get("text", "").strip()
        segments = []

        if full_text:
            segments.append(TranscriptionSegment(
                start=0.0,
                end=0.0,
                text=full_text,
            ))

        transcription = TranscriptionResult(
            text=result["text"].strip(),
            segments=segments,
            language="hi-en",  # Hindi-English mixed
        )

        self.report_progress(100, "Hindi-English transcription complete")
        return transcription

    def _load_model(self) -> None:
        """Load the HindiSTT model with optimized parameters."""
        import os

        try:
            import torch
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
        except ImportError:
            raise ImportError(
                "transformers not installed. Install with: pip install transformers torch"
            )

        # Determine device and dtype
        if self._use_gpu:
            if torch.cuda.is_available():
                self._device = "cuda:0"
                self._dtype = torch.float16
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self._device = "mps"  # Apple Silicon GPU
                self._dtype = torch.float32  # Use float32 on MPS to avoid NaN errors
            else:
                self._device = "cpu"
                self._dtype = torch.float32
        else:
            self._device = "cpu"
            self._dtype = torch.float32

        self.report_progress(3, f"Loading model on {self._device}...")

        # Patch torch.load to handle CUDA-saved models on non-CUDA devices
        original_load = torch.load
        target_device = "cpu" if self._device == "mps" else self._device
        def patched_load(*args, **kwargs):
            if 'map_location' not in kwargs:
                kwargs['map_location'] = torch.device(target_device)
            return original_load(*args, **kwargs)
        torch.load = patched_load

        try:
            model_kwargs = {
                "torch_dtype": self._dtype,
                "low_cpu_mem_usage": True,
                "use_safetensors": True,
            }

            if self._use_flash_attention and self._device not in ("cpu", "mps"):
                try:
                    model_kwargs["attn_implementation"] = "flash_attention_2"
                except Exception:
                    pass

            # Download and load model
            self.report_progress(5, f"Downloading {self._model_id}...")

            self._model = AutoModelForSpeechSeq2Seq.from_pretrained(
                self._model_id,
                **model_kwargs
            )

            self.report_progress(15, "Moving model to device...")
            self._model = self._model.to(self._device)
            self._model.eval()

            self.report_progress(20, "Loading processor...")
            self._processor = AutoProcessor.from_pretrained(self._model_id)

        finally:
            torch.load = original_load

        self.report_progress(25, "Model loaded successfully")

    def _transcribe(self) -> Dict[str, Any]:
        """Transcribe audio file with chunking to avoid timestamp issues."""
        import tempfile
        import soundfile as sf
        import numpy as np
        from localmind.audio.preprocessing import preprocess_audio_for_transcription

        # Load and preprocess audio
        if self._use_preprocessing:
            self.report_progress(35, "Preprocessing audio (volume leveling, noise reduction)...")
            try:
                audio, sr = preprocess_audio_for_transcription(
                    str(self._audio_path),
                    target_sr=16000,
                    apply_compression=True,
                    apply_gate=True,
                    telephone_filter=False,
                )
            except Exception as e:
                print(f"Warning: Audio preprocessing failed ({e}), using original audio")
                import librosa
                audio, sr = librosa.load(str(self._audio_path), sr=16000, mono=True)
        else:
            import librosa
            audio, sr = librosa.load(str(self._audio_path), sr=16000, mono=True)

        # Chunk audio with 5-second overlap for better boundary handling
        chunk_duration = 25  # seconds (< 30s limit)
        overlap_duration = 5  # seconds overlap
        stride_duration = chunk_duration - overlap_duration  # 20 seconds

        chunk_samples = chunk_duration * sr
        stride_samples = stride_duration * sr
        total_samples = len(audio)

        # Calculate number of chunks with overlap
        num_chunks = max(1, int(np.ceil((total_samples - chunk_samples) / stride_samples)) + 1)

        print(f"Processing audio in {num_chunks} chunks (25s each, 5s overlap)...")

        all_text = []
        previous_text_end = ""  # Store end of previous chunk for deduplication

        for i in range(num_chunks):
            # Calculate chunk boundaries with overlap
            start_sample = i * stride_samples
            end_sample = min(start_sample + chunk_samples, total_samples)

            # For the last chunk, make sure we get all remaining audio
            if i == num_chunks - 1:
                end_sample = total_samples

            chunk = audio[start_sample:end_sample]

            # Pad chunk to 30 seconds (Whisper requirement for mel features length 3000)
            target_length = 30 * sr  # 30 seconds
            if len(chunk) < target_length:
                # Pad with zeros to reach 30 seconds
                padding = target_length - len(chunk)
                chunk = np.pad(chunk, (0, padding), mode='constant', constant_values=0)

            # Transcribe chunk with optimized parameters
            progress = 40 + int((i / num_chunks) * 50)
            self.report_progress(progress, f"Transcribing chunk {i+1}/{num_chunks}...")

            try:
                # Process audio through processor
                inputs = self._processor(
                    chunk,
                    sampling_rate=sr,
                    return_tensors="pt",
                    return_attention_mask=True
                )

                input_features = inputs.input_features.to(self._device, dtype=self._dtype)

                # CRITICAL generation parameters for maximum word capture
                generate_kwargs = {
                    # Language and task (suppress warnings)
                    "language": "en",  # Hindi-English mixed
                    "task": "transcribe",

                    # Temperature fallback for difficult code-mixed speech
                    "temperature": (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),

                    # CRITICAL: Low threshold to capture quiet speakers
                    "no_speech_threshold": 0.3,  # Default 0.6 causes missing words!

                    # Relaxed hallucination detection for better recall
                    "compression_ratio_threshold": 2.4,  # Default 1.35 too aggressive
                    "logprob_threshold": -1.0,

                    # Don't condition on previous tokens for better independence
                    "condition_on_prev_tokens": False,

                    # Generation settings
                    "max_new_tokens": 444,  # Leave room for special tokens
                    "num_beams": 1,
                    "do_sample": False,
                }

                # Generate transcription
                import torch
                with torch.no_grad():
                    try:
                        generated_ids = self._model.generate(
                            input_features,
                            **generate_kwargs
                        )
                    except Exception:
                        # Fallback for older transformers
                        generated_ids = self._model.generate(
                            input_features,
                            max_new_tokens=444,
                            num_beams=1,
                            do_sample=False
                        )

                # Decode
                text = self._processor.batch_decode(
                    generated_ids,
                    skip_special_tokens=True
                )[0].strip()

                if text:
                    if i == 0:
                        # First chunk - keep everything
                        all_text.append(text)
                        # Store last few words for overlap detection
                        words = text.split()
                        previous_text_end = " ".join(words[-10:]) if len(words) > 10 else text
                    else:
                        # Subsequent chunks - try to remove duplicate overlap
                        # Simple deduplication: check if start of current text matches end of previous
                        words = text.split()
                        deduplicated = False

                        # Try to find overlap by checking first N words against previous chunk's end
                        for overlap_words in range(min(15, len(words)), 0, -1):
                            chunk_start = " ".join(words[:overlap_words])
                            if chunk_start in previous_text_end:
                                # Found overlap - skip these words
                                remaining_text = " ".join(words[overlap_words:])
                                if remaining_text:
                                    all_text.append(remaining_text)
                                    # Update previous_text_end
                                    remaining_words = remaining_text.split()
                                    previous_text_end = " ".join(remaining_words[-10:]) if len(remaining_words) > 10 else remaining_text
                                deduplicated = True
                                break

                        if not deduplicated:
                            # No clear overlap found - keep all (better to duplicate than lose words)
                            all_text.append(text)
                            previous_text_end = " ".join(words[-10:]) if len(words) > 10 else text

            except Exception as e:
                print(f"Warning: Chunk {i} failed ({e}), skipping")

        # Combine all chunks
        full_text = " ".join(all_text)

        return {"text": full_text}


class DualChannelHindiSTTWorker(BaseWorker):
    """Worker for dual-channel Hindi-English transcription with separate channel processing."""

    def __init__(
        self,
        audio_path: str,
        use_gpu: bool = True,
        use_flash_attention: bool = False,
        model_variant: Literal["apex", "prime"] = "apex",
        agent_channel: int = 0,
        customer_channel: int = 1,
        use_preprocessing: bool = True,
        parent=None,
    ):
        """Initialize dual-channel Hindi STT worker.

        Args:
            audio_path: Path to audio file.
            use_gpu: Whether to use GPU acceleration.
            use_flash_attention: Use Flash Attention 2 for faster inference.
            model_variant: Which model to use - "apex" (fast, noisy audio) or "prime" (accurate, clean audio).
            agent_channel: Channel index for agent audio.
            customer_channel: Channel index for customer audio.
            use_preprocessing: Apply audio preprocessing (volume leveling, noise reduction).
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._audio_path = Path(audio_path)
        self._use_gpu = use_gpu
        self._use_flash_attention = use_flash_attention
        self._model_variant = model_variant
        self._model_id = HINDI_MODELS[model_variant]
        self._agent_channel = agent_channel
        self._customer_channel = customer_channel
        self._use_preprocessing = use_preprocessing
        self._model = None
        self._processor = None
        self._device = None
        self._dtype = None

    def do_work(self) -> TranscriptionResult:
        """Perform dual-channel Hindi-English transcription."""
        model_name = "Apex" if self._model_variant == "apex" else "Prime"
        self.report_progress(0, f"Loading Hindi model ({model_name})...")

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

        # Merge transcripts from chunked processing
        self.report_progress(85, "Merging transcripts...")

        all_segments = []

        # Add agent transcription
        agent_text = agent_result.get("text", "").strip()
        if agent_text:
            all_segments.append(TranscriptionSegment(
                start=0.0,
                end=0.0,
                text=agent_text,
                speaker="Agent",  # Assigned from channel 0
            ))

        # Add customer transcription
        customer_text = customer_result.get("text", "").strip()
        if customer_text:
            all_segments.append(TranscriptionSegment(
                start=0.0,
                end=0.0,
                text=customer_text,
                speaker="Customer",  # Assigned from channel 1
            ))

        # Build full text - with speaker labels
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
        """Load the HindiSTT model with optimized parameters."""
        import os

        try:
            import torch
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
        except ImportError:
            raise ImportError(
                "transformers not installed. Install with: pip install transformers torch"
            )

        # Determine device and dtype
        if self._use_gpu:
            if torch.cuda.is_available():
                self._device = "cuda:0"
                self._dtype = torch.float16
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self._device = "mps"  # Apple Silicon GPU
                self._dtype = torch.float32  # Use float32 on MPS to avoid NaN errors
            else:
                self._device = "cpu"
                self._dtype = torch.float32
        else:
            self._device = "cpu"
            self._dtype = torch.float32

        self.report_progress(3, f"Loading model on {self._device}...")

        # Patch torch.load to handle CUDA-saved models on non-CUDA devices
        original_load = torch.load
        target_device = "cpu" if self._device == "mps" else self._device
        def patched_load(*args, **kwargs):
            if 'map_location' not in kwargs:
                kwargs['map_location'] = torch.device(target_device)
            return original_load(*args, **kwargs)
        torch.load = patched_load

        try:
            model_kwargs = {
                "torch_dtype": self._dtype,
                "low_cpu_mem_usage": True,
                "use_safetensors": True,
            }

            if self._use_flash_attention and self._device not in ("cpu", "mps"):
                try:
                    model_kwargs["attn_implementation"] = "flash_attention_2"
                except Exception:
                    pass

            # Download and load model
            self.report_progress(5, f"Downloading {self._model_id}...")

            self._model = AutoModelForSpeechSeq2Seq.from_pretrained(
                self._model_id,
                **model_kwargs
            )

            self.report_progress(10, "Moving model to device...")
            self._model = self._model.to(self._device)
            self._model.eval()

            self.report_progress(15, "Loading processor...")
            self._processor = AutoProcessor.from_pretrained(self._model_id)

        finally:
            torch.load = original_load

        self.report_progress(18, "Model loaded successfully")

    def _load_channels(self):
        """Load and optionally preprocess separate audio channels with independent normalization."""
        import librosa
        import tempfile
        import soundfile as sf

        try:
            # Check if audio is stereo
            audio, sr = librosa.load(str(self._audio_path), sr=16000, mono=False)
            is_stereo = audio.ndim == 2
        except Exception as e:
            raise RuntimeError(f"Failed to load audio: {e}")

        # Apply preprocessing if enabled
        if self._use_preprocessing:
            from localmind.audio.preprocessing import preprocess_dual_channel_audio, preprocess_audio_for_transcription

            if not is_stereo:
                # Mono audio - use single preprocessing
                try:
                    processed_audio, sr = preprocess_audio_for_transcription(
                        str(self._audio_path),
                        target_sr=16000,
                        apply_compression=True,
                        apply_gate=True,
                        telephone_filter=False,  # Disabled - too aggressive for MP3/compressed audio
                    )

                    # Save to temp file
                    import numpy as np
                    temp_path = str(Path(tempfile.gettempdir()) / "preprocessed_mono.wav")
                    # Ensure audio is float32 and in valid range [-1, 1]
                    processed_audio = np.clip(processed_audio, -1.0, 1.0).astype(np.float32)
                    sf.write(temp_path, processed_audio, sr, subtype='FLOAT')
                    return temp_path, temp_path
                except Exception as e:
                    print(f"Warning: Audio preprocessing failed ({e}), using original audio")

            else:
                # Stereo audio - preprocess each channel independently (CRITICAL for uneven volumes)
                try:
                    agent_path, customer_path = preprocess_dual_channel_audio(
                        str(self._audio_path),
                        agent_channel=self._agent_channel,
                        customer_channel=self._customer_channel,
                        target_sr=16000,
                    )
                    return agent_path, customer_path
                except Exception as e:
                    print(f"Warning: Dual-channel preprocessing failed ({e}), using basic channel split")

        # Fallback: No preprocessing or preprocessing failed
        if not is_stereo:
            # Mono - return same path for both channels
            return str(self._audio_path), str(self._audio_path)

        # Stereo - basic channel extraction without preprocessing
        import numpy as np
        agent_audio = audio[self._agent_channel]
        customer_audio = audio[self._customer_channel]

        temp_dir = tempfile.gettempdir()
        agent_path = str(Path(temp_dir) / "agent_channel.wav")
        customer_path = str(Path(temp_dir) / "customer_channel.wav")

        # Ensure audio is float32 and in valid range
        agent_audio = np.clip(agent_audio, -1.0, 1.0).astype(np.float32)
        customer_audio = np.clip(customer_audio, -1.0, 1.0).astype(np.float32)

        sf.write(agent_path, agent_audio, sr, subtype='FLOAT')
        sf.write(customer_path, customer_audio, sr, subtype='FLOAT')

        return agent_path, customer_path

    def _transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio file with overlapping chunks."""
        import soundfile as sf
        import numpy as np
        import tempfile

        # Load audio
        audio, sr = sf.read(audio_path)

        # Chunk with 5-second overlap
        chunk_duration = 25  # seconds
        overlap_duration = 5  # seconds
        stride_duration = chunk_duration - overlap_duration  # 20 seconds

        chunk_samples = chunk_duration * sr
        stride_samples = stride_duration * sr
        total_samples = len(audio)

        num_chunks = max(1, int(np.ceil((total_samples - chunk_samples) / stride_samples)) + 1)

        all_text = []
        previous_text_end = ""

        for i in range(num_chunks):
            start_sample = i * stride_samples
            end_sample = min(start_sample + chunk_samples, total_samples)

            if i == num_chunks - 1:
                end_sample = total_samples

            chunk = audio[start_sample:end_sample]

            # Pad chunk to 30 seconds (Whisper requirement)
            target_length = 30 * sr
            if len(chunk) < target_length:
                padding = target_length - len(chunk)
                chunk = np.pad(chunk, (0, padding), mode='constant', constant_values=0)

            # Transcribe chunk with optimized parameters
            try:
                # Process audio through processor
                inputs = self._processor(
                    chunk,
                    sampling_rate=sr,
                    return_tensors="pt",
                    return_attention_mask=True
                )

                input_features = inputs.input_features.to(self._device, dtype=self._dtype)

                # CRITICAL generation parameters
                generate_kwargs = {
                    "language": "en",
                    "task": "transcribe",
                    "temperature": (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
                    "no_speech_threshold": 0.3,  # CRITICAL for capturing quiet speakers
                    "compression_ratio_threshold": 2.4,
                    "logprob_threshold": -1.0,
                    "condition_on_prev_tokens": False,
                    "max_new_tokens": 444,
                    "num_beams": 1,
                    "do_sample": False,
                }

                # Generate transcription
                import torch
                with torch.no_grad():
                    try:
                        generated_ids = self._model.generate(
                            input_features,
                            **generate_kwargs
                        )
                    except Exception:
                        generated_ids = self._model.generate(
                            input_features,
                            max_new_tokens=444,
                            num_beams=1,
                            do_sample=False
                        )

                # Decode
                text = self._processor.batch_decode(
                    generated_ids,
                    skip_special_tokens=True
                )[0].strip()

                if text:
                    if i == 0:
                        all_text.append(text)
                        words = text.split()
                        previous_text_end = " ".join(words[-10:]) if len(words) > 10 else text
                    else:
                        # Deduplicate overlap
                        words = text.split()
                        deduplicated = False

                        for overlap_words in range(min(15, len(words)), 0, -1):
                            chunk_start = " ".join(words[:overlap_words])
                            if chunk_start in previous_text_end:
                                remaining_text = " ".join(words[overlap_words:])
                                if remaining_text:
                                    all_text.append(remaining_text)
                                    remaining_words = remaining_text.split()
                                    previous_text_end = " ".join(remaining_words[-10:]) if len(remaining_words) > 10 else remaining_text
                                deduplicated = True
                                break

                        if not deduplicated:
                            all_text.append(text)
                            previous_text_end = " ".join(words[-10:]) if len(words) > 10 else text

            except Exception as e:
                print(f"Warning: Dual-channel chunk {i} failed ({e}), skipping")

        # Combine chunks
        full_text = " ".join(all_text)
        return {"text": full_text}
