"""
Sistema de Cache Avançado para UltraSinger
Fornece cache em memória e em disco para otimizar performance
"""

import os
import json
import pickle
import hashlib
import time
from typing import Any, Dict, Optional, Union, List
from pathlib import Path
from dataclasses import dataclass, asdict
from threading import Lock
import tempfile
import shutil

@dataclass
class CacheEntry:
    """Entrada do cache com metadados"""
    key: str
    value: Any
    timestamp: float
    ttl: Optional[float] = None
    size: int = 0
    access_count: int = 0
    last_access: float = 0.0
    
    def is_expired(self) -> bool:
        """Verifica se a entrada expirou"""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl
    
    def update_access(self):
        """Atualiza estatísticas de acesso"""
        self.access_count += 1
        self.last_access = time.time()

class MemoryCache:
    """Cache em memória com LRU e TTL"""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._access_order: List[str] = []
    
    def _generate_key(self, key: Union[str, Dict, List]) -> str:
        """Gera chave hash para objetos complexos"""
        if isinstance(key, str):
            return key
        
        # Converter para string JSON ordenada para consistência
        key_str = json.dumps(key, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _evict_expired(self):
        """Remove entradas expiradas"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            self._remove_key(key)
    
    def _evict_lru(self):
        """Remove entradas menos recentemente usadas"""
        while len(self._cache) >= self.max_size:
            if not self._access_order:
                break
            
            lru_key = self._access_order.pop(0)
            if lru_key in self._cache:
                self._remove_key(lru_key)
    
    def _remove_key(self, key: str):
        """Remove chave do cache e da ordem de acesso"""
        if key in self._cache:
            del self._cache[key]
        
        if key in self._access_order:
            self._access_order.remove(key)
    
    def _update_access_order(self, key: str):
        """Atualiza ordem de acesso (move para o final)"""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    def get(self, key: Union[str, Dict, List]) -> Optional[Any]:
        """Recupera valor do cache"""
        with self._lock:
            cache_key = self._generate_key(key)
            
            if cache_key not in self._cache:
                return None
            
            entry = self._cache[cache_key]
            
            # Verificar expiração
            if entry.is_expired():
                self._remove_key(cache_key)
                return None
            
            # Atualizar estatísticas
            entry.update_access()
            self._update_access_order(cache_key)
            
            return entry.value
    
    def set(self, key: Union[str, Dict, List], value: Any, ttl: Optional[float] = None) -> bool:
        """Armazena valor no cache"""
        with self._lock:
            cache_key = self._generate_key(key)
            
            # Limpar expirados
            self._evict_expired()
            
            # Verificar espaço
            if cache_key not in self._cache:
                self._evict_lru()
            
            # Calcular tamanho aproximado
            try:
                size = len(pickle.dumps(value))
            except:
                size = len(str(value))
            
            # Criar entrada
            entry = CacheEntry(
                key=cache_key,
                value=value,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl,
                size=size,
                access_count=1,
                last_access=time.time()
            )
            
            self._cache[cache_key] = entry
            self._update_access_order(cache_key)
            
            return True
    
    def delete(self, key: Union[str, Dict, List]) -> bool:
        """Remove valor do cache"""
        with self._lock:
            cache_key = self._generate_key(key)
            
            if cache_key in self._cache:
                self._remove_key(cache_key)
                return True
            
            return False
    
    def clear(self):
        """Limpa todo o cache"""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        with self._lock:
            total_size = sum(entry.size for entry in self._cache.values())
            total_accesses = sum(entry.access_count for entry in self._cache.values())
            
            return {
                'entries': len(self._cache),
                'max_size': self.max_size,
                'total_size_bytes': total_size,
                'total_accesses': total_accesses,
                'hit_ratio': 0.0  # Seria necessário rastrear misses para calcular
            }

class DiskCache:
    """Cache em disco para dados persistentes"""
    
    def __init__(self, cache_dir: Optional[str] = None, max_size_mb: int = 100):
        self.cache_dir = Path(cache_dir) if cache_dir else Path(tempfile.gettempdir()) / "ultrasingercache"
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self._lock = Lock()
        
        # Criar diretório se não existir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_filename(self, key: Union[str, Dict, List]) -> str:
        """Gera nome de arquivo seguro para a chave"""
        if isinstance(key, str):
            key_str = key
        else:
            key_str = json.dumps(key, sort_keys=True, default=str)
        
        # Hash para nome de arquivo seguro
        hash_key = hashlib.md5(key_str.encode()).hexdigest()
        return f"cache_{hash_key}.pkl"
    
    def _get_file_path(self, key: Union[str, Dict, List]) -> Path:
        """Retorna caminho completo do arquivo de cache"""
        filename = self._generate_filename(key)
        return self.cache_dir / filename
    
    def _cleanup_old_files(self):
        """Remove arquivos antigos se exceder limite de tamanho"""
        try:
            # Listar todos os arquivos de cache com timestamps
            cache_files = []
            total_size = 0
            
            for file_path in self.cache_dir.glob("cache_*.pkl"):
                if file_path.is_file():
                    stat = file_path.stat()
                    cache_files.append((file_path, stat.st_mtime, stat.st_size))
                    total_size += stat.st_size
            
            # Se exceder limite, remover arquivos mais antigos
            if total_size > self.max_size_bytes:
                # Ordenar por timestamp (mais antigos primeiro)
                cache_files.sort(key=lambda x: x[1])
                
                for file_path, _, size in cache_files:
                    if total_size <= self.max_size_bytes:
                        break
                    
                    try:
                        file_path.unlink()
                        total_size -= size
                    except:
                        pass
        
        except Exception:
            pass  # Ignorar erros de limpeza
    
    def get(self, key: Union[str, Dict, List]) -> Optional[Any]:
        """Recupera valor do cache em disco"""
        with self._lock:
            file_path = self._get_file_path(key)
            
            if not file_path.exists():
                return None
            
            try:
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                
                # Verificar expiração se houver TTL
                if isinstance(data, dict) and 'ttl' in data and 'timestamp' in data:
                    if data['ttl'] and time.time() - data['timestamp'] > data['ttl']:
                        file_path.unlink()
                        return None
                    return data.get('value')
                
                return data
            
            except Exception:
                # Se houver erro ao ler, remover arquivo corrompido
                try:
                    file_path.unlink()
                except:
                    pass
                return None
    
    def set(self, key: Union[str, Dict, List], value: Any, ttl: Optional[float] = None) -> bool:
        """Armazena valor no cache em disco"""
        with self._lock:
            try:
                file_path = self._get_file_path(key)
                
                # Preparar dados com metadados
                cache_data = {
                    'value': value,
                    'timestamp': time.time(),
                    'ttl': ttl
                }
                
                # Salvar no disco
                with open(file_path, 'wb') as f:
                    pickle.dump(cache_data, f)
                
                # Limpeza periódica
                self._cleanup_old_files()
                
                return True
            
            except Exception:
                return False
    
    def delete(self, key: Union[str, Dict, List]) -> bool:
        """Remove valor do cache em disco"""
        with self._lock:
            file_path = self._get_file_path(key)
            
            if file_path.exists():
                try:
                    file_path.unlink()
                    return True
                except:
                    pass
            
            return False
    
    def clear(self):
        """Limpa todo o cache em disco"""
        with self._lock:
            try:
                for file_path in self.cache_dir.glob("cache_*.pkl"):
                    try:
                        file_path.unlink()
                    except:
                        pass
            except:
                pass
    
    def stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache em disco"""
        with self._lock:
            try:
                files = list(self.cache_dir.glob("cache_*.pkl"))
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                
                return {
                    'entries': len(files),
                    'total_size_bytes': total_size,
                    'max_size_bytes': self.max_size_bytes,
                    'cache_dir': str(self.cache_dir)
                }
            except:
                return {
                    'entries': 0,
                    'total_size_bytes': 0,
                    'max_size_bytes': self.max_size_bytes,
                    'cache_dir': str(self.cache_dir)
                }

class CacheManager:
    """Gerenciador de cache híbrido (memória + disco)"""
    
    def __init__(self, 
                 memory_max_size: int = 1000,
                 memory_ttl: Optional[float] = 3600,  # 1 hora
                 disk_max_size_mb: int = 100,
                 disk_cache_dir: Optional[str] = None):
        
        self.memory_cache = MemoryCache(memory_max_size, memory_ttl)
        self.disk_cache = DiskCache(disk_cache_dir, disk_max_size_mb)
        self._stats = {
            'memory_hits': 0,
            'disk_hits': 0,
            'misses': 0,
            'sets': 0
        }
        self._lock = Lock()
    
    def get(self, key: Union[str, Dict, List], use_disk: bool = True) -> Optional[Any]:
        """Recupera valor do cache (memória primeiro, depois disco)"""
        with self._lock:
            # Tentar memória primeiro
            value = self.memory_cache.get(key)
            if value is not None:
                self._stats['memory_hits'] += 1
                return value
            
            # Tentar disco se habilitado
            if use_disk:
                value = self.disk_cache.get(key)
                if value is not None:
                    self._stats['disk_hits'] += 1
                    # Promover para memória
                    self.memory_cache.set(key, value)
                    return value
            
            self._stats['misses'] += 1
            return None
    
    def set(self, key: Union[str, Dict, List], value: Any, 
            ttl: Optional[float] = None, 
            memory_only: bool = False) -> bool:
        """Armazena valor no cache"""
        with self._lock:
            self._stats['sets'] += 1
            
            # Sempre armazenar em memória
            memory_success = self.memory_cache.set(key, value, ttl)
            
            # Armazenar em disco se não for memory_only
            disk_success = True
            if not memory_only:
                disk_success = self.disk_cache.set(key, value, ttl)
            
            return memory_success or disk_success
    
    def delete(self, key: Union[str, Dict, List]) -> bool:
        """Remove valor de ambos os caches"""
        with self._lock:
            memory_deleted = self.memory_cache.delete(key)
            disk_deleted = self.disk_cache.delete(key)
            return memory_deleted or disk_deleted
    
    def clear(self, memory_only: bool = False):
        """Limpa caches"""
        with self._lock:
            self.memory_cache.clear()
            if not memory_only:
                self.disk_cache.clear()
            
            # Reset stats
            self._stats = {
                'memory_hits': 0,
                'disk_hits': 0,
                'misses': 0,
                'sets': 0
            }
    
    def stats(self) -> Dict[str, Any]:
        """Retorna estatísticas completas"""
        with self._lock:
            memory_stats = self.memory_cache.stats()
            disk_stats = self.disk_cache.stats()
            
            total_hits = self._stats['memory_hits'] + self._stats['disk_hits']
            total_requests = total_hits + self._stats['misses']
            
            hit_ratio = total_hits / total_requests if total_requests > 0 else 0.0
            
            return {
                'memory': memory_stats,
                'disk': disk_stats,
                'performance': {
                    'memory_hits': self._stats['memory_hits'],
                    'disk_hits': self._stats['disk_hits'],
                    'misses': self._stats['misses'],
                    'sets': self._stats['sets'],
                    'hit_ratio': hit_ratio,
                    'total_requests': total_requests
                }
            }

# Instância global do cache manager
_cache_manager: Optional[CacheManager] = None

def get_cache_manager() -> CacheManager:
    """Retorna instância singleton do cache manager"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

def cache_result(key_prefix: str = "", ttl: Optional[float] = None, memory_only: bool = False):
    """Decorator para cache automático de resultados de função"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Gerar chave baseada na função e argumentos
            func_name = f"{func.__module__}.{func.__name__}"
            cache_key = {
                'function': func_name,
                'prefix': key_prefix,
                'args': args,
                'kwargs': kwargs
            }
            
            cache_manager = get_cache_manager()
            
            # Tentar recuperar do cache
            result = cache_manager.get(cache_key)
            if result is not None:
                return result
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl, memory_only)
            
            return result
        
        return wrapper
    return decorator

# Funções de conveniência
def cache_get(key: Union[str, Dict, List], use_disk: bool = True) -> Optional[Any]:
    """Função de conveniência para get"""
    return get_cache_manager().get(key, use_disk)

def cache_set(key: Union[str, Dict, List], value: Any, 
              ttl: Optional[float] = None, memory_only: bool = False) -> bool:
    """Função de conveniência para set"""
    return get_cache_manager().set(key, value, ttl, memory_only)

def cache_delete(key: Union[str, Dict, List]) -> bool:
    """Função de conveniência para delete"""
    return get_cache_manager().delete(key)

def cache_clear(memory_only: bool = False):
    """Função de conveniência para clear"""
    get_cache_manager().clear(memory_only)

def cache_stats() -> Dict[str, Any]:
    """Função de conveniência para stats"""
    return get_cache_manager().stats()