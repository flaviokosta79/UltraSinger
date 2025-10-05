"""
Teste: Validação corrigida com limpeza de título
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.MetadataValidator import MetadataValidator, MetadataSource
import re

print("=" * 80)
print("🧪 TESTE: Validação Corrigida (YouTube vs Musicbrainz sem LRCLib)")
print("=" * 80)
print()

# Simular cenário real: LRCLib não encontrou, YouTube vs Musicbrainz
validator = MetadataValidator()

# Dados do YouTube (corretos)
youtube_artist = "ANAVITÓRIA"
youtube_title = "Trevo (Vevo Presents)"

# Dados do Musicbrainz (errados - música diferente)
musicbrainz_data = MetadataSource(
    artist="Anavitória",
    title="Outrória",
    year=2018,
    source="musicbrainz",
    confidence=0.75,
    found=True
)

# LRCLib NÃO encontrou (None)
lrclib_data = None

print("📺 DADOS DO YOUTUBE:")
print(f"   Artista: {youtube_artist}")
print(f"   Música: {youtube_title}")
print()

print("🎵 DADOS DO MUSICBRAINZ:")
print(f"   Artista: {musicbrainz_data.artist}")
print(f"   Música: {musicbrainz_data.title}")
print()

print("🔍 LRCLIB:")
print(f"   Status: Não encontrado")
print()

# Calcular similaridade manualmente
normalized_yt = validator.normalize_string(youtube_title)
normalized_mb = validator.normalize_string(musicbrainz_data.title)
similarity = validator.calculate_similarity(youtube_title, musicbrainz_data.title)

print(f"📊 ANÁLISE DE SIMILARIDADE:")
print(f"   YouTube normalizado: '{normalized_yt}'")
print(f"   Musicbrainz normalizado: '{normalized_mb}'")
print(f"   Similaridade: {similarity:.2%}")
print()

# Executar validação
result = validator.validate_metadata(
    youtube_artist=youtube_artist,
    youtube_title=youtube_title,
    lrclib_data=lrclib_data,
    musicbrainz_data=musicbrainz_data
)

print("=" * 80)
print("✅ RESULTADO DA VALIDAÇÃO:")
print("=" * 80)
print(f"   Artista final: {result.artist}")
print(f"   Título final: {result.title}")
print(f"   Fonte primária: {result.primary_source}")
print(f"   Confiança: {result.confidence*100:.0f}%")
print(f"   Concordância: {result.sources_agreement*100:.0f}%")
print()

# Verificar se escolheu corretamente
if result.primary_source == "youtube":
    print("✅ PASSOU: Escolheu YouTube (correto - Musicbrainz estava errado)")
    print(f"   Música: {result.title}")
elif result.primary_source == "musicbrainz":
    print("❌ FALHOU: Escolheu Musicbrainz (errado - deveria ser YouTube)")
    print(f"   Música errada: {result.title}")
else:
    print(f"⚠️  Resultado inesperado: {result.primary_source}")

print()
print("=" * 80)

# Teste adicional: Limpar título do YouTube
print()
print("🧹 TESTE ADICIONAL: Limpeza de Título")
print("=" * 80)

clean_title = youtube_title
youtube_suffixes = [
    'official video', 'official music video', 'official audio',
    'lyric video', 'lyrics', 'vevo presents', 'live', 'acoustic',
    'remix', 'remaster', 'hd', '4k', 'explicit', 'visualizer'
]
for suffix in youtube_suffixes:
    clean_title = re.sub(rf'\s*\({suffix}\)', '', clean_title, flags=re.IGNORECASE)
    clean_title = re.sub(rf'\s*\[{suffix}\]', '', clean_title, flags=re.IGNORECASE)
clean_title = clean_title.strip()

print(f"   Título original: '{youtube_title}'")
print(f"   Título limpo: '{clean_title}'")
print()

if clean_title == "Trevo":
    print("✅ Limpeza funcionou: 'Trevo (Vevo Presents)' → 'Trevo'")
else:
    print(f"⚠️  Limpeza não funcionou completamente: '{clean_title}'")

print()
print("=" * 80)
print("🏁 TESTE CONCLUÍDO")
print("=" * 80)
