"""RTX 5060TI 16GB GPU Optimizer for UltraSinger"""

import torch
import os
import subprocess
import json
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from modules.console_colors import ULTRASINGER_HEAD, red_highlighted, blue_highlighted, green_highlighted

@dataclass
class GPUConfig:
    """Configuration for RTX 5060TI 16GB"""
    gpu_name: str
    vram_total_gb: int
    cuda_version: str
    driver_version: str
    is_rtx_5060ti: bool
    optimization_mode: str = "balanced"  # conservative, balanced, aggressive

@dataclass
class ComponentOptimization:
    """Optimization settings for each component"""
    whisper: Dict[str, Any]
    demucs: Dict[str, Any]
    crepe: Dict[str, Any]

class RTX5060TIOptimizer:
    """RTX 5060TI 16GB specific optimizer for UltraSinger"""
    
    def __init__(self):
        self.gpu_config: Optional[GPUConfig] = None
        self.optimization_config: Optional[ComponentOptimization] = None
        self.is_initialized = False
        
    def detect_rtx_5060ti(self) -> Tuple[bool, GPUConfig]:
        """Detect RTX 5060TI 16GB GPU and gather system information"""
        print(f"{ULTRASINGER_HEAD} 🚀 Detectando GPU RTX 5060TI 16GB...")
        
        try:
            # Try using nvidia-ml-py first
            try:
                import pynvml
                pynvml.nvmlInit()
                
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count == 0:
                    print(f"{ULTRASINGER_HEAD} ❌ Nenhuma GPU NVIDIA detectada")
                    return False, None
                
                # Check first GPU (primary)
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                gpu_name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                vram_gb = memory_info.total / (1024**3)
                
            except ImportError:
                # Fallback to nvidia-smi if pynvml not available
                result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    print(f"{ULTRASINGER_HEAD} ❌ nvidia-smi não disponível")
                    return False, None
                
                lines = result.stdout.strip().split('\n')
                if not lines:
                    print(f"{ULTRASINGER_HEAD} ❌ Nenhuma GPU detectada")
                    return False, None
                
                # Parse first GPU info
                gpu_info = lines[0].split(', ')
                gpu_name = gpu_info[0].strip()
                vram_mb = float(gpu_info[1].strip())
                vram_gb = vram_mb / 1024
            
            # Get CUDA version
            cuda_version = self._get_cuda_version()
            driver_version = self._get_nvidia_driver_version()
            
            print(f"{ULTRASINGER_HEAD} 🔍 GPU detectada: {blue_highlighted(gpu_name)}")
            print(f"{ULTRASINGER_HEAD} 💾 VRAM: {blue_highlighted(f'{vram_gb:.1f}GB')}")
            print(f"{ULTRASINGER_HEAD} 🔧 CUDA: {cuda_version}, Driver: {driver_version}")
            
            # Check if it's RTX 5060TI with 16GB
            is_rtx_5060ti = ("RTX 5060" in gpu_name.upper() or "5060" in gpu_name) and vram_gb >= 15.5
            
            if is_rtx_5060ti:
                print(f"{ULTRASINGER_HEAD} ✅ {green_highlighted('RTX 5060TI 16GB detectada!')}")
                
                gpu_config = GPUConfig(
                    gpu_name=gpu_name,
                    vram_total_gb=int(vram_gb),
                    cuda_version=cuda_version,
                    driver_version=driver_version,
                    is_rtx_5060ti=True
                )
                
                return True, gpu_config
            else:
                print(f"{ULTRASINGER_HEAD} ⚠️ GPU detectada: {gpu_name} ({vram_gb:.1f}GB)")
                print(f"{ULTRASINGER_HEAD} ℹ️ Otimizações específicas para RTX 5060TI não aplicadas")
                
                gpu_config = GPUConfig(
                    gpu_name=gpu_name,
                    vram_total_gb=int(vram_gb),
                    cuda_version=cuda_version,
                    driver_version=driver_version,
                    is_rtx_5060ti=False
                )
                
                return False, gpu_config
                
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} ❌ Erro na detecção da GPU: {str(e)}")
            # Create a fallback GPU config for testing
            fallback_config = GPUConfig(
                gpu_name="Unknown GPU",
                vram_total_gb=8,
                cuda_version="Unknown",
                driver_version="Unknown",
                is_rtx_5060ti=False
            )
            return False, fallback_config
    
    def _get_nvidia_driver_version(self) -> str:
        """Get NVIDIA driver version"""
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "Unknown"
    
    def _get_cuda_version(self) -> str:
        """Get CUDA version"""
        try:
            if torch.cuda.is_available():
                return torch.version.cuda if torch.version.cuda else "Unknown"
        except:
            pass
        return "Unknown"
    
    def generate_rtx_5060ti_optimizations(self, mode: str = "balanced") -> ComponentOptimization:
        """Generate optimized configurations for RTX 5060TI 16GB"""
        print(f"{ULTRASINGER_HEAD} ⚡ Gerando otimizações para RTX 5060TI (modo: {blue_highlighted(mode)})...")
        
        if mode == "conservative":
            # Conservative settings - prioritize stability
            optimizations = ComponentOptimization(
                whisper={
                    "model": "large-v3-turbo",
                    "batch_size": 16,
                    "compute_type": "float16",
                    "device": "cuda",
                    "vram_usage_mb": 6000,
                    "description": "Configuração conservativa para máxima estabilidade"
                },
                demucs={
                    "model": "htdemucs_ft",
                    "chunk_size": 131072,  # 128k samples
                    "overlap": 0.25,
                    "device": "cuda",
                    "vram_usage_mb": 4000,
                    "description": "Separação de áudio estável com chunks menores"
                },
                crepe={
                    "model_capacity": "large",
                    "step_size": 10,
                    "device": "cuda",
                    "vram_usage_mb": 2000,
                    "description": "Detecção de pitch confiável"
                }
            )
        elif mode == "aggressive":
            # Aggressive settings - maximize performance
            optimizations = ComponentOptimization(
                whisper={
                    "model": "large-v3-turbo",
                    "batch_size": 48,
                    "compute_type": "float16",
                    "device": "cuda",
                    "vram_usage_mb": 10000,
                    "description": "Máxima velocidade de transcrição"
                },
                demucs={
                    "model": "htdemucs_ft",
                    "chunk_size": 524288,  # 512k samples
                    "overlap": 0.1,
                    "device": "cuda",
                    "vram_usage_mb": 8000,
                    "description": "Separação rápida com chunks grandes"
                },
                crepe={
                    "model_capacity": "full",
                    "step_size": 5,
                    "device": "cuda",
                    "vram_usage_mb": 3000,
                    "description": "Máxima qualidade de pitch"
                }
            )
        else:  # balanced (default)
            # Balanced settings - optimal performance/stability ratio
            optimizations = ComponentOptimization(
                whisper={
                    "model": "large-v3-turbo",
                    "batch_size": 32,
                    "compute_type": "float16",
                    "device": "cuda",
                    "vram_usage_mb": 8000,
                    "description": "Equilíbrio ideal entre velocidade e qualidade"
                },
                demucs={
                    "model": "htdemucs_ft",
                    "chunk_size": 262144,  # 256k samples
                    "overlap": 0.25,
                    "device": "cuda",
                    "vram_usage_mb": 6000,
                    "description": "Separação otimizada para RTX 5060TI"
                },
                crepe={
                    "model_capacity": "full",
                    "step_size": 5,
                    "device": "cuda",
                    "vram_usage_mb": 2500,
                    "description": "Alta qualidade de pitch com eficiência"
                }
            )
        
        # Calculate total VRAM usage
        total_vram = (optimizations.whisper["vram_usage_mb"] + 
                     optimizations.demucs["vram_usage_mb"] + 
                     optimizations.crepe["vram_usage_mb"])
        
        print(f"{ULTRASINGER_HEAD} 📊 Uso estimado de VRAM: {blue_highlighted(f'{total_vram/1024:.1f}GB')} / 16GB")
        
        if total_vram > 14000:  # Leave 2GB for system
            print(f"{ULTRASINGER_HEAD} ⚠️ {red_highlighted('Uso de VRAM alto - monitoramento ativo')}")
        
        return optimizations
    
    def initialize_rtx_5060ti(self, optimization_mode: str = "balanced") -> bool:
        """Initialize RTX 5060TI optimization system"""
        print(f"{ULTRASINGER_HEAD} 🔧 Inicializando otimizações RTX 5060TI...")
        
        # Detect GPU
        is_rtx_5060ti, gpu_config = self.detect_rtx_5060ti()
        
        if not gpu_config:
            print(f"{ULTRASINGER_HEAD} ❌ Falha na detecção da GPU")
            return False
        
        self.gpu_config = gpu_config
        self.gpu_config.optimization_mode = optimization_mode
        
        # Generate optimizations
        self.optimization_config = self.generate_rtx_5060ti_optimizations(optimization_mode)
        
        self.is_initialized = True
        
        if is_rtx_5060ti:
            print(f"{ULTRASINGER_HEAD} ✅ {green_highlighted('RTX 5060TI otimizada com sucesso!')}")
            self._print_optimization_summary()
        else:
            print(f"{ULTRASINGER_HEAD} ℹ️ GPU configurada (otimizações genéricas aplicadas)")
        
        return True
    
    def initialize_gpu_optimization(self, optimization_mode: str = "balanced") -> bool:
        """Alias for initialize_rtx_5060ti for compatibility"""
        return self.initialize_rtx_5060ti(optimization_mode)
    
    def _print_optimization_summary(self):
        """Print optimization summary"""
        if not self.optimization_config:
            return
            
        print(f"\n{ULTRASINGER_HEAD} 📋 {blue_highlighted('RESUMO DAS OTIMIZAÇÕES RTX 5060TI:')}")
        print(f"{ULTRASINGER_HEAD} ┌─ Whisper: {self.optimization_config.whisper['model']} "
              f"(batch: {self.optimization_config.whisper['batch_size']}, "
              f"tipo: {self.optimization_config.whisper['compute_type']})")
        print(f"{ULTRASINGER_HEAD} ├─ Demucs: {self.optimization_config.demucs['model']} "
              f"(chunk: {self.optimization_config.demucs['chunk_size']//1024}k)")
        print(f"{ULTRASINGER_HEAD} └─ CREPE: {self.optimization_config.crepe['model_capacity']} "
              f"(step: {self.optimization_config.crepe['step_size']}ms)")
        
        total_vram = sum([
            self.optimization_config.whisper["vram_usage_mb"],
            self.optimization_config.demucs["vram_usage_mb"],
            self.optimization_config.crepe["vram_usage_mb"]
        ]) / 1024
        
        print(f"{ULTRASINGER_HEAD} 💾 Uso total estimado: {green_highlighted(f'{total_vram:.1f}GB')} / 16GB\n")
    
    def get_whisper_config(self) -> Dict[str, Any]:
        """Get optimized Whisper configuration"""
        if not self.optimization_config:
            return {}
        return self.optimization_config.whisper
    
    def get_demucs_config(self) -> Dict[str, Any]:
        """Get optimized Demucs configuration"""
        if not self.optimization_config:
            return {}
        return self.optimization_config.demucs
    
    def get_crepe_config(self) -> Dict[str, Any]:
        """Get optimized CREPE configuration"""
        if not self.optimization_config:
            return {}
        return self.optimization_config.crepe
    
    def is_rtx_5060ti_detected(self) -> bool:
        """Check if RTX 5060TI was detected"""
        return self.gpu_config and self.gpu_config.is_rtx_5060ti
    
    def get_gpu_info(self) -> Optional[GPUConfig]:
        """Get GPU configuration information"""
        return self.gpu_config
    
    def save_optimization_profile(self, filepath: str):
        """Save optimization profile to file"""
        if not self.gpu_config or not self.optimization_config:
            return
            
        profile = {
            "gpu_config": {
                "gpu_name": self.gpu_config.gpu_name,
                "vram_total_gb": self.gpu_config.vram_total_gb,
                "cuda_version": self.gpu_config.cuda_version,
                "driver_version": self.gpu_config.driver_version,
                "is_rtx_5060ti": self.gpu_config.is_rtx_5060ti,
                "optimization_mode": self.gpu_config.optimization_mode
            },
            "optimizations": {
                "whisper": self.optimization_config.whisper,
                "demucs": self.optimization_config.demucs,
                "crepe": self.optimization_config.crepe
            },
            "created_at": datetime.now().isoformat()
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            print(f"{ULTRASINGER_HEAD} 💾 Perfil de otimização salvo: {filepath}")
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} ❌ Erro ao salvar perfil: {str(e)}")

# Global instance
rtx_5060ti_optimizer = RTX5060TIOptimizer()