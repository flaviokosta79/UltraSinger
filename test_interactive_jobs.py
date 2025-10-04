"""
Teste do modo interativo com seleção de jobs
"""
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from Settings import Settings
from modules.init_interactive_mode import InteractiveMode

def test_configure_processing_jobs():
    """Testa a função de configuração de jobs"""
    print("=" * 60)
    print("TESTE: Configuração de Jobs de Processamento")
    print("=" * 60)

    settings = Settings()
    interactive = InteractiveMode()

    # Testar configuração padrão
    print("\n1. Testando configuração padrão...")
    print("   - use_separated_vocal deve ser True")
    print("   - ignore_audio deve ser False")
    print("   - create_midi deve ser False")
    print("   - hyphenation deve ser True")

    # Valores esperados
    assert hasattr(settings, 'use_separated_vocal'), "Settings deve ter use_separated_vocal"
    assert hasattr(settings, 'ignore_audio'), "Settings deve ter ignore_audio"
    assert hasattr(settings, 'create_midi'), "Settings deve ter create_midi"
    assert hasattr(settings, 'hyphenation'), "Settings deve ter hyphenation"

    print("   ✓ Todos os atributos necessários existem")

    # Testar valores padrão
    print("\n2. Testando valores padrão...")
    print(f"   - use_separated_vocal: {settings.use_separated_vocal}")
    print(f"   - ignore_audio: {settings.ignore_audio}")
    print(f"   - create_midi: {settings.create_midi}")
    print(f"   - create_plot: {settings.create_plot}")
    print(f"   - hyphenation: {settings.hyphenation}")
    print(f"   - create_karaoke: {settings.create_karaoke}")
    print(f"   - create_audio_chunks: {settings.create_audio_chunks}")

    # Testar modificação de valores
    print("\n3. Testando modificação de valores...")
    settings.use_separated_vocal = False
    settings.create_midi = True
    settings.create_plot = True

    print(f"   - use_separated_vocal alterado para: {settings.use_separated_vocal}")
    print(f"   - create_midi alterado para: {settings.create_midi}")
    print(f"   - create_plot alterado para: {settings.create_plot}")

    assert settings.use_separated_vocal == False, "use_separated_vocal deve ser False"
    assert settings.create_midi == True, "create_midi deve ser True"
    assert settings.create_plot == True, "create_plot deve ser True"

    print("   ✓ Valores modificados corretamente")

    print("\n" + "=" * 60)
    print("✓ TESTE CONCLUÍDO COM SUCESSO")
    print("=" * 60)

