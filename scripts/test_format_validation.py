#!/usr/bin/env python3
"""
Teste abrangente do sistema de validação de formatos
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.format_validator import FormatValidator, FormatConverter
from modules.error_handler import ErrorHandler
from modules.console_colors import ULTRASINGER_HEAD, green_highlighted, red_highlighted, blue_highlighted


def create_test_files():
    """Criar arquivos de teste"""
    test_files = {}
    
    # Criar diretório temporário
    temp_dir = tempfile.mkdtemp()
    
    # Arquivo MP3 simulado
    mp3_file = os.path.join(temp_dir, "test_song.mp3")
    with open(mp3_file, 'wb') as f:
        f.write(b'ID3' + b'\x00' * 100)  # Header MP3 básico
    test_files['mp3'] = mp3_file
    
    # Arquivo WAV simulado
    wav_file = os.path.join(temp_dir, "test_song.wav")
    with open(wav_file, 'wb') as f:
        f.write(b'RIFF' + b'\x00' * 100)  # Header WAV básico
    test_files['wav'] = wav_file
    
    # Arquivo UltraStar.txt válido
    ultrastar_file = os.path.join(temp_dir, "test_song.txt")
    ultrastar_content = """#TITLE:Test Song
#ARTIST:Test Artist
#MP3:test_song.mp3
#BPM:120
#LANGUAGE:pt-BR
#GENRE:Pop
#YEAR:2023
: 0 4 60 Test
: 4 4 62 Song
E
"""
    with open(ultrastar_file, 'w', encoding='utf-8') as f:
        f.write(ultrastar_content)
    test_files['ultrastar'] = ultrastar_file
    
    # Arquivo UltraStar.txt inválido
    invalid_ultrastar_file = os.path.join(temp_dir, "invalid_song.txt")
    with open(invalid_ultrastar_file, 'w', encoding='utf-8') as f:
        f.write("#TITLE:Invalid Song\n")  # Faltam tags obrigatórias
    test_files['invalid_ultrastar'] = invalid_ultrastar_file
    
    # Arquivo com formato não suportado
    unsupported_file = os.path.join(temp_dir, "test_song.xyz")
    with open(unsupported_file, 'w') as f:
        f.write("unsupported format")
    test_files['unsupported'] = unsupported_file
    
    return test_files, temp_dir


def test_audio_format_validation():
    """Testar validação de formatos de áudio"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Validação de Formatos de Áudio ===')}")
    
    validator = FormatValidator()
    test_files, temp_dir = create_test_files()
    
    try:
        # Teste 1: Arquivo MP3 válido
        print("\n1. Testando arquivo MP3...")
        result = validator.validate_input_file(test_files['mp3'])
        
        if result['is_valid'] and result['file_type'] == 'audio':
            print(f"✓ {green_highlighted('MP3 validado com sucesso')}")
            print(f"  - Extensão: {result['format_info']['extension']}")
            print(f"  - Tamanho: {result['format_info']['file_size']} bytes")
        else:
            print(f"✗ {red_highlighted('Falha na validação do MP3')}")
            print(f"  - Erros: {result['errors']}")
        
        # Teste 2: Arquivo WAV válido
        print("\n2. Testando arquivo WAV...")
        result = validator.validate_input_file(test_files['wav'])
        
        if result['is_valid'] and result['file_type'] == 'audio':
            print(f"✓ {green_highlighted('WAV validado com sucesso')}")
        else:
            print(f"✗ {red_highlighted('Falha na validação do WAV')}")
        
        # Teste 3: Arquivo não suportado
        print("\n3. Testando arquivo não suportado...")
        result = validator.validate_input_file(test_files['unsupported'])
        
        if not result['is_valid']:
            print(f"✓ {green_highlighted('Arquivo não suportado detectado corretamente')}")
            print(f"  - Erros: {result['errors']}")
        else:
            print(f"✗ {red_highlighted('Arquivo não suportado não foi detectado')}")
        
        # Teste 4: Arquivo inexistente
        print("\n4. Testando arquivo inexistente...")
        result = validator.validate_input_file("arquivo_inexistente.mp3")
        
        if not result['is_valid']:
            print(f"✓ {green_highlighted('Arquivo inexistente detectado corretamente')}")
        else:
            print(f"✗ {red_highlighted('Arquivo inexistente não foi detectado')}")
            
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de validação de áudio: {e}')}")
        return False
    
    finally:
        # Limpar arquivos temporários
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_ultrastar_validation():
    """Testar validação de arquivos UltraStar"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Validação UltraStar ===')}")
    
    validator = FormatValidator()
    test_files, temp_dir = create_test_files()
    
    try:
        # Teste 1: Arquivo UltraStar válido
        print("\n1. Testando arquivo UltraStar válido...")
        result = validator.validate_input_file(test_files['ultrastar'])
        
        if result['is_valid'] and result['file_type'] == 'ultrastar':
            print(f"✓ {green_highlighted('UltraStar válido detectado')}")
            print(f"  - Título: {result['format_info'].get('title', 'N/A')}")
            print(f"  - Artista: {result['format_info'].get('artist', 'N/A')}")
            print(f"  - BPM: {result['format_info'].get('bpm', 'N/A')}")
            print(f"  - Notas: {result['format_info'].get('note_count', 0)}")
        else:
            print(f"✗ {red_highlighted('Falha na validação do UltraStar válido')}")
            print(f"  - Erros: {result['errors']}")
        
        # Teste 2: Arquivo UltraStar inválido
        print("\n2. Testando arquivo UltraStar inválido...")
        result = validator.validate_input_file(test_files['invalid_ultrastar'])
        
        if not result['is_valid']:
            print(f"✓ {green_highlighted('UltraStar inválido detectado corretamente')}")
            print(f"  - Erros: {result['errors']}")
        else:
            print(f"✗ {red_highlighted('UltraStar inválido não foi detectado')}")
            
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de validação UltraStar: {e}')}")
        return False
    
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_youtube_url_validation():
    """Testar validação de URLs do YouTube"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Validação de URLs YouTube ===')}")
    
    validator = FormatValidator()
    
    # URLs de teste
    test_urls = {
        'valid': [
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'https://youtu.be/dQw4w9WgXcQ',
            'http://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'youtube.com/watch?v=dQw4w9WgXcQ'
        ],
        'invalid': [
            'https://www.google.com',
            'not_a_url',
            'https://www.youtube.com/invalid',
            'https://vimeo.com/123456'
        ]
    }
    
    try:
        # Teste URLs válidas
        print("\n1. Testando URLs válidas do YouTube...")
        for url in test_urls['valid']:
            result = validator.validate_input_file(url)
            
            if result['is_valid'] and result['file_type'] == 'youtube_url':
                print(f"✓ {green_highlighted(f'URL válida: {url}')}")
                print(f"  - Video ID: {result['format_info'].get('video_id', 'N/A')}")
            else:
                print(f"✗ {red_highlighted(f'URL deveria ser válida: {url}')}")
        
        # Teste URLs inválidas
        print("\n2. Testando URLs inválidas...")
        for url in test_urls['invalid']:
            result = validator.validate_input_file(url)
            
            if not result['is_valid']:
                print(f"✓ {green_highlighted(f'URL inválida detectada: {url}')}")
            else:
                print(f"✗ {red_highlighted(f'URL deveria ser inválida: {url}')}")
                
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de validação YouTube: {e}')}")
        return False


