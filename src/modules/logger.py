"""
Sistema de logging avançado para UltraSinger
Fornece logging estruturado com diferentes níveis e formatação colorida
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
import json

# Cores para terminal
class LogColors:
    """Cores ANSI para formatação de logs no terminal"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Cores básicas
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Cores brilhantes
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'


class ColoredFormatter(logging.Formatter):
    """Formatador personalizado com cores para diferentes níveis de log"""
    
    LEVEL_COLORS = {
        logging.DEBUG: LogColors.CYAN,
        logging.INFO: LogColors.GREEN,
        logging.WARNING: LogColors.YELLOW,
        logging.ERROR: LogColors.RED,
        logging.CRITICAL: LogColors.BRIGHT_RED + LogColors.BOLD,
    }
    
    def __init__(self, fmt=None, datefmt=None, use_colors=True):
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors and sys.stdout.isatty()
    
    def format(self, record):
        if self.use_colors:
            # Aplicar cor baseada no nível
            level_color = self.LEVEL_COLORS.get(record.levelno, LogColors.WHITE)
            record.levelname = f"{level_color}{record.levelname}{LogColors.RESET}"
            
            # Colorir o nome do módulo
            if hasattr(record, 'module_name'):
                record.module_name = f"{LogColors.BLUE}{record.module_name}{LogColors.RESET}"
        
        return super().format(record)


