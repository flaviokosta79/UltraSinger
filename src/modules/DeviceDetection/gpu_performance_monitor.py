"""GPU Performance Monitor for RTX 5060TI 16GB"""

import torch
import psutil
import time
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

from modules.console_colors import ULTRASINGER_HEAD, red_highlighted, blue_highlighted, green_highlighted, yellow_highlighted

@dataclass
class GPUMetrics:
    """GPU performance metrics"""
    timestamp: datetime
    vram_used_mb: int
    vram_total_mb: int
    vram_usage_percent: float
    gpu_utilization_percent: float
    temperature_celsius: int
    power_draw_watts: int
    memory_clock_mhz: int
    gpu_clock_mhz: int

@dataclass
class PerformanceAlert:
    """Performance alert information"""
    level: str  # info, warning, critical
    message: str
    timestamp: datetime
    metric_name: str
    current_value: float
    threshold_value: float

@dataclass
class ComponentPerformance:
    """Performance tracking for each component"""
    component_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    peak_vram_mb: int = 0
    avg_vram_mb: int = 0
    peak_gpu_util: float = 0.0
    avg_gpu_util: float = 0.0
    processing_time_seconds: float = 0.0
    samples_count: int = 0
    metrics_history: List[GPUMetrics] = field(default_factory=list)

