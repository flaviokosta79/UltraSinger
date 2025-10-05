"""
Teste: Validação cruzada de metadados
Testar MetadataValidator com casos reais
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.MetadataValidator import MetadataValidator, MetadataSource

print("=" * 80)
print("🧪 TESTE: Validação Cruzada de Metadados")
print("=" * 80)
print()

validator = MetadataValidator()

# ==========================================
# CASO 1: YouTube correto, Musicbrainz errado
# ==========================================
print("📝 CASO 1: YouTube vs Musicbrainz (Anavitória - Trevo)")
print("-" * 80)

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

# Dados do LRCLib (corretos)
lrclib_data = MetadataSource(
    artist="Anavitória",
    title="Trevo (Tu)",
    source="lrclib",
    confidence=0.9,
    found=True
)

result = validator.validate_metadata(
    youtube_artist=youtube_artist,
    youtube_title=youtube_title,
    lrclib_data=lrclib_data,
    musicbrainz_data=musicbrainz_data
)

print(f"\n✅ RESULTADO:")
print(f"   Artista final: {result.artist}")
print(f"   Título final: {result.title}")
print(f"   Fonte primária: {result.primary_source}")
print(f"   Confiança: {result.confidence*100:.0f}%")
print(f"   Concordância: {result.sources_agreement*100:.0f}%")
print(f"\n   Fontes disponíveis: {', '.join(result.all_sources.keys())}")

# Verificar se escolheu corretamente (deve ser LRCLib ou YouTube, não Musicbrainz)
if "outrória" in result.title.lower():
    print(f"\n❌ FALHOU: Escolheu Musicbrainz errado ('Outrória')")
else:
    print(f"\n✅ PASSOU: Evitou Musicbrainz errado")

print()
print()

# ==========================================
# CASO 2: Todas concordam
# ==========================================
print("📝 CASO 2: Alta concordância entre fontes")
print("-" * 80)

lrclib_data2 = MetadataSource(
    artist="Pollo",
    title="Vagalumes",
    source="lrclib",
    confidence=0.9,
    found=True
)

musicbrainz_data2 = MetadataSource(
    artist="Pollo",
    title="Vagalumes",
    year=2013,
    source="musicbrainz",
    confidence=0.75,
    found=True
)

result2 = validator.validate_metadata(
    youtube_artist="Pollo",
    youtube_title="Vagalumes",
    lrclib_data=lrclib_data2,
    musicbrainz_data=musicbrainz_data2
)

print(f"\n✅ RESULTADO:")
print(f"   Artista final: {result2.artist}")
print(f"   Título final: {result2.title}")
print(f"   Fonte primária: {result2.primary_source}")
print(f"   Confiança: {result2.confidence*100:.0f}%")
print(f"   Concordância: {result2.sources_agreement*100:.0f}%")

if result2.sources_agreement > 0.85:
    print(f"\n✅ PASSOU: Alta concordância detectada")
else:
    print(f"\n⚠️  Aviso: Concordância menor que esperado")

print()
print()

# ==========================================
# CASO 3: Apenas YouTube (sem outras fontes)
# ==========================================
print("📝 CASO 3: Apenas dados do YouTube")
print("-" * 80)

result3 = validator.validate_metadata(
    youtube_artist="Artista Desconhecido",
    youtube_title="Música Rara"
)

print(f"\n✅ RESULTADO:")
print(f"   Artista final: {result3.artist}")
print(f"   Título final: {result3.title}")
print(f"   Fonte primária: {result3.primary_source}")
print(f"   Confiança: {result3.confidence*100:.0f}%")
print(f"   Concordância: {result3.sources_agreement*100:.0f}%")

if result3.primary_source == "youtube":
    print(f"\n✅ PASSOU: Usou YouTube como fallback")
else:
    print(f"\n❌ FALHOU: Deveria usar YouTube")

print()
print("=" * 80)
print("🏁 TESTE CONCLUÍDO")
print("=" * 80)
