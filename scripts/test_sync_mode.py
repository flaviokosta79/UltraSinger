"""
Teste do modo de sincronização: Letra LRCLib + Timestamps WhisperX
"""

import sys
sys.path.insert(0, 'src')

from modules.LRCLib.lrclib_integration import LRCLibAPI, LyricsCorrector

# 1. Buscar letra no LRCLib
print("=" * 70)
print("TESTE DE SINCRONIZAÇÃO - LRCLIB + WHISPERX")
print("=" * 70)

api = LRCLibAPI()
print("\n🔍 Buscando letra de 'Vagalumes' - 'Pollo' no LRCLib...")
result = api.get_lyrics('Pollo', 'Vagalumes')

if not result:
    print("❌ Letra não encontrada!")
    sys.exit(1)

print(f"✅ Letra encontrada! ID: {result.id}")

# 2. Simular segmentos do WhisperX (incluindo o erro "janela e monê")
test_segments = [
    {'text': 'Vou', 'start': 0.0, 'end': 0.5},
    {'text': 'caçar', 'start': 0.6, 'end': 1.2},
    {'text': 'mais', 'start': 1.3, 'end': 1.6},
    {'text': 'um', 'start': 1.7, 'end': 1.9},
    {'text': 'milhão', 'start': 2.0, 'end': 2.5},
    {'text': 'de', 'start': 2.6, 'end': 2.8},
    {'text': 'vagalumes', 'start': 2.9, 'end': 3.5},
    {'text': 'por', 'start': 3.6, 'end': 3.8},
    {'text': 'aí', 'start': 3.9, 'end': 4.3},
    {'text': 'Pra', 'start': 4.5, 'end': 4.7},
    {'text': 'te', 'start': 4.8, 'end': 4.9},
    {'text': 'ver', 'start': 5.0, 'end': 5.2},
    {'text': 'sorrir', 'start': 5.3, 'end': 5.8},
    {'text': 'eu', 'start': 5.9, 'end': 6.0},
    {'text': 'posso', 'start': 6.1, 'end': 6.4},
    {'text': 'colorir', 'start': 6.5, 'end': 7.0},
    {'text': 'o', 'start': 7.1, 'end': 7.2},
    {'text': 'céu', 'start': 7.3, 'end': 7.6},
    {'text': 'de', 'start': 7.7, 'end': 7.9},
    {'text': 'outra', 'start': 8.0, 'end': 8.3},
    {'text': 'cor', 'start': 8.4, 'end': 8.7},
    # ERRO AQUI: "janela e monê" em vez de "Janelle Monáe"
    {'text': 'Eu', 'start': 9.0, 'end': 9.2},
    {'text': 'e', 'start': 9.3, 'end': 9.4},
    {'text': 'você', 'start': 9.5, 'end': 9.8},
    {'text': 'ao', 'start': 9.9, 'end': 10.0},
    {'text': 'som', 'start': 10.1, 'end': 10.3},
    {'text': 'de', 'start': 10.4, 'end': 10.5},
    {'text': 'janela', 'start': 10.6, 'end': 11.0},  # ❌ ERRO
    {'text': 'e', 'start': 11.1, 'end': 11.2},        # ❌ ERRO
    {'text': 'monê', 'start': 11.3, 'end': 11.7},     # ❌ ERRO
]

print(f"\n📝 Simulando {len(test_segments)} segmentos do WhisperX")
print(f"   Incluindo erro: 'janela e monê' (deveria ser 'Janelle Monáe')")

# 3. Testar sincronização
print("\n" + "=" * 70)
print("APLICANDO SINCRONIZAÇÃO")
print("=" * 70)

corrector = LyricsCorrector(use_sync_mode=True)
synced_segments, num_synced = corrector.correct(test_segments, result.plain_lyrics)

# 4. Verificar resultado
print("\n" + "=" * 70)
print("RESULTADO DA SINCRONIZAÇÃO")
print("=" * 70)

print("\n📋 ANTES (WhisperX com erro):")
print("-" * 70)
for i, seg in enumerate(test_segments[22:30], start=23):  # Região do erro
    print(f"{i:3d}. [{seg['start']:6.2f}s] {seg['text']}")

print("\n📋 DEPOIS (LRCLib + timestamps):")
print("-" * 70)
for i, seg in enumerate(synced_segments[22:30], start=23):  # Mesma região
    print(f"{i:3d}. [{seg['start']:6.2f}s] {seg['text']}")

# 5. Verificar se "Janelle Monáe" foi corrigido
synced_text = " ".join([seg['text'] for seg in synced_segments])

print("\n" + "=" * 70)
print("VALIDAÇÃO")
print("=" * 70)

if "Janelle" in synced_text:
    print("✅ SUCESSO! Nome 'Janelle Monáe' foi sincronizado corretamente!")
    print(f"\n🎯 Texto sincronizado contém:")
    for seg in synced_segments:
        if 'Janelle' in seg['text'] or 'Monáe' in seg['text']:
            print(f"   • [{seg['start']:.2f}s] {seg['text']}")
else:
    print("❌ FALHA! Nome 'Janelle Monáe' não foi encontrado")
    print(f"\n📝 Texto sincronizado:")
    print(synced_text[:200] + "...")

print("\n" + "=" * 70)
