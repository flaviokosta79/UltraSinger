"""
Módulo de otimização de performance para UltraSinger
Gerencia recursos de hardware, memória e otimizações de processamento
"""

import os
import sys
import psutil
import torch
import gc
import threading
import time
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

from modules.console_colors import ULTRASINGER_HEAD, red_highlighted, blue_highlighted, green_highlighted, yellow_highlighted
from modules.logger import get_logger

logger = get_logger()


class DeviceType(Enum):
    """Tipos de dispositivo disponíveis"""
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"  # Apple Metal Performance Shaders


class ProcessingMode(Enum):
    """Modos de processamento"""
    FAST = "fast"           # Prioriza velocidade
    BALANCED = "balanced"   # Equilibra velocidade e qualidade
    QUALITY = "quality"     # Prioriza qualidade
    MEMORY_EFFICIENT = "memory_efficient"  # Otimiza uso de memória


@dataclass
class SystemResources:
    """Informações sobre recursos do sistema"""
    cpu_count: int
    cpu_percent: float
    memory_total: float  # GB
    memory_available: float  # GB
    memory_percent: float
    gpu_available: bool
    gpu_count: int
    gpu_memory_total: float  # GB
    gpu_memory_free: float  # GB
    gpu_name: str
    platform: str


@dataclass
class OptimizationSettings:
    """Configurações de otimização"""
    device_type: DeviceType
    processing_mode: ProcessingMode
    batch_size: int
    num_workers: int
    memory_limit_gb: float
    enable_mixed_precision: bool
    enable_gradient_checkpointing: bool
    cache_enabled: bool
    prefetch_factor: int


