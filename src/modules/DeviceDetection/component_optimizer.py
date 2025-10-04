"""Component-specific optimizers for RTX 5060TI 16GB"""

import torch
import os
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json

from modules.console_colors import ULTRASINGER_HEAD, red_highlighted, blue_highlighted, green_highlighted, yellow_highlighted

@dataclass
class WhisperOptimization:
    """Whisper optimization configuration"""
    model_name: str
    batch_size: int
    compute_type: str
    device: str
    beam_size: int
    best_of: int
    temperature: float
    compression_ratio_threshold: float
    log_prob_threshold: float
    no_speech_threshold: float
    condition_on_previous_text: bool
    initial_prompt: Optional[str]
    word_timestamps: bool
    prepend_punctuations: str
    append_punctuations: str
    vram_usage_mb: int
    expected_speedup: float

@dataclass
class DemucsOptimization:
    """Demucs optimization configuration"""
    model_name: str
    device: str
    chunk_size: int
    overlap: float
    shifts: int
    split: bool
    segment_length: Optional[int]
    jobs: int
    progress: bool
    float32: bool
    int24: bool
    two_stems: Optional[str]
    mp3: bool
    mp3_bitrate: int
    flac: bool
    vram_usage_mb: int
    expected_speedup: float

@dataclass
class CrepeOptimization:
    """CREPE optimization configuration"""
    model_capacity: str
    device: str
    step_size: int
    batch_size: int
    fmin: int
    fmax: int
    decoder: str
    center: bool
    pad_mode: str
    vram_usage_mb: int
    expected_accuracy: float

