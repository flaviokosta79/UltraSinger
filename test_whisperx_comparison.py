"""
Script de Comparação: WhisperX 3.3.1 vs 3.4.3
==============================================
Testa o mesmo áudio nas duas versões e compara resultados
"""

import whisperx
import torch
import json
import time
from pathlib import Path

def test_whisperx():
    """Testa WhisperX com um áudio de exemplo"""

    print("\n" + "="*60)
    print("TESTE WhisperX - Comparação de Versões")
    print("="*60 + "\n")

    # Configuração
    audio_file = r"E:\VSCode\Projects\UltraSinger\output\Pollo - Vagalumes\Pollo - Vagalumes.mp3"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"

    print(f"📁 Áudio: {Path(audio_file).name}")
    print(f"🖥️  Device: {device}")
    print(f"🔢 Compute Type: {compute_type}\n")

    # Verificar versões
    print("📦 Versões Instaladas:")
    try:
        import importlib.metadata
        print(f"   - WhisperX: {importlib.metadata.version('whisperx')}")
        print(f"   - ctranslate2: {importlib.metadata.version('ctranslate2')}")
        print(f"   - numpy: {importlib.metadata.version('numpy')}")
        print(f"   - PyTorch: {torch.__version__}")
    except:
        print("   (não foi possível verificar versões)")

    print("\n" + "-"*60)
    print("Iniciando teste de transcrição...")
    print("-"*60 + "\n")

    # Teste 1: Carregar modelo
    print("📥 [1/4] Carregando modelo Whisper base...")
    start_time = time.time()
    try:
        model = whisperx.load_model("base", device, compute_type=compute_type)
        load_time = time.time() - start_time
        print(f"   ✓ Modelo carregado em {load_time:.2f}s\n")
    except Exception as e:
        print(f"   ✗ ERRO ao carregar modelo: {e}\n")
        return False

    # Teste 2: Carregar áudio
    print("🎵 [2/4] Carregando áudio...")
    start_time = time.time()
    try:
        audio = whisperx.load_audio(audio_file)
        audio_duration = len(audio) / 16000  # 16kHz sample rate
        load_time = time.time() - start_time
        print(f"   ✓ Áudio carregado em {load_time:.2f}s")
        print(f"   📊 Duração: {audio_duration:.1f}s\n")
    except Exception as e:
        print(f"   ✗ ERRO ao carregar áudio: {e}\n")
        return False

    # Teste 3: Transcrição (primeiros 30 segundos)
    print("🎤 [3/4] Transcrevendo (primeiros 30s)...")
    start_time = time.time()
    try:
        audio_sample = audio[:16000 * 30]  # Primeiros 30 segundos
        result = model.transcribe(audio_sample, batch_size=16)
        transcribe_time = time.time() - start_time

        print(f"   ✓ Transcrição concluída em {transcribe_time:.2f}s")
        print(f"   📝 Idioma detectado: {result['language']}")
        print(f"   📊 Segmentos: {len(result['segments'])}\n")

    except Exception as e:
        print(f"   ✗ ERRO ao transcrever: {e}\n")
        return False

    # Teste 4: Mostrar resultado
    print("📄 [4/4] Resultado da Transcrição (primeiras 5 linhas):")
    print("-"*60)

    word_count = 0
    for i, segment in enumerate(result['segments'][:5]):
        text = segment['text'].strip()
        start = segment['start']
        end = segment['end']
        words = len(text.split())
        word_count += words
        print(f"{i+1}. [{start:.1f}s - {end:.1f}s] {text}")

    print("-"*60)
    print(f"Total de palavras (5 primeiras linhas): {word_count}\n")

    # Estatísticas
    print("="*60)
    print("RESUMO DO TESTE")
    print("="*60)
    print(f"✓ Modelo carregado com sucesso")
    print(f"✓ Áudio processado: {audio_duration:.1f}s")
    print(f"✓ Transcrição: {transcribe_time:.2f}s ({audio_duration/transcribe_time:.1f}x velocidade real)")
    print(f"✓ Idioma: {result['language']}")
    print(f"✓ Segmentos: {len(result['segments'])}")

    # Testar feature específica: números
    print("\n" + "-"*60)
    print("🔍 Testando suporte a números...")
    print("-"*60)

    has_numbers = False
    for segment in result['segments']:
        text = segment['text']
        if any(char.isdigit() for char in text):
            has_numbers = True
            print(f"   Número encontrado: '{text.strip()}'")
            if 'words' in segment:
                for word in segment['words']:
                    if any(char.isdigit() for char in word.get('word', '')):
                        print(f"   → Palavra: {word['word']} | Start: {word.get('start', 'N/A')} | End: {word.get('end', 'N/A')}")

    if not has_numbers:
        print("   ℹ️  Nenhum número encontrado neste trecho")

    print("\n" + "="*60)
    print("✓ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*60 + "\n")

    # Salvar resultado para comparação
    result_file = "test_result_343.json" if "3.4.3" in str(importlib.metadata.version('whisperx')) else "test_result_331.json"
    try:
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                'version': importlib.metadata.version('whisperx'),
                'language': result['language'],
                'segments_count': len(result['segments']),
                'transcribe_time': transcribe_time,
                'first_5_segments': [
                    {
                        'text': seg['text'],
                        'start': seg['start'],
                        'end': seg['end']
                    } for seg in result['segments'][:5]
                ]
            }, f, indent=2, ensure_ascii=False)
        print(f"💾 Resultado salvo em: {result_file}\n")
    except:
        pass

    return True

if __name__ == "__main__":
    try:
        success = test_whisperx()
        if success:
            print("\n✅ Teste finalizado com sucesso!")
            print("\n📊 Próximo passo:")
            print("   Compare este resultado com o da versão 3.3.1")
            print("   Arquivos: test_result_343.json vs test_result_331.json\n")
    except Exception as e:
        print(f"\n❌ ERRO durante o teste: {e}")
        import traceback
        traceback.print_exc()
