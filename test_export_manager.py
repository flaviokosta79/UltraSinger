#!/usr/bin/env python3
"""
Teste abrangente do sistema de exportação em múltiplos formatos
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.export_manager import ExportManager
from modules.error_handler import ErrorHandler
from modules.console_colors import ULTRASINGER_HEAD, green_highlighted, red_highlighted, blue_highlighted


def create_test_data():
    """Criar dados de teste para exportação"""
    return {
        'title': 'Test Song',
        'artist': 'Test Artist',
        'bpm': 120,
        'language': 'pt-BR',
        'genre': 'Pop',
        'year': '2023',
        'mp3': 'test_song.mp3',
        'gap': 0,
        'notes': [
            {'type': ':', 'start': 0, 'length': 4, 'pitch': 60, 'text': 'Test'},
            {'type': ':', 'start': 4, 'length': 4, 'pitch': 62, 'text': 'Song'},
            {'type': ':', 'start': 8, 'length': 4, 'pitch': 64, 'text': 'Export'},
            {'type': 'E', 'start': 12, 'length': 0, 'pitch': 0, 'text': ''}
        ],
        'segments': [
            {
                'start_time': 0.0,
                'end_time': 2.0,
                'pitch': 60,
                'text': 'Test',
                'confidence': 0.95
            },
            {
                'start_time': 2.0,
                'end_time': 4.0,
                'pitch': 62,
                'text': 'Song',
                'confidence': 0.92
            },
            {
                'start_time': 4.0,
                'end_time': 6.0,
                'pitch': 64,
                'text': 'Export',
                'confidence': 0.88
            }
        ]
    }


def test_ultrastar_export():
    """Testar exportação para formato UltraStar.txt"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Exportação UltraStar ===')}")
    
    export_manager = ExportManager()
    test_data = create_test_data()
    
    try:
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, "test_song.txt")
        
        print("\n1. Exportando para formato UltraStar.txt...")
        result = export_manager.export_ultrastar(test_data, output_file)
        
        if result['success'] and os.path.exists(output_file):
            print(f"✓ {green_highlighted('Exportação UltraStar bem-sucedida')}")
            print(f"  - Arquivo: {result['file_path']}")
            print(f"  - Tamanho: {result['file_size']} bytes")
            
            # Verificar conteúdo do arquivo
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if '#TITLE:Test Song' in content and '#ARTIST:Test Artist' in content:
                print(f"✓ {green_highlighted('Conteúdo UltraStar válido')}")
            else:
                print(f"✗ {red_highlighted('Conteúdo UltraStar inválido')}")
                
        else:
            print(f"✗ {red_highlighted('Falha na exportação UltraStar')}")
            print(f"  - Erro: {result.get('error', 'Desconhecido')}")
        
        # Limpar
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de exportação UltraStar: {e}')}")
        return False


