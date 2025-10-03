"""
SpeechBrain Model Manager

Handles downloading, caching, and loading of SpeechBrain models with intelligent
memory management and automatic optimization for different hardware configurations.
"""

import os
import json
import hashlib
import shutil
import torch
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import threading
from pathlib import Path

from speechbrain.inference import SepformerSeparation, EncoderDecoderASR, EncoderASR
from speechbrain.inference.VAD import VAD

from modules.console_colors import (
    ULTRASINGER_HEAD, 
    blue_highlighted, 
    green_highlighted, 
    yellow_highlighted,
    red_highlighted
)
from .config_manager import SpeechBrainConfig


class ModelInfo:
    """Information about a cached model"""
    
    def __init__(self, model_name: str, model_type: str, cache_path: str):
        self.model_name = model_name
        self.model_type = model_type
        self.cache_path = cache_path
        self.last_used = datetime.now()
        self.download_date = datetime.now()
        self.size_mb = self._calculate_size()
        self.usage_count = 0
    
    def _calculate_size(self) -> float:
        """Calculate model size in MB"""
        if not os.path.exists(self.cache_path):
            return 0.0
        
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.cache_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    def update_usage(self):
        """Update usage statistics"""
        self.last_used = datetime.now()
        self.usage_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "cache_path": self.cache_path,
            "last_used": self.last_used.isoformat(),
            "download_date": self.download_date.isoformat(),
            "size_mb": self.size_mb,
            "usage_count": self.usage_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelInfo':
        """Create from dictionary"""
        info = cls(data["model_name"], data["model_type"], data["cache_path"])
        info.last_used = datetime.fromisoformat(data["last_used"])
        info.download_date = datetime.fromisoformat(data["download_date"])
        info.size_mb = data["size_mb"]
        info.usage_count = data["usage_count"]
        return info


