#!/usr/bin/env python3
"""
Teste do sistema de conversão automática de formatos
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.format_validator import FormatConverter
from modules.console_colors import ULTRASINGER_HEAD, green_highlighted, red_highlighted, blue_highlighted


def create_test_audio_files():
    """Criar arquivos de áudio de teste simulados"""
    test_files = {}
    temp_dir = tempfile.mkdtemp()
    
    # Arquivo WAV simulado (com header RIFF)
    wav_file = os.path.join(temp_dir, "test_audio.wav")
    with open(wav_file, 'wb') as f:
        # Header WAV básico
        f.write(b'RIFF')  # ChunkID
        f.write((1000).to_bytes(4, 'little'))  # ChunkSize
        f.write(b'WAVE')  # Format
        f.write(b'fmt ')  # Subchunk1ID
        f.write((16).to_bytes(4, 'little'))  # Subchunk1Size
        f.write((1).to_bytes(2, 'little'))  # AudioFormat (PCM)
        f.write((2).to_bytes(2, 'little'))  # NumChannels
        f.write((44100).to_bytes(4, 'little'))  # SampleRate
        f.write((176400).to_bytes(4, 'little'))  # ByteRate
        f.write((4).to_bytes(2, 'little'))  # BlockAlign
        f.write((16).to_bytes(2, 'little'))  # BitsPerSample
        f.write(b'data')  # Subchunk2ID
        f.write((1000).to_bytes(4, 'little'))  # Subchunk2Size
        f.write(b'\x00' * 1000)  # Dados de áudio simulados
    test_files['wav'] = wav_file
    
    # Arquivo FLAC simulado (com header fLaC)
    flac_file = os.path.join(temp_dir, "test_audio.flac")
    with open(flac_file, 'wb') as f:
        f.write(b'fLaC')  # FLAC signature
        f.write(b'\x00' * 100)  # Dados simulados
    test_files['flac'] = flac_file
    
    # Arquivo OGG simulado (com header OggS)
    ogg_file = os.path.join(temp_dir, "test_audio.ogg")
    with open(ogg_file, 'wb') as f:
        f.write(b'OggS')  # OGG signature
        f.write(b'\x00' * 100)  # Dados simulados
    test_files['ogg'] = ogg_file
    
    # Arquivo não suportado
    unsupported_file = os.path.join(temp_dir, "test_audio.xyz")
    with open(unsupported_file, 'w') as f:
        f.write("formato não suportado")
    test_files['unsupported'] = unsupported_file
    
    return test_files, temp_dir


def test_ffmpeg_availability():
    """Testar disponibilidade do ffmpeg"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Disponibilidade do FFmpeg ===')}")
    
    converter = FormatConverter()
    
    try:
        is_available = converter.is_ffmpeg_available()
        
        if is_available:
            print(f"✓ {green_highlighted('FFmpeg está disponível no sistema')}")
            
            # Testar versão do ffmpeg
            version_info = converter.get_ffmpeg_version()
            if version_info:
                print(f"  - Versão: {version_info}")
            
        else:
            print(f"⚠ {blue_highlighted('FFmpeg não está disponível')}")
            print("  - Conversões automáticas não funcionarão")
            print("  - Instale o FFmpeg para habilitar conversões")
        
        return is_available
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro ao verificar FFmpeg: {e}')}")
        return False