def test_midi_export():
    """Testar exportação para formato MIDI"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Exportação MIDI ===')}")
    
    export_manager = ExportManager()
    test_data = create_test_data()
    
    try:
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, "test_song.mid")
        
        print("\n1. Exportando para formato MIDI...")
        result = export_manager.export_midi(test_data, output_file)
        
        if result['success'] and os.path.exists(output_file):
            print(f"✓ {green_highlighted('Exportação MIDI bem-sucedida')}")
            print(f"  - Arquivo: {result['file_path']}")
            print(f"  - Tamanho: {result['file_size']} bytes")
            print(f"  - Duração: {result.get('duration', 'N/A')} segundos")
            print(f"  - Notas: {result.get('note_count', 0)}")
        else:
            print(f"✗ {red_highlighted('Falha na exportação MIDI')}")
            print(f"  - Erro: {result.get('error', 'Desconhecido')}")
        
        # Limpar
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de exportação MIDI: {e}')}")
        return False


def test_json_export():
    """Testar exportação para formato JSON"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Exportação JSON ===')}")
    
    export_manager = ExportManager()
    test_data = create_test_data()
    
    try:
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, "test_song.json")
        
        print("\n1. Exportando para formato JSON...")
        result = export_manager.export_json(test_data, output_file)
        
        if result['success'] and os.path.exists(output_file):
            print(f"✓ {green_highlighted('Exportação JSON bem-sucedida')}")
            print(f"  - Arquivo: {result['file_path']}")
            print(f"  - Tamanho: {result['file_size']} bytes")
            
            # Verificar se é JSON válido
            with open(output_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                
            if 'metadata' in json_data and 'notes' in json_data:
                print(f"✓ {green_highlighted('JSON válido com estrutura correta')}")
                print(f"  - Metadados: {len(json_data['metadata'])} campos")
                print(f"  - Notas: {len(json_data['notes'])} itens")
            else:
                print(f"✗ {red_highlighted('Estrutura JSON inválida')}")
                
        else:
            print(f"✗ {red_highlighted('Falha na exportação JSON')}")
            print(f"  - Erro: {result.get('error', 'Desconhecido')}")
        
        # Limpar
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de exportação JSON: {e}')}")
        return False


def test_csv_export():
    """Testar exportação para formato CSV"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Exportação CSV ===')}")
    
    export_manager = ExportManager()
    test_data = create_test_data()
    
    try:
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, "test_song.csv")
        
        print("\n1. Exportando para formato CSV...")
        result = export_manager.export_csv(test_data, output_file)
        
        if result['success'] and os.path.exists(output_file):
            print(f"✓ {green_highlighted('Exportação CSV bem-sucedida')}")
            print(f"  - Arquivo: {result['file_path']}")
            print(f"  - Tamanho: {result['file_size']} bytes")
            
            # Verificar conteúdo CSV
            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            if len(lines) > 1 and 'start_time' in lines[0]:
                print(f"✓ {green_highlighted('CSV válido com cabeçalho')}")
                print(f"  - Linhas: {len(lines)} (incluindo cabeçalho)")
            else:
                print(f"✗ {red_highlighted('CSV inválido')}")
                
        else:
            print(f"✗ {red_highlighted('Falha na exportação CSV')}")
            print(f"  - Erro: {result.get('error', 'Desconhecido')}")
        
        # Limpar
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de exportação CSV: {e}')}")
        return False


def test_lyrics_export():
    """Testar exportação de letras"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Exportação de Letras ===')}")
    
    export_manager = ExportManager()
    test_data = create_test_data()
    
    try:
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, "test_song_lyrics.txt")
        
        print("\n1. Exportando letras...")
        result = export_manager.export_lyrics(test_data, output_file)
        
        if result['success'] and os.path.exists(output_file):
            print(f"✓ {green_highlighted('Exportação de letras bem-sucedida')}")
            print(f"  - Arquivo: {result['file_path']}")
            print(f"  - Tamanho: {result['file_size']} bytes")
            
            # Verificar conteúdo das letras
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'Test Song Export' in content:
                print(f"✓ {green_highlighted('Letras extraídas corretamente')}")
            else:
                print(f"✗ {red_highlighted('Letras não extraídas corretamente')}")
                
        else:
            print(f"✗ {red_highlighted('Falha na exportação de letras')}")
            print(f"  - Erro: {result.get('error', 'Desconhecido')}")
        
        # Limpar
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de exportação de letras: {e}')}")
        return False


