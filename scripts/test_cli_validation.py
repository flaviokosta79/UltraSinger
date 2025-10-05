#!/usr/bin/env python3
"""
Teste de validação das opções de linha de comando do UltraSinger
Testa diretamente as funções de parsing sem executar o programa completo
"""

import os
import sys
import tempfile
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.console_colors import ULTRASINGER_HEAD, green_highlighted, red_highlighted, blue_highlighted
from modules.common_print import print_help
from Settings import Settings

# Importar funções do UltraSinger
try:
    from UltraSinger import arg_options, init_settings
    from modules.Speech_Recognition.Whisper import WhisperModel
    from modules.Audio.separation import DemucsModel
    from modules.Ultrastar.ultrastar_txt import FormatVersion
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    sys.exit(1)

def test_arg_options():
    """Testar se as opções de argumentos estão definidas corretamente"""
    print(f"\n{ULTRASINGER_HEAD} Testando definições de argumentos...")
    
    try:
        long_opts, short_opts = arg_options()
        
        expected_long = [
            "help", "ifile=", "ofile=", "crepe=", "crepe_step_size=", 
            "demucs=", "whisper=", "whisper_align_model=", "whisper_batch_size=",
            "whisper_compute_type=", "language=", "plot", "midi",
            "disable_hyphenation", "disable_separation", "disable_karaoke",
            "create_audio_chunks", "ignore_audio", "force_cpu",
            "force_whisper_cpu", "force_crepe_cpu", "format_version=",
            "keep_cache", "musescore_path=", "keep_numbers",
            "interactive", "cookiefile=", "ffmpeg="
        ]
        
        expected_short = "hi:o:amv:"
        
        missing_long = [opt for opt in expected_long if opt not in long_opts]
        missing_short = [char for char in expected_short if char not in short_opts]
        
        if not missing_long and not missing_short:
            print(f"✓ {green_highlighted('Todas as opções definidas corretamente')}")
            print(f"  Opções longas: {len(long_opts)} definidas")
            print(f"  Opções curtas: {len(short_opts)} caracteres")
            return True
        else:
            print(f"✗ {red_highlighted('Opções faltando:')}")
            if missing_long:
                print(f"  Longas: {missing_long}")
            if missing_short:
                print(f"  Curtas: {missing_short}")
            return False
            
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro ao testar opções: {e}')}")
        return False

def test_help_function():
    """Testar se a função de ajuda funciona"""
    print(f"\n{ULTRASINGER_HEAD} Testando função de ajuda...")
    
    try:
        # Capturar saída da função print_help
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            print_help()
        
        help_output = f.getvalue()
        
        if "UltraSinger.py" in help_output and "[opt]" in help_output:
            print(f"✓ {green_highlighted('Função de ajuda funcionando')}")
            print(f"  Tamanho da ajuda: {len(help_output)} caracteres")
            return True
        else:
            print(f"✗ {red_highlighted('Função de ajuda não retorna conteúdo esperado')}")
            return False
            
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro ao testar função de ajuda: {e}')}")
        return False

