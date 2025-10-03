"""
SpeechBrain Configuration Manager

Manages configuration settings for SpeechBrain models and processing parameters,
providing intelligent defaults and optimization based on hardware capabilities.
"""

import os
import json
import torch
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

from modules.console_colors import ULTRASINGER_HEAD, blue_highlighted, yellow_highlighted


class ProcessingMode(Enum):
    """Processing mode options"""
    FAST = "fast"
    BALANCED = "balanced"
    HIGH_QUALITY = "high_quality"
    CUSTOM = "custom"


@dataclass
class SepFormerConfig:
    """Configuration for SepFormer separation"""
    model_name: str = "speechbrain/sepformer-wsj02mix"
    sample_rate: int = 8000
    chunk_length: int = 32000
    overlap_ratio: float = 0.1
    normalize_audio: bool = True
    use_gpu: bool = True
    batch_size: int = 1


@dataclass
class ConformerConfig:
    """Configuration for Conformer ASR"""
    model_name: str = "speechbrain/asr-conformer-transformerlm-librispeech"
    language: str = "en"
    beam_size: int = 10
    lm_weight: float = 0.60
    use_gpu: bool = True
    batch_size: int = 1
    enable_vad: bool = True
    vad_threshold: float = 0.5


@dataclass
class LLMConfig:
    """Configuration for LLM rescoring"""
    model_name: str = "microsoft/DialoGPT-medium"
    max_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    use_gpu: bool = True
    context_window: int = 100


@dataclass
class AlignmentConfig:
    """Configuration for forced alignment"""
    model_name: str = "speechbrain/asr-wav2vec2-commonvoice-en"
    hop_length: int = 320
    frame_rate: int = 50
    use_phonemes: bool = True
    alignment_threshold: float = 0.3


@dataclass
class VADConfig:
    """Configuration for Voice Activity Detection"""
    model_name: str = "speechbrain/vad-crdnn-libriparty"
    frame_length: int = 25
    frame_shift: int = 10
    threshold: float = 0.5
    min_speech_duration: float = 0.1
    min_silence_duration: float = 0.1


