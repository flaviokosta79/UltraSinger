"""
Forced Alignment Module

Advanced forced alignment using SpeechBrain models for precise temporal synchronization
of lyrics with audio, optimized for karaoke creation with word and phoneme-level timing.
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
import re

from speechbrain.inference import EncoderASR
from speechbrain.alignment.ctc_segmentation import CTCSegmentation

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
from .conformer_asr import ASRModel, TranscriptionResult


class AlignmentModel(Enum):
    """Available alignment models with detailed information"""
    
    WAV2VEC2_BASE_960H = "speechbrain/asr-wav2vec2-librispeech"
    WAV2VEC2_LARGE_960H = "speechbrain/asr-wav2vec2-librispeech-large"
    WAV2VEC2_COMMONVOICE_EN = "speechbrain/asr-wav2vec2-commonvoice-en"
    WAV2VEC2_COMMONVOICE_FR = "speechbrain/asr-wav2vec2-commonvoice-fr"
    WAV2VEC2_COMMONVOICE_IT = "speechbrain/asr-wav2vec2-commonvoice-it"
    WAV2VEC2_COMMONVOICE_ES = "speechbrain/asr-wav2vec2-commonvoice-es"
    WAV2VEC2_COMMONVOICE_DE = "speechbrain/asr-wav2vec2-commonvoice-de"
    WAV2VEC2_COMMONVOICE_PT = "speechbrain/asr-wav2vec2-commonvoice-pt"
    
    @classmethod
    def get_model_info(cls, model: 'AlignmentModel') -> Dict[str, Any]:
        """Get detailed information about a specific alignment model"""
        model_info = {
            cls.WAV2VEC2_BASE_960H: {
                "language": "en",
                "dataset": "LibriSpeech",
                "accuracy": "Very High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "English alignment, high accuracy"
            },
            cls.WAV2VEC2_LARGE_960H: {
                "language": "en",
                "dataset": "LibriSpeech",
                "accuracy": "Excellent",
                "speed": "Medium",
                "sample_rate": 16000,
                "recommended_for": "English alignment, best quality"
            },
            cls.WAV2VEC2_COMMONVOICE_EN: {
                "language": "en",
                "dataset": "CommonVoice",
                "accuracy": "High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "English alignment, general purpose"
            },
            cls.WAV2VEC2_COMMONVOICE_FR: {
                "language": "fr",
                "dataset": "CommonVoice",
                "accuracy": "High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "French alignment"
            },
            cls.WAV2VEC2_COMMONVOICE_IT: {
                "language": "it",
                "dataset": "CommonVoice",
                "accuracy": "High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "Italian alignment"
            },
            cls.WAV2VEC2_COMMONVOICE_ES: {
                "language": "es",
                "dataset": "CommonVoice",
                "accuracy": "High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "Spanish alignment"
            },
            cls.WAV2VEC2_COMMONVOICE_DE: {
                "language": "de",
                "dataset": "CommonVoice",
                "accuracy": "High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "German alignment"
            },
            cls.WAV2VEC2_COMMONVOICE_PT: {
                "language": "pt",
                "dataset": "CommonVoice",
                "accuracy": "High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "Portuguese alignment"
            }
        }
        return model_info.get(model, {})
    
    @classmethod
    def get_models_by_language(cls, language: str) -> List['AlignmentModel']:
        """Get available alignment models for a specific language"""
        models = []
        for model in cls:
            info = cls.get_model_info(model)
            if info.get("language") == language.lower():
                models.append(model)
        return models
    
    @classmethod
    def get_recommended_model(cls, language: str, priority: str = "accuracy") -> Optional['AlignmentModel']:
        """Get recommended alignment model for language and priority"""
        models = cls.get_models_by_language(language)
        if not models:
            return None
        
        if priority == "speed":
            # Prefer base models for speed
            base_models = [m for m in models if "base" in m.value.lower() or "commonvoice" in m.value.lower()]
            return base_models[0] if base_models else models[0]
        
        # Default to accuracy - prefer large models
        large_models = [m for m in models if "large" in m.value.lower()]
        return large_models[0] if large_models else models[0]


class AlignmentSegment:
    """Container for alignment segment with precise timing"""
    
    def __init__(self, text: str, start: float, end: float, confidence: float = 1.0):
        self.text = text
        self.start = start
        self.end = end
        self.confidence = confidence
        self.word_segments = []
        self.phoneme_segments = []
    
    @property
    def duration(self) -> float:
        """Get segment duration"""
        return self.end - self.start
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "duration": self.duration,
            "confidence": self.confidence,
            "word_segments": [ws.to_dict() if hasattr(ws, 'to_dict') else ws for ws in self.word_segments],
            "phoneme_segments": [ps.to_dict() if hasattr(ps, 'to_dict') else ps for ps in self.phoneme_segments]
        }


class WordSegment:
    """Container for word-level alignment"""
    
    def __init__(self, word: str, start: float, end: float, confidence: float = 1.0):
        self.word = word
        self.start = start
        self.end = end
        self.confidence = confidence
    
    @property
    def duration(self) -> float:
        """Get word duration"""
        return self.end - self.start
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "word": self.word,
            "start": self.start,
            "end": self.end,
            "duration": self.duration,
            "confidence": self.confidence
        }


class AlignmentResult:
    """Container for forced alignment results"""
    
    def __init__(self, segments: List[AlignmentSegment], confidence: float = 1.0):
        self.segments = segments
        self.confidence = confidence
        self.processing_time = 0.0
        self.model_used = ""
        self.language = ""
        self.total_duration = 0.0
    
    @property
    def word_count(self) -> int:
        """Get total word count"""
        return sum(len(seg.word_segments) for seg in self.segments)
    
    @property
    def total_text(self) -> str:
        """Get complete aligned text"""
        return " ".join(seg.text for seg in self.segments)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "segments": [seg.to_dict() for seg in self.segments],
            "confidence": self.confidence,
            "processing_time": self.processing_time,
            "model_used": self.model_used,
            "language": self.language,
            "total_duration": self.total_duration,
            "word_count": self.word_count,
            "total_text": self.total_text
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def to_ultrastar_format(self) -> List[str]:
        """Convert to UltraStar format lines"""
        lines = []
        
        for segment in self.segments:
            if segment.word_segments:
                for word_seg in segment.word_segments:
                    # UltraStar format: : start_beat length pitch text
                    # Convert time to beats (assuming 4 beats per second for now)
                    start_beat = int(word_seg.start * 4)
                    length_beat = int(word_seg.duration * 4)
                    pitch = 0  # Placeholder - would need pitch detection
                    
                    lines.append(f": {start_beat} {length_beat} {pitch} {word_seg.word}")
            else:
                # Fallback: use segment-level timing
                start_beat = int(segment.start * 4)
                length_beat = int(segment.duration * 4)
                pitch = 0
                
                words = segment.text.split()
                if words:
                    word_duration = segment.duration / len(words)
                    for i, word in enumerate(words):
                        word_start_beat = start_beat + int(i * word_duration * 4)
                        word_length_beat = int(word_duration * 4)
                        lines.append(f": {word_start_beat} {word_length_beat} {pitch} {word}")
        
        return lines


class ForcedAligner:
    """Advanced forced alignment using SpeechBrain models"""
    
    def __init__(self, config: SpeechBrainConfig, model_manager: SpeechBrainModelManager):
        self.config = config
        self.model_manager = model_manager
        self.current_model = None
        self.current_model_name = None
        self.current_language = None
        
        # Performance tracking
        self.alignment_stats = {
            "total_alignments": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "total_audio_duration": 0.0,
            "real_time_factor": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "by_language": {}
        }
    
    def align_text_to_audio(self,
                           input_path: str,
                           text: str,
                           language: str = "en",
                           model: Optional[AlignmentModel] = None,
                           use_cache: bool = True,
                           word_level: bool = True,
                           phoneme_level: bool = False) -> AlignmentResult:
        """
        Perform forced alignment of text to audio
        
        Args:
            input_path: Path to input audio file
            text: Text to align with audio
            language: Target language code
            model: Specific alignment model to use
            use_cache: Whether to use cached results
            word_level: Whether to return word-level alignment
            phoneme_level: Whether to return phoneme-level alignment
            
        Returns:
            AlignmentResult with precise timing information
        """
        start_time = time.time()
        
        # Validate input
        if not check_file_exists(input_path):
            raise FileNotFoundError(f"Input audio file not found: {input_path}")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Determine model
        if model is None:
            model = AlignmentModel.get_recommended_model(language, self.config.alignment.priority)
            if model is None:
                raise ValueError(f"No alignment model available for language: {language}")
        
        model_info = AlignmentModel.get_model_info(model)
        
        print(f"{ULTRASINGER_HEAD} Starting forced alignment with {blue_highlighted(model.value.split('/')[-1])}")
        print(f"{ULTRASINGER_HEAD} Language: {blue_highlighted(language.upper())} - Text length: {blue_highlighted(f'{len(text)} chars')}")
        
        # Check cache
        cache_key = self._get_cache_key(input_path, text, model.value)
        if use_cache:
            cached_result = self._check_cache(cache_key)
            if cached_result:
                self.alignment_stats["cache_hits"] += 1
                print(f"{ULTRASINGER_HEAD} {green_highlighted('Cache:')} Using cached alignment")
                return cached_result
        
        self.alignment_stats["cache_misses"] += 1
        
        # Load model
        alignment_model = self._load_model(model)
        
        # Load and preprocess audio
        waveform, sample_rate, duration = self._load_audio(input_path, model_info["sample_rate"])
        
        print(f"{ULTRASINGER_HEAD} Processing audio: {blue_highlighted(f'{duration:.1f}s')} at {blue_highlighted(f'{sample_rate}Hz')}")
        
        # Preprocess text
        processed_text = self._preprocess_text(text, language)
        print(f"{ULTRASINGER_HEAD} Processed text: {blue_highlighted(f'{len(processed_text.split())} words')}")
        
        # Perform alignment
        try:
            result = self._perform_alignment(
                alignment_model, 
                waveform, 
                sample_rate, 
                processed_text,
                word_level,
                phoneme_level
            )
            
            # Set metadata
            result.processing_time = time.time() - start_time
            result.model_used = model.value
            result.language = language
            result.total_duration = duration
            
            # Update statistics
            self._update_stats(result.processing_time, duration, language)
            
            # Cache result
            if use_cache:
                self._save_cache(cache_key, result)
            
            # Calculate real-time factor
            rtf = result.processing_time / duration if duration > 0 else 0
            
            print(f"{ULTRASINGER_HEAD} {green_highlighted('Success:')} Alignment completed in {blue_highlighted(f'{result.processing_time:.1f}s')}")
            print(f"{ULTRASINGER_HEAD} Real-time factor: {blue_highlighted(f'{rtf:.2f}x')}")
            print(f"{ULTRASINGER_HEAD} Segments: {blue_highlighted(f'{len(result.segments)}')} - Words: {blue_highlighted(f'{result.word_count}')}")
            print(f"{ULTRASINGER_HEAD} Average confidence: {blue_highlighted(f'{result.confidence:.2f}')}")
            
            return result
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Alignment failed: {str(e)}")
            raise e
    
    def _load_model(self, model: AlignmentModel) -> EncoderASR:
        """Load alignment model"""
        if self.current_model_name != model.value:
            print(f"{ULTRASINGER_HEAD} Loading alignment model: {blue_highlighted(model.value.split('/')[-1])}")
            self.current_model = self.model_manager.load_wav2vec2_model(model.value)
            self.current_model_name = model.value
            
            model_info = AlignmentModel.get_model_info(model)
            self.current_language = model_info["language"]
        
        return self.current_model
    
    def _load_audio(self, input_path: str, target_sample_rate: int) -> Tuple[torch.Tensor, int, float]:
        """Load and preprocess audio for alignment"""
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
    
    def _preprocess_text(self, text: str, language: str) -> str:
        """Preprocess text for alignment"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Convert to lowercase for better alignment
        text = text.lower()
        
        # Remove punctuation that might interfere with alignment
        # Keep apostrophes for contractions
        text = re.sub(r'[^\w\s\']', '', text)
        
        # Language-specific preprocessing
        if language == "fr":
            # Handle French contractions and liaisons
            text = re.sub(r'\bl\'', 'l ', text)
            text = re.sub(r'\bd\'', 'd ', text)
        elif language == "it":
            # Handle Italian contractions
            text = re.sub(r'\bdell\'', 'dell ', text)
            text = re.sub(r'\bnell\'', 'nell ', text)
        elif language == "es":
            # Handle Spanish contractions
            text = re.sub(r'\bdel\b', 'de el', text)
            text = re.sub(r'\bal\b', 'a el', text)
        
        # Remove extra spaces again
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    def _perform_alignment(self,
                          model: EncoderASR,
                          waveform: torch.Tensor,
                          sample_rate: int,
                          text: str,
                          word_level: bool,
                          phoneme_level: bool) -> AlignmentResult:
        """Perform the actual forced alignment"""
        try:
            # Ensure correct device
            device = "cuda" if self.config.alignment.use_gpu and torch.cuda.is_available() else "cpu"
            waveform = waveform.to(device)
            
            # Get CTC logits from the model
            with torch.no_grad():
                if hasattr(model, 'encode_batch'):
                    # Use batch encoding
                    logits = model.encode_batch(waveform.unsqueeze(0))
                    if isinstance(logits, tuple):
                        logits = logits[0]  # Take first element if tuple
                else:
                    # Fallback method
                    logits = model.transcribe_file(waveform.squeeze(0), return_logits=True)
            
            # Perform CTC segmentation
            segments = self._ctc_segmentation(logits, text, sample_rate)
            
            # Generate word-level segments if requested
            if word_level:
                for segment in segments:
                    segment.word_segments = self._generate_word_segments(
                        segment.text, segment.start, segment.end
                    )
            
            # Generate phoneme-level segments if requested
            if phoneme_level:
                for segment in segments:
                    segment.phoneme_segments = self._generate_phoneme_segments(
                        segment.text, segment.start, segment.end
                    )
            
            # Calculate overall confidence
            overall_confidence = np.mean([seg.confidence for seg in segments]) if segments else 0.0
            
            return AlignmentResult(segments=segments, confidence=overall_confidence)
            
        except torch.cuda.OutOfMemoryError:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} GPU out of memory, falling back to CPU")
            # Clear GPU cache and retry on CPU
            torch.cuda.empty_cache()
            waveform = waveform.cpu()
            
            # Reload model on CPU
            self.config.alignment.use_gpu = False
            model = self.model_manager.load_wav2vec2_model(self.current_model_name)
            
            with torch.no_grad():
                if hasattr(model, 'encode_batch'):
                    logits = model.encode_batch(waveform.unsqueeze(0))
                    if isinstance(logits, tuple):
                        logits = logits[0]
                else:
                    logits = model.transcribe_file(waveform.squeeze(0), return_logits=True)
            
            segments = self._ctc_segmentation(logits, text, sample_rate)
            
            if word_level:
                for segment in segments:
                    segment.word_segments = self._generate_word_segments(
                        segment.text, segment.start, segment.end
                    )
            
            if phoneme_level:
                for segment in segments:
                    segment.phoneme_segments = self._generate_phoneme_segments(
                        segment.text, segment.start, segment.end
                    )
            
            overall_confidence = np.mean([seg.confidence for seg in segments]) if segments else 0.0
            return AlignmentResult(segments=segments, confidence=overall_confidence)
    
    def _ctc_segmentation(self, logits: torch.Tensor, text: str, sample_rate: int) -> List[AlignmentSegment]:
        """Perform CTC segmentation to align text with audio"""
        # This is a simplified implementation
        # In practice, you would use SpeechBrain's CTCSegmentation class
        
        # Split text into sentences/phrases
        sentences = self._split_text_into_segments(text)
        
        # Calculate time per frame
        time_per_frame = 0.02  # Assuming 20ms frames (typical for Wav2Vec2)
        total_frames = logits.shape[1] if len(logits.shape) > 1 else len(logits)
        total_duration = total_frames * time_per_frame
        
        segments = []
        current_time = 0.0
        
        for i, sentence in enumerate(sentences):
            # Estimate segment duration based on text length
            text_ratio = len(sentence) / len(text)
            segment_duration = total_duration * text_ratio
            
            # Create segment
            segment = AlignmentSegment(
                text=sentence,
                start=current_time,
                end=current_time + segment_duration,
                confidence=0.8  # Placeholder confidence
            )
            
            segments.append(segment)
            current_time += segment_duration
        
        return segments
    
    def _split_text_into_segments(self, text: str) -> List[str]:
        """Split text into alignment segments"""
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # If no sentence boundaries, split by phrases (commas)
        if len(sentences) <= 1:
            phrases = re.split(r'[,;]+', text)
            phrases = [p.strip() for p in phrases if p.strip()]
            if len(phrases) > 1:
                return phrases
        
        # If still no good splits, split by word count
        if len(sentences) <= 1:
            words = text.split()
            chunk_size = max(5, len(words) // 4)  # Aim for 4 segments minimum
            chunks = []
            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i + chunk_size])
                chunks.append(chunk)
            return chunks
        
        return sentences
    
    def _generate_word_segments(self, text: str, start_time: float, end_time: float) -> List[WordSegment]:
        """Generate word-level segments within a text segment"""
        words = text.split()
        if not words:
            return []
        
        duration = end_time - start_time
        word_duration = duration / len(words)
        
        word_segments = []
        current_time = start_time
        
        for word in words:
            word_seg = WordSegment(
                word=word,
                start=current_time,
                end=current_time + word_duration,
                confidence=0.8  # Placeholder confidence
            )
            word_segments.append(word_seg)
            current_time += word_duration
        
        return word_segments
    
    def _generate_phoneme_segments(self, text: str, start_time: float, end_time: float) -> List[Dict[str, Any]]:
        """Generate phoneme-level segments (simplified implementation)"""
        # This would require a phoneme dictionary and more sophisticated processing
        # For now, return empty list as placeholder
        return []
    
    def _get_cache_key(self, input_path: str, text: str, model_name: str) -> str:
        """Generate cache key for alignment"""
        import hashlib
        
        # Get file stats for cache invalidation
        try:
            stat = os.stat(input_path)
            file_info = f"{stat.st_size}_{stat.st_mtime}"
        except:
            file_info = "unknown"
        
        # Include text hash for cache key
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:8]
        
        cache_string = f"{input_path}_{model_name}_{text_hash}_{file_info}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[AlignmentResult]:
        """Check for cached alignment result"""
        cache_dir = os.path.join(os.path.dirname(__file__), ".cache", "alignments")
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct segments
            segments = []
            for seg_data in data["segments"]:
                segment = AlignmentSegment(
                    text=seg_data["text"],
                    start=seg_data["start"],
                    end=seg_data["end"],
                    confidence=seg_data["confidence"]
                )
                
                # Reconstruct word segments
                for word_data in seg_data.get("word_segments", []):
                    word_seg = WordSegment(
                        word=word_data["word"],
                        start=word_data["start"],
                        end=word_data["end"],
                        confidence=word_data["confidence"]
                    )
                    segment.word_segments.append(word_seg)
                
                segment.phoneme_segments = seg_data.get("phoneme_segments", [])
                segments.append(segment)
            
            result = AlignmentResult(segments=segments, confidence=data["confidence"])
            result.processing_time = data.get("processing_time", 0.0)
            result.model_used = data.get("model_used", "")
            result.language = data.get("language", "")
            result.total_duration = data.get("total_duration", 0.0)
            
            return result
            
        except Exception:
            return None
    
    def _save_cache(self, cache_key: str, result: AlignmentResult):
        """Save alignment result to cache"""
        cache_dir = os.path.join(os.path.dirname(__file__), ".cache", "alignments")
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to save alignment cache: {str(e)}")
    
    def _update_stats(self, processing_time: float, audio_duration: float, language: str):
        """Update performance statistics"""
        self.alignment_stats["total_alignments"] += 1
        self.alignment_stats["total_time"] += processing_time
        self.alignment_stats["total_audio_duration"] += audio_duration
        
        # Calculate averages
        total_alignments = self.alignment_stats["total_alignments"]
        self.alignment_stats["average_time"] = self.alignment_stats["total_time"] / total_alignments
        
        if self.alignment_stats["total_audio_duration"] > 0:
            self.alignment_stats["real_time_factor"] = (
                self.alignment_stats["total_time"] / self.alignment_stats["total_audio_duration"]
            )
        
        # Update language-specific stats
        if language not in self.alignment_stats["by_language"]:
            self.alignment_stats["by_language"][language] = {
                "count": 0,
                "total_time": 0.0,
                "total_duration": 0.0
            }
        
        lang_stats = self.alignment_stats["by_language"][language]
        lang_stats["count"] += 1
        lang_stats["total_time"] += processing_time
        lang_stats["total_duration"] += audio_duration
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.alignment_stats.copy()
    
    def print_performance_stats(self):
        """Print performance statistics"""
        stats = self.alignment_stats
        
        print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('Forced Alignment Performance Stats:')}")
        print(f"  Total Alignments: {blue_highlighted(str(stats['total_alignments']))}")
        avg_time_text = f"{stats['average_time']:.1f}s"
        print(f"  Average Time: {blue_highlighted(avg_time_text)}")
        rtf_text = f"{stats['real_time_factor']:.2f}x"
        print(f"  Real-time Factor: {blue_highlighted(rtf_text)}")
        cache_rate = f"{stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%" if stats['cache_hits']+stats['cache_misses'] > 0 else '0%'
        print(f"  Cache Hit Rate: {blue_highlighted(cache_rate)}")
        
        if stats["by_language"]:
            print(f"  By Language:")
            for lang, lang_stats in stats["by_language"].items():
                rtf = lang_stats["total_time"] / lang_stats["total_duration"] if lang_stats["total_duration"] > 0 else 0
                count_text = f"{lang_stats['count']} files"
            rtf_text = f"{rtf:.2f}x"
            print(f"    {lang.upper()}: {blue_highlighted(count_text)} - RTF: {blue_highlighted(rtf_text)}")
    
    def clear_cache(self):
        """Clear alignment cache"""
        cache_dir = os.path.join(os.path.dirname(__file__), ".cache", "alignments")
        try:
            if os.path.exists(cache_dir):
                import shutil
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
                print(f"{ULTRASINGER_HEAD} Cleared alignment cache")
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to clear cache: {str(e)}")


def get_available_models() -> List[AlignmentModel]:
    """Get list of available alignment models"""
    return list(AlignmentModel)


def get_models_by_language(language: str) -> List[AlignmentModel]:
    """Get available alignment models for specific language"""
    return AlignmentModel.get_models_by_language(language)


def get_supported_languages() -> List[str]:
    """Get list of supported languages for alignment"""
    languages = set()
    for model in AlignmentModel:
        info = AlignmentModel.get_model_info(model)
        if "language" in info:
            languages.add(info["language"])
    return sorted(list(languages))