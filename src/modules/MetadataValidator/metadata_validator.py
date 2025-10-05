"""
Metadata Validator - Validação cruzada entre LRCLib e Musicbrainz

Este módulo realiza validação cruzada de metadados de músicas usando múltiplas fontes:
- LRCLib (letras sincronizadas)
- Musicbrainz (banco de dados de música)
- YouTube (dados originais)

Retorna os metadados mais confiáveis baseado em scoring de confiança.
"""

from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher
import re


@dataclass
class MetadataSource:
    """Metadados de uma fonte específica"""
    artist: str
    title: str
    album: Optional[str] = None
    year: Optional[int] = None
    source: str = ""  # 'youtube', 'lrclib', 'musicbrainz'
    confidence: float = 0.0  # 0.0 a 1.0
    found: bool = False
    additional_data: Optional[Dict[str, Any]] = None


@dataclass
class ValidatedMetadata:
    """Resultado da validação cruzada"""
    artist: str
    title: str
    album: Optional[str] = None
    year: Optional[int] = None
    confidence: float = 0.0
    sources_agreement: float = 0.0  # Concordância entre fontes (0-1)
    primary_source: str = ""  # Fonte primária usada
    all_sources: Optional[Dict[str, MetadataSource]] = None


class MetadataValidator:
    """
    Validador de metadados com verificação cruzada entre múltiplas fontes
    """

    def __init__(self):
        self.similarity_threshold = 0.75  # Threshold para considerar similar

    def normalize_string(self, text: str) -> str:
        """Normaliza string para comparação (remove acentos, lowercase, etc)"""
        if not text:
            return ""

        # Lowercase
        text = text.lower()

        # Remover caracteres especiais comuns
        text = re.sub(r'[^\w\s-]', '', text)

        # Remover múltiplos espaços
        text = re.sub(r'\s+', ' ', text).strip()

        # Remover sufixos comuns do YouTube
        youtube_suffixes = [
            'official video', 'official music video', 'official audio',
            'lyric video', 'lyrics', 'vevo presents', 'live', 'acoustic',
            'remix', 'remaster', 'hd', '4k', 'explicit'
        ]
        for suffix in youtube_suffixes:
            if text.endswith(suffix):
                text = text[:-len(suffix)].strip()
            # Também remover entre parênteses
            text = re.sub(rf'\s*\({suffix}\)', '', text, flags=re.IGNORECASE)
            text = re.sub(rf'\s*\[{suffix}\]', '', text, flags=re.IGNORECASE)

        return text.strip()

    def calculate_similarity(self, str1: str, str2: str) -> float:
        """Calcula similaridade entre duas strings (0-1)"""
        if not str1 or not str2:
            return 0.0

        # Normalizar antes de comparar
        norm1 = self.normalize_string(str1)
        norm2 = self.normalize_string(str2)

        if norm1 == norm2:
            return 1.0

        # Usar SequenceMatcher para similaridade
        return SequenceMatcher(None, norm1, norm2).ratio()

    def validate_metadata(
        self,
        youtube_artist: str,
        youtube_title: str,
        lrclib_data: Optional[MetadataSource] = None,
        musicbrainz_data: Optional[MetadataSource] = None
    ) -> ValidatedMetadata:
        """
        Valida e retorna os metadados mais confiáveis

        Args:
            youtube_artist: Artista detectado do YouTube
            youtube_title: Título detectado do YouTube
            lrclib_data: Dados retornados do LRCLib (opcional)
            musicbrainz_data: Dados retornados do Musicbrainz (opcional)

        Returns:
            ValidatedMetadata com os dados mais confiáveis
        """

        # Fonte YouTube (baseline)
        youtube_source = MetadataSource(
            artist=youtube_artist,
            title=youtube_title,
            source='youtube',
            confidence=0.6,  # YouTube é razoavelmente confiável
            found=True
        )

        sources = {
            'youtube': youtube_source
        }

        if lrclib_data and lrclib_data.found:
            sources['lrclib'] = lrclib_data

        if musicbrainz_data and musicbrainz_data.found:
            sources['musicbrainz'] = musicbrainz_data

        # Calcular concordância entre fontes
        agreement_score = self._calculate_sources_agreement(sources)

        # Determinar qual fonte usar como primária
        primary_source, final_artist, final_title = self._determine_primary_source(
            sources, agreement_score
        )

        # Pegar metadados extras da melhor fonte disponível
        album = None
        year = None

        # Priorizar Musicbrainz para metadados extras
        if 'musicbrainz' in sources:
            album = sources['musicbrainz'].album
            year = sources['musicbrainz'].year
        elif 'lrclib' in sources:
            album = sources['lrclib'].album
            year = sources['lrclib'].year

        # Calcular confiança final
        final_confidence = self._calculate_final_confidence(
            sources, primary_source, agreement_score
        )

        return ValidatedMetadata(
            artist=final_artist,
            title=final_title,
            album=album,
            year=year,
            confidence=final_confidence,
            sources_agreement=agreement_score,
            primary_source=primary_source,
            all_sources=sources
        )

    def _calculate_sources_agreement(self, sources: Dict[str, MetadataSource]) -> float:
        """
        Calcula o nível de concordância entre as fontes (0-1)
        1.0 = todas as fontes concordam perfeitamente
        0.0 = nenhuma concordância
        """
        if len(sources) <= 1:
            return 1.0  # Uma fonte sempre concorda consigo mesma

        source_list = list(sources.values())
        agreements = []

        # Comparar cada par de fontes
        for i in range(len(source_list)):
            for j in range(i + 1, len(source_list)):
                source1 = source_list[i]
                source2 = source_list[j]

                # Similaridade do artista
                artist_sim = self.calculate_similarity(source1.artist, source2.artist)

                # Similaridade do título
                title_sim = self.calculate_similarity(source1.title, source2.title)

                # Concordância é a média das duas similaridades
                pair_agreement = (artist_sim + title_sim) / 2
                agreements.append(pair_agreement)

        # Retornar média de todas as concordâncias
        return sum(agreements) / len(agreements) if agreements else 0.0

    def _determine_primary_source(
        self,
        sources: Dict[str, MetadataSource],
        agreement_score: float
    ) -> Tuple[str, str, str]:
        """
        Determina qual fonte usar como primária e retorna (fonte, artista, título)

        Lógica de priorização:
        1. Se concordância alta (>0.85): usar fonte com maior confiança
        2. Se LRCLib encontrou: priorizar LRCLib (mais preciso para letras)
        3. Se apenas Musicbrainz: usar Musicbrainz
        4. Fallback: usar YouTube
        """

        # Alta concordância: todas as fontes concordam, usar a mais confiável
        if agreement_score > 0.85:
            best_source = max(sources.values(), key=lambda s: s.confidence)
            return best_source.source, best_source.artist, best_source.title

        # Concordância média-alta: priorizar LRCLib (mais preciso para música com letra)
        if agreement_score > 0.65 and 'lrclib' in sources:
            lrclib = sources['lrclib']
            return 'lrclib', lrclib.artist, lrclib.title

        # Concordância baixa: fontes divergem, usar heurísticas

        # Se LRCLib encontrou E título é muito diferente do YouTube
        if 'lrclib' in sources and 'youtube' in sources:
            lrclib = sources['lrclib']
            youtube = sources['youtube']

            title_similarity = self.calculate_similarity(lrclib.title, youtube.title)

            # Se títulos são similares (>0.7), confiar no LRCLib
            if title_similarity > 0.7:
                return 'lrclib', lrclib.artist, lrclib.title

            # Se muito diferentes, pode ser música errada do Musicbrainz
            # Manter YouTube nesse caso
            if title_similarity < 0.5:
                print(f"⚠️  Aviso: LRCLib/Musicbrainz retornou título muito diferente ({lrclib.title} vs {youtube.title})")
                print(f"   Usando dados do YouTube para maior precisão")
                return 'youtube', youtube.artist, youtube.title

        # Se apenas Musicbrainz disponível (sem LRCLib)
        if 'musicbrainz' in sources and 'lrclib' not in sources and 'youtube' in sources:
            mb = sources['musicbrainz']
            youtube = sources['youtube']

            # Verificar se Musicbrainz é muito diferente do YouTube
            title_similarity = self.calculate_similarity(mb.title, youtube.title)

            # Se títulos muito diferentes (<0.5), pode ser música errada
            if title_similarity < 0.5:
                print(f"⚠️  Aviso: Musicbrainz retornou título muito diferente")
                print(f"   YouTube: '{youtube.title}' vs Musicbrainz: '{mb.title}'")
                print(f"   Usando dados do YouTube (similaridade: {title_similarity:.0%})")
                return 'youtube', youtube.artist, youtube.title

            # Se similaridade razoável (>0.5), usar Musicbrainz
            return 'musicbrainz', mb.artist, mb.title

        # Fallback: YouTube
        youtube = sources['youtube']
        return 'youtube', youtube.artist, youtube.title

    def _calculate_final_confidence(
        self,
        sources: Dict[str, MetadataSource],
        primary_source: str,
        agreement_score: float
    ) -> float:
        """
        Calcula confiança final baseado em:
        - Confiança da fonte primária
        - Concordância entre fontes
        - Número de fontes disponíveis
        """

        if primary_source not in sources:
            return 0.5  # Confiança média se fonte primária não disponível

        base_confidence = sources[primary_source].confidence

        # Bonus por concordância entre fontes
        agreement_bonus = agreement_score * 0.2

        # Bonus por múltiplas fontes
        sources_bonus = min(len(sources) - 1, 2) * 0.1  # Máx 0.2 para 3+ fontes

        # Confiança final (máximo 1.0)
        final = min(base_confidence + agreement_bonus + sources_bonus, 1.0)

        return round(final, 2)


