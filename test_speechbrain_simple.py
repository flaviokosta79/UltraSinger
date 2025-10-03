#!/usr/bin/env python3
"""
Teste simplificado dos módulos SpeechBrain
Evita importações problemáticas do TensorFlow
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_file_structure():
    """Verifica se os arquivos SpeechBrain existem"""
    print("🔍 Verificando estrutura de arquivos...")
    
    speechbrain_dir = Path("src/modules/SpeechBrain")
    
    required_files = [
        "__init__.py",
        "config_manager.py",
        "model_manager.py",
        "sepformer_separation.py",
        "conformer_asr.py",
        "vad_system.py",
        "forced_alignment.py",
        "speechbrain_integration.py"
    ]
    
    missing_files = []
    
    for file_name in required_files:
        file_path = speechbrain_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} - AUSENTE")
            missing_files.append(file_name)
    
    if missing_files:
        print(f"❌ Arquivos ausentes: {missing_files}")
        return False
    
    print("✅ Todos os arquivos necessários estão presentes")
    return True

def test_basic_config():
    """Testa apenas configurações básicas sem SpeechBrain imports"""
    print("\n🔍 Testando configurações básicas...")
    
    try:
        # Importar apenas enums sem dependências externas
        from modules.SpeechBrain.config_manager import ProcessingMode
        print("✅ ProcessingMode importado")
        
        # Testar enums
        modes = list(ProcessingMode)
        print(f"✅ {len(modes)} modos de processamento: {[m.value for m in modes]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_speechbrain_import():
    """Testa importação básica do SpeechBrain"""
    print("\n🔍 Testando importação do SpeechBrain...")
    
    try:
        import speechbrain
        print(f"✅ SpeechBrain {speechbrain.__version__} importado")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao importar SpeechBrain: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🚀 Teste Simplificado SpeechBrain")
    print("=" * 50)
    
    tests = [
        ("Estrutura de Arquivos", test_file_structure),
        ("SpeechBrain Import", test_speechbrain_import),
        ("Configurações Básicas", test_basic_config),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico no teste {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Estrutura básica funcionando!")
        return 0
    else:
        print("⚠️  Alguns testes falharam.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n💥 Erro crítico: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)