class SpeechBrainModelManager:
    """Manages SpeechBrain models with intelligent caching and optimization"""
    
    def __init__(self, config: SpeechBrainConfig):
        self.config = config
        self.cache_path = config.cache_path
        self.models_info_path = os.path.join(self.cache_path, "models_info.json")
        self.loaded_models: Dict[str, Any] = {}
        self.models_info: Dict[str, ModelInfo] = {}
        self._lock = threading.Lock()
        
        # Create cache directory
        os.makedirs(self.cache_path, exist_ok=True)
        
        # Load existing model information
        self._load_models_info()
        
        # Clean up old models if needed
        self._cleanup_old_models()
    
    def _load_models_info(self):
        """Load model information from cache"""
        if os.path.exists(self.models_info_path):
            try:
                with open(self.models_info_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for model_key, model_data in data.items():
                    self.models_info[model_key] = ModelInfo.from_dict(model_data)
                    
            except Exception as e:
                print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to load models info: {str(e)}")
    
    def _save_models_info(self):
        """Save model information to cache"""
        try:
            data = {key: info.to_dict() for key, info in self.models_info.items()}
            with open(self.models_info_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to save models info: {str(e)}")
    
    def _cleanup_old_models(self, max_age_days: int = 30, max_cache_size_gb: float = 10.0):
        """Clean up old or unused models"""
        if not self.models_info:
            return
        
        current_time = datetime.now()
        total_size_mb = sum(info.size_mb for info in self.models_info.values())
        
        # Remove models older than max_age_days that haven't been used recently
        models_to_remove = []
        for model_key, info in self.models_info.items():
            age_days = (current_time - info.download_date).days
            unused_days = (current_time - info.last_used).days
            
            if age_days > max_age_days and unused_days > 7:
                models_to_remove.append(model_key)
        
        # If cache is too large, remove least recently used models
        if total_size_mb > max_cache_size_gb * 1024:
            sorted_models = sorted(
                self.models_info.items(),
                key=lambda x: (x[1].last_used, x[1].usage_count)
            )
            
            for model_key, info in sorted_models:
                if total_size_mb <= max_cache_size_gb * 1024:
                    break
                models_to_remove.append(model_key)
                total_size_mb -= info.size_mb
        
        # Remove selected models
        for model_key in models_to_remove:
            self._remove_model(model_key)
        
        if models_to_remove:
            print(f"{ULTRASINGER_HEAD} Cleaned up {len(models_to_remove)} old models from cache")
    
    def _remove_model(self, model_key: str):
        """Remove a model from cache"""
        if model_key in self.models_info:
            info = self.models_info[model_key]
            if os.path.exists(info.cache_path):
                shutil.rmtree(info.cache_path, ignore_errors=True)
            del self.models_info[model_key]
            
            # Remove from loaded models if present
            if model_key in self.loaded_models:
                del self.loaded_models[model_key]
    
    def _get_model_key(self, model_name: str, model_type: str) -> str:
        """Generate unique key for model"""
        return f"{model_type}_{hashlib.md5(model_name.encode()).hexdigest()[:8]}"
    
    def _get_model_cache_path(self, model_name: str, model_type: str) -> str:
        """Get cache path for model"""
        model_key = self._get_model_key(model_name, model_type)
        return os.path.join(self.cache_path, model_type, model_key)
    
    def load_sepformer_model(self, model_name: Optional[str] = None) -> SepformerSeparation:
        """Load SepFormer separation model"""
        model_name = model_name or self.config.sepformer.model_name
        model_key = self._get_model_key(model_name, "sepformer")
        
        with self._lock:
            # Return cached model if available
            if model_key in self.loaded_models:
                self.models_info[model_key].update_usage()
                return self.loaded_models[model_key]
            
            print(f"{ULTRASINGER_HEAD} Loading SepFormer model: {blue_highlighted(model_name)}")
            
            try:
                # Set device
                device = "cuda" if self.config.sepformer.use_gpu and torch.cuda.is_available() else "cpu"
                
                # Load model
                model = SepformerSeparation.from_hparams(
                    source=model_name,
                    savedir=self._get_model_cache_path(model_name, "sepformer"),
                    run_opts={"device": device}
                )
                
                # Cache the loaded model
                self.loaded_models[model_key] = model
                
                # Update model info
                cache_path = self._get_model_cache_path(model_name, "sepformer")
                if model_key not in self.models_info:
                    self.models_info[model_key] = ModelInfo(model_name, "sepformer", cache_path)
                
                self.models_info[model_key].update_usage()
                self._save_models_info()
                
                print(f"{ULTRASINGER_HEAD} {green_highlighted('Success:')} SepFormer model loaded on {device}")
                return model
                
            except Exception as e:
                print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Failed to load SepFormer model: {str(e)}")
                raise e
    
    def load_conformer_model(self, model_name: Optional[str] = None, language: Optional[str] = None) -> EncoderDecoderASR:
        """Load Conformer ASR model"""
        model_name = model_name or self.config.conformer.model_name
        language = language or self.config.conformer.language
        model_key = self._get_model_key(f"{model_name}_{language}", "conformer")
        
        with self._lock:
            # Return cached model if available
            if model_key in self.loaded_models:
                self.models_info[model_key].update_usage()
                return self.loaded_models[model_key]
            
            print(f"{ULTRASINGER_HEAD} Loading Conformer ASR model: {blue_highlighted(model_name)} ({language})")
            
            try:
                # Set device
                device = "cuda" if self.config.conformer.use_gpu and torch.cuda.is_available() else "cpu"
                
                # Load model
                model = EncoderDecoderASR.from_hparams(
                    source=model_name,
                    savedir=self._get_model_cache_path(model_name, "conformer"),
                    run_opts={"device": device}
                )
                
                # Cache the loaded model
                self.loaded_models[model_key] = model
                
                # Update model info
                cache_path = self._get_model_cache_path(model_name, "conformer")
                if model_key not in self.models_info:
                    self.models_info[model_key] = ModelInfo(f"{model_name}_{language}", "conformer", cache_path)
                
                self.models_info[model_key].update_usage()
                self._save_models_info()
                
                print(f"{ULTRASINGER_HEAD} {green_highlighted('Success:')} Conformer ASR model loaded on {device}")
                return model
                
            except Exception as e:
                print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Failed to load Conformer model: {str(e)}")
                raise e
    
    def load_wav2vec2_model(self, model_name: Optional[str] = None, language: Optional[str] = None) -> EncoderASR:
        """Load Wav2Vec2 ASR model for alignment"""
        if not model_name:
            language = language or self.config.conformer.language
            model_name = f"speechbrain/asr-wav2vec2-commonvoice-{language}"
        
        model_key = self._get_model_key(model_name, "wav2vec2")
        
        with self._lock:
            # Return cached model if available
            if model_key in self.loaded_models:
                self.models_info[model_key].update_usage()
                return self.loaded_models[model_key]
            
            print(f"{ULTRASINGER_HEAD} Loading Wav2Vec2 model: {blue_highlighted(model_name)}")
            
            try:
                # Set device
                device = "cuda" if self.config.alignment.use_gpu and torch.cuda.is_available() else "cpu"
                
                # Load model
                model = EncoderASR.from_hparams(
                    source=model_name,
                    savedir=self._get_model_cache_path(model_name, "wav2vec2"),
                    run_opts={"device": device}
                )
                
                # Cache the loaded model
                self.loaded_models[model_key] = model
                
                # Update model info
                cache_path = self._get_model_cache_path(model_name, "wav2vec2")
                if model_key not in self.models_info:
                    self.models_info[model_key] = ModelInfo(model_name, "wav2vec2", cache_path)
                
                self.models_info[model_key].update_usage()
                self._save_models_info()
                
                print(f"{ULTRASINGER_HEAD} {green_highlighted('Success:')} Wav2Vec2 model loaded on {device}")
                return model
                
            except Exception as e:
                print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Failed to load Wav2Vec2 model: {str(e)}")
                raise e
    
    def load_vad_model(self, model_name: Optional[str] = None) -> VAD:
        """Load VAD model"""
        model_name = model_name or self.config.vad.model_name
        model_key = self._get_model_key(model_name, "vad")
        
        with self._lock:
            # Return cached model if available
            if model_key in self.loaded_models:
                self.models_info[model_key].update_usage()
                return self.loaded_models[model_key]
            
            print(f"{ULTRASINGER_HEAD} Loading VAD model: {blue_highlighted(model_name)}")
            
            try:
                # Set device
                device = "cuda" if torch.cuda.is_available() else "cpu"
                
                # Load model
                model = VAD.from_hparams(
                    source=model_name,
                    savedir=self._get_model_cache_path(model_name, "vad"),
                    run_opts={"device": device}
                )
                
                # Cache the loaded model
                self.loaded_models[model_key] = model
                
                # Update model info
                cache_path = self._get_model_cache_path(model_name, "vad")
                if model_key not in self.models_info:
                    self.models_info[model_key] = ModelInfo(model_name, "vad", cache_path)
                
                self.models_info[model_key].update_usage()
                self._save_models_info()
                
                print(f"{ULTRASINGER_HEAD} {green_highlighted('Success:')} VAD model loaded on {device}")
                return model
                
            except Exception as e:
                print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Failed to load VAD model: {str(e)}")
                raise e
    
    def clear_memory(self):
        """Clear loaded models from memory"""
        with self._lock:
            self.loaded_models.clear()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        print(f"{ULTRASINGER_HEAD} Cleared model cache from memory")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached models"""
        total_size_mb = sum(info.size_mb for info in self.models_info.values())
        
        return {
            "total_models": len(self.models_info),
            "total_size_mb": total_size_mb,
            "total_size_gb": total_size_mb / 1024,
            "cache_path": self.cache_path,
            "models": [
                {
                    "name": info.model_name,
                    "type": info.model_type,
                    "size_mb": info.size_mb,
                    "last_used": info.last_used.strftime("%Y-%m-%d %H:%M"),
                    "usage_count": info.usage_count
                }
                for info in self.models_info.values()
            ]
        }
    
    def print_cache_info(self):
        """Print cache information"""
        info = self.get_cache_info()
        
        print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('SpeechBrain Model Cache:')}")
        print(f"  Total Models: {blue_highlighted(str(info['total_models']))}")
        size_text = f"{info['total_size_gb']:.2f} GB"
        print(f"  Total Size: {blue_highlighted(size_text)}")
        print(f"  Cache Path: {blue_highlighted(info['cache_path'])}")
        
        if info['models']:
            print(f"  {blue_highlighted('Cached Models:')}")
            for model in sorted(info['models'], key=lambda x: x['last_used'], reverse=True):
                print(f"    - {model['name']} ({model['type']}) - {model['size_mb']:.1f}MB - Used {model['usage_count']} times")
    
    def __del__(self):
        """Cleanup on destruction"""
        self._save_models_info()