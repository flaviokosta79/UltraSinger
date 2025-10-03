#!/usr/bin/env python3
"""
Sistema de Logs Detalhados do UltraSinger
Fornece logging avançado para debugging e monitoramento
"""

import os
import json
import logging
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from contextlib import contextmanager

from modules.console_colors import ULTRASINGER_HEAD, green_highlighted, red_highlighted, yellow_highlighted


class LogLevel(Enum):
    """Níveis de log personalizados"""
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    PERFORMANCE = 25
    EXPORT = 22
    VALIDATION = 24


@dataclass
class LogEntry:
    """Entrada de log estruturada"""
    timestamp: datetime
    level: str
    module: str
    function: str
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    memory_usage: Optional[int] = None
    error_details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


class DetailedLogger:
    """Logger avançado com recursos de debugging e monitoramento"""
    
    def __init__(self, name: str = "UltraSinger", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar loggers
        self.logger = logging.getLogger(name)
        self.logger.setLevel(LogLevel.TRACE.value)
        
        # Evitar duplicação de handlers
        if not self.logger.handlers:
            self._setup_handlers()
        
        # Armazenamento em memória para análise
        self.log_entries: List[LogEntry] = []
        self.session_start = datetime.now()
        self.performance_metrics = {}
        
        # Configurações
        self.max_memory_entries = 1000
        self.auto_flush_interval = 100
        self.enable_performance_tracking = True
        self.enable_memory_tracking = True
        
        # Contadores
        self.log_count = 0
        self.error_count = 0
        self.warning_count = 0
    
    def _setup_handlers(self):
        """Configurar handlers de log"""
        # Handler para arquivo principal
        main_log_file = self.log_dir / f"{self.name.lower()}.log"
        file_handler = logging.FileHandler(main_log_file, encoding='utf-8')
        file_handler.setLevel(LogLevel.DEBUG.value)
        
        # Handler para erros
        error_log_file = self.log_dir / f"{self.name.lower()}_errors.log"
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_handler.setLevel(LogLevel.ERROR.value)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LogLevel.INFO.value)
        
        # Formatadores
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s'
        )
        
        file_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        # Adicionar handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
    
    def _get_caller_info(self) -> tuple:
        """Obter informações do chamador"""
        import inspect
        
        frame = inspect.currentframe()
        try:
            # Subir na pilha para encontrar o chamador real
            caller_frame = frame.f_back.f_back
            module = caller_frame.f_globals.get('__name__', 'unknown')
            function = caller_frame.f_code.co_name
            return module, function
        finally:
            del frame
    
    def _get_memory_usage(self) -> Optional[int]:
        """Obter uso atual de memória"""
        if not self.enable_memory_tracking:
            return None
        
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            return None
        except Exception:
            return None
    
    def _create_log_entry(self, level: str, message: str, data: Optional[Dict] = None, 
                         execution_time: Optional[float] = None, 
                         error_details: Optional[Dict] = None) -> LogEntry:
        """Criar entrada de log estruturada"""
        module, function = self._get_caller_info()
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            module=module,
            function=function,
            message=message,
            data=data,
            execution_time=execution_time,
            memory_usage=self._get_memory_usage(),
            error_details=error_details
        )
        
        # Adicionar à memória
        self.log_entries.append(entry)
        
        # Limitar entradas em memória
        if len(self.log_entries) > self.max_memory_entries:
            self.log_entries = self.log_entries[-self.max_memory_entries:]
        
        # Auto-flush periódico
        self.log_count += 1
        if self.log_count % self.auto_flush_interval == 0:
            self.flush_to_json()
        
        return entry
    
    def trace(self, message: str, data: Optional[Dict] = None):
        """Log de trace (mais detalhado que debug)"""
        entry = self._create_log_entry("TRACE", message, data)
        self.logger.log(LogLevel.TRACE.value, message)
    
    def debug(self, message: str, data: Optional[Dict] = None):
        """Log de debug"""
        entry = self._create_log_entry("DEBUG", message, data)
        self.logger.debug(message)
    
    def info(self, message: str, data: Optional[Dict] = None):
        """Log de informação"""
        entry = self._create_log_entry("INFO", message, data)
        self.logger.info(message)
    
    def warning(self, message: str, data: Optional[Dict] = None):
        """Log de aviso"""
        entry = self._create_log_entry("WARNING", message, data)
        self.logger.warning(message)
        self.warning_count += 1
    
    def error(self, message: str, error: Optional[Exception] = None, data: Optional[Dict] = None):
        """Log de erro"""
        error_details = None
        if error:
            error_details = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': traceback.format_exc()
            }
        
        entry = self._create_log_entry("ERROR", message, data, error_details=error_details)
        self.logger.error(message)
        self.error_count += 1
    
    def critical(self, message: str, error: Optional[Exception] = None, data: Optional[Dict] = None):
        """Log crítico"""
        error_details = None
        if error:
            error_details = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': traceback.format_exc()
            }
        
        entry = self._create_log_entry("CRITICAL", message, data, error_details=error_details)
        self.logger.critical(message)
        self.error_count += 1
    
    def performance(self, message: str, execution_time: float, data: Optional[Dict] = None):
        """Log de performance"""
        entry = self._create_log_entry("PERFORMANCE", message, data, execution_time=execution_time)
        self.logger.log(LogLevel.PERFORMANCE.value, f"{message} (tempo: {execution_time:.3f}s)")
        
        # Armazenar métricas de performance
        if self.enable_performance_tracking:
            module, function = self._get_caller_info()
            key = f"{module}.{function}"
            
            if key not in self.performance_metrics:
                self.performance_metrics[key] = {
                    'count': 0,
                    'total_time': 0.0,
                    'min_time': float('inf'),
                    'max_time': 0.0,
                    'avg_time': 0.0
                }
            
            metrics = self.performance_metrics[key]
            metrics['count'] += 1
            metrics['total_time'] += execution_time
            metrics['min_time'] = min(metrics['min_time'], execution_time)
            metrics['max_time'] = max(metrics['max_time'], execution_time)
            metrics['avg_time'] = metrics['total_time'] / metrics['count']
    
    def export_log(self, message: str, format_type: str, file_path: str, success: bool, 
                   file_size: int = 0, data: Optional[Dict] = None):
        """Log específico para exportação"""
        export_data = {
            'format_type': format_type,
            'file_path': file_path,
            'success': success,
            'file_size': file_size
        }
        
        if data:
            export_data.update(data)
        
        level = "INFO" if success else "ERROR"
        entry = self._create_log_entry("EXPORT", message, export_data)
        self.logger.log(LogLevel.EXPORT.value, message)
    
    def validation_log(self, message: str, file_path: str, is_valid: bool, 
                      errors: List[str] = None, warnings: List[str] = None, 
                      data: Optional[Dict] = None):
        """Log específico para validação"""
        validation_data = {
            'file_path': file_path,
            'is_valid': is_valid,
            'errors': errors or [],
            'warnings': warnings or []
        }
        
        if data:
            validation_data.update(data)
        
        level = "INFO" if is_valid else "WARNING"
        entry = self._create_log_entry("VALIDATION", message, validation_data)
        self.logger.log(LogLevel.VALIDATION.value, message)
    
    @contextmanager
    def performance_timer(self, operation_name: str, data: Optional[Dict] = None):
        """Context manager para medir tempo de execução"""
        start_time = datetime.now()
        
        try:
            self.debug(f"Iniciando operação: {operation_name}", data)
            yield
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.error(f"Erro na operação: {operation_name}", e, data)
            self.performance(f"Operação falhou: {operation_name}", execution_time, data)
            raise
            
        else:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.performance(f"Operação concluída: {operation_name}", execution_time, data)
    
    @contextmanager
    def log_context(self, context_name: str, data: Optional[Dict] = None):
        """Context manager para logging de contexto"""
        self.info(f"Entrando no contexto: {context_name}", data)
        
        try:
            yield self
        except Exception as e:
            self.error(f"Erro no contexto: {context_name}", e, data)
            raise
        finally:
            self.info(f"Saindo do contexto: {context_name}", data)
    
    def flush_to_json(self):
        """Salvar logs em formato JSON para análise"""
        if not self.log_entries:
            return
        
        json_file = self.log_dir / f"{self.name.lower()}_structured.json"
        
        try:
            # Carregar logs existentes se houver
            existing_logs = []
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    existing_logs = json.load(f)
            
            # Adicionar novos logs
            new_logs = [entry.to_dict() for entry in self.log_entries]
            all_logs = existing_logs + new_logs
            
            # Limitar tamanho do arquivo
            if len(all_logs) > 5000:
                all_logs = all_logs[-5000:]
            
            # Salvar
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(all_logs, f, indent=2, ensure_ascii=False)
            
            # Limpar logs em memória
            self.log_entries.clear()
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar logs JSON: {e}")
    
    def generate_session_report(self) -> str:
        """Gerar relatório da sessão atual"""
        session_duration = datetime.now() - self.session_start
        
        lines = [
            f"{ULTRASINGER_HEAD} RELATÓRIO DE SESSÃO DE LOGS",
            "=" * 60,
            f"Início da sessão: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duração: {session_duration}",
            f"Total de logs: {self.log_count}",
            f"Erros: {red_highlighted(str(self.error_count))}",
            f"Avisos: {yellow_highlighted(str(self.warning_count))}",
            ""
        ]
        
        # Métricas de performance
        if self.performance_metrics:
            lines.extend([
                "📊 MÉTRICAS DE PERFORMANCE:",
                "-" * 40
            ])
            
            for operation, metrics in sorted(self.performance_metrics.items()):
                lines.extend([
                    f"🔧 {operation}:",
                    f"  Execuções: {metrics['count']}",
                    f"  Tempo total: {metrics['total_time']:.3f}s",
                    f"  Tempo médio: {metrics['avg_time']:.3f}s",
                    f"  Tempo mín/máx: {metrics['min_time']:.3f}s / {metrics['max_time']:.3f}s",
                    ""
                ])
        
        # Logs recentes por nível
        if self.log_entries:
            lines.extend([
                "📋 RESUMO DOS LOGS RECENTES:",
                "-" * 40
            ])
            
            level_counts = {}
            for entry in self.log_entries[-100:]:  # Últimas 100 entradas
                level_counts[entry.level] = level_counts.get(entry.level, 0) + 1
            
            for level, count in sorted(level_counts.items()):
                lines.append(f"  {level}: {count}")
        
        return "\n".join(lines)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Obter resumo de erros"""
        error_entries = [entry for entry in self.log_entries if entry.level in ['ERROR', 'CRITICAL']]
        
        error_types = {}
        for entry in error_entries:
            if entry.error_details:
                error_type = entry.error_details.get('type', 'Unknown')
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': len(error_entries),
            'error_types': error_types,
            'recent_errors': [entry.to_dict() for entry in error_entries[-10:]]
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obter resumo de performance"""
        return {
            'session_duration': (datetime.now() - self.session_start).total_seconds(),
            'total_operations': sum(m['count'] for m in self.performance_metrics.values()),
            'slowest_operations': sorted(
                [(op, m['max_time']) for op, m in self.performance_metrics.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'most_frequent_operations': sorted(
                [(op, m['count']) for op, m in self.performance_metrics.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    def export_logs_to_csv(self, filename: Optional[str] = None) -> str:
        """Exportar logs para CSV"""
        import csv
        
        if not filename:
            filename = f"{self.name.lower()}_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        csv_path = self.log_dir / filename
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Cabeçalho
            writer.writerow([
                'Timestamp', 'Level', 'Module', 'Function', 'Message', 
                'Execution_Time', 'Memory_Usage', 'Has_Error_Details'
            ])
            
            # Dados
            for entry in self.log_entries:
                writer.writerow([
                    entry.timestamp.isoformat(),
                    entry.level,
                    entry.module,
                    entry.function,
                    entry.message,
                    entry.execution_time or '',
                    entry.memory_usage or '',
                    bool(entry.error_details)
                ])
        
        return str(csv_path)
    
    def cleanup_old_logs(self, days_to_keep: int = 7):
        """Limpar logs antigos"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for log_file in self.log_dir.glob("*.log"):
            try:
                if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                    log_file.unlink()
                    self.info(f"Log antigo removido: {log_file.name}")
            except Exception as e:
                self.warning(f"Erro ao remover log antigo {log_file.name}: {e}")
    
    def close(self):
        """Fechar logger e salvar dados finais"""
        # Salvar logs finais
        self.flush_to_json()
        
        # Gerar relatório final
        report = self.generate_session_report()
        report_file = self.log_dir / f"{self.name.lower()}_session_report.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.info(f"Sessão de logging finalizada. Relatório salvo em: {report_file}")
        
        # Fechar handlers
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)


# Instância global do logger
_global_logger: Optional[DetailedLogger] = None


def get_logger(name: str = "UltraSinger") -> DetailedLogger:
    """Obter instância global do logger"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = DetailedLogger(name)
    
    return _global_logger


def setup_logging(name: str = "UltraSinger", log_dir: str = "logs") -> DetailedLogger:
    """Configurar sistema de logging"""
    global _global_logger
    
    _global_logger = DetailedLogger(name, log_dir)
    return _global_logger


# Funções de conveniência
def log_info(message: str, data: Optional[Dict] = None):
    """Log de informação usando logger global"""
    get_logger().info(message, data)


def log_error(message: str, error: Optional[Exception] = None, data: Optional[Dict] = None):
    """Log de erro usando logger global"""
    get_logger().error(message, error, data)


def log_performance(message: str, execution_time: float, data: Optional[Dict] = None):
    """Log de performance usando logger global"""
    get_logger().performance(message, execution_time, data)


def log_export(message: str, format_type: str, file_path: str, success: bool, 
               file_size: int = 0, data: Optional[Dict] = None):
    """Log de exportação usando logger global"""
    get_logger().export_log(message, format_type, file_path, success, file_size, data)


def log_validation(message: str, file_path: str, is_valid: bool, 
                  errors: List[str] = None, warnings: List[str] = None, 
                  data: Optional[Dict] = None):
    """Log de validação usando logger global"""
    get_logger().validation_log(message, file_path, is_valid, errors, warnings, data)