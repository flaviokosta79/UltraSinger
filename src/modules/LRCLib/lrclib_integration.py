"""
LRCLib Integration Module for UltraSinger
==========================================
Integra API do LRCLib com WhisperX para melhorar transcrições

Features:
- Busca automática de letras no LRCLib
- Extração de hotwords da letra para WhisperX 3.4.3
- Correção de transcrição usando letra como referência
- Merge inteligente de timestamps WhisperX + texto LRCLib
"""

import requests
import re
from typing import Optional, List, Dict, Tuple
from difflib import SequenceMatcher
from dataclasses import dataclass


@dataclass
class LRCLibLyrics:
    """Dados da letra do LRCLib"""
    id: int
    track_name: str
    artist_name: str
    album_name: Optional[str]
    duration: int
    instrumental: bool
    plain_lyrics: str
    synced_lyrics: Optional[str]


class LRCLibAPI:
    """Cliente para API do LRCLib"""

    BASE_URL = "https://lrclib.net/api"
    USER_AGENT = "UltraSinger/1.0 (https://github.com/rakuri255/UltraSinger)"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})

    def get_lyrics(
        self,
        artist: str,
        track: str,
        album: Optional[str] = None,
        duration: Optional[int] = None,
        use_cached: bool = False
    ) -> Optional[LRCLibLyrics]:
        """
        Busca letra no LRCLib

        Args:
            artist: Nome do artista
            track: Nome da música
            album: Nome do álbum (opcional)
            duration: Duração em segundos (±2s tolerância)
            use_cached: Se True, usa apenas cache do LRCLib (mais rápido)

        Returns:
            LRCLibLyrics ou None se não encontrado
        """

        # Tentar busca exata se tiver duração
        if duration:
            result = self._get_by_signature(
                artist, track, album, duration, use_cached
            )
            if result:
                return result

        # Fallback: busca por query
        return self._search_lyrics(artist, track)

    def _get_by_signature(
        self,
        artist: str,
        track: str,
        album: Optional[str],
        duration: int,
        use_cached: bool
    ) -> Optional[LRCLibLyrics]:
        """Busca pela assinatura exata da música"""

        endpoint = "/get-cached" if use_cached else "/get"

        params = {
            "artist_name": artist,
            "track_name": track,
            "duration": int(duration)
        }

        if album:
            params["album_name"] = album

        try:
            response = self.session.get(
                f"{self.BASE_URL}{endpoint}",
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return self._parse_lyrics_response(data)

            elif response.status_code == 404:
                # Não encontrado - tentar busca
                return None

            else:
                print(f"⚠️ LRCLib retornou status {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            print("⚠️ Timeout ao buscar letra no LRCLib")
            return None
        except Exception as e:
            print(f"⚠️ Erro ao buscar no LRCLib: {e}")
            return None

    def _search_lyrics(
        self,
        artist: str,
        track: str
    ) -> Optional[LRCLibLyrics]:
        """Busca letra por query (menos preciso)"""

        try:
            response = self.session.get(
                f"{self.BASE_URL}/search",
                params={
                    "artist_name": artist,
                    "track_name": track
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                results = response.json()
                if results:
                    # Retornar primeiro resultado
                    return self._parse_lyrics_response(results[0])

            return None

        except Exception as e:
            print(f"⚠️ Erro ao buscar no LRCLib: {e}")
            return None

    def _parse_lyrics_response(self, data: Dict) -> LRCLibLyrics:
        """Converte resposta JSON para LRCLibLyrics"""
        return LRCLibLyrics(
            id=data.get("id", 0),
            track_name=data.get("trackName", ""),
            artist_name=data.get("artistName", ""),
            album_name=data.get("albumName"),
            duration=data.get("duration", 0),
            instrumental=data.get("instrumental", False),
            plain_lyrics=data.get("plainLyrics", ""),
            synced_lyrics=data.get("syncedLyrics")
        )


class HotwordExtractor:
    """Extrai hotwords da letra para usar no WhisperX"""

    # Palavras comuns em português (não usar como hotwords)
    COMMON_WORDS = {
        'o', 'a', 'de', 'da', 'do', 'em', 'um', 'uma', 'os', 'as',
        'que', 'para', 'com', 'não', 'por', 'mais', 'se', 'no', 'na',
        'eu', 'você', 'ele', 'ela', 'nós', 'eles', 'elas',
        'é', 'foi', 'são', 'ser', 'estar', 'ter', 'fazer',
        'amor', 'vida', 'coração', 'sempre', 'nunca', 'tudo', 'nada',
        'quando', 'onde', 'como', 'porque', 'quero', 'posso',
        'yeah', 'baby', 'oh', 'hey', 'ooh', 'ah', 'la'
    }

    def extract(self, lyrics: str, max_hotwords: int = 50) -> List[str]:
        """
        Extrai hotwords da letra

        Args:
            lyrics: Letra da música
            max_hotwords: Máximo de hotwords a retornar

        Returns:
            Lista de hotwords únicas
        """

        # Limpar timestamps se houver
        lyrics_clean = re.sub(r'\[\d+:\d+\.\d+\]', '', lyrics)

        # Remover pontuação mas manter palavras
        lyrics_clean = re.sub(r'[^\w\s]', ' ', lyrics_clean)

        # Separar em palavras
        words = lyrics_clean.split()

        hotwords = set()

        for word in words:
            word_clean = word.strip().lower()

            if not word_clean or len(word_clean) < 3:
                continue

            # Adicionar se:
            # 1. Começa com maiúscula (nome próprio)
            # 2. Tem mais de 6 letras (palavra específica)
            # 3. Não é palavra comum

            if word[0].isupper():
                # Provável nome próprio - manter capitalização original
                hotwords.add(word.strip())

            elif len(word_clean) > 6 and word_clean not in self.COMMON_WORDS:
                # Palavra longa e não comum
                hotwords.add(word_clean)

        # Converter para lista e limitar
        return sorted(list(hotwords))[:max_hotwords]


class LyricsCorrector:
    """Corrige transcrição WhisperX usando letra LRCLib como referência"""

    def __init__(self, similarity_threshold: float = 0.8):
        """
        Args:
            similarity_threshold: Limiar de similaridade (0-1)
                                  Acima deste valor, considera correto
        """
        self.similarity_threshold = similarity_threshold

    def correct(
        self,
        whisperx_segments: List[Dict],
        lrclib_lyrics: str
    ) -> Tuple[List[Dict], int]:
        """
        Corrige segmentos do WhisperX usando letra LRCLib

        Args:
            whisperx_segments: Segmentos transcritos pelo WhisperX
            lrclib_lyrics: Letra do LRCLib (plain text)

        Returns:
            Tupla (segmentos_corrigidos, numero_de_correcoes)
        """

        # Limpar letra LRCLib
        lrclib_clean = self._clean_lyrics(lrclib_lyrics)

        # Combinar texto WhisperX
        whisperx_text = " ".join([
            seg['text'].strip() for seg in whisperx_segments
        ])

        # Calcular similaridade
        similarity = self._calculate_similarity(whisperx_text, lrclib_clean)

        print(f"📊 Similaridade WhisperX vs LRCLib: {similarity:.2%}")

        # SEMPRE aplicar correções, mesmo com alta similaridade
        # Motivo: nomes próprios, acentos e pequenas diferenças são importantes
        if similarity >= 0.95:
            print("ℹ️ Transcrição muito precisa, mas verificando nomes próprios...")
        
        # Aplicar correções palavra por palavra
        corrected, num_corrections = self._apply_word_corrections(
            whisperx_segments,
            lrclib_clean
        )
        
        if num_corrections > 0:
            print(f"✏️ {num_corrections} correções aplicadas usando LRCLib")
        else:
            print("ℹ️ Nenhuma correção necessária")
        
        return corrected, num_corrections

    def _clean_lyrics(self, lyrics: str) -> str:
        """Remove timestamps e normaliza texto"""
        # Remover timestamps
        clean = re.sub(r'\[\d+:\d+\.\d+\]', '', lyrics)
        # Normalizar espaços
        clean = " ".join(clean.split())
        return clean.strip()

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade entre dois textos (0-1)"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def _apply_word_corrections(
        self,
        segments: List[Dict],
        reference_lyrics: str
    ) -> Tuple[List[Dict], int]:
        """
        Aplica correções palavra por palavra usando alinhamento inteligente
        
        Estratégia:
        1. Extrai todas as palavras da transcrição e referência
        2. Alinha usando SequenceMatcher (lida com inserções/deleções/substituições)
        3. Aplica correções mantendo timestamps dos segmentos originais
        4. Lida com nomes compostos (ex: "janela e monê" -> "Janelle Monáe")
        """
        
        # Extrair todas as palavras transcritas
        transcribed_words = []
        for seg in segments:
            transcribed_words.extend(seg['text'].split())
        
        # Extrair palavras de referência
        reference_words = reference_lyrics.split()
        
        # Alinhar palavras usando SequenceMatcher
        matcher = SequenceMatcher(
            None,
            [w.lower() for w in transcribed_words],
            [w.lower() for w in reference_words]
        )
        
        # Construir mapa de correções: índice_transcrito -> palavra_correta
        word_corrections = {}
        corrections_made = 0
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                # Palavras diferentes - aplicar correção
                # i1:i2 são índices em transcribed_words
                # j1:j2 são índices em reference_words
                
                trans_slice = transcribed_words[i1:i2]
                ref_slice = reference_words[j1:j2]
                
                # Caso 1: Mesma quantidade de palavras - substituição 1:1
                if len(trans_slice) == len(ref_slice):
                    for idx, (trans_w, ref_w) in enumerate(zip(trans_slice, ref_slice)):
                        if trans_w.lower() != ref_w.lower():
                            word_corrections[i1 + idx] = ref_w
                            corrections_made += 1
                
                # Caso 2: Mais palavras transcritas (3) que referência (2)
                # Ex: ["janela", "e", "monê"] -> ["Janelle", "Monáe"]
                elif len(trans_slice) > len(ref_slice):
                    # Marcar primeiro conjunto de palavras para correção composta
                    combined_ref = " ".join(ref_slice)
                    word_corrections[i1] = combined_ref
                    
                    # Marcar palavras subsequentes para remoção
                    for idx in range(1, len(trans_slice)):
                        word_corrections[i1 + idx] = ""  # Remove
                    
                    corrections_made += 1
                
                # Caso 3: Menos palavras transcritas que referência
                # Ex: ["Janelle"] -> ["Janelle", "Monáe"]
                elif len(trans_slice) < len(ref_slice):
                    # Expandir primeira palavra
                    combined_ref = " ".join(ref_slice)
                    word_corrections[i1] = combined_ref
                    corrections_made += 1
            
            elif tag == 'delete':
                # Palavras extras na transcrição - remover
                for idx in range(i1, i2):
                    word_corrections[idx] = ""
                    corrections_made += 1
            
            elif tag == 'insert':
                # Palavras faltando na transcrição - adicionar após posição anterior
                # (mais complexo, skip por enquanto)
                pass
        
        # Aplicar correções aos segmentos mantendo timestamps
        corrected_segments = []
        word_idx = 0
        
        for segment in segments:
            segment_copy = segment.copy()
            words = segment['text'].split()
            corrected_words = []
            
            for word in words:
                if word_idx in word_corrections:
                    corrected = word_corrections[word_idx]
                    if corrected:  # Não é remoção
                        corrected_words.append(corrected)
                else:
                    corrected_words.append(word)
                word_idx += 1
            
            segment_copy['text'] = " ".join(corrected_words)
            corrected_segments.append(segment_copy)
        
        return corrected_segments, corrections_made


class LRCLibWhisperXIntegration:
    """Integração completa LRCLib + WhisperX"""

    def __init__(self, whisperx_version: str = "3.4.3"):
        self.lrclib = LRCLibAPI()
        self.hotword_extractor = HotwordExtractor()
        self.corrector = LyricsCorrector()
        self.whisperx_version = whisperx_version
        self.supports_hotwords = whisperx_version >= "3.4.0"

    def transcribe_with_lrclib(
        self,
        audio_path: str,
        artist: str,
        track: str,
        album: Optional[str] = None,
        duration: Optional[int] = None,
        device: str = "cuda",
        use_lrclib_cache: bool = False,
        model_name: str = "base",
        align_model: Optional[str] = None,
        batch_size: int = 16,
        compute_type: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict:
        """
        Pipeline completo:
        1. Busca letra no LRCLib
        2. Extrai hotwords (se 3.4.3+)
        3. Transcreve com WhisperX
        4. Corrige usando LRCLib

        Args:
            audio_path: Caminho do arquivo de áudio
            artist: Nome do artista
            track: Nome da música
            album: Nome do álbum (opcional)
            duration: Duração em segundos
            device: 'cuda' ou 'cpu'
            use_lrclib_cache: Usar apenas cache (mais rápido)

        Returns:
            Dict com:
            - segments: Segmentos transcritos e corrigidos
            - language: Idioma detectado
            - lrclib_found: Se encontrou letra no LRCLib
            - lrclib_data: Dados do LRCLib (se encontrado)
            - hotwords_used: Lista de hotwords usadas
            - corrections_applied: Número de correções
        """

        print("\n" + "="*70)
        print("🎵 TRANSCRIÇÃO COM LRCLIB + WHISPERX")
        print("="*70)

        # PASSO 1: Buscar letra no LRCLib
        print(f"\n🔍 Buscando letra de '{track}' - '{artist}' no LRCLib...")

        lrclib_data = self.lrclib.get_lyrics(
            artist=artist,
            track=track,
            album=album,
            duration=duration,
            use_cached=use_lrclib_cache
        )

        hotwords = []

        if lrclib_data:
            print(f"✅ Letra encontrada!")
            print(f"   • ID: {lrclib_data.id}")
            print(f"   • Instrumental: {'Sim' if lrclib_data.instrumental else 'Não'}")

            if not lrclib_data.instrumental and self.supports_hotwords:
                # PASSO 2: Extrair hotwords
                print("\n🎯 Extraindo hotwords da letra...")
                hotwords = self.hotword_extractor.extract(
                    lrclib_data.plain_lyrics
                )
                print(f"   • Hotwords encontradas: {len(hotwords)}")
                if hotwords:
                    print(f"   • Exemplos: {', '.join(hotwords[:5])}")
        else:
            print("⚠️ Letra não encontrada no LRCLib")
            print("   Continuando apenas com WhisperX...")

        # PASSO 3: Transcrever com WhisperX
        print("\n🎤 Transcrevendo com WhisperX...")

        import whisperx

        # Preparar kwargs para load_model (remover None)
        load_kwargs = {
            "device": device
        }
        if compute_type:
            load_kwargs["compute_type"] = compute_type
        if language:
            load_kwargs["language"] = language

        model = whisperx.load_model(model_name, **load_kwargs)
        audio = whisperx.load_audio(audio_path)

        transcribe_kwargs: Dict = {}

        if language:
            transcribe_kwargs["language"] = language

        if hotwords and self.supports_hotwords:
            transcribe_kwargs["hotwords"] = hotwords  # type: ignore
            print(f"   ✨ Usando {len(hotwords)} hotwords do LRCLib")

        result = model.transcribe(audio, batch_size=batch_size, **transcribe_kwargs)

        print(f"   ✅ Transcrição concluída")
        print(f"   • Idioma: {result['language']}")
        print(f"   • Segmentos: {len(result['segments'])}")

        # PASSO 4: Corrigir com LRCLib
        corrections = 0
        corrected_segments = result['segments']

        if lrclib_data and not lrclib_data.instrumental:
            print("\n✏️ Aplicando correções do LRCLib...")
            corrected_segments, corrections = self.corrector.correct(
                result['segments'],
                lrclib_data.plain_lyrics
            )

            if corrections > 0:
                print(f"   ✅ {corrections} correções aplicadas")
            else:
                print("   ✅ Nenhuma correção necessária (transcrição precisa!)")

        # Resultado final
        print("\n" + "="*70)
        print("✅ TRANSCRIÇÃO COMPLETA!")
        print("="*70)

        return {
            'segments': corrected_segments,
            'language': result['language'],
            'lrclib_found': lrclib_data is not None,
            'lrclib_data': lrclib_data,
            'hotwords_used': hotwords,
            'corrections_applied': corrections
        }


# =============================================================================
# EXEMPLO DE USO
# =============================================================================

def example_usage():
    """Exemplo de uso do módulo"""

    # Inicializar integração
    integration = LRCLibWhisperXIntegration(whisperx_version="3.4.3")

    # Transcrever com LRCLib
    result = integration.transcribe_with_lrclib(
        audio_path=r"E:\VSCode\Projects\UltraSinger\output\Pollo - Vagalumes\Pollo - Vagalumes.mp3",
        artist="Pollo",
        track="Vagalumes",
        duration=170,
        device="cuda"
    )

    # Exibir resultado
    print("\n📊 ESTATÍSTICAS:")
    print(f"   • Letra encontrada no LRCLib: {'✅ Sim' if result['lrclib_found'] else '❌ Não'}")
    print(f"   • Hotwords usadas: {len(result['hotwords_used'])}")
    print(f"   • Correções aplicadas: {result['corrections_applied']}")
    print(f"   • Idioma detectado: {result['language']}")
    print(f"   • Total de segmentos: {len(result['segments'])}")

    print("\n📝 PRIMEIROS 5 SEGMENTOS:")
    for i, seg in enumerate(result['segments'][:5], 1):
        print(f"   {i}. [{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['text']}")


if __name__ == "__main__":
    example_usage()