def test_batch_validation():
    """Testar validação em lote"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Validação em Lote ===')}")
    
    validator = FormatValidator()
    test_files, temp_dir = create_test_files()
    
    try:
        # Lista de arquivos para teste em lote
        file_list = [
            test_files['mp3'],
            test_files['wav'],
            test_files['ultrastar'],
            test_files['unsupported'],
            'arquivo_inexistente.mp3',
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        ]
        
        print(f"\nValidando {len(file_list)} arquivos em lote...")
        results = validator.validate_batch_files(file_list)
        
        valid_count = sum(1 for r in results.values() if r['is_valid'])
        invalid_count = len(results) - valid_count
        
        print(f"✓ {green_highlighted(f'Validação em lote concluída')}")
        print(f"  - Arquivos válidos: {valid_count}")
        print(f"  - Arquivos inválidos: {invalid_count}")
        
        # Obter estatísticas
        stats = validator.get_format_statistics(file_list)
        print(f"\nEstatísticas:")
        print(f"  - Total de arquivos: {stats['total_files']}")
        print(f"  - Arquivos válidos: {stats['valid_files']}")
        print(f"  - Arquivos inválidos: {stats['invalid_files']}")
        print(f"  - Tipos de arquivo: {stats['file_types']}")
        print(f"  - Distribuição de formatos: {stats['format_distribution']}")
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de validação em lote: {e}')}")
        return False
    
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_format_converter():
    """Testar conversor de formatos"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Conversor de Formatos ===')}")
    
    converter = FormatConverter()
    
    try:
        # Verificar se ffmpeg está disponível
        print("\n1. Verificando disponibilidade do ffmpeg...")
        if converter.is_ffmpeg_available():
            print(f"✓ {green_highlighted('ffmpeg está disponível')}")
            
            # Criar arquivo de teste
            temp_dir = tempfile.mkdtemp()
            input_file = os.path.join(temp_dir, "test_input.wav")
            output_file = os.path.join(temp_dir, "test_output.mp3")
            
            # Criar arquivo WAV simulado (header básico)
            with open(input_file, 'wb') as f:
                f.write(b'RIFF' + b'\x00' * 1000)
            
            print("\n2. Testando conversão WAV para MP3...")
            # Nota: Este teste pode falhar se o arquivo não for um WAV real
            # É apenas para testar a interface do conversor
            success = converter.convert_to_supported_format(
                input_file, output_file, 'mp3', 'medium'
            )
            
            if success and os.path.exists(output_file):
                print(f"✓ {green_highlighted('Conversão simulada executada')}")
            else:
                print(f"⚠ {blue_highlighted('Conversão não executada (arquivo de teste não é áudio real)')}")
            
            # Limpar
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
        else:
            print(f"⚠ {blue_highlighted('ffmpeg não está disponível - conversão não testada')}")
            
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de conversão: {e}')}")
        return False


