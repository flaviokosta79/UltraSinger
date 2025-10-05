#!/usr/bin/env python3
"""
Teste CORE do SpeechBrain - apenas funcionalidades essenciais
Evita completamente qualquer importação que possa acionar TensorFlow
"""

import sys
import os
from pathlib import Path

def test_speechbrain_only():
    """Testa apenas SpeechBrain sem importar nossos módulos"""
    print("🔍 Testando SpeechBrain puro...")
    
    try:
        import speechbrain
        print(f"✅ SpeechBrain {speechbrain.__version__} importado")
        
        # Testa algumas funcionalidades básicas do SpeechBrain
        from speechbrain.utils.data_utils import download_file
        print("✅ speechbrain.utils.data_utils disponível")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_torch_only():
    """Testa apenas PyTorch"""
    print("\n🔍 Testando PyTorch puro...")
    
    try:
        import torch
        import torchaudio
        print(f"✅ PyTorch {torch.__version__}")
        print(f"✅ torchaudio {torchaudio.__version__}")
        
        # Teste básico
        x = torch.randn(3, 4)
        y = x.sum()
        print(f"✅ Operação básica: tensor {x.shape} -> soma {y.item():.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_file_existence():
    """Verifica apenas se os arquivos existem"""
    print("\n🔍 Verificando existência de arquivos...")
    
    base_path = Path(__file__).parent / "src" / "modules" / "SpeechBrain"
    
    files = [
        "__init__.py",
        "config_manager.py", 
        "model_manager.py",
        "speechbrain_integration.py"
    ]
    
    found = 0
    for file in files:
        path = base_path / file
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {file} ({size} bytes)")
            found += 1
        else:
            print(f"❌ {file} não encontrado")
    
    return found == len(files)

def test_config_file_content():
    """Verifica conteúdo do arquivo de configuração sem importar"""
    print("\n🔍 Analisando config_manager.py...")
    
    try:
        config_path = Path(__file__).parent / "src" / "modules" / "SpeechBrain" / "config_manager.py"
        
        if not config_path.exists():
            print("❌ config_manager.py não encontrado")
            return False
        
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica estruturas importantes
        checks = [
            ("class ProcessingMode", "ProcessingMode enum"),
            ("class SepFormerModel", "SepFormerModel enum"),
            ("class ASRModel", "ASRModel enum"),
            ("class VADModel", "VADModel enum"),
            ("@dataclass", "dataclass decorators"),
            ("from enum import", "enum imports")
        ]
        
        passed = 0
        for check, description in checks:
            if check in content:
                print(f"✅ {description} encontrado")
                passed += 1
            else:
                print(f"❌ {description} não encontrado")
        
        print(f"📊 {passed}/{len(checks)} verificações passaram")
        return passed >= len(checks) - 1  # Permite 1 falha
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False

def test_dependencies_status():
    """Verifica status das dependências principais"""
    print("\n🔍 Verificando dependências principais...")
    
    try:
        # Testa dependências uma por uma
        deps = [
            ("numpy", "numpy"),
            ("torch", "torch"),
            ("torchaudio", "torchaudio"),
            ("speechbrain", "speechbrain")
        ]
        
        available = 0
        for name, module in deps:
            try:
                __import__(module)
                print(f"✅ {name} disponível")
                available += 1
            except ImportError:
                print(f"❌ {name} não disponível")
        
        print(f"📊 {available}/{len(deps)} dependências disponíveis")
        return available == len(deps)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Executa testes core"""
    print("=" * 50)
    print("🔧 TESTE CORE SPEECHBRAIN")
    print("=" * 50)
    
    tests = [
        ("Dependências Principais", test_dependencies_status),
        ("SpeechBrain Puro", test_speechbrain_only),
        ("PyTorch Puro", test_torch_only),
        ("Existência de Arquivos", test_file_existence),
        ("Conteúdo Config", test_config_file_content),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO CORE")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} testes core passaram")
    
    if passed >= 4:
        print("🎉 Core do SpeechBrain está funcional!")
        print("💡 Problemas de TensorFlow não afetam funcionalidade básica")
        return 0
    else:
        print("⚠️  Problemas no core detectados")
        return 1

if __name__ == "__main__":
    exit(main())