class GPUPerformanceMonitor:
    """Real-time GPU performance monitor for RTX 5060TI"""
    
    def __init__(self, rtx_5060ti_optimizer=None):
        self.rtx_optimizer = rtx_5060ti_optimizer
        self.is_monitoring = False
        self.monitoring_thread = None
        self.metrics_history: List[GPUMetrics] = []
        self.alerts: List[PerformanceAlert] = []
        self.component_tracking: Dict[str, ComponentPerformance] = {}
        self.alert_callbacks: List[Callable] = []
        
        # Performance thresholds for RTX 5060TI 16GB
        self.thresholds = {
            "vram_warning_percent": 80.0,      # 12.8GB
            "vram_critical_percent": 90.0,     # 14.4GB
            "gpu_util_warning_percent": 95.0,
            "temperature_warning_celsius": 80,
            "temperature_critical_celsius": 85,
            "power_warning_watts": 200,
            "memory_clock_min_mhz": 8000,      # Expected for RTX 5060TI
            "gpu_clock_min_mhz": 1500
        }
        
        self.monitoring_interval = 1.0  # seconds
        self.max_history_size = 300     # 5 minutes at 1s intervals
        
    def start_monitoring(self):
        """Start real-time GPU monitoring"""
        if self.is_monitoring:
            return
            
        print(f"{ULTRASINGER_HEAD} 📊 Iniciando monitoramento de performance RTX 5060TI...")
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        print(f"{ULTRASINGER_HEAD} ✅ {green_highlighted('Monitor de performance ativo')}")
    
    def stop_monitoring(self):
        """Stop GPU monitoring"""
        if not self.is_monitoring:
            return
            
        print(f"{ULTRASINGER_HEAD} 🛑 Parando monitor de performance...")
        self.is_monitoring = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        
        print(f"{ULTRASINGER_HEAD} ✅ Monitor de performance parado")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self._collect_gpu_metrics()
                if metrics:
                    self._process_metrics(metrics)
                    self._check_alerts(metrics)
                    
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"{ULTRASINGER_HEAD} ⚠️ Erro no monitoramento: {str(e)}")
                time.sleep(self.monitoring_interval)
    
    def _collect_gpu_metrics(self) -> Optional[GPUMetrics]:
        """Collect current GPU metrics"""
        try:
            if not torch.cuda.is_available():
                return None
                
            # Get VRAM usage
            vram_used = torch.cuda.memory_allocated(0)
            vram_reserved = torch.cuda.memory_reserved(0)
            vram_total = torch.cuda.get_device_properties(0).total_memory
            
            vram_used_mb = int(vram_used / (1024**2))
            vram_total_mb = int(vram_total / (1024**2))
            vram_usage_percent = (vram_used / vram_total) * 100
            
            # Try to get additional metrics via nvidia-ml-py if available
            gpu_util = 0.0
            temperature = 0
            power_draw = 0
            memory_clock = 0
            gpu_clock = 0
            
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                
                # GPU utilization
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_util = float(util.gpu)
                
                # Temperature
                temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                
                # Power draw
                try:
                    power_draw = pynvml.nvmlDeviceGetPowerUsage(handle) // 1000  # mW to W
                except:
                    power_draw = 0
                
                # Clock speeds
                try:
                    memory_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
                    gpu_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
                except:
                    memory_clock = 0
                    gpu_clock = 0
                    
            except ImportError:
                # pynvml not available, use basic metrics only
                pass
            except Exception:
                # Error getting detailed metrics, continue with basic ones
                pass
            
            return GPUMetrics(
                timestamp=datetime.now(),
                vram_used_mb=vram_used_mb,
                vram_total_mb=vram_total_mb,
                vram_usage_percent=vram_usage_percent,
                gpu_utilization_percent=gpu_util,
                temperature_celsius=temperature,
                power_draw_watts=power_draw,
                memory_clock_mhz=memory_clock,
                gpu_clock_mhz=gpu_clock
            )
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} ⚠️ Erro coletando métricas: {str(e)}")
            return None
    
    def _process_metrics(self, metrics: GPUMetrics):
        """Process and store metrics"""
        # Add to history
        self.metrics_history.append(metrics)
        
        # Limit history size
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
        
        # Update component tracking
        for component_name, component_perf in self.component_tracking.items():
            if component_perf.end_time is None:  # Still running
                component_perf.metrics_history.append(metrics)
                component_perf.peak_vram_mb = max(component_perf.peak_vram_mb, metrics.vram_used_mb)
                component_perf.peak_gpu_util = max(component_perf.peak_gpu_util, metrics.gpu_utilization_percent)
                
                # Calculate averages
                component_perf.samples_count += 1
                component_perf.avg_vram_mb = int(sum(m.vram_used_mb for m in component_perf.metrics_history) / len(component_perf.metrics_history))
                component_perf.avg_gpu_util = sum(m.gpu_utilization_percent for m in component_perf.metrics_history) / len(component_perf.metrics_history)
    
    def _check_alerts(self, metrics: GPUMetrics):
        """Check for performance alerts"""
        alerts = []
        
        # VRAM usage alerts
        if metrics.vram_usage_percent >= self.thresholds["vram_critical_percent"]:
            alerts.append(PerformanceAlert(
                level="critical",
                message=f"VRAM crítica: {metrics.vram_usage_percent:.1f}% ({metrics.vram_used_mb}MB/{metrics.vram_total_mb}MB)",
                timestamp=metrics.timestamp,
                metric_name="vram_usage",
                current_value=metrics.vram_usage_percent,
                threshold_value=self.thresholds["vram_critical_percent"]
            ))
        elif metrics.vram_usage_percent >= self.thresholds["vram_warning_percent"]:
            alerts.append(PerformanceAlert(
                level="warning",
                message=f"VRAM alta: {metrics.vram_usage_percent:.1f}% ({metrics.vram_used_mb}MB/{metrics.vram_total_mb}MB)",
                timestamp=metrics.timestamp,
                metric_name="vram_usage",
                current_value=metrics.vram_usage_percent,
                threshold_value=self.thresholds["vram_warning_percent"]
            ))
        
        # Temperature alerts
        if metrics.temperature_celsius >= self.thresholds["temperature_critical_celsius"]:
            alerts.append(PerformanceAlert(
                level="critical",
                message=f"Temperatura crítica: {metrics.temperature_celsius}°C",
                timestamp=metrics.timestamp,
                metric_name="temperature",
                current_value=metrics.temperature_celsius,
                threshold_value=self.thresholds["temperature_critical_celsius"]
            ))
        elif metrics.temperature_celsius >= self.thresholds["temperature_warning_celsius"]:
            alerts.append(PerformanceAlert(
                level="warning",
                message=f"Temperatura alta: {metrics.temperature_celsius}°C",
                timestamp=metrics.timestamp,
                metric_name="temperature",
                current_value=metrics.temperature_celsius,
                threshold_value=self.thresholds["temperature_warning_celsius"]
            ))
        
        # GPU utilization alerts
        if metrics.gpu_utilization_percent >= self.thresholds["gpu_util_warning_percent"]:
            alerts.append(PerformanceAlert(
                level="warning",
                message=f"GPU utilização alta: {metrics.gpu_utilization_percent:.1f}%",
                timestamp=metrics.timestamp,
                metric_name="gpu_utilization",
                current_value=metrics.gpu_utilization_percent,
                threshold_value=self.thresholds["gpu_util_warning_percent"]
            ))
        
        # Process alerts
        for alert in alerts:
            self._handle_alert(alert)
    
    def _handle_alert(self, alert: PerformanceAlert):
        """Handle performance alert"""
        # Add to alerts history
        self.alerts.append(alert)
        
        # Limit alerts history
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # Print alert
        if alert.level == "critical":
            print(f"{ULTRASINGER_HEAD} 🚨 {red_highlighted(alert.message)}")
        elif alert.level == "warning":
            print(f"{ULTRASINGER_HEAD} ⚠️ {yellow_highlighted(alert.message)}")
        else:
            print(f"{ULTRASINGER_HEAD} ℹ️ {blue_highlighted(alert.message)}")
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"{ULTRASINGER_HEAD} ⚠️ Erro no callback de alerta: {str(e)}")
    
    def start_component_tracking(self, component_name: str):
        """Start tracking performance for a specific component"""
        print(f"{ULTRASINGER_HEAD} 📈 Iniciando tracking: {blue_highlighted(component_name)}")
        
        self.component_tracking[component_name] = ComponentPerformance(
            component_name=component_name,
            start_time=datetime.now()
        )
    
    def stop_component_tracking(self, component_name: str):
        """Stop tracking performance for a specific component"""
        if component_name not in self.component_tracking:
            return
        
        component_perf = self.component_tracking[component_name]
        component_perf.end_time = datetime.now()
        component_perf.processing_time_seconds = (component_perf.end_time - component_perf.start_time).total_seconds()
        
        print(f"{ULTRASINGER_HEAD} 📊 Finalizando tracking: {blue_highlighted(component_name)}")
        self._print_component_summary(component_perf)
    
    def _print_component_summary(self, component_perf: ComponentPerformance):
        """Print component performance summary"""
        print(f"{ULTRASINGER_HEAD} 📋 {blue_highlighted(f'RESUMO - {component_perf.component_name.upper()}:')}")
        print(f"{ULTRASINGER_HEAD} ├─ Tempo de processamento: {green_highlighted(f'{component_perf.processing_time_seconds:.1f}s')}")
        print(f"{ULTRASINGER_HEAD} ├─ VRAM pico: {blue_highlighted(f'{component_perf.peak_vram_mb}MB')} "
              f"(média: {component_perf.avg_vram_mb}MB)")
        print(f"{ULTRASINGER_HEAD} ├─ GPU utilização pico: {blue_highlighted(f'{component_perf.peak_gpu_util:.1f}%')} "
              f"(média: {component_perf.avg_gpu_util:.1f}%)")
        print(f"{ULTRASINGER_HEAD} └─ Amostras coletadas: {component_perf.samples_count}")
    
    def get_current_metrics(self) -> Optional[GPUMetrics]:
        """Get current GPU metrics"""
        return self._collect_gpu_metrics()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.metrics_history[-60:]  # Last minute
        
        return {
            "monitoring_active": self.is_monitoring,
            "total_samples": len(self.metrics_history),
            "monitoring_duration_minutes": len(self.metrics_history) * self.monitoring_interval / 60,
            "current_vram_usage_percent": recent_metrics[-1].vram_usage_percent if recent_metrics else 0,
            "peak_vram_usage_percent": max(m.vram_usage_percent for m in recent_metrics) if recent_metrics else 0,
            "avg_vram_usage_percent": sum(m.vram_usage_percent for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0,
            "current_gpu_utilization": recent_metrics[-1].gpu_utilization_percent if recent_metrics else 0,
            "peak_gpu_utilization": max(m.gpu_utilization_percent for m in recent_metrics) if recent_metrics else 0,
            "avg_gpu_utilization": sum(m.gpu_utilization_percent for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0,
            "current_temperature": recent_metrics[-1].temperature_celsius if recent_metrics else 0,
            "peak_temperature": max(m.temperature_celsius for m in recent_metrics) if recent_metrics else 0,
            "total_alerts": len(self.alerts),
            "critical_alerts": len([a for a in self.alerts if a.level == "critical"]),
            "warning_alerts": len([a for a in self.alerts if a.level == "warning"]),
            "components_tracked": len(self.component_tracking)
        }
    
    def print_performance_report(self):
        """Print detailed performance report"""
        summary = self.get_performance_summary()
        
        if not summary:
            print(f"{ULTRASINGER_HEAD} ℹ️ Nenhum dado de performance disponível")
            return
        
        print(f"\n{ULTRASINGER_HEAD} 📊 {blue_highlighted('RELATÓRIO DE PERFORMANCE RTX 5060TI:')}")
        print(f"{ULTRASINGER_HEAD} ┌─ Status: {'🟢 Ativo' if summary['monitoring_active'] else '🔴 Inativo'}")
        print(f"{ULTRASINGER_HEAD} ├─ Duração: {summary['monitoring_duration_minutes']:.1f} minutos")
        print(f"{ULTRASINGER_HEAD} ├─ Amostras: {summary['total_samples']}")
        vram_current = f"{summary['current_vram_usage_percent']:.1f}%"
        vram_peak = f"{summary['peak_vram_usage_percent']:.1f}%"
        vram_avg = f"{summary['avg_vram_usage_percent']:.1f}%"
        gpu_current = f"{summary['current_gpu_utilization']:.1f}%"
        gpu_peak = f"{summary['peak_gpu_utilization']:.1f}%"
        gpu_avg = f"{summary['avg_gpu_utilization']:.1f}%"
        
        print(f"{ULTRASINGER_HEAD} ├─ VRAM atual: {green_highlighted(vram_current)} "
              f"(pico: {vram_peak}, média: {vram_avg})")
        print(f"{ULTRASINGER_HEAD} ├─ GPU atual: {green_highlighted(gpu_current)} "
              f"(pico: {gpu_peak}, média: {gpu_avg})")
        print(f"{ULTRASINGER_HEAD} ├─ Temperatura: {summary['current_temperature']}°C (pico: {summary['peak_temperature']}°C)")
        print(f"{ULTRASINGER_HEAD} ├─ Alertas: {summary['total_alerts']} total "
              f"({summary['critical_alerts']} críticos, {summary['warning_alerts']} avisos)")
        print(f"{ULTRASINGER_HEAD} └─ Componentes: {summary['components_tracked']} rastreados\n")
    
    def add_alert_callback(self, callback: Callable):
        """Add callback for alerts"""
        self.alert_callbacks.append(callback)
    
    def save_performance_log(self, filepath: str):
        """Save performance log to file"""
        try:
            log_data = {
                "summary": self.get_performance_summary(),
                "metrics_history": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "vram_used_mb": m.vram_used_mb,
                        "vram_total_mb": m.vram_total_mb,
                        "vram_usage_percent": m.vram_usage_percent,
                        "gpu_utilization_percent": m.gpu_utilization_percent,
                        "temperature_celsius": m.temperature_celsius,
                        "power_draw_watts": m.power_draw_watts
                    }
                    for m in self.metrics_history[-100:]  # Last 100 samples
                ],
                "alerts": [
                    {
                        "level": a.level,
                        "message": a.message,
                        "timestamp": a.timestamp.isoformat(),
                        "metric_name": a.metric_name,
                        "current_value": a.current_value,
                        "threshold_value": a.threshold_value
                    }
                    for a in self.alerts[-50:]  # Last 50 alerts
                ],
                "component_performance": {
                    name: {
                        "component_name": perf.component_name,
                        "start_time": perf.start_time.isoformat(),
                        "end_time": perf.end_time.isoformat() if perf.end_time else None,
                        "processing_time_seconds": perf.processing_time_seconds,
                        "peak_vram_mb": perf.peak_vram_mb,
                        "avg_vram_mb": perf.avg_vram_mb,
                        "peak_gpu_util": perf.peak_gpu_util,
                        "avg_gpu_util": perf.avg_gpu_util,
                        "samples_count": perf.samples_count
                    }
                    for name, perf in self.component_tracking.items()
                },
                "created_at": datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            print(f"{ULTRASINGER_HEAD} 💾 Log de performance salvo: {filepath}")
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} ❌ Erro ao salvar log: {str(e)}")

# Global instance
gpu_performance_monitor = GPUPerformanceMonitor()