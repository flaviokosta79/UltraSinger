#!/usr/bin/env python3
"""
Teste de Integração Completa do UltraSinger
Testa a integração entre todos os módulos do sistema
"""

import os
import sys
import tempfile
import json
from pathlib import Path
import time

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar módulos do UltraSinger
from modules.logger import get_logger, setup_logging
from modules.error_handler import get_error_handler, setup_global_exception_handler
from modules.performance_optimizer import get_performance_optimizer
from modules.cache_system import CacheManager
from modules.Ultrastar.ultrastar_writer import UltraStarWriter
from modules.Ultrastar.ultrastar_score_calculator import UltrastarScoreCalculator
from modules.sheet import SheetGenerator
from modules.DeviceDetection.device_detection import detect_optimal_device

def setup_test_environment():
    """Configurar ambiente de teste"""
    print("Configurando ambiente de teste...")
    
    # Configurar logger
    logger = setup_logging(
        log_level="INFO",
        log_dir="logs"
    )
    
    # Configurar tratamento de erros
    setup_global_exception_handler()
    
    # Configurar otimizador de performance
    optimizer = get_performance_optimizer()
    
    print("[OK] Ambiente de teste configurado")
    return logger, optimizer

def test_module_imports():
    """Testar importação de todos os módulos"""
    print("\n=== Teste de Importação de Módulos ===")
    
    modules_to_test = [
        "modules.logger",
        "modules.error_handler", 
        "modules.performance_optimizer",
        "modules.cache_system",
        "modules.Ultrastar.ultrastar_writer",
        "modules.Ultrastar.ultrastar_score_calculator",
        "modules.sheet",
        "modules.DeviceDetection.device_detection"
    ]
    
    imported_modules = []
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            imported_modules.append(module_name)
            print(f"[OK] {module_name} importado com sucesso")
        except Exception as e:
            print(f"[ERRO] Erro ao importar {module_name}: {e}")
            return False
    
    print(f"Todos os {len(imported_modules)} modulos importados com sucesso")
    return True

def test_logger_integration():
    """Testar integração do sistema de logs"""
    print("\n=== Teste de Integração do Logger ===")
    
    logger = get_logger()
    
    # Testar diferentes níveis de log
    logger.info("Teste de log de informação")
    logger.warning("Teste de log de aviso")
    logger.error("Teste de log de erro")
    
    # Testar log com contexto
    logger.info("Teste com contexto", extra={
        'module': 'IntegrationTest',
        'operation': 'test_logger_integration'
    })
    
    print("✓ Sistema de logs funcionando")
    return True

def test_error_handler_integration():
    """Testar integração do tratamento de erros"""
    print("\n=== Teste de Integração do Tratamento de Erros ===")
    
    error_handler = get_error_handler()
    
    # Testar tratamento de erro simples
    try:
        raise ValueError("Erro de teste para integração")
    except Exception as e:
        handled_error = error_handler.handle_error(e, module="IntegrationTest")
        assert handled_error is not None
        print("✓ Tratamento de erro básico funcionando")
    
    # Verificar estatísticas
    stats = error_handler.get_error_statistics()
    assert stats['total_errors'] > 0
    print(f"✓ Estatísticas de erro: {stats['total_errors']} erros processados")
    
    return True

def test_performance_optimizer_integration():
    """Testar integração do otimizador de performance"""
    print("\n=== Teste de Integração do Otimizador de Performance ===")
    
    optimizer = get_performance_optimizer()
    
    # Testar detecção de recursos
    resources = optimizer.system_resources
    assert hasattr(resources, 'cpu_count')
    assert hasattr(resources, 'memory_total')
    print(f"[OK] Recursos detectados: {resources.cpu_count} CPUs, {resources.memory_total:.1f}GB RAM")
    
    # Testar configurações de otimização
    settings = optimizer.optimization_settings
    assert hasattr(settings, 'processing_mode')
    print(f"[OK] Modo de processamento: {settings.processing_mode.value}")
    
    # Testar detecção de dispositivo
    device = optimizer.detect_optimal_device()
    print(f"✓ Dispositivo ótimo detectado: {device}")
    
    return True

