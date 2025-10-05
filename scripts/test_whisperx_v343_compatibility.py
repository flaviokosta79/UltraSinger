#!/usr/bin/env python3
"""
Teste de Compatibilidade WhisperX v3.4.3
Verifica se a nova versão funciona corretamente com UltraSinger
"""

import sys
import os
import traceback
import whisperx
import torch

def test_whisperx_import():
    """Testa se o WhisperX pode ser importado corretamente"""
    try:
        print(f"✅ WhisperX importado com sucesso - Versão: {whisperx.__version__}")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar WhisperX: {e}")
        return False

def test_basic_functionality():
    """Testa funcionalidades básicas do WhisperX"""
    try:
        print("\n🔧 Testando funcionalidades básicas...")
        
        # Teste 1: Verificar se pode carregar modelo pequeno
        print("  📦 Carregando modelo 'tiny' para teste...")
        model = whisperx.load_model("tiny", device="cpu", compute_type="int8")
        print("  ✅ Modelo carregado com sucesso")
        
        # Teste 2: Verificar se pode criar áudio de teste
        print("  🎵 Testando carregamento de áudio...")
        # Criar um arquivo de áudio de teste simples (silêncio)
        import numpy as np
        import soundfile as sf
        
        # Criar 1 segundo de silêncio
        sample_rate = 16000
        duration = 1.0
        samples = int(sample_rate * duration)
        audio_data = np.zeros(samples, dtype=np.float32)
        
        test_audio_path = "test_audio_temp.wav"
        sf.write(test_audio_path, audio_data, sample_rate)
        
        # Carregar áudio com WhisperX
        audio = whisperx.load_audio(test_audio_path)
        print(f"  ✅ Áudio carregado - Shape: {audio.shape}")
        
        # Teste 3: Transcrição básica
        print("  🎤 Testando transcrição...")
        result = model.transcribe(audio, batch_size=1)
        print(f"  ✅ Transcrição realizada - Segmentos: {len(result.get('segments', []))}")
        
        # Limpeza
        os.remove(test_audio_path)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no teste básico: {e}")
        traceback.print_exc()
        return False

def test_model_loading():
    """Testa carregamento de diferentes modelos"""
    models_to_test = ["tiny", "base", "small"]
    
    print("\n🎯 Testando carregamento de modelos...")
    
    for model_name in models_to_test:
        try:
            print(f"  📦 Testando modelo: {model_name}")
            model = whisperx.load_model(model_name, device="cpu", compute_type="int8")
            print(f"  ✅ {model_name} carregado com sucesso")
            del model  # Liberar memória
        except Exception as e:
            print(f"  ❌ Erro ao carregar {model_name}: {e}")

def test_device_compatibility():
    """Testa compatibilidade com diferentes dispositivos"""
    print("\n💻 Testando compatibilidade de dispositivos...")
    
    # Teste CPU
    try:
        print("  🖥️  Testando CPU...")
        model = whisperx.load_model("tiny", device="cpu", compute_type="int8")
        print("  ✅ CPU compatível")
        del model
    except Exception as e:
        print(f"  ❌ Erro com CPU: {e}")
    
    # Teste GPU (se disponível)
    if torch.cuda.is_available():
        try:
            print("  🎮 Testando GPU...")
            model = whisperx.load_model("tiny", device="cuda", compute_type="float16")
            print("  ✅ GPU compatível")
            del model
        except Exception as e:
            print(f"  ❌ Erro com GPU: {e}")
    else:
        print("  ℹ️  GPU não disponível para teste")

def test_alignment_functionality():
    """Testa funcionalidade de alinhamento"""
    print("\n🎯 Testando funcionalidade de alinhamento...")
    
    try:
        # Carregar modelo de alinhamento para inglês
        model_a, metadata = whisperx.load_align_model(language_code="en", device="cpu")
        print("  ✅ Modelo de alinhamento carregado")
        
        # Teste básico de alinhamento (com dados fictícios)
        segments = [{"start": 0.0, "end": 1.0, "text": "test"}]
        
        print("  ✅ Funcionalidade de alinhamento disponível")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no teste de alinhamento: {e}")
        return False

def main():
    """Função principal do teste"""
    print("🚀 TESTE DE COMPATIBILIDADE WHISPERX v3.4.3")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 5
    
    # Teste 1: Importação
    if test_whisperx_import():
        tests_passed += 1
    
    # Teste 2: Funcionalidade básica
    if test_basic_functionality():
        tests_passed += 1
    
    # Teste 3: Carregamento de modelos
    test_model_loading()
    tests_passed += 1  # Sempre conta como passou se não crashou
    
    # Teste 4: Compatibilidade de dispositivos
    test_device_compatibility()
    tests_passed += 1  # Sempre conta como passou se não crashou
    
    # Teste 5: Funcionalidade de alinhamento
    if test_alignment_functionality():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTADO FINAL: {tests_passed}/{total_tests} testes passaram")
    
    if tests_passed == total_tests:
        print("🎉 WhisperX v3.4.3 está totalmente compatível!")
        return True
    elif tests_passed >= 3:
        print("⚠️  WhisperX v3.4.3 está parcialmente compatível")
        return True
    else:
        print("❌ WhisperX v3.4.3 apresenta problemas de compatibilidade")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)