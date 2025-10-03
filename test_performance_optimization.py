"""
Teste do sistema de otimização de performance do UltraSinger
"""

import time
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.performance_optimizer import (
    PerformanceOptimizer, 
    get_performance_optimizer,
    get_optimal_device,
    estimate_processing_time,
    DeviceType,
    ProcessingMode
)
from modules.logger import get_logger

logger = get_logger()

def test_system_detection():
    """Testar detecção de recursos do sistema"""
    print("\n=== Teste de Detecção de Sistema ===")
    
    optimizer = PerformanceOptimizer()
    resources = optimizer.system_resources
    
    print(f"✓ CPU detectada: {resources.cpu_count} cores")
    print(f"✓ Memória detectada: {resources.memory_total:.1f}GB total")
    print(f"✓ GPU disponível: {resources.gpu_available}")
    
    if resources.gpu_available:
        print(f"✓ GPU: {resources.gpu_name}")
        print(f"✓ VRAM: {resources.gpu_memory_total:.1f}GB")
    
    print(f"✓ Plataforma: {resources.platform}")
    
    assert resources.cpu_count > 0, "CPU count deve ser maior que 0"
    assert resources.memory_total > 0, "Memória total deve ser maior que 0"
    
    return True

def test_optimization_settings():
    """Testar criação de configurações de otimização"""
    print("\n=== Teste de Configurações de Otimização ===")
    
    optimizer = PerformanceOptimizer()
    settings = optimizer.optimization_settings
    
    print(f"✓ Dispositivo selecionado: {settings.device_type.value}")
    print(f"✓ Modo de processamento: {settings.processing_mode.value}")
    print(f"✓ Batch size: {settings.batch_size}")
    print(f"✓ Número de workers: {settings.num_workers}")
    print(f"✓ Limite de memória: {settings.memory_limit_gb:.1f}GB")
    print(f"✓ Mixed precision: {settings.enable_mixed_precision}")
    print(f"✓ Cache habilitado: {settings.cache_enabled}")
    
    assert settings.batch_size > 0, "Batch size deve ser maior que 0"
    assert settings.num_workers > 0, "Número de workers deve ser maior que 0"
    assert settings.memory_limit_gb > 0, "Limite de memória deve ser maior que 0"
    
    return True

def test_task_optimization():
    """Testar otimizações específicas por tarefa"""
    print("\n=== Teste de Otimização por Tarefa ===")
    
    optimizer = PerformanceOptimizer()
    
    # Teste para separação de áudio
    audio_opts = optimizer.optimize_for_task("audio_separation")
    print(f"✓ Separação de áudio: {audio_opts}")
    assert "device" in audio_opts, "Configuração de device deve estar presente"
    
    # Teste para transcrição
    transcription_opts = optimizer.optimize_for_task("transcription", model_size="small")
    print(f"✓ Transcrição: {transcription_opts}")
    assert "device" in transcription_opts, "Configuração de device deve estar presente"
    
    # Teste para detecção de pitch
    pitch_opts = optimizer.optimize_for_task("pitch_detection")
    print(f"✓ Detecção de pitch: {pitch_opts}")
    assert "device" in pitch_opts, "Configuração de device deve estar presente"
    
    # Teste para geração de partituras
    sheet_opts = optimizer.optimize_for_task("sheet_generation")
    print(f"✓ Geração de partituras: {sheet_opts}")
    assert "parallel_processing" in sheet_opts, "Configuração de processamento paralelo deve estar presente"
    
    return True

def test_device_detection():
    """Testar detecção de dispositivo ótimo"""
    print("\n=== Teste de Detecção de Dispositivo ===")
    
    # Teste sem forçar CPU
    optimal_device = get_optimal_device(force_cpu=False)
    print(f"✓ Dispositivo ótimo: {optimal_device}")
    assert optimal_device in ["cpu", "cuda", "mps"], f"Dispositivo inválido: {optimal_device}"
    
    # Teste forçando CPU
    cpu_device = get_optimal_device(force_cpu=True)
    print(f"✓ Dispositivo forçado CPU: {cpu_device}")
    assert cpu_device == "cpu", "Dispositivo forçado deve ser CPU"
    
    return True

def test_time_estimation():
    """Testar estimativa de tempo de processamento"""
    print("\n=== Teste de Estimativa de Tempo ===")
    
    # Teste para diferentes tarefas
    tasks = ["audio_separation", "transcription", "pitch_detection", "sheet_generation"]
    input_size = 10.0  # 10MB de áudio
    
    for task in tasks:
        estimated_time = estimate_processing_time(task, input_size)
        print(f"✓ {task}: ~{estimated_time:.1f}s para {input_size}MB")
        assert estimated_time > 0, f"Tempo estimado deve ser positivo para {task}"
    
    return True

