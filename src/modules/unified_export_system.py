#!/usr/bin/env python3
"""
Sistema Unificado de Exportação do UltraSinger
Gerencia a exportação para múltiplos formatos com configurações personalizáveis
"""

import os
import json
import mido
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from modules.console_colors import ULTRASINGER_HEAD, green_highlighted, red_highlighted, yellow_highlighted
from modules.error_handler import ErrorHandler
from modules.output_validator import OutputValidator, ValidationResult
from modules.cache_system import cache_result, get_cache_manager


@dataclass
class ExportConfig:
    """Configuração de exportação"""
    output_dir: str
    filename_base: str
    formats: List[str]
    overwrite_existing: bool = False
    validate_output: bool = True
    create_backup: bool = False
    parallel_export: bool = True
    max_workers: int = 4
    
    # Configurações específicas por formato
    ultrastar_config: Dict[str, Any] = None
    midi_config: Dict[str, Any] = None
    musicxml_config: Dict[str, Any] = None
    pdf_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.ultrastar_config is None:
            self.ultrastar_config = {
                'encoding': 'utf-8',
                'add_timestamps': True,
                'normalize_pitch': True,
                'add_creator_tag': True
            }
        
        if self.midi_config is None:
            self.midi_config = {
                'format': 1,
                'ticks_per_beat': 480,
                'tempo': 120,
                'channel': 0,
                'velocity': 80
            }
        
        if self.musicxml_config is None:
            self.musicxml_config = {
                'version': '3.1',
                'divisions': 480,
                'key_signature': 'C',
                'time_signature': '4/4'
            }
        
        if self.pdf_config is None:
            self.pdf_config = {
                'page_size': 'A4',
                'font_size': 12,
                'include_chords': True,
                'include_lyrics': True
            }


