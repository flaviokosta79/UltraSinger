"""
Teste comparativo dos 3 modos de correção/sincronização LRCLib
"""

import sys
sys.path.insert(0, 'src')

from modules.LRCLib.lrclib_integration import LRCLibAPI, LyricsCorrector

# 1. Buscar letra no LRCLib
print("=" * 80)
print("TESTE COMPARATIVO - 3 MODOS DE CORREÇÃO")
print("=" * 80)

api = LRCLibAPI()
print("\n🔍 Buscando letra de 'Vagalumes' - 'Pollo' no LRCLib...")
result = api.get_lyrics('Pollo', 'Vagalumes')

if not result:
    print("❌ Letra não encontrada!")
    sys.exit(1)

print(f"✅ Letra encontrada! ID: {result.id}")

# 2. Simular segmentos do WhisperX (incluindo erro "janela e monê")
test_segments = [
    {'text': 'Eu', 'start': 9.0, 'end': 9.2},
    {'text': 'e', 'start': 9.3, 'end': 9.4},
    {'text': 'você', 'start': 9.5, 'end': 9.8},
    {'text': 'ao', 'start': 9.9, 'end': 10.0},
    {'text': 'som', 'start': 10.1, 'end': 10.3},
    {'text': 'de', 'start': 10.4, 'end': 10.5},
    {'text': 'janela', 'start': 10.6, 'end': 11.0},  # ❌ ERRO
    {'text': 'e', 'start': 11.1, 'end': 11.2},        # ❌ ERRO
    {'text': 'monê', 'start': 11.3, 'end': 11.7},     # ❌ ERRO
    {'text': 'Vem', 'start': 11.8, 'end': 12.0},
    {'text': 'deixa', 'start': 12.1, 'end': 12.4},
    {'text': 'acontecer', 'start': 12.5, 'end': 13.0},
]

print(f"\n📝 Testando com {len(test_segments)} segmentos")
print("   Incluindo erro: 'janela e monê' (deveria ser 'Janelle Monáe')")

# Preparar letra de referência (apenas o trecho relevante)
reference_lyrics = """
Eu e você ao som de Janelle Monáe
Vem deixa acontecer e
"""

print("\n" + "=" * 80)
print("TEXTO ORIGINAL (WhisperX - COM ERRO)")
print("=" * 80)
for i, seg in enumerate(test_segments, 1):
    print(f"{i:2d}. [{seg['start']:5.1f}s - {seg['end']:5.1f}s] {seg['text']}")

# 3. Testar os 3 modos
modos = [
    ("CORRECTION", LyricsCorrector.MODE_CORRECTION, "Correção palavra por palavra (TESTADO ✅)"),
    ("HYBRID", LyricsCorrector.MODE_HYBRID, "Híbrido - mantém estrutura WhisperX (NOVO 🆕)"),
    ("SYNC", LyricsCorrector.MODE_SYNC, "Sincronização pura LRCLib (EXPERIMENTAL 🧪)"),
]

resultados = {}

for nome, modo, descricao in modos:
    print("\n" + "=" * 80)
    print(f"TESTANDO MODO: {nome}")
    print(f"Descrição: {descricao}")
    print("=" * 80)

    corrector = LyricsCorrector(mode=modo)
    corrected, num_corrections = corrector.correct(test_segments.copy(), reference_lyrics)

    resultados[nome] = {
        'segments': corrected,
        'corrections': num_corrections,
        'text': " ".join([s['text'] for s in corrected])
    }

    print(f"\n📋 RESULTADO ({num_corrections} correções):")
    print("-" * 80)
    for i, seg in enumerate(corrected[:15], 1):  # Mostrar primeiros 15
        print(f"{i:2d}. [{seg['start']:5.1f}s - {seg['end']:5.1f}s] {seg['text']}")

    if len(corrected) > 15:
        print(f"    ... (+{len(corrected) - 15} palavras)")

# 4. Comparar resultados
print("\n" + "=" * 80)
print("COMPARAÇÃO DOS RESULTADOS")
print("=" * 80)

print("\n🎯 VALIDAÇÃO: Procurando 'Janelle Monáe'")
print("-" * 80)

for nome in resultados:
    texto = resultados[nome]['text']
    num_corr = resultados[nome]['corrections']

    if "Janelle" in texto and "Monáe" in texto:
        status = "✅ SUCESSO"
    elif "Janelle" in texto:
        status = "⚠️ PARCIAL (só 'Janelle')"
    else:
        status = "❌ FALHOU"

    print(f"{nome:12s} | {status:20s} | {num_corr:3d} correções | {len(resultados[nome]['segments']):3d} segmentos")

# 5. Recomendação
print("\n" + "=" * 80)
print("RECOMENDAÇÃO")
print("=" * 80)

melhor_modo = None
melhor_score = -1

for nome in resultados:
    texto = resultados[nome]['text']
    score = 0

    # Pontos por encontrar Janelle Monáe
    if "Janelle" in texto:
        score += 10
    if "Monáe" in texto:
        score += 10

    # Pontos por manter estrutura (número razoável de segmentos)
    num_segs = len(resultados[nome]['segments'])
    if 10 <= num_segs <= 20:
        score += 5

    if score > melhor_score:
        melhor_score = score
        melhor_modo = nome

print(f"\n🏆 MODO RECOMENDADO: {melhor_modo}")
print(f"   Score: {melhor_score}/25 pontos")

print("\n💡 COMO ESCOLHER O MODO:")
print("   • CORRECTION: Mais conservador, preserva timestamps originais")
print("   • HYBRID: Melhor compromisso entre correção e timing")
print("   • SYNC: Usa letra 100% do LRCLib (pode desalinhar timing)")

print("\n" + "=" * 80)
