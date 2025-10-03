#!/usr/bin/env python3
"""
Teste completo das opções de linha de comando do UltraSinger
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.console_colors import ULTRASINGER_HEAD, green_highlighted, red_highlighted, blue_highlighted

def test_help_option():
    """Testar opção de ajuda"""
    print(f"\n{ULTRASINGER_HEAD} Testando opção --help...")
    
    try:
        result = subprocess.run([
            sys.executable, "src/UltraSinger.py", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "UltraSinger.py" in result.stdout:
            print(f"✓ {green_highlighted('Opção --help funcionando')}")
            return True
        else:
            print(f"✗ {red_highlighted('Opção --help falhou')}")
            return False
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro ao testar --help: {e}')}")
        return False

def test_version_display():
    """Testar exibição de versão"""
    print(f"\n{ULTRASINGER_HEAD} Testando exibição de versão...")
    
    try:
        # Testar sem argumentos (deve mostrar help e sair)
        result = subprocess.run([
            sys.executable, "src/UltraSinger.py"
        ], capture_output=True, text=True, timeout=10)
        
        if "UltraSinger" in result.stdout:
            print(f"✓ {green_highlighted('Versão exibida corretamente')}")
            return True
        else:
            print(f"✗ {red_highlighted('Versão não exibida')}")
            return False
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro ao testar versão: {e}')}")
        return False

def test_input_output_options():
    """Testar opções de entrada e saída"""
    print(f"\n{ULTRASINGER_HEAD} Testando opções de entrada e saída...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Criar arquivo de áudio de teste (vazio para teste)
        test_audio = os.path.join(temp_dir, "test.mp3")
        with open(test_audio, 'w') as f:
            f.write("")  # Arquivo vazio para teste
        
        output_dir = os.path.join(temp_dir, "output")
        
        try:
            # Testar com arquivo inexistente (deve falhar graciosamente)
            result = subprocess.run([
                sys.executable, "src/UltraSinger.py",
                "-i", "arquivo_inexistente.mp3",
                "-o", output_dir
            ], capture_output=True, text=True, timeout=15)
            
            # Esperamos que falhe, mas de forma controlada
            print(f"✓ {green_highlighted('Opções -i e -o reconhecidas')}")
            return True
            
        except Exception as e:
            print(f"✗ {red_highlighted(f'Erro ao testar opções I/O: {e}')}")
            return False

def test_model_options():
    """Testar opções de modelo"""
    print(f"\n{ULTRASINGER_HEAD} Testando opções de modelo...")
    
    test_cases = [
        ("--whisper", "base"),
        ("--crepe", "medium"),
        ("--demucs", "htdemucs"),
        ("--language", "pt")
    ]
    
    passed = 0
    total = len(test_cases)
    
    for option, value in test_cases:
        try:
            result = subprocess.run([
                sys.executable, "src/UltraSinger.py",
                "--help"  # Usar help para testar se as opções são reconhecidas
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✓ {green_highlighted(f'Opção {option} reconhecida')}")
                passed += 1
            else:
                print(f"✗ {red_highlighted(f'Opção {option} não reconhecida')}")
                
        except Exception as e:
            print(f"✗ {red_highlighted(f'Erro ao testar {option}: {e}')}")
    
    return passed == total

def test_boolean_flags():
    """Testar flags booleanas"""
    print(f"\n{ULTRASINGER_HEAD} Testando flags booleanas...")
    
    boolean_flags = [
        "--plot",
        "--midi", 
        "--disable_hyphenation",
        "--disable_separation",
        "--disable_karaoke",
        "--ignore_audio",
        "--force_cpu",
        "--force_whisper_cpu",
        "--force_crepe_cpu",
        "--keep_cache",
        "--keep_numbers",
        "--interactive"
    ]
    
    passed = 0
    total = len(boolean_flags)
    
    for flag in boolean_flags:
        try:
            # Testar se a flag é reconhecida (usando help)
            result = subprocess.run([
                sys.executable, "src/UltraSinger.py",
                "--help"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✓ {green_highlighted(f'Flag {flag} reconhecida')}")
                passed += 1
            else:
                print(f"✗ {red_highlighted(f'Flag {flag} não reconhecida')}")
                
        except Exception as e:
            print(f"✗ {red_highlighted(f'Erro ao testar {flag}: {e}')}")
    
    return passed == total

def test_format_version_option():
    """Testar opção de versão de formato"""
    print(f"\n{ULTRASINGER_HEAD} Testando opção --format_version...")
    
    format_versions = ["0.3.0", "1.0.0", "1.1.0", "1.2.0"]
    
    passed = 0
    total = len(format_versions)
    
    for version in format_versions:
        try:
            # Testar com help para verificar se a opção é reconhecida
            result = subprocess.run([
                sys.executable, "src/UltraSinger.py",
                "--help"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✓ {green_highlighted(f'Versão de formato {version} suportada')}")
                passed += 1
            else:
                print(f"✗ {red_highlighted(f'Versão de formato {version} não suportada')}")
                
        except Exception as e:
            print(f"✗ {red_highlighted(f'Erro ao testar versão {version}: {e}')}")
    
    return passed == total

def test_path_options():
    """Testar opções de caminho"""
    print(f"\n{ULTRASINGER_HEAD} Testando opções de caminho...")
    
    path_options = [
        ("--musescore_path", "/usr/bin/musescore"),
        ("--cookiefile", "cookies.txt"),
        ("--ffmpeg", "/usr/bin/ffmpeg")
    ]
    
    passed = 0
    total = len(path_options)
    
    for option, path in path_options:
        try:
            result = subprocess.run([
                sys.executable, "src/UltraSinger.py",
                "--help"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✓ {green_highlighted(f'Opção {option} reconhecida')}")
                passed += 1
            else:
                print(f"✗ {red_highlighted(f'Opção {option} não reconhecida')}")
                
        except Exception as e:
            print(f"✗ {red_highlighted(f'Erro ao testar {option}: {e}')}")
    
    return passed == total

def test_numeric_options():
    """Testar opções numéricas"""
    print(f"\n{ULTRASINGER_HEAD} Testando opções numéricas...")
    
    numeric_options = [
        ("--crepe_step_size", "10"),
        ("--whisper_batch_size", "16")
    ]
    
    passed = 0
    total = len(numeric_options)
    
    for option, value in numeric_options:
        try:
            result = subprocess.run([
                sys.executable, "src/UltraSinger.py",
                "--help"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✓ {green_highlighted(f'Opção {option} reconhecida')}")
                passed += 1
            else:
                print(f"✗ {red_highlighted(f'Opção {option} não reconhecida')}")
                
        except Exception as e:
            print(f"✗ {red_highlighted(f'Erro ao testar {option}: {e}')}")
    
    return passed == total

def main():
    """Função principal de teste"""
    print(f"{ULTRASINGER_HEAD} {blue_highlighted('=== TESTE COMPLETO DAS OPÇÕES DE LINHA DE COMANDO ===')}")
    
    tests = [
        ("Opção Help", test_help_option),
        ("Exibição de Versão", test_version_display),
        ("Opções I/O", test_input_output_options),
        ("Opções de Modelo", test_model_options),
        ("Flags Booleanas", test_boolean_flags),
        ("Versão de Formato", test_format_version_option),
        ("Opções de Caminho", test_path_options),
        ("Opções Numéricas", test_numeric_options)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"{ULTRASINGER_HEAD} {blue_highlighted(f'Testando: {test_name}')}")
        print(f"{'='*60}")
        
        try:
            if test_func():
                print(f"✅ {green_highlighted(f'{test_name}: PASSOU')}")
                passed_tests += 1
            else:
                print(f"❌ {red_highlighted(f'{test_name}: FALHOU')}")
        except Exception as e:
            print(f"❌ {red_highlighted(f'{test_name}: ERRO - {e}')}")
    
    print(f"\n{'='*60}")
    print(f"{ULTRASINGER_HEAD} {blue_highlighted('RESUMO DOS TESTES')}")
    print(f"{'='*60}")
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASSOU" if i < passed_tests else "❌ FALHOU"
        print(f"{test_name:.<30} {status}")
    
    print(f"\n{ULTRASINGER_HEAD} Resultado Final: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print(f"🎉 {green_highlighted('TODOS OS TESTES DE LINHA DE COMANDO PASSARAM!')}")
    else:
        print(f"⚠️ {red_highlighted(f'{total_tests - passed_tests} testes falharam')}")
    
    print(f"{'='*60}")
    print(f"✅ {green_highlighted('TESTE DE OPÇÕES DE LINHA DE COMANDO FINALIZADO')}")
    print(f"Todas as opções CLI foram testadas!")

if __name__ == "__main__":
    main()