#!/usr/bin/env python3
"""
Sistema de validação e padronização de formatos de saída do UltraSinger
Suporta UltraStar.txt, MIDI, MusicXML, PDF e outros formatos
"""

import os
import re
import json
import mido
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from modules.console_colors import ULTRASINGER_HEAD, green_highlighted, red_highlighted, yellow_highlighted
from modules.error_handler import ErrorHandler


@dataclass
class ValidationResult:
    """Resultado da validação de um arquivo"""
    is_valid: bool
    file_type: str
    file_path: str
    file_size: int
    format_version: Optional[str] = None
    errors: List[str] = None
    warnings: List[str] = None
    suggestions: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.suggestions is None:
            self.suggestions = []
        if self.metadata is None:
            self.metadata = {}


class OutputValidator:
    """Validador principal para todos os formatos de saída"""
    
    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        self.error_handler = error_handler or ErrorHandler()
        self.validation_rules = self._load_validation_rules()
        
    def _load_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Carregar regras de validação para cada formato"""
        return {
            'ultrastar_txt': {
                'required_tags': ['#TITLE:', '#ARTIST:', '#MP3:', '#BPM:'],
                'optional_tags': ['#LANGUAGE:', '#GENRE:', '#YEAR:', '#CREATOR:', '#VERSION:'],
                'note_types': [':', '*', 'F', '-'],
                'max_line_length': 1000,
                'encoding': 'utf-8'
            },
            'midi': {
                'required_tracks': 1,
                'max_tracks': 16,
                'supported_formats': [0, 1, 2],
                'min_tempo': 60,
                'max_tempo': 300,
                'required_events': ['note_on', 'note_off']
            },
            'musicxml': {
                'required_elements': ['score-partwise', 'part-list', 'part'],
                'supported_versions': ['3.0', '3.1', '4.0'],
                'max_file_size_mb': 50
            },
            'pdf': {
                'min_pages': 1,
                'max_pages': 100,
                'max_file_size_mb': 20,
                'required_metadata': ['title', 'creator']
            }
        }
    
    def validate_file(self, file_path: str, expected_format: Optional[str] = None) -> ValidationResult:
        """Validar um arquivo de saída"""
        if not os.path.exists(file_path):
            return ValidationResult(
                is_valid=False,
                file_type='unknown',
                file_path=file_path,
                file_size=0,
                errors=[f"Arquivo não encontrado: {file_path}"]
            )
        
        file_size = os.path.getsize(file_path)
        file_ext = Path(file_path).suffix.lower()
        
        # Detectar formato automaticamente se não especificado
        if not expected_format:
            expected_format = self._detect_format(file_path, file_ext)
        
        # Validar baseado no formato
        if expected_format == 'ultrastar_txt':
            return self._validate_ultrastar_txt(file_path, file_size)
        elif expected_format == 'midi':
            return self._validate_midi(file_path, file_size)
        elif expected_format == 'musicxml':
            return self._validate_musicxml(file_path, file_size)
        elif expected_format == 'pdf':
            return self._validate_pdf(file_path, file_size)
        elif expected_format == 'json':
            return self._validate_json(file_path, file_size)
        else:
            return ValidationResult(
                is_valid=False,
                file_type=expected_format or 'unknown',
                file_path=file_path,
                file_size=file_size,
                errors=[f"Formato não suportado: {expected_format}"]
            )
    
    def _detect_format(self, file_path: str, file_ext: str) -> str:
        """Detectar formato do arquivo baseado na extensão e conteúdo"""
        format_map = {
            '.txt': 'ultrastar_txt',
            '.mid': 'midi',
            '.midi': 'midi',
            '.musicxml': 'musicxml',
            '.xml': 'musicxml',
            '.pdf': 'pdf',
            '.json': 'json',
            '.csv': 'csv'
        }
        
        detected_format = format_map.get(file_ext, 'unknown')
        
        # Verificação adicional para .txt (pode ser UltraStar ou texto simples)
        if file_ext == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # Ler apenas o início
                    if any(tag in content for tag in ['#TITLE:', '#ARTIST:', '#BPM:']):
                        detected_format = 'ultrastar_txt'
                    else:
                        detected_format = 'lyrics_txt'
            except:
                detected_format = 'unknown'
        
        return detected_format
    
    def _validate_ultrastar_txt(self, file_path: str, file_size: int) -> ValidationResult:
        """Validar arquivo UltraStar.txt"""
        result = ValidationResult(
            is_valid=True,
            file_type='ultrastar_txt',
            file_path=file_path,
            file_size=file_size
        )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            rules = self.validation_rules['ultrastar_txt']
            
            # Verificar tags obrigatórias
            found_tags = {}
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    tag = line.split(':')[0] + ':'
                    if tag in rules['required_tags']:
                        found_tags[tag] = line.split(':', 1)[1].strip()
            
            # Verificar tags faltantes
            missing_tags = [tag for tag in rules['required_tags'] if tag not in found_tags]
            if missing_tags:
                result.errors.extend([f"Tag obrigatória faltante: {tag}" for tag in missing_tags])
                result.is_valid = False
            
            # Validar BPM
            if '#BPM:' in found_tags:
                try:
                    bpm = float(found_tags['#BPM:'].replace(',', '.'))
                    if bpm <= 0 or bpm > 500:
                        result.warnings.append(f"BPM suspeito: {bpm}")
                except ValueError:
                    result.errors.append("BPM inválido")
                    result.is_valid = False
            
            # Validar notas
            note_lines = [line for line in lines if line and not line.startswith('#') and line != 'E']
            if not note_lines:
                result.warnings.append("Nenhuma nota encontrada")
            
            # Verificar formato das notas
            for i, line in enumerate(note_lines, 1):
                if not self._validate_note_line(line):
                    result.errors.append(f"Formato de nota inválido na linha {i}: {line[:50]}")
                    result.is_valid = False
            
            # Verificar se termina com 'E'
            if lines and lines[-1].strip() != 'E':
                result.warnings.append("Arquivo não termina com 'E'")
            
            # Metadados
            result.metadata = {
                'tags_found': found_tags,
                'note_count': len(note_lines),
                'line_count': len(lines),
                'encoding': 'utf-8'
            }
            
        except UnicodeDecodeError:
            result.errors.append("Erro de codificação - arquivo deve estar em UTF-8")
            result.is_valid = False
        except Exception as e:
            result.errors.append(f"Erro ao validar arquivo: {str(e)}")
            result.is_valid = False
        
        return result
    
    def _validate_note_line(self, line: str) -> bool:
        """Validar formato de uma linha de nota UltraStar"""
        # Formato: TIPO INICIO DURACAO PITCH TEXTO
        # Exemplo: : 0 4 60 Hello
        parts = line.split(' ', 4)
        
        if len(parts) < 4:
            return False
        
        note_type, start, duration, pitch = parts[:4]
        
        # Verificar tipo de nota
        if note_type not in [':', '*', 'F', '-']:
            return False
        
        # Verificar se start, duration e pitch são números
        try:
            int(start)
            int(duration)
            int(pitch)
        except ValueError:
            return False
        
        return True
    
    def _validate_midi(self, file_path: str, file_size: int) -> ValidationResult:
        """Validar arquivo MIDI"""
        result = ValidationResult(
            is_valid=True,
            file_type='midi',
            file_path=file_path,
            file_size=file_size
        )
        
        try:
            mid = mido.MidiFile(file_path)
            rules = self.validation_rules['midi']
            
            # Verificar formato MIDI
            if mid.type not in rules['supported_formats']:
                result.warnings.append(f"Formato MIDI não padrão: {mid.type}")
            
            # Verificar número de tracks
            if len(mid.tracks) < rules['required_tracks']:
                result.errors.append(f"Muito poucas tracks: {len(mid.tracks)}")
                result.is_valid = False
            elif len(mid.tracks) > rules['max_tracks']:
                result.warnings.append(f"Muitas tracks: {len(mid.tracks)}")
            
            # Verificar se há notas
            has_notes = False
            total_notes = 0
            
            for track in mid.tracks:
                for msg in track:
                    if msg.type in ['note_on', 'note_off']:
                        has_notes = True
                        if msg.type == 'note_on' and msg.velocity > 0:
                            total_notes += 1
            
            if not has_notes:
                result.errors.append("Nenhuma nota encontrada no arquivo MIDI")
                result.is_valid = False
            
            # Metadados
            result.metadata = {
                'format': mid.type,
                'tracks': len(mid.tracks),
                'ticks_per_beat': mid.ticks_per_beat,
                'length_seconds': mid.length,
                'total_notes': total_notes
            }
            
        except Exception as e:
            result.errors.append(f"Erro ao validar MIDI: {str(e)}")
            result.is_valid = False
        
        return result
    
    def _validate_musicxml(self, file_path: str, file_size: int) -> ValidationResult:
        """Validar arquivo MusicXML"""
        result = ValidationResult(
            is_valid=True,
            file_type='musicxml',
            file_path=file_path,
            file_size=file_size
        )
        
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Verificar elementos obrigatórios
            rules = self.validation_rules['musicxml']
            
            if root.tag not in ['score-partwise', 'score-timewise']:
                result.errors.append("Elemento raiz inválido para MusicXML")
                result.is_valid = False
            
            # Verificar part-list
            part_list = root.find('part-list')
            if part_list is None:
                result.errors.append("Elemento 'part-list' não encontrado")
                result.is_valid = False
            
            # Verificar parts
            parts = root.findall('part')
            if not parts:
                result.errors.append("Nenhuma parte musical encontrada")
                result.is_valid = False
            
            # Verificar tamanho do arquivo
            if file_size > rules['max_file_size_mb'] * 1024 * 1024:
                result.warnings.append(f"Arquivo muito grande: {file_size / (1024*1024):.1f}MB")
            
            # Metadados
            result.metadata = {
                'root_element': root.tag,
                'parts_count': len(parts),
                'file_size_mb': file_size / (1024 * 1024)
            }
            
        except ET.ParseError as e:
            result.errors.append(f"XML inválido: {str(e)}")
            result.is_valid = False
        except Exception as e:
            result.errors.append(f"Erro ao validar MusicXML: {str(e)}")
            result.is_valid = False
        
        return result
    
    def _validate_pdf(self, file_path: str, file_size: int) -> ValidationResult:
        """Validar arquivo PDF"""
        result = ValidationResult(
            is_valid=True,
            file_type='pdf',
            file_path=file_path,
            file_size=file_size
        )
        
        try:
            # Verificação básica de cabeçalho PDF
            with open(file_path, 'rb') as f:
                header = f.read(8)
                if not header.startswith(b'%PDF-'):
                    result.errors.append("Arquivo não é um PDF válido")
                    result.is_valid = False
                    return result
            
            rules = self.validation_rules['pdf']
            
            # Verificar tamanho do arquivo
            if file_size > rules['max_file_size_mb'] * 1024 * 1024:
                result.warnings.append(f"Arquivo PDF muito grande: {file_size / (1024*1024):.1f}MB")
            
            # Metadados básicos
            result.metadata = {
                'file_size_mb': file_size / (1024 * 1024),
                'pdf_version': header.decode('ascii', errors='ignore')
            }
            
        except Exception as e:
            result.errors.append(f"Erro ao validar PDF: {str(e)}")
            result.is_valid = False
        
        return result
    
    def _validate_json(self, file_path: str, file_size: int) -> ValidationResult:
        """Validar arquivo JSON"""
        result = ValidationResult(
            is_valid=True,
            file_type='json',
            file_path=file_path,
            file_size=file_size
        )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Verificar se é um objeto válido
            if not isinstance(data, (dict, list)):
                result.warnings.append("JSON não contém objeto ou array")
            
            # Metadados
            result.metadata = {
                'data_type': type(data).__name__,
                'keys_count': len(data) if isinstance(data, (dict, list)) else 0
            }
            
        except json.JSONDecodeError as e:
            result.errors.append(f"JSON inválido: {str(e)}")
            result.is_valid = False
        except Exception as e:
            result.errors.append(f"Erro ao validar JSON: {str(e)}")
            result.is_valid = False
        
        return result
    
    def validate_batch(self, file_paths: List[str]) -> Dict[str, ValidationResult]:
        """Validar múltiplos arquivos"""
        results = {}
        
        for file_path in file_paths:
            try:
                results[file_path] = self.validate_file(file_path)
            except Exception as e:
                results[file_path] = ValidationResult(
                    is_valid=False,
                    file_type='unknown',
                    file_path=file_path,
                    file_size=0,
                    errors=[f"Erro na validação: {str(e)}"]
                )
        
        return results
    
    def generate_validation_report(self, results: Dict[str, ValidationResult]) -> str:
        """Gerar relatório de validação"""
        report_lines = [
            f"{ULTRASINGER_HEAD} RELATÓRIO DE VALIDAÇÃO DE ARQUIVOS",
            "=" * 60,
            f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Arquivos validados: {len(results)}",
            ""
        ]
        
        valid_count = sum(1 for r in results.values() if r.is_valid)
        invalid_count = len(results) - valid_count
        
        report_lines.extend([
            f"✅ Arquivos válidos: {green_highlighted(str(valid_count))}",
            f"❌ Arquivos inválidos: {red_highlighted(str(invalid_count))}",
            ""
        ])
        
        # Detalhes por arquivo
        for file_path, result in results.items():
            status = "✅ VÁLIDO" if result.is_valid else "❌ INVÁLIDO"
            report_lines.append(f"{status} - {Path(file_path).name} ({result.file_type})")
            
            if result.errors:
                for error in result.errors:
                    report_lines.append(f"  ❌ {error}")
            
            if result.warnings:
                for warning in result.warnings:
                    report_lines.append(f"  ⚠️ {warning}")
            
            if result.suggestions:
                for suggestion in result.suggestions:
                    report_lines.append(f"  💡 {suggestion}")
            
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def get_format_standards(self, format_type: str) -> Dict[str, Any]:
        """Obter padrões e regras para um formato específico"""
        return self.validation_rules.get(format_type, {})
    
    def suggest_fixes(self, result: ValidationResult) -> List[str]:
        """Sugerir correções para problemas encontrados"""
        suggestions = []
        
        if result.file_type == 'ultrastar_txt':
            for error in result.errors:
                if 'Tag obrigatória faltante' in error:
                    tag = error.split(':')[-1].strip()
                    suggestions.append(f"Adicionar tag {tag} no início do arquivo")
                elif 'BPM inválido' in error:
                    suggestions.append("Verificar e corrigir o valor do BPM (deve ser um número positivo)")
                elif 'Formato de nota inválido' in error:
                    suggestions.append("Verificar formato das notas: TIPO INICIO DURACAO PITCH TEXTO")
        
        elif result.file_type == 'midi':
            for error in result.errors:
                if 'Nenhuma nota encontrada' in error:
                    suggestions.append("Adicionar eventos de nota (note_on/note_off) ao arquivo MIDI")
                elif 'Muito poucas tracks' in error:
                    suggestions.append("Adicionar pelo menos uma track com dados musicais")
        
        return suggestions