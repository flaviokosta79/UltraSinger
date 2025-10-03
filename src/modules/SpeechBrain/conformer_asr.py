"""
Conformer/Branchformer ASR Module

Advanced Automatic Speech Recognition using SpeechBrain's Conformer and Branchformer models,
optimized for multilingual karaoke transcription with high accuracy and temporal precision.
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

from speechbrain.inference import EncoderDecoderASR, EncoderASR

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


class ASRModel(Enum):
    """Available ASR models with detailed information"""
    
    # Conformer models
    CONFORMER_LIBRISPEECH = "speechbrain/asr-conformer-librispeech"
    CONFORMER_COMMONVOICE_EN = "speechbrain/asr-conformer-commonvoice-en"
    CONFORMER_COMMONVOICE_FR = "speechbrain/asr-conformer-commonvoice-fr"
    CONFORMER_COMMONVOICE_IT = "speechbrain/asr-conformer-commonvoice-it"
    CONFORMER_COMMONVOICE_ES = "speechbrain/asr-conformer-commonvoice-es"
    
    # Branchformer models
    BRANCHFORMER_LIBRISPEECH = "speechbrain/asr-branchformer-librispeech"
    
    # Wav2Vec2 models
    WAV2VEC2_COMMONVOICE_EN = "speechbrain/asr-wav2vec2-commonvoice-en"
    WAV2VEC2_COMMONVOICE_FR = "speechbrain/asr-wav2vec2-commonvoice-fr"
    WAV2VEC2_COMMONVOICE_IT = "speechbrain/asr-wav2vec2-commonvoice-it"
    WAV2VEC2_COMMONVOICE_ES = "speechbrain/asr-wav2vec2-commonvoice-es"
    WAV2VEC2_COMMONVOICE_DE = "speechbrain/asr-wav2vec2-commonvoice-de"
    WAV2VEC2_COMMONVOICE_PT = "speechbrain/asr-wav2vec2-commonvoice-pt"
    
    @classmethod
    def get_model_info(cls, model: 'ASRModel') -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        model_info = {
            # Conformer models
            cls.CONFORMER_LIBRISPEECH: {
                "architecture": "Conformer",
                "language": "en",
                "dataset": "LibriSpeech",
                "wer": 2.46,
                "quality": "Excellent",
                "speed": "Medium",
                "sample_rate": 16000,
                "recommended_for": "High-quality English transcription"
            },
            cls.CONFORMER_COMMONVOICE_EN: {
                "architecture": "Conformer",
                "language": "en",
                "dataset": "CommonVoice",
                "wer": 3.2,
                "quality": "Very High",
                "speed": "Medium",
                "sample_rate": 16000,
                "recommended_for": "General English transcription"
            },
            cls.CONFORMER_COMMONVOICE_FR: {
                "architecture": "Conformer",
                "language": "fr",
                "dataset": "CommonVoice",
                "wer": 4.1,
                "quality": "Very High",
                "speed": "Medium",
                "sample_rate": 16000,
                "recommended_for": "French transcription"
            },
            cls.CONFORMER_COMMONVOICE_IT: {
                "architecture": "Conformer",
                "language": "it",
                "dataset": "CommonVoice",
                "wer": 3.8,
                "quality": "Very High",
                "speed": "Medium",
                "sample_rate": 16000,
                "recommended_for": "Italian transcription"
            },
            cls.CONFORMER_COMMONVOICE_ES: {
                "architecture": "Conformer",
                "language": "es",
                "dataset": "CommonVoice",
                "wer": 4.2,
                "quality": "Very High",
                "speed": "Medium",
                "sample_rate": 16000,
                "recommended_for": "Spanish transcription"
            },
            
            # Branchformer models
            cls.BRANCHFORMER_LIBRISPEECH: {
                "architecture": "Branchformer",
                "language": "en",
                "dataset": "LibriSpeech",
                "wer": 2.34,
                "quality": "Excellent",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "High-speed English transcription"
            },
            
            # Wav2Vec2 models
            cls.WAV2VEC2_COMMONVOICE_EN: {
                "architecture": "Wav2Vec2",
                "language": "en",
                "dataset": "CommonVoice",
                "wer": 3.5,
                "quality": "High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "Fast English transcription"
            },
            cls.WAV2VEC2_COMMONVOICE_FR: {
                "architecture": "Wav2Vec2",
                "language": "fr",
                "dataset": "CommonVoice",
                "wer": 4.8,
                "quality": "High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "Fast French transcription"
            },
            cls.WAV2VEC2_COMMONVOICE_IT: {
                "architecture": "Wav2Vec2",
                "language": "it",
                "dataset": "CommonVoice",
                "wer": 4.5,
                "quality": "High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "Fast Italian transcription"
            },
            cls.WAV2VEC2_COMMONVOICE_ES: {
                "architecture": "Wav2Vec2",
                "language": "es",
                "dataset": "CommonVoice",
                "wer": 5.1,
                "quality": "High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "Fast Spanish transcription"
            },
            cls.WAV2VEC2_COMMONVOICE_DE: {
                "architecture": "Wav2Vec2",
                "language": "de",
                "dataset": "CommonVoice",
                "wer": 4.9,
                "quality": "High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "Fast German transcription"
            },
            cls.WAV2VEC2_COMMONVOICE_PT: {
                "architecture": "Wav2Vec2",
                "language": "pt",
                "dataset": "CommonVoice",
                "wer": 5.3,
                "quality": "High",
                "speed": "Fast",
                "sample_rate": 16000,
                "recommended_for": "Fast Portuguese transcription"
            }
        }
        return model_info.get(model, {})
    
    @classmethod
    def get_models_by_language(cls, language: str) -> List['ASRModel']:
        """Get available models for a specific language"""
        models = []
        for model in cls:
            info = cls.get_model_info(model)
            if info.get("language") == language.lower():
                models.append(model)
        return models
    
    @classmethod
    def get_recommended_model(cls, language: str, priority: str = "quality") -> Optional['ASRModel']:
        """Get recommended model for language and priority (quality/speed)"""
        models = cls.get_models_by_language(language)
        if not models:
            return None
        
        if priority == "speed":
            # Prefer Wav2Vec2 for speed
            wav2vec_models = [m for m in models if "wav2vec2" in m.value.lower()]
            if wav2vec_models:
                return min(wav2vec_models, key=lambda m: cls.get_model_info(m).get("wer", 10))
        
        # Default to quality - prefer Conformer/Branchformer
        quality_models = [m for m in models if "conformer" in m.value.lower() or "branchformer" in m.value.lower()]
        if quality_models:
            return min(quality_models, key=lambda m: cls.get_model_info(m).get("wer", 10))
        
        # Fallback to best available
        return min(models, key=lambda m: cls.get_model_info(m).get("wer", 10))


class TranscriptionResult:
    """Container for transcription results with timing information"""
    
    def __init__(self, text: str, confidence: float = 1.0, segments: Optional[List[Dict]] = None):
        self.text = text
        self.confidence = confidence
        self.segments = segments or []
        self.processing_time = 0.0
        self.model_used = ""
        self.language = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "text": self.text,
            "confidence": self.confidence,
            "segments": self.segments,
            "processing_time": self.processing_time,
            "model_used": self.model_used,
            "language": self.language
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class ConformerASR:
    """Advanced ASR using Conformer/Branchformer models"""
    
    def __init__(self, config: SpeechBrainConfig, model_manager: SpeechBrainModelManager):
        self.config = config
        self.model_manager = model_manager
        self.current_model = None
        self.current_model_name = None
        self.current_language = None
        
        # Performance tracking
        self.transcription_stats = {
            "total_transcriptions": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "total_audio_duration": 0.0,
            "real_time_factor": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "by_language": {}
        }
    
    def transcribe_audio(self, 
                        input_path: str,
                        language: str = "en",
                        model: Optional[ASRModel] = None,
                        use_cache: bool = True,
                        return_segments: bool = True,
                        chunk_length: Optional[float] = None) -> TranscriptionResult:
        """
        Transcribe audio to text with timing information
        
        Args:
            input_path: Path to input audio file
            language: Target language code (en, fr, it, es, de, pt)
            model: Specific ASR model to use
            use_cache: Whether to use cached results
            return_segments: Whether to return word-level segments
            chunk_length: Maximum chunk length in seconds (None = no chunking)
            
        Returns:
            TranscriptionResult with text and timing information
        """
        start_time = time.time()
        
        # Validate input
        if not check_file_exists(input_path):
            raise FileNotFoundError(f"Input audio file not found: {input_path}")
        
        # Determine model
        if model is None:
            model = ASRModel.get_recommended_model(language, self.config.conformer.priority)
            if model is None:
                raise ValueError(f"No ASR model available for language: {language}")
        
        model_info = ASRModel.get_model_info(model)
        
        print(f"{ULTRASINGER_HEAD} Starting ASR transcription with {blue_highlighted(model.value.split('/')[-1])}")
        print(f"{ULTRASINGER_HEAD} Language: {blue_highlighted(language.upper())} - Architecture: {blue_highlighted(model_info['architecture'])}")
        wer_text = f"{model_info['wer']:.1f}%"
        print(f"{ULTRASINGER_HEAD} Expected WER: {blue_highlighted(wer_text)}")
        
        # Check cache
        cache_key = self._get_cache_key(input_path, model.value)
        if use_cache:
            cached_result = self._check_cache(cache_key)
            if cached_result:
                self.transcription_stats["cache_hits"] += 1
                print(f"{ULTRASINGER_HEAD} {green_highlighted('Cache:')} Using cached transcription")
                return cached_result
        
        self.transcription_stats["cache_misses"] += 1
        
        # Load model
        asr_model = self._load_model(model)
        
        # Load and preprocess audio
        waveform, sample_rate, duration = self._load_audio(input_path, model_info["sample_rate"])
        
        print(f"{ULTRASINGER_HEAD} Processing audio: {blue_highlighted(f'{duration:.1f}s')} at {blue_highlighted(f'{sample_rate}Hz')}")
        
        # Perform transcription
        try:
            if chunk_length and duration > chunk_length:
                result = self._transcribe_chunked(asr_model, waveform, sample_rate, chunk_length, return_segments)
            else:
                result = self._transcribe_single(asr_model, waveform, sample_rate, return_segments)
            
            # Set metadata
            result.processing_time = time.time() - start_time
            result.model_used = model.value
            result.language = language
            
            # Update statistics
            self._update_stats(result.processing_time, duration, language)
            
            # Cache result
            if use_cache:
                self._save_cache(cache_key, result)
            
            # Calculate real-time factor
            rtf = result.processing_time / duration if duration > 0 else 0
            
            print(f"{ULTRASINGER_HEAD} {green_highlighted('Success:')} Transcription completed in {blue_highlighted(f'{result.processing_time:.1f}s')}")
            print(f"{ULTRASINGER_HEAD} Real-time factor: {blue_highlighted(f'{rtf:.2f}x')}")
            print(f"{ULTRASINGER_HEAD} Confidence: {blue_highlighted(f'{result.confidence:.2f}')}")
            print(f"{ULTRASINGER_HEAD} Text length: {blue_highlighted(f'{len(result.text)} chars')}")
            
            if result.segments:
                print(f"{ULTRASINGER_HEAD} Segments: {blue_highlighted(f'{len(result.segments)} words')}")
            
            return result
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Transcription failed: {str(e)}")
            raise e
    
    def _load_model(self, model: ASRModel) -> Union[EncoderDecoderASR, EncoderASR]:
        """Load ASR model"""
        if self.current_model_name != model.value:
            print(f"{ULTRASINGER_HEAD} Loading model: {blue_highlighted(model.value.split('/')[-1])}")
            
            model_info = ASRModel.get_model_info(model)
            if model_info["architecture"] == "Wav2Vec2":
                self.current_model = self.model_manager.load_wav2vec2_model(model.value)
            else:
                self.current_model = self.model_manager.load_conformer_model(model.value)
            
            self.current_model_name = model.value
            self.current_language = model_info["language"]
        
        return self.current_model
    
    def _load_audio(self, input_path: str, target_sample_rate: int) -> Tuple[torch.Tensor, int, float]:
        """Load and preprocess audio"""
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
    
    def _transcribe_single(self, model: Union[EncoderDecoderASR, EncoderASR], 
                          waveform: torch.Tensor, 
                          sample_rate: int,
                          return_segments: bool) -> TranscriptionResult:
        """Transcribe single audio segment"""
        try:
            # Ensure correct device
            device = "cuda" if self.config.conformer.use_gpu and torch.cuda.is_available() else "cpu"
            waveform = waveform.to(device)
            
            # Perform transcription
            with torch.no_grad():
                if hasattr(model, 'transcribe_batch'):
                    # Use batch transcription if available
                    transcriptions = model.transcribe_batch(waveform.unsqueeze(0))
                    text = transcriptions[0] if transcriptions else ""
                else:
                    # Use single transcription
                    text = model.transcribe_file(waveform.squeeze(0))
            
            # Calculate confidence (simplified)
            confidence = self._estimate_confidence(text)
            
            # Generate segments if requested
            segments = []
            if return_segments and text:
                segments = self._generate_segments(text, waveform.shape[1] / sample_rate)
            
            return TranscriptionResult(text=text, confidence=confidence, segments=segments)
            
        except torch.cuda.OutOfMemoryError:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} GPU out of memory, falling back to CPU")
            # Clear GPU cache and retry on CPU
            torch.cuda.empty_cache()
            waveform = waveform.cpu()
            
            # Reload model on CPU
            self.config.conformer.use_gpu = False
            model = self.model_manager.load_conformer_model(self.current_model_name)
            
            with torch.no_grad():
                if hasattr(model, 'transcribe_batch'):
                    transcriptions = model.transcribe_batch(waveform.unsqueeze(0))
                    text = transcriptions[0] if transcriptions else ""
                else:
                    text = model.transcribe_file(waveform.squeeze(0))
            
            confidence = self._estimate_confidence(text)
            segments = []
            if return_segments and text:
                segments = self._generate_segments(text, waveform.shape[1] / sample_rate)
            
            return TranscriptionResult(text=text, confidence=confidence, segments=segments)
    
    def _transcribe_chunked(self, model: Union[EncoderDecoderASR, EncoderASR],
                           waveform: torch.Tensor,
                           sample_rate: int,
                           chunk_length: float,
                           return_segments: bool) -> TranscriptionResult:
        """Transcribe audio in chunks for long files"""
        chunk_samples = int(chunk_length * sample_rate)
        total_samples = waveform.shape[1]
        
        all_texts = []
        all_segments = []
        total_confidence = 0.0
        chunk_count = 0
        
        print(f"{ULTRASINGER_HEAD} Processing {blue_highlighted(f'{total_samples // chunk_samples + 1}')} chunks")
        
        for start_idx in range(0, total_samples, chunk_samples):
            end_idx = min(start_idx + chunk_samples, total_samples)
            chunk = waveform[:, start_idx:end_idx]
            
            chunk_start_time = start_idx / sample_rate
            chunk_duration = (end_idx - start_idx) / sample_rate
            
            # Transcribe chunk
            chunk_result = self._transcribe_single(model, chunk, sample_rate, return_segments)
            
            if chunk_result.text.strip():
                all_texts.append(chunk_result.text.strip())
                total_confidence += chunk_result.confidence
                chunk_count += 1
                
                # Adjust segment timings
                if return_segments and chunk_result.segments:
                    for segment in chunk_result.segments:
                        segment["start"] += chunk_start_time
                        segment["end"] += chunk_start_time
                    all_segments.extend(chunk_result.segments)
            
            print(f"{ULTRASINGER_HEAD} Chunk {chunk_count}: {blue_highlighted(f'{len(chunk_result.text)} chars')}")
        
        # Combine results
        final_text = " ".join(all_texts)
        final_confidence = total_confidence / chunk_count if chunk_count > 0 else 0.0
        
        return TranscriptionResult(text=final_text, confidence=final_confidence, segments=all_segments)
    
    def _estimate_confidence(self, text: str) -> float:
        """Estimate transcription confidence (simplified metric)"""
        if not text:
            return 0.0
        
        # Simple heuristics for confidence estimation
        word_count = len(text.split())
        char_count = len(text)
        
        # Base confidence on text characteristics
        confidence = 0.8  # Base confidence
        
        # Adjust based on length (longer texts tend to be more reliable)
        if word_count > 10:
            confidence += 0.1
        elif word_count < 3:
            confidence -= 0.2
        
        # Adjust based on character diversity
        unique_chars = len(set(text.lower()))
        if unique_chars > 15:
            confidence += 0.05
        
        # Penalize excessive repetition
        words = text.lower().split()
        if len(words) > 0:
            unique_words = len(set(words))
            repetition_ratio = unique_words / len(words)
            if repetition_ratio < 0.5:
                confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_segments(self, text: str, duration: float) -> List[Dict[str, Any]]:
        """Generate word-level segments with estimated timing"""
        words = text.split()
        if not words:
            return []
        
        segments = []
        words_per_second = len(words) / duration if duration > 0 else 1
        
        for i, word in enumerate(words):
            start_time = i / words_per_second
            end_time = (i + 1) / words_per_second
            
            segments.append({
                "word": word,
                "start": start_time,
                "end": end_time,
                "confidence": self._estimate_confidence(word)
            })
        
        return segments
    
    def _get_cache_key(self, input_path: str, model_name: str) -> str:
        """Generate cache key for transcription"""
        import hashlib
        
        # Get file stats for cache invalidation
        try:
            stat = os.stat(input_path)
            file_info = f"{stat.st_size}_{stat.st_mtime}"
        except:
            file_info = "unknown"
        
        cache_string = f"{input_path}_{model_name}_{file_info}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[TranscriptionResult]:
        """Check for cached transcription result"""
        cache_dir = os.path.join(os.path.dirname(__file__), ".cache", "transcriptions")
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            result = TranscriptionResult(
                text=data["text"],
                confidence=data["confidence"],
                segments=data.get("segments", [])
            )
            result.processing_time = data.get("processing_time", 0.0)
            result.model_used = data.get("model_used", "")
            result.language = data.get("language", "")
            
            return result
            
        except Exception:
            return None
    
    def _save_cache(self, cache_key: str, result: TranscriptionResult):
        """Save transcription result to cache"""
        cache_dir = os.path.join(os.path.dirname(__file__), ".cache", "transcriptions")
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to save cache: {str(e)}")
    
    def _update_stats(self, processing_time: float, audio_duration: float, language: str):
        """Update performance statistics"""
        self.transcription_stats["total_transcriptions"] += 1
        self.transcription_stats["total_time"] += processing_time
        self.transcription_stats["total_audio_duration"] += audio_duration
        
        # Calculate averages
        total_transcriptions = self.transcription_stats["total_transcriptions"]
        self.transcription_stats["average_time"] = self.transcription_stats["total_time"] / total_transcriptions
        
        if self.transcription_stats["total_audio_duration"] > 0:
            self.transcription_stats["real_time_factor"] = (
                self.transcription_stats["total_time"] / self.transcription_stats["total_audio_duration"]
            )
        
        # Update language-specific stats
        if language not in self.transcription_stats["by_language"]:
            self.transcription_stats["by_language"][language] = {
                "count": 0,
                "total_time": 0.0,
                "total_duration": 0.0
            }
        
        lang_stats = self.transcription_stats["by_language"][language]
        lang_stats["count"] += 1
        lang_stats["total_time"] += processing_time
        lang_stats["total_duration"] += audio_duration
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.transcription_stats.copy()
    
    def print_performance_stats(self):
        """Print performance statistics"""
        stats = self.transcription_stats
        
        print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('ASR Performance Stats:')}")
        print(f"  Total Transcriptions: {blue_highlighted(str(stats['total_transcriptions']))}")
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
        """Clear transcription cache"""
        cache_dir = os.path.join(os.path.dirname(__file__), ".cache", "transcriptions")
        try:
            if os.path.exists(cache_dir):
                import shutil
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
                print(f"{ULTRASINGER_HEAD} Cleared transcription cache")
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to clear cache: {str(e)}")


def get_available_models() -> List[ASRModel]:
    """Get list of available ASR models"""
    return list(ASRModel)


def get_models_by_language(language: str) -> List[ASRModel]:
    """Get available models for specific language"""
    return ASRModel.get_models_by_language(language)


def get_supported_languages() -> List[str]:
    """Get list of supported languages"""
    languages = set()
    for model in ASRModel:
        info = ASRModel.get_model_info(model)
        if "language" in info:
            languages.add(info["language"])
    return sorted(list(languages))