@dataclass
class ExportResult:
    """Resultado de uma exportação"""
    format_type: str
    file_path: str
    success: bool
    file_size: int = 0
    export_time: float = 0.0
    validation_result: Optional[ValidationResult] = None
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class UnifiedExportSystem:
    """Sistema unificado para exportação de múltiplos formatos"""
    
    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        self.error_handler = error_handler or ErrorHandler()
        self.validator = OutputValidator(error_handler)
        self.cache_manager = get_cache_manager()
        
        # Mapeamento de formatos para métodos de exportação
        self.export_methods = {
            'ultrastar_txt': self._export_ultrastar_txt,
            'midi': self._export_midi,
            'musicxml': self._export_musicxml,
            'pdf': self._export_pdf,
            'json': self._export_json,
            'csv': self._export_csv,
            'lyrics_txt': self._export_lyrics_txt
        }
        
        # Extensões de arquivo por formato
        self.file_extensions = {
            'ultrastar_txt': '.txt',
            'midi': '.mid',
            'musicxml': '.musicxml',
            'pdf': '.pdf',
            'json': '.json',
            'csv': '.csv',
            'lyrics_txt': '_lyrics.txt'
        }
    
    def export_all_formats(self, song_data: Dict[str, Any], config: ExportConfig) -> Dict[str, ExportResult]:
        """Exportar para todos os formatos especificados"""
        print(f"{ULTRASINGER_HEAD} Iniciando exportação unificada...")
        print(f"Formatos: {', '.join(config.formats)}")
        print(f"Diretório de saída: {config.output_dir}")
        
        # Criar diretório de saída se não existir
        os.makedirs(config.output_dir, exist_ok=True)
        
        results = {}
        
        if config.parallel_export and len(config.formats) > 1:
            results = self._export_parallel(song_data, config)
        else:
            results = self._export_sequential(song_data, config)
        
        # Gerar relatório de exportação
        self._generate_export_report(results, config)
        
        return results
    
    def _export_sequential(self, song_data: Dict[str, Any], config: ExportConfig) -> Dict[str, ExportResult]:
        """Exportação sequencial"""
        results = {}
        
        for format_type in config.formats:
            print(f"Exportando para {format_type}...")
            
            try:
                result = self._export_single_format(song_data, format_type, config)
                results[format_type] = result
                
                if result.success:
                    print(f"✅ {format_type}: {green_highlighted('Sucesso')}")
                else:
                    print(f"❌ {format_type}: {red_highlighted('Falhou')} - {result.error_message}")
                    
            except Exception as e:
                results[format_type] = ExportResult(
                    format_type=format_type,
                    file_path="",
                    success=False,
                    error_message=str(e)
                )
                print(f"❌ {format_type}: {red_highlighted('Erro')} - {str(e)}")
        
        return results
    
    def _export_parallel(self, song_data: Dict[str, Any], config: ExportConfig) -> Dict[str, ExportResult]:
        """Exportação paralela"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            # Submeter tarefas
            future_to_format = {
                executor.submit(self._export_single_format, song_data, fmt, config): fmt
                for fmt in config.formats
            }
            
            # Coletar resultados
            for future in as_completed(future_to_format):
                format_type = future_to_format[future]
                
                try:
                    result = future.result()
                    results[format_type] = result
                    
                    if result.success:
                        print(f"✅ {format_type}: {green_highlighted('Sucesso')}")
                    else:
                        print(f"❌ {format_type}: {red_highlighted('Falhou')} - {result.error_message}")
                        
                except Exception as e:
                    results[format_type] = ExportResult(
                        format_type=format_type,
                        file_path="",
                        success=False,
                        error_message=str(e)
                    )
                    print(f"❌ {format_type}: {red_highlighted('Erro')} - {str(e)}")
        
        return results
    
    def _export_single_format(self, song_data: Dict[str, Any], format_type: str, config: ExportConfig) -> ExportResult:
        """Exportar para um formato específico"""
        start_time = datetime.now()
        
        # Verificar se o método de exportação existe
        if format_type not in self.export_methods:
            return ExportResult(
                format_type=format_type,
                file_path="",
                success=False,
                error_message=f"Formato não suportado: {format_type}"
            )
        
        # Gerar caminho do arquivo
        extension = self.file_extensions.get(format_type, f'.{format_type}')
        file_path = os.path.join(config.output_dir, f"{config.filename_base}{extension}")
        
        # Verificar se arquivo já existe
        if os.path.exists(file_path) and not config.overwrite_existing:
            return ExportResult(
                format_type=format_type,
                file_path=file_path,
                success=False,
                error_message="Arquivo já existe e overwrite_existing=False"
            )
        
        # Criar backup se solicitado
        if config.create_backup and os.path.exists(file_path):
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(file_path, backup_path)
        
        try:
            # Executar exportação
            export_method = self.export_methods[format_type]
            export_method(song_data, file_path, config)
            
            # Calcular tempo de exportação
            export_time = (datetime.now() - start_time).total_seconds()
            
            # Obter tamanho do arquivo
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            # Validar arquivo se solicitado
            validation_result = None
            if config.validate_output:
                validation_result = self.validator.validate_file(file_path, format_type)
            
            return ExportResult(
                format_type=format_type,
                file_path=file_path,
                success=True,
                file_size=file_size,
                export_time=export_time,
                validation_result=validation_result
            )
            
        except Exception as e:
            return ExportResult(
                format_type=format_type,
                file_path=file_path,
                success=False,
                error_message=str(e),
                export_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _export_ultrastar_txt(self, song_data: Dict[str, Any], file_path: str, config: ExportConfig):
        """Exportar para formato UltraStar.txt"""
        ultrastar_config = config.ultrastar_config
        
        lines = []
        
        # Cabeçalho com tags obrigatórias
        lines.append(f"#TITLE:{song_data.get('title', 'Unknown Title')}")
        lines.append(f"#ARTIST:{song_data.get('artist', 'Unknown Artist')}")
        lines.append(f"#MP3:{song_data.get('audio_file', 'audio.mp3')}")
        lines.append(f"#BPM:{song_data.get('bpm', 120)}")
        
        # Tags opcionais
        if song_data.get('language'):
            lines.append(f"#LANGUAGE:{song_data['language']}")
        if song_data.get('genre'):
            lines.append(f"#GENRE:{song_data['genre']}")
        if song_data.get('year'):
            lines.append(f"#YEAR:{song_data['year']}")
        
        # Tag do criador se solicitado
        if ultrastar_config.get('add_creator_tag', True):
            lines.append(f"#CREATOR:UltraSinger v2.0")
            lines.append(f"#VERSION:{datetime.now().strftime('%Y-%m-%d')}")
        
        # Gap se disponível
        if song_data.get('gap'):
            lines.append(f"#GAP:{song_data['gap']}")
        
        lines.append("")  # Linha em branco
        
        # Notas
        notes = song_data.get('notes', [])
        for note in notes:
            note_type = note.get('type', ':')
            start = note.get('start', 0)
            duration = note.get('duration', 1)
            pitch = note.get('pitch', 60)
            text = note.get('text', '')
            
            # Normalizar pitch se solicitado
            if ultrastar_config.get('normalize_pitch', True):
                pitch = max(0, min(127, pitch))
            
            lines.append(f"{note_type} {start} {duration} {pitch} {text}")
        
        # Fim do arquivo
        lines.append("E")
        
        # Escrever arquivo
        with open(file_path, 'w', encoding=ultrastar_config.get('encoding', 'utf-8')) as f:
            f.write('\n'.join(lines))
    
    def _export_midi(self, song_data: Dict[str, Any], file_path: str, config: ExportConfig):
        """Exportar para formato MIDI"""
        midi_config = config.midi_config
        
        # Criar arquivo MIDI
        mid = mido.MidiFile(type=midi_config.get('format', 1))
        track = mido.MidiTrack()
        mid.tracks.append(track)
        
        # Configurar tempo
        tempo = mido.bpm2tempo(song_data.get('bpm', midi_config.get('tempo', 120)))
        track.append(mido.MetaMessage('set_tempo', tempo=tempo))
        
        # Configurar time signature
        track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
        
        # Adicionar título
        if song_data.get('title'):
            track.append(mido.MetaMessage('track_name', name=song_data['title']))
        
        # Converter notas
        notes = song_data.get('notes', [])
        current_time = 0
        
        for note in notes:
            if note.get('type') in [':', '*']:  # Apenas notas cantadas
                start = note.get('start', 0)
                duration = note.get('duration', 1)
                pitch = note.get('pitch', 60)
                velocity = midi_config.get('velocity', 80)
                channel = midi_config.get('channel', 0)
                
                # Calcular delta time
                delta_time = max(0, start - current_time)
                
                # Note on
                track.append(mido.Message('note_on', 
                                        channel=channel, 
                                        note=pitch, 
                                        velocity=velocity, 
                                        time=delta_time))
                
                # Note off
                track.append(mido.Message('note_off', 
                                        channel=channel, 
                                        note=pitch, 
                                        velocity=0, 
                                        time=duration))
                
                current_time = start + duration
        
        # Salvar arquivo
        mid.save(file_path)
    
    def _export_musicxml(self, song_data: Dict[str, Any], file_path: str, config: ExportConfig):
        """Exportar para formato MusicXML"""
        musicxml_config = config.musicxml_config
        
        # Template básico MusicXML
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML {musicxml_config.get('version', '3.1')} Partwise//EN" 
    "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="{musicxml_config.get('version', '3.1')}">
  <work>
    <work-title>{song_data.get('title', 'Unknown Title')}</work-title>
  </work>
  <identification>
    <creator type="composer">{song_data.get('artist', 'Unknown Artist')}</creator>
    <encoding>
      <software>UltraSinger v2.0</software>
      <encoding-date>{datetime.now().strftime('%Y-%m-%d')}</encoding-date>
    </encoding>
  </identification>
  <part-list>
    <score-part id="P1">
      <part-name>Vocal</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>{musicxml_config.get('divisions', 480)}</divisions>
        <key>
          <fifths>0</fifths>
        </key>
        <time>
          <beats>4</beats>
          <beat-type>4</beat-type>
        </time>
      </attributes>'''
        
        # Adicionar notas (simplificado)
        notes = song_data.get('notes', [])
        for note in notes[:10]:  # Limitar para exemplo
            if note.get('type') in [':', '*']:
                pitch = note.get('pitch', 60)
                duration = note.get('duration', 480)
                
                xml_content += f'''
      <note>
        <pitch>
          <step>C</step>
          <octave>4</octave>
        </pitch>
        <duration>{duration}</duration>
        <type>quarter</type>
      </note>'''
        
        xml_content += '''
    </measure>
  </part>
</score-partwise>'''
        
        # Escrever arquivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
    
    def _export_pdf(self, song_data: Dict[str, Any], file_path: str, config: ExportConfig):
        """Exportar para formato PDF (placeholder - requer biblioteca específica)"""
        # Esta é uma implementação básica - para PDF real seria necessário usar
        # bibliotecas como reportlab, matplotlib, ou similar
        
        # Por enquanto, criar um arquivo de texto que simula PDF
        content = f"""PDF Export Placeholder
