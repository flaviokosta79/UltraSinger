"""
Teste do sistema robusto de tratamento de erros do UltraSinger
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.error_handler import (
    ErrorHandler, 
    UltraSingerError,
    ErrorCategory,
    ErrorSeverity,
    ValidationError,
    ProcessingError,
    ResourceError,
    InputValidator,
    error_handler_decorator,
    safe_execute,
    validate_system_requirements,
    get_error_handler,
    setup_global_exception_handler
)
from modules.logger import get_logger

logger = get_logger()

def test_error_creation():
    """Testar criação de erros estruturados"""
    print("\n=== Teste de Criação de Erros ===")
    
    # Criar erro básico
    error = UltraSingerError(
        category=ErrorCategory.VALIDATION,
        severity=ErrorSeverity.MEDIUM,
        message="Teste de erro de validação",
        module="TestModule"
    )
    
    assert error.category == ErrorCategory.VALIDATION
    assert error.severity == ErrorSeverity.MEDIUM
    assert error.message == "Teste de erro de validação"
    assert error.module == "TestModule"
    assert isinstance(error.suggestions, list)
    assert isinstance(error.context, dict)
    
    print("✓ Criação de erro básico funcionando")
    
    # Criar erro com detalhes
    detailed_error = UltraSingerError(
        category=ErrorCategory.AUDIO_PROCESSING,
        severity=ErrorSeverity.HIGH,
        message="Falha no processamento de áudio",
        details="Stack trace detalhado aqui",
        suggestions=["Verifique o arquivo de áudio", "Tente outro formato"],
        error_code="AUDIO_001",
        context={"file_path": "/test/audio.mp3", "duration": 180}
    )
    
    assert len(detailed_error.suggestions) == 2
    assert detailed_error.error_code == "AUDIO_001"
    assert "file_path" in detailed_error.context
    
    print("✓ Criação de erro detalhado funcionando")
    
    return True

def test_custom_exceptions():
    """Testar exceções personalizadas"""
    print("\n=== Teste de Exceções Personalizadas ===")
    
    # Teste ValidationError
    try:
        raise ValidationError(
            "Campo obrigatório não preenchido",
            field="artist",
            value=None,
            suggestions=["Preencha o campo artista"]
        )
    except ValidationError as e:
        assert e.field == "artist"
        assert e.value is None
        assert len(e.suggestions) == 1
        print("✓ ValidationError funcionando")
    
    # Teste ProcessingError
    try:
        raise ProcessingError(
            "Falha na separação de áudio",
            stage="demucs_processing",
            context={"model": "htdemucs", "device": "cuda"}
        )
    except ProcessingError as e:
        assert e.stage == "demucs_processing"
        assert "model" in e.context
        print("✓ ProcessingError funcionando")
    
    # Teste ResourceError
    try:
        raise ResourceError(
            "Memória insuficiente",
            resource_type="GPU_MEMORY",
            available=4.0,
            required=8.0
        )
    except ResourceError as e:
        assert e.resource_type == "GPU_MEMORY"
        assert e.available == 4.0
        assert e.required == 8.0
        print("✓ ResourceError funcionando")
    
    return True

def test_error_handler():
    """Testar manipulador de erros"""
    print("\n=== Teste de Manipulador de Erros ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Criar handler com diretório temporário
        handler = ErrorHandler(log_errors=True, save_error_reports=True)
        handler.error_reports_dir = Path(temp_dir) / "error_reports"
        handler.error_reports_dir.mkdir(exist_ok=True)
        
        # Testar tratamento de Exception simples
        try:
            raise ValueError("Valor inválido para teste")
        except Exception as e:
            ultrasinger_error = handler.handle_error(
                error=e,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.MEDIUM,
                module="TestModule",
                context={"test_param": "test_value"}
            )
            
            assert isinstance(ultrasinger_error, UltraSingerError)
            assert ultrasinger_error.category == ErrorCategory.VALIDATION
            assert ultrasinger_error.original_exception == e
            print("✓ Tratamento de Exception funcionando")
        
        # Testar tratamento de UltraSingerError
        custom_error = UltraSingerError(
            category=ErrorCategory.AI_MODEL,
            severity=ErrorSeverity.HIGH,
            message="Modelo não carregado",
            module="WhisperModule"
        )
        
        handled_error = handler.handle_error(custom_error)
        assert handled_error == custom_error
        print("✓ Tratamento de UltraSingerError funcionando")
        
        # Verificar estatísticas
        stats = handler.get_error_summary()
        assert stats["total_errors"] == 2
        assert "validation" in stats["by_category"]
        assert "ai_model" in stats["by_category"]
        print("✓ Estatísticas de erro funcionando")
        
        # Verificar histórico
        assert len(handler.error_history) == 2
        print("✓ Histórico de erros funcionando")
    
    return True

def test_input_validator():
    """Testar validador de entradas"""
    print("\n=== Teste de Validador de Entradas ===")
    
    # Teste de validação de arquivo
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Arquivo existente com extensão válida
        assert InputValidator.validate_file_path(temp_path, must_exist=True, extensions=['.mp3'])
        print("✓ Validação de arquivo existente funcionando")
        
        # Teste de arquivo inexistente
        try:
            InputValidator.validate_file_path("arquivo_inexistente.mp3", must_exist=True)
            assert False, "Deveria ter lançado ValidationError"
        except ValidationError as e:
            assert "não encontrado" in str(e).lower()
            print("✓ Validação de arquivo inexistente funcionando")
        
        # Teste de extensão inválida
        try:
            InputValidator.validate_file_path(temp_path, extensions=['.wav'])
            assert False, "Deveria ter lançado ValidationError"
        except ValidationError as e:
            assert "extensão" in str(e).lower()
            print("✓ Validação de extensão funcionando")
    
    finally:
        os.unlink(temp_path)
    
    # Teste de validação de URL
    assert InputValidator.validate_url("https://www.youtube.com/watch?v=test")
    print("✓ Validação de URL válida funcionando")
    
    try:
        InputValidator.validate_url("invalid_url")
        assert False, "Deveria ter lançado ValidationError"
    except ValidationError as e:
        assert "http" in str(e).lower()
        print("✓ Validação de URL inválida funcionando")
    
    # Teste de validação numérica
    assert InputValidator.validate_numeric_range(5, min_val=0, max_val=10)
    print("✓ Validação numérica válida funcionando")
    
    try:
        InputValidator.validate_numeric_range(15, min_val=0, max_val=10)
        assert False, "Deveria ter lançado ValidationError"
    except ValidationError as e:
        assert "menor ou igual" in str(e).lower()
        print("✓ Validação numérica inválida funcionando")
    
    # Teste de validação de modelo
    available_models = ["small", "medium", "large"]
    assert InputValidator.validate_model_name("small", available_models)
    print("✓ Validação de modelo válido funcionando")
    
    try:
        InputValidator.validate_model_name("invalid_model", available_models)
        assert False, "Deveria ter lançado ValidationError"
    except ValidationError as e:
        assert "não disponível" in str(e).lower()
        print("✓ Validação de modelo inválido funcionando")
    
    return True

def test_error_decorator():
    """Testar decorator de tratamento de erros"""
    print("\n=== Teste de Decorator de Erros ===")
    
    @error_handler_decorator(
        category=ErrorCategory.AUDIO_PROCESSING,
        severity=ErrorSeverity.HIGH,
        reraise=False
    )
    def function_with_error():
        raise ValueError("Erro simulado")
    
    # Função que não re-lança erro
    result = function_with_error()
    assert isinstance(result, UltraSingerError)
    assert result.category == ErrorCategory.AUDIO_PROCESSING
    print("✓ Decorator sem re-lançamento funcionando")
    
    @error_handler_decorator(
        category=ErrorCategory.VALIDATION,
        severity=ErrorSeverity.MEDIUM,
        reraise=True
    )
    def function_with_reraise():
        raise ValueError("Erro que será re-lançado")
    
    # Função que re-lança erro
    try:
        function_with_reraise()
        assert False, "Deveria ter re-lançado o erro"
    except ValueError:
        print("✓ Decorator com re-lançamento funcionando")
    
    return True

def test_safe_execute():
    """Testar execução segura"""
    print("\n=== Teste de Execução Segura ===")
    
    def function_that_works():
        return "sucesso"
    
    def function_that_fails():
        raise ValueError("Falha simulada")
    
    # Função que funciona
    result = safe_execute(function_that_works)
    assert result == "sucesso"
    print("✓ Execução segura de função válida funcionando")
    
    # Função que falha
    result = safe_execute(function_that_fails, default_return="valor_padrão")
    assert result == "valor_padrão"
    print("✓ Execução segura de função com erro funcionando")
    
    return True

def test_system_validation():
    """Testar validação de requisitos do sistema"""
    print("\n=== Teste de Validação do Sistema ===")
    
    issues = validate_system_requirements()
    
    # Deve retornar uma lista (pode estar vazia se tudo estiver OK)
    assert isinstance(issues, list)
    print(f"✓ Validação do sistema executada: {len(issues)} problemas encontrados")
    
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("  Sistema atende todos os requisitos")
    
    return True

def test_global_error_handler():
    """Testar manipulador global de erros"""
    print("\n=== Teste de Manipulador Global ===")
    
    # Obter primeira instância
    handler1 = get_error_handler()
    
    # Obter segunda instância
    handler2 = get_error_handler()
    
    # Devem ser a mesma instância
    assert handler1 is handler2
    print("✓ Instância global funcionando")
    
    # Testar configuração do manipulador global de exceções
    setup_global_exception_handler()
    print("✓ Manipulador global de exceções configurado")
    
    return True

def test_error_suggestions():
    """Testar sistema de sugestões de erro"""
    print("\n=== Teste de Sugestões de Erro ===")
    
    handler = ErrorHandler()
    
    # Testar diferentes tipos de erro para verificar sugestões
    test_errors = [
        (FileNotFoundError("Arquivo não encontrado"), ErrorCategory.FILE_IO),
        (PermissionError("Permissão negada"), ErrorCategory.FILE_IO),
        (MemoryError("Sem memória"), ErrorCategory.SYSTEM_RESOURCE),
        (ValueError("Valor inválido"), ErrorCategory.VALIDATION),
    ]
    
    for error, category in test_errors:
        ultrasinger_error = handler.handle_error(error, category=category)
        assert len(ultrasinger_error.suggestions) > 0
        print(f"✓ Sugestões para {type(error).__name__}: {len(ultrasinger_error.suggestions)} sugestões")
    
    return True

def test_error_reporting():
    """Testar sistema de relatórios de erro"""
    print("\n=== Teste de Relatórios de Erro ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        handler = ErrorHandler(save_error_reports=True)
        handler.error_reports_dir = Path(temp_dir) / "error_reports"
        handler.error_reports_dir.mkdir(exist_ok=True)
        
        # Criar erro crítico que deve gerar relatório
        try:
            raise RuntimeError("Erro crítico para teste")
        except Exception as e:
            handler.handle_error(
                error=e,
                category=ErrorCategory.SYSTEM_RESOURCE,
                severity=ErrorSeverity.CRITICAL,
                module="TestModule"
            )
        
        # Verificar se relatório foi criado
        report_files = list(handler.error_reports_dir.glob("*.json"))
        assert len(report_files) > 0, "Relatório de erro não foi criado"
        
        # Verificar conteúdo do relatório
        with open(report_files[0], 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        required_fields = ["timestamp", "category", "severity", "module", "message", "system_info"]
        for field in required_fields:
            assert field in report_data, f"Campo {field} não encontrado no relatório"
        
        print(f"✓ Relatório de erro criado: {report_files[0].name}")
        print(f"✓ Relatório contém todos os campos necessários")
    
    return True

def run_all_tests():
    """Executar todos os testes"""
    print("🚀 Iniciando testes do sistema de tratamento de erros...")
    
    tests = [
        ("Criação de Erros", test_error_creation),
        ("Exceções Personalizadas", test_custom_exceptions),
        ("Manipulador de Erros", test_error_handler),
        ("Validador de Entradas", test_input_validator),
        ("Decorator de Erros", test_error_decorator),
        ("Execução Segura", test_safe_execute),
        ("Validação do Sistema", test_system_validation),
        ("Manipulador Global", test_global_error_handler),
        ("Sugestões de Erro", test_error_suggestions),
        ("Relatórios de Erro", test_error_reporting)
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
        print("\n🎉 Todos os testes passaram! Sistema de tratamento de erros funcionando perfeitamente.")
    else:
        print(f"\n⚠️  {failed} teste(s) falharam. Verifique os erros acima.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)