class UltraSingerLogger:
    """Logger principal do UltraSinger com funcionalidades avançadas"""
    
    def __init__(self, name: str = "UltraSinger", log_dir: Optional[str] = None):
        self.name = name
        self.log_dir = log_dir or "logs"
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Evitar duplicação de handlers
        if not self.logger.handlers:
            self._setup_handlers()
        
        # Métricas de performance
        self.performance_metrics = {}
        self.operation_start_times = {}
    
    def _setup_handlers(self):
        """Configurar handlers de console e arquivo"""
        
        # Handler para console com cores
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        console_format = "[%(asctime)s] [%(levelname)s] [%(module_name)s] %(message)s"
        console_formatter = ColoredFormatter(
            fmt=console_format,
            datefmt="%H:%M:%S",
            use_colors=True
        )
        console_handler.setFormatter(console_formatter)
        
        # Handler para arquivo detalhado
        if self.log_dir:
            os.makedirs(self.log_dir, exist_ok=True)
            
            # Log geral
            log_file = os.path.join(self.log_dir, f"ultrasinger_{datetime.now().strftime('%Y%m%d')}.log")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            file_format = "[%(asctime)s] [%(levelname)s] [%(name)s.%(module_name)s] [%(funcName)s:%(lineno)d] %(message)s"
            file_formatter = logging.Formatter(
                fmt=file_format,
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            
            # Log de erros separado
            error_file = os.path.join(self.log_dir, f"ultrasinger_errors_{datetime.now().strftime('%Y%m%d')}.log")
            error_handler = logging.FileHandler(error_file, encoding='utf-8')
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(file_formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(error_handler)
        
        self.logger.addHandler(console_handler)
    
    def _add_context(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Adicionar contexto padrão aos logs"""
        context = {
            'module_name': 'Core'
        }
        
        if extra:
            context.update(extra)
        
        return context
    
    def debug(self, message: str, module: str = "Core", **kwargs):
        """Log de debug detalhado"""
        extra = self._add_context({'module_name': module})
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.debug(message, extra=extra)
    
    def info(self, message: str, module: str = "Core", **kwargs):
        """Log informativo"""
        extra = self._add_context({'module_name': module})
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, module: str = "Core", **kwargs):
        """Log de aviso"""
        extra = self._add_context({'module_name': module})
        if kwargs:
            message = f"{message} | {kwargs}"
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, module: str = "Core", exception: Optional[Exception] = None, **kwargs):
        """Log de erro com detalhes da exceção"""
        extra = self._add_context({'module_name': module})
        
        if exception:
            message = f"{message} | Exception: {type(exception).__name__}: {str(exception)}"
        
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        
        self.logger.error(message, extra=extra, exc_info=exception is not None)
    
    def critical(self, message: str, module: str = "Core", exception: Optional[Exception] = None, **kwargs):
        """Log crítico para erros graves"""
        extra = self._add_context({'module_name': module})
        
        if exception:
            message = f"{message} | Exception: {type(exception).__name__}: {str(exception)}"
        
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        
        self.logger.critical(message, extra=extra, exc_info=exception is not None)
    
    def start_operation(self, operation_name: str, module: str = "Core", **context):
        """Iniciar tracking de uma operação"""
        self.operation_start_times[operation_name] = datetime.now()
        self.info(f"Iniciando operação: {operation_name}", module=module, **context)
    
    def end_operation(self, operation_name: str, module: str = "Core", success: bool = True, **context):
        """Finalizar tracking de uma operação"""
        if operation_name in self.operation_start_times:
            start_time = self.operation_start_times[operation_name]
            duration = (datetime.now() - start_time).total_seconds()
            
            # Salvar métrica
            if operation_name not in self.performance_metrics:
                self.performance_metrics[operation_name] = []
            self.performance_metrics[operation_name].append({
                'duration': duration,
                'success': success,
                'timestamp': datetime.now().isoformat()
            })
            
            status = "✓" if success else "✗"
            self.info(
                f"{status} Operação finalizada: {operation_name} ({duration:.2f}s)",
                module=module,
                duration=duration,
                success=success,
                **context
            )
            
            del self.operation_start_times[operation_name]
        else:
            self.warning(f"Operação {operation_name} não foi iniciada corretamente", module=module)
    
    def log_performance_metrics(self):
        """Log das métricas de performance coletadas"""
        if not self.performance_metrics:
            self.info("Nenhuma métrica de performance coletada")
            return
        
        self.info("=== MÉTRICAS DE PERFORMANCE ===")
        
        for operation, metrics in self.performance_metrics.items():
            if not metrics:
                continue
            
            durations = [m['duration'] for m in metrics]
            successes = [m['success'] for m in metrics]
            
            avg_duration = sum(durations) / len(durations)
            success_rate = sum(successes) / len(successes) * 100
            
            self.info(
                f"{operation}: {len(metrics)} execuções, "
                f"tempo médio: {avg_duration:.2f}s, "
                f"taxa de sucesso: {success_rate:.1f}%"
            )
    
    def save_performance_report(self, output_file: Optional[str] = None):
        """Salvar relatório detalhado de performance"""
        if not self.performance_metrics:
            return
        
        if not output_file:
            output_file = os.path.join(self.log_dir, f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'metrics': self.performance_metrics
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.info(f"Relatório de performance salvo: {output_file}")
            
        except Exception as e:
            self.error(f"Falha ao salvar relatório de performance", exception=e)


# Instância global do logger
_global_logger = None

def get_logger(name: str = "UltraSinger", log_dir: Optional[str] = None) -> UltraSingerLogger:
    """Obter instância do logger (singleton)"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = UltraSingerLogger(name, log_dir)
    
    return _global_logger


def setup_logging(log_level: str = "INFO", log_dir: Optional[str] = None, enable_performance_tracking: bool = True):
    """Configurar sistema de logging global"""
    
    # Configurar nível de log
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logger = get_logger(log_dir=log_dir)
    logger.logger.setLevel(numeric_level)
    
    # Configurar handlers existentes
    for handler in logger.logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            handler.setLevel(max(numeric_level, logging.INFO))  # Console sempre INFO ou superior
        else:
            handler.setLevel(numeric_level)
    
    logger.info("Sistema de logging configurado", log_level=log_level, log_dir=log_dir)
    
    return logger


# Funções de conveniência para uso direto
def debug(message: str, module: str = "Core", **kwargs):
    """Log de debug"""
    get_logger().debug(message, module, **kwargs)

def info(message: str, module: str = "Core", **kwargs):
    """Log informativo"""
    get_logger().info(message, module, **kwargs)

def warning(message: str, module: str = "Core", **kwargs):
    """Log de aviso"""
    get_logger().warning(message, module, **kwargs)

def error(message: str, module: str = "Core", exception: Optional[Exception] = None, **kwargs):
    """Log de erro"""
    get_logger().error(message, module, exception, **kwargs)

def critical(message: str, module: str = "Core", exception: Optional[Exception] = None, **kwargs):
    """Log crítico"""
    get_logger().critical(message, module, exception, **kwargs)

def start_operation(operation_name: str, module: str = "Core", **context):
    """Iniciar operação"""
    get_logger().start_operation(operation_name, module, **context)

def end_operation(operation_name: str, module: str = "Core", success: bool = True, **context):
    """Finalizar operação"""
    get_logger().end_operation(operation_name, module, success, **context)