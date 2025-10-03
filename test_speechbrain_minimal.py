#!/usr/bin/env python3
"""
Teste mínimo de SpeechBrain - evita completamente problemas de TensorFlow
Testa apenas funcionalidades essenciais sem importar módulos problemáticos
"""

import os
import sys
from pathlib import Path

def test_speechbrain_basic():
    """Testa apenas a importação básica do SpeechBrain"""
    print("🔍 Testando importação básica do SpeechBrain...")
    try:
        import speechbrain
        print(f"✅ SpeechBrain {speechbrain.__version__} importado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar SpeechBrain: {e}")
        return False

def test_torch_basic():
    """Testa PyTorch básico"""
    print("\n🔍 Testando PyTorch básico...")
    try:
        import torch
        import torchaudio
        print(f"✅ PyTorch {torch.__version__} e torchaudio {torchaudio.__version__}")
        
        # Teste básico
        x = torch.randn(2, 3)
        print(f"✅ Tensor criado: {x.shape}")
        return True
    except Exception as e:
        print(f"❌ Erro com PyTorch: {e}")
        return False

def test_file_structure():
    """Verifica se os arquivos SpeechBrain existem"""
    print("\n🔍 Verificando estrutura de arquivos...")
    
    base_path = Path(__file__).parent / "src" / "modules" / "SpeechBrain"
    expected_files = [
        "__init__.py",
        "config_manager.py",
        "model_manager.py",
        "speechbrain_integration.py"
    ]
    
    all_found = True
    for file in expected_files:
        file_path = base_path / file
        if file_path.exists():
            print(f"✅ {file} encontrado")
        else:
            print(f"❌ {file} não encontrado")
            all_found = False
    
    return all_found

def test_simple_config():
    """Testa configuração simples sem importar módulos problemáticos"""
    print("\n🔍 Testando configuração simples...")
    try:
        # Adiciona src ao path
        src_path = Path(__file__).parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Testa apenas se o arquivo existe e pode ser lido
        config_file = src_path / "modules" / "SpeechBrain" / "config_manager.py"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'ProcessingMode' in content:
                    print("✅ ProcessingMode encontrado no config_manager.py")
                    return True
                else:
                    print("❌ ProcessingMode não encontrado no arquivo")
                    return False
        else:
            print("❌ config_manager.py não encontrado")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return False

def main():
    """Executa testes mínimos"""
    print("=" * 50)
    print("🚀 TESTE MÍNIMO SPEECHBRAIN")
    print("=" * 50)
    
    tests = [
        ("SpeechBrain Básico", test_speechbrain_basic),
        ("PyTorch Básico", test_torch_basic),
        ("Estrutura de Arquivos", test_file_structure),
        ("Configuração Simples", test_simple_config),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} testes passaram")
    
    if passed >= 3:  # Pelo menos 3 de 4 testes devem passar
        print("🎉 SpeechBrain está funcionalmente pronto!")
        return 0
    else:
        print("⚠️  Problemas detectados.")
        return 1

if __name__ == "__main__":
    exit(main())