Title: {song_data.get('title', 'Unknown')}
Artist: {song_data.get('artist', 'Unknown')}
BPM: {song_data.get('bpm', 120)}

Notes: {len(song_data.get('notes', []))} notes found

Generated by UltraSinger v2.0
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _export_json(self, song_data: Dict[str, Any], file_path: str, config: ExportConfig):
        """Exportar para formato JSON"""
        # Adicionar metadados de exportação
        export_data = {
            'metadata': {
                'exported_by': 'UltraSinger v2.0',
                'export_date': datetime.now().isoformat(),
                'format_version': '1.0'
            },
            'song_data': song_data
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def _export_csv(self, song_data: Dict[str, Any], file_path: str, config: ExportConfig):
        """Exportar notas para formato CSV"""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Cabeçalho
            writer.writerow(['Type', 'Start', 'Duration', 'Pitch', 'Text'])
            
            # Notas
            notes = song_data.get('notes', [])
            for note in notes:
                writer.writerow([
                    note.get('type', ':'),
                    note.get('start', 0),
                    note.get('duration', 1),
                    note.get('pitch', 60),
                    note.get('text', '')
                ])
    
    def _export_lyrics_txt(self, song_data: Dict[str, Any], file_path: str, config: ExportConfig):
        """Exportar apenas as letras para arquivo de texto"""
        lines = [
            f"Title: {song_data.get('title', 'Unknown Title')}",
            f"Artist: {song_data.get('artist', 'Unknown Artist')}",
            "",
            "Lyrics:",
            ""
        ]
        
        # Extrair texto das notas
        notes = song_data.get('notes', [])
        current_line = []
        
        for note in notes:
            if note.get('type') in [':', '*', 'F']:
                text = note.get('text', '').strip()
                if text:
                    if text.endswith('-'):
                        current_line.append(text[:-1])
                    else:
                        current_line.append(text)
                        if current_line:
                            lines.append(' '.join(current_line))
                            current_line = []
        
        # Adicionar linha final se houver
        if current_line:
            lines.append(' '.join(current_line))
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def _generate_export_report(self, results: Dict[str, ExportResult], config: ExportConfig):
        """Gerar relatório de exportação"""
        report_path = os.path.join(config.output_dir, f"{config.filename_base}_export_report.txt")
        
        lines = [
            f"{ULTRASINGER_HEAD} RELATÓRIO DE EXPORTAÇÃO",
            "=" * 60,
            f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Arquivo base: {config.filename_base}",
            f"Diretório: {config.output_dir}",
            ""
        ]
        
        successful = sum(1 for r in results.values() if r.success)
        total = len(results)
        
        lines.extend([
            f"Formatos exportados: {successful}/{total}",
            f"Taxa de sucesso: {(successful/total*100):.1f}%",
            ""
        ])
        
        # Detalhes por formato
        for format_type, result in results.items():
            status = "✅ SUCESSO" if result.success else "❌ FALHOU"
            lines.append(f"{status} - {format_type}")
            
            if result.success:
                lines.append(f"  📁 Arquivo: {Path(result.file_path).name}")
                lines.append(f"  📊 Tamanho: {result.file_size:,} bytes")
                lines.append(f"  ⏱️ Tempo: {result.export_time:.2f}s")
                
                if result.validation_result:
                    val_status = "✅" if result.validation_result.is_valid else "❌"
                    lines.append(f"  🔍 Validação: {val_status}")
            else:
                lines.append(f"  ❌ Erro: {result.error_message}")
            
            lines.append("")
        
        # Salvar relatório
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"📋 Relatório salvo em: {report_path}")
    
    @cache_result(ttl=3600)  # Cache por 1 hora
    def get_supported_formats(self) -> List[str]:
        """Obter lista de formatos suportados"""
        return list(self.export_methods.keys())
    
    def create_default_config(self, output_dir: str, filename_base: str, formats: List[str]) -> ExportConfig:
        """Criar configuração padrão"""
        return ExportConfig(
            output_dir=output_dir,
            filename_base=filename_base,
            formats=formats
        )
    
    def validate_config(self, config: ExportConfig) -> Tuple[bool, List[str]]:
        """Validar configuração de exportação"""
        errors = []
        
        # Verificar diretório de saída
        if not config.output_dir:
            errors.append("Diretório de saída não especificado")
        
        # Verificar nome base do arquivo
        if not config.filename_base:
            errors.append("Nome base do arquivo não especificado")
        
        # Verificar formatos
        if not config.formats:
            errors.append("Nenhum formato especificado")
        
        unsupported = [f for f in config.formats if f not in self.export_methods]
        if unsupported:
            errors.append(f"Formatos não suportados: {', '.join(unsupported)}")
        
        return len(errors) == 0, errors