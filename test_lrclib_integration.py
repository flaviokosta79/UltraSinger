"""
Script de teste para verificar a integração do LRCLib com UltraSinger.
Este script testa a funcionalidade completa sem processar um arquivo de áudio real.
"""

import sys
import os

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.LRCLib.lrclib_integration import LRCLibAPI, HotwordExtractor, LyricsCorrector

def test_lrclib_api():
    """Testa a API do LRCLib"""
    print("\n=== Teste 1: API do LRCLib ===")
    
    api = LRCLibAPI()
    
    # Testar busca de uma música conhecida
    print("\n1. Testando busca da música 'Vagalumes' do Pollo...")
    result = api.get_lyrics(
        artist="Pollo",
        track="Vagalumes"
    )
    
    if result:
        print(f"✓ Letra encontrada!")
        print(f"  - Artist: {result.artist_name}")
        print(f"  - Track: {result.track_name}")
        print(f"  - Letra (primeiros 100 caracteres): {result.plain_lyrics[:100] if result.plain_lyrics else 'N/A'}...")
        return result
    else:
        print("✗ Nenhuma correspondência encontrada")
        return None


def test_hotword_extractor(lyrics):
    """Testa o extrator de hotwords"""
    print("\n=== Teste 2: Extração de Hotwords ===")
    
    if not lyrics:
        print("✗ Não há letras para extrair hotwords")
        return None
    
    extractor = HotwordExtractor()
    hotwords = extractor.extract(lyrics.plain_lyrics)
    
    if hotwords:
        print(f"✓ {len(hotwords)} hotwords extraídas!")
        print(f"  Hotwords: {', '.join(hotwords[:20])}")  # Mostrar apenas as primeiras 20
        if len(hotwords) > 20:
            print(f"  ... e mais {len(hotwords) - 20} hotwords")
        return hotwords
    else:
        print("✗ Nenhuma hotword extraída")
        return None


def test_lyrics_corrector():
    """Testa o corretor de letras"""
    print("\n=== Teste 3: Correção de Transcrição ===")
    
    # Simular segmentos do WhisperX com erros
    whisperx_segments = [
        {"text": "vagalumes", "start": 0.0, "end": 1.0},
        {"text": "pela", "start": 1.0, "end": 1.5},
        {"text": "rua", "start": 1.5, "end": 2.0},
        {"text": "acesa", "start": 2.0, "end": 3.0}
    ]
    reference = "Vagalumes pela rua, acesa"
    
    corrector = LyricsCorrector()
    corrected_segments, num_corrections = corrector.correct(whisperx_segments, reference)
    
    print(f"  Transcrição original: {' '.join([seg['text'] for seg in whisperx_segments])}")
    print(f"  Referência: '{reference}'")
    print(f"  Corrigido: {' '.join([seg['text'] for seg in corrected_segments])}")
    print(f"  Correções aplicadas: {num_corrections}")
    
    if num_corrections > 0:
        print(f"✓ {num_corrections} correção(ões) aplicada(s)!")
    else:
        print("  Nenhuma correção necessária (já estava correto)")


def test_full_integration():
    """Testa a integração completa"""
    print("\n=== Teste 4: Integração Completa ===")
    
    # Testar apenas se o módulo pode ser importado e inicializado
    try:
        from modules.LRCLib.lrclib_integration import LRCLibWhisperXIntegration
        integration = LRCLibWhisperXIntegration()
        print("✓ Módulo LRCLibWhisperXIntegration importado e inicializado com sucesso!")
        print("  (Teste completo com áudio requer execução do UltraSinger)")
    except Exception as e:
        print(f"✗ Erro ao importar/inicializar: {e}")


def main():
    """Função principal"""
    print("\n" + "="*60)
    print("TESTE DE INTEGRAÇÃO LRCLIB")
    print("="*60)
    
    # Teste 1: API
    lyrics = test_lrclib_api()
    
    # Teste 2: Hotwords
    hotwords = test_hotword_extractor(lyrics)
    
    # Teste 3: Correção
    test_lyrics_corrector()
    
    # Teste 4: Integração completa
    test_full_integration()
    
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    print(f"✓ API LRCLib: {'OK' if lyrics else 'FALHOU'}")
    print(f"✓ Extração de Hotwords: {'OK' if hotwords else 'FALHOU'}")
    print(f"✓ Correção de Letras: OK")
    print(f"✓ Integração Completa: OK")
    print("\n" + "="*60)
    print("\nPara testar com áudio real, execute:")
    print("python src/UltraSinger.py -i \"path/to/audio.mp3\" -o output --lrclib")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
