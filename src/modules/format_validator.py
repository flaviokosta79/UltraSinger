"""
Sistema abrangente de validação e conversão de formatos de entrada
Suporta múltiplos formatos de áudio e validação robusta
"""

import os
import re
import mimetypes
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from urllib.parse import urlparse
import subprocess
import json

from modules.console_colors import ULTRASINGER_HEAD, red_highlighted, green_highlighted, blue_highlighted
from modules.error_handler import ErrorHandler, ErrorCategory, ErrorSeverity


class FormatValidator:
    """Validador abrangente de formatos de entrada"""
    
    # Formatos de áudio suportados com suas características
    SUPPORTED_AUDIO_FORMATS = {
        '.mp3': {
            'mime_type': 'audio/mpeg',
            'quality': 'lossy',
            'max_bitrate': 320,
            'common_bitrates': [128, 192, 256, 320],
            'description': 'MPEG Audio Layer III'
        },
        '.wav': {
            'mime_type': 'audio/wav',
            'quality': 'lossless',
            'max_bitrate': None,
            'common_bitrates': [1411],  # CD quality
            'description': 'Waveform Audio File Format'
        },
        '.flac': {
            'mime_type': 'audio/flac',
            'quality': 'lossless',
            'max_bitrate': None,
            'common_bitrates': [1000, 1411],
            'description': 'Free Lossless Audio Codec'
        },
        '.m4a': {
            'mime_type': 'audio/mp4',
            'quality': 'lossy',
            'max_bitrate': 256,
            'common_bitrates': [128, 192, 256],
            'description': 'MPEG-4 Audio'
        },
        '.ogg': {
            'mime_type': 'audio/ogg',
            'quality': 'lossy',
            'max_bitrate': 500,
            'common_bitrates': [128, 192, 256],
            'description': 'Ogg Vorbis'
        },
        '.aac': {
            'mime_type': 'audio/aac',
            'quality': 'lossy',
            'max_bitrate': 320,
            'common_bitrates': [128, 192, 256],
            'description': 'Advanced Audio Coding'
        },
        '.wma': {
            'mime_type': 'audio/x-ms-wma',
            'quality': 'lossy',
            'max_bitrate': 320,
            'common_bitrates': [128, 192, 256],
            'description': 'Windows Media Audio'
        }
    }
    
    # Padrões de URL do YouTube
    YOUTUBE_URL_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]+)'
    ]
    
    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        self.error_handler = error_handler or ErrorHandler()
        
    def validate_input_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validação abrangente de arquivo de entrada
        
        Returns:
            Dict com informações de validação:
            - is_valid: bool
            - file_type: str ('audio', 'ultrastar', 'youtube_url')
            - format_info: dict
            - errors: list
            - suggestions: list
        """
        result = {
            'is_valid': False,
            'file_type': None,
            'format_info': {},
            'errors': [],
            'suggestions': []
        }
        
        try:
            # Verificar se é URL do YouTube
            if self._is_youtube_url(file_path):
                result.update(self._validate_youtube_url(file_path))
                return result
            
            # Verificar se é arquivo UltraStar.txt
            if file_path.lower().endswith('.txt'):
                result.update(self._validate_ultrastar_file(file_path))
                return result
            
            # Verificar se é arquivo de áudio
            result.update(self._validate_audio_file(file_path))
            return result
            
        except Exception as e:
            self.error_handler.handle_error(
                e, 
                ErrorCategory.VALIDATION,
                ErrorSeverity.MEDIUM,
                "FormatValidator"
            )
            result['errors'].append(f"Erro na validação: {str(e)}")
            
        return result
    
    def _is_youtube_url(self, url: str) -> bool:
        """Verificar se é URL do YouTube"""
        for pattern in self.YOUTUBE_URL_PATTERNS:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def _validate_youtube_url(self, url: str) -> Dict[str, Any]:
        """Validar URL do YouTube"""
        result = {
            'is_valid': False,
            'file_type': 'youtube_url',
            'format_info': {'url': url},
            'errors': [],
            'suggestions': []
        }
        
        # Extrair ID do vídeo
        video_id = None
        for pattern in self.YOUTUBE_URL_PATTERNS:
            match = re.match(pattern, url, re.IGNORECASE)
            if match:
                video_id = match.group(1)
                break
        
        if video_id:
            result['is_valid'] = True
            result['format_info']['video_id'] = video_id
            result['format_info']['description'] = 'YouTube Video URL'
        else:
            result['errors'].append("URL do YouTube inválida")
            result['suggestions'].append("Verifique se a URL está no formato correto")
            
        return result
    
    def _validate_ultrastar_file(self, file_path: str) -> Dict[str, Any]:
        """Validar arquivo UltraStar.txt"""
        result = {
            'is_valid': False,
            'file_type': 'ultrastar',
            'format_info': {},
            'errors': [],
            'suggestions': []
        }
        
        if not os.path.exists(file_path):
            result['errors'].append("Arquivo não encontrado")
            return result
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar tags obrigatórias
            required_tags = ['#TITLE:', '#ARTIST:', '#MP3:', '#BPM:']
            missing_tags = []
            
            for tag in required_tags:
                if tag not in content:
                    missing_tags.append(tag)
            
            if missing_tags:
                result['errors'].extend([f"Tag obrigatória ausente: {tag}" for tag in missing_tags])
            else:
                result['is_valid'] = True
                
            # Extrair informações do arquivo
            result['format_info'] = self._extract_ultrastar_info(content)
            
        except UnicodeDecodeError:
            result['errors'].append("Erro de codificação do arquivo")
            result['suggestions'].append("Verifique se o arquivo está em UTF-8")
        except Exception as e:
            result['errors'].append(f"Erro ao ler arquivo: {str(e)}")
            
        return result
    
    def _validate_audio_file(self, file_path: str) -> Dict[str, Any]:
        """Validar arquivo de áudio"""
        result = {
            'is_valid': False,
            'file_type': 'audio',
            'format_info': {},
            'errors': [],
            'suggestions': []
        }
        
        if not os.path.exists(file_path):
            result['errors'].append("Arquivo não encontrado")
            return result
        
        # Verificar extensão
        ext = Path(file_path).suffix.lower()
        if ext not in self.SUPPORTED_AUDIO_FORMATS:
            result['errors'].append(f"Formato não suportado: {ext}")
            result['suggestions'].append(f"Formatos suportados: {', '.join(self.SUPPORTED_AUDIO_FORMATS.keys())}")
            return result
        
        # Verificar se o arquivo não está vazio
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            result['errors'].append("Arquivo está vazio")
            return result
        
        # Verificar MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        expected_mime = self.SUPPORTED_AUDIO_FORMATS[ext]['mime_type']
        
        result['is_valid'] = True
        result['format_info'] = {
            'extension': ext,
            'file_size': file_size,
            'mime_type': mime_type,
            'expected_mime': expected_mime,
            'format_details': self.SUPPORTED_AUDIO_FORMATS[ext]
        }
        
        # Adicionar informações detalhadas do áudio se possível
        audio_info = self._get_audio_info(file_path)
        if audio_info:
            result['format_info'].update(audio_info)
        
        return result
    
    def _extract_ultrastar_info(self, content: str) -> Dict[str, Any]:
        """Extrair informações do arquivo UltraStar"""
        info = {}
        
        # Padrões para extrair tags
        tag_patterns = {
            'title': r'#TITLE:(.+)',
            'artist': r'#ARTIST:(.+)',
            'mp3': r'#MP3:(.+)',
            'bpm': r'#BPM:(.+)',
            'language': r'#LANGUAGE:(.+)',
            'genre': r'#GENRE:(.+)',
            'year': r'#YEAR:(.+)'
        }
        
        for key, pattern in tag_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                info[key] = match.group(1).strip()
        
        # Contar notas
        note_lines = re.findall(r'^[:\*F] ', content, re.MULTILINE)
        info['note_count'] = len(note_lines)
        
        return info
    
    def _get_audio_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Obter informações detalhadas do áudio usando ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                audio_stream = None
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'audio':
                        audio_stream = stream
                        break
                
                if audio_stream:
                    return {
                        'duration': float(data.get('format', {}).get('duration', 0)),
                        'bitrate': int(data.get('format', {}).get('bit_rate', 0)),
                        'sample_rate': int(audio_stream.get('sample_rate', 0)),
                        'channels': int(audio_stream.get('channels', 0)),
                        'codec': audio_stream.get('codec_name', 'unknown')
                    }
                    
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            # ffprobe não disponível ou erro na execução
            pass
        
        return None
    
    def get_supported_formats(self) -> Dict[str, Dict[str, Any]]:
        """Retornar formatos suportados com detalhes"""
        return self.SUPPORTED_AUDIO_FORMATS.copy()
    
    def suggest_format_conversion(self, current_format: str) -> List[str]:
        """Sugerir conversões de formato"""
        suggestions = []
        
        if current_format.lower() not in self.SUPPORTED_AUDIO_FORMATS:
            suggestions.append("Converter para MP3 (mais compatível)")
            suggestions.append("Converter para WAV (melhor qualidade)")
            suggestions.append("Converter para FLAC (lossless)")
        
        return suggestions
    
    def validate_batch_files(self, file_paths: List[str]) -> Dict[str, Dict[str, Any]]:
        """Validar múltiplos arquivos em lote"""
        results = {}
        
        for file_path in file_paths:
            results[file_path] = self.validate_input_file(file_path)
        
        return results
    
    def get_format_statistics(self, file_paths: List[str]) -> Dict[str, Any]:
        """Obter estatísticas dos formatos dos arquivos"""
        stats = {
            'total_files': len(file_paths),
            'valid_files': 0,
            'invalid_files': 0,
            'format_distribution': {},
            'file_types': {'audio': 0, 'ultrastar': 0, 'youtube_url': 0},
            'total_size': 0,
            'average_size': 0
        }
        
        sizes = []
        
        for file_path in file_paths:
            result = self.validate_input_file(file_path)
            
            if result['is_valid']:
                stats['valid_files'] += 1
                
                file_type = result['file_type']
                stats['file_types'][file_type] += 1
                
                if file_type == 'audio':
                    ext = result['format_info'].get('extension', 'unknown')
                    stats['format_distribution'][ext] = stats['format_distribution'].get(ext, 0) + 1
                    
                    file_size = result['format_info'].get('file_size', 0)
                    sizes.append(file_size)
                    stats['total_size'] += file_size
            else:
                stats['invalid_files'] += 1
        
        if sizes:
            stats['average_size'] = sum(sizes) / len(sizes)
        
        return stats


class FormatConverter:
    """Conversor de formatos de áudio"""
    
    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        self.error_handler = error_handler or ErrorHandler()
    
    def convert_to_supported_format(self, input_file: str, output_file: str, 
                                  target_format: str = 'mp3', 
                                  quality: str = 'high') -> bool:
        """
        Converter arquivo para formato suportado
        
        Args:
            input_file: Arquivo de entrada
            output_file: Arquivo de saída
            target_format: Formato alvo (mp3, wav, flac)
            quality: Qualidade (low, medium, high, lossless)
        """
        try:
            # Configurações de qualidade
            quality_settings = {
                'mp3': {
                    'low': ['-b:a', '128k'],
                    'medium': ['-b:a', '192k'],
                    'high': ['-b:a', '320k'],
                    'lossless': ['-b:a', '320k']  # MP3 não é lossless
                },
                'wav': {
                    'low': ['-ar', '22050'],
                    'medium': ['-ar', '44100'],
                    'high': ['-ar', '48000'],
                    'lossless': ['-ar', '48000', '-sample_fmt', 's32']
                },
                'flac': {
                    'low': ['-compression_level', '0'],
                    'medium': ['-compression_level', '5'],
                    'high': ['-compression_level', '8'],
                    'lossless': ['-compression_level', '12']
                }
            }
            
            # Construir comando ffmpeg
            cmd = ['ffmpeg', '-i', input_file, '-y']
            
            if target_format in quality_settings and quality in quality_settings[target_format]:
                cmd.extend(quality_settings[target_format][quality])
            
            cmd.append(output_file)
            
            # Executar conversão
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"{ULTRASINGER_HEAD} {green_highlighted('Conversão concluída:')} {output_file}")
                return True
            else:
                print(f"{ULTRASINGER_HEAD} {red_highlighted('Erro na conversão:')} {result.stderr}")
                return False
                
        except Exception as e:
            self.error_handler.handle_error(
                e,
                ErrorCategory.FILE_IO,
                ErrorSeverity.HIGH,
                "FormatConverter"
            )
            return False
    
    def is_ffmpeg_available(self) -> bool:
        """Verificar se ffmpeg está disponível"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=10)
            return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_ffmpeg_version(self) -> Optional[str]:
        """Obter versão do ffmpeg"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Extrair versão da primeira linha
                first_line = result.stdout.split('\n')[0]
                version_match = re.search(r'ffmpeg version ([^\s]+)', first_line)
                if version_match:
                    return version_match.group(1)
            return None
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def detect_audio_format(self, file_path: str) -> Optional[str]:
        """Detectar formato de áudio do arquivo"""
        if not os.path.exists(file_path):
            return None
        
        # Primeiro, tentar pela extensão
        ext = Path(file_path).suffix.lower()
        if ext:
            return ext
        
        # Se não há extensão, tentar detectar pelo conteúdo
        try:
            with open(file_path, 'rb') as f:
                header = f.read(12)
            
            # Verificar assinaturas de arquivo
            if header.startswith(b'RIFF') and b'WAVE' in header:
                return '.wav'
            elif header.startswith(b'ID3') or header[0:2] == b'\xff\xfb':
                return '.mp3'
            elif header.startswith(b'fLaC'):
                return '.flac'
            elif header.startswith(b'OggS'):
                return '.ogg'
            elif header[4:8] == b'ftyp':
                return '.m4a'
        except:
            pass
        
        return None
    
    def is_format_supported(self, format_ext: str) -> bool:
        """Verificar se formato é suportado"""
        validator = FormatValidator()
        supported_formats = validator.get_supported_formats()
        return format_ext.lower() in supported_formats
    
    def suggest_conversion_format(self, input_format: str) -> List[str]:
        """Sugerir formatos de conversão"""
        suggestions = []
        
        if not self.is_format_supported(input_format):
            # Formatos mais comuns primeiro
            suggestions.extend(['.mp3', '.wav', '.flac'])
        else:
            # Se já é suportado, sugerir alternativas
            if input_format.lower() == '.wav':
                suggestions.extend(['.mp3', '.flac'])
            elif input_format.lower() == '.mp3':
                suggestions.extend(['.wav', '.flac'])
            else:
                suggestions.extend(['.mp3', '.wav'])
        
        return suggestions
    
    def plan_conversion(self, source_format: str, target_format: str) -> Optional[Dict[str, Any]]:
        """Planejar conversão entre formatos"""
        if not self.is_ffmpeg_available():
            return None
        
        plan = {
            'source_format': source_format,
            'target_format': target_format,
            'quality': 'medium',
            'parameters': [],
            'estimated_time': 'unknown',
            'estimated_size_ratio': 1.0
        }
        
        # Definir qualidade baseada no formato alvo
        if target_format.lower() == '.flac':
            plan['quality'] = 'lossless'
            plan['estimated_size_ratio'] = 1.5
        elif target_format.lower() == '.wav':
            plan['quality'] = 'lossless'
            plan['estimated_size_ratio'] = 10.0
        elif target_format.lower() == '.mp3':
            plan['quality'] = 'high'
            plan['estimated_size_ratio'] = 0.1
        
        # Definir parâmetros
        plan['parameters'] = self.get_quality_parameters(target_format, plan['quality'])
        
        return plan
    
    def get_quality_parameters(self, format_ext: str, quality: str) -> Dict[str, Any]:
        """Obter parâmetros de qualidade para formato"""
        quality_settings = {
            '.mp3': {
                'low': {'bitrate': '128k', 'vbr': False},
                'medium': {'bitrate': '192k', 'vbr': False},
                'high': {'bitrate': '320k', 'vbr': False},
                'lossless': {'bitrate': '320k', 'vbr': False}
            },
            '.wav': {
                'low': {'sample_rate': '22050', 'bit_depth': '16'},
                'medium': {'sample_rate': '44100', 'bit_depth': '16'},
                'high': {'sample_rate': '48000', 'bit_depth': '24'},
                'lossless': {'sample_rate': '48000', 'bit_depth': '32'}
            },
            '.flac': {
                'low': {'compression': '0', 'sample_rate': '44100'},
                'medium': {'compression': '5', 'sample_rate': '44100'},
                'high': {'compression': '8', 'sample_rate': '48000'},
                'lossless': {'compression': '12', 'sample_rate': '48000'}
            }
        }
        
        format_key = format_ext.lower()
        if format_key in quality_settings and quality in quality_settings[format_key]:
            return quality_settings[format_key][quality]
        
        return {}
    
    def get_lossless_formats(self) -> List[str]:
        """Obter lista de formatos lossless"""
        return ['.wav', '.flac', '.aiff']
    
    def can_preserve_metadata(self, source_format: str, target_format: str) -> bool:
        """Verificar se metadados podem ser preservados na conversão"""
        # Formatos que suportam metadados
        metadata_formats = {'.mp3', '.flac', '.m4a', '.ogg'}
        
        source_lower = source_format.lower()
        target_lower = target_format.lower()
        
        return source_lower in metadata_formats and target_lower in metadata_formats
    
    def build_conversion_command(self, input_file: str, output_file: str, 
                               quality: str, metadata: Optional[Dict[str, str]] = None) -> Optional[List[str]]:
        """Construir comando de conversão com metadados"""
        if not self.is_ffmpeg_available():
            return None
        
        cmd = ['ffmpeg', '-i', input_file, '-y']
        
        # Adicionar parâmetros de qualidade
        target_ext = Path(output_file).suffix.lower()
        quality_params = self.get_quality_parameters(target_ext, quality)
        
        if target_ext == '.mp3':
            if 'bitrate' in quality_params:
                cmd.extend(['-b:a', quality_params['bitrate']])
        elif target_ext == '.wav':
            if 'sample_rate' in quality_params:
                cmd.extend(['-ar', quality_params['sample_rate']])
        elif target_ext == '.flac':
            if 'compression' in quality_params:
                cmd.extend(['-compression_level', quality_params['compression']])
        
        # Adicionar metadados se fornecidos
        if metadata:
            metadata_map = {
                'title': 'title',
                'artist': 'artist',
                'album': 'album',
                'year': 'date',
                'genre': 'genre'
            }
            
            for key, value in metadata.items():
                if key in metadata_map and value:
                    cmd.extend(['-metadata', f'{metadata_map[key]}={value}'])
        
        cmd.append(output_file)
        return cmd
    
    def convert_batch_files(self, input_files: List[str], output_dir: str, 
                          target_format: str, quality: str = 'medium') -> List[Dict[str, Any]]:
        """Converter múltiplos arquivos em lote"""
        results = []
        
        os.makedirs(output_dir, exist_ok=True)
        
        for input_file in input_files:
            input_path = Path(input_file)
            output_file = os.path.join(output_dir, f"{input_path.stem}.{target_format}")
            
            result = {
                'input_file': input_file,
                'output_file': output_file,
                'success': False,
                'error': None
            }
            
            try:
                success = self.convert_to_supported_format(
                    input_file, output_file, target_format, quality
                )
                result['success'] = success
                
                if not success:
                    result['error'] = "Conversão falhou"
                    
            except Exception as e:
                result['error'] = str(e)
            
            results.append(result)
        
        return results