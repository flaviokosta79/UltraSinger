"""
Sistema robusto de tratamento de erros e validações para UltraSinger
Centraliza o tratamento de exceções e fornece validações consistentes
"""

import os
import sys
import traceback
import functools
from typing import Dict, Any, Optional, List, Callable, Union, Type
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from modules.console_colors import ULTRASINGER_HEAD, red_highlighted, blue_highlighted, yellow_highlighted
from modules.logger import get_logger

logger = get_logger()


class ErrorSeverity(Enum):
    """Níveis de severidade de erro"""
    LOW = "low"           # Avisos, não impedem execução
    MEDIUM = "medium"     # Erros recuperáveis
    HIGH = "high"         # Erros críticos, impedem execução
    CRITICAL = "critical" # Erros que podem corromper dados


class ErrorCategory(Enum):
    """Categorias de erro"""
    VALIDATION = "validation"
    FILE_IO = "file_io"
    NETWORK = "network"
    AUDIO_PROCESSING = "audio_processing"
    AI_MODEL = "ai_model"
    SYSTEM_RESOURCE = "system_resource"
    USER_INPUT = "user_input"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    UNKNOWN = "unknown"


@dataclass
class UltraSingerError:
    """Estrutura padronizada de erro"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Optional[str] = None
    suggestions: List[str] = None
    error_code: Optional[str] = None
    module: str = "Core"
    context: Dict[str, Any] = None
    original_exception: Optional[Exception] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.context is None:
            self.context = {}


class ValidationError(Exception):
    """Exceção personalizada para erros de validação"""
    
    def __init__(self, message: str, field: str = None, value: Any = None, suggestions: List[str] = None):
        super().__init__(message)
        self.field = field
        self.value = value
        self.suggestions = suggestions or []


class ProcessingError(Exception):
    """Exceção personalizada para erros de processamento"""
    
    def __init__(self, message: str, stage: str = None, context: Dict[str, Any] = None):
        super().__init__(message)
        self.stage = stage
        self.context = context or {}


class ResourceError(Exception):
    """Exceção personalizada para erros de recursos"""
    
    def __init__(self, message: str, resource_type: str = None, available: float = None, required: float = None):
        super().__init__(message)
        self.resource_type = resource_type
        self.available = available
        self.required = required


class ErrorHandler:
    """Manipulador central de erros"""
    
    def __init__(self, log_errors: bool = True, save_error_reports: bool = True):
        self.log_errors = log_errors
        self.save_error_reports = save_error_reports
        self.error_history: List[UltraSingerError] = []
        self.error_stats = {
            "total_errors": 0,
            "by_category": {},
            "by_severity": {},
            "by_module": {}
        }
        
        # Configurar diretório de relatórios de erro
        self.error_reports_dir = Path("logs/error_reports")
        if self.save_error_reports:
            self.error_reports_dir.mkdir(parents=True, exist_ok=True)
    
    def handle_error(self, 
                    error: Union[Exception, UltraSingerError],
                    category: ErrorCategory = ErrorCategory.UNKNOWN,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    module: str = "Core",
                    context: Dict[str, Any] = None,
                    suggestions: List[str] = None) -> UltraSingerError:
        """Processar e registrar um erro"""
        
        if isinstance(error, UltraSingerError):
            ultrasinger_error = error
        else:
            # Converter Exception para UltraSingerError
            ultrasinger_error = UltraSingerError(
                category=category,
                severity=severity,
                message=str(error),
                details=self._get_error_details(error),
                suggestions=suggestions or self._get_default_suggestions(category, error),
                module=module,
                context=context or {},
                original_exception=error
            )
        
        # Registrar erro
        self._register_error(ultrasinger_error)
        
        # Log do erro
        if self.log_errors:
            self._log_error(ultrasinger_error)
        
        # Salvar relatório se necessário
        if self.save_error_reports and ultrasinger_error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self._save_error_report(ultrasinger_error)
        
        return ultrasinger_error
    
    def _get_error_details(self, error: Exception) -> str:
        """Obter detalhes técnicos do erro"""
        if hasattr(error, '__traceback__') and error.__traceback__:
            return ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        return str(error)
    
    def _get_default_suggestions(self, category: ErrorCategory, error: Exception) -> List[str]:
        """Obter sugestões padrão baseadas na categoria do erro"""
        
        suggestions_map = {
            ErrorCategory.VALIDATION: [
                "Verifique se todos os campos obrigatórios estão preenchidos",
                "Confirme se os valores estão no formato correto",
                "Consulte a documentação para requisitos específicos"
            ],
            ErrorCategory.FILE_IO: [
                "Verifique se o arquivo existe e tem as permissões corretas",
                "Confirme se há espaço suficiente em disco",
                "Tente usar um caminho absoluto para o arquivo"
            ],
            ErrorCategory.NETWORK: [
                "Verifique sua conexão com a internet",
                "Tente novamente em alguns minutos",
                "Considere usar um proxy ou VPN se necessário"
            ],
            ErrorCategory.AUDIO_PROCESSING: [
                "Verifique se o arquivo de áudio não está corrompido",
                "Tente converter o áudio para um formato suportado",
                "Reduza a qualidade ou duração do áudio se necessário"
            ],
            ErrorCategory.AI_MODEL: [
                "Verifique se há memória suficiente disponível",
                "Tente usar um modelo menor ou forçar uso de CPU",
                "Reinicie o aplicativo para limpar a memória"
            ],
            ErrorCategory.SYSTEM_RESOURCE: [
                "Feche outros aplicativos para liberar recursos",
                "Considere usar configurações de menor qualidade",
                "Verifique se há espaço suficiente em disco"
            ],
            ErrorCategory.USER_INPUT: [
                "Verifique se os parâmetros estão corretos",
                "Consulte a ajuda do comando para sintaxe correta",
                "Tente usar valores padrão primeiro"
            ],
            ErrorCategory.CONFIGURATION: [
                "Verifique o arquivo de configuração",
                "Restaure as configurações padrão se necessário",
                "Consulte a documentação de configuração"
            ],
            ErrorCategory.DEPENDENCY: [
                "Verifique se todas as dependências estão instaladas",
                "Tente reinstalar as dependências",
                "Verifique se as versões são compatíveis"
            ]
        }
        
        base_suggestions = suggestions_map.get(category, ["Consulte a documentação ou reporte o erro"])
        
        # Sugestões específicas baseadas no tipo de exceção
        error_type = type(error).__name__
        if error_type == "FileNotFoundError":
            base_suggestions.insert(0, "Verifique se o caminho do arquivo está correto")
        elif error_type == "PermissionError":
            base_suggestions.insert(0, "Execute com privilégios de administrador se necessário")
        elif error_type == "MemoryError":
            base_suggestions.insert(0, "Reduza o tamanho do batch ou use configurações de menor memória")
        elif "CUDA" in str(error) or "GPU" in str(error):
            base_suggestions.insert(0, "Tente forçar o uso de CPU com --force_cpu")
        
        return base_suggestions
    
    def _register_error(self, error: UltraSingerError):
        """Registrar erro nas estatísticas"""
        self.error_history.append(error)
        
        # Atualizar estatísticas
        self.error_stats["total_errors"] += 1
        
        # Por categoria
        category_key = error.category.value
        self.error_stats["by_category"][category_key] = self.error_stats["by_category"].get(category_key, 0) + 1
        
        # Por severidade
        severity_key = error.severity.value
        self.error_stats["by_severity"][severity_key] = self.error_stats["by_severity"].get(severity_key, 0) + 1
        
        # Por módulo
        module_key = error.module
        self.error_stats["by_module"][module_key] = self.error_stats["by_module"].get(module_key, 0) + 1
        
        # Manter apenas últimos 1000 erros
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
    
    def _log_error(self, error: UltraSingerError):
        """Fazer log do erro"""
        
        # Determinar nível de log baseado na severidade
        if error.severity == ErrorSeverity.LOW:
            log_func = logger.warning
        elif error.severity == ErrorSeverity.MEDIUM:
            log_func = logger.error
        else:  # HIGH ou CRITICAL
            log_func = logger.critical
        
        # Log principal
        log_func(
            f"{error.message}",
            module=error.module,
            category=error.category.value,
            severity=error.severity.value,
            exception=error.original_exception,
            **error.context
        )
        
        # Log de sugestões se disponíveis
        if error.suggestions:
            logger.info(f"Sugestões: {'; '.join(error.suggestions)}", module=error.module)
    
    def _save_error_report(self, error: UltraSingerError):
        """Salvar relatório detalhado do erro"""
        try:
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_report_{timestamp}_{error.category.value}.json"
            filepath = self.error_reports_dir / filename
            
            report = {
                "timestamp": timestamp,
                "category": error.category.value,
                "severity": error.severity.value,
                "module": error.module,
                "message": error.message,
                "details": error.details,
                "suggestions": error.suggestions,
                "context": error.context,
                "error_code": error.error_code,
                "system_info": {
                    "platform": sys.platform,
                    "python_version": sys.version,
                    "working_directory": os.getcwd()
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Relatório de erro salvo: {filename}", module="ErrorHandler")
            
        except Exception as e:
            logger.warning(f"Falha ao salvar relatório de erro: {e}", module="ErrorHandler")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Obter resumo dos erros"""
        return {
            "total_errors": self.error_stats["total_errors"],
            "by_category": dict(self.error_stats["by_category"]),
            "by_severity": dict(self.error_stats["by_severity"]),
            "by_module": dict(self.error_stats["by_module"]),
            "recent_errors": [
                {
                    "category": error.category.value,
                    "severity": error.severity.value,
                    "message": error.message,
                    "module": error.module
                }
                for error in self.error_history[-10:]  # Últimos 10 erros
            ]
        }
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Obter estatísticas detalhadas dos erros"""
        return {
            "total_errors": self.error_stats["total_errors"],
            "categories": dict(self.error_stats["by_category"]),
            "severities": dict(self.error_stats["by_severity"]),
            "modules": dict(self.error_stats["by_module"]),
            "error_rate": len(self.error_history) / max(1, self.error_stats["total_errors"]),
            "recent_count": len(self.error_history[-10:])
        }
    
    def clear_error_history(self):
        """Limpar histórico de erros"""
        self.error_history.clear()
        self.error_stats = {
            "total_errors": 0,
            "by_category": {},
            "by_severity": {},
            "by_module": {}
        }
        logger.info("Histórico de erros limpo", module="ErrorHandler")


class InputValidator:
    """Validador de entradas do usuário"""
    
    @staticmethod
    def validate_file_path(path: str, must_exist: bool = True, extensions: List[str] = None) -> bool:
        """Validar caminho de arquivo"""
        if not path or not isinstance(path, str):
            raise ValidationError("Caminho do arquivo não pode estar vazio", field="file_path", value=path)
        
        path_obj = Path(path)
        
        if must_exist and not path_obj.exists():
            raise ValidationError(
                f"Arquivo não encontrado: {path}",
                field="file_path",
                value=path,
                suggestions=["Verifique se o caminho está correto", "Use caminho absoluto"]
            )
        
        if extensions:
            if not any(path.lower().endswith(ext.lower()) for ext in extensions):
                raise ValidationError(
                    f"Extensão de arquivo inválida. Esperado: {', '.join(extensions)}",
                    field="file_extension",
                    value=path_obj.suffix,
                    suggestions=[f"Use um arquivo com extensão {', '.join(extensions)}"]
                )
        
        return True
    
    @staticmethod
    def validate_url(url: str, allowed_domains: List[str] = None) -> bool:
        """Validar URL"""
        if not url or not isinstance(url, str):
            raise ValidationError("URL não pode estar vazia", field="url", value=url)
        
        # Validação básica de URL
        if not (url.startswith('http://') or url.startswith('https://')):
            raise ValidationError(
                "URL deve começar com http:// ou https://",
                field="url",
                value=url,
                suggestions=["Adicione http:// ou https:// no início da URL"]
            )
        
        # Validar domínios permitidos
        if allowed_domains:
            domain_found = any(domain in url for domain in allowed_domains)
            if not domain_found:
                raise ValidationError(
                    f"Domínio não permitido. Domínios aceitos: {', '.join(allowed_domains)}",
                    field="url_domain",
                    value=url,
                    suggestions=[f"Use uma URL de: {', '.join(allowed_domains)}"]
                )
        
        return True
    
    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_val: float = None, max_val: float = None, field_name: str = "value") -> bool:
        """Validar valor numérico dentro de um intervalo"""
        if not isinstance(value, (int, float)):
            raise ValidationError(
                f"{field_name} deve ser um número",
                field=field_name,
                value=value,
                suggestions=["Use um valor numérico válido"]
            )
        
        if min_val is not None and value < min_val:
            raise ValidationError(
                f"{field_name} deve ser maior ou igual a {min_val}",
                field=field_name,
                value=value,
                suggestions=[f"Use um valor >= {min_val}"]
            )
        
        if max_val is not None and value > max_val:
            raise ValidationError(
                f"{field_name} deve ser menor ou igual a {max_val}",
                field=field_name,
                value=value,
                suggestions=[f"Use um valor <= {max_val}"]
            )
        
        return True
    
    @staticmethod
    def validate_audio_format(file_path: str) -> bool:
        """Validar formato de arquivo de áudio"""
        supported_formats = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac']
        
        return InputValidator.validate_file_path(
            file_path,
            must_exist=True,
            extensions=supported_formats
        )
    
    @staticmethod
    def validate_model_name(model_name: str, available_models: List[str]) -> bool:
        """Validar nome do modelo"""
        if not model_name or not isinstance(model_name, str):
            raise ValidationError("Nome do modelo não pode estar vazio", field="model_name", value=model_name)
        
        if model_name not in available_models:
            raise ValidationError(
                f"Modelo '{model_name}' não disponível",
                field="model_name",
                value=model_name,
                suggestions=[f"Use um dos modelos disponíveis: {', '.join(available_models)}"]
            )
        
        return True


def error_handler_decorator(category: ErrorCategory = ErrorCategory.UNKNOWN, 
                          severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                          reraise: bool = True):
    """Decorator para tratamento automático de erros"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Obter instância do error handler
                error_handler = get_error_handler()
                
                # Processar erro
                ultrasinger_error = error_handler.handle_error(
                    error=e,
                    category=category,
                    severity=severity,
                    module=func.__module__ or "Unknown",
                    context={
                        "function": func.__name__,
                        "args": str(args)[:200],  # Limitar tamanho
                        "kwargs": str(kwargs)[:200]
                    }
                )
                
                # Re-lançar exceção se necessário
                if reraise:
                    raise e
                
                return ultrasinger_error
        
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default_return=None, **kwargs) -> Any:
    """Executar função de forma segura com tratamento de erro"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler = get_error_handler()
        error_handler.handle_error(
            error=e,
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.MEDIUM,
            module=func.__module__ or "Unknown",
            context={"function": func.__name__}
        )
        return default_return


def validate_system_requirements() -> List[str]:
    """Validar requisitos do sistema"""
    issues = []
    
    try:
        # Verificar Python
        if sys.version_info < (3, 8):
            issues.append("Python 3.8+ é necessário")
        
        # Verificar espaço em disco (mínimo 1GB)
        import shutil
        free_space = shutil.disk_usage('.').free / (1024**3)  # GB
        if free_space < 1.0:
            issues.append(f"Espaço em disco insuficiente: {free_space:.1f}GB disponível, mínimo 1GB necessário")
        
        # Verificar dependências críticas
        critical_modules = ['torch', 'numpy', 'librosa']
        for module in critical_modules:
            try:
                __import__(module)
            except ImportError:
                issues.append(f"Módulo crítico não encontrado: {module}")
        
    except Exception as e:
        issues.append(f"Erro na validação do sistema: {e}")
    
    return issues


# Instância global
_global_error_handler = None

def get_error_handler() -> ErrorHandler:
    """Obter instância global do manipulador de erros"""
    global _global_error_handler
    
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    
    return _global_error_handler


def setup_global_exception_handler():
    """Configurar manipulador global de exceções não capturadas"""
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Permitir Ctrl+C
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_handler = get_error_handler()
        error_handler.handle_error(
            error=exc_value,
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.CRITICAL,
            module="Global",
            context={"uncaught_exception": True}
        )
        
        # Chamar o handler padrão também
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = handle_exception
    logger.info("Manipulador global de exceções configurado", module="ErrorHandler")