def create_lrclib_source(lrclib_result: Dict[str, Any]) -> Optional[MetadataSource]:
    """
    Cria MetadataSource a partir do resultado do LRCLib

    Args:
        lrclib_result: Dict retornado pela API do LRCLib

    Returns:
        MetadataSource ou None se não encontrado
    """
    if not lrclib_result or lrclib_result.get('instrumental', True):
        return None

    artist = lrclib_result.get('artistName', '')
    title = lrclib_result.get('trackName', '')
    album = lrclib_result.get('albumName')

    if not artist or not title:
        return None

    return MetadataSource(
        artist=artist,
        title=title,
        album=album,
        source='lrclib',
        confidence=0.9,  # LRCLib é muito confiável quando encontra
        found=True,
        additional_data=lrclib_result
    )


def create_musicbrainz_source(song_info) -> Optional[MetadataSource]:
    """
    Cria MetadataSource a partir do SongInfo do Musicbrainz

    Args:
        song_info: Objeto SongInfo retornado pelo search_musicbrainz

    Returns:
        MetadataSource ou None se não encontrado
    """
    if not song_info or not song_info.artist or not song_info.title:
        return None

    return MetadataSource(
        artist=song_info.artist,
        title=song_info.title,
        year=song_info.year,
        source='musicbrainz',
        confidence=0.75,  # Musicbrainz é confiável mas pode confundir músicas similares
        found=True,
        additional_data={
            'genres': song_info.genres,
            'cover_url': song_info.cover_url
        }
    )