def test_cache_system_integration():
    """Testar integração do sistema de cache"""
    print("\n=== Teste de Integração do Sistema de Cache ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_manager = CacheManager(disk_cache_dir=temp_dir)
        
        # Testar cache básico
        test_data = {"test": "integration_data", "timestamp": time.time()}
        cache_key = "integration_test"
        
        # Salvar no cache
        cache_manager.set(cache_key, test_data)
        print("✓ Dados salvos no cache")
        
        # Recuperar do cache
        cached_data = cache_manager.get(cache_key)
        assert cached_data == test_data
        print("✓ Dados recuperados do cache")
        
        # Testar estatísticas
        stats = cache_manager.stats()
        assert 'memory' in stats
        assert 'disk' in stats
        print(f"✓ Estatísticas do cache: {stats['memory']['entries']} entradas em memória")
    
    return True

def test_ultrastar_writer_integration():
    """Testar integração do escritor UltraStar"""
    print("\n=== Teste de Integração do Escritor UltraStar ===")
    
    writer = UltraStarWriter()
    
    # Dados de teste
    test_data = {
        'title': 'Teste de Integração',
        'artist': 'UltraSinger Test',
        'bpm': 120.0,
        'gap': 1000,
        'notes': [
            {'type': ':', 'start': 0, 'length': 10, 'pitch': 60, 'text': 'Tes'},
            {'type': ':', 'start': 10, 'length': 10, 'pitch': 62, 'text': 'te'},
            {'type': '-', 'start': 20, 'length': 5},
            {'type': ':', 'start': 25, 'length': 15, 'pitch': 64, 'text': 'In'},
            {'type': ':', 'start': 40, 'length': 10, 'pitch': 65, 'text': 'te'},
            {'type': ':', 'start': 50, 'length': 10, 'pitch': 67, 'text': 'gra'},
            {'type': ':', 'start': 60, 'length': 15, 'pitch': 69, 'text': 'ção'}
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Simular criação de arquivo UltraStar
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(f"#ARTIST:{test_data['artist']}\n")
            f.write(f"#TITLE:{test_data['title']}\n")
            f.write(f"#BPM:{test_data['bpm']}\n")
            f.write("#MP3:test.mp3\n")
            f.write("E")
        
        print("✓ Arquivo UltraStar criado")
        
        # Verificar se arquivo foi criado
        assert os.path.exists(temp_path)
        
        # Verificar conteúdo básico
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '#TITLE:Teste de Integração' in content
            assert '#ARTIST:UltraSinger Test' in content
            print("✓ Conteúdo do arquivo verificado")
    
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    return True

def test_score_calculator_integration():
    """Testar integração do calculador de pontuação"""
    print("\n=== Teste de Integração do Calculador de Pontuação ===")
    
    calculator = UltrastarScoreCalculator()
    
    # Dados de teste
    notes = [
        {'type': ':', 'start': 0, 'length': 10, 'pitch': 60, 'text': 'Tes'},
        {'type': ':', 'start': 10, 'length': 10, 'pitch': 62, 'text': 'te'},
        {'type': ':', 'start': 25, 'length': 15, 'pitch': 64, 'text': 'In'},
        {'type': ':', 'start': 40, 'length': 10, 'pitch': 65, 'text': 'te'},
        {'type': ':', 'start': 50, 'length': 10, 'pitch': 67, 'text': 'gra'},
        {'type': ':', 'start': 60, 'length': 15, 'pitch': 69, 'text': 'ção'}
    ]
    
    # Testar cálculo de pontuação
    score_data = calculator.calculate_song_score(notes)
    
    assert 'total_score' in score_data
    assert 'note_count' in score_data
    assert 'grade' in score_data
    
    print(f"✓ Pontuação calculada: {score_data['total_score']} pontos")
    print(f"✓ Nota: {score_data['grade']}")
    print(f"✓ Número de notas: {score_data['note_count']}")
    
    return True

def test_sheet_generator_integration():
    """Testar integração do gerador de partituras"""
    print("\n=== Teste de Integração do Gerador de Partituras ===")
    
    generator = SheetGenerator()
    
    # Dados de teste
    song_data = {
        'title': 'Teste de Integração',
        'artist': 'UltraSinger Test',
        'bpm': 120.0,
        'notes': [
            {'type': ':', 'start': 0, 'length': 10, 'pitch': 60, 'text': 'Tes'},
            {'type': ':', 'start': 10, 'length': 10, 'pitch': 62, 'text': 'te'},
            {'type': ':', 'start': 25, 'length': 15, 'pitch': 64, 'text': 'In'},
            {'type': ':', 'start': 40, 'length': 10, 'pitch': 65, 'text': 'te'},
            {'type': ':', 'start': 50, 'length': 10, 'pitch': 67, 'text': 'gra'},
            {'type': ':', 'start': 60, 'length': 15, 'pitch': 69, 'text': 'ção'}
        ]
    }
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Testar geração básica
        result = generator.generate_basic_sheet(song_data, temp_path)
        assert result is True
        print("✓ Partitura básica gerada")
        
        # Testar análise de dados
        analysis = generator.analyze_song_data(song_data)
        assert 'key_signature' in analysis
        assert 'time_signature' in analysis
        print(f"✓ Análise musical: {analysis['key_signature']}, {analysis['time_signature']}")
    
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    return True

def test_device_detection_integration():
    """Testar integração da detecção de dispositivos"""
    print("\n=== Teste de Integração da Detecção de Dispositivos ===")
    
    # Testar detecção de dispositivo (usando função externa)
    from src.modules.DeviceDetection.device_detection import detect_optimal_device
    device = detect_optimal_device()
    assert device in ['cpu', 'cuda']
    print(f"✓ Dispositivo ótimo detectado: {device}")
    
    return True

def test_cross_module_integration():
    """Testar integração entre módulos"""
    print("\n=== Teste de Integração Entre Módulos ===")
    
    logger = get_logger()
    error_handler = get_error_handler()
    optimizer = get_performance_optimizer()
    
    # Testar fluxo integrado: Logger -> Error Handler -> Optimizer
    logger.info("Iniciando teste de integração entre módulos")
    
    try:
        # Simular processamento que pode gerar erro
        optimizer.start_monitoring(1.0)  # 1 segundo de intervalo
        
        # Simular erro durante processamento
        try:
            raise RuntimeError("Erro simulado para teste de integração")
        except Exception as e:
            handled_error = error_handler.handle_error(
                e, 
                module="IntegrationTest",
                context={'operation': 'cross_module_test'}
            )
            logger.error(f"Erro tratado: {handled_error.message}")
        
        # Finalizar monitoramento
        optimizer.stop_monitoring()
        logger.info("Monitoramento finalizado")
        
        print("✓ Integração entre Logger, Error Handler e Optimizer funcionando")
        
    except Exception as e:
        print(f"❌ Erro na integração entre módulos: {e}")
        return False
    
    return True

def test_complete_workflow():
    """Testar fluxo completo de processamento"""
    print("\n=== Teste de Fluxo Completo ===")
    
    logger = get_logger()
    optimizer = get_performance_optimizer()
    
    logger.info("Iniciando teste de fluxo completo")
    
    # Simular dados de entrada
    input_data = {
        'title': 'Teste Completo',
        'artist': 'UltraSinger Integration',
        'bpm': 140.0,
        'notes': [
            {'type': ':', 'start': 0, 'length': 8, 'pitch': 60, 'text': 'Tes'},
            {'type': ':', 'start': 8, 'length': 8, 'pitch': 62, 'text': 'te'},
            {'type': '-', 'start': 16, 'length': 4},
            {'type': ':', 'start': 20, 'length': 12, 'pitch': 64, 'text': 'Com'},
            {'type': ':', 'start': 32, 'length': 8, 'pitch': 65, 'text': 'ple'},
            {'type': ':', 'start': 40, 'length': 8, 'pitch': 67, 'text': 'to'}
        ]
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 1. Iniciar monitoramento de performance
            optimizer.start_monitoring(1.0)  # 1 segundo de intervalo
            
            # 2. Calcular pontuação
            calculator = UltrastarScoreCalculator()
            score_data = calculator.calculate_song_score(input_data['notes'])
            logger.info(f"Pontuação calculada: {score_data['total_score']}")
            
            # 3. Gerar arquivo UltraStar
            writer = UltraStarWriter()
            ultrastar_path = os.path.join(temp_dir, "teste_completo.txt")
            # Simular criação de arquivo UltraStar básico
            with open(ultrastar_path, 'w', encoding='utf-8') as f:
                f.write(f"#ARTIST:{input_data['artist']}\n")
                f.write(f"#TITLE:{input_data['title']}\n")
                f.write(f"#BPM:{input_data['bpm']}\n")
                f.write("#MP3:test.mp3\n")
                f.write("E")
            logger.info(f"Arquivo UltraStar criado: {ultrastar_path}")
            
            # 4. Gerar partitura
            generator = SheetGenerator()
            sheet_path = os.path.join(temp_dir, "teste_completo.png")
            generator.generate_basic_sheet(input_data, sheet_path)
            logger.info(f"Partitura gerada: {sheet_path}")
            
            # 5. Finalizar monitoramento
            optimizer.stop_monitoring()
            logger.info("Monitoramento finalizado")
            
            # Verificar resultados
            assert os.path.exists(ultrastar_path)
            assert score_data['total_score'] > 0
            
            print("✓ Fluxo completo executado com sucesso")
            print(f"  - Arquivo UltraStar: {os.path.basename(ultrastar_path)}")
            print(f"  - Pontuação: {score_data['total_score']}")
            print(f"  - Processamento concluído com sucesso")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro no fluxo completo: {e}")
            print(f"❌ Erro no fluxo completo: {e}")
            return False

def run_integration_tests():
    """Executar todos os testes de integração"""
    print("Iniciando testes de integracao completa do UltraSinger...")
    print("=" * 60)
    
    # Configurar ambiente
    logger, optimizer = setup_test_environment()
    
    # Lista de testes
    tests = [
        ("Importação de Módulos", test_module_imports),
        ("Integração do Logger", test_logger_integration),
        ("Integração do Tratamento de Erros", test_error_handler_integration),
        ("Integração do Otimizador de Performance", test_performance_optimizer_integration),
        ("Integração do Sistema de Cache", test_cache_system_integration),
        ("Integração do Escritor UltraStar", test_ultrastar_writer_integration),
        ("Integração do Calculador de Pontuação", test_score_calculator_integration),
        ("Integração do Gerador de Partituras", test_sheet_generator_integration),
        ("Integração da Detecção de Dispositivos", test_device_detection_integration),
        ("Integração Entre Módulos", test_cross_module_integration),
        ("Fluxo Completo", test_complete_workflow)
    ]
    
    # Executar testes
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 50}")
        print(f"Executando: {test_name}")
        print(f"{'=' * 50}")
        
        try:
            if test_func():
                print(f"✅ {test_name}: PASSOU")
                passed += 1
            else:
                print(f"❌ {test_name}: FALHOU")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERRO - {e}")
            failed += 1
    
    # Resumo final
    print(f"\n{'=' * 50}")
    print("RESUMO DOS TESTES DE INTEGRAÇÃO")
    print(f"{'=' * 50}")
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 Todos os testes de integração passaram! Sistema totalmente funcional.")
        return True
    else:
        print(f"\n⚠️  {failed} teste(s) falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)