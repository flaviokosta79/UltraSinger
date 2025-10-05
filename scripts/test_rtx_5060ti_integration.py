#!/usr/bin/env python3
"""
Script de teste para validar integração completa RTX 5060TI no UltraSinger
Testa todos os componentes: detecção, otimização, monitoramento e fallback
"""

import sys
import os
import time
import json
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from modules.DeviceDetection.rtx_5060ti_optimizer import RTX5060TIOptimizer
    from modules.DeviceDetection.gpu_performance_monitor import GPUPerformanceMonitor
    from modules.DeviceDetection.gpu_fallback_system import GPUFallbackSystem
    from modules.DeviceDetection.component_optimizer import ComponentOptimizer
    from modules.DeviceDetection.rtx_5060ti_interface import RTX5060TIInterface
    from Settings import Settings
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)


class RTX5060TIIntegrationTest:
    """Classe para testar integração completa RTX 5060TI"""
    
    def __init__(self):
        self.results = {
            "gpu_detection": False,
            "optimization": False,
            "monitoring": False,
            "fallback": False,
            "interface": False,
            "settings_integration": False,
            "performance_metrics": {},
            "errors": []
        }
        
    def print_header(self, title: str):
        """Imprime cabeçalho formatado"""
        print("\n" + "="*60)
        print(f"🧪 {title}")
        print("="*60)
    
    def print_test_result(self, test_name: str, success: bool, details: str = ""):
        """Imprime resultado do teste"""
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if details:
            print(f"   📝 {details}")
    
    def test_gpu_detection(self) -> bool:
        """Testa detecção da RTX 5060TI"""
        self.print_header("TESTE DE DETECÇÃO GPU")
        
        try:
            optimizer = RTX5060TIOptimizer()
            is_rtx_5060ti, gpu_config = optimizer.detect_rtx_5060ti()
            
            if gpu_config:
                self.print_test_result(
                    "Detecção RTX 5060TI", 
                    True, 
                    f"GPU: {gpu_config.gpu_name}, VRAM: {gpu_config.vram_total_gb}GB"
                )
                
                # Verificar se tem 16GB
                has_16gb = gpu_config.vram_total_gb >= 15
                self.print_test_result(
                    "Verificação 16GB VRAM", 
                    has_16gb, 
                    f"VRAM detectada: {gpu_config.vram_total_gb}GB"
                )
                
                # Verificar CUDA
                has_cuda = gpu_config.cuda_version != "Unknown"
                self.print_test_result(
                    "Detecção CUDA", 
                    has_cuda, 
                    f"CUDA: {gpu_config.cuda_version}"
                )
                
                # Verificar se é RTX 5060TI
                self.print_test_result(
                    "RTX 5060TI Específica", 
                    is_rtx_5060ti, 
                    f"RTX 5060TI: {is_rtx_5060ti}"
                )
                
                self.results["gpu_detection"] = True  # Passou se detectou qualquer GPU
                return True
            else:
                self.print_test_result("Detecção RTX 5060TI", False, "GPU não detectada")
                return False
                
        except Exception as e:
            self.results["errors"].append(f"GPU Detection: {str(e)}")
            self.print_test_result("Detecção RTX 5060TI", False, f"Erro: {e}")
            return False
    
    def test_optimization(self) -> bool:
        """Testa sistema de otimização"""
        self.print_header("TESTE DE OTIMIZAÇÃO")
        
        try:
            component_optimizer = ComponentOptimizer()
            
            # Testar cada modo de otimização
            modes = ["conservative", "balanced", "aggressive"]
            all_passed = True
            
            for mode in modes:
                try:
                    config = component_optimizer.get_optimized_config(mode)
                    
                    # Verificar se tem configurações para todos os componentes
                    has_whisper = hasattr(config, 'whisper') and config.whisper is not None
                    has_demucs = hasattr(config, 'demucs') and config.demucs is not None
                    has_crepe = hasattr(config, 'crepe') and config.crepe is not None
                    
                    mode_passed = has_whisper and has_demucs and has_crepe
                    self.print_test_result(
                        f"Otimização modo {mode}", 
                        mode_passed,
                        f"Whisper: {has_whisper}, Demucs: {has_demucs}, CREPE: {has_crepe}"
                    )
                    
                    if not mode_passed:
                        all_passed = False
                        
                except Exception as e:
                    self.print_test_result(f"Otimização modo {mode}", False, f"Erro: {e}")
                    all_passed = False
            
            # Testar cálculo de VRAM
            try:
                vram_usage = component_optimizer.calculate_total_vram_usage("balanced")
                vram_valid = 0 < vram_usage < 16
                self.print_test_result(
                    "Cálculo VRAM", 
                    vram_valid, 
                    f"Uso estimado: {vram_usage:.1f}GB"
                )
                all_passed = all_passed and vram_valid
            except Exception as e:
                self.print_test_result("Cálculo VRAM", False, f"Erro: {e}")
                all_passed = False
            
            self.results["optimization"] = all_passed
            return all_passed
            
        except Exception as e:
            self.results["errors"].append(f"Optimization: {str(e)}")
            self.print_test_result("Sistema de Otimização", False, f"Erro: {e}")
            return False
    
    def test_monitoring(self) -> bool:
        """Testa sistema de monitoramento"""
        self.print_header("TESTE DE MONITORAMENTO")
        
        try:
            monitor = GPUPerformanceMonitor()
            
            # Testar inicialização
            monitor.start_monitoring()
            self.print_test_result("Inicialização Monitor", True, "Monitor iniciado")
            
            # Aguardar algumas métricas
            time.sleep(2)
            
            # Testar coleta de métricas
            if hasattr(monitor, 'get_current_metrics'):
                metrics = monitor.get_current_metrics()
                if metrics:
                    self.print_test_result(
                        "Coleta de Métricas", 
                        True, 
                        f"Temp: {metrics.temperature}°C, Uso: {metrics.utilization}%"
                    )
                    
                    # Salvar métricas para relatório
                    self.results["performance_metrics"] = {
                        "temperature": metrics.temperature,
                        "utilization": metrics.utilization,
                        "memory_used_gb": metrics.memory_used_gb,
                        "memory_total_gb": metrics.memory_total_gb
                    }
                    
                    monitoring_passed = True
                else:
                    self.print_test_result("Coleta de Métricas", False, "Métricas não disponíveis")
                    monitoring_passed = False
            else:
                self.print_test_result("Coleta de Métricas", False, "Método não implementado")
                monitoring_passed = False
            
            # Parar monitoramento
            monitor.stop_monitoring()
            self.print_test_result("Parada Monitor", True, "Monitor parado")
            
            self.results["monitoring"] = monitoring_passed
            return monitoring_passed
            
        except Exception as e:
            self.results["errors"].append(f"Monitoring: {str(e)}")
            self.print_test_result("Sistema de Monitoramento", False, f"Erro: {e}")
            return False
    
    def test_fallback_system(self) -> bool:
        """Testa sistema de fallback"""
        self.print_header("TESTE DE FALLBACK")
        
        try:
            fallback = GPUFallbackSystem()
            
            # Testar inicialização
            fallback.initialize()
            self.print_test_result("Inicialização Fallback", True, "Sistema inicializado")
            
            # Testar verificação de saúde
            health_status = fallback.check_system_health()
            has_health_data = isinstance(health_status, dict) and len(health_status) > 0
            self.print_test_result(
                "Verificação Saúde", 
                has_health_data, 
                f"Componentes monitorados: {health_status.get('total_components', 0)}"
            )
            
            # Testar configurações de fallback
            has_configs = hasattr(fallback, 'component_configs') and fallback.component_configs
            self.print_test_result(
                "Configurações Fallback", 
                has_configs, 
                "Configurações carregadas" if has_configs else "Configurações não encontradas"
            )
            
            # Testar status do sistema
            try:
                fallback.print_system_status()
                self.print_test_result("Status do Sistema", True, "Status exibido")
            except Exception as e:
                self.print_test_result("Status do Sistema", False, f"Erro: {e}")
            
            self.results["fallback"] = has_health_data and has_configs
            return self.results["fallback"]
            
        except Exception as e:
            self.results["errors"].append(f"Fallback: {str(e)}")
            self.print_test_result("Sistema de Fallback", False, f"Erro: {e}")
            return False
    
    def test_interface(self) -> bool:
        """Testa interface interativa"""
        self.print_header("TESTE DE INTERFACE")
        
        try:
            interface = RTX5060TIInterface()
            
            # Testar carregamento de presets
            has_presets = len(interface.presets) > 0
            self.print_test_result(
                "Carregamento Presets", 
                has_presets, 
                f"{len(interface.presets)} presets carregados"
            )
            
            # Testar aplicação de preset
            if has_presets:
                preset_applied = interface.apply_preset("balanced")
                self.print_test_result(
                    "Aplicação Preset", 
                    preset_applied, 
                    "Preset 'balanced' aplicado"
                )
            else:
                preset_applied = False
                self.print_test_result("Aplicação Preset", False, "Nenhum preset disponível")
            
            self.results["interface"] = has_presets and preset_applied
            return self.results["interface"]
            
        except Exception as e:
            self.results["errors"].append(f"Interface: {str(e)}")
            self.print_test_result("Interface Interativa", False, f"Erro: {e}")
            return False
    
    def test_settings_integration(self) -> bool:
        """Testa integração com Settings"""
        self.print_header("TESTE DE INTEGRAÇÃO SETTINGS")
        
        try:
            settings = Settings()
            
            # Verificar se as novas configurações RTX existem
            rtx_settings = [
                'rtx_5060ti_detected',
                'rtx_5060ti_optimization_mode',
                'rtx_5060ti_auto_optimize',
                'rtx_5060ti_monitor_performance',
                'rtx_5060ti_fallback_enabled',
                'rtx_5060ti_vram_limit_gb',
                'rtx_5060ti_config'
            ]
            
            missing_settings = []
            for setting in rtx_settings:
                if not hasattr(settings, setting):
                    missing_settings.append(setting)
            
            if not missing_settings:
                self.print_test_result(
                    "Configurações RTX", 
                    True, 
                    f"Todas as {len(rtx_settings)} configurações encontradas"
                )
                
                # Testar valores padrão
                default_values_ok = (
                    settings.rtx_5060ti_auto_optimize == True and
                    settings.rtx_5060ti_optimization_mode == "balanced" and
                    settings.rtx_5060ti_vram_limit_gb == 14.0
                )
                
                self.print_test_result(
                    "Valores Padrão", 
                    default_values_ok, 
                    "Valores padrão corretos"
                )
                
                settings_passed = default_values_ok
            else:
                self.print_test_result(
                    "Configurações RTX", 
                    False, 
                    f"Configurações faltando: {', '.join(missing_settings)}"
                )
                settings_passed = False
            
            self.results["settings_integration"] = settings_passed
            return settings_passed
            
        except Exception as e:
            self.results["errors"].append(f"Settings: {str(e)}")
            self.print_test_result("Integração Settings", False, f"Erro: {e}")
            return False
    
    def generate_report(self) -> None:
        """Gera relatório final dos testes"""
        self.print_header("RELATÓRIO FINAL")
        
        total_tests = len([k for k in self.results.keys() if k not in ['performance_metrics', 'errors']])
        passed_tests = sum([1 for k, v in self.results.items() if k not in ['performance_metrics', 'errors'] and v])
        
        print(f"📊 Testes Executados: {total_tests}")
        print(f"✅ Testes Aprovados: {passed_tests}")
        print(f"❌ Testes Falharam: {total_tests - passed_tests}")
        print(f"📈 Taxa de Sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.results["performance_metrics"]:
            print("\n📊 MÉTRICAS DE PERFORMANCE:")
            metrics = self.results["performance_metrics"]
            print(f"   🌡️  Temperatura: {metrics.get('temperature', 'N/A')}°C")
            print(f"   ⚡ Utilização: {metrics.get('utilization', 'N/A')}%")
            print(f"   💾 VRAM: {metrics.get('memory_used_gb', 'N/A')}/{metrics.get('memory_total_gb', 'N/A')} GB")
        
        if self.results["errors"]:
            print("\n❌ ERROS ENCONTRADOS:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        # Salvar relatório em arquivo
        report_path = "rtx_5060ti_test_report.json"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Relatório salvo em: {report_path}")
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")
        
        # Conclusão
        if passed_tests == total_tests:
            print("\n🎉 INTEGRAÇÃO RTX 5060TI COMPLETA E FUNCIONAL!")
        elif passed_tests >= total_tests * 0.8:
            print("\n⚠️  INTEGRAÇÃO RTX 5060TI PARCIALMENTE FUNCIONAL")
        else:
            print("\n❌ INTEGRAÇÃO RTX 5060TI PRECISA DE CORREÇÕES")
    
    def run_all_tests(self) -> None:
        """Executa todos os testes"""
        print("🚀 INICIANDO TESTES DE INTEGRAÇÃO RTX 5060TI")
        print("="*60)
        
        # Executar todos os testes
        self.test_gpu_detection()
        self.test_optimization()
        self.test_monitoring()
        self.test_fallback_system()
        self.test_interface()
        self.test_settings_integration()
        
        # Gerar relatório final
        self.generate_report()


def main():
    """Função principal"""
    print("🎮 TESTE DE INTEGRAÇÃO RTX 5060TI - ULTRASINGER")
    print("="*60)
    print("Este script testa todos os componentes da integração RTX 5060TI")
    print("Certifique-se de que sua RTX 5060TI está conectada e drivers atualizados")
    print("="*60)
    
    # Aguardar confirmação do usuário
    try:
        input("Pressione Enter para iniciar os testes ou Ctrl+C para cancelar...")
    except KeyboardInterrupt:
        print("\n👋 Testes cancelados pelo usuário")
        return
    
    # Executar testes
    tester = RTX5060TIIntegrationTest()
    tester.run_all_tests()


if __name__ == "__main__":
    main()