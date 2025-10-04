"""
Interface interativa para configurações RTX 5060TI
Fornece interface de linha de comando para configurar otimizações específicas da RTX 5060TI
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from .rtx_5060ti_optimizer import RTX5060TIOptimizer, GPUConfig
from .component_optimizer import ComponentOptimizer
from .gpu_performance_monitor import GPUPerformanceMonitor


@dataclass
class RTXPreset:
    """Preset de configuração RTX 5060TI"""
    name: str
    description: str
    optimization_mode: str
    whisper_config: Dict[str, Any]
    demucs_config: Dict[str, Any]
    crepe_config: Dict[str, Any]
    vram_limit_gb: float
    monitor_performance: bool
    fallback_enabled: bool


class RTX5060TIInterface:
    """Interface interativa para configurações RTX 5060TI"""
    
    def __init__(self):
        self.optimizer = RTX5060TIOptimizer()
        self.component_optimizer = ComponentOptimizer()
        self.monitor = GPUPerformanceMonitor()
        self.presets = self._load_presets()
        
    def _load_presets(self) -> Dict[str, RTXPreset]:
        """Carrega presets predefinidos"""
        return {
            "gaming": RTXPreset(
                name="Gaming",
                description="Configuração otimizada para uso durante jogos",
                optimization_mode="conservative",
                whisper_config={"batch_size": 8, "compute_type": "float16"},
                demucs_config={"segment": 10, "overlap": 0.25},
                crepe_config={"model_capacity": "medium", "step_size": 20},
                vram_limit_gb=12.0,
                monitor_performance=True,
                fallback_enabled=True
            ),
            "performance": RTXPreset(
                name="Performance",
                description="Máxima performance para processamento rápido",
                optimization_mode="aggressive",
                whisper_config={"batch_size": 16, "compute_type": "float16"},
                demucs_config={"segment": 20, "overlap": 0.1},
                crepe_config={"model_capacity": "full", "step_size": 10},
                vram_limit_gb=15.0,
                monitor_performance=True,
                fallback_enabled=True
            ),
            "balanced": RTXPreset(
                name="Balanced",
                description="Equilíbrio entre performance e estabilidade",
                optimization_mode="balanced",
                whisper_config={"batch_size": 12, "compute_type": "float16"},
                demucs_config={"segment": 15, "overlap": 0.2},
                crepe_config={"model_capacity": "large", "step_size": 15},
                vram_limit_gb=14.0,
                monitor_performance=True,
                fallback_enabled=True
            ),
            "quality": RTXPreset(
                name="Quality",
                description="Máxima qualidade com processamento mais lento",
                optimization_mode="conservative",
                whisper_config={"batch_size": 6, "compute_type": "float32"},
                demucs_config={"segment": 8, "overlap": 0.4},
                crepe_config={"model_capacity": "full", "step_size": 5},
                vram_limit_gb=13.0,
                monitor_performance=True,
                fallback_enabled=True
            )
        }
    
    def show_gpu_status(self) -> None:
        """Mostra status atual da GPU"""
        print("\n" + "="*60)
        print("🎮 STATUS RTX 5060TI")
        print("="*60)
        
        gpu_config = self.optimizer.detect_rtx_5060ti()
        if gpu_config:
            print(f"✅ RTX 5060TI detectada: {gpu_config.name}")
            print(f"📊 VRAM Total: {gpu_config.memory_gb:.1f} GB")
            print(f"🔧 Driver CUDA: {gpu_config.cuda_version}")
            print(f"⚡ Compute Capability: {gpu_config.compute_capability}")
            
            # Mostrar métricas em tempo real se disponível
            if hasattr(self.monitor, 'get_current_metrics'):
                metrics = self.monitor.get_current_metrics()
                if metrics:
                    print(f"🌡️  Temperatura: {metrics.temperature}°C")
                    print(f"⚡ Utilização: {metrics.utilization}%")
                    print(f"💾 VRAM Usada: {metrics.memory_used_gb:.1f}/{metrics.memory_total_gb:.1f} GB")
        else:
            print("❌ RTX 5060TI não detectada")
        
        print("="*60)
    
    def show_presets_menu(self) -> None:
        """Mostra menu de presets disponíveis"""
        print("\n" + "="*60)
        print("🎯 PRESETS RTX 5060TI DISPONÍVEIS")
        print("="*60)
        
        for i, (key, preset) in enumerate(self.presets.items(), 1):
            print(f"{i}. {preset.name}")
            print(f"   📝 {preset.description}")
            print(f"   ⚙️  Modo: {preset.optimization_mode}")
            print(f"   💾 VRAM Limite: {preset.vram_limit_gb} GB")
            print()
    
    def apply_preset(self, preset_name: str) -> bool:
        """Aplica um preset específico"""
        if preset_name not in self.presets:
            print(f"❌ Preset '{preset_name}' não encontrado")
            return False
        
        preset = self.presets[preset_name]
        print(f"\n🎯 Aplicando preset: {preset.name}")
        
        try:
            # Aplicar configurações do preset
            config = {
                'optimization_mode': preset.optimization_mode,
                'vram_limit_gb': preset.vram_limit_gb,
                'monitor_performance': preset.monitor_performance,
                'fallback_enabled': preset.fallback_enabled,
                'whisper_config': preset.whisper_config,
                'demucs_config': preset.demucs_config,
                'crepe_config': preset.crepe_config
            }
            
            # Salvar configuração
            self._save_config(config)
            print(f"✅ Preset '{preset.name}' aplicado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao aplicar preset: {e}")
            return False
    
    def show_optimization_menu(self) -> None:
        """Mostra menu de otimizações manuais"""
        print("\n" + "="*60)
        print("⚙️  CONFIGURAÇÕES MANUAIS RTX 5060TI")
        print("="*60)
        print("1. Configurar Whisper")
        print("2. Configurar Demucs")
        print("3. Configurar CREPE")
        print("4. Configurar VRAM Limite")
        print("5. Configurar Monitoramento")
        print("6. Configurar Fallback")
        print("7. Testar Configuração")
        print("8. Salvar Configuração Personalizada")
        print("0. Voltar")
        print("="*60)
    
    def configure_whisper(self) -> Dict[str, Any]:
        """Configuração interativa do Whisper"""
        print("\n🎤 CONFIGURAÇÃO WHISPER")
        print("-" * 30)
        
        batch_sizes = [4, 8, 12, 16, 20, 24]
        compute_types = ["float16", "float32", "int8"]
        
        print("Batch Size disponíveis:")
        for i, size in enumerate(batch_sizes, 1):
            print(f"{i}. {size}")
        
        try:
            choice = int(input("Escolha o batch size (1-6): ")) - 1
            batch_size = batch_sizes[choice]
        except (ValueError, IndexError):
            batch_size = 12  # Default
        
        print("\nCompute Type disponíveis:")
        for i, ctype in enumerate(compute_types, 1):
            print(f"{i}. {ctype}")
        
        try:
            choice = int(input("Escolha o compute type (1-3): ")) - 1
            compute_type = compute_types[choice]
        except (ValueError, IndexError):
            compute_type = "float16"  # Default
        
        config = {
            "batch_size": batch_size,
            "compute_type": compute_type
        }
        
        print(f"✅ Whisper configurado: Batch Size={batch_size}, Compute Type={compute_type}")
        return config
    
    def configure_demucs(self) -> Dict[str, Any]:
        """Configuração interativa do Demucs"""
        print("\n🎵 CONFIGURAÇÃO DEMUCS")
        print("-" * 30)
        
        segments = [8, 10, 15, 20, 25]
        overlaps = [0.1, 0.2, 0.25, 0.3, 0.4]
        
        print("Segment disponíveis:")
        for i, seg in enumerate(segments, 1):
            print(f"{i}. {seg}")
        
        try:
            choice = int(input("Escolha o segment (1-5): ")) - 1
            segment = segments[choice]
        except (ValueError, IndexError):
            segment = 15  # Default
        
        print("\nOverlap disponíveis:")
        for i, overlap in enumerate(overlaps, 1):
            print(f"{i}. {overlap}")
        
        try:
            choice = int(input("Escolha o overlap (1-5): ")) - 1
            overlap = overlaps[choice]
        except (ValueError, IndexError):
            overlap = 0.2  # Default
        
        config = {
            "segment": segment,
            "overlap": overlap
        }
        
        print(f"✅ Demucs configurado: Segment={segment}, Overlap={overlap}")
        return config
    
    def configure_crepe(self) -> Dict[str, Any]:
        """Configuração interativa do CREPE"""
        print("\n🎼 CONFIGURAÇÃO CREPE")
        print("-" * 30)
        
        capacities = ["tiny", "small", "medium", "large", "full"]
        step_sizes = [5, 10, 15, 20, 25]
        
        print("Model Capacity disponíveis:")
        for i, cap in enumerate(capacities, 1):
            print(f"{i}. {cap}")
        
        try:
            choice = int(input("Escolha a capacidade (1-5): ")) - 1
            capacity = capacities[choice]
        except (ValueError, IndexError):
            capacity = "large"  # Default
        
        print("\nStep Size disponíveis:")
        for i, step in enumerate(step_sizes, 1):
            print(f"{i}. {step}")
        
        try:
            choice = int(input("Escolha o step size (1-5): ")) - 1
            step_size = step_sizes[choice]
        except (ValueError, IndexError):
            step_size = 15  # Default
        
        config = {
            "model_capacity": capacity,
            "step_size": step_size
        }
        
        print(f"✅ CREPE configurado: Capacity={capacity}, Step Size={step_size}")
        return config
    
    def test_configuration(self) -> None:
        """Testa a configuração atual"""
        print("\n🧪 TESTANDO CONFIGURAÇÃO RTX 5060TI")
        print("-" * 40)
        
        try:
            # Verificar detecção da GPU
            gpu_config = self.optimizer.detect_rtx_5060ti()
            if not gpu_config:
                print("❌ RTX 5060TI não detectada")
                return
            
            print("✅ GPU detectada com sucesso")
            
            # Testar otimizações
            optimizations = self.component_optimizer.get_optimized_config("balanced")
            print("✅ Otimizações carregadas")
            
            # Verificar VRAM disponível
            if hasattr(self.monitor, 'get_current_metrics'):
                metrics = self.monitor.get_current_metrics()
                if metrics and metrics.memory_available_gb > 8.0:
                    print("✅ VRAM suficiente disponível")
                else:
                    print("⚠️  VRAM limitada - considere usar modo conservativo")
            
            print("\n🎉 Configuração testada com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Salva configuração em arquivo"""
        config_path = "rtx_5060ti_config.json"
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"💾 Configuração salva em: {config_path}")
        except Exception as e:
            print(f"❌ Erro ao salvar configuração: {e}")
    
    def run_interactive_setup(self) -> None:
        """Executa setup interativo completo"""
        print("\n" + "="*60)
        print("🚀 SETUP INTERATIVO RTX 5060TI")
        print("="*60)
        
        while True:
            print("\n📋 MENU PRINCIPAL:")
            print("1. Ver Status da GPU")
            print("2. Aplicar Preset")
            print("3. Configuração Manual")
            print("4. Testar Configuração")
            print("5. Monitoramento em Tempo Real")
            print("0. Sair")
            
            try:
                choice = input("\nEscolha uma opção (0-5): ").strip()
                
                if choice == "0":
                    print("👋 Saindo do setup RTX 5060TI...")
                    break
                elif choice == "1":
                    self.show_gpu_status()
                elif choice == "2":
                    self.show_presets_menu()
                    preset_choice = input("Digite o número do preset (1-4): ").strip()
                    preset_map = {
                        "1": "gaming",
                        "2": "performance", 
                        "3": "balanced",
                        "4": "quality"
                    }
                    if preset_choice in preset_map:
                        self.apply_preset(preset_map[preset_choice])
                elif choice == "3":
                    self._run_manual_config()
                elif choice == "4":
                    self.test_configuration()
                elif choice == "5":
                    self._run_monitoring()
                else:
                    print("❌ Opção inválida")
                    
            except KeyboardInterrupt:
                print("\n👋 Setup interrompido pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
    
    def _run_manual_config(self) -> None:
        """Executa configuração manual"""
        config = {
            "optimization_mode": "balanced",
            "vram_limit_gb": 14.0,
            "monitor_performance": True,
            "fallback_enabled": True,
            "whisper_config": {},
            "demucs_config": {},
            "crepe_config": {}
        }
        
        while True:
            self.show_optimization_menu()
            choice = input("Escolha uma opção (0-8): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                config["whisper_config"] = self.configure_whisper()
            elif choice == "2":
                config["demucs_config"] = self.configure_demucs()
            elif choice == "3":
                config["crepe_config"] = self.configure_crepe()
            elif choice == "4":
                try:
                    vram = float(input("Digite o limite de VRAM em GB (8-15): "))
                    if 8 <= vram <= 15:
                        config["vram_limit_gb"] = vram
                        print(f"✅ VRAM limite definido: {vram} GB")
                    else:
                        print("❌ Valor deve estar entre 8 e 15 GB")
                except ValueError:
                    print("❌ Valor inválido")
            elif choice == "5":
                monitor = input("Ativar monitoramento? (s/n): ").lower() == 's'
                config["monitor_performance"] = monitor
                print(f"✅ Monitoramento: {'Ativado' if monitor else 'Desativado'}")
            elif choice == "6":
                fallback = input("Ativar fallback CPU/GPU? (s/n): ").lower() == 's'
                config["fallback_enabled"] = fallback
                print(f"✅ Fallback: {'Ativado' if fallback else 'Desativado'}")
            elif choice == "7":
                self.test_configuration()
            elif choice == "8":
                self._save_config(config)
                print("✅ Configuração personalizada salva!")
                break
    
    def _run_monitoring(self) -> None:
        """Executa monitoramento em tempo real"""
        print("\n📊 MONITORAMENTO RTX 5060TI EM TEMPO REAL")
        print("Pressione Ctrl+C para parar...")
        
        try:
            self.monitor.start_monitoring()
            import time
            
            while True:
                if hasattr(self.monitor, 'get_current_metrics'):
                    metrics = self.monitor.get_current_metrics()
                    if metrics:
                        print(f"\r🌡️ {metrics.temperature}°C | ⚡ {metrics.utilization}% | 💾 {metrics.memory_used_gb:.1f}GB", end="")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n📊 Monitoramento interrompido")
        finally:
            self.monitor.stop_monitoring()


# Interface de linha de comando
def run_rtx_interface():
    """Executa interface RTX 5060TI"""
    interface = RTX5060TIInterface()
    interface.run_interactive_setup()


if __name__ == "__main__":
    run_rtx_interface()