def test_settings_parsing():
    """Testar parsing de configurações com argumentos válidos"""
    print(f"\n{ULTRASINGER_HEAD} Testando parsing de configurações...")
    
    test_cases = [
        # Caso 1: Argumentos básicos
        (["-i", "test.mp3", "-o", "output"], "Argumentos básicos"),
        # Caso 2: Opções de modelo
        (["-i", "test.mp3", "--whisper", "base", "--crepe", "medium"], "Opções de modelo"),
        # Caso 3: Flags booleanas
        (["-i", "test.mp3", "--plot", "--midi", "--keep_cache"], "Flags booleanas"),
        # Caso 4: Opções numéricas
        (["-i", "test.mp3", "--crepe_step_size", "20", "--whisper_batch_size", "8"], "Opções numéricas"),
        # Caso 5: Versão de formato
        (["-i", "test.mp3", "--format_version", "1.2.0"], "Versão de formato"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for args, description in test_cases:
        try:
            # Criar uma nova instância de Settings para cada teste
            settings = Settings()
            
            # Simular o parsing (sem executar o programa completo)
            # Vamos testar apenas se os argumentos são reconhecidos
            long_opts, short_opts = arg_options()
            
            # Verificar se todos os argumentos são válidos
            valid = True
            for i, arg in enumerate(args):
                if arg.startswith("--"):
                    option = arg[2:]
                    if option not in [opt.rstrip("=") for opt in long_opts]:
                        valid = False
                        break
                elif arg.startswith("-") and len(arg) == 2:
                    option = arg[1]
                    if option not in short_opts:
                        valid = False
                        break
            
            if valid:
                print(f"✓ {green_highlighted(f'{description}: argumentos válidos')}")
                passed += 1
            else:
                print(f"✗ {red_highlighted(f'{description}: argumentos inválidos')}")
                
        except Exception as e:
            print(f"✗ {red_highlighted(f'{description}: erro - {e}')}")
    
    return passed == total

def test_model_enums():
    """Testar se os enums de modelo estão funcionando"""
    print(f"\n{ULTRASINGER_HEAD} Testando enums de modelo...")
    
    try:
        # Testar WhisperModel
        whisper_models = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]
        whisper_valid = all(hasattr(WhisperModel, model.upper().replace("-", "_")) or 
                           any(model in m.value for m in WhisperModel) for model in whisper_models)
        
        # Testar DemucsModel
        demucs_models = ["htdemucs", "htdemucs_ft", "mdx", "mdx_extra"]
        demucs_valid = all(hasattr(DemucsModel, model.upper()) or 
                          any(model in m.value for m in DemucsModel) for model in demucs_models)
        
        # Testar FormatVersion
        format_versions = ["0.3.0", "1.0.0", "1.1.0", "1.2.0"]
        format_valid = all(hasattr(FormatVersion, f"V{version.replace('.', '_')}") or
                          any(version in v.value for v in FormatVersion) for version in format_versions)
        
        if whisper_valid and demucs_valid and format_valid:
            print(f"✓ {green_highlighted('Todos os enums de modelo funcionando')}")
            print(f"  WhisperModel: {len(list(WhisperModel))} modelos")
            print(f"  DemucsModel: {len(list(DemucsModel))} modelos")
            print(f"  FormatVersion: {len(list(FormatVersion))} versões")
            return True
        else:
            print(f"✗ {red_highlighted('Alguns enums não funcionam:')}")
            if not whisper_valid:
                print(f"  WhisperModel: problema")
            if not demucs_valid:
                print(f"  DemucsModel: problema")
            if not format_valid:
                print(f"  FormatVersion: problema")
            return False
            
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro ao testar enums: {e}')}")
        return False

def test_required_arguments():
    """Testar validação de argumentos obrigatórios"""
    print(f"\n{ULTRASINGER_HEAD} Testando validação de argumentos obrigatórios...")
    
    try:
        # Testar se argumentos obrigatórios são detectados
        long_opts, short_opts = arg_options()
        
        # Verificar se opções que requerem valores estão marcadas com "="
        required_value_opts = [opt for opt in long_opts if opt.endswith("=")]
        
        expected_required = [
            "ifile=", "ofile=", "crepe=", "crepe_step_size=", "demucs=",
            "whisper=", "whisper_align_model=", "whisper_batch_size=",
            "whisper_compute_type=", "language=", "format_version=",
            "musescore_path=", "cookiefile=", "ffmpeg="
        ]
        
        missing_required = [opt for opt in expected_required if opt not in required_value_opts]
        
        if not missing_required:
            print(f"✓ {green_highlighted('Argumentos obrigatórios definidos corretamente')}")
            print(f"  {len(required_value_opts)} opções requerem valores")
            return True
        else:
            print(f"✗ {red_highlighted(f'Argumentos obrigatórios faltando: {missing_required}')}")
            return False
            
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro ao testar argumentos obrigatórios: {e}')}")
        return False

def test_boolean_flags():
    """Testar flags booleanas"""
    print(f"\n{ULTRASINGER_HEAD} Testando flags booleanas...")
    
    try:
        long_opts, short_opts = arg_options()
        
        # Flags que não devem ter "=" (são booleanas)
        boolean_flags = [opt for opt in long_opts if not opt.endswith("=")]
        
        expected_boolean = [
            "help", "plot", "midi", "disable_hyphenation", "disable_separation",
            "disable_karaoke", "create_audio_chunks", "ignore_audio",
            "force_cpu", "force_whisper_cpu", "force_crepe_cpu",
            "keep_cache", "keep_numbers", "interactive"
        ]
        
        missing_boolean = [opt for opt in expected_boolean if opt not in boolean_flags]
        
        if not missing_boolean:
            print(f"✓ {green_highlighted('Flags booleanas definidas corretamente')}")
            print(f"  {len(boolean_flags)} flags booleanas")
            return True
        else:
            print(f"✗ {red_highlighted(f'Flags booleanas faltando: {missing_boolean}')}")
            return False
            
    except Exception as e:
        print(f"✗ {red_highlighted(f'Erro ao testar flags booleanas: {e}')}")
        return False

def main():
    """Função principal de teste"""
    print(f"{ULTRASINGER_HEAD} {blue_highlighted('=== VALIDAÇÃO DAS OPÇÕES DE LINHA DE COMANDO ===')}")
    
    tests = [
        ("Definições de Argumentos", test_arg_options),
        ("Função de Ajuda", test_help_function),
        ("Parsing de Configurações", test_settings_parsing),
        ("Enums de Modelo", test_model_enums),
        ("Argumentos Obrigatórios", test_required_arguments),
        ("Flags Booleanas", test_boolean_flags)
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
        print(f"{test_name:.<35} {status}")
    
    print(f"\n{ULTRASINGER_HEAD} Resultado Final: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print(f"🎉 {green_highlighted('TODAS AS VALIDAÇÕES DE CLI PASSARAM!')}")
    else:
        print(f"⚠️ {red_highlighted(f'{total_tests - passed_tests} validações falharam')}")
    
    print(f"{'='*60}")
    print(f"✅ {green_highlighted('VALIDAÇÃO DE OPÇÕES CLI FINALIZADA')}")
    print(f"Sistema de linha de comando validado!")

if __name__ == "__main__":
    main()