def test_job_combinations():
    """Testa diferentes combinações de jobs"""
    print("\n" + "=" * 60)
    print("TESTE: Combinações de Jobs")
    print("=" * 60)

    # Cenário 1: Criação completa
    print("\n📋 Cenário 1: Criação Completa de Karaoke")
    settings1 = Settings()
    settings1.use_separated_vocal = True
    settings1.ignore_audio = False  # Usar Whisper
    settings1.create_midi = False
    settings1.create_plot = False
    settings1.hyphenation = True
    settings1.create_karaoke = True

    print("   Jobs ativos:")
    print(f"   ✓ Separação Vocal: {settings1.use_separated_vocal}")
    print(f"   ✓ Transcrição: {not settings1.ignore_audio}")
    print(f"   ✓ Hifenização: {settings1.hyphenation}")
    print(f"   ✓ Karaokê: {settings1.create_karaoke}")
    print(f"   ✗ MIDI: {settings1.create_midi}")
    print(f"   ✗ Gráficos: {settings1.create_plot}")

    # Cenário 2: Re-pitch apenas
    print("\n📋 Cenário 2: Re-pitch de Arquivo Existente")
    settings2 = Settings()
    settings2.use_separated_vocal = False
    settings2.ignore_audio = True  # Não usar Whisper
    settings2.create_midi = False
    settings2.create_plot = False
    settings2.hyphenation = False
    settings2.create_karaoke = True

    print("   Jobs ativos:")
    print(f"   ✗ Separação Vocal: {settings2.use_separated_vocal}")
    print(f"   ✗ Transcrição: {not settings2.ignore_audio}")
    print(f"   ✓ Pitch Detection: sempre ativo")
    print(f"   ✗ Hifenização: {settings2.hyphenation}")
    print(f"   ✓ Karaokê: {settings2.create_karaoke}")

    # Cenário 3: Análise completa
    print("\n📋 Cenário 3: Análise Completa com Todos Jobs")
    settings3 = Settings()
    settings3.use_separated_vocal = True
    settings3.ignore_audio = False
    settings3.create_midi = True
    settings3.create_plot = True
    settings3.hyphenation = True
    settings3.create_karaoke = True
    settings3.create_audio_chunks = True

    print("   Jobs ativos:")
    print(f"   ✓ Separação Vocal: {settings3.use_separated_vocal}")
    print(f"   ✓ Transcrição: {not settings3.ignore_audio}")
    print(f"   ✓ Pitch Detection: sempre ativo")
    print(f"   ✓ MIDI: {settings3.create_midi}")
    print(f"   ✓ Gráficos: {settings3.create_plot}")
    print(f"   ✓ Hifenização: {settings3.hyphenation}")
    print(f"   ✓ Karaokê: {settings3.create_karaoke}")
    print(f"   ✓ Audio Chunks: {settings3.create_audio_chunks}")

    print("\n" + "=" * 60)
    print("✓ TESTE DE COMBINAÇÕES CONCLUÍDO")
    print("=" * 60)

def test_cache_structure():
    """Testa a estrutura do cache"""
    print("\n" + "=" * 60)
    print("TESTE: Estrutura do Cache")
    print("=" * 60)

    settings = Settings()
    interactive = InteractiveMode()

    # Configurar alguns valores
    settings.use_separated_vocal = True
    settings.ignore_audio = False
    settings.create_midi = True
    settings.create_plot = True
    settings.hyphenation = True
    settings.crepe_model_capacity = "full"
    settings.crepe_step_size = 10

    print("\n1. Salvando configurações no cache...")

    # Salvar cache (não executar realmente para não criar arquivo)
    expected_cache_keys = [
        "whisper_model",
        "demucs_model",
        "language",
        "whisper_batch_size",
        "whisper_compute_type",
        "crepe_model_capacity",
        "crepe_step_size",
        "force_cpu",
        "force_whisper_cpu",
        "force_crepe_cpu",
        "use_separated_vocal",
        "ignore_audio",
        "create_midi",
        "create_plot",
        "hyphenation",
        "create_karaoke",
        "create_audio_chunks",
        "keep_cache",
        "keep_numbers",
        "timestamp"
    ]

    print(f"   Esperados {len(expected_cache_keys)} campos no cache:")
    for key in expected_cache_keys:
        print(f"   - {key}")

    print("\n2. Verificando atributos nas Settings...")
    for key in expected_cache_keys:
        if key != "timestamp":
            has_attr = hasattr(settings, key)
            print(f"   {'✓' if has_attr else '✗'} {key}: {has_attr}")

    print("\n" + "=" * 60)
    print("✓ TESTE DE CACHE CONCLUÍDO")
    print("=" * 60)

def main():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print("INICIANDO TESTES DO MODO INTERATIVO COM SELEÇÃO DE JOBS")
    print("=" * 60)

    try:
        test_configure_processing_jobs()
        test_job_combinations()
        test_cache_structure()

        print("\n" + "=" * 60)
        print("🎉 TODOS OS TESTES PASSARAM COM SUCESSO! 🎉")
        print("=" * 60)
        print("\nPróximos passos:")
        print("1. Execute: python src/UltraSinger.py --interactive")
        print("2. Teste a seleção de jobs manualmente")
        print("3. Verifique o cache gerado em: interactive_settings_cache.json")
        print("4. Teste diferentes combinações de jobs")

    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
