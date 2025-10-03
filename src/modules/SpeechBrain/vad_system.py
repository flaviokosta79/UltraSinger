"""
Voice Activity Detection (VAD) System

Advanced VAD using SpeechBrain models for precise speech segmentation,
optimized for karaoke creation with robust silence detection and noise handling.
"""

import os
import torch
import torchaudio
import numpy as np
from typing import Tuple, Optional, Dict, Any, List, Union
from enum import Enum
from pathlib import Path
import time
import json

from speechbrain.inference import VAD

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


class VADModel(Enum):
    """Available VAD models with detailed information"""
    
    MARBLENET = "speechbrain/vad-crdnn-libriparty"
    CRDNN_LIBRIPARTY = "speechbrain/vad-crdnn-libriparty"
    
    @classmethod
    def get_model_info(cls, model: 'VADModel') -> Dict[str, Any]:
        """Get detailed information about a specific VAD model"""
        model_info = {
            cls.MARBLENET: {
                "architecture": "MarbleNet",
                "dataset": "LibriParty",
                "accuracy": "Very High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "General VAD, real-time processing"
            },
            cls.CRDNN_LIBRIPARTY: {
                "architecture": "CRDNN",
                "dataset": "LibriParty",
                "accuracy": "High",
                "speed": "Very Fast",
                "sample_rate": 16000,
                "recommended_for": "Fast VAD, batch processing"
            }
        }
        return model_info.get(model, {})
    
    @classmethod
    def get_recommended_model(cls, priority: str = "accuracy") -> 'VADModel':
        """Get recommended VAD model based on priority"""
        if priority == "speed":
            return cls.CRDNN_LIBRIPARTY
        else:  # accuracy
            return cls.MARBLENET


class VADSegment:
    """Container for VAD segment with speech/silence classification"""
    
    def __init__(self, start: float, end: float, is_speech: bool, confidence: float = 1.0):
        self.start = start
        self.end = end
        self.is_speech = is_speech
        self.confidence = confidence
    
    @property
    def duration(self) -> float:
        """Get segment duration"""
        return self.end - self.start
    
    @property
    def label(self) -> str:
        """Get segment label"""
        return "speech" if self.is_speech else "silence"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "start": self.start,
            "end": self.end,
            "duration": self.duration,
            "is_speech": self.is_speech,
            "label": self.label,
            "confidence": self.confidence
        }


class VADResult:
    """Container for VAD results"""
    
    def __init__(self, segments: List[VADSegment], confidence: float = 1.0):
        self.segments = segments
        self.confidence = confidence
        self.processing_time = 0.0
        self.model_used = ""
        self.total_duration = 0.0
    
    @property
    def speech_segments(self) -> List[VADSegment]:
        """Get only speech segments"""
        return [seg for seg in self.segments if seg.is_speech]
    
    @property
    def silence_segments(self) -> List[VADSegment]:
        """Get only silence segments"""
        return [seg for seg in self.segments if not seg.is_speech]
    
    @property
    def speech_ratio(self) -> float:
        """Get ratio of speech to total duration"""
        if self.total_duration <= 0:
            return 0.0
        
        speech_duration = sum(seg.duration for seg in self.speech_segments)
        return speech_duration / self.total_duration
    
    @property
    def silence_ratio(self) -> float:
        """Get ratio of silence to total duration"""
        return 1.0 - self.speech_ratio
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "segments": [seg.to_dict() for seg in self.segments],
            "confidence": self.confidence,
            "processing_time": self.processing_time,
            "model_used": self.model_used,
            "total_duration": self.total_duration,
            "speech_ratio": self.speech_ratio,
            "silence_ratio": self.silence_ratio,
            "num_speech_segments": len(self.speech_segments),
            "num_silence_segments": len(self.silence_segments)
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def get_speech_intervals(self) -> List[Tuple[float, float]]:
        """Get list of speech intervals as (start, end) tuples"""
        return [(seg.start, seg.end) for seg in self.speech_segments]
    
    def get_silence_intervals(self) -> List[Tuple[float, float]]:
        """Get list of silence intervals as (start, end) tuples"""
        return [(seg.start, seg.end) for seg in self.silence_segments]


