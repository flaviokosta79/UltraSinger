#!/usr/bin/env python3
"""
Teste de integração simplificado do SpeechBrain
Foca apenas nos módulos principais sem dependências problemáticas
"""

import sys
import os
import traceback
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Testa se os módulos podem ser importados corretamente"""
    print("🔍 Testando importações dos módulos SpeechBrain...")
    
    try:
        # Testar importações básicas
        from modules.SpeechBrain.model_manager import ModelManager
        print("✅ ModelManager importado com sucesso")
        
        from modules.SpeechBrain.sepformer_separation import SepFormerSeparation, SeparationModel
        print("✅ SepFormerSeparation importado com sucesso")
        
        from modules.SpeechBrain.conformer_asr import ConformerASR, ASRModel
        print("✅ ConformerASR importado com sucesso")
        
        from modules.SpeechBrain.vad_system import VADSystem, VADModel
        print("✅ VADSystem importado com sucesso")
        
        from modules.SpeechBrain.speechbrain_integration import SpeechBrainIntegration
        print("✅ SpeechBrainIntegration importado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {str(e)}")
        print(f"🔍 Traceback completo:")
        traceback.print_exc()
        return False

def test_model_manager():
    """Testa a funcionalidade básica do ModelManager"""
    print("\n🔍 Testando ModelManager...")
    
    try:
        from modules.SpeechBrain.model_manager import ModelManager
        
        # Criar instância
        manager = ModelManager()
        print("✅ ModelManager criado com sucesso")
        
        # Testar métodos básicos
        cache_info = manager.get_cache_info()
        print(f"✅ Cache info obtido: {len(cache_info)} modelos em cache")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no ModelManager: {str(e)}")
        traceback.print_exc()
        return False

def test_speechbrain_integration():
    """Testa a classe principal de integração"""
    print("\n🔍 Testando SpeechBrainIntegration...")
    
    try:
        from modules.SpeechBrain.speechbrain_integration import SpeechBrainIntegration
        
        # Criar instância
        integration = SpeechBrainIntegration()
        print("✅ SpeechBrainIntegration criado com sucesso")
        
        # Testar configuração
        config = integration.get_configuration()
        print(f"✅ Configuração obtida: {len(config)} seções")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no SpeechBrainIntegration: {str(e)}")
        traceback.print_exc()
        return False

def test_enums():
    """Testa se os enums estão funcionando corretamente"""
    print("\n🔍 Testando Enums...")
    
    try:
        from modules.SpeechBrain.sepformer_separation import SepFormerModel
        from modules.SpeechBrain.conformer_asr import ASRModel
        from modules.SpeechBrain.vad_system import VADModel
        
        # Testar SepFormerModel
        sep_models = list(SepFormerModel)
        print(f"✅ SepFormerModel: {len(sep_models)} modelos disponíveis")
        
        # Testar ASRModel
        asr_models = list(ASRModel)
        print(f"✅ ASRModel: {len(asr_models)} modelos disponíveis")
        
        # Testar VADModel
        vad_models = list(VADModel)
        print(f"✅ VADModel: {len(vad_models)} modelos disponíveis")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos Enums: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Função principal do teste"""
    print("🚀 Iniciando teste de integração SpeechBrain (Simplificado)")
    print("=" * 60)
    
    tests = [
        ("Importações", test_imports),
        ("ModelManager", test_model_manager),
        ("SpeechBrainIntegration", test_speechbrain_integration),
        ("Enums", test_enums),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico no teste {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado Final: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Integração SpeechBrain está funcionando.")
        return 0
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro crítico: {str(e)}")
        traceback.print_exc()
        sys.exit(1)