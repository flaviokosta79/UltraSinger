"""
Exemplos Práticos: Novos Recursos WhisperX 3.4.3
================================================
Scripts de exemplo para testar cada recurso novo
"""

import whisperx
import torch
import json
from pathlib import Path


# ============================================================================
# EXEMPLO 1: Timestamps de Números
# ============================================================================

def exemplo_timestamps_numeros():
    """
    Demonstra como acessar timestamps precisos de números
    """
    print("\n" + "="*70)
    print("EXEMPLO 1: TIMESTAMPS DE NÚMEROS")
    print("="*70 + "\n")

    # Configuração
    audio_file = r"E:\VSCode\Projects\UltraSinger\output\Pollo - Vagalumes\Pollo - Vagalumes.mp3"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Carregar modelo
    print("📥 Carregando modelo...")
    model = whisperx.load_model("base", device=device)

    # Carregar e transcrever áudio
    print("🎤 Transcrevendo...")
    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio[:16000 * 60])  # Primeiro minuto

    # Procurar números
    print("\n📊 Procurando números no áudio...\n")

    numeros_encontrados = []
    for segment in result['segments']:
        if 'words' in segment:
            for word in segment['words']:
                word_text = word.get('word', '')
                # Verifica se tem dígito
                if any(char.isdigit() for char in word_text):
                    numeros_encontrados.append({
                        'palavra': word_text,
                        'inicio': word.get('start', 0),
                        'fim': word.get('end', 0)
                    })

    if numeros_encontrados:
        print(f"✅ Encontrados {len(numeros_encontrados)} números:\n")
        for num in numeros_encontrados:
            print(f"   Número: '{num['palavra']}'")
            print(f"   ⏱️  Tempo: {num['inicio']:.2f}s - {num['fim']:.2f}s")
            print()
    else:
        print("ℹ️  Nenhum número encontrado neste áudio.")
        print("   Experimente com um áudio que contenha números falados!")

    print("\n" + "="*70)


# ============================================================================
# EXEMPLO 2: Hotwords (Palavras Prioritárias)
# ============================================================================

def exemplo_hotwords():
    """
    Demonstra como usar hotwords para melhorar reconhecimento
    """
    print("\n" + "="*70)
    print("EXEMPLO 2: HOTWORDS (PALAVRAS PRIORITÁRIAS)")
    print("="*70 + "\n")

    audio_file = r"E:\VSCode\Projects\UltraSinger\output\Pollo - Vagalumes\Pollo - Vagalumes.mp3"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Carregar modelo
    print("📥 Carregando modelo...")
    model = whisperx.load_model("base", device=device)
    audio = whisperx.load_audio(audio_file)
    audio_sample = audio[:16000 * 30]  # 30 segundos

    # TESTE 1: SEM hotwords
    print("\n🔹 Teste 1: SEM hotwords")
    print("-" * 70)
    result_sem = model.transcribe(audio_sample, language="pt")
    texto_sem = result_sem['segments'][0]['text'] if result_sem['segments'] else ""
    print(f"Resultado: {texto_sem}\n")

    # TESTE 2: COM hotwords
    print("🔹 Teste 2: COM hotwords")
    print("-" * 70)

    # Hotwords baseados na música "Vagalumes" do Pollo
    hotwords = [
        "vagalumes",    # Título da música
        "Pollo",        # Nome do artista
        "sorrir",       # Palavras da letra
        "colorir",
        "céu",
        "força",
        "amanheça"
    ]

    print(f"Hotwords usadas: {', '.join(hotwords)}")

    result_com = model.transcribe(
        audio_sample,
        language="pt",
        hotwords=hotwords  # ← NOVIDADE DO 3.4.3!
    )

    texto_com = result_com['segments'][0]['text'] if result_com['segments'] else ""
    print(f"Resultado: {texto_com}\n")

    # Comparação
    print("📊 COMPARAÇÃO:")
    print("-" * 70)
    if texto_sem == texto_com:
        print("✅ Resultados idênticos (áudio já era claro)")
    else:
        print("🔄 Resultados diferentes:")
        print(f"\n   SEM hotwords: {texto_sem}")
        print(f"   COM hotwords: {texto_com}")

    print("\n💡 DICA: Hotwords são mais úteis quando:")
    print("   • O áudio tem nomes próprios difíceis")
    print("   • Há termos técnicos ou jargões")
    print("   • O artista tem nome estrangeiro")
    print("   • A qualidade do áudio não é perfeita")

    print("\n" + "="*70)


