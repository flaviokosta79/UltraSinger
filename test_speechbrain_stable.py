#!/usr/bin/env python3
"""
Teste de integração SpeechBrain com versões estáveis
Evita problemas de TensorFlow testando apenas funcionalidades essenciais
"""

import os
import sys
import traceback
from pathlib import Path

def test_speechbrain_import():
    """Testa importação básica do SpeechBrain"""
    print("🔍 Testando importação do SpeechBrain...")
    try:
        import speechbrain
        print(f"✅ SpeechBrain {speechbrain.__version__} importado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar SpeechBrain: {e}")
        return False

def test_config_manager_import():
    """Testa importação do config_manager sem TensorFlow"""
    print("\n🔍 Testando importação do config_manager...")
    try:
        # Adiciona o diretório src ao path
        src_path = Path(__file__).parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Testa apenas a importação da enum ProcessingMode
        from modules.SpeechBrain.config_manager import ProcessingMode
        print(f"✅ ProcessingMode importado: {list(ProcessingMode)}")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar ProcessingMode: {e}")
        traceback.print_exc()
        return False

def test_speechbrain_modules_structure():
    """Verifica se os módulos SpeechBrain estão no lugar correto"""
    print("\n🔍 Verificando estrutura dos módulos SpeechBrain...")
    
    base_path = Path(__file__).parent / "src" / "modules" / "SpeechBrain"
    expected_files = [
        "config_manager.py",
        "models.py",
        "__init__.py"
    ]
    
    all_found = True
    for file in expected_files:
        file_path = base_path / file
        if file_path.exists():
            print(f"✅ {file} encontrado")
        else:
            print(f"❌ {file} não encontrado em {file_path}")
            all_found = False
    
    return all_found

def test_basic_torch_compatibility():
    """Testa compatibilidade básica com PyTorch"""
    print("\n🔍 Testando compatibilidade com PyTorch...")
    try:
        import torch
        import torchaudio
        print(f"✅ PyTorch {torch.__version__} e torchaudio {torchaudio.__version__} disponíveis")
        
        # Teste básico de tensor
        x = torch.randn(2, 3)
        print(f"✅ Tensor criado: {x.shape}")
        return True
    except Exception as e:
        print(f"❌ Erro com PyTorch: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🚀 TESTE DE INTEGRAÇÃO SPEECHBRAIN - VERSÕES ESTÁVEIS")
    print("=" * 60)
    
    tests = [
        ("Importação SpeechBrain", test_speechbrain_import),
        ("Estrutura dos Módulos", test_speechbrain_modules_structure),
        ("Compatibilidade PyTorch", test_basic_torch_compatibility),
        ("Config Manager", test_config_manager_import),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 Todos os testes passaram! SpeechBrain está pronto para uso.")
        return 0
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    exit(main())