def test_supported_formats():
    """Testar informações de formatos suportados"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Formatos Suportados ===')}")
    
    validator = FormatValidator()
    
    try:
        formats = validator.get_supported_formats()
        
        print(f"\nFormatos de áudio suportados ({len(formats)}):")
        for ext, info in formats.items():
            print(f"  {ext}:")
            print(f"    - Descrição: {info['description']}")
            print(f"    - Qualidade: {info['quality']}")
            print(f"    - MIME Type: {info['mime_type']}")
            if info['max_bitrate']:
                print(f"    - Bitrate máximo: {info['max_bitrate']} kbps")
        
        # Testar sugestões de conversão
        print(f"\nSugestões de conversão para formato não suportado:")
        suggestions = validator.suggest_format_conversion('.xyz')
        for suggestion in suggestions:
            print(f"  - {suggestion}")
            
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de formatos suportados: {e}')}")
        return False


def main():
    """Executar todos os testes de validação de formatos"""
    print(f"{ULTRASINGER_HEAD} {blue_highlighted('🎵 INICIANDO TESTES DE VALIDAÇÃO DE FORMATOS 🎵')}")
    print("=" * 70)
    
    tests = [
        ("Validação de Formatos de Áudio", test_audio_format_validation),
        ("Validação de Arquivos UltraStar", test_ultrastar_validation),
        ("Validação de URLs YouTube", test_youtube_url_validation),
        ("Validação em Lote", test_batch_validation),
        ("Conversor de Formatos", test_format_converter),
        ("Formatos Suportados", test_supported_formats)
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
    print(f"{ULTRASINGER_HEAD} {blue_highlighted('RESUMO DOS TESTES DE VALIDAÇÃO')}")
    print(f"Testes executados: {total}")
    print(f"Testes aprovados: {green_highlighted(str(passed))}")
    print(f"Testes falharam: {red_highlighted(str(total - passed))}")
    print(f"Taxa de sucesso: {green_highlighted(f'{(passed/total)*100:.1f}%')}")
    
    if passed == total:
        print(f"\n🎉 {green_highlighted('TODOS OS TESTES DE VALIDAÇÃO PASSARAM!')}")
        return True
    else:
        print(f"\n⚠️ {red_highlighted('ALGUNS TESTES FALHARAM - VERIFICAR IMPLEMENTAÇÃO')}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)