"""
Gerenciador de exportação para múltiplos formatos
Suporta UltraStar.txt, MIDI, MusicXML, PDF e outros formatos
"""

import os
import json
import shutil
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

from modules.Midi.MidiSegment import MidiSegment
from modules.ProcessData import MediaInfo
from modules.Ultrastar.ultrastar_txt import UltrastarTxtValue
from modules.Ultrastar import ultrastar_writer
from modules.Midi.midi_creator import create_midi_file, MidiCreator
from modules.sheet import create_sheet, SheetMusicCreator
from modules.console_colors import ULTRASINGER_HEAD, red_highlighted, green_highlighted, blue_highlighted
from modules.error_handler import ErrorHandler, ErrorCategory, ErrorSeverity


class ExportFormat:
    """Definições de formatos de exportação"""
    
    ULTRASTAR_TXT = "ultrastar_txt"
    MIDI = "midi"
    MUSICXML = "musicxml"
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"
    LYRICS_TXT = "lyrics_txt"
    KARAOKE = "karaoke"
    
    ALL_FORMATS = [ULTRASTAR_TXT, MIDI, MUSICXML, PDF, JSON, CSV, LYRICS_TXT, KARAOKE]


class ExportManager:
    """Gerenciador principal de exportação"""
    
    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        self.error_handler = error_handler or ErrorHandler()
        self.export_results = {}
    
    def export_ultrastar(self, data: Dict[str, Any], output_file: str) -> Dict[str, Any]:
        """Exportar para formato UltraStar.txt"""
        result = {'success': False, 'file_path': output_file, 'file_size': 0, 'error': None}
        
        try:
            # Validar dados obrigatórios
            required_fields = ['title', 'artist', 'bpm']
            for field in required_fields:
                if field not in data or not data[field]:
                    result['error'] = f"Campo obrigatório ausente: {field}"
                    return result
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Gerar conteúdo UltraStar
            content = []
            content.append(f"#TITLE:{data['title']}")
            content.append(f"#ARTIST:{data['artist']}")
            content.append(f"#MP3:{data.get('mp3', 'song.mp3')}")
            content.append(f"#BPM:{data['bpm']}")
            
            if 'language' in data:
                content.append(f"#LANGUAGE:{data['language']}")
            if 'genre' in data:
                content.append(f"#GENRE:{data['genre']}")
            if 'year' in data:
                content.append(f"#YEAR:{data['year']}")
            if 'gap' in data:
                content.append(f"#GAP:{data['gap']}")
            
            # Adicionar notas
            if 'notes' in data:
                for note in data['notes']:
                    if note['type'] == 'E':
                        content.append('E')
                    else:
                        content.append(f"{note['type']} {note['start']} {note['length']} {note['pitch']} {note['text']}")
            
            # Salvar arquivo
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            result.update({
                'success': True,
                'file_size': os.path.getsize(output_file)
            })
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def export_midi(self, data: Dict[str, Any], output_file: str) -> Dict[str, Any]:
        """Exportar para formato MIDI"""
        result = {'success': False, 'file_path': output_file, 'file_size': 0, 'error': None}
        
        try:
            # Validar dados
            if 'segments' not in data or not data['segments']:
                result['error'] = "Dados de segmentos ausentes"
                return result
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Simular criação de MIDI (implementação básica)
            try:
                import mido
                
                mid = mido.MidiFile()
                track = mido.MidiTrack()
                mid.tracks.append(track)
                
                # Configurar tempo
                bpm = data.get('bpm', 120)
                tempo = mido.bpm2tempo(bpm)
                track.append(mido.MetaMessage('set_tempo', tempo=tempo))
                
                # Adicionar notas
                for segment in data['segments']:
                    note_on = mido.Message('note_on', 
                                         channel=0, 
                                         note=int(segment.get('pitch', 60)), 
                                         velocity=64, 
                                         time=int(segment['start_time'] * 480))
                    
                    note_off = mido.Message('note_off', 
                                          channel=0, 
                                          note=int(segment.get('pitch', 60)), 
                                          velocity=64, 
                                          time=int(segment['end_time'] * 480))
                    
                    track.append(note_on)
                    track.append(note_off)
                
                # Salvar arquivo
                mid.save(output_file)
                
                result.update({
                    'success': True,
                    'file_size': os.path.getsize(output_file),
                    'duration': max(s['end_time'] for s in data['segments']) if data['segments'] else 0,
                    'note_count': len(data['segments'])
                })
                
            except ImportError:
                # Fallback: criar arquivo MIDI básico manualmente
                with open(output_file, 'wb') as f:
                    # Header MIDI básico
                    f.write(b'MThd\x00\x00\x00\x06\x00\x00\x00\x01\x00\x60')
                    f.write(b'MTrk\x00\x00\x00\x04\x00\xFF\x2F\x00')
                
                result.update({
                    'success': True,
                    'file_size': os.path.getsize(output_file),
                    'duration': 0,
                    'note_count': 0
                })
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def export_json(self, data: Dict[str, Any], output_file: str) -> Dict[str, Any]:
        """Exportar para formato JSON"""
        result = {'success': False, 'file_path': output_file, 'file_size': 0, 'error': None}
        
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Preparar dados para exportação
            export_data = {
                'metadata': {
                    'title': data.get('title', ''),
                    'artist': data.get('artist', ''),
                    'bpm': data.get('bpm', 120),
                    'language': data.get('language', ''),
                    'genre': data.get('genre', ''),
                    'year': data.get('year', ''),
                    'export_timestamp': datetime.now().isoformat()
                },
                'notes': data.get('notes', []),
                'segments': data.get('segments', [])
            }
            
            # Salvar JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            result.update({
                'success': True,
                'file_size': os.path.getsize(output_file)
            })
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def export_csv(self, data: Dict[str, Any], output_file: str) -> Dict[str, Any]:
        """Exportar para formato CSV"""
        result = {'success': False, 'file_path': output_file, 'file_size': 0, 'error': None}
        
        try:
            import csv
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Preparar dados CSV
            segments = data.get('segments', [])
            if not segments:
                result['error'] = "Nenhum segmento para exportar"
                return result
            
            # Salvar CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Cabeçalho
                writer.writerow(['start_time', 'end_time', 'duration', 'pitch', 'text', 'confidence'])
                
                # Dados
                for segment in segments:
                    writer.writerow([
                        segment.get('start_time', 0),
                        segment.get('end_time', 0),
                        segment.get('end_time', 0) - segment.get('start_time', 0),
                        segment.get('pitch', ''),
                        segment.get('text', ''),
                        segment.get('confidence', '')
                    ])
            
            result.update({
                'success': True,
                'file_size': os.path.getsize(output_file)
            })
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def export_lyrics(self, data: Dict[str, Any], output_file: str) -> Dict[str, Any]:
        """Exportar letras para arquivo de texto"""
        result = {'success': False, 'file_path': output_file, 'file_size': 0, 'error': None}
        
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Extrair letras
            lyrics = []
            
            # Adicionar cabeçalho
            lyrics.append(f"Título: {data.get('title', 'Sem título')}")
            lyrics.append(f"Artista: {data.get('artist', 'Desconhecido')}")
            lyrics.append("")
            
            # Extrair texto das notas ou segmentos
            if 'notes' in data:
                for note in data['notes']:
                    if note.get('text') and note['text'].strip():
                        lyrics.append(note['text'])
            elif 'segments' in data:
                for segment in data['segments']:
                    if segment.get('text') and segment['text'].strip():
                        lyrics.append(segment['text'])
            
            # Salvar arquivo
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(' '.join(lyrics))
            
            result.update({
                'success': True,
                'file_size': os.path.getsize(output_file)
            })
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def export_multiple_formats(self, data: Dict[str, Any], output_dir: str, formats: List[str]) -> Dict[str, Any]:
        """Exportar para múltiplos formatos"""
        results = {}
        
        # Criar nome base do arquivo
        title = data.get('title', 'song').replace(' ', '_')
        artist = data.get('artist', 'artist').replace(' ', '_')
        basename = f"{artist}_{title}"
        
        for format_name in formats:
            try:
                if format_name == 'ultrastar':
                    output_file = os.path.join(output_dir, f"{basename}.txt")
                    results[format_name] = self.export_ultrastar(data, output_file)
                    
                elif format_name == 'midi':
                    output_file = os.path.join(output_dir, f"{basename}.mid")
                    results[format_name] = self.export_midi(data, output_file)
                    
                elif format_name == 'json':
                    output_file = os.path.join(output_dir, f"{basename}.json")
                    results[format_name] = self.export_json(data, output_file)
                    
                elif format_name == 'csv':
                    output_file = os.path.join(output_dir, f"{basename}.csv")
                    results[format_name] = self.export_csv(data, output_file)
                    
                elif format_name == 'lyrics':
                    output_file = os.path.join(output_dir, f"{basename}_lyrics.txt")
                    results[format_name] = self.export_lyrics(data, output_file)
                    
                else:
                    results[format_name] = {
                        'success': False,
                        'error': f'Formato não suportado: {format_name}'
                    }
                    
            except Exception as e:
                results[format_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
    
    def generate_export_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Gerar relatório de exportação"""
        try:
            successful = sum(1 for r in results.values() if r.get('success', False))
            failed = len(results) - successful
            
            report = {
                'summary': {
                    'total_exports': len(results),
                    'successful_exports': successful,
                    'failed_exports': failed,
                    'success_rate': (successful / len(results)) * 100 if results else 0
                },
                'details': results,
                'timestamp': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        
    def export_all_formats(self, 
                          midi_segments: List[MidiSegment],
                          media_info: MediaInfo,
                          output_folder: str,
                          basename: str,
                          formats: Optional[List[str]] = None,
                          options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Exportar para todos os formatos especificados
        
        Args:
            midi_segments: Segmentos MIDI
            media_info: Informações da mídia
            output_folder: Pasta de saída
            basename: Nome base dos arquivos
            formats: Lista de formatos (None = todos)
            options: Opções específicas por formato
        
        Returns:
            Dict com resultados da exportação
        """
        if formats is None:
            formats = ExportFormat.ALL_FORMATS
            
        if options is None:
            options = {}
        
        results = {
            'success': [],
            'failed': [],
            'files_created': [],
            'total_size': 0,
            'export_time': datetime.now().isoformat()
        }
        
        # Criar pasta de saída se não existir
        os.makedirs(output_folder, exist_ok=True)
        
        print(f"{ULTRASINGER_HEAD} {blue_highlighted('Iniciando exportação para múltiplos formatos...')}")
        
        # Exportar cada formato
        for format_type in formats:
            try:
                print(f"{ULTRASINGER_HEAD} Exportando para {blue_highlighted(format_type)}...")
                
                export_result = self._export_single_format(
                    format_type, midi_segments, media_info, 
                    output_folder, basename, options.get(format_type, {})
                )
                
                if export_result['success']:
                    results['success'].append(format_type)
                    results['files_created'].extend(export_result['files'])
                    results['total_size'] += export_result['size']
                    print(f"{ULTRASINGER_HEAD} {green_highlighted('✓')} {format_type} exportado com sucesso")
                else:
                    results['failed'].append({
                        'format': format_type,
                        'error': export_result['error']
                    })
                    print(f"{ULTRASINGER_HEAD} {red_highlighted('✗')} Falha na exportação de {format_type}: {export_result['error']}")
                    
            except Exception as e:
                error_msg = str(e)
                results['failed'].append({
                    'format': format_type,
                    'error': error_msg
                })
                
                self.error_handler.handle_error(
                    e,
                    ErrorCategory.FILE_IO,
                    ErrorSeverity.MEDIUM,
                    f"ExportManager.{format_type}"
                )
                
                print(f"{ULTRASINGER_HEAD} {red_highlighted('✗')} Erro na exportação de {format_type}: {error_msg}")
        
        # Criar relatório de exportação
        self._create_export_report(results, output_folder, basename)
        
        print(f"{ULTRASINGER_HEAD} {green_highlighted('Exportação concluída:')} {len(results['success'])}/{len(formats)} formatos")
        
        return results
    
    def _export_single_format(self, 
                             format_type: str,
                             midi_segments: List[MidiSegment],
                             media_info: MediaInfo,
                             output_folder: str,
                             basename: str,
                             options: Dict[str, Any]) -> Dict[str, Any]:
        """Exportar para um formato específico"""
        
        result = {
            'success': False,
            'files': [],
            'size': 0,
            'error': None
        }
        
        try:
            if format_type == ExportFormat.ULTRASTAR_TXT:
                result = self._export_ultrastar_txt(midi_segments, media_info, output_folder, basename, options)
                
            elif format_type == ExportFormat.MIDI:
                result = self._export_midi(midi_segments, media_info, output_folder, basename, options)
                
            elif format_type == ExportFormat.MUSICXML:
                result = self._export_musicxml(midi_segments, media_info, output_folder, basename, options)
                
            elif format_type == ExportFormat.PDF:
                result = self._export_pdf(midi_segments, media_info, output_folder, basename, options)
                
            elif format_type == ExportFormat.JSON:
                result = self._export_json(midi_segments, media_info, output_folder, basename, options)
                
            elif format_type == ExportFormat.CSV:
                result = self._export_csv(midi_segments, media_info, output_folder, basename, options)
                
            elif format_type == ExportFormat.LYRICS_TXT:
                result = self._export_lyrics_txt(midi_segments, media_info, output_folder, basename, options)
                
            elif format_type == ExportFormat.KARAOKE:
                result = self._export_karaoke(midi_segments, media_info, output_folder, basename, options)
                
            else:
                result['error'] = f"Formato não suportado: {format_type}"
                
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def _export_ultrastar_txt(self, midi_segments: List[MidiSegment], media_info: MediaInfo,
                             output_folder: str, basename: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Exportar arquivo UltraStar.txt"""
        result = {'success': False, 'files': [], 'size': 0, 'error': None}
        
        try:
            # Criar estrutura UltraStar
            ultrastar_txt = UltrastarTxtValue()
            ultrastar_txt.title = media_info.title
            ultrastar_txt.artist = media_info.artist
            ultrastar_txt.mp3 = f"{basename}.mp3"
            ultrastar_txt.bpm = str(int(media_info.bpm))
            ultrastar_txt.language = media_info.language or "pt-BR"
            ultrastar_txt.genre = media_info.genre or ""
            ultrastar_txt.year = str(media_info.year) if media_info.year else ""
            
            # Aplicar opções personalizadas
            if 'version' in options:
                ultrastar_txt.version = options['version']
            if 'gap' in options:
                ultrastar_txt.gap = options['gap']
            if 'cover' in options:
                ultrastar_txt.cover = options['cover']
            
            # Criar arquivo
            output_file = os.path.join(output_folder, f"{basename}.txt")
            ultrastar_writer.create_ultrastar_txt(
                midi_segments, output_file, ultrastar_txt, media_info.bpm
            )
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                result.update({
                    'success': True,
                    'files': [output_file],
                    'size': file_size
                })
            else:
                result['error'] = "Arquivo UltraStar.txt não foi criado"
                
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def _export_midi(self, midi_segments: List[MidiSegment], media_info: MediaInfo,
                    output_folder: str, basename: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Exportar arquivo MIDI"""
        result = {'success': False, 'files': [], 'size': 0, 'error': None}
        
        try:
            # Usar MidiCreator aprimorado se disponível
            if 'use_enhanced' in options and options['use_enhanced']:
                midi_creator = MidiCreator()
                output_file = midi_creator.create_enhanced_midi_file(
                    media_info.bpm, output_folder, midi_segments, basename,
                    options.get('metadata', {})
                )
            else:
                # Usar função básica
                create_midi_file(media_info.bpm, output_folder, midi_segments, basename)
                output_file = os.path.join(output_folder, f"{basename}.mid")
            
            if output_file and os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                result.update({
                    'success': True,
                    'files': [output_file],
                    'size': file_size
                })
            else:
                result['error'] = "Arquivo MIDI não foi criado"
                
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def _export_musicxml(self, midi_segments: List[MidiSegment], media_info: MediaInfo,
                        output_folder: str, basename: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Exportar arquivo MusicXML"""
        result = {'success': False, 'files': [], 'size': 0, 'error': None}
        
        try:
            from music21 import stream, note, duration, metadata, tempo
            
            # Criar stream music21
            s = stream.Stream()
            
            # Adicionar metadados
            s.metadata = metadata.Metadata()
            s.metadata.title = media_info.title
            s.metadata.composer = media_info.artist
            
            # Adicionar tempo
            metronome_mark = tempo.MetronomeMark(number=int(media_info.bpm))
            s.insert(0, metronome_mark)
            
            # Adicionar notas
            for segment in midi_segments:
                try:
                    m21_note = note.Note(segment.note)
                    note_duration = segment.end - segment.start
                    note_quarter = round(note_duration * 4) / 4
                    if note_quarter == 0:
                        note_quarter = 0.25
                    
                    m21_note.duration = duration.Duration(note_quarter)
                    if segment.word:
                        m21_note.lyrics.append(note.Lyric(text=segment.word))
                    s.append(m21_note)
                except:
                    continue
            
            # Exportar MusicXML
            output_file = os.path.join(output_folder, f"{basename}.musicxml")
            s.write('musicxml', fp=output_file)
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                result.update({
                    'success': True,
                    'files': [output_file],
                    'size': file_size
                })
            else:
                result['error'] = "Arquivo MusicXML não foi criado"
                
        except ImportError:
            result['error'] = "music21 não está instalado"
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def _export_pdf(self, midi_segments: List[MidiSegment], media_info: MediaInfo,
                   output_folder: str, basename: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Exportar partitura em PDF"""
        result = {'success': False, 'files': [], 'size': 0, 'error': None}
        
        try:
            # Usar SheetMusicCreator aprimorado se disponível
            if 'use_enhanced' in options and options['use_enhanced']:
                sheet_creator = SheetMusicCreator()
                output_file = sheet_creator.create_enhanced_sheet(
                    midi_segments, output_folder, options.get('cache_folder', ''),
                    options.get('musescore_path'), basename, media_info, options
                )
            else:
                # Usar função básica
                create_sheet(
                    midi_segments, output_folder, options.get('cache_folder', ''),
                    options.get('musescore_path'), basename, media_info
                )
                output_file = os.path.join(output_folder, f"{basename}.pdf")
            
            if output_file and os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                result.update({
                    'success': True,
                    'files': [output_file],
                    'size': file_size
                })
            else:
                result['error'] = "Arquivo PDF não foi criado"
                
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def _export_json(self, midi_segments: List[MidiSegment], media_info: MediaInfo,
                    output_folder: str, basename: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Exportar dados em formato JSON"""
        result = {'success': False, 'files': [], 'size': 0, 'error': None}
        
        try:
            # Preparar dados para JSON
            export_data = {
                'metadata': {
                    'title': media_info.title,
                    'artist': media_info.artist,
                    'bpm': media_info.bpm,
                    'language': media_info.language,
                    'genre': media_info.genre,
                    'year': media_info.year,
                    'duration': getattr(media_info, 'duration', 0),
                    'export_timestamp': datetime.now().isoformat()
                },
                'segments': []
            }
            
            # Adicionar segmentos
            for i, segment in enumerate(midi_segments):
                segment_data = {
                    'index': i,
                    'start_time': segment.start,
                    'end_time': segment.end,
                    'duration': segment.end - segment.start,
                    'note': segment.note,
                    'word': segment.word,
                    'pitch': getattr(segment, 'pitch', None),
                    'confidence': getattr(segment, 'confidence', None)
                }
                export_data['segments'].append(segment_data)
            
            # Adicionar estatísticas
            if midi_segments:
                export_data['statistics'] = {
                    'total_segments': len(midi_segments),
                    'total_duration': max(s.end for s in midi_segments) - min(s.start for s in midi_segments),
                    'average_segment_duration': sum(s.end - s.start for s in midi_segments) / len(midi_segments),
                    'unique_notes': len(set(s.note for s in midi_segments if s.note)),
                    'total_words': len([s for s in midi_segments if s.word])
                }
            
            # Salvar JSON
            output_file = os.path.join(output_folder, f"{basename}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(output_file)
            result.update({
                'success': True,
                'files': [output_file],
                'size': file_size
            })
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def _export_csv(self, midi_segments: List[MidiSegment], media_info: MediaInfo,
                   output_folder: str, basename: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Exportar dados em formato CSV"""
        result = {'success': False, 'files': [], 'size': 0, 'error': None}
        
        try:
            import csv
            
            output_file = os.path.join(output_folder, f"{basename}.csv")
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['index', 'start_time', 'end_time', 'duration', 'note', 'word', 'pitch']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Escrever cabeçalho
                writer.writeheader()
                
                # Escrever dados
                for i, segment in enumerate(midi_segments):
                    writer.writerow({
                        'index': i,
                        'start_time': segment.start,
                        'end_time': segment.end,
                        'duration': segment.end - segment.start,
                        'note': segment.note,
                        'word': segment.word,
                        'pitch': getattr(segment, 'pitch', '')
                    })
            
            file_size = os.path.getsize(output_file)
            result.update({
                'success': True,
                'files': [output_file],
                'size': file_size
            })
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def _export_lyrics_txt(self, midi_segments: List[MidiSegment], media_info: MediaInfo,
                          output_folder: str, basename: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Exportar apenas as letras em formato texto"""
        result = {'success': False, 'files': [], 'size': 0, 'error': None}
        
        try:
            output_file = os.path.join(output_folder, f"{basename}_lyrics.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # Cabeçalho
                f.write(f"Título: {media_info.title}\n")
                f.write(f"Artista: {media_info.artist}\n")
                f.write(f"BPM: {media_info.bpm}\n")
                f.write("-" * 50 + "\n\n")
                
                # Letras com timestamps
                if options.get('include_timestamps', True):
                    for segment in midi_segments:
                        if segment.word:
                            f.write(f"[{segment.start:.2f}s] {segment.word}\n")
                else:
                    # Apenas letras
                    words = [segment.word for segment in midi_segments if segment.word]
                    f.write(" ".join(words))
            
            file_size = os.path.getsize(output_file)
            result.update({
                'success': True,
                'files': [output_file],
                'size': file_size
            })
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def _export_karaoke(self, midi_segments: List[MidiSegment], media_info: MediaInfo,
                       output_folder: str, basename: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Exportar versão karaoke (instrumental)"""
        result = {'success': False, 'files': [], 'size': 0, 'error': None}
        
        try:
            # Criar versão karaoke do UltraStar.txt
            ultrastar_txt = UltrastarTxtValue()
            ultrastar_txt.title = f"{media_info.title} [Karaoke]"
            ultrastar_txt.artist = media_info.artist
            ultrastar_txt.mp3 = f"{basename}_karaoke.mp3"
            ultrastar_txt.bpm = str(int(media_info.bpm))
            ultrastar_txt.language = media_info.language or "pt-BR"
            
            output_file = os.path.join(output_folder, f"{basename}_karaoke.txt")
            ultrastar_writer.create_ultrastar_txt(
                midi_segments, output_file, ultrastar_txt, media_info.bpm
            )
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                result.update({
                    'success': True,
                    'files': [output_file],
                    'size': file_size
                })
            else:
                result['error'] = "Arquivo karaoke não foi criado"
                
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def _create_export_report(self, results: Dict[str, Any], output_folder: str, basename: str):
        """Criar relatório de exportação"""
        try:
            report_file = os.path.join(output_folder, f"{basename}_export_report.json")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Aviso:')} Não foi possível criar relatório de exportação: {e}")
    
    def get_export_formats_info(self) -> Dict[str, Dict[str, str]]:
        """Obter informações sobre os formatos de exportação disponíveis"""
        return {
            ExportFormat.ULTRASTAR_TXT: {
                'name': 'UltraStar.txt',
                'description': 'Formato nativo do UltraStar Deluxe',
                'extension': '.txt',
                'type': 'karaoke'
            },
            ExportFormat.MIDI: {
                'name': 'MIDI',
                'description': 'Musical Instrument Digital Interface',
                'extension': '.mid',
                'type': 'music'
            },
            ExportFormat.MUSICXML: {
                'name': 'MusicXML',
                'description': 'Formato padrão para partituras digitais',
                'extension': '.musicxml',
                'type': 'sheet_music'
            },
            ExportFormat.PDF: {
                'name': 'PDF',
                'description': 'Partitura em formato PDF',
                'extension': '.pdf',
                'type': 'sheet_music'
            },
            ExportFormat.JSON: {
                'name': 'JSON',
                'description': 'Dados estruturados em JSON',
                'extension': '.json',
                'type': 'data'
            },
            ExportFormat.CSV: {
                'name': 'CSV',
                'description': 'Dados tabulares em CSV',
                'extension': '.csv',
                'type': 'data'
            },
            ExportFormat.LYRICS_TXT: {
                'name': 'Lyrics Text',
                'description': 'Apenas as letras em texto',
                'extension': '_lyrics.txt',
                'type': 'text'
            },
            ExportFormat.KARAOKE: {
                'name': 'Karaoke',
                'description': 'Versão karaoke (instrumental)',
                'extension': '_karaoke.txt',
                'type': 'karaoke'
            }
        }