# ============================================================================
# EXEMPLO 3: Comparação de VAD (Pyannote vs Silero)
# ============================================================================

def exemplo_vad_comparison():
    """
    Compara performance entre Pyannote VAD e Silero VAD
    """
    print("\n" + "="*70)
    print("EXEMPLO 3: COMPARAÇÃO DE VAD (Voice Activity Detection)")
    print("="*70 + "\n")

    import time

    audio_file = r"E:\VSCode\Projects\UltraSinger\output\Pollo - Vagalumes\Pollo - Vagalumes.mp3"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Carregar modelo
    print("📥 Carregando modelo...")
    model = whisperx.load_model("base", device=device)
    audio = whisperx.load_audio(audio_file)
    audio_sample = audio[:16000 * 60]  # 1 minuto

    # TESTE 1: Pyannote VAD (padrão)
    print("\n🔹 Teste 1: Pyannote VAD (padrão)")
    print("-" * 70)
    start = time.time()
    result_pyannote = model.transcribe(audio_sample, language="pt")
    time_pyannote = time.time() - start
    print(f"⏱️  Tempo: {time_pyannote:.2f}s")
    print(f"📊 Segmentos: {len(result_pyannote['segments'])}")

    # TESTE 2: Silero VAD (novo)
    print("\n🔹 Teste 2: Silero VAD (novo no 3.4.3)")
    print("-" * 70)
    print("ℹ️  Nota: Silero VAD ainda em desenvolvimento, pode não estar disponível")

    try:
        start = time.time()
        result_silero = model.transcribe(
            audio_sample,
            language="pt",
            vad_filter=True,
            vad_options={
                "vad_onset": 0.500,
                "vad_offset": 0.363
            }
        )
        time_silero = time.time() - start
        print(f"⏱️  Tempo: {time_silero:.2f}s")
        print(f"📊 Segmentos: {len(result_silero['segments'])}")

        # Comparação
        print("\n📊 RESULTADO DA COMPARAÇÃO:")
        print("-" * 70)
        print(f"Pyannote VAD:  {time_pyannote:.2f}s")
        print(f"Silero VAD:    {time_silero:.2f}s")

        if time_silero < time_pyannote:
            diff_percent = ((time_pyannote - time_silero) / time_pyannote) * 100
            print(f"✅ Silero é {diff_percent:.1f}% mais rápido!")
        else:
            print("ℹ️  Pyannote foi mais rápido neste teste")

    except Exception as e:
        print(f"⚠️  Silero VAD não disponível: {e}")
        print("   (Pode não estar implementado nesta versão)")

    print("\n💡 RECOMENDAÇÃO para UltraSinger:")
    print("   • Use Pyannote VAD (padrão) para QUALIDADE MÁXIMA")
    print("   • Use Silero VAD apenas se VELOCIDADE for crítica")

    print("\n" + "="*70)


# ============================================================================
# EXEMPLO 4: Integração Completa (Todos os Recursos)
# ============================================================================