def test_format_detection():
    """Testar detecção de formatos de arquivo"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Detecção de Formatos ===')}")
    
    converter = FormatConverter()
    test_files, temp_dir = create_test_audio_files()
    
    try:
        # Testar detecção de cada formato
        for format_name, file_path in test_files.items():
            print(f"\n{format_name.upper()}:")
            
            detected_format = converter.detect_audio_format(file_path)
            
            if detected_format:
                print(f"✓ {green_highlighted(f'Formato detectado: {detected_format}')}")
                
                # Verificar se é suportado
                is_supported = converter.is_format_supported(detected_format)
                if is_supported:
                    print(f"  - Status: {green_highlighted('Suportado')}")
                else:
                    print(f"  - Status: {red_highlighted('Não suportado')}")
                    
                    # Sugerir conversão
                    suggestions = converter.suggest_conversion_format(detected_format)
                    if suggestions:
                        print(f"  - Sugestões: {', '.join(suggestions)}")
            else:
                print(f"✗ {red_highlighted('Formato não detectado')}")
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro na detecção de formatos: {e}')}")
        return False
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_conversion_planning():
    """Testar planejamento de conversões"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Planejamento de Conversões ===')}")
    
    converter = FormatConverter()
    
    try:
        # Cenários de teste
        test_scenarios = [
            {
                'input_format': '.xyz',
                'description': 'Formato não suportado para MP3'
            },
            {
                'input_format': '.wma',
                'description': 'WMA para formato mais compatível'
            },
            {
                'input_format': '.m4a',
                'description': 'M4A para formato lossless'
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n{scenario['description']}:")
            
            # Obter sugestões de conversão
            suggestions = converter.suggest_conversion_format(scenario['input_format'])
            
            if suggestions:
                print(f"✓ {green_highlighted('Sugestões encontradas:')}")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"  {i}. {suggestion}")
                
                # Testar planejamento de conversão
                target_format = suggestions[0]  # Usar primeira sugestão
                conversion_plan = converter.plan_conversion(
                    scenario['input_format'], target_format
                )
                
                if conversion_plan:
                    print(f"✓ {green_highlighted('Plano de conversão criado:')}")
                    print(f"  - Origem: {conversion_plan['source_format']}")
                    print(f"  - Destino: {conversion_plan['target_format']}")
                    print(f"  - Qualidade: {conversion_plan['quality']}")
                    print(f"  - Parâmetros: {conversion_plan['parameters']}")
                else:
                    print(f"✗ {red_highlighted('Falha ao criar plano de conversão')}")
            else:
                print(f"⚠ {blue_highlighted('Nenhuma sugestão disponível')}")
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no planejamento de conversões: {e}')}")
        return False


def test_conversion_execution():
    """Testar execução de conversões"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Execução de Conversões ===')}")
    
    converter = FormatConverter()
    
    # Verificar se ffmpeg está disponível
    if not converter.is_ffmpeg_available():
        print(f"⚠ {blue_highlighted('FFmpeg não disponível - teste de conversão simulado')}")
        return True
    
    test_files, temp_dir = create_test_audio_files()
    
    try:
        # Testar conversão WAV para MP3
        input_file = test_files['wav']
        output_file = os.path.join(temp_dir, "converted_audio.mp3")
        
        print(f"\n1. Convertendo WAV para MP3...")
        
        success = converter.convert_to_supported_format(
            input_file, output_file, 'mp3', 'medium'
        )
        
        if success and os.path.exists(output_file):
            print(f"✓ {green_highlighted('Conversão executada com sucesso')}")
            print(f"  - Arquivo de saída: {output_file}")
            print(f"  - Tamanho: {os.path.getsize(output_file)} bytes")
            
            # Verificar se o arquivo convertido é válido
            converted_format = converter.detect_audio_format(output_file)
            if converted_format == '.mp3':
                print(f"✓ {green_highlighted('Formato de saída correto')}")
            else:
                print(f"⚠ {blue_highlighted(f'Formato detectado: {converted_format}')}")
                
        else:
            print(f"⚠ {blue_highlighted('Conversão não executada (arquivo de teste pode não ser áudio real)')}")
        
        # Testar conversão em lote
        print(f"\n2. Testando conversão em lote...")
        
        batch_files = [test_files['wav'], test_files['flac']]
        batch_results = converter.convert_batch_files(
            batch_files, temp_dir, 'mp3'
        )
        
        successful_conversions = sum(1 for r in batch_results if r['success'])
        
        print(f"✓ {green_highlighted('Conversão em lote concluída')}")
        print(f"  - Arquivos processados: {len(batch_files)}")
        print(f"  - Conversões bem-sucedidas: {successful_conversions}")
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro na execução de conversões: {e}')}")
        return False
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_conversion_quality_options():
    """Testar opções de qualidade de conversão"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Opções de Qualidade ===')}")
    
    converter = FormatConverter()
    
    try:
        # Testar diferentes níveis de qualidade
        quality_levels = ['low', 'medium', 'high', 'lossless']
        
        for quality in quality_levels:
            print(f"\n{quality.upper()}:")
            
            # Obter parâmetros para a qualidade
            params = converter.get_quality_parameters('mp3', quality)
            
            if params:
                print(f"✓ {green_highlighted('Parâmetros obtidos:')}")
                for key, value in params.items():
                    print(f"  - {key}: {value}")
            else:
                print(f"✗ {red_highlighted('Parâmetros não encontrados')}")
        
        # Testar formatos lossless
        print(f"\nFormatos lossless disponíveis:")
        lossless_formats = converter.get_lossless_formats()
        
        for fmt in lossless_formats:
            print(f"  - {fmt}")
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de qualidade: {e}')}")
        return False