class SpeechBrainConfig:
    """Main configuration manager for SpeechBrain integration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "speechbrain_config.json"
        )
        
        # Initialize default configurations
        self.sepformer = SepFormerConfig()
        self.conformer = ConformerConfig()
        self.llm = LLMConfig()
        self.alignment = AlignmentConfig()
        self.vad = VADConfig()
        
        # General settings
        self.processing_mode = ProcessingMode.BALANCED
        self.cache_enabled = True
        self.cache_path = os.path.join(os.path.expanduser("~"), ".speechbrain_cache")
        self.device = self._detect_device()
        self.max_memory_usage = self._estimate_memory_limit()
        
        # Load existing configuration if available
        self.load_config()
        
        # Optimize configuration based on hardware
        self._optimize_for_hardware()
    
    def _detect_device(self) -> str:
        """Detect optimal device for processing"""
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
            print(f"{ULTRASINGER_HEAD} Detected GPU: {torch.cuda.get_device_name(0)} ({gpu_memory:.1f}GB)")
            return "cuda"
        else:
            print(f"{ULTRASINGER_HEAD} Using CPU for SpeechBrain processing")
            return "cpu"
    
    def _estimate_memory_limit(self) -> float:
        """Estimate available memory limit in GB"""
        if self.device == "cuda":
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            return gpu_memory * 0.8  # Use 80% of available GPU memory
        else:
            # For CPU, estimate based on system RAM (simplified)
            return 4.0  # Conservative estimate
    
    def _optimize_for_hardware(self):
        """Optimize configuration based on available hardware"""
        if self.device == "cuda":
            memory_gb = self._estimate_memory_limit()
            
            # Optimize batch sizes based on available memory
            if memory_gb >= 12:
                self.sepformer.batch_size = 4
                self.conformer.batch_size = 8
                self.processing_mode = ProcessingMode.HIGH_QUALITY
            elif memory_gb >= 8:
                self.sepformer.batch_size = 2
                self.conformer.batch_size = 4
                self.processing_mode = ProcessingMode.BALANCED
            else:
                self.sepformer.batch_size = 1
                self.conformer.batch_size = 2
                self.processing_mode = ProcessingMode.FAST
                
            # Enable GPU for all components
            self.sepformer.use_gpu = True
            self.conformer.use_gpu = True
            self.llm.use_gpu = True
            
        else:
            # CPU optimization
            self.sepformer.batch_size = 1
            self.conformer.batch_size = 1
            self.processing_mode = ProcessingMode.FAST
            
            # Disable GPU for all components
            self.sepformer.use_gpu = False
            self.conformer.use_gpu = False
            self.llm.use_gpu = False
        
        print(f"{ULTRASINGER_HEAD} Optimized for {blue_highlighted(self.processing_mode.value)} processing mode")
    
    def set_language(self, language: str):
        """Set language for ASR and related components"""
        self.conformer.language = language
        
        # Update model based on language
        language_models = {
            "en": "speechbrain/asr-conformer-transformerlm-librispeech",
            "pt": "speechbrain/asr-conformer-commonvoice-pt",
            "es": "speechbrain/asr-conformer-commonvoice-es",
            "fr": "speechbrain/asr-conformer-commonvoice-fr",
            "de": "speechbrain/asr-conformer-commonvoice-de",
            "it": "speechbrain/asr-conformer-commonvoice-it"
        }
        
        if language in language_models:
            self.conformer.model_name = language_models[language]
            self.alignment.model_name = f"speechbrain/asr-wav2vec2-commonvoice-{language}"
        else:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Language {language} not optimized, using default English models")
    
    def set_processing_mode(self, mode: ProcessingMode):
        """Set processing mode and adjust parameters accordingly"""
        self.processing_mode = mode
        
        if mode == ProcessingMode.FAST:
            self.sepformer.chunk_length = 16000
            self.conformer.beam_size = 5
            self.llm.max_length = 256
            self.conformer.enable_vad = False
            
        elif mode == ProcessingMode.BALANCED:
            self.sepformer.chunk_length = 32000
            self.conformer.beam_size = 10
            self.llm.max_length = 512
            self.conformer.enable_vad = True
            
        elif mode == ProcessingMode.HIGH_QUALITY:
            self.sepformer.chunk_length = 64000
            self.sepformer.overlap_ratio = 0.2
            self.conformer.beam_size = 20
            self.llm.max_length = 1024
            self.conformer.enable_vad = True
            self.vad.threshold = 0.3  # More sensitive
    
    def get_model_recommendations(self, language: str = "en") -> Dict[str, str]:
        """Get recommended models for specific language"""
        recommendations = {
            "sepformer": "speechbrain/sepformer-wsj02mix",  # Universal
            "conformer": f"speechbrain/asr-conformer-commonvoice-{language}",
            "wav2vec2": f"speechbrain/asr-wav2vec2-commonvoice-{language}",
            "vad": "speechbrain/vad-crdnn-libriparty"
        }
        
        # Fallback to English if language not supported
        supported_languages = ["en", "pt", "es", "fr", "de", "it", "ru", "zh"]
        if language not in supported_languages:
            recommendations["conformer"] = "speechbrain/asr-conformer-transformerlm-librispeech"
            recommendations["wav2vec2"] = "speechbrain/asr-wav2vec2-commonvoice-en"
        
        return recommendations
    
    def save_config(self):
        """Save current configuration to file"""
        config_data = {
            "sepformer": asdict(self.sepformer),
            "conformer": asdict(self.conformer),
            "llm": asdict(self.llm),
            "alignment": asdict(self.alignment),
            "vad": asdict(self.vad),
            "processing_mode": self.processing_mode.value,
            "cache_enabled": self.cache_enabled,
            "cache_path": self.cache_path,
            "device": self.device,
            "max_memory_usage": self.max_memory_usage
        }
        
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        print(f"{ULTRASINGER_HEAD} Configuration saved to {blue_highlighted(self.config_path)}")
    
    def load_config(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Update configurations
            if "sepformer" in config_data:
                self.sepformer = SepFormerConfig(**config_data["sepformer"])
            if "conformer" in config_data:
                self.conformer = ConformerConfig(**config_data["conformer"])
            if "llm" in config_data:
                self.llm = LLMConfig(**config_data["llm"])
            if "alignment" in config_data:
                self.alignment = AlignmentConfig(**config_data["alignment"])
            if "vad" in config_data:
                self.vad = VADConfig(**config_data["vad"])
            
            # Update general settings
            if "processing_mode" in config_data:
                self.processing_mode = ProcessingMode(config_data["processing_mode"])
            if "cache_enabled" in config_data:
                self.cache_enabled = config_data["cache_enabled"]
            if "cache_path" in config_data:
                self.cache_path = config_data["cache_path"]
            
            print(f"{ULTRASINGER_HEAD} Configuration loaded from {blue_highlighted(self.config_path)}")
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to load config: {str(e)}")
    
    def get_cache_path(self, model_type: str, model_name: str) -> str:
        """Get cache path for specific model"""
        safe_name = model_name.replace("/", "_").replace(":", "_")
        return os.path.join(self.cache_path, model_type, safe_name)
    
    def print_current_config(self):
        """Print current configuration summary"""
        print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('SpeechBrain Configuration:')}")
        print(f"  Processing Mode: {blue_highlighted(self.processing_mode.value)}")
        print(f"  Device: {blue_highlighted(self.device)}")
        print(f"  Memory Limit: {blue_highlighted(f'{self.max_memory_usage:.1f}GB')}")
        print(f"  Cache Enabled: {blue_highlighted(str(self.cache_enabled))}")
        print(f"  Language: {blue_highlighted(self.conformer.language)}")
        print(f"  SepFormer Model: {blue_highlighted(self.sepformer.model_name.split('/')[-1])}")
        print(f"  Conformer Model: {blue_highlighted(self.conformer.model_name.split('/')[-1])}")
        print(f"  Batch Sizes: Sep={blue_highlighted(str(self.sepformer.batch_size))}, ASR={blue_highlighted(str(self.conformer.batch_size))}")