def test_batch_export():
    """Testar exportação em lote"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Exportação em Lote ===')}")
    
    export_manager = ExportManager()
    test_data = create_test_data()
    
    try:
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp()
        
        # Formatos para exportação em lote
        formats = ['ultrastar', 'midi', 'json', 'csv', 'lyrics']
        
        print(f"\n1. Exportando em {len(formats)} formatos...")
        results = export_manager.export_multiple_formats(
            test_data, temp_dir, formats
        )
        
        successful_exports = sum(1 for r in results.values() if r['success'])
        
        print(f"✓ {green_highlighted(f'Exportação em lote concluída')}")
        print(f"  - Formatos solicitados: {len(formats)}")
        print(f"  - Exportações bem-sucedidas: {successful_exports}")
        print(f"  - Taxa de sucesso: {(successful_exports/len(formats))*100:.1f}%")
        
        # Verificar arquivos criados
        created_files = []
        for root, dirs, files in os.walk(temp_dir):
            created_files.extend(files)
        
        print(f"  - Arquivos criados: {len(created_files)}")
        for file in created_files:
            print(f"    • {file}")
        
        # Gerar relatório de exportação
        print(f"\n2. Gerando relatório de exportação...")
        report = export_manager.generate_export_report(results)
        
        if report:
            print(f"✓ {green_highlighted('Relatório gerado com sucesso')}")
            print(f"  - Total de exportações: {report['summary']['total_exports']}")
            print(f"  - Exportações bem-sucedidas: {report['summary']['successful_exports']}")
            print(f"  - Exportações falharam: {report['summary']['failed_exports']}")
        
        # Limpar
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return successful_exports >= len(formats) * 0.8  # 80% de sucesso mínimo
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de exportação em lote: {e}')}")
        return False


def test_export_validation():
    """Testar validação de exportações"""
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== Teste de Validação de Exportações ===')}")
    
    export_manager = ExportManager()
    test_data = create_test_data()
    
    try:
        # Teste 1: Dados inválidos
        print("\n1. Testando exportação com dados inválidos...")
        invalid_data = {}  # Dados vazios
        
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, "invalid.txt")
        
        result = export_manager.export_ultrastar(invalid_data, output_file)
        
        if not result['success']:
            print(f"✓ {green_highlighted('Dados inválidos detectados corretamente')}")
            print(f"  - Erro: {result.get('error', 'N/A')}")
        else:
            print(f"✗ {red_highlighted('Dados inválidos não foram detectados')}")
        
        # Teste 2: Caminho inválido
        print("\n2. Testando exportação com caminho inválido...")
        invalid_path = "/caminho/inexistente/arquivo.txt"
        
        result = export_manager.export_ultrastar(test_data, invalid_path)
        
        if not result['success']:
            print(f"✓ {green_highlighted('Caminho inválido detectado corretamente')}")
        else:
            print(f"✗ {red_highlighted('Caminho inválido não foi detectado')}")
        
        # Teste 3: Formato não suportado
        print("\n3. Testando formato não suportado...")
        
        try:
            result = export_manager.export_multiple_formats(
                test_data, temp_dir, ['formato_inexistente']
            )
            
            if 'formato_inexistente' in result and not result['formato_inexistente']['success']:
                print(f"✓ {green_highlighted('Formato não suportado detectado')}")
            else:
                print(f"✗ {red_highlighted('Formato não suportado não foi detectado')}")
        except Exception as e:
            print(f"✓ {green_highlighted(f'Formato não suportado rejeitado: {e}')}")
        
        # Limpar
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro no teste de validação: {e}')}")
        return False


def main():
    """Executar todos os testes de exportação"""
    print(f"{ULTRASINGER_HEAD} {blue_highlighted('🎵 INICIANDO TESTES DE EXPORTAÇÃO 🎵')}")
    print("=" * 70)
    
    tests = [
        ("Exportação UltraStar", test_ultrastar_export),
        ("Exportação MIDI", test_midi_export),
        ("Exportação JSON", test_json_export),
        ("Exportação CSV", test_csv_export),
        ("Exportação de Letras", test_lyrics_export),
        ("Exportação em Lote", test_batch_export),
        ("Validação de Exportações", test_export_validation)
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
    print(f"{ULTRASINGER_HEAD} {blue_highlighted('RESUMO DOS TESTES DE EXPORTAÇÃO')}")
    print(f"Testes executados: {total}")
    print(f"Testes aprovados: {green_highlighted(str(passed))}")
    print(f"Testes falharam: {red_highlighted(str(total - passed))}")
    print(f"Taxa de sucesso: {green_highlighted(f'{(passed/total)*100:.1f}%')}")
    
    if passed == total:
        print(f"\n🎉 {green_highlighted('TODOS OS TESTES DE EXPORTAÇÃO PASSARAM!')}")
        return True
    else:
        print(f"\n⚠️ {red_highlighted('ALGUNS TESTES FALHARAM - VERIFICAR IMPLEMENTAÇÃO')}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)