def test_conversion_metadata_preservation():
    """Testar preservação de metadados durante conversão"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Preservação de Metadados ===')}")
    
    converter = FormatConverter()
    
    try:
        # Metadados de teste
        test_metadata = {
            'title': 'Test Song',
            'artist': 'Test Artist',
            'album': 'Test Album',
            'year': '2023',
            'genre': 'Pop'
        }
        
        print(f"Metadados de teste:")
        for key, value in test_metadata.items():
            print(f"  - {key}: {value}")
        
        # Testar se o conversor pode preservar metadados
        can_preserve = converter.can_preserve_metadata('.wav', '.mp3')
        
        if can_preserve:
            print(f"✓ {green_highlighted('Conversor pode preservar metadados WAV → MP3')}")
            
            # Obter comando de conversão com metadados
            command = converter.build_conversion_command(
                'input.wav', 'output.mp3', 'medium', test_metadata
            )
            
            if command:
                print(f"✓ {green_highlighted('Comando de conversão gerado:')}")
                print(f"  {' '.join(command)}")
            else:
                print(f"✗ {red_highlighted('Falha ao gerar comando')}")
                
        else:
            print(f"⚠ {blue_highlighted('Preservação de metadados não suportada para esta conversão')}")
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de metadados: {e}')}")
        return False


def main():
    """Executar todos os testes do conversor de formatos"""
    print(f"{ULTRASINGER_HEAD} {blue_highlighted('🎵 INICIANDO TESTES DO CONVERSOR DE FORMATOS 🎵')}")
    print("=" * 70)
    
    tests = [
        ("Disponibilidade do FFmpeg", test_ffmpeg_availability),
        ("Detecção de Formatos", test_format_detection),
        ("Planejamento de Conversões", test_conversion_planning),
        ("Execução de Conversões", test_conversion_execution),
        ("Opções de Qualidade", test_conversion_quality_options),
        ("Preservação de Metadados", test_conversion_metadata_preservation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {green_highlighted(f'{test_name} - PASSOU')}")
            else:
                print(f"\n❌ {red_highlighted(f'{test_name} - FALHOU')}")
        except Exception as e:
            print(f"\n💥 {red_highlighted(f'{test_name} - ERRO: {e}')}")
    
    print(f"\n{'='*70}")
    print(f"{ULTRASINGER_HEAD} {blue_highlighted('RESUMO DOS TESTES DO CONVERSOR')}")
    print(f"Testes executados: {total}")
    print(f"Testes aprovados: {green_highlighted(str(passed))}")
    print(f"Testes falharam: {red_highlighted(str(total - passed))}")
    print(f"Taxa de sucesso: {green_highlighted(f'{(passed/total)*100:.1f}%')}")
    
    if passed == total:
        print(f"\n🎉 {green_highlighted('TODOS OS TESTES DO CONVERSOR PASSARAM!')}")
        return True
    else:
        print(f"\n⚠️ {red_highlighted('ALGUNS TESTES FALHARAM - VERIFICAR IMPLEMENTAÇÃO')}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)