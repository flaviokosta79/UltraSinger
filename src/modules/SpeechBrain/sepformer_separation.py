"""
SepFormer Audio Separation Module

Advanced vocal/instrumental separation using SpeechBrain's SepFormer models,
optimized for karaoke creation with intelligent caching and performance optimization.
"""

import os
import torch
import torchaudio
import numpy as np
from typing import Tuple, Optional, Dict, Any, List
from enum import Enum
from pathlib import Path
import time

from speechbrain.inference import SepformerSeparation

from modules.console_colors import (
    ULTRASINGER_HEAD,
    blue_highlighted,
    green_highlighted,
    yellow_highlighted,
    red_highlighted
)
from modules.os_helper import check_file_exists
from .config_manager import SpeechBrainConfig
from .model_manager import SpeechBrainModelManager


class SepFormerModel(Enum):
    """Available SepFormer models with detailed information"""
    
    WSJ02MIX = "speechbrain/sepformer-wsj02mix"
    WSJ03MIX = "speechbrain/sepformer-wsj03mix"
    WHAM = "speechbrain/sepformer-wham"
    WHAMR = "speechbrain/sepformer-whamr"
    LIBRI2MIX = "speechbrain/sepformer-libri2mix"
    LIBRI3MIX = "speechbrain/sepformer-libri3mix"
    
    @classmethod
    def get_model_info(cls, model: 'SepFormerModel') -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        model_info = {
            cls.WSJ02MIX: {
                "description": "2-speaker separation trained on WSJ0-2mix",
                "speakers": 2,
                "quality": "High",
                "speed": "Fast",
                "sample_rate": 8000,
                "recommended_for": "General vocal separation, karaoke"
            },
            cls.WSJ03MIX: {
                "description": "3-speaker separation trained on WSJ0-3mix",
                "speakers": 3,
                "quality": "High",
                "speed": "Medium",
                "sample_rate": 8000,
                "recommended_for": "Complex multi-speaker scenarios"
            },
            cls.WHAM: {
                "description": "Separation with background noise (WHAM dataset)",
                "speakers": 2,
                "quality": "Very High",
                "speed": "Medium",
                "sample_rate": 8000,
                "recommended_for": "Noisy environments, live recordings"
            },
            cls.WHAMR: {
                "description": "Separation with noise and reverb (WHAM! dataset)",
                "speakers": 2,
                "quality": "Excellent",
                "speed": "Slow",
                "sample_rate": 8000,
                "recommended_for": "Reverberant, noisy recordings"
            },
            cls.LIBRI2MIX: {
                "description": "2-speaker separation trained on Libri2Mix",
                "speakers": 2,
                "quality": "Very High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "High-quality speech separation"
            },
            cls.LIBRI3MIX: {
                "description": "3-speaker separation trained on Libri3Mix",
                "speakers": 3,
                "quality": "Very High",
                "speed": "Medium",
                "sample_rate": 16000,
                "recommended_for": "Multi-speaker high-quality separation"
            }
        }
        return model_info.get(model, {})
    
    @classmethod
    def get_recommended_model(cls, use_case: str = "karaoke") -> 'SepFormerModel':
        """Get recommended model based on use case"""
        recommendations = {
            "karaoke": cls.WSJ02MIX,  # Best for vocal/instrumental separation
            "noisy": cls.WHAM,        # Best for noisy recordings
            "reverb": cls.WHAMR,      # Best for reverberant recordings
            "high_quality": cls.LIBRI2MIX,  # Best quality for clean recordings
            "multi_speaker": cls.WSJ03MIX   # Best for multiple speakers
        }
        return recommendations.get(use_case, cls.WSJ02MIX)


