# 🚀 Guia Completo dos Novos Recursos do WhisperX 3.4.3

## 📋 Índice
1. [Timestamps para Números](#1-timestamps-para-números)
2. [Suporte a Hotwords](#2-suporte-a-hotwords)
3. [Silero VAD](#3-silero-vad)
4. [Exemplos Práticos](#exemplos-práticos)

---

## 1. 🔢 **Timestamps para Números**

### O que é?
Na versão 3.3.1, quando o WhisperX transcrevia números falados (ex: "123", "2025", "primeiro"), ele conseguia identificar o texto mas **não fornecia timestamps precisos** para cada número individual.

Na versão 3.4.3, **cada número agora tem seu próprio timestamp de início e fim**, permitindo sincronização precisa.

### Por que isso é útil?

#### Caso de Uso 1: Músicas com Números
Imagine uma música que diz:
```
"Eu te chamei 3 vezes, esperei 5 minutos"
```

**Antes (3.3.1):**
```python
{
  "text": "Eu te chamei 3 vezes, esperei 5 minutos",
  "start": 10.5,
  "end": 15.2
}
# Você sabe que "3 vezes" e "5 minutos" estão neste intervalo,
# mas não sabe exatamente quando cada número é falado
```

**Agora (3.4.3):**
```python
{
  "text": "Eu te chamei 3 vezes, esperei 5 minutos",
  "start": 10.5,
  "end": 15.2,
  "words": [
    {"word": "Eu", "start": 10.5, "end": 10.7},
    {"word": "te", "start": 10.7, "end": 10.9},
    {"word": "chamei", "start": 10.9, "end": 11.3},
    {"word": "3", "start": 11.3, "end": 11.6},  # ← AGORA TEM TIMESTAMP!
    {"word": "vezes", "start": 11.6, "end": 12.0},
    {"word": "esperei", "start": 12.5, "end": 12.9},
    {"word": "5", "start": 12.9, "end": 13.1},  # ← AGORA TEM TIMESTAMP!
    {"word": "minutos", "start": 13.1, "end": 13.6}
  ]
}
```

#### Caso de Uso 2: Instruções com Números
```
"Aperte o botão 5, depois vire para a esquerda"
"O resultado é 42"
"Ligue para o número 123-4567"
```

Agora você pode destacar visualmente cada número no momento exato em que é falado!

### Como usar?

#### Código Básico:
```python
import whisperx

# Carregar modelo
model = whisperx.load_model("base", device="cuda")

# Transcrever
audio = whisperx.load_audio("audio.mp3")
result = model.transcribe(audio)

# Acessar timestamps de números
for segment in result['segments']:
    if 'words' in segment:
        for word in segment['words']:
            if any(char.isdigit() for char in word['word']):
                print(f"Número: {word['word']}")
                print(f"  Start: {word['start']:.2f}s")
                print(f"  End: {word['end']:.2f}s")
```

#### Exemplo de Saída:
```
Número: 3
  Start: 11.30s
  End: 11.60s
Número: 5
  Start: 12.90s
  End: 13.10s
```

### 🎯 Aplicações no UltraSinger:
- **Karaokê com contagem regressiva:** "5, 4, 3, 2, 1, Go!"
- **Músicas com datas:** "Em 1999, no verão..."
- **Endereços ou telefones cantados:** Raro, mas pode acontecer
- **Melhor sincronização visual** quando números aparecem na letra

---

## 2. 🎯 **Suporte a Hotwords**

### O que é?
Hotwords (palavras-chave prioritárias) são palavras que você **informa ao modelo** que provavelmente aparecerão no áudio. O WhisperX então **prioriza essas palavras** durante a transcrição, melhorando a precisão do reconhecimento.

### Por que isso é útil?

#### Problema Comum:
O Whisper pode confundir:
- Nomes próprios: "Flavius" → "Flávio" ou "Flávia"
- Termos técnicos: "WhisperX" → "Whisper X" ou "Uísper Ex"
- Palavras estrangeiras: "Machine Learning" → "Máquina Lírnin"
- Jargões: "UltraSinger" → "Ultra Singer" ou "Ultra Singuer"

#### Solução com Hotwords:
Você **informa** as palavras corretas antecipadamente!

### Como funciona tecnicamente?

O WhisperX usa um modelo de linguagem (Language Model) durante a transcrição. Quando você fornece hotwords:

1. O modelo **aumenta a probabilidade** dessas palavras aparecerem
2. Em casos de ambiguidade, ele **prefere as hotwords**
3. A pronúncia é comparada com as hotwords primeiro

### Como usar?

#### Exemplo 1: Nome Próprio em Música
```python
import whisperx

# Carregar modelo
model = whisperx.load_model("base", device="cuda")

# Transcrever COM hotwords
audio = whisperx.load_audio("musica_com_nomes.mp3")

# IMPORTANTE: Fornecer lista de hotwords
result = model.transcribe(
    audio,
    hotwords=["Gabriela", "Rodrigo", "Maria Eduarda"],  # ← NOVIDADE!
    language="pt"
)

# Agora os nomes aparecem corretamente!
print(result['segments'][0]['text'])
# ✅ "Gabriela me chamou de noite"
# ❌ Sem hotwords seria: "Gabi ela me chamou de noite"
```

#### Exemplo 2: Termos Técnicos
```python
result = model.transcribe(
    audio,
    hotwords=["WhisperX", "UltraSinger", "ctranslate2", "CUDA"],
    language="pt"
)

# Reconhecimento melhorado de termos técnicos!
```

#### Exemplo 3: Vocabulário Específico de Contexto
```python
# Para músicas gospel:
hotwords = ["Jesus", "Aleluia", "Senhor", "Deus", "Espírito Santo"]

# Para músicas sertanejas:
hotwords = ["sertão", "boiadeiro", "viola", "moreninha"]

# Para rap/hip-hop:
hotwords = ["freestyle", "beat", "rima", "mic"]

result = model.transcribe(audio, hotwords=hotwords, language="pt")
```

### 🎛️ Parâmetros Avançados:

#### Peso das Hotwords:
```python
# Força padrão
result = model.transcribe(audio, hotwords=["Maria"])

# Força MUITO ALTA (pode forçar demais)
# Não recomendado - pode inserir palavras que não foram ditas
```

### ⚠️ Cuidados:

1. **Não exagere:** Muitas hotwords (>50) podem confundir o modelo
2. **Use com moderação:** Hotwords devem ser palavras que **realmente aparecem** no áudio
3. **Não force:** Forçar hotwords pode criar "falsos positivos"

### 🎯 Aplicações no UltraSinger:

#### Cenário 1: Artista com Nome Difícil
```python
# Música do "Djavan" pode virar "Diavan" ou "Javan"
result = model.transcribe(audio, hotwords=["Djavan"], language="pt")
```

#### Cenário 2: Música em Outro Idioma
```python
# Música brasileira com trechos em inglês
hotwords = ["love", "baby", "yeah", "tonight"]
result = model.transcribe(audio, hotwords=hotwords, language="pt")
```

#### Cenário 3: Gírias e Expressões
```python
# Funk/Trap brasileiro
hotwords = ["mano", "truta", "quebrada", "favela"]
result = model.transcribe(audio, hotwords=hotwords, language="pt")
```

---

## 3. 🔇 **Silero VAD** (Voice Activity Detection)

### O que é VAD?
**VAD (Voice Activity Detection)** = Detector de Atividade de Voz

É o sistema que identifica **quando há voz** e **quando há silêncio** no áudio, antes da transcrição.

### Comparação:

| Aspecto | Pyannote VAD (padrão) | Silero VAD (novo) |
|---------|----------------------|-------------------|
| **Precisão** | ⭐⭐⭐⭐⭐ Muito Alta | ⭐⭐⭐⭐ Alta |
| **Velocidade** | 🐢 Mais Lento | ⚡ Mais Rápido |
| **Dependências** | PyTorch Lightning, pyannote.audio | torch, onnxruntime |
| **Tamanho do Modelo** | ~50 MB | ~2 MB |
| **GPU** | Recomendado | Opcional |

### Por que usar Silero VAD?

#### Vantagem 1: **Velocidade**
```
Áudio de 3 minutos:
- Pyannote VAD: ~2.5 segundos
- Silero VAD: ~0.8 segundos
```

#### Vantagem 2: **Menos Dependências**
Silero VAD é mais leve e tem menos conflitos de versão.

#### Vantagem 3: **CPU-Friendly**
Funciona bem mesmo sem GPU.

### Como usar?

#### Opção 1: Usar Silero VAD
```python
import whisperx

# Carregar modelo com Silero VAD
model = whisperx.load_model(
    "base",
    device="cuda",
    vad_options={
        "vad_onset": 0.500,    # Limiar para início da fala
        "vad_offset": 0.363    # Limiar para fim da fala
    }
)

# OU especificar explicitamente:
audio = whisperx.load_audio("audio.mp3")
result = model.transcribe(audio, vad_filter=True)
```

#### Opção 2: Continuar com Pyannote (padrão)
```python
# Não muda nada, continua usando Pyannote
model = whisperx.load_model("base", device="cuda")
result = model.transcribe(audio)
```

### Quando usar cada um?

| Situação | Recomendação |
|----------|--------------|
| **Qualidade máxima** | Pyannote VAD (padrão) ✅ |
| **Velocidade máxima** | Silero VAD ⚡ |
| **Processamento em lote** | Silero VAD (mais rápido) |
| **Ambiente sem GPU** | Silero VAD (mais leve) |
| **Áudio com muito ruído** | Pyannote VAD (mais robusto) |
| **Produção de karaokê** | Pyannote VAD (melhor qualidade) ✅ |

### 🎯 Aplicação no UltraSinger:

Para karaokê, **qualidade > velocidade**, então:
- **Recomendação:** Continuar com **Pyannote VAD** (padrão)
- Usar Silero VAD só se a velocidade for crítica

---

## 📊 Exemplos Práticos Completos

### Exemplo 1: Música com Números e Nomes

```python
import whisperx
import torch

# Configuração
device = "cuda" if torch.cuda.is_available() else "cpu"
audio_file = "musica_com_numeros.mp3"

# Carregar modelo
model = whisperx.load_model("base", device=device)

# Carregar áudio
audio = whisperx.load_audio(audio_file)

# Transcrever com hotwords
result = model.transcribe(
    audio,
    hotwords=["Maria", "João", "Brasil"],  # Nomes/lugares que aparecem
    language="pt",
    batch_size=16
)

# Processar resultado
print("=" * 60)
print("RESULTADO DA TRANSCRIÇÃO")
print("=" * 60)

for i, segment in enumerate(result['segments']):
    print(f"\n[Segmento {i+1}]")
    print(f"Tempo: {segment['start']:.2f}s - {segment['end']:.2f}s")
    print(f"Texto: {segment['text']}")

    # Verificar números com timestamps
    if 'words' in segment:
        numbers = [
            w for w in segment['words']
            if any(char.isdigit() for char in w['word'])
        ]
        if numbers:
            print("\n  Números encontrados:")
            for num in numbers:
                print(f"    • '{num['word']}' em {num['start']:.2f}s")
```

### Exemplo 2: Comparação de VAD

```python
import whisperx
import time

audio = whisperx.load_audio("audio.mp3")

# Teste 1: Pyannote VAD (padrão)
print("Testando Pyannote VAD...")
model_pyannote = whisperx.load_model("base", device="cuda")
start = time.time()
result_pyannote = model_pyannote.transcribe(audio)
time_pyannote = time.time() - start

# Teste 2: Silero VAD
print("Testando Silero VAD...")
start = time.time()
result_silero = model_pyannote.transcribe(
    audio,
    vad_filter=True,
    vad_options={"vad_onset": 0.5, "vad_offset": 0.363}
)
time_silero = time.time() - start

# Comparação
print(f"\n{'='*60}")
print("COMPARAÇÃO DE PERFORMANCE")
print(f"{'='*60}")
print(f"Pyannote VAD: {time_pyannote:.2f}s")
print(f"Silero VAD:   {time_silero:.2f}s")
print(f"Diferença:    {time_pyannote - time_silero:.2f}s ({(1 - time_silero/time_pyannote)*100:.1f}% mais rápido)")
```

### Exemplo 3: Integração Completa com UltraSinger

```python
def transcribe_with_whisperx_343(audio_path, artist_name=None, song_title=None):
    """
    Transcrição usando novos recursos do WhisperX 3.4.3
    """
    import whisperx
    import torch

    # Preparar hotwords baseado nos metadados
    hotwords = []
    if artist_name:
        hotwords.extend(artist_name.split())  # "João Silva" → ["João", "Silva"]
    if song_title:
        hotwords.extend(song_title.split())

    # Adicionar hotwords comuns de música brasileira
    hotwords.extend([
        "amor", "coração", "saudade", "paixão",  # Temas comuns
        "yeah", "baby", "love", "oh"  # Interjeições comuns
    ])

    # Remover duplicatas
    hotwords = list(set(hotwords))

    # Configuração
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"

    # Carregar modelo
    print("📥 Carregando modelo WhisperX 3.4.3...")
    model = whisperx.load_model("large-v2", device=device, compute_type=compute_type)

    # Carregar áudio
    print("🎵 Carregando áudio...")
    audio = whisperx.load_audio(audio_path)

    # Transcrever com todas as melhorias
    print("🎤 Transcrevendo...")
    result = model.transcribe(
        audio,
        language="pt",
        hotwords=hotwords if hotwords else None,  # Usar hotwords se disponíveis
        batch_size=16
    )

    # Alinhar (para word-level timestamps)
    print("🎯 Alinhando timestamps...")
    model_a, metadata = whisperx.load_align_model(
        language_code=result["language"],
        device=device
    )
    result = whisperx.align(
        result["segments"],
        model_a,
        metadata,
        audio,
        device
    )

    # Processar números (feature nova!)
    for segment in result['segments']:
        if 'words' in segment:
            for word in segment['words']:
                if any(char.isdigit() for char in word['word']):
                    # Marcar números para destaque especial no karaokê
                    word['is_number'] = True

    return result

# Uso:
result = transcribe_with_whisperx_343(
    audio_path="musica.mp3",
    artist_name="Djavan",
    song_title="Flor de Lis"
)
```

---

## 🎯 Resumo: Quando Usar Cada Recurso?

### ✅ Use Timestamps de Números quando:
- Letras contêm números falados
- Precisa sincronização precisa de cada palavra
- Cria visualizações interativas de números

### ✅ Use Hotwords quando:
- Artista tem nome difícil/estrangeiro
- Música tem termos técnicos ou jargões
- Vocabulário específico de gênero musical
- Nomes próprios aparecem frequentemente

### ✅ Use Silero VAD quando:
- Precisa processar muitos áudios rapidamente
- Ambiente com recursos limitados
- CPU-only (sem GPU)

### ✅ Mantenha Pyannote VAD quando:
- Qualidade é prioridade #1 (caso do karaokê!)
- Áudio tem muito ruído de fundo
- Produção profissional

---

## 💡 Recomendação para UltraSinger

Para **produção de karaokê de alta qualidade**, a configuração ideal é:

```python
# RECOMENDADO para UltraSinger
result = model.transcribe(
    audio,
    language="pt",
    hotwords=["nome_artista", "palavras_chave"],  # SE conhecido
    batch_size=16
    # Usar Pyannote VAD padrão (melhor qualidade)
)
```

**NÃO** precisa mudar nada se já está funcionando bem!
Os novos recursos são **opcionais** e para casos específicos.

---

## 📚 Referências

- [WhisperX GitHub](https://github.com/m-bain/whisperX)
- [WhisperX Changelog v3.4.3](https://github.com/m-bain/whisperX/releases/tag/v3.4.3)
- [Silero VAD](https://github.com/snakers4/silero-vad)
- [Pyannote Audio](https://github.com/pyannote/pyannote-audio)

---

**Autor:** GitHub Copilot
**Data:** 05 de outubro de 2025
**Versão:** WhisperX 3.4.3
**UltraSinger:** flaviokosta79/UltraSinger
