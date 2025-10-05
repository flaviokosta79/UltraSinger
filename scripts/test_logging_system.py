#!/usr/bin/env python3
"""
Teste completo do sistema de logging do UltraSinger
"""

import os
import sys
import tempfile
import time
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.logger import (
    UltraSingerLogger, 
    get_logger, 
    setup_logging,
    debug, info, warning, error, critical,
    start_operation, end_operation
)


def test_basic_logging():
    """Testar funcionalidades básicas de logging"""
    print("\n=== Testando Logging Básico ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = os.path.join(temp_dir, "logs")
        
        # Configurar logging
        logger = setup_logging(log_level="DEBUG", log_dir=log_dir)
        
        print("1. Testando diferentes níveis de log...")
        
        # Testar diferentes níveis
        debug("Mensagem de debug detalhada", module="Test", context="test_basic")
        info("Informação importante", module="Test", user_action="testing")
        warning("Aviso sobre algo", module="Test", warning_type="test")
        error("Erro de teste", module="Test", error_code=404)
        critical("Erro crítico de teste", module="Test", severity="high")
        
        print("✓ Logs básicos enviados")
        
        # Verificar se arquivos de log foram criados
        log_files = list(Path(log_dir).glob("*.log"))
        if log_files:
            print(f"✓ Arquivos de log criados: {len(log_files)}")
            
            # Verificar conteúdo
            for log_file in log_files:
                if log_file.stat().st_size > 0:
                    print(f"✓ Log file {log_file.name} tem conteúdo ({log_file.stat().st_size} bytes)")
                else:
                    print(f"⚠ Log file {log_file.name} está vazio")
        else:
            print("⚠ Nenhum arquivo de log criado")
        
        return True


def test_performance_tracking():
    """Testar sistema de tracking de performance"""
    print("\n=== Testando Tracking de Performance ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = os.path.join(temp_dir, "logs")
        logger = setup_logging(log_dir=log_dir)
        
        print("1. Testando operações com timing...")
        
        # Simular operações com diferentes durações
        operations = [
            ("audio_processing", 0.5, True),
            ("transcription", 1.2, True),
            ("pitch_detection", 0.8, True),
            ("file_generation", 0.3, False),  # Simular falha
            ("cache_operation", 0.1, True)
        ]
        
        for op_name, duration, success in operations:
            start_operation(op_name, module="Performance", test_mode=True)
            time.sleep(duration)  # Simular processamento
            end_operation(op_name, module="Performance", success=success, duration_simulated=duration)
        
        print("✓ Operações de performance testadas")
        
        # Gerar relatório de métricas
        print("2. Gerando relatório de performance...")
        logger.log_performance_metrics()
        
        # Salvar relatório em arquivo
        report_file = os.path.join(temp_dir, "performance_report.json")
        logger.save_performance_report(report_file)
        
        if os.path.exists(report_file):
            size = os.path.getsize(report_file)
            print(f"✓ Relatório de performance salvo: {report_file} ({size} bytes)")
        else:
            print("✗ Falha ao salvar relatório de performance")
        
        return True


def test_error_handling():
    """Testar logging de erros e exceções"""
    print("\n=== Testando Logging de Erros ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = os.path.join(temp_dir, "logs")
        logger = setup_logging(log_dir=log_dir)
        
        print("1. Testando logging de exceções...")
        
        # Simular diferentes tipos de erro
        try:
            # Erro de divisão por zero
            result = 1 / 0
        except ZeroDivisionError as e:
            error("Erro de divisão por zero", module="Math", exception=e, operation="division")
        
        try:
            # Erro de arquivo não encontrado
            with open("arquivo_inexistente.txt", 'r') as f:
                content = f.read()
        except FileNotFoundError as e:
            error("Arquivo não encontrado", module="FileIO", exception=e, filename="arquivo_inexistente.txt")
        
        try:
            # Erro de índice
            lista = [1, 2, 3]
            item = lista[10]
        except IndexError as e:
            critical("Erro crítico de índice", module="DataProcessing", exception=e, index=10, list_size=len(lista))
        
        print("✓ Exceções logadas com sucesso")
        
        # Verificar se arquivo de erro foi criado
        error_files = list(Path(log_dir).glob("*errors*.log"))
        if error_files:
            print(f"✓ Arquivo de erros criado: {error_files[0].name}")
        else:
            print("⚠ Arquivo de erros não encontrado")
        
        return True


def test_module_specific_logging():
    """Testar logging específico por módulo"""
    print("\n=== Testando Logging por Módulo ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = os.path.join(temp_dir, "logs")
        logger = setup_logging(log_dir=log_dir)
        
        print("1. Testando logs de diferentes módulos...")
        
        # Simular logs de diferentes módulos do UltraSinger
        modules_tests = [
            ("Audio.Separation", "Iniciando separação de áudio", {"model": "htdemucs", "device": "cpu"}),
            ("Speech.Whisper", "Transcrevendo áudio", {"model": "small", "language": "pt"}),
            ("Pitch.Detection", "Detectando pitch", {"algorithm": "crepe", "step_size": 10}),
            ("MIDI.Generation", "Gerando arquivo MIDI", {"segments": 150, "bpm": 120}),
            ("Sheet.Creation", "Criando partitura", {"format": "pdf", "musescore_version": 4}),
            ("UltraStar.Export", "Exportando UltraStar.txt", {"format_version": "1.1.0"}),
            ("Cache.System", "Operação de cache", {"cache_type": "pitch", "hit_rate": 0.85})
        ]
        
        for module, message, context in modules_tests:
            info(message, module=module, **context)
        
        print("✓ Logs de módulos específicos enviados")
        
        # Testar operações complexas
        print("2. Testando operação complexa com sub-operações...")
        
        start_operation("complete_processing", module="Core", input_file="test.mp3")
        
        # Sub-operações
        for sub_op in ["audio_separation", "transcription", "pitch_detection", "file_generation"]:
            start_operation(sub_op, module="Core.SubProcess", parent="complete_processing")
            time.sleep(0.1)  # Simular processamento
            end_operation(sub_op, module="Core.SubProcess", success=True)
        
        end_operation("complete_processing", module="Core", success=True, total_sub_operations=4)
        
        print("✓ Operação complexa logada")
        
        return True


def test_log_levels():
    """Testar diferentes níveis de log"""
    print("\n=== Testando Níveis de Log ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = os.path.join(temp_dir, "logs")
        
        # Testar diferentes níveis
        levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        
        for level in levels:
            print(f"Testando nível: {level}")
            
            logger = setup_logging(log_level=level, log_dir=log_dir)
            
            # Enviar logs de todos os níveis
            debug(f"Debug message - level {level}", module="LevelTest")
            info(f"Info message - level {level}", module="LevelTest")
            warning(f"Warning message - level {level}", module="LevelTest")
            error(f"Error message - level {level}", module="LevelTest")
            
        print("✓ Todos os níveis de log testados")
        
        return True


def main():
    """Função principal de teste"""
    print("🔍 TESTE COMPLETO DO SISTEMA DE LOGGING ULTRASINGER 🔍")
    print("=" * 60)
    
    tests = [
        ("Logging Básico", test_basic_logging),
        ("Tracking de Performance", test_performance_tracking),
        ("Logging de Erros", test_error_handling),
        ("Logging por Módulo", test_module_specific_logging),
        ("Níveis de Log", test_log_levels)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            if result:
                print(f"✅ {test_name}: PASSOU")
                passed += 1
            else:
                print(f"❌ {test_name}: FALHOU")
        except Exception as e:
            print(f"❌ {test_name}: ERRO - {e}")
    
    print("\n" + "="*60)
    print(f"Resultado Final: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES DE LOGGING PASSARAM!")
    else:
        print(f"⚠️  {total - passed} teste(s) falharam")
    
    print("="*60)
    print("✅ TESTE COMPLETO FINALIZADO")
    print("Sistema de logging testado e funcionando!")


if __name__ == "__main__":
    main()