class SepFormerSeparator:
    """Advanced audio separation using SpeechBrain SepFormer models"""
    
    def __init__(self, config: SpeechBrainConfig, model_manager: SpeechBrainModelManager):
        self.config = config
        self.model_manager = model_manager
        self.current_model = None
        self.current_model_name = None
        
        # Performance tracking
        self.separation_stats = {
            "total_separations": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def separate_audio(self, 
                      input_path: str, 
                      output_dir: str,
                      model: Optional[SepFormerModel] = None,
                      use_cache: bool = True,
                      normalize_output: bool = True,
                      target_sample_rate: Optional[int] = None) -> Tuple[str, str, Dict[str, Any]]:
        """
        Separate audio into vocal and instrumental tracks
        
        Args:
            input_path: Path to input audio file
            output_dir: Directory to save separated audio
            model: SepFormer model to use (default from config)
            use_cache: Whether to use cached results
            normalize_output: Whether to normalize output audio
            target_sample_rate: Target sample rate for output (None = keep original)
            
        Returns:
            Tuple of (vocal_path, instrumental_path, separation_info)
        """
        start_time = time.time()
        
        # Validate input
        if not check_file_exists(input_path):
            raise FileNotFoundError(f"Input audio file not found: {input_path}")
        
        # Determine model
        model = model or SepFormerModel(self.config.sepformer.model_name)
        model_info = SepFormerModel.get_model_info(model)
        
        print(f"{ULTRASINGER_HEAD} Starting SepFormer separation with {blue_highlighted(model.value.split('/')[-1])}")
        print(f"{ULTRASINGER_HEAD} Model info: {model_info['description']} - Quality: {blue_highlighted(model_info['quality'])}")
        
        # Setup output paths
        os.makedirs(output_dir, exist_ok=True)
        base_name = Path(input_path).stem
        vocal_path = os.path.join(output_dir, f"{base_name}_vocals.wav")
        instrumental_path = os.path.join(output_dir, f"{base_name}_instrumental.wav")
        
        # Check cache
        if use_cache and self._check_cache(vocal_path, instrumental_path):
            self.separation_stats["cache_hits"] += 1
            print(f"{ULTRASINGER_HEAD} {green_highlighted('Cache:')} Using cached separation results")
            
            separation_info = {
                "model_used": model.value,
                "processing_time": 0.0,
                "from_cache": True,
                "sample_rate": self._get_audio_info(vocal_path)["sample_rate"],
                "quality_score": self._estimate_quality(vocal_path, instrumental_path)
            }
            
            return vocal_path, instrumental_path, separation_info
        
        self.separation_stats["cache_misses"] += 1
        
        # Load model
        separator = self._load_model(model)
        
        # Load and preprocess audio
        waveform, sample_rate = self._load_audio(input_path, model_info["sample_rate"])
        
        duration_text = f"{waveform.shape[1]/sample_rate:.1f}s"
        sample_rate_text = f"{sample_rate}Hz"
        print(f"{ULTRASINGER_HEAD} Processing audio: {blue_highlighted(duration_text)} at {blue_highlighted(sample_rate_text)}")
        
        # Perform separation
        try:
            separated_sources = self._perform_separation(separator, waveform, sample_rate)
            
            # Process and save results
            self._save_separated_audio(
                separated_sources, 
                vocal_path, 
                instrumental_path,
                sample_rate,
                target_sample_rate,
                normalize_output
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            self._update_stats(processing_time)
            
            # Validate results
            quality_score = self._estimate_quality(vocal_path, instrumental_path)
            
            separation_info = {
                "model_used": model.value,
                "processing_time": processing_time,
                "from_cache": False,
                "sample_rate": target_sample_rate or sample_rate,
                "quality_score": quality_score,
                "input_duration": waveform.shape[1] / sample_rate,
                "output_vocal_size": os.path.getsize(vocal_path) / (1024 * 1024),  # MB
                "output_instrumental_size": os.path.getsize(instrumental_path) / (1024 * 1024)  # MB
            }
            
            print(f"{ULTRASINGER_HEAD} {green_highlighted('Success:')} Separation completed in {blue_highlighted(f'{processing_time:.1f}s')}")
            print(f"{ULTRASINGER_HEAD} Quality score: {blue_highlighted(f'{quality_score:.2f}')}")
            print(f"{ULTRASINGER_HEAD} Output files:")
            vocal_size_text = f"{separation_info['output_vocal_size']:.1f}MB"
            instrumental_size_text = f"{separation_info['output_instrumental_size']:.1f}MB"
            print(f"  - Vocals: {blue_highlighted(vocal_size_text)}")
            print(f"  - Instrumental: {blue_highlighted(instrumental_size_text)}")
            
            return vocal_path, instrumental_path, separation_info
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Separation failed: {str(e)}")
            # Clean up partial files
            for path in [vocal_path, instrumental_path]:
                if os.path.exists(path):
                    os.remove(path)
            raise e
    
    def _load_model(self, model: SepFormerModel) -> SepformerSeparation:
        """Load SepFormer model"""
        if self.current_model_name != model.value:
            print(f"{ULTRASINGER_HEAD} Loading model: {blue_highlighted(model.value.split('/')[-1])}")
            self.current_model = self.model_manager.load_sepformer_model(model.value)
            self.current_model_name = model.value
        
        return self.current_model
    
    def _load_audio(self, input_path: str, target_sample_rate: int) -> Tuple[torch.Tensor, int]:
        """Load and preprocess audio"""
        try:
            waveform, sample_rate = torchaudio.load(input_path)
            
            # Resample if necessary
            if sample_rate != target_sample_rate:
                resampler = torchaudio.transforms.Resample(sample_rate, target_sample_rate)
                waveform = resampler(waveform)
                sample_rate = target_sample_rate
                print(f"{ULTRASINGER_HEAD} Resampled audio to {blue_highlighted(f'{sample_rate}Hz')}")
            
            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
                print(f"{ULTRASINGER_HEAD} Converted stereo to mono")
            
            return waveform, sample_rate
            
        except Exception as e:
            raise RuntimeError(f"Failed to load audio: {str(e)}")
    
    def _perform_separation(self, separator: SepformerSeparation, waveform: torch.Tensor, sample_rate: int) -> torch.Tensor:
        """Perform the actual separation"""
        try:
            # Ensure correct device
            device = "cuda" if self.config.sepformer.use_gpu and torch.cuda.is_available() else "cpu"
            waveform = waveform.to(device)
            
            # Perform separation
            with torch.no_grad():
                if hasattr(separator, 'separate_batch'):
                    # Use batch separation if available
                    separated = separator.separate_batch(waveform.unsqueeze(0))
                    separated = separated.squeeze(0)
                else:
                    # Use single separation
                    separated = separator.separate_sources(waveform.squeeze(0))
            
            return separated
            
        except torch.cuda.OutOfMemoryError:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} GPU out of memory, falling back to CPU")
            # Clear GPU cache and retry on CPU
            torch.cuda.empty_cache()
            waveform = waveform.cpu()
            
            # Reload model on CPU
            self.config.sepformer.use_gpu = False
            separator = self.model_manager.load_sepformer_model(self.current_model_name)
            
            with torch.no_grad():
                if hasattr(separator, 'separate_batch'):
                    separated = separator.separate_batch(waveform.unsqueeze(0))
                    separated = separated.squeeze(0)
                else:
                    separated = separator.separate_sources(waveform.squeeze(0))
            
            return separated
    
    def _save_separated_audio(self, 
                            separated_sources: torch.Tensor,
                            vocal_path: str,
                            instrumental_path: str,
                            original_sample_rate: int,
                            target_sample_rate: Optional[int],
                            normalize: bool):
        """Save separated audio sources"""
        
        # Move to CPU for saving
        separated_sources = separated_sources.cpu()
        
        # Extract sources (assuming first is vocals, second is instrumental)
        if separated_sources.shape[0] >= 2:
            vocals = separated_sources[0:1]  # Keep channel dimension
            instrumental = separated_sources[1:2]
        else:
            # Fallback: use original as instrumental, separated as vocals
            vocals = separated_sources[0:1]
            instrumental = separated_sources[0:1] * 0.1  # Placeholder
        
        # Normalize if requested
        if normalize:
            vocals = self._normalize_audio(vocals)
            instrumental = self._normalize_audio(instrumental)
        
        # Resample if target sample rate is different
        final_sample_rate = target_sample_rate or original_sample_rate
        if final_sample_rate != original_sample_rate:
            resampler = torchaudio.transforms.Resample(original_sample_rate, final_sample_rate)
            vocals = resampler(vocals)
            instrumental = resampler(instrumental)
        
        # Save audio files
        torchaudio.save(vocal_path, vocals, final_sample_rate)
        torchaudio.save(instrumental_path, instrumental, final_sample_rate)
    
    def _normalize_audio(self, audio: torch.Tensor, target_db: float = -20.0) -> torch.Tensor:
        """Normalize audio to target dB level"""
        # Calculate RMS
        rms = torch.sqrt(torch.mean(audio ** 2))
        
        # Avoid division by zero
        if rms < 1e-8:
            return audio
        
        # Calculate scaling factor
        target_rms = 10 ** (target_db / 20.0)
        scale_factor = target_rms / rms
        
        # Apply scaling with clipping protection
        normalized = audio * scale_factor
        normalized = torch.clamp(normalized, -0.95, 0.95)
        
        return normalized
    
    def _check_cache(self, vocal_path: str, instrumental_path: str) -> bool:
        """Check if cached separation results exist and are valid"""
        if not (check_file_exists(vocal_path) and check_file_exists(instrumental_path)):
            return False
        
        # Check file sizes (should be > 1KB)
        try:
            vocal_size = os.path.getsize(vocal_path)
            instrumental_size = os.path.getsize(instrumental_path)
            return vocal_size > 1024 and instrumental_size > 1024
        except:
            return False
    
    def _get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """Get audio file information"""
        try:
            info = torchaudio.info(audio_path)
            return {
                "sample_rate": info.sample_rate,
                "num_channels": info.num_channels,
                "num_frames": info.num_frames,
                "duration": info.num_frames / info.sample_rate
            }
        except:
            return {"sample_rate": 16000, "num_channels": 1, "num_frames": 0, "duration": 0.0}
    
    def _estimate_quality(self, vocal_path: str, instrumental_path: str) -> float:
        """Estimate separation quality (simplified metric)"""
        try:
            # Load both files
            vocals, _ = torchaudio.load(vocal_path)
            instrumental, _ = torchaudio.load(instrumental_path)
            
            # Calculate energy ratio
            vocal_energy = torch.mean(vocals ** 2)
            instrumental_energy = torch.mean(instrumental ** 2)
            
            # Simple quality metric based on energy distribution
            total_energy = vocal_energy + instrumental_energy
            if total_energy > 0:
                balance = min(vocal_energy, instrumental_energy) / total_energy
                return float(balance * 2)  # Scale to 0-1 range
            else:
                return 0.0
                
        except:
            return 0.5  # Default quality score
    
    def _update_stats(self, processing_time: float):
        """Update performance statistics"""
        self.separation_stats["total_separations"] += 1
        self.separation_stats["total_time"] += processing_time
        self.separation_stats["average_time"] = (
            self.separation_stats["total_time"] / self.separation_stats["total_separations"]
        )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.separation_stats.copy()
    
    def print_performance_stats(self):
        """Print performance statistics"""
        stats = self.separation_stats
        
        print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('SepFormer Performance Stats:')}")
        print(f"  Total Separations: {blue_highlighted(str(stats['total_separations']))}")
        avg_time_text = f"{stats['average_time']:.1f}s"
        print(f"  Average Time: {blue_highlighted(avg_time_text)}")
        cache_rate = f"{stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%" if stats['cache_hits']+stats['cache_misses'] > 0 else '0%'
        print(f"  Cache Hit Rate: {blue_highlighted(cache_rate)}")
        total_time_text = f"{stats['total_time']:.1f}s"
        print(f"  Total Processing Time: {blue_highlighted(total_time_text)}")
    
    def clear_cache(self, output_dir: str):
        """Clear cached separation results"""
        try:
            if os.path.exists(output_dir):
                for file in os.listdir(output_dir):
                    if file.endswith(('_vocals.wav', '_instrumental.wav')):
                        os.remove(os.path.join(output_dir, file))
                print(f"{ULTRASINGER_HEAD} Cleared separation cache in {blue_highlighted(output_dir)}")
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to clear cache: {str(e)}")


def get_available_models() -> List[SepFormerModel]:
    """Get list of available SepFormer models"""
    return list(SepFormerModel)


def get_recommended_model(use_case: str = "karaoke") -> SepFormerModel:
    """Get recommended SepFormer model for specific use case"""
    return SepFormerModel.get_recommended_model(use_case)