"""SpeechBrain Integration Module for UltraSinger

This module provides advanced audio separation and ASR capabilities using SpeechBrain 1.0,
specifically optimized for karaoke creation with superior vocal/instrumental separation
and precise multilingual transcription with temporal alignment.

Key Features:
- SepFormer: Advanced neural source separation for vocal/instrumental separation
- Conformer/Branchformer ASR: State-of-the-art speech recognition with multilingual support
- LLM Rescoring: Language model-based transcription improvement
- Forced Alignment: Precise temporal synchronization for karaoke timing
- VAD: Voice Activity Detection for improved segmentation
- Model Management: Intelligent caching and memory optimization

This integration is designed to be non-invasive and work alongside existing UltraSinger
functionality while providing significant improvements in audio processing quality.
"""

# Core configuration and management
from .config_manager import SpeechBrainConfig, ProcessingMode
from .model_manager import SpeechBrainModelManager

# Audio separation
from .sepformer_separation import SepFormerSeparator, SepFormerModel

# Speech recognition and alignment
from .conformer_asr import ConformerASR, ASRModel, TranscriptionResult
# from .forced_alignment import ForcedAligner, AlignmentModel, AlignmentResult  # Temporarily disabled due to ctc_segmentation issues

# Voice Activity Detection
from .vad_system import VADSystem, VADModel, VADResult

# LLM Rescoring
from .llm_rescoring import LLMRescorer, LLMModel, RescoringResult

# Main integration interface
from .speechbrain_integration import (
    SpeechBrainPipeline,
    create_speechbrain_pipeline,
    separate_audio_with_speechbrain,
    transcribe_audio_with_speechbrain,
    align_text_with_speechbrain
)

__version__ = "1.0.0"
__author__ = "UltraSinger SpeechBrain Integration"

# Export main classes and functions
__all__ = [
    # Configuration
    "SpeechBrainConfig",
    "ProcessingMode",
    
    # Model management
    "SpeechBrainModelManager",
    
    # Audio separation
    "SepFormerSeparator",
    "SepFormerModel",
    
    # Speech recognition
    "ConformerASR",
    "ASRModel",
    "TranscriptionResult",
    
    # Forced alignment
    # "ForcedAligner",
    # "AlignmentModel",
    # "AlignmentResult",
    
    # Voice Activity Detection
    "VADSystem",
    "VADModel",
    "VADResult",
    
    # LLM Rescoring
    "LLMRescorer",
    "LLMModel",
    "RescoringResult",
    
    # Main pipeline
    "SpeechBrainPipeline",
    "create_speechbrain_pipeline",
    "separate_audio_with_speechbrain",
    "transcribe_audio_with_speechbrain",
    "align_text_with_speechbrain",
]