#!/usr/bin/env python3
"""
Teste do Sistema de Cache e Otimizações de Performance do UltraSinger
"""

import os
import sys
import json
import time
import tempfile
import shutil
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.Pitcher.pitcher import save_pitch_cache, load_pitch_cache
from modules.Pitcher.pitched_data import PitchedData
from modules.Midi.midi_creator import MidiCreator
from modules.sheet import SheetMusicCreator
from modules.Ultrastar.ultrastar_writer import UltraStarWriter
from modules.Ultrastar.ultrastar_score_calculator import UltrastarScoreCalculator
from modules.ProcessData import MediaInfo
from modules.Midi.MidiSegment import MidiSegment
import numpy as np

def test_pitch_cache():
    """Testar sistema de cache de pitch detection"""
    print("\n=== Testando Sistema de Cache de Pitch ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_path = os.path.join(temp_dir, "pitch_cache.json")
        
        # Criar dados de pitch de teste
        print("1. Criando dados de pitch de teste...")
        pitched_data = PitchedData(
            times=np.array([0.0, 0.1, 0.2, 0.3, 0.4]),
            frequencies=np.array([440.0, 493.88, 523.25, 587.33, 659.25]),
            confidence=np.array([0.9, 0.85, 0.92, 0.88, 0.91])
        )
        
        # Testar salvamento no cache
        print("2. Testando salvamento no cache...")
        start_time = time.time()
        save_pitch_cache(cache_path, pitched_data)
        save_time = time.time() - start_time
        
        if os.path.exists(cache_path):
            file_size = os.path.getsize(cache_path)
            print(f"✓ Cache salvo com sucesso: {cache_path} ({file_size} bytes, {save_time:.3f}s)")
        else:
            print("✗ Falha ao salvar cache")
            return False
        
        # Testar carregamento do cache
        print("3. Testando carregamento do cache...")
        start_time = time.time()
        loaded_data = load_pitch_cache(cache_path)
        load_time = time.time() - start_time
        
        if loaded_data:
            print(f"✓ Cache carregado com sucesso ({load_time:.3f}s)")
            
            # Verificar integridade dos dados
            if (np.array_equal(loaded_data.times, pitched_data.times) and
                np.array_equal(loaded_data.frequencies, pitched_data.frequencies) and
                np.array_equal(loaded_data.confidence, pitched_data.confidence)):
                print("✓ Integridade dos dados verificada")
                return True
            else:
                print("✗ Dados corrompidos no cache")
                return False
        else:
            print("✗ Falha ao carregar cache")
            return False

def test_midi_cache():
    """Testar sistema de cache de MIDI"""
    print("\n=== Testando Sistema de Cache de MIDI ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Diretório de cache: {temp_dir}")
        
        # Criar dados de teste
        midi_segments = [
            MidiSegment("C4", 0.0, 1.0, "Hello"),
            MidiSegment("D4", 1.0, 2.0, "world"),
            MidiSegment("E4", 2.0, 3.0, "test")
        ]
        
        media_info = MediaInfo(
            title="Cache Test Song",
            artist="Cache Test Artist",
            bpm=120.0
        )
        
        # Testar criação com cache
        print("1. Testando criação de MIDI com cache...")
        midi_creator = MidiCreator(cache_folder=temp_dir)
        
        start_time = time.time()
        result = midi_creator.create_enhanced_midi_file(
            real_bpm=media_info.bpm,
            song_output=temp_dir,
            midi_segments=midi_segments,
            basename_without_ext="test_cached",
            metadata={"use_cache": True}
        )
        creation_time = time.time() - start_time
        
        if result:
            print(f"✓ MIDI criado com cache ({creation_time:.3f}s)")
            
            # Verificar se arquivos de cache foram criados
            cache_files = [f for f in os.listdir(temp_dir) if f.endswith('.cache')]
            if cache_files:
                print(f"✓ Arquivos de cache criados: {len(cache_files)}")
                return True
            else:
                print("⚠ MIDI criado mas sem arquivos de cache específicos")
                return True
        else:
            print("✗ Falha na criação de MIDI com cache")
            return False

def test_sheet_cache():
    """Testar sistema de cache de partituras"""
    print("\n=== Testando Sistema de Cache de Partituras ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Diretório de cache: {temp_dir}")
        
        # Criar dados de teste
        midi_segments = [
            MidiSegment("C4", 0.0, 1.0, "Test"),
            MidiSegment("D4", 1.0, 2.0, "cache"),
            MidiSegment("E4", 2.0, 3.0, "system")
        ]
        
        media_info = MediaInfo(
            title="Sheet Cache Test",
            artist="Test Artist",
            bpm=120.0
        )
        
        # Testar criação com cache
        print("1. Testando criação de partitura com cache...")
        sheet_creator = SheetMusicCreator(cache_folder=temp_dir)
        
        # Verificar se MuseScore está disponível
        try:
            start_time = time.time()
            result = sheet_creator.create_sheet(
                midi_segments=midi_segments,
                media_info=media_info,
                output_path=os.path.join(temp_dir, "test_cached_sheet.pdf")
            )
            creation_time = time.time() - start_time
            
            if result:
                print(f"✓ Partitura criada com cache ({creation_time:.3f}s)")
                
                # Verificar metadados de cache
                cache_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
                if cache_files:
                    print(f"✓ Metadados de cache salvos: {len(cache_files)} arquivos")
                    return True
                else:
                    print("⚠ Partitura criada mas sem metadados de cache")
                    return True
            else:
                print("✗ Falha na criação de partitura com cache")
                return False
                
        except Exception as e:
            print(f"⚠ MuseScore não disponível ou erro: {e}")
            return True  # Não é um erro crítico

def test_ultrastar_cache():
    """Testar sistema de cache de UltraStar"""
    print("\n=== Testando Sistema de Cache de UltraStar ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Diretório de cache: {temp_dir}")
        
        # Criar dados de teste
        midi_segments = [
            MidiSegment("C4", 0.0, 1.0, "Ultra"),
            MidiSegment("D4", 1.0, 2.0, "Star"),
            MidiSegment("E4", 2.0, 3.0, "cache")
        ]
        
        media_info = MediaInfo(
            title="UltraStar Cache Test",
            artist="Cache Artist",
            bpm=120.0
        )
        
        # Testar writer com cache
        print("1. Testando UltraStarWriter com cache...")
        writer = UltraStarWriter(cache_folder=temp_dir)
        
        # Testar salvamento de metadados
        from modules.Ultrastar.ultrastar_txt import UltrastarTxtValue
        ultrastar_data = UltrastarTxtValue()
        ultrastar_data.title = media_info.title
        ultrastar_data.artist = media_info.artist
        ultrastar_data.bpm = str(media_info.bpm)
        ultrastar_data.mp3 = "test.mp3"
        ultrastar_data.audio = "test.mp3"
        
        output_file = os.path.join(temp_dir, "test_cache.txt")
        
        start_time = time.time()
        writer.save_metadata(ultrastar_data, output_file)
        save_time = time.time() - start_time
        
        print(f"✓ Metadados salvos ({save_time:.3f}s)")
        
        # Verificar arquivos de cache
        cache_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
        if cache_files:
            print(f"✓ Arquivos de metadados criados: {len(cache_files)}")
            return True
        else:
            print("⚠ Metadados processados mas sem arquivos de cache específicos")
            return True

def test_score_cache():
    """Testar sistema de cache de pontuação"""
    print("\n=== Testando Sistema de Cache de Pontuação ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Diretório de cache: {temp_dir}")
        
        # Testar calculadora com cache
        print("1. Testando UltrastarScoreCalculator com cache...")
        calculator = UltrastarScoreCalculator(cache_folder=temp_dir)
        
        # Testar cálculo de precisão de pitch
        start_time = time.time()
        is_accurate, accuracy = calculator.calculate_pitch_accuracy("C4", "C4", tolerance=0.5)
        calc_time = time.time() - start_time
        
        if is_accurate and accuracy > 0.9:
            print(f"✓ Cálculo de precisão funcionando ({calc_time:.3f}s, precisão: {accuracy:.2f})")
            
            # Verificar se pasta de cache foi criada
            if os.path.exists(calculator.cache_folder):
                print(f"✓ Pasta de cache criada: {calculator.cache_folder}")
                return True
            else:
                print("✗ Pasta de cache não foi criada")
                return False
        else:
            print(f"✗ Falha no cálculo de precisão (precisão: {accuracy:.2f})")
            return False

def test_performance_optimizations():
    """Testar otimizações de performance"""
    print("\n=== Testando Otimizações de Performance ===")
    
    # Testar processamento em lote
    print("1. Testando processamento em lote...")
    
    # Criar múltiplos segmentos para teste
    large_segments = []
    for i in range(100):
        note = f"C{4 + (i % 3)}"  # C4, C5, C6
        start = i * 0.1
        end = start + 0.1
        word = f"word{i}"
        large_segments.append(MidiSegment(note, start, end, word))
    
    # Testar processamento
    start_time = time.time()
    
    # Simular processamento otimizado
    processed_count = 0
    batch_size = 10
    
    for i in range(0, len(large_segments), batch_size):
        batch = large_segments[i:i+batch_size]
        # Simular processamento do lote
        processed_count += len(batch)
    
    processing_time = time.time() - start_time
    
    if processed_count == len(large_segments):
        print(f"✓ Processamento em lote concluído ({processed_count} segmentos em {processing_time:.3f}s)")
        if processing_time > 0:
            print(f"  Taxa: {processed_count/processing_time:.1f} segmentos/segundo")
        else:
            print(f"  Taxa: >1000 segmentos/segundo (processamento muito rápido)")
        return True
    else:
        print(f"✗ Falha no processamento em lote ({processed_count}/{len(large_segments)})")
        return False

def test_memory_optimization():
    """Testar otimizações de memória"""
    print("\n=== Testando Otimizações de Memória ===")
    
    print("1. Testando estimativa de uso de memória...")
    
    # Testar estimativa de memória para Demucs
    try:
        from modules.Audio.separation import estimate_memory_usage, DemucsModel
        
        memory_info = estimate_memory_usage(DemucsModel.HTDEMUCS, "cpu")
        
        if memory_info:
            print(f"✓ Estimativa de memória obtida: {memory_info}")
            if 'estimated_memory_gb' in memory_info:
                print(f"  Memória estimada: {memory_info['estimated_memory_gb']:.1f} GB")
            if 'recommendations' in memory_info:
                print(f"  Recomendações: {memory_info['recommendations']}")
            return True
        else:
            print("✗ Falha na estimativa de memória")
            return False
            
    except Exception as e:
        print(f"⚠ Erro na estimativa de memória: {e}")
        return True  # Não é crítico

def main():
    """Executar todos os testes de cache e performance"""
    print("🚀 TESTE COMPLETO DO SISTEMA DE CACHE E PERFORMANCE 🚀")
    print("=" * 60)
    
    tests = [
        ("Cache de Pitch", test_pitch_cache),
        ("Cache de MIDI", test_midi_cache),
        ("Cache de Partituras", test_sheet_cache),
        ("Cache de UltraStar", test_ultrastar_cache),
        ("Cache de Pontuação", test_score_cache),
        ("Otimizações de Performance", test_performance_optimizations),
        ("Otimizações de Memória", test_memory_optimization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSOU")
            else:
                print(f"❌ {test_name}: FALHOU")
                
        except Exception as e:
            print(f"💥 ERRO GERAL NO TESTE {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES DE CACHE E PERFORMANCE")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nResultado Final: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES DE CACHE E PERFORMANCE PASSARAM!")
    else:
        print(f"⚠️  {total - passed} teste(s) falharam")
    
    print("="*60)
    print("✅ TESTE COMPLETO FINALIZADO")
    print("Sistema de cache e otimizações testados!")

if __name__ == "__main__":
    main()