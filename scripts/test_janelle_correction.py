"""
Teste específico para verificar correção de "janela e monê" -> "Janelle Monáe"
"""

import sys
sys.path.insert(0, 'src')

from modules.LRCLib.lrclib_integration import LyricsCorrector

# Simular segmentos do WhisperX
test_segments = [
    {'text': 'Eu', 'start': 2180, 'end': 2185},
    {'text': 'e', 'start': 2186, 'end': 2188},
    {'text': 'você', 'start': 2189, 'end': 2195},
    {'text': 'ao', 'start': 2196, 'end': 2198},
    {'text': 'som', 'start': 2199, 'end': 2203},
    {'text': 'de', 'start': 2204, 'end': 2207},
    {'text': 'janela', 'start': 2208, 'end': 2213},
    {'text': 'e', 'start': 2214, 'end': 2216},
    {'text': 'monê', 'start': 2217, 'end': 2229},
    {'text': 'Vem', 'start': 2230, 'end': 2237},
]

# Letra correta do LRCLib
reference_lyrics = """
Eu e você ao som de Janelle Monáe
Vem deixa acontecer e
"""

print("=" * 70)
print("TESTE DE CORREÇÃO - Janelle Monáe")
print("=" * 70)

# Criar corretor
corrector = LyricsCorrector()

# Testar correção
corrected, num_corrections = corrector.correct(test_segments, reference_lyrics)

print(f"\n{num_corrections} correções aplicadas\n")

print("ANTES DA CORREÇÃO:")
print("-" * 70)
for seg in test_segments:
    print(f"  {seg['text']}")

print("\nDEPOIS DA CORREÇÃO:")
print("-" * 70)
for seg in corrected:
    print(f"  {seg['text']}")

print("\n" + "=" * 70)

# Verificar se corrigiu
text_before = " ".join([s['text'] for s in test_segments])
text_after = " ".join([s['text'] for s in corrected])

if "Janelle" in text_after:
    print("✅ SUCESSO! Nome corrigido corretamente!")
else:
    print("❌ FALHA! Nome não foi corrigido")
    print(f"\nAntes:  {text_before}")
    print(f"Depois: {text_after}")
