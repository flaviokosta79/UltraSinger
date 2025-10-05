"""
Teste do LyricsCorrector - Validar correções

Testa especificamente o caso "Janelle Monáe" → "janela e monê"
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.LRCLib.lyrics_corrector import LyricsCorrector, PhoneticMatcher

print("=" * 80)
print("🧪 TESTE DO LYRICS CORRECTOR")
print("=" * 80)
print()

# Letra oficial (simplificada)
OFFICIAL_LYRICS = """
Eu e você ao som de Janelle Monáe
Vem, deixa acontecer
Abro a janela pra que você possa ver
"""

# Hotwords
HOTWORDS = ["Janelle", "Monáe", "Vagalumes", "Pollo"]

# Criar corretor
print("1️⃣  CRIANDO CORRETOR")
print("-" * 80)
corrector = LyricsCorrector(
    official_lyrics=OFFICIAL_LYRICS,
    hotwords=HOTWORDS,
    enable_phonetic=True,
    enable_context=True,
    confidence_threshold=0.7
)
print(f"✅ Corretor criado com {len(corrector.correction_patterns)} patterns")
print()

# Teste 1: Correção "janela e monê" → "Janelle Monáe" (com contexto "som")
print("2️⃣  TESTE 1: Correção com contexto 'som'")
print("-" * 80)

text1 = "Eu e você ao som de janela e monê Vem, deixa acontecer"
print(f"Original: {text1}")

corrected1, corrections1 = corrector.correct_transcription(text1)
print(f"Corrigido: {corrected1}")
print(f"Correções aplicadas: {len(corrections1)}")

for i, corr in enumerate(corrections1):
    print(f"  {i+1}. '{corr['original']}' → '{corr['corrected']}' "
          f"(confiança: {corr['confidence']:.2f})")

if "Janelle Monáe" in corrected1 and "janela e monê" not in corrected1.lower():
    print("✅ TESTE 1 PASSOU: 'Janelle Monáe' corrigido corretamente!")
else:
    print("❌ TESTE 1 FALHOU: Correção não aplicada")
print()

# Teste 2: Manter "janela" sem contexto "som"
print("3️⃣  TESTE 2: Manter 'janela' genuíno (sem contexto 'som')")
print("-" * 80)

text2 = "Abro a janela pra que você possa ver"
print(f"Original: {text2}")

corrected2, corrections2 = corrector.correct_transcription(text2)
print(f"Corrigido: {corrected2}")
print(f"Correções aplicadas: {len(corrections2)}")

if "janela" in corrected2 and "Janelle" not in corrected2:
    print("✅ TESTE 2 PASSOU: 'janela' mantido corretamente!")
else:
    print("❌ TESTE 2 FALHOU: 'janela' foi incorretamente modificado")
print()

# Teste 3: Variações de escrita
print("4️⃣  TESTE 3: Variações de escrita")
print("-" * 80)

variations = [
    "ao som de janela e mone",
    "ao som de janela monê",
    "ao som de janelle mone",
]

for i, text in enumerate(variations):
    print(f"\nVariação {i+1}: {text}")
    corrected, corrections = corrector.correct_transcription(text)
    print(f"Corrigido: {corrected}")

    if "Janelle Monáe" in corrected:
        print("✅ Correção aplicada")
    else:
        print("⚠️  Correção não aplicada")

print()

# Teste 4: PhoneticMatcher
print("5️⃣  TESTE 4: Similaridade fonética")
print("-" * 80)

test_pairs = [
    ("janela", "Janelle", True),
    ("mone", "Monáe", True),
    ("vagalume", "Vagalumes", True),
    ("casa", "Janelle", False),
]

for word1, word2, should_be_similar in test_pairs:
    distance = PhoneticMatcher.phonetic_distance(word1, word2)
    is_similar = PhoneticMatcher.are_similar(word1, word2, threshold=0.3)

    status = "✅" if is_similar == should_be_similar else "❌"
    print(f"{status} '{word1}' vs '{word2}': distância={distance:.2f}, "
          f"similar={is_similar} (esperado: {should_be_similar})")

print()

# Teste 5: Texto completo (simulando transcrição real)
print("6️⃣  TESTE 5: Texto completo com múltiplas ocorrências")
print("-" * 80)

full_text = """
Vou caçar mais de um milhão de vagalumes por aí
Pra te ver sorrir
Eu vou de Marte até a Lua
Cê sabe, eu já tô na tua
Eu e você ao som de janela e monê
Vem, deixa acontecer
E me abraça que o tempo não passa
Saio do compasso, passo apuros que vier
Abro a janela pra que você possa ver
Vou caçar mais de um milhão de vagalumes por aí
"""

print("Original (trecho):")
print(full_text[:200] + "...")
print()

corrected_full, corrections_full = corrector.correct_transcription(full_text)

print(f"Correções aplicadas: {len(corrections_full)}")
for i, corr in enumerate(corrections_full):
    print(f"  {i+1}. Posição {corr['position']}: '{corr['original']}' → '{corr['corrected']}'")

print()
print("Texto corrigido (linhas com 'Janelle' ou 'janela'):")
for line in corrected_full.split('\n'):
    if 'janelle' in line.lower() or 'janela' in line.lower():
        print(f"  {line.strip()}")

print()

# Estatísticas
print("7️⃣  ESTATÍSTICAS FINAIS")
print("-" * 80)

stats = corrector.get_correction_stats(corrections_full)
print(f"Total de correções: {stats['total_corrections']}")
print(f"Confiança média: {stats['avg_confidence']:.2f}")
print(f"Correções por pattern:")
for pattern, count in stats['corrections_by_pattern'].items():
    print(f"  - {pattern}: {count}x")

print()
print("=" * 80)
print("🏁 TESTES CONCLUÍDOS")
print("=" * 80)

# Validação final
print()
print("🎯 VALIDAÇÃO FINAL:")
print("-" * 80)

# Verificar se "Janelle Monáe" aparece E "janela" também (em contextos diferentes)
has_janelle = "Janelle Monáe" in corrected_full
has_janela = "janela" in corrected_full.lower() and "som" not in corrected_full[corrected_full.lower().find("janela")-20:corrected_full.lower().find("janela")+20].lower() if "janela" in corrected_full.lower() else False

print(f"✅ 'Janelle Monáe' corrigido: {has_janelle}")
print(f"✅ 'janela' genuíno mantido: {has_janela}")

if has_janelle and has_janela:
    print()
    print("🎉 SUCESSO TOTAL! Corretor funcionando perfeitamente!")
    print("   - 'Janelle Monáe' corrigido em contexto musical")
    print("   - 'janela' mantido em contexto literal")
else:
    print()
    print("⚠️  Atenção: Revisar lógica de correção")
