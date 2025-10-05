#!/usr/bin/env python3
"""
Teste completo da geração de arquivos UltraStar.txt, MIDI e partituras
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.Midi.MidiSegment import MidiSegment
from modules.Midi.midi_creator import MidiCreator, create_midi_file
from modules.sheet import SheetMusicCreator, create_sheet
from modules.Ultrastar.ultrastar_writer import UltraStarWriter
from modules.ProcessData import MediaInfo
from modules.Ultrastar.ultrastar_txt import UltrastarTxtValue, UltrastarNoteLine, UltrastarTxtTag, UltrastarTxtNoteTypeTag

def create_test_data():
    """Criar dados de teste para simulação"""
    
    # Criar segmentos MIDI de teste
    midi_segments = [
        MidiSegment("C4", 0.0, 1.0, "Hello"),
        MidiSegment("D4", 1.0, 2.0, "world"),
        MidiSegment("E4", 2.0, 3.0, "this"),
        MidiSegment("F4", 3.0, 4.0, "is"),
        MidiSegment("G4", 4.0, 5.0, "a"),
        MidiSegment("A4", 5.0, 6.0, "test"),
        MidiSegment("B4", 6.0, 7.0, "song"),
        MidiSegment("C5", 7.0, 8.0, "for"),
        MidiSegment("B4", 8.0, 9.0, "Ultra"),
        MidiSegment("A4", 9.0, 10.0, "Singer")
    ]
    
    # Criar informações de mídia de teste
    media_info = MediaInfo(
        title="Música de Teste",
        artist="Artista de Teste", 
        bpm=120.0,
        year="2024",
        genre="Pop",
        language="pt-BR"
    )
    media_info.duration = 10.0
    
    return midi_segments, media_info

def create_ultrastar_txt_data(midi_segments, media_info):
    """Criar dados UltraStar.txt de teste"""
    
    # Criar estrutura UltraStar.txt
    ultrastar_data = UltrastarTxtValue()
    ultrastar_data.title = media_info.title
    ultrastar_data.artist = media_info.artist
    ultrastar_data.bpm = str(media_info.bpm)
    ultrastar_data.language = media_info.language or "pt-BR"
    ultrastar_data.genre = media_info.genre or "Pop"
    ultrastar_data.year = media_info.year or "2024"
    ultrastar_data.creator = "UltraSinger Test"
    ultrastar_data.comment = "Arquivo de teste gerado automaticamente"
    
    # Adicionar linhas de notas
    ultrastar_data.UltrastarNoteLines = []
    for i, segment in enumerate(midi_segments):
        note_line = UltrastarNoteLine(
            startBeat=segment.start * 4,  # Converter para beats
            startTime=segment.start,
            endTime=segment.end,
            duration=(segment.end - segment.start) * 4,
            pitch=60 + (i % 12),  # Pitch MIDI simples
            word=segment.word,
            noteType=UltrastarTxtNoteTypeTag.NORMAL
        )
        ultrastar_data.UltrastarNoteLines.append(note_line)
    
    return ultrastar_data

def test_midi_generation():
    """Testar geração de arquivos MIDI"""
    print("=== Testando Geração de MIDI ===")
    
    midi_segments, media_info = create_test_data()
    
    # Criar diretório temporário
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Diretório temporário: {temp_dir}")
        
        # Teste 1: Geração básica de MIDI
        print("\n1. Testando geração básica de MIDI...")
        try:
            create_midi_file(
                real_bpm=media_info.bpm,
                song_output=temp_dir,
                midi_segments=midi_segments,
                basename_without_ext="test_basic"
            )
            
            midi_file = os.path.join(temp_dir, "test_basic.mid")
            if os.path.exists(midi_file):
                size = os.path.getsize(midi_file)
                print(f"✓ MIDI básico criado com sucesso: {midi_file} ({size} bytes)")
            else:
                print("✗ Falha na criação do MIDI básico")
                
        except Exception as e:
            print(f"✗ Erro na geração básica de MIDI: {e}")
        
        # Teste 2: Geração avançada de MIDI
        print("\n2. Testando geração avançada de MIDI...")
        try:
            midi_creator = MidiCreator(cache_folder=temp_dir)
            
            # Validar dados
            if midi_creator.validate_midi_data(midi_segments, media_info.bpm):
                print("✓ Validação de dados MIDI passou")
                
                # Estimar propriedades
                properties = midi_creator.estimate_midi_size(midi_segments)
                print(f"✓ Propriedades estimadas: {properties}")
                
                # Criar MIDI avançado
                metadata = {
                    "instrument_program": 0,
                    "created_by": "UltraSinger Test",
                    "version": "1.0"
                }
                
                result = midi_creator.create_enhanced_midi_file(
                    real_bpm=media_info.bpm,
                    song_output=temp_dir,
                    midi_segments=midi_segments,
                    basename_without_ext="test_enhanced",
                    metadata=metadata
                )
                
                if result:
                    size = os.path.getsize(result)
                    print(f"✓ MIDI avançado criado com sucesso: {result} ({size} bytes)")
                else:
                    print("✗ Falha na criação do MIDI avançado")
            else:
                print("✗ Validação de dados MIDI falhou:")
                for error in midi_creator.get_validation_errors():
                    print(f"  - {error}")
                    
        except Exception as e:
            print(f"✗ Erro na geração avançada de MIDI: {e}")

def test_sheet_generation():
    """Testar geração de partituras"""
    print("\n=== Testando Geração de Partituras ===")
    
    midi_segments, media_info = create_test_data()
    
    # Criar diretório temporário
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = os.path.join(temp_dir, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        print(f"Diretório temporário: {temp_dir}")
        print(f"Diretório de cache: {cache_dir}")
        
        # Teste 1: Verificar se MuseScore está disponível
        print("\n1. Verificando disponibilidade do MuseScore...")
        from modules.sheet import find_musescore_version_in_path
        
        version = find_musescore_version_in_path('C:\\Program Files')
        if version != -1:
            print(f"✓ MuseScore versão {version} encontrado")
            
            # Teste 2: Geração básica de partitura
            print("\n2. Testando geração básica de partitura...")
            try:
                create_sheet(
                    midi_segments=midi_segments,
                    output_folder_path=temp_dir,
                    cache_folder_path=cache_dir,
                    musescore_path=None,  # Auto-detectar
                    filename="test_basic_sheet",
                    media_info=media_info
                )
                
                pdf_file = os.path.join(temp_dir, "test_basic_sheet.pdf")
                if os.path.exists(pdf_file):
                    size = os.path.getsize(pdf_file)
                    print(f"✓ Partitura básica criada com sucesso: {pdf_file} ({size} bytes)")
                else:
                    print("✗ Falha na criação da partitura básica")
                    
            except Exception as e:
                print(f"✗ Erro na geração básica de partitura: {e}")
            
            # Teste 3: Geração avançada de partitura
            print("\n3. Testando geração avançada de partitura...")
            try:
                sheet_creator = SheetMusicCreator(cache_folder=cache_dir)
                
                # Validar dados
                if sheet_creator.validate_sheet_data(midi_segments, media_info):
                    print("✓ Validação de dados de partitura passou")
                    
                    # Analisar tonalidade
                    key = sheet_creator.analyze_musical_key(midi_segments)
                    print(f"✓ Tonalidade detectada: {key}")
                    
                    # Sugerir compasso
                    time_sig = sheet_creator.suggest_time_signature(midi_segments, media_info.bpm)
                    print(f"✓ Compasso sugerido: {time_sig}")
                    
                    # Criar partitura avançada
                    options = {
                        "enhanced_formatting": True,
                        "add_expressions": True,
                        "auto_key_detection": True
                    }
                    
                    result = sheet_creator.create_enhanced_sheet(
                        midi_segments=midi_segments,
                        output_folder_path=temp_dir,
                        cache_folder_path=cache_dir,
                        musescore_path=None,
                        filename="test_enhanced_sheet",
                        media_info=media_info,
                        options=options
                    )
                    
                    if result:
                        size = os.path.getsize(result)
                        print(f"✓ Partitura avançada criada com sucesso: {result} ({size} bytes)")
                    else:
                        print("✗ Falha na criação da partitura avançada")
                else:
                    print("✗ Validação de dados de partitura falhou:")
                    for error in sheet_creator.get_validation_errors():
                        print(f"  - {error}")
                        
            except Exception as e:
                print(f"✗ Erro na geração avançada de partitura: {e}")
                
        else:
            print("⚠ MuseScore não encontrado - pulando testes de partitura")
            print("  Para testar partituras, instale o MuseScore em C:\\Program Files")

def test_ultrastar_generation():
    """Testar geração de arquivos UltraStar.txt"""
    print("\n=== Testando Geração de UltraStar.txt ===")
    
    midi_segments, media_info = create_test_data()
    ultrastar_data = create_ultrastar_txt_data(midi_segments, media_info)
    
    # Criar diretório temporário
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Diretório temporário: {temp_dir}")
        
        # Teste 1: Geração básica de UltraStar.txt
        print("\n1. Testando geração básica de UltraStar.txt...")
        try:
            from modules.Ultrastar.ultrastar_writer import create_ultrastar_txt
            
            # Adicionar arquivo MP3 obrigatório
            ultrastar_data.mp3 = "test_song.mp3"
            ultrastar_data.audio = "test_song.mp3"
            
            output_file = os.path.join(temp_dir, "test_basic.txt")
            create_ultrastar_txt(midi_segments, output_file, ultrastar_data, media_info.bpm)
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"✓ UltraStar.txt básico criado com sucesso: {output_file} ({file_size} bytes)")
                
                # Mostrar primeiras linhas
                with open(output_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:10]
                    print("Primeiras linhas:")
                    for line in lines:
                        print(f"  {line.strip()}")
            else:
                print("✗ Falha na criação do UltraStar.txt básico")
                
        except Exception as e:
            print(f"✗ Erro na geração básica de UltraStar.txt: {e}")
        
        # Teste 2: Geração avançada de UltraStar.txt
        print("\n2. Testando geração avançada de UltraStar.txt...")
        try:
            writer = UltraStarWriter(cache_folder=temp_dir)
            
            # Validar dados (precisa dos midi_segments também)
            if writer.validate_ultrastar_data(ultrastar_data, midi_segments):
                print("✓ Validação de dados UltraStar passou")
                
                # Criar backup se necessário
                output_file = os.path.join(temp_dir, "test_enhanced.txt")
                backup = writer.create_backup(output_file)
                
                # Salvar metadados
                writer.save_metadata(ultrastar_data, output_file)
                
                # Criar arquivo UltraStar.txt usando a função padrão
                create_ultrastar_txt(midi_segments, output_file, ultrastar_data, media_info.bpm)
                
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    print(f"✓ UltraStar.txt avançado criado com sucesso: {output_file} ({file_size} bytes)")
                    
                    # Mostrar primeiras linhas
                    with open(output_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:10]
                        print("Primeiras linhas:")
                        for line in lines:
                            print(f"  {line.strip()}")
                else:
                    print("✗ Falha na criação do UltraStar.txt avançado")
            else:
                print("✗ Validação de dados UltraStar falhou:")
                for error in writer.get_validation_errors():
                    print(f"  - {error}")
                    
        except Exception as e:
            print(f"✗ Erro na geração avançada de UltraStar.txt: {e}")

def main():
    """Função principal de teste"""
    print("🎵 TESTE COMPLETO DE GERAÇÃO DE ARQUIVOS ULTRASINGER 🎵")
    print("=" * 60)
    
    try:
        # Testar geração de MIDI
        test_midi_generation()
        
        # Testar geração de partituras
        test_sheet_generation()
        
        # Testar geração de UltraStar.txt
        test_ultrastar_generation()
        
        print("\n" + "=" * 60)
        print("✓ TESTE COMPLETO FINALIZADO")
        print("Todos os módulos de geração foram testados!")
        
    except Exception as e:
        print(f"\n✗ ERRO GERAL NO TESTE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()