class PerformanceOptimizer:
    """Otimizador de performance principal"""
    
    def __init__(self, log_performance: bool = True):
        self.log_performance = log_performance
        self.system_resources = self._detect_system_resources()
        self.optimization_settings = self._create_default_settings()
        self._setup_environment()
        
        # Métricas de performance
        self.performance_metrics = {
            'memory_usage': [],
            'processing_times': [],
            'gpu_utilization': [],
            'cpu_utilization': []
        }
        
        # Thread para monitoramento
        self._monitoring_active = False
        self._monitoring_thread = None
    
    def _detect_system_resources(self) -> SystemResources:
        """Detectar recursos disponíveis do sistema"""
        logger.info("Detectando recursos do sistema", module="Performance")
        
        # CPU
        cpu_count = psutil.cpu_count(logical=True)
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memória
        memory = psutil.virtual_memory()
        memory_total = memory.total / (1024**3)  # GB
        memory_available = memory.available / (1024**3)  # GB
        memory_percent = memory.percent
        
        # GPU
        gpu_available = torch.cuda.is_available()
        gpu_count = torch.cuda.device_count() if gpu_available else 0
        gpu_memory_total = 0.0
        gpu_memory_free = 0.0
        gpu_name = "None"
        
        if gpu_available and gpu_count > 0:
            try:
                gpu_props = torch.cuda.get_device_properties(0)
                gpu_memory_total = gpu_props.total_memory / (1024**3)  # GB
                gpu_memory_free = (gpu_props.total_memory - torch.cuda.memory_allocated(0)) / (1024**3)
                gpu_name = gpu_props.name
            except Exception as e:
                logger.warning(f"Erro ao obter informações da GPU: {e}", module="Performance")
        
        # Plataforma
        platform = sys.platform
        
        resources = SystemResources(
            cpu_count=cpu_count,
            cpu_percent=cpu_percent,
            memory_total=memory_total,
            memory_available=memory_available,
            memory_percent=memory_percent,
            gpu_available=gpu_available,
            gpu_count=gpu_count,
            gpu_memory_total=gpu_memory_total,
            gpu_memory_free=gpu_memory_free,
            gpu_name=gpu_name,
            platform=platform
        )
        
        self._log_system_resources(resources)
        return resources
    
    def _log_system_resources(self, resources: SystemResources):
        """Log das informações de recursos do sistema"""
        print(f"{ULTRASINGER_HEAD} {blue_highlighted('Sistema detectado:')}")
        print(f"  CPU: {resources.cpu_count} cores ({resources.cpu_percent:.1f}% uso)")
        print(f"  RAM: {resources.memory_available:.1f}GB disponível de {resources.memory_total:.1f}GB ({resources.memory_percent:.1f}% uso)")
        
        if resources.gpu_available:
            print(f"  GPU: {green_highlighted(resources.gpu_name)}")
            print(f"  VRAM: {resources.gpu_memory_free:.1f}GB disponível de {resources.gpu_memory_total:.1f}GB")
            
            if resources.gpu_memory_total < 4.0:
                print(f"  {yellow_highlighted('Aviso: GPU com pouca VRAM, considere usar CPU para modelos grandes')}")
        else:
            print(f"  GPU: {red_highlighted('Não disponível')}")
        
        print(f"  Plataforma: {resources.platform}")
    
    def _create_default_settings(self) -> OptimizationSettings:
        """Criar configurações padrão baseadas nos recursos do sistema"""
        
        # Determinar dispositivo
        if self.system_resources.gpu_available and self.system_resources.gpu_memory_total >= 4.0:
            device_type = DeviceType.CUDA
        elif sys.platform == "darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device_type = DeviceType.MPS
        else:
            device_type = DeviceType.CPU
        
        # Determinar modo de processamento baseado nos recursos
        if self.system_resources.memory_total < 8.0:
            processing_mode = ProcessingMode.MEMORY_EFFICIENT
        elif self.system_resources.gpu_available and self.system_resources.gpu_memory_total >= 8.0:
            processing_mode = ProcessingMode.FAST
        else:
            processing_mode = ProcessingMode.BALANCED
        
        # Configurações baseadas no modo
        if processing_mode == ProcessingMode.MEMORY_EFFICIENT:
            batch_size = 1
            num_workers = min(2, self.system_resources.cpu_count // 2)
            memory_limit_gb = self.system_resources.memory_available * 0.5
        elif processing_mode == ProcessingMode.FAST:
            batch_size = 4 if device_type == DeviceType.CUDA else 2
            num_workers = min(4, self.system_resources.cpu_count)
            memory_limit_gb = self.system_resources.memory_available * 0.7
        else:  # BALANCED
            batch_size = 2
            num_workers = min(3, self.system_resources.cpu_count // 2)
            memory_limit_gb = self.system_resources.memory_available * 0.6
        
        # Configurações avançadas
        enable_mixed_precision = device_type == DeviceType.CUDA and self.system_resources.gpu_memory_total >= 6.0
        enable_gradient_checkpointing = processing_mode == ProcessingMode.MEMORY_EFFICIENT
        
        settings = OptimizationSettings(
            device_type=device_type,
            processing_mode=processing_mode,
            batch_size=batch_size,
            num_workers=num_workers,
            memory_limit_gb=memory_limit_gb,
            enable_mixed_precision=enable_mixed_precision,
            enable_gradient_checkpointing=enable_gradient_checkpointing,
            cache_enabled=True,
            prefetch_factor=2
        )
        
        logger.info(f"Configurações de otimização criadas", module="Performance", 
                   device=device_type.value, mode=processing_mode.value, batch_size=batch_size)
        
        return settings
    
    def _setup_environment(self):
        """Configurar variáveis de ambiente para otimização"""
        
        # PyTorch
        if self.optimization_settings.device_type == DeviceType.CPU:
            # Otimizações para CPU
            torch.set_num_threads(self.optimization_settings.num_workers)
            os.environ["OMP_NUM_THREADS"] = str(self.optimization_settings.num_workers)
            os.environ["MKL_NUM_THREADS"] = str(self.optimization_settings.num_workers)
        
        # TensorFlow
        if TF_AVAILABLE:
            # Configurar uso de memória GPU para TensorFlow
            if self.optimization_settings.device_type == DeviceType.CUDA:
                try:
                    gpus = tf.config.experimental.list_physical_devices('GPU')
                    if gpus:
                        for gpu in gpus:
                            tf.config.experimental.set_memory_growth(gpu, True)
                except Exception as e:
                    logger.warning(f"Erro ao configurar TensorFlow GPU: {e}", module="Performance")
        
        # Configurações gerais
        os.environ["PYTHONHASHSEED"] = "0"  # Para reprodutibilidade
        
        logger.info("Ambiente configurado para otimização", module="Performance")
    
    def get_optimized_settings(self, processing_mode: ProcessingMode = None, device_type: DeviceType = None) -> OptimizationSettings:
        """Obter configurações otimizadas para um modo específico"""
        
        # Usar configurações atuais como base
        settings = OptimizationSettings(
            device_type=device_type or self.optimization_settings.device_type,
            processing_mode=processing_mode or self.optimization_settings.processing_mode,
            batch_size=self.optimization_settings.batch_size,
            num_workers=self.optimization_settings.num_workers,
            memory_limit_gb=self.optimization_settings.memory_limit_gb,
            enable_mixed_precision=self.optimization_settings.enable_mixed_precision,
            enable_gradient_checkpointing=self.optimization_settings.enable_gradient_checkpointing,
            cache_enabled=self.optimization_settings.cache_enabled,
            prefetch_factor=self.optimization_settings.prefetch_factor
        )
        
        # Ajustar baseado no modo solicitado
        if processing_mode:
            if processing_mode == ProcessingMode.MEMORY_EFFICIENT:
                settings.batch_size = 1
                settings.num_workers = min(2, self.system_resources.cpu_count // 2)
                settings.memory_limit_gb = self.system_resources.memory_available * 0.5
                settings.enable_gradient_checkpointing = True
            elif processing_mode == ProcessingMode.FAST:
                settings.batch_size = 4 if settings.device_type == DeviceType.CUDA else 2
                settings.num_workers = min(4, self.system_resources.cpu_count)
                settings.memory_limit_gb = self.system_resources.memory_available * 0.7
            elif processing_mode == ProcessingMode.BALANCED:
                settings.batch_size = 2
                settings.num_workers = min(3, self.system_resources.cpu_count // 2)
                settings.memory_limit_gb = self.system_resources.memory_available * 0.6
        
        return settings
    
    def optimize_for_task(self, task_type: str, **kwargs) -> Dict[str, Any]:
        """Otimizar configurações para um tipo específico de tarefa"""
        
        optimizations = {}
        
        if task_type == "audio_separation":
            # Demucs é intensivo em memória
            if self.system_resources.gpu_memory_total < 8.0:
                optimizations.update({
                    "device": "cpu",
                    "batch_size": 1,
                    "segment_length": 10.0  # Segmentos menores
                })
            else:
                optimizations.update({
                    "device": self.optimization_settings.device_type.value,
                    "batch_size": self.optimization_settings.batch_size,
                    "segment_length": 20.0
                })
        
        elif task_type == "transcription":
            # Whisper
            model_size = kwargs.get("model_size", "small")
            
            if model_size in ["large", "large-v2", "large-v3"]:
                if self.system_resources.gpu_memory_total < 6.0:
                    optimizations.update({
                        "device": "cpu",
                        "compute_type": "int8"
                    })
                else:
                    optimizations.update({
                        "device": self.optimization_settings.device_type.value,
                        "compute_type": "float16" if self.optimization_settings.enable_mixed_precision else "float32"
                    })
            else:
                optimizations.update({
                    "device": self.optimization_settings.device_type.value,
                    "compute_type": "float16" if self.optimization_settings.enable_mixed_precision else "float32"
                })
        
        elif task_type == "pitch_detection":
            # Crepe
            optimizations.update({
                "device": self.optimization_settings.device_type.value,
                "batch_size": min(32, self.optimization_settings.batch_size * 8),
                "step_size": 10 if self.optimization_settings.processing_mode == ProcessingMode.FAST else 20
            })
        
        elif task_type == "sheet_generation":
            # MuseScore é CPU-bound
            optimizations.update({
                "parallel_processing": False,  # MuseScore não suporta paralelização
                "memory_limit": min(2.0, self.optimization_settings.memory_limit_gb)
            })
        
        logger.info(f"Otimizações aplicadas para {task_type}", module="Performance", **optimizations)
        return optimizations
    
    def start_monitoring(self, interval: float = 5.0):
        """Iniciar monitoramento de performance em tempo real"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self._monitoring_thread.start()
        
        logger.info("Monitoramento de performance iniciado", module="Performance", interval=interval)
    
    def stop_monitoring(self):
        """Parar monitoramento de performance"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=1.0)
        
        logger.info("Monitoramento de performance parado", module="Performance")
    
    def _monitoring_loop(self, interval: float):
        """Loop de monitoramento de performance"""
        while self._monitoring_active:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent()
                
                # Memória
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # GPU
                gpu_percent = 0.0
                if self.system_resources.gpu_available:
                    try:
                        gpu_memory_used = torch.cuda.memory_allocated(0) / (1024**3)  # GB
                        gpu_percent = (gpu_memory_used / self.system_resources.gpu_memory_total) * 100
                    except:
                        pass
                
                # Salvar métricas
                self.performance_metrics['cpu_utilization'].append(cpu_percent)
                self.performance_metrics['memory_usage'].append(memory_percent)
                self.performance_metrics['gpu_utilization'].append(gpu_percent)
                
                # Manter apenas últimas 100 medições
                for key in self.performance_metrics:
                    if len(self.performance_metrics[key]) > 100:
                        self.performance_metrics[key] = self.performance_metrics[key][-100:]
                
                # Log se uso estiver alto
                if cpu_percent > 90:
                    logger.warning(f"Alto uso de CPU: {cpu_percent:.1f}%", module="Performance")
                
                if memory_percent > 90:
                    logger.warning(f"Alto uso de memória: {memory_percent:.1f}%", module="Performance")
                
                if gpu_percent > 90:
                    logger.warning(f"Alto uso de GPU: {gpu_percent:.1f}%", module="Performance")
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Erro no monitoramento de performance: {e}", module="Performance")
                time.sleep(interval)
    
    def cleanup_memory(self):
        """Limpeza agressiva de memória"""
        logger.info("Iniciando limpeza de memória", module="Performance")
        
        # Python garbage collection
        collected = gc.collect()
        
        # PyTorch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        # TensorFlow
        if TF_AVAILABLE:
            try:
                tf.keras.backend.clear_session()
            except:
                pass
        
        logger.info(f"Limpeza de memória concluída", module="Performance", objects_collected=collected)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Gerar relatório de performance"""
        
        if not self.performance_metrics['cpu_utilization']:
            return {"error": "Nenhum dado de monitoramento disponível"}
        
        report = {
            "system_resources": {
                "cpu_count": self.system_resources.cpu_count,
                "memory_total_gb": self.system_resources.memory_total,
                "gpu_available": self.system_resources.gpu_available,
                "gpu_name": self.system_resources.gpu_name,
                "gpu_memory_total_gb": self.system_resources.gpu_memory_total
            },
            "optimization_settings": {
                "device_type": self.optimization_settings.device_type.value,
                "processing_mode": self.optimization_settings.processing_mode.value,
                "batch_size": self.optimization_settings.batch_size,
                "num_workers": self.optimization_settings.num_workers
            },
            "performance_metrics": {}
        }
        
        # Calcular estatísticas das métricas
        for metric_name, values in self.performance_metrics.items():
            if values:
                report["performance_metrics"][metric_name] = {
                    "avg": sum(values) / len(values),
                    "max": max(values),
                    "min": min(values),
                    "current": values[-1] if values else 0
                }
        
        return report
    
    def suggest_optimizations(self) -> List[str]:
        """Sugerir otimizações baseadas no uso atual"""
        suggestions = []
        
        if not self.performance_metrics['cpu_utilization']:
            return ["Inicie o monitoramento para receber sugestões"]
        
        # Análise de CPU
        avg_cpu = sum(self.performance_metrics['cpu_utilization']) / len(self.performance_metrics['cpu_utilization'])
        if avg_cpu > 80:
            suggestions.append("CPU com alto uso - considere reduzir batch_size ou num_workers")
        elif avg_cpu < 30:
            suggestions.append("CPU subutilizada - considere aumentar batch_size ou num_workers")
        
        # Análise de memória
        avg_memory = sum(self.performance_metrics['memory_usage']) / len(self.performance_metrics['memory_usage'])
        if avg_memory > 85:
            suggestions.append("Memória com alto uso - considere modo MEMORY_EFFICIENT")
        
        # Análise de GPU
        if self.system_resources.gpu_available:
            avg_gpu = sum(self.performance_metrics['gpu_utilization']) / len(self.performance_metrics['gpu_utilization'])
            if avg_gpu < 20 and self.optimization_settings.device_type == DeviceType.CUDA:
                suggestions.append("GPU subutilizada - verifique se os modelos estão usando GPU")
            elif avg_gpu > 90:
                suggestions.append("GPU com alto uso - considere reduzir batch_size")
        
        return suggestions if suggestions else ["Sistema operando de forma otimizada"]


def get_optimal_device(force_cpu: bool = False) -> str:
    """Obter dispositivo ótimo para processamento"""
    if force_cpu:
        return "cpu"
    
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        if gpu_memory >= 4.0:  # Mínimo 4GB para usar GPU
            return "cuda"
    
    if sys.platform == "darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return "mps"
    
    return "cpu"


def estimate_processing_time(task_type: str, input_size: float, device: str = "auto") -> float:
    """Estimar tempo de processamento para uma tarefa"""
    
    if device == "auto":
        device = get_optimal_device()
    
    # Estimativas baseadas em benchmarks (em segundos por MB de áudio)
    base_times = {
        "audio_separation": {"cpu": 2.5, "cuda": 0.8, "mps": 1.2},
        "transcription": {"cpu": 1.8, "cuda": 0.5, "mps": 0.7},
        "pitch_detection": {"cpu": 1.2, "cuda": 0.3, "mps": 0.5},
        "sheet_generation": {"cpu": 0.1, "cuda": 0.1, "mps": 0.1}  # CPU-bound
    }
    
    if task_type not in base_times:
        return input_size * 1.0  # Estimativa genérica
    
    device_key = device if device in base_times[task_type] else "cpu"
    base_time = base_times[task_type][device_key]
    
    return input_size * base_time


# Instância global
_global_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """Obter instância global do otimizador de performance"""
    global _global_optimizer
    
    if _global_optimizer is None:
        _global_optimizer = PerformanceOptimizer()
    
    return _global_optimizer