def test_monitoring_system():
    """Testar sistema de monitoramento"""
    print("\n=== Teste de Sistema de Monitoramento ===")
    
    optimizer = PerformanceOptimizer()
    
    # Iniciar monitoramento
    optimizer.start_monitoring(interval=1.0)
    print("✓ Monitoramento iniciado")
    
    # Aguardar algumas medições
    time.sleep(3)
    
    # Verificar se métricas foram coletadas
    metrics = optimizer.performance_metrics
    assert len(metrics['cpu_utilization']) > 0, "Métricas de CPU devem ter sido coletadas"
    assert len(metrics['memory_usage']) > 0, "Métricas de memória devem ter sido coletadas"
    
    print(f"✓ Métricas coletadas: {len(metrics['cpu_utilization'])} medições")
    
    # Parar monitoramento
    optimizer.stop_monitoring()
    print("✓ Monitoramento parado")
    
    return True

def test_performance_report():
    """Testar geração de relatório de performance"""
    print("\n=== Teste de Relatório de Performance ===")
    
    optimizer = PerformanceOptimizer()
    
    # Iniciar monitoramento para coletar dados
    optimizer.start_monitoring(interval=0.5)
    time.sleep(2)
    optimizer.stop_monitoring()
    
    # Gerar relatório
    report = optimizer.get_performance_report()
    print("✓ Relatório gerado")
    
    assert "system_resources" in report, "Relatório deve conter recursos do sistema"
    assert "optimization_settings" in report, "Relatório deve conter configurações"
    assert "performance_metrics" in report, "Relatório deve conter métricas"
    
    # Verificar estrutura do relatório
    system_resources = report["system_resources"]
    assert "cpu_count" in system_resources, "Relatório deve conter contagem de CPU"
    assert "memory_total_gb" in system_resources, "Relatório deve conter memória total"
    
    print(f"✓ CPU: {system_resources['cpu_count']} cores")
    print(f"✓ Memória: {system_resources['memory_total_gb']:.1f}GB")
    print(f"✓ GPU: {system_resources['gpu_available']}")
    
    return True

def test_memory_cleanup():
    """Testar limpeza de memória"""
    print("\n=== Teste de Limpeza de Memória ===")
    
    optimizer = PerformanceOptimizer()
    
    # Executar limpeza
    optimizer.cleanup_memory()
    print("✓ Limpeza de memória executada")
    
    return True

def test_optimization_suggestions():
    """Testar sugestões de otimização"""
    print("\n=== Teste de Sugestões de Otimização ===")
    
    optimizer = PerformanceOptimizer()
    
    # Coletar alguns dados primeiro
    optimizer.start_monitoring(interval=0.5)
    time.sleep(2)
    optimizer.stop_monitoring()
    
    # Obter sugestões
    suggestions = optimizer.suggest_optimizations()
    print(f"✓ Sugestões geradas: {len(suggestions)}")
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    assert isinstance(suggestions, list), "Sugestões devem ser uma lista"
    assert len(suggestions) > 0, "Deve haver pelo menos uma sugestão"
    
    return True

def test_global_optimizer():
    """Testar instância global do otimizador"""
    print("\n=== Teste de Otimizador Global ===")
    
    # Obter primeira instância
    optimizer1 = get_performance_optimizer()
    
    # Obter segunda instância
    optimizer2 = get_performance_optimizer()
    
    # Devem ser a mesma instância
    assert optimizer1 is optimizer2, "Instâncias globais devem ser iguais"
    print("✓ Instância global funcionando corretamente")
    
    return True

def run_all_tests():
    """Executar todos os testes"""
    print("🚀 Iniciando testes do sistema de otimização de performance...")
    
    tests = [
        ("Detecção de Sistema", test_system_detection),
        ("Configurações de Otimização", test_optimization_settings),
        ("Otimização por Tarefa", test_task_optimization),
        ("Detecção de Dispositivo", test_device_detection),
        ("Estimativa de Tempo", test_time_estimation),
        ("Sistema de Monitoramento", test_monitoring_system),
        ("Relatório de Performance", test_performance_report),
        ("Limpeza de Memória", test_memory_cleanup),
        ("Sugestões de Otimização", test_optimization_suggestions),
        ("Otimizador Global", test_global_optimizer)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*50}")
            print(f"Executando: {test_name}")
            print('='*50)
            
            result = test_func()
            if result:
                print(f"✅ {test_name}: PASSOU")
                passed += 1
            else:
                print(f"❌ {test_name}: FALHOU")
                failed += 1
                
        except Exception as e:
            print(f"❌ {test_name}: ERRO - {str(e)}")
            failed += 1
    
    print(f"\n{'='*50}")
    print("RESUMO DOS TESTES")
    print('='*50)
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 Todos os testes passaram! Sistema de otimização funcionando perfeitamente.")
    else:
        print(f"\n⚠️  {failed} teste(s) falharam. Verifique os erros acima.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)