class VADSystem:
    """Advanced Voice Activity Detection system"""
    
    def __init__(self, config: SpeechBrainConfig, model_manager: SpeechBrainModelManager):
        self.config = config
        self.model_manager = model_manager
        self.current_model = None
        self.current_model_name = None
        
        # Performance tracking
        self.vad_stats = {
            "total_detections": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "total_audio_duration": 0.0,
            "real_time_factor": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def detect_voice_activity(self,
                             input_path: str,
                             model: Optional[VADModel] = None,
                             use_cache: bool = True,
                             min_speech_duration: float = 0.1,
                             min_silence_duration: float = 0.1,
                             merge_threshold: float = 0.3) -> VADResult:
        """
        Detect voice activity in audio
        
        Args:
            input_path: Path to input audio file
            model: Specific VAD model to use
            use_cache: Whether to use cached results
            min_speech_duration: Minimum duration for speech segments (seconds)
            min_silence_duration: Minimum duration for silence segments (seconds)
            merge_threshold: Threshold for merging nearby speech segments (seconds)
            
        Returns:
            VADResult with speech/silence segments
        """
        start_time = time.time()
        
        # Validate input
        if not check_file_exists(input_path):
            raise FileNotFoundError(f"Input audio file not found: {input_path}")
        
        # Determine model
        model = model or VADModel.get_recommended_model(self.config.vad.priority)
        model_info = VADModel.get_model_info(model)
        
        print(f"{ULTRASINGER_HEAD} Starting VAD with {blue_highlighted(model.value.split('/')[-1])}")
        print(f"{ULTRASINGER_HEAD} Architecture: {blue_highlighted(model_info['architecture'])} - Speed: {blue_highlighted(model_info['speed'])}")
        
        # Check cache
        cache_key = self._get_cache_key(input_path, model.value, min_speech_duration, min_silence_duration)
        if use_cache:
            cached_result = self._check_cache(cache_key)
            if cached_result:
                self.vad_stats["cache_hits"] += 1
                print(f"{ULTRASINGER_HEAD} {green_highlighted('Cache:')} Using cached VAD results")
                return cached_result
        
        self.vad_stats["cache_misses"] += 1
        
        # Load model
        vad_model = self._load_model(model)
        
        # Load and preprocess audio
        waveform, sample_rate, duration = self._load_audio(input_path, model_info["sample_rate"])
        
        print(f"{ULTRASINGER_HEAD} Processing audio: {blue_highlighted(f'{duration:.1f}s')} at {blue_highlighted(f'{sample_rate}Hz')}")
        
        # Perform VAD
        try:
            result = self._perform_vad(
                vad_model,
                waveform,
                sample_rate,
                duration,
                min_speech_duration,
                min_silence_duration,
                merge_threshold
            )
            
            # Set metadata
            result.processing_time = time.time() - start_time
            result.model_used = model.value
            result.total_duration = duration
            
            # Update statistics
            self._update_stats(result.processing_time, duration)
            
            # Cache result
            if use_cache:
                self._save_cache(cache_key, result)
            
            # Calculate real-time factor
            rtf = result.processing_time / duration if duration > 0 else 0
            
            print(f"{ULTRASINGER_HEAD} {green_highlighted('Success:')} VAD completed in {blue_highlighted(f'{result.processing_time:.1f}s')}")
            print(f"{ULTRASINGER_HEAD} Real-time factor: {blue_highlighted(f'{rtf:.2f}x')}")
            print(f"{ULTRASINGER_HEAD} Speech ratio: {blue_highlighted(f'{result.speech_ratio:.1%}')}")
            print(f"{ULTRASINGER_HEAD} Speech segments: {blue_highlighted(f'{len(result.speech_segments)}')} - Silence segments: {blue_highlighted(f'{len(result.silence_segments)}')}")
            
            return result
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} VAD failed: {str(e)}")
            raise e
    
    def _load_model(self, model: VADModel) -> VAD:
        """Load VAD model"""
        if self.current_model_name != model.value:
            print(f"{ULTRASINGER_HEAD} Loading VAD model: {blue_highlighted(model.value.split('/')[-1])}")
            self.current_model = self.model_manager.load_vad_model(model.value)
            self.current_model_name = model.value
        
        return self.current_model
    
    def _load_audio(self, input_path: str, target_sample_rate: int) -> Tuple[torch.Tensor, int, float]:
        """Load and preprocess audio for VAD"""
        try:
            waveform, sample_rate = torchaudio.load(input_path)
            
            # Calculate duration
            duration = waveform.shape[1] / sample_rate
            
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
            
            return waveform, sample_rate, duration
            
        except Exception as e:
            raise RuntimeError(f"Failed to load audio: {str(e)}")
    
    def _perform_vad(self,
                    model: VAD,
                    waveform: torch.Tensor,
                    sample_rate: int,
                    duration: float,
                    min_speech_duration: float,
                    min_silence_duration: float,
                    merge_threshold: float) -> VADResult:
        """Perform voice activity detection"""
        try:
            # Ensure correct device
            device = "cuda" if self.config.vad.use_gpu and torch.cuda.is_available() else "cpu"
            waveform = waveform.to(device)
            
            # Perform VAD
            with torch.no_grad():
                if hasattr(model, 'get_speech_prob_file'):
                    # Use probability-based detection
                    speech_probs = model.get_speech_prob_file(waveform.squeeze(0))
                elif hasattr(model, 'get_boundaries'):
                    # Use boundary detection
                    boundaries = model.get_boundaries(waveform.squeeze(0))
                    speech_probs = self._boundaries_to_probs(boundaries, duration)
                else:
                    # Fallback: use simple energy-based VAD
                    speech_probs = self._energy_based_vad(waveform, sample_rate)
            
            # Convert probabilities to segments
            segments = self._probs_to_segments(
                speech_probs,
                sample_rate,
                duration,
                min_speech_duration,
                min_silence_duration,
                merge_threshold
            )
            
            # Calculate overall confidence
            overall_confidence = np.mean([seg.confidence for seg in segments]) if segments else 0.0
            
            return VADResult(segments=segments, confidence=overall_confidence)
            
        except torch.cuda.OutOfMemoryError:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} GPU out of memory, falling back to CPU")
            # Clear GPU cache and retry on CPU
            torch.cuda.empty_cache()
            waveform = waveform.cpu()
            
            # Reload model on CPU
            self.config.vad.use_gpu = False
            model = self.model_manager.load_vad_model(self.current_model_name)
            
            with torch.no_grad():
                if hasattr(model, 'get_speech_prob_file'):
                    speech_probs = model.get_speech_prob_file(waveform.squeeze(0))
                elif hasattr(model, 'get_boundaries'):
                    boundaries = model.get_boundaries(waveform.squeeze(0))
                    speech_probs = self._boundaries_to_probs(boundaries, duration)
                else:
                    speech_probs = self._energy_based_vad(waveform, sample_rate)
            
            segments = self._probs_to_segments(
                speech_probs,
                sample_rate,
                duration,
                min_speech_duration,
                min_silence_duration,
                merge_threshold
            )
            
            overall_confidence = np.mean([seg.confidence for seg in segments]) if segments else 0.0
            return VADResult(segments=segments, confidence=overall_confidence)
    
    def _boundaries_to_probs(self, boundaries: List[Tuple[float, float]], duration: float) -> np.ndarray:
        """Convert boundary list to probability array"""
        # Create probability array with 100ms resolution
        time_resolution = 0.1  # 100ms
        num_frames = int(duration / time_resolution) + 1
        probs = np.zeros(num_frames)
        
        # Mark speech regions
        for start, end in boundaries:
            start_frame = int(start / time_resolution)
            end_frame = int(end / time_resolution)
            probs[start_frame:end_frame] = 1.0
        
        return probs
    
    def _energy_based_vad(self, waveform: torch.Tensor, sample_rate: int) -> np.ndarray:
        """Fallback energy-based VAD"""
        # Frame-based energy calculation
        frame_length = int(0.025 * sample_rate)  # 25ms frames
        hop_length = int(0.01 * sample_rate)     # 10ms hop
        
        # Calculate frame energy
        waveform_np = waveform.squeeze().cpu().numpy()
        frames = []
        
        for i in range(0, len(waveform_np) - frame_length, hop_length):
            frame = waveform_np[i:i + frame_length]
            energy = np.sum(frame ** 2)
            frames.append(energy)
        
        frames = np.array(frames)
        
        # Normalize and threshold
        if len(frames) > 0:
            frames = frames / np.max(frames) if np.max(frames) > 0 else frames
            
            # Adaptive threshold based on energy distribution
            threshold = np.percentile(frames, 30)  # 30th percentile as threshold
            speech_probs = (frames > threshold).astype(float)
        else:
            speech_probs = np.array([0.0])
        
        return speech_probs
    
    def _probs_to_segments(self,
                          speech_probs: np.ndarray,
                          sample_rate: int,
                          duration: float,
                          min_speech_duration: float,
                          min_silence_duration: float,
                          merge_threshold: float) -> List[VADSegment]:
        """Convert speech probabilities to segments"""
        
        # Determine time resolution
        time_resolution = duration / len(speech_probs) if len(speech_probs) > 0 else 0.01
        
        # Threshold probabilities
        threshold = 0.5
        is_speech = speech_probs > threshold
        
        # Find segment boundaries
        segments = []
        current_state = None
        current_start = 0.0
        
        for i, speech_flag in enumerate(is_speech):
            current_time = i * time_resolution
            
            if current_state is None:
                # First frame
                current_state = speech_flag
                current_start = current_time
            elif current_state != speech_flag:
                # State change
                segment_duration = current_time - current_start
                
                # Apply minimum duration filters
                if current_state and segment_duration >= min_speech_duration:
                    # Speech segment
                    confidence = np.mean(speech_probs[int(current_start/time_resolution):i])
                    segments.append(VADSegment(current_start, current_time, True, confidence))
                elif not current_state and segment_duration >= min_silence_duration:
                    # Silence segment
                    confidence = 1.0 - np.mean(speech_probs[int(current_start/time_resolution):i])
                    segments.append(VADSegment(current_start, current_time, False, confidence))
                
                current_state = speech_flag
                current_start = current_time
        
        # Handle final segment
        if current_state is not None:
            segment_duration = duration - current_start
            if current_state and segment_duration >= min_speech_duration:
                confidence = np.mean(speech_probs[int(current_start/time_resolution):])
                segments.append(VADSegment(current_start, duration, True, confidence))
            elif not current_state and segment_duration >= min_silence_duration:
                confidence = 1.0 - np.mean(speech_probs[int(current_start/time_resolution):])
                segments.append(VADSegment(current_start, duration, False, confidence))
        
        # Merge nearby speech segments
        segments = self._merge_speech_segments(segments, merge_threshold)
        
        # Fill gaps with silence segments
        segments = self._fill_silence_gaps(segments, duration)
        
        # Sort by start time
        segments.sort(key=lambda x: x.start)
        
        return segments
    
    def _merge_speech_segments(self, segments: List[VADSegment], merge_threshold: float) -> List[VADSegment]:
        """Merge nearby speech segments"""
        if not segments:
            return segments
        
        merged = []
        current_speech = None
        
        for segment in segments:
            if segment.is_speech:
                if current_speech is None:
                    current_speech = segment
                else:
                    # Check if segments are close enough to merge
                    gap = segment.start - current_speech.end
                    if gap <= merge_threshold:
                        # Merge segments
                        current_speech.end = segment.end
                        current_speech.confidence = (current_speech.confidence + segment.confidence) / 2
                    else:
                        # Add previous speech segment and start new one
                        merged.append(current_speech)
                        current_speech = segment
            else:
                # Silence segment
                if current_speech is not None:
                    merged.append(current_speech)
                    current_speech = None
                merged.append(segment)
        
        # Add final speech segment if exists
        if current_speech is not None:
            merged.append(current_speech)
        
        return merged
    
    def _fill_silence_gaps(self, segments: List[VADSegment], total_duration: float) -> List[VADSegment]:
        """Fill gaps between segments with silence"""
        if not segments:
            return [VADSegment(0.0, total_duration, False, 1.0)]
        
        filled = []
        current_time = 0.0
        
        for segment in sorted(segments, key=lambda x: x.start):
            # Add silence before this segment if there's a gap
            if segment.start > current_time:
                filled.append(VADSegment(current_time, segment.start, False, 1.0))
            
            filled.append(segment)
            current_time = segment.end
        
        # Add final silence if needed
        if current_time < total_duration:
            filled.append(VADSegment(current_time, total_duration, False, 1.0))
        
        return filled
    
    def _get_cache_key(self, input_path: str, model_name: str, min_speech: float, min_silence: float) -> str:
        """Generate cache key for VAD"""
        import hashlib
        
        # Get file stats for cache invalidation
        try:
            stat = os.stat(input_path)
            file_info = f"{stat.st_size}_{stat.st_mtime}"
        except:
            file_info = "unknown"
        
        cache_string = f"{input_path}_{model_name}_{min_speech}_{min_silence}_{file_info}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[VADResult]:
        """Check for cached VAD result"""
        cache_dir = os.path.join(os.path.dirname(__file__), ".cache", "vad")
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct segments
            segments = []
            for seg_data in data["segments"]:
                segment = VADSegment(
                    start=seg_data["start"],
                    end=seg_data["end"],
                    is_speech=seg_data["is_speech"],
                    confidence=seg_data["confidence"]
                )
                segments.append(segment)
            
            result = VADResult(segments=segments, confidence=data["confidence"])
            result.processing_time = data.get("processing_time", 0.0)
            result.model_used = data.get("model_used", "")
            result.total_duration = data.get("total_duration", 0.0)
            
            return result
            
        except Exception:
            return None
    
    def _save_cache(self, cache_key: str, result: VADResult):
        """Save VAD result to cache"""
        cache_dir = os.path.join(os.path.dirname(__file__), ".cache", "vad")
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to save VAD cache: {str(e)}")
    
    def _update_stats(self, processing_time: float, audio_duration: float):
        """Update performance statistics"""
        self.vad_stats["total_detections"] += 1
        self.vad_stats["total_time"] += processing_time
        self.vad_stats["total_audio_duration"] += audio_duration
        
        # Calculate averages
        total_detections = self.vad_stats["total_detections"]
        self.vad_stats["average_time"] = self.vad_stats["total_time"] / total_detections
        
        if self.vad_stats["total_audio_duration"] > 0:
            self.vad_stats["real_time_factor"] = (
                self.vad_stats["total_time"] / self.vad_stats["total_audio_duration"]
            )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.vad_stats.copy()
    
    def print_performance_stats(self):
        """Print performance statistics"""
        stats = self.vad_stats
        
        print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('VAD Performance Stats:')}")
        print(f"  Total Detections: {blue_highlighted(str(stats['total_detections']))}")
        avg_time_text = f"{stats['average_time']:.1f}s"
        print(f"  Average Time: {blue_highlighted(avg_time_text)}")
        rtf_text = f"{stats['real_time_factor']:.2f}x"
        print(f"  Real-time Factor: {blue_highlighted(rtf_text)}")
        cache_rate = f"{stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%" if stats['cache_hits']+stats['cache_misses'] > 0 else '0%'
        print(f"  Cache Hit Rate: {blue_highlighted(cache_rate)}")
    
    def clear_cache(self):
        """Clear VAD cache"""
        cache_dir = os.path.join(os.path.dirname(__file__), ".cache", "vad")
        try:
            if os.path.exists(cache_dir):
                import shutil
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
                print(f"{ULTRASINGER_HEAD} Cleared VAD cache")
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to clear cache: {str(e)}")


def get_available_models() -> List[VADModel]:
    """Get list of available VAD models"""
    return list(VADModel)


def get_recommended_model(priority: str = "accuracy") -> VADModel:
    """Get recommended VAD model based on priority"""
    return VADModel.get_recommended_model(priority)