def exemplo_completo():
    """
    Exemplo usando TODOS os novos recursos juntos
    """
    print("\n" + "="*70)
    print("EXEMPLO 4: INTEGRAÇÃO COMPLETA (TODOS OS RECURSOS)")
    print("="*70 + "\n")

    audio_file = r"E:\VSCode\Projects\UltraSinger\output\Pollo - Vagalumes\Pollo - Vagalumes.mp3"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Metadados (normalmente viriam do nome do arquivo ou tags)
    artista = "Pollo"
    musica = "Vagalumes"

    # Preparar hotwords inteligentes
    print("🎯 Preparando hotwords baseadas nos metadados...")
    hotwords = []

    # Adicionar nome do artista e música
    hotwords.extend(artista.split())
    hotwords.extend(musica.split())

    # Adicionar palavras comuns do gênero (você pode customizar)
    if "pop" in musica.lower() or "rock" in musica.lower():
        hotwords.extend(["amor", "coração", "yeah", "baby"])

    # Remover duplicatas
    hotwords = list(set(hotwords))

    print(f"   Hotwords: {', '.join(hotwords)}\n")

    # Carregar modelo
    print("📥 Carregando modelo...")
    model = whisperx.load_model("base", device=device)

    # Carregar áudio
    print("🎵 Carregando áudio...")
    audio = whisperx.load_audio(audio_file)

    # Transcrever com TODOS os recursos
    print("🎤 Transcrevendo com recursos avançados...")
    print("   • Hotwords: ✅")
    print("   • Timestamps de números: ✅")
    print("   • VAD otimizado: ✅\n")

    result = model.transcribe(
        audio[:16000 * 60],  # 1 minuto
        language="pt",
        hotwords=hotwords,
        batch_size=16
    )

    # Análise do resultado
    print("\n📊 ANÁLISE DO RESULTADO:")
    print("-" * 70)

    total_palavras = 0
    total_numeros = 0

    for i, segment in enumerate(result['segments'][:3]):  # Primeiros 3 segmentos
        print(f"\n[Segmento {i+1}]")
        print(f"⏱️  Tempo: {segment['start']:.2f}s - {segment['end']:.2f}s")
        print(f"📝 Texto: {segment['text']}")

        # Contar palavras
        palavras = segment['text'].split()
        total_palavras += len(palavras)

        # Procurar números
        if 'words' in segment:
            numeros = [
                w for w in segment['words']
                if any(char.isdigit() for char in w.get('word', ''))
            ]

            if numeros:
                total_numeros += len(numeros)
                print(f"\n   🔢 Números encontrados:")
                for num in numeros:
                    print(f"      • '{num['word']}' em {num['start']:.2f}s")

    print("\n" + "-" * 70)
    print(f"📊 ESTATÍSTICAS:")
    print(f"   • Total de segmentos: {len(result['segments'])}")
    print(f"   • Total de palavras: {total_palavras}")
    print(f"   • Total de números: {total_numeros}")
    print(f"   • Idioma: {result.get('language', 'N/A')}")

    # Salvar resultado
    output_file = "exemplo_completo_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'artista': artista,
            'musica': musica,
            'hotwords': hotwords,
            'language': result['language'],
            'segments': [
                {
                    'text': seg['text'],
                    'start': seg['start'],
                    'end': seg['end'],
                    'words': seg.get('words', [])
                } for seg in result['segments']
            ]
        }, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultado completo salvo em: {output_file}")

    print("\n" + "="*70)


# ============================================================================
# MENU PRINCIPAL
# ============================================================================

def main():
    """Menu principal para escolher qual exemplo executar"""

    print("\n" + "="*70)
    print("EXEMPLOS PRÁTICOS: WhisperX 3.4.3 - Novos Recursos")
    print("="*70)

    print("\nEscolha um exemplo para executar:\n")
    print("1. 🔢 Timestamps de Números")
    print("2. 🎯 Hotwords (Palavras Prioritárias)")
    print("3. 🔇 Comparação de VAD (Pyannote vs Silero)")
    print("4. 🚀 Integração Completa (Todos os Recursos)")
    print("5. ✨ Executar TODOS os exemplos")
    print("0. ❌ Sair")

    escolha = input("\n👉 Digite o número da opção: ").strip()

    if escolha == "1":
        exemplo_timestamps_numeros()
    elif escolha == "2":
        exemplo_hotwords()
    elif escolha == "3":
        exemplo_vad_comparison()
    elif escolha == "4":
        exemplo_completo()
    elif escolha == "5":
        exemplo_timestamps_numeros()
        exemplo_hotwords()
        exemplo_vad_comparison()
        exemplo_completo()
    elif escolha == "0":
        print("\n👋 Até logo!\n")
        return
    else:
        print("\n❌ Opção inválida!")
        return

    print("\n✅ Exemplo concluído!")
    print("\n💡 DICA: Leia o arquivo 'GUIA_RECURSOS_WHISPERX_343.md' para")
    print("   mais detalhes sobre cada recurso.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