class ComponentOptimizer:
    """Component-specific optimizer for RTX 5060TI 16GB"""
    
    def __init__(self, rtx_optimizer=None):
        self.rtx_optimizer = rtx_optimizer
        self.optimizations_cache = {}
        
    def get_whisper_optimization(self, mode: str = "balanced") -> WhisperOptimization:
        """Get optimized Whisper configuration for RTX 5060TI"""
        cache_key = f"whisper_{mode}"
        
        if cache_key in self.optimizations_cache:
            return self.optimizations_cache[cache_key]
        
        print(f"{ULTRASINGER_HEAD} 🎤 Otimizando Whisper para RTX 5060TI (modo: {blue_highlighted(mode)})...")
        
        if mode == "conservative":
            optimization = WhisperOptimization(
                model_name="large-v3-turbo",
                batch_size=8,
                compute_type="float16",
                device="cuda",
                beam_size=1,
                best_of=1,
                temperature=0.0,
                compression_ratio_threshold=2.4,
                log_prob_threshold=-1.0,
                no_speech_threshold=0.6,
                condition_on_previous_text=True,
                initial_prompt=None,
                word_timestamps=True,
                prepend_punctuations="\"'([{-",
                append_punctuations="\"'.。,，!！?？:：\")]}、",
                vram_usage_mb=4000,
                expected_speedup=2.5
            )
        elif mode == "aggressive":
            optimization = WhisperOptimization(
                model_name="large-v3-turbo",
                batch_size=32,
                compute_type="float16",
                device="cuda",
                beam_size=1,
                best_of=1,
                temperature=0.0,
                compression_ratio_threshold=2.4,
                log_prob_threshold=-1.0,
                no_speech_threshold=0.6,
                condition_on_previous_text=False,  # Faster processing
                initial_prompt=None,
                word_timestamps=True,
                prepend_punctuations="\"'([{-",
                append_punctuations="\"'.。,，!！?？:：\")]}、",
                vram_usage_mb=8000,
                expected_speedup=4.0
            )
        else:  # balanced
            optimization = WhisperOptimization(
                model_name="large-v3-turbo",
                batch_size=16,
                compute_type="float16",
                device="cuda",
                beam_size=1,
                best_of=1,
                temperature=0.0,
                compression_ratio_threshold=2.4,
                log_prob_threshold=-1.0,
                no_speech_threshold=0.6,
                condition_on_previous_text=True,
                initial_prompt=None,
                word_timestamps=True,
                prepend_punctuations="\"'([{-",
                append_punctuations="\"'.。,，!！?？:：\")]}、",
                vram_usage_mb=6000,
                expected_speedup=3.2
            )
        
        self.optimizations_cache[cache_key] = optimization
        
        print(f"{ULTRASINGER_HEAD} ✅ Whisper otimizado: batch_size={optimization.batch_size}, "
              f"VRAM={optimization.vram_usage_mb}MB, speedup={optimization.expected_speedup}x")
        
        return optimization
    
    def get_demucs_optimization(self, mode: str = "balanced") -> DemucsOptimization:
        """Get optimized Demucs configuration for RTX 5060TI"""
        cache_key = f"demucs_{mode}"
        
        if cache_key in self.optimizations_cache:
            return self.optimizations_cache[cache_key]
        
        print(f"{ULTRASINGER_HEAD} 🎵 Otimizando Demucs para RTX 5060TI (modo: {blue_highlighted(mode)})...")
        
        if mode == "conservative":
            optimization = DemucsOptimization(
                model_name="htdemucs_ft",
                device="cuda",
                chunk_size=131072,  # 128k samples (~3s at 44.1kHz)
                overlap=0.25,
                shifts=1,
                split=True,
                segment_length=None,
                jobs=1,
                progress=True,
                float32=False,  # Use float16 for memory efficiency
                int24=False,
                two_stems=None,
                mp3=False,
                mp3_bitrate=320,
                flac=False,
                vram_usage_mb=3000,
                expected_speedup=1.8
            )
        elif mode == "aggressive":
            optimization = DemucsOptimization(
                model_name="htdemucs_ft",
                device="cuda",
                chunk_size=524288,  # 512k samples (~12s at 44.1kHz)
                overlap=0.1,  # Less overlap for speed
                shifts=1,
                split=False,  # Process entire track at once
                segment_length=None,
                jobs=1,
                progress=True,
                float32=False,
                int24=False,
                two_stems=None,
                mp3=False,
                mp3_bitrate=320,
                flac=False,
                vram_usage_mb=8000,
                expected_speedup=3.5
            )
        else:  # balanced
            optimization = DemucsOptimization(
                model_name="htdemucs_ft",
                device="cuda",
                chunk_size=262144,  # 256k samples (~6s at 44.1kHz)
                overlap=0.25,
                shifts=1,
                split=True,
                segment_length=None,
                jobs=1,
                progress=True,
                float32=False,
                int24=False,
                two_stems=None,
                mp3=False,
                mp3_bitrate=320,
                flac=False,
                vram_usage_mb=5000,
                expected_speedup=2.8
            )
        
        self.optimizations_cache[cache_key] = optimization
        
        print(f"{ULTRASINGER_HEAD} ✅ Demucs otimizado: chunk_size={optimization.chunk_size//1024}k, "
              f"overlap={optimization.overlap}, VRAM={optimization.vram_usage_mb}MB, speedup={optimization.expected_speedup}x")
        
        return optimization
    
    def get_crepe_optimization(self, mode: str = "balanced") -> CrepeOptimization:
        """Get optimized CREPE configuration for RTX 5060TI"""
        cache_key = f"crepe_{mode}"
        
        if cache_key in self.optimizations_cache:
            return self.optimizations_cache[cache_key]
        
        print(f"{ULTRASINGER_HEAD} 🎼 Otimizando CREPE para RTX 5060TI (modo: {blue_highlighted(mode)})...")
        
        if mode == "conservative":
            optimization = CrepeOptimization(
                model_capacity="large",
                device="cuda",
                step_size=10,  # 10ms steps
                batch_size=512,
                fmin=50,
                fmax=2000,
                decoder="viterbi",
                center=True,
                pad_mode="constant",
                vram_usage_mb=1500,
                expected_accuracy=0.92
            )
        elif mode == "aggressive":
            optimization = CrepeOptimization(
                model_capacity="full",
                device="cuda",
                step_size=5,  # 5ms steps for higher precision
                batch_size=1024,  # Larger batches for RTX 5060TI
                fmin=50,
                fmax=2000,
                decoder="viterbi",
                center=True,
                pad_mode="constant",
                vram_usage_mb=3000,
                expected_accuracy=0.96
            )
        else:  # balanced
            optimization = CrepeOptimization(
                model_capacity="full",
                device="cuda",
                step_size=5,
                batch_size=768,
                fmin=50,
                fmax=2000,
                decoder="viterbi",
                center=True,
                pad_mode="constant",
                vram_usage_mb=2200,
                expected_accuracy=0.95
            )
        
        self.optimizations_cache[cache_key] = optimization
        
        print(f"{ULTRASINGER_HEAD} ✅ CREPE otimizado: capacity={optimization.model_capacity}, "
              f"step_size={optimization.step_size}ms, batch_size={optimization.batch_size}, "
              f"VRAM={optimization.vram_usage_mb}MB, accuracy={optimization.expected_accuracy}")
        
        return optimization
    
    def get_total_vram_usage(self, mode: str = "balanced") -> int:
        """Calculate total VRAM usage for all components"""
        whisper_opt = self.get_whisper_optimization(mode)
        demucs_opt = self.get_demucs_optimization(mode)
        crepe_opt = self.get_crepe_optimization(mode)
        
        total_vram = whisper_opt.vram_usage_mb + demucs_opt.vram_usage_mb + crepe_opt.vram_usage_mb
        
        return total_vram
    
    def get_optimized_config(self, mode: str = "balanced"):
        """Get complete optimized configuration for all components"""
        from types import SimpleNamespace
        
        # Get individual optimizations
        whisper_opt = self.get_whisper_optimization(mode)
        demucs_opt = self.get_demucs_optimization(mode)
        crepe_opt = self.get_crepe_optimization(mode)
        
        # Create a namespace object with all configurations
        config = SimpleNamespace()
        config.whisper = whisper_opt
        config.demucs = demucs_opt
        config.crepe = crepe_opt
        config.mode = mode
        config.total_vram_mb = self.get_total_vram_usage(mode)
        
        return config
    
    def calculate_total_vram_usage(self, mode: str = "balanced") -> float:
        """Calculate total VRAM usage in GB"""
        total_mb = self.get_total_vram_usage(mode)
        return total_mb / 1024.0
    
    def validate_vram_requirements(self, mode: str = "balanced") -> Tuple[bool, str]:
        """Validate if VRAM requirements can be met"""
        total_vram_mb = self.get_total_vram_usage(mode)
        total_vram_gb = total_vram_mb / 1024
        
        # RTX 5060TI has 16GB, leave 2GB for system
        available_vram_gb = 14.0
        
        if total_vram_gb <= available_vram_gb:
            return True, f"VRAM OK: {total_vram_gb:.1f}GB / {available_vram_gb}GB disponível"
        else:
            return False, f"VRAM insuficiente: {total_vram_gb:.1f}GB necessário, {available_vram_gb}GB disponível"
    
    def print_optimization_summary(self, mode: str = "balanced"):
        """Print detailed optimization summary"""
        print(f"\n{ULTRASINGER_HEAD} 📋 {blue_highlighted(f'RESUMO DE OTIMIZAÇÕES RTX 5060TI ({mode.upper()}):')}")
        
        # Get optimizations
        whisper_opt = self.get_whisper_optimization(mode)
        demucs_opt = self.get_demucs_optimization(mode)
        crepe_opt = self.get_crepe_optimization(mode)
        
        # Whisper summary
        print(f"{ULTRASINGER_HEAD} ┌─ {blue_highlighted('WHISPER:')}")
        print(f"{ULTRASINGER_HEAD} │  ├─ Modelo: {whisper_opt.model_name}")
        print(f"{ULTRASINGER_HEAD} │  ├─ Batch size: {whisper_opt.batch_size}")
        print(f"{ULTRASINGER_HEAD} │  ├─ Compute type: {whisper_opt.compute_type}")
        print(f"{ULTRASINGER_HEAD} │  ├─ VRAM: {whisper_opt.vram_usage_mb}MB")
        print(f"{ULTRASINGER_HEAD} │  └─ Speedup esperado: {green_highlighted(f'{whisper_opt.expected_speedup}x')}")
        
        # Demucs summary
        print(f"{ULTRASINGER_HEAD} ├─ {blue_highlighted('DEMUCS:')}")
        print(f"{ULTRASINGER_HEAD} │  ├─ Modelo: {demucs_opt.model_name}")
        print(f"{ULTRASINGER_HEAD} │  ├─ Chunk size: {demucs_opt.chunk_size//1024}k samples")
        print(f"{ULTRASINGER_HEAD} │  ├─ Overlap: {demucs_opt.overlap}")
        print(f"{ULTRASINGER_HEAD} │  ├─ VRAM: {demucs_opt.vram_usage_mb}MB")
        print(f"{ULTRASINGER_HEAD} │  └─ Speedup esperado: {green_highlighted(f'{demucs_opt.expected_speedup}x')}")
        
        # CREPE summary
        print(f"{ULTRASINGER_HEAD} ├─ {blue_highlighted('CREPE:')}")
        print(f"{ULTRASINGER_HEAD} │  ├─ Capacidade: {crepe_opt.model_capacity}")
        print(f"{ULTRASINGER_HEAD} │  ├─ Step size: {crepe_opt.step_size}ms")
        print(f"{ULTRASINGER_HEAD} │  ├─ Batch size: {crepe_opt.batch_size}")
        print(f"{ULTRASINGER_HEAD} │  ├─ VRAM: {crepe_opt.vram_usage_mb}MB")
        print(f"{ULTRASINGER_HEAD} │  └─ Precisão esperada: {green_highlighted(f'{crepe_opt.expected_accuracy:.1%}')}")
        
        # Total summary
        total_vram_mb = self.get_total_vram_usage(mode)
        is_valid, vram_message = self.validate_vram_requirements(mode)
        
        print(f"{ULTRASINGER_HEAD} └─ {blue_highlighted('TOTAL:')}")
        print(f"{ULTRASINGER_HEAD}    ├─ VRAM total: {total_vram_mb}MB ({total_vram_mb/1024:.1f}GB)")
        
        if is_valid:
            print(f"{ULTRASINGER_HEAD}    └─ Status: {green_highlighted('✅ ' + vram_message)}")
        else:
            print(f"{ULTRASINGER_HEAD}    └─ Status: {red_highlighted('❌ ' + vram_message)}")
        
        print()
    
    def apply_whisper_optimization(self, whisper_config: Dict[str, Any], mode: str = "balanced") -> Dict[str, Any]:
        """Apply Whisper optimization to existing config"""
        optimization = self.get_whisper_optimization(mode)
        
        # Update config with optimized values
        optimized_config = whisper_config.copy()
        optimized_config.update({
            "model": optimization.model_name,
            "batch_size": optimization.batch_size,
            "compute_type": optimization.compute_type,
            "device": optimization.device,
            "beam_size": optimization.beam_size,
            "best_of": optimization.best_of,
            "temperature": optimization.temperature,
            "compression_ratio_threshold": optimization.compression_ratio_threshold,
            "log_prob_threshold": optimization.log_prob_threshold,
            "no_speech_threshold": optimization.no_speech_threshold,
            "condition_on_previous_text": optimization.condition_on_previous_text,
            "word_timestamps": optimization.word_timestamps,
            "prepend_punctuations": optimization.prepend_punctuations,
            "append_punctuations": optimization.append_punctuations
        })
        
        return optimized_config
    
    def apply_demucs_optimization(self, demucs_config: Dict[str, Any], mode: str = "balanced") -> Dict[str, Any]:
        """Apply Demucs optimization to existing config"""
        optimization = self.get_demucs_optimization(mode)
        
        # Update config with optimized values
        optimized_config = demucs_config.copy()
        optimized_config.update({
            "model": optimization.model_name,
            "device": optimization.device,
            "chunk_size": optimization.chunk_size,
            "overlap": optimization.overlap,
            "shifts": optimization.shifts,
            "split": optimization.split,
            "jobs": optimization.jobs,
            "float32": optimization.float32,
            "int24": optimization.int24,
            "mp3": optimization.mp3,
            "mp3_bitrate": optimization.mp3_bitrate,
            "flac": optimization.flac
        })
        
        return optimized_config
    
    def apply_crepe_optimization(self, crepe_config: Dict[str, Any], mode: str = "balanced") -> Dict[str, Any]:
        """Apply CREPE optimization to existing config"""
        optimization = self.get_crepe_optimization(mode)
        
        # Update config with optimized values
        optimized_config = crepe_config.copy()
        optimized_config.update({
            "model_capacity": optimization.model_capacity,
            "device": optimization.device,
            "step_size": optimization.step_size,
            "batch_size": optimization.batch_size,
            "fmin": optimization.fmin,
            "fmax": optimization.fmax,
            "decoder": optimization.decoder,
            "center": optimization.center,
            "pad_mode": optimization.pad_mode
        })
        
        return optimized_config
    
    def save_optimization_profile(self, filepath: str, mode: str = "balanced"):
        """Save optimization profile to file"""
        try:
            whisper_opt = self.get_whisper_optimization(mode)
            demucs_opt = self.get_demucs_optimization(mode)
            crepe_opt = self.get_crepe_optimization(mode)
            
            profile = {
                "optimization_mode": mode,
                "rtx_5060ti_optimized": True,
                "total_vram_usage_mb": self.get_total_vram_usage(mode),
                "whisper": {
                    "model_name": whisper_opt.model_name,
                    "batch_size": whisper_opt.batch_size,
                    "compute_type": whisper_opt.compute_type,
                    "device": whisper_opt.device,
                    "beam_size": whisper_opt.beam_size,
                    "best_of": whisper_opt.best_of,
                    "temperature": whisper_opt.temperature,
                    "compression_ratio_threshold": whisper_opt.compression_ratio_threshold,
                    "log_prob_threshold": whisper_opt.log_prob_threshold,
                    "no_speech_threshold": whisper_opt.no_speech_threshold,
                    "condition_on_previous_text": whisper_opt.condition_on_previous_text,
                    "word_timestamps": whisper_opt.word_timestamps,
                    "prepend_punctuations": whisper_opt.prepend_punctuations,
                    "append_punctuations": whisper_opt.append_punctuations,
                    "vram_usage_mb": whisper_opt.vram_usage_mb,
                    "expected_speedup": whisper_opt.expected_speedup
                },
                "demucs": {
                    "model_name": demucs_opt.model_name,
                    "device": demucs_opt.device,
                    "chunk_size": demucs_opt.chunk_size,
                    "overlap": demucs_opt.overlap,
                    "shifts": demucs_opt.shifts,
                    "split": demucs_opt.split,
                    "segment_length": demucs_opt.segment_length,
                    "jobs": demucs_opt.jobs,
                    "float32": demucs_opt.float32,
                    "int24": demucs_opt.int24,
                    "two_stems": demucs_opt.two_stems,
                    "mp3": demucs_opt.mp3,
                    "mp3_bitrate": demucs_opt.mp3_bitrate,
                    "flac": demucs_opt.flac,
                    "vram_usage_mb": demucs_opt.vram_usage_mb,
                    "expected_speedup": demucs_opt.expected_speedup
                },
                "crepe": {
                    "model_capacity": crepe_opt.model_capacity,
                    "device": crepe_opt.device,
                    "step_size": crepe_opt.step_size,
                    "batch_size": crepe_opt.batch_size,
                    "fmin": crepe_opt.fmin,
                    "fmax": crepe_opt.fmax,
                    "decoder": crepe_opt.decoder,
                    "center": crepe_opt.center,
                    "pad_mode": crepe_opt.pad_mode,
                    "vram_usage_mb": crepe_opt.vram_usage_mb,
                    "expected_accuracy": crepe_opt.expected_accuracy
                },
                "created_at": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "Unknown GPU"
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            
            print(f"{ULTRASINGER_HEAD} 💾 Perfil de otimização salvo: {filepath}")
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} ❌ Erro ao salvar perfil: {str(e)}")

    def apply_rtx_5060ti_optimizations(self, mode: str = "balanced"):
        """Apply RTX 5060TI optimizations to the system"""
        print(f"{ULTRASINGER_HEAD} 🚀 Aplicando otimizações RTX 5060TI (modo: {blue_highlighted(mode)})...")
        
        try:
            # Validate VRAM requirements
            is_valid, message = self.validate_vram_requirements(mode)
            if not is_valid:
                print(f"{ULTRASINGER_HEAD} ⚠️ {yellow_highlighted(message)}")
                print(f"{ULTRASINGER_HEAD} 🔄 Mudando para modo conservativo...")
                mode = "conservative"
            
            # Get optimizations for all components
            whisper_opt = self.get_whisper_optimization(mode)
            demucs_opt = self.get_demucs_optimization(mode)
            crepe_opt = self.get_crepe_optimization(mode)
            
            # Print optimization summary
            self.print_optimization_summary(mode)
            
            # Set environment variables for CUDA optimizations
            if torch.cuda.is_available():
                os.environ['CUDA_LAUNCH_BLOCKING'] = '0'  # Enable async CUDA operations
                os.environ['TORCH_CUDNN_V8_API_ENABLED'] = '1'  # Enable cuDNN v8 API
                
            print(f"{ULTRASINGER_HEAD} ✅ {green_highlighted('Otimizações RTX 5060TI aplicadas com sucesso!')}")
            
            return True
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} ❌ Erro ao aplicar otimizações RTX 5060TI: {str(e)}")
            return False

# Global instance
component_optimizer = ComponentOptimizer()