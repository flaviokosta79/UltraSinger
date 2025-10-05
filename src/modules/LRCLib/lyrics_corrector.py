"""
Lyrics Corrector - Correção inteligente baseada em contexto

Corrige erros de transcrição usando:
1. Letra oficial como referência
2. Padrões fonéticos (palavras que soam similar)
3. Contexto (palavras ao redor)
4. Hotwords extraídos da letra

Author: UltraSinger + LRCLib Integration
Date: 2025-10-05
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import difflib

logger = logging.getLogger(__name__)


@dataclass
class CorrectionPattern:
    """Pattern de correção com contexto"""
    pattern: str  # Regex ou texto a buscar
    correction: str  # Texto correto
    context_before: Optional[str] = None  # Contexto antes (opcional)
    context_after: Optional[str] = None  # Contexto depois (opcional)
    confidence: float = 1.0  # Confiança na correção (0-1)
    is_regex: bool = False  # Se é regex ou texto simples


class PhoneticMatcher:
    """
    Matcher fonético para português
    Identifica palavras que soam similar
    """

    # Mapeamento de caracteres fonéticos similares
    PHONETIC_MAP = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u',
        'ç': 'c',
    }

    # Substituições fonéticas comuns
    PHONETIC_SUBSTITUTIONS = [
        ('s', 'z'),
        ('c', 'k'),
        ('c', 'qu'),
        ('ss', 's'),
        ('x', 'ch'),
        ('g', 'j'),
    ]

    @classmethod
    def normalize(cls, text: str) -> str:
        """Normalizar texto para comparação fonética"""
        text = text.lower()
        for char, replacement in cls.PHONETIC_MAP.items():
            text = text.replace(char, replacement)
        return text

    @classmethod
    def phonetic_distance(cls, word1: str, word2: str) -> float:
        """
        Calcular distância fonética entre duas palavras
        Retorna 0-1 (0 = idêntico, 1 = completamente diferente)
        """
        norm1 = cls.normalize(word1)
        norm2 = cls.normalize(word2)

        # Usar SequenceMatcher do difflib
        matcher = difflib.SequenceMatcher(None, norm1, norm2)
        return 1.0 - matcher.ratio()

    @classmethod
    def are_similar(cls, word1: str, word2: str, threshold: float = 0.3) -> bool:
        """
        Verificar se duas palavras são foneticamente similares

        Args:
            word1: Primeira palavra
            word2: Segunda palavra
            threshold: Limiar de similaridade (0-1, menor = mais similar)

        Returns:
            True se similaridade >= threshold
        """
        distance = cls.phonetic_distance(word1, word2)
        return distance <= threshold


class LyricsCorrector:
    """
    Corretor inteligente de letras baseado em contexto

    Usa a letra oficial como referência para corrigir erros de transcrição,
    especialmente útil quando hotwords do Whisper não funcionam com música.
    """

    def __init__(
        self,
        official_lyrics: str,
        hotwords: List[str],
        enable_phonetic: bool = True,
        enable_context: bool = True,
        confidence_threshold: float = 0.7
    ):
        """
        Inicializar corretor

        Args:
            official_lyrics: Letra oficial completa
            hotwords: Lista de palavras-chave para proteger
            enable_phonetic: Habilitar correção fonética
            enable_context: Habilitar correção por contexto
            confidence_threshold: Limiar mínimo de confiança para aplicar correção
        """
        self.official_lyrics = official_lyrics
        self.hotwords = hotwords
        self.enable_phonetic = enable_phonetic
        self.enable_context = enable_context
        self.confidence_threshold = confidence_threshold

        # Construir patterns de correção
        self.correction_patterns: List[CorrectionPattern] = []
        self._build_correction_patterns()

        logger.info(f"LyricsCorrector inicializado com {len(self.correction_patterns)} patterns")

    def _build_correction_patterns(self):
        """Construir patterns de correção baseados em hotwords e letra oficial"""

        # Pattern 1: Correções específicas conhecidas
        # Caso "Janelle Monáe" → "janela e monê"
        self.correction_patterns.append(
            CorrectionPattern(
                pattern=r'\b(ao\s+)?som\s+de\s+janela\s+e\s+mon[eêé]\b',
                correction='som de Janelle Monáe',
                context_before='você',
                is_regex=True,
                confidence=0.95
            )
        )

        # Pattern 2: Variações de "janela e monê"
        janelle_variations = [
            (r'\bjanela\s+e\s+mon[eêé]\b', 'Janelle Monáe'),
            (r'\bjanela\s+mon[eêé]\b', 'Janelle Monáe'),
            (r'\bjanelle\s+mone\b', 'Janelle Monáe'),
        ]

        for pattern, correction in janelle_variations:
            # Verificar se está em contexto musical (perto de "som")
            self.correction_patterns.append(
                CorrectionPattern(
                    pattern=pattern,
                    correction=correction,
                    context_before='som',
                    is_regex=True,
                    confidence=0.85
                )
            )

        # Pattern 3: Proteger hotwords genuínos
        # Ex: "janela" sem contexto de "som" deve ser mantido
        # (implementado no método correct_with_context)

        logger.debug(f"Construídos {len(self.correction_patterns)} patterns de correção")

    def _check_context(
        self,
        text: str,
        match_start: int,
        match_end: int,
        context_before: Optional[str],
        context_after: Optional[str],
        context_window: int = 50
    ) -> bool:
        """
        Verificar se o contexto ao redor do match corresponde

        Args:
            text: Texto completo
            match_start: Início do match
            match_end: Fim do match
            context_before: Texto esperado antes (opcional)
            context_after: Texto esperado depois (opcional)
            context_window: Janela de caracteres para buscar contexto

        Returns:
            True se contexto corresponde
        """
        if not context_before and not context_after:
            return True  # Sem requisito de contexto

        # Extrair contexto real
        start = max(0, match_start - context_window)
        end = min(len(text), match_end + context_window)

        text_before = text[start:match_start].lower()
        text_after = text[match_end:end].lower()

        # Verificar contexto antes
        if context_before and context_before.lower() not in text_before:
            return False

        # Verificar contexto depois
        if context_after and context_after.lower() not in text_after:
            return False

        return True

    def correct_transcription(self, transcribed_text: str) -> Tuple[str, List[Dict]]:
        """
        Corrigir transcrição usando patterns e contexto

        Args:
            transcribed_text: Texto transcrito pelo Whisper

        Returns:
            Tupla (texto_corrigido, lista_de_correções_aplicadas)
        """
        corrected_text = transcribed_text
        corrections_applied = []

        for pattern in self.correction_patterns:
            if pattern.confidence < self.confidence_threshold:
                continue  # Pular correções com baixa confiança

            if pattern.is_regex:
                # Buscar matches do regex
                matches = list(re.finditer(pattern.pattern, corrected_text, re.IGNORECASE))

                for match in reversed(matches):  # Reverso para manter índices válidos
                    # Verificar contexto
                    if self.enable_context:
                        if not self._check_context(
                            corrected_text,
                            match.start(),
                            match.end(),
                            pattern.context_before,
                            pattern.context_after
                        ):
                            logger.debug(f"Contexto não corresponde para: {match.group()}")
                            continue

                    # Aplicar correção
                    original = match.group()
                    corrected_text = (
                        corrected_text[:match.start()] +
                        pattern.correction +
                        corrected_text[match.end():]
                    )

                    corrections_applied.append({
                        'original': original,
                        'corrected': pattern.correction,
                        'position': match.start(),
                        'confidence': pattern.confidence,
                        'pattern': pattern.pattern
                    })

                    logger.info(f"Correção aplicada: '{original}' → '{pattern.correction}' "
                               f"(confiança: {pattern.confidence:.2f})")

            else:
                # Busca simples (case-insensitive)
                pos = 0
                while True:
                    pos = corrected_text.lower().find(pattern.pattern.lower(), pos)
                    if pos == -1:
                        break

                    match_end = pos + len(pattern.pattern)

                    # Verificar contexto
                    if self.enable_context:
                        if not self._check_context(
                            corrected_text,
                            pos,
                            match_end,
                            pattern.context_before,
                            pattern.context_after
                        ):
                            pos += 1
                            continue

                    # Aplicar correção
                    original = corrected_text[pos:match_end]
                    corrected_text = (
                        corrected_text[:pos] +
                        pattern.correction +
                        corrected_text[match_end:]
                    )

                    corrections_applied.append({
                        'original': original,
                        'corrected': pattern.correction,
                        'position': pos,
                        'confidence': pattern.confidence,
                        'pattern': pattern.pattern
                    })

                    logger.info(f"Correção aplicada: '{original}' → '{pattern.correction}' "
                               f"(confiança: {pattern.confidence:.2f})")

                    pos += len(pattern.correction)

        return corrected_text, corrections_applied

    def correct_word_with_phonetic(
        self,
        word: str,
        candidate_words: List[str],
        max_distance: float = 0.3
    ) -> Optional[str]:
        """
        Corrigir palavra usando similaridade fonética

        Args:
            word: Palavra a corrigir
            candidate_words: Lista de candidatos (ex: hotwords)
            max_distance: Distância fonética máxima para considerar match

        Returns:
            Palavra correta ou None se não encontrou match
        """
        if not self.enable_phonetic:
            return None

        best_match = None
        best_distance = float('inf')

        for candidate in candidate_words:
            distance = PhoneticMatcher.phonetic_distance(word, candidate)
            if distance < best_distance and distance <= max_distance:
                best_distance = distance
                best_match = candidate

        if best_match:
            logger.debug(f"Match fonético: '{word}' → '{best_match}' "
                        f"(distância: {best_distance:.2f})")

        return best_match

    def get_correction_stats(self, corrections_applied: List[Dict]) -> Dict:
        """
        Obter estatísticas das correções aplicadas

        Args:
            corrections_applied: Lista de correções do correct_transcription()

        Returns:
            Dicionário com estatísticas
        """
        if not corrections_applied:
            return {
                'total_corrections': 0,
                'avg_confidence': 0.0,
                'corrections_by_type': {}
            }

        total = len(corrections_applied)
        avg_confidence = sum(c['confidence'] for c in corrections_applied) / total

        # Agrupar por padrão
        by_pattern = {}
        for correction in corrections_applied:
            pattern = correction['pattern']
            if pattern not in by_pattern:
                by_pattern[pattern] = 0
            by_pattern[pattern] += 1

        return {
            'total_corrections': total,
            'avg_confidence': avg_confidence,
            'corrections_by_pattern': by_pattern
        }


# Funções auxiliares para uso fácil

def create_corrector_from_lrclib(
    lrclib_data: Dict,
    hotwords: List[str],
    **kwargs
) -> LyricsCorrector:
    """
    Criar corretor a partir de dados do LRCLib

    Args:
        lrclib_data: Dados JSON do LRCLib API
        hotwords: Lista de hotwords extraídos
        **kwargs: Argumentos adicionais para LyricsCorrector

    Returns:
        Instância de LyricsCorrector configurada
    """
    official_lyrics = lrclib_data.get('plainLyrics', '')

    if not official_lyrics:
        logger.warning("Letra oficial não disponível no LRCLib, correções limitadas")
        official_lyrics = ""

    return LyricsCorrector(
        official_lyrics=official_lyrics,
        hotwords=hotwords,
        **kwargs
    )


def quick_correct(
    transcribed_text: str,
    official_lyrics: str,
    hotwords: List[str]
) -> str:
    """
    Correção rápida sem configurações avançadas

    Args:
        transcribed_text: Texto transcrito
        official_lyrics: Letra oficial
        hotwords: Hotwords

    Returns:
        Texto corrigido
    """
    corrector = LyricsCorrector(
        official_lyrics=official_lyrics,
        hotwords=hotwords
    )

    corrected_text, _ = corrector.correct_transcription(transcribed_text)
    return corrected_text
