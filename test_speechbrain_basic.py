#!/usr/bin/env python3
"""
Teste básico de importação dos módulos SpeechBrain
Sem dependências externas problemáticas
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_imports():
    """Testa importações básicas sem dependências externas"""
    print("🔍 Testando importações básicas...")
    
    try:
        # Testar apenas enums e classes básicas (sem SpeechBrain imports)
        print("✅ Testando enums...")
        
        # Importar apenas os enums sem instanciar classes que usam SpeechBrain
        import importlib.util
        
        # Verificar se os arquivos existem
        speechbrain_dir = Path("src/modules/SpeechBrain")
        files_to_check = [
            "config_manager.py",
            "sepformer_separation.py", 
            "conformer_asr.py",
            "vad_system.py",
            "model_manager.py"
        ]
        
        for file_name in files_to_check:
            file_path = speechbrain_dir / file_name
            if file_path.exists():
                print(f"✅ {file_name} encontrado")
            else:
                print(f"❌ {file_name} não encontrado")
                return False
        
        # Testar importação básica do config_manager apenas
        from modules.SpeechBrain.config_manager import ProcessingMode
        print("✅ ProcessingMode importado")
        
        processing_modes = list(ProcessingMode)
        print(f"✅ {len(processing_modes)} modos de processamento disponíveis")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_config_manager():
    """Testa o gerenciador de configuração"""
    print("\n🔍 Testando ConfigManager...")
    
    try:
        from modules.SpeechBrain.config_manager import SpeechBrainConfig
        
        # Criar configuração
        config = SpeechBrainConfig()
        print("✅ SpeechBrainConfig criado")
        
        # Testar propriedades básicas
        print(f"✅ Device: {config.device}")
        print(f"✅ Processing mode: {config.processing_mode.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no ConfigManager: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print("🚀 Teste Básico SpeechBrain")
    print("=" * 50)
    
    tests = [
        ("Importações Básicas", test_basic_imports),
        ("ConfigManager", test_config_manager),
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
        print(f"{test_name:20} {status}")
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