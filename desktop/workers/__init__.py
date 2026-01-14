"""
Background worker threads for CallScore Desktop.

This module provides the worker infrastructure for running
long-running operations (transcription, auditing, etc.) in
background threads without blocking the UI.
"""

from desktop.workers.base_worker import (
    BaseWorker,
    SimpleWorker,
    WorkerSignals,
    ProcessingStage,
)
from desktop.workers.memory_manager import (
    MemoryManager,
    MemoryMonitor,
    MemoryStatus,
)
from desktop.workers.processing_worker import (
    ProcessingWorker,
    ProcessingResult,
    TranscriptionOnlyWorker,
)

__all__ = [
    # Base worker classes
    "BaseWorker",
    "SimpleWorker",
    "WorkerSignals",
    "ProcessingStage",
    # Memory management
    "MemoryManager",
    "MemoryMonitor",
    "MemoryStatus",
    # Processing workers
    "ProcessingWorker",
    "ProcessingResult",
    "TranscriptionOnlyWorker",
]
