"""Intelligent CPU/GPU Fallback System for RTX 5060TI"""

import torch
import psutil
import time
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import traceback

from modules.console_colors import ULTRASINGER_HEAD, red_highlighted, blue_highlighted, green_highlighted, yellow_highlighted

@dataclass
class FallbackEvent:
    """Fallback event information"""
    timestamp: datetime
    component: str
    reason: str
    error_message: str
    fallback_action: str
    success: bool
    recovery_time_seconds: float

@dataclass
class ComponentHealth:
    """Component health status"""
    component_name: str
    is_healthy: bool
    last_error: Optional[str]
    error_count: int
    last_success_time: datetime
    consecutive_failures: int
    fallback_active: bool
    recovery_attempts: int

class GPUFallbackSystem:
    """Intelligent CPU/GPU fallback system for RTX 5060TI"""
    
    def __init__(self, rtx_optimizer=None, performance_monitor=None):
        self.rtx_optimizer = rtx_optimizer
        self.performance_monitor = performance_monitor
        self.component_health: Dict[str, ComponentHealth] = {}
        self.fallback_events: List[FallbackEvent] = []
        self.is_monitoring = False
        self.monitoring_thread = None
        self.is_initialized = False
        
        # Fallback thresholds
        self.thresholds = {
            "max_consecutive_failures": 3,
            "vram_critical_percent": 95.0,
            "temperature_critical_celsius": 87,
            "recovery_timeout_seconds": 300,  # 5 minutes
            "health_check_interval": 30,      # 30 seconds
            "max_recovery_attempts": 5
        }
        
        # Component configurations
        self.component_configs = {
            "whisper": {
                "gpu_fallback": {"device": "cpu", "compute_type": "int8"},
                "cpu_config": {"device": "cpu", "compute_type": "int8", "batch_size": 4}
            },
            "demucs": {
                "gpu_fallback": {"device": "cpu", "chunk_size": 65536},
                "cpu_config": {"device": "cpu", "chunk_size": 32768, "jobs": psutil.cpu_count()}
            },
            "crepe": {
                "gpu_fallback": {"device": "cpu", "batch_size": 64},
                "cpu_config": {"device": "cpu", "batch_size": 32, "model_capacity": "large"}
            }
        }
        
        self.fallback_callbacks: Dict[str, List[Callable]] = {}
    
    def initialize(self):
        """Initialize the fallback system"""
        print(f"{ULTRASINGER_HEAD} 🔧 Inicializando sistema de fallback...")
        
        # Initialize health tracking for all components
        for component in ["whisper", "demucs", "crepe"]:
            self.initialize_component_health(component)
        
        self.is_initialized = True
        print(f"{ULTRASINGER_HEAD} ✅ {green_highlighted('Sistema de fallback inicializado')}")
        return True
        
    def initialize_component_health(self, component_name: str):
        """Initialize health tracking for a component"""
        if component_name not in self.component_health:
            self.component_health[component_name] = ComponentHealth(
                component_name=component_name,
                is_healthy=True,
                last_error=None,
                error_count=0,
                last_success_time=datetime.now(),
                consecutive_failures=0,
                fallback_active=False,
                recovery_attempts=0
            )
            
            print(f"{ULTRASINGER_HEAD} 🏥 Inicializando monitoramento de saúde: {blue_highlighted(component_name)}")
    
    def start_health_monitoring(self):
        """Start health monitoring system"""
        if self.is_monitoring:
            return
            
        print(f"{ULTRASINGER_HEAD} 🔍 Iniciando sistema de monitoramento de saúde...")
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._health_monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        print(f"{ULTRASINGER_HEAD} ✅ {green_highlighted('Sistema de fallback ativo')}")
    
    def stop_health_monitoring(self):
        """Stop health monitoring system"""
        if not self.is_monitoring:
            return
            
        print(f"{ULTRASINGER_HEAD} 🛑 Parando sistema de monitoramento...")
        self.is_monitoring = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        
        print(f"{ULTRASINGER_HEAD} ✅ Sistema de fallback parado")
    
    def cleanup(self):
        """Cleanup fallback system resources"""
        self.stop_health_monitoring()
        print(f"{ULTRASINGER_HEAD} 🧹 Sistema de fallback limpo")
    
    def _health_monitoring_loop(self):
        """Main health monitoring loop"""
        while self.is_monitoring:
            try:
                self._check_system_health()
                self._attempt_recovery()
                time.sleep(self.thresholds["health_check_interval"])
                
            except Exception as e:
                print(f"{ULTRASINGER_HEAD} ⚠️ Erro no monitoramento de saúde: {str(e)}")
                time.sleep(self.thresholds["health_check_interval"])
    
    def _check_system_health(self):
        """Check overall system health"""
        if not self.performance_monitor:
            return
            
        try:
            current_metrics = self.performance_monitor.get_current_metrics()
            if not current_metrics:
                return
            
            # Check VRAM usage
            if current_metrics.vram_usage_percent >= self.thresholds["vram_critical_percent"]:
                self._trigger_vram_fallback(current_metrics.vram_usage_percent)
            
            # Check temperature
            if current_metrics.temperature_celsius >= self.thresholds["temperature_critical_celsius"]:
                self._trigger_temperature_fallback(current_metrics.temperature_celsius)
                
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} ⚠️ Erro na verificação de saúde do sistema: {str(e)}")
    
    def _trigger_vram_fallback(self, vram_usage: float):
        """Trigger fallback due to VRAM issues"""
        print(f"{ULTRASINGER_HEAD} 🚨 {red_highlighted(f'VRAM crítica detectada: {vram_usage:.1f}%')}")
        
        # Find components to fallback
        for component_name in ["whisper", "demucs", "crepe"]:
            if component_name in self.component_health:
                health = self.component_health[component_name]
                if not health.fallback_active:
                    self._execute_fallback(component_name, "vram_critical", 
                                         f"VRAM usage: {vram_usage:.1f}%")
    
    def _trigger_temperature_fallback(self, temperature: int):
        """Trigger fallback due to temperature issues"""
        print(f"{ULTRASINGER_HEAD} 🌡️ {red_highlighted(f'Temperatura crítica detectada: {temperature}°C')}")
        
        # Fallback all GPU components
        for component_name in ["whisper", "demucs", "crepe"]:
            if component_name in self.component_health:
                health = self.component_health[component_name]
                if not health.fallback_active:
                    self._execute_fallback(component_name, "temperature_critical", 
                                         f"Temperature: {temperature}°C")
    
    def report_component_error(self, component_name: str, error: Exception, context: str = ""):
        """Report an error for a component"""
        self.initialize_component_health(component_name)
        health = self.component_health[component_name]
        
        error_message = f"{str(error)} | Context: {context}"
        
        health.last_error = error_message
        health.error_count += 1
        health.consecutive_failures += 1
        health.is_healthy = False
        
        print(f"{ULTRASINGER_HEAD} ❌ Erro em {red_highlighted(component_name)}: {error_message}")
        
        # Check if fallback is needed
        if health.consecutive_failures >= self.thresholds["max_consecutive_failures"]:
            if not health.fallback_active:
                self._execute_fallback(component_name, "consecutive_failures", error_message)
        
        return self._should_fallback(component_name)
    
    def report_component_success(self, component_name: str):
        """Report successful operation for a component"""
        self.initialize_component_health(component_name)
        health = self.component_health[component_name]
        
        health.last_success_time = datetime.now()
        health.consecutive_failures = 0
        health.is_healthy = True
        
        # If component was in fallback, consider recovery
        if health.fallback_active:
            print(f"{ULTRASINGER_HEAD} ✅ {green_highlighted(component_name)} funcionando normalmente")
            self._consider_recovery(component_name)
    
    def _should_fallback(self, component_name: str) -> bool:
        """Determine if component should fallback"""
        if component_name not in self.component_health:
            return False
            
        health = self.component_health[component_name]
        return health.consecutive_failures >= self.thresholds["max_consecutive_failures"]
    
    def _execute_fallback(self, component_name: str, reason: str, error_message: str):
        """Execute fallback for a component"""
        start_time = time.time()
        
        try:
            health = self.component_health[component_name]
            health.fallback_active = True
            
            print(f"{ULTRASINGER_HEAD} 🔄 Executando fallback para {yellow_highlighted(component_name)} (razão: {reason})")
            
            # Get fallback configuration
            fallback_config = self._get_fallback_config(component_name)
            
            # Execute fallback callbacks
            if component_name in self.fallback_callbacks:
                for callback in self.fallback_callbacks[component_name]:
                    try:
                        callback(component_name, fallback_config, reason)
                    except Exception as e:
                        print(f"{ULTRASINGER_HEAD} ⚠️ Erro no callback de fallback: {str(e)}")
            
            recovery_time = time.time() - start_time
            
            # Record fallback event
            event = FallbackEvent(
                timestamp=datetime.now(),
                component=component_name,
                reason=reason,
                error_message=error_message,
                fallback_action=f"CPU fallback with config: {fallback_config}",
                success=True,
                recovery_time_seconds=recovery_time
            )
            
            self.fallback_events.append(event)
            
            print(f"{ULTRASINGER_HEAD} ✅ {green_highlighted(f'Fallback executado para {component_name}')} "
                  f"(tempo: {recovery_time:.2f}s)")
            
        except Exception as e:
            recovery_time = time.time() - start_time
            
            # Record failed fallback event
            event = FallbackEvent(
                timestamp=datetime.now(),
                component=component_name,
                reason=reason,
                error_message=error_message,
                fallback_action=f"Failed CPU fallback: {str(e)}",
                success=False,
                recovery_time_seconds=recovery_time
            )
            
            self.fallback_events.append(event)
            
            print(f"{ULTRASINGER_HEAD} ❌ {red_highlighted(f'Falha no fallback para {component_name}')}: {str(e)}")
    
    def _get_fallback_config(self, component_name: str) -> Dict[str, Any]:
        """Get fallback configuration for component"""
        if component_name in self.component_configs:
            return self.component_configs[component_name]["cpu_config"].copy()
        
        # Default CPU fallback
        return {"device": "cpu"}
    
    def _consider_recovery(self, component_name: str):
        """Consider recovery from fallback to GPU"""
        health = self.component_health[component_name]
        
        # Check if enough time has passed since last error
        time_since_error = datetime.now() - health.last_success_time
        if time_since_error.total_seconds() < self.thresholds["recovery_timeout_seconds"]:
            return
        
        # Check if max recovery attempts reached
        if health.recovery_attempts >= self.thresholds["max_recovery_attempts"]:
            print(f"{ULTRASINGER_HEAD} ⚠️ {yellow_highlighted(f'Máximo de tentativas de recuperação atingido para {component_name}')}")
            return
        
        # Check system conditions
        if not self._is_system_ready_for_recovery():
            return
        
        self._attempt_component_recovery(component_name)
    
    def _is_system_ready_for_recovery(self) -> bool:
        """Check if system is ready for GPU recovery"""
        if not self.performance_monitor:
            return True  # Assume ready if no monitoring
        
        try:
            current_metrics = self.performance_monitor.get_current_metrics()
            if not current_metrics:
                return True
            
            # Check VRAM usage
            if current_metrics.vram_usage_percent >= 80.0:  # Conservative threshold
                return False
            
            # Check temperature
            if current_metrics.temperature_celsius >= 75:  # Conservative threshold
                return False
            
            return True
            
        except Exception:
            return False
    
    def _attempt_component_recovery(self, component_name: str):
        """Attempt to recover component to GPU"""
        health = self.component_health[component_name]
        health.recovery_attempts += 1
        
        print(f"{ULTRASINGER_HEAD} 🔄 Tentando recuperação GPU para {blue_highlighted(component_name)} "
              f"(tentativa {health.recovery_attempts}/{self.thresholds['max_recovery_attempts']})")
        
        try:
            # Get GPU configuration
            gpu_config = self._get_gpu_config(component_name)
            
            # Execute recovery callbacks
            if component_name in self.fallback_callbacks:
                for callback in self.fallback_callbacks[component_name]:
                    try:
                        callback(component_name, gpu_config, "recovery")
                    except Exception as e:
                        print(f"{ULTRASINGER_HEAD} ⚠️ Erro no callback de recuperação: {str(e)}")
                        raise
            
            # If successful, mark as recovered
            health.fallback_active = False
            health.recovery_attempts = 0
            
            print(f"{ULTRASINGER_HEAD} ✅ {green_highlighted(f'Recuperação GPU bem-sucedida para {component_name}')}")
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} ❌ {red_highlighted(f'Falha na recuperação GPU para {component_name}')}: {str(e)}")
    
    def _get_gpu_config(self, component_name: str) -> Dict[str, Any]:
        """Get GPU configuration for component"""
        if self.rtx_optimizer and hasattr(self.rtx_optimizer, 'optimization_config'):
            if component_name == "whisper":
                return self.rtx_optimizer.get_whisper_config()
            elif component_name == "demucs":
                return self.rtx_optimizer.get_demucs_config()
            elif component_name == "crepe":
                return self.rtx_optimizer.get_crepe_config()
        
        # Default GPU config
        return {"device": "cuda"}
    
    def _attempt_recovery(self):
        """Attempt recovery for components in fallback"""
        for component_name, health in self.component_health.items():
            if health.fallback_active and health.is_healthy:
                self._consider_recovery(component_name)
    
    def add_fallback_callback(self, component_name: str, callback: Callable):
        """Add callback for fallback events"""
        if component_name not in self.fallback_callbacks:
            self.fallback_callbacks[component_name] = []
        
        self.fallback_callbacks[component_name].append(callback)
        print(f"{ULTRASINGER_HEAD} 📞 Callback de fallback adicionado para {component_name}")
    
    def get_component_status(self, component_name: str) -> Optional[ComponentHealth]:
        """Get component health status"""
        return self.component_health.get(component_name)
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check and return system health status"""
        return self.get_system_status()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        total_components = len(self.component_health)
        healthy_components = sum(1 for h in self.component_health.values() if h.is_healthy)
        fallback_components = sum(1 for h in self.component_health.values() if h.fallback_active)
        
        return {
            "monitoring_active": self.is_monitoring,
            "total_components": total_components,
            "healthy_components": healthy_components,
            "unhealthy_components": total_components - healthy_components,
            "fallback_components": fallback_components,
            "total_fallback_events": len(self.fallback_events),
            "successful_fallbacks": len([e for e in self.fallback_events if e.success]),
            "failed_fallbacks": len([e for e in self.fallback_events if not e.success]),
            "components": {
                name: {
                    "is_healthy": health.is_healthy,
                    "fallback_active": health.fallback_active,
                    "error_count": health.error_count,
                    "consecutive_failures": health.consecutive_failures,
                    "recovery_attempts": health.recovery_attempts,
                    "last_success": health.last_success_time.isoformat()
                }
                for name, health in self.component_health.items()
            }
        }
    
    def print_system_status(self):
        """Print detailed system status"""
        status = self.get_system_status()
        
        print(f"\n{ULTRASINGER_HEAD} 🏥 {blue_highlighted('STATUS DO SISTEMA DE FALLBACK:')}")
        print(f"{ULTRASINGER_HEAD} ┌─ Monitoramento: {'🟢 Ativo' if status['monitoring_active'] else '🔴 Inativo'}")
        print(f"{ULTRASINGER_HEAD} ├─ Componentes: {status['total_components']} total")
        print(f"{ULTRASINGER_HEAD} ├─ Saudáveis: {green_highlighted(str(status['healthy_components']))}")
        print(f"{ULTRASINGER_HEAD} ├─ Não saudáveis: {red_highlighted(str(status['unhealthy_components']))}")
        print(f"{ULTRASINGER_HEAD} ├─ Em fallback: {yellow_highlighted(str(status['fallback_components']))}")
        print(f"{ULTRASINGER_HEAD} ├─ Eventos de fallback: {status['total_fallback_events']} "
              f"({status['successful_fallbacks']} sucessos, {status['failed_fallbacks']} falhas)")
        
        if status['components']:
            print(f"{ULTRASINGER_HEAD} └─ Detalhes dos componentes:")
            for name, comp_status in status['components'].items():
                status_icon = "🟢" if comp_status['is_healthy'] else "🔴"
                fallback_icon = "🔄" if comp_status['fallback_active'] else "⚡"
                print(f"{ULTRASINGER_HEAD}    ├─ {status_icon} {fallback_icon} {name}: "
                      f"erros={comp_status['error_count']}, "
                      f"falhas_consecutivas={comp_status['consecutive_failures']}, "
                      f"tentativas_recuperação={comp_status['recovery_attempts']}")
        
        print()
    
    def force_component_fallback(self, component_name: str, reason: str = "manual"):
        """Force fallback for a specific component"""
        print(f"{ULTRASINGER_HEAD} 🔧 Forçando fallback manual para {blue_highlighted(component_name)}")
        self._execute_fallback(component_name, reason, "Manual fallback requested")
    
    def force_component_recovery(self, component_name: str):
        """Force recovery for a specific component"""
        if component_name not in self.component_health:
            print(f"{ULTRASINGER_HEAD} ⚠️ Componente {component_name} não encontrado")
            return
        
        print(f"{ULTRASINGER_HEAD} 🔧 Forçando recuperação manual para {blue_highlighted(component_name)}")
        self._attempt_component_recovery(component_name)

# Global instance
gpu_fallback_system = GPUFallbackSystem()