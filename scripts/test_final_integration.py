"""
Teste Final - Integração Completa LRCLib + WhisperX + LyricsCorrector

Testa:
1. Busca no LRCLib
2. Extração de hotwords
3. Transcrição WhisperX com hotwords (asr_options)
4. Pós-processamento avançado (LyricsCorrector)
5. Correção clássica (compatibilidade)
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.LRCLib.lrclib_integration import LRCLibWhisperXIntegration

print("=" * 80)
print("🎵 TESTE FINAL - INTEGRAÇÃO COMPLETA")
print("=" * 80)
print()

# Configuração
AUDIO_PATH = r"E:\VSCode\Projects\UltraSinger\output\Pollo - Vagalumes\Pollo - Vagalumes.mp3"
ARTIST = "Pollo"
TRACK = "Vagalumes"
DURATION = 167  # segundos

print(f"📁 Áudio: {AUDIO_PATH}")
print(f"🎤 Artista: {ARTIST}")
print(f"🎵 Música: {TRACK}")
print(f"⏱️  Duração: {DURATION}s")
print()

# Inicializar integração
print("🔧 Inicializando integração LRCLib + WhisperX 3.4.3...")
integration = LRCLibWhisperXIntegration(whisperx_version="3.4.3")
print("✅ Integração inicializada")
print()

# Executar transcrição completa
print("🚀 Executando pipeline completo...")
print()

result = integration.transcribe_with_lrclib(
    audio_path=AUDIO_PATH,
    artist=ARTIST,
    track=TRACK,
    duration=DURATION,
    device="cuda",
    model_name="base",  # Usar base para ser mais rápido
    batch_size=8,
    compute_type="float16",
    language="pt"
)

print()
print("=" * 80)
print("📊 RESULTADO FINAL")
print("=" * 80)
print()

# Estatísticas
print("📈 ESTATÍSTICAS:")
print(f"   • Letra encontrada no LRCLib: {'✅ Sim' if result['lrclib_found'] else '❌ Não'}")
print(f"   • Hotwords extraídas: {len(result['hotwords_used'])}")
print(f"   • Correções avançadas: {result.get('advanced_corrections', 0)}")
print(f"   • Correções clássicas: {result['corrections_applied']}")
print(f"   • Idioma detectado: {result['language']}")
print(f"   • Total de segmentos: {len(result['segments'])}")
print()

# Mostrar hotwords
if result['hotwords_used']:
    print("🎯 HOTWORDS USADAS:")
    print(f"   {', '.join(result['hotwords_used'][:10])}")
    if len(result['hotwords_used']) > 10:
        print(f"   ... e mais {len(result['hotwords_used']) - 10}")
    print()

# Mostrar correções avançadas
if result.get('advanced_corrections_list'):
    print("🔧 CORREÇÕES AVANÇADAS APLICADAS:")
    for i, corr in enumerate(result['advanced_corrections_list'][:5], 1):
        print(f"   {i}. '{corr['original']}' → '{corr['corrected']}' "
              f"(confiança: {corr['confidence']:.2f})")
    if len(result['advanced_corrections_list']) > 5:
        print(f"   ... e mais {len(result['advanced_corrections_list']) - 5}")
    print()

# Procurar "Janelle Monáe" e "janela" nos segmentos
print("🔍 VERIFICANDO PALAVRAS-CHAVE:")
print("-" * 80)

found_janelle = False
found_janela = False
found_error = False

for seg in result['segments']:
    text = seg['text']
    text_lower = text.lower()
    start = seg.get('start', 0)

    # Procurar "Janelle Monáe"
    if 'janelle' in text_lower and 'monáe' in text_lower or 'monae' in text_lower:
        found_janelle = True
        print(f"✅ [{start:.1f}s] 'Janelle Monáe' encontrado: {text[:60]}...")

    # Procurar "janela" (genuíno, sem "som")
    if 'janela' in text_lower and 'som' not in text_lower:
        found_janela = True
        print(f"✅ [{start:.1f}s] 'janela' genuíno mantido: {text[:60]}...")

    # Procurar erro "janela e monê"
    if 'janela' in text_lower and 'monê' in text_lower and 'som' in text_lower:
        found_error = True
        print(f"❌ [{start:.1f}s] ERRO PERSISTENTE: {text[:60]}...")

print()

# Validação final
print("=" * 80)
print("🎯 VALIDAÇÃO FINAL")
print("=" * 80)
print()

if found_janelle and found_janela and not found_error:
    print("🎉 SUCESSO TOTAL!")
    print()
    print("✅ 'Janelle Monáe' corrigido corretamente (contexto musical)")
    print("✅ 'janela' genuíno mantido (contexto literal)")
    print("✅ Nenhum erro residual detectado")
    print()
    print("🏆 A integração está funcionando perfeitamente!")
elif found_janelle and not found_error:
    print("✅ SUCESSO PARCIAL!")
    print()
    print("✅ 'Janelle Monáe' corrigido corretamente")
    if not found_janela:
        print("⚠️  'janela' literal não encontrado (pode não estar nesse trecho)")
elif found_error:
    print("⚠️  ERRO DETECTADO!")
    print()
    print("❌ 'janela e monê' ainda presente")
    print("   Correção avançada não foi aplicada nesse segmento")
else:
    print("⚠️  RESULTADO INCONCLUSIVO")
    print()
    print("   Palavras-chave não encontradas")
    print("   Verificar segmentos manualmente")

print()
print("=" * 80)
print("📝 PRIMEIROS 10 SEGMENTOS:")
print("=" * 80)
for i, seg in enumerate(result['segments'][:10], 1):
    start = seg.get('start', 0)
    end = seg.get('end', 0)
    text = seg['text']
    print(f"{i:2d}. [{start:6.2f}s - {end:6.2f}s] {text[:70]}")

print()
print("=" * 80)
print("🏁 TESTE CONCLUÍDO")
print("=" * 80)
