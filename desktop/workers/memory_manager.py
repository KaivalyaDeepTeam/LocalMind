"""
Memory Manager for CallScore Desktop

Provides utilities for monitoring and managing system memory,
especially important for large model loading operations.
"""

import gc
import sys
import logging
from typing import Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MemoryStatus:
    """Current memory status information."""
    total_gb: float
    available_gb: float
    used_gb: float
    percent_used: float
    gpu_available_gb: Optional[float] = None
    gpu_used_gb: Optional[float] = None


class MemoryManager:
    """
    Manages memory for large model operations.

    Provides utilities for:
    - Checking available system memory
    - Cleaning up GPU memory after model unloading
    - Determining if there's enough memory for operations
    """

    # Memory thresholds in GB
    SAFE_MEMORY_GB = 4.0      # Comfortable amount for operations
    WARNING_MEMORY_GB = 2.0   # Minimum before warning
    CRITICAL_MEMORY_GB = 1.0  # Minimum to proceed

    # Model memory requirements (approximate)
    MODEL_REQUIREMENTS_GB = {
        "whisper-large-v3": 3.0,
        "whisper-hindi2hinglish": 3.0,
        "phi-3.5-mini": 2.5,
        "mistral-7b": 4.5,
    }

    @staticmethod
    def get_memory_status() -> MemoryStatus:
        """
        Get current system and GPU memory status.

        Returns:
            MemoryStatus with current memory information.
        """
        try:
            import psutil
            mem = psutil.virtual_memory()

            status = MemoryStatus(
                total_gb=mem.total / 1e9,
                available_gb=mem.available / 1e9,
                used_gb=mem.used / 1e9,
                percent_used=mem.percent,
            )

            # Try to get GPU memory
            gpu_available, gpu_used = MemoryManager._get_gpu_memory()
            if gpu_available is not None:
                status.gpu_available_gb = gpu_available
                status.gpu_used_gb = gpu_used

            return status

        except ImportError:
            logger.warning("psutil not installed, memory monitoring limited")
            return MemoryStatus(
                total_gb=0,
                available_gb=0,
                used_gb=0,
                percent_used=0,
            )

    @staticmethod
    def _get_gpu_memory() -> Tuple[Optional[float], Optional[float]]:
        """
        Get GPU memory information if available.

        Returns:
            Tuple of (available_gb, used_gb) or (None, None) if no GPU.
        """
        try:
            import torch

            if torch.cuda.is_available():
                # NVIDIA GPU
                device = torch.cuda.current_device()
                total = torch.cuda.get_device_properties(device).total_memory
                allocated = torch.cuda.memory_allocated(device)
                available = (total - allocated) / 1e9
                used = allocated / 1e9
                return available, used

            elif torch.backends.mps.is_available():
                # Apple Silicon - MPS doesn't provide detailed memory info
                # Return None to indicate GPU is available but memory unknown
                return None, None

        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"Could not get GPU memory: {e}")

        return None, None

    @staticmethod
    def get_available_memory_gb() -> float:
        """
        Get available system memory in GB.

        Returns:
            Available memory in gigabytes.
        """
        status = MemoryManager.get_memory_status()
        return status.available_gb

    @staticmethod
    def has_enough_memory(required_gb: float) -> bool:
        """
        Check if there's enough available memory.

        Args:
            required_gb: Amount of memory needed in GB.

        Returns:
            True if enough memory is available.
        """
        available = MemoryManager.get_available_memory_gb()
        return available >= required_gb

    @staticmethod
    def check_model_memory(model_name: str) -> Tuple[bool, str]:
        """
        Check if there's enough memory for a specific model.

        Args:
            model_name: Name of the model to check.

        Returns:
            Tuple of (can_load: bool, message: str).
        """
        required = MemoryManager.MODEL_REQUIREMENTS_GB.get(model_name, 3.0)
        available = MemoryManager.get_available_memory_gb()

        if available >= required + MemoryManager.SAFE_MEMORY_GB:
            return True, f"Sufficient memory available ({available:.1f} GB)"
        elif available >= required + MemoryManager.WARNING_MEMORY_GB:
            return True, f"Memory is limited ({available:.1f} GB), processing may be slow"
        elif available >= required:
            return True, f"Low memory ({available:.1f} GB), consider closing other applications"
        else:
            return False, f"Insufficient memory ({available:.1f} GB available, {required:.1f} GB required)"

    @staticmethod
    def force_cleanup() -> None:
        """
        Force aggressive memory cleanup.

        Runs garbage collection and clears GPU caches.
        Call this after unloading models.
        """
        # First pass garbage collection
        gc.collect()

        try:
            import torch

            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
                logger.debug("Cleared CUDA cache")

            # Clear MPS cache (Apple Silicon)
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
                torch.mps.synchronize()
                logger.debug("Cleared MPS cache")

        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"GPU cleanup error (non-critical): {e}")

        # Final garbage collection
        gc.collect()

    @staticmethod
    def get_recommended_device() -> str:
        """
        Get the recommended compute device.

        Returns:
            Device string: "cuda", "mps", or "cpu".
        """
        try:
            import torch

            if torch.cuda.is_available():
                # Check if we have enough GPU memory
                device = torch.cuda.current_device()
                props = torch.cuda.get_device_properties(device)
                total_gb = props.total_memory / 1e9

                if total_gb >= 6.0:
                    return "cuda"
                else:
                    logger.info(f"GPU has limited memory ({total_gb:.1f} GB), may use CPU for some operations")
                    return "cuda"

            elif torch.backends.mps.is_available():
                return "mps"

        except ImportError:
            pass

        return "cpu"

    @staticmethod
    def log_memory_status() -> None:
        """Log current memory status for debugging."""
        status = MemoryManager.get_memory_status()

        logger.info(
            f"Memory Status: {status.used_gb:.1f}/{status.total_gb:.1f} GB "
            f"({status.percent_used:.0f}% used), "
            f"{status.available_gb:.1f} GB available"
        )

        if status.gpu_available_gb is not None:
            logger.info(
                f"GPU Memory: {status.gpu_used_gb:.1f} GB used, "
                f"{status.gpu_available_gb:.1f} GB available"
            )


class MemoryMonitor:
    """
    Context manager for monitoring memory usage during operations.

    Example:
        with MemoryMonitor("Model Loading") as monitor:
            load_model()
        print(f"Memory delta: {monitor.delta_gb:.2f} GB")
    """

    def __init__(self, operation_name: str = "Operation"):
        self.operation_name = operation_name
        self.start_memory: float = 0
        self.end_memory: float = 0
        self.delta_gb: float = 0

    def __enter__(self) -> "MemoryMonitor":
        self.start_memory = MemoryManager.get_available_memory_gb()
        logger.debug(f"{self.operation_name}: Starting with {self.start_memory:.2f} GB available")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.end_memory = MemoryManager.get_available_memory_gb()
        self.delta_gb = self.start_memory - self.end_memory

        logger.debug(
            f"{self.operation_name}: Completed. "
            f"Memory delta: {self.delta_gb:+.2f} GB, "
            f"Now available: {self.end_memory:.2f} GB"
        )

        return False  # Don't suppress exceptions
