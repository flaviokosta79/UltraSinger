# DESCOBERTA CRÍTICA - ANÁLISE FINAL HOTWORDS

**Data**: 5 de outubro de 2025
**Música**: Pollo - Vagalumes
**Problema**: "Janelle Monáe" transcrito como "janela e monê" aos ~22 segundos

---

## 🎯 DESCOBERTA CRUCIAL

A música contém **AMBAS** as palavras em momentos diferentes:

### ✅ Linha 41 (~22 segundos):
```
"Eu e você ao som de Janelle Monáe"
```
**Transcrição WhisperX:** "janela e monê" ❌ **ERRO CONFIRMADO**

### ✅ Linha 60 (~140 segundos):
```
"Abro a janela pra que você possa ver"
```
**Transcrição WhisperX:** "Abra a janela..." ✅ **CORRETO** (pequena variação "Abro"→"Abra")

---

## 📊 TESTES REALIZADOS

### 1. Modelo Base + Hotwords (onset=0.5 padrão)
- **Resultado**: 6 segmentos, VAD agressivo
- **Erro**: "Janelle Monáe" não transcrito (seção cortada pelo VAD)

### 2. Modelo Large-v3 + Hotwords (onset=0.5 padrão)
- **Resultado**: 6 segmentos, mesmo problema
- **Erro**: Timestamp 22s dentro do segmento 0, mas "Janelle Monáe" ausente

### 3. Modelo Large-v3 + Hotwords + VAD Permissivo (onset=0.3)
- **Resultado**: 6 segmentos, erro PERSISTE
- **Segmento 5 (~140s):** "Abra a janela..." ✅ CORRETO
- **Segmento 0 (~12-31s contém 22s):** Não menciona "Janelle" nem "janela" ❌

---

## 🔍 ANÁLISE DO ERRO

### Contexto aos 22 segundos (output_test_hybrid):
```
: 2179  e
: 2181  você
: 2190  é
: 2191  o
: 2195  som
: 2199  de
: 2204  janela    ← ERRO!
: 2216  e
: 2217  monê      ← ERRO!
: 2231  Vem
```

**Esperado:** "Eu e você ao som de **Janelle Monáe**"
**Obtido:** "Eu e você ao som de **janela e monê**"

---

## ✅ CONCLUSÕES

### O QUE FUNCIONOU:
1. ✅ WhisperX 3.4.3 instalado corretamente (PR #1073)
2. ✅ Hotwords implementado via `asr_options`
3. ✅ Método correto confirmado
4. ✅ Modelo large-v3 testado
5. ✅ VAD ajustado (onset=0.3)
6. ✅ Transcrição de "janela" (~140s) CORRETA

### O QUE NÃO FUNCIONOU:
1. ❌ Hotwords não corrigiram "Janelle Monáe" aos 22s
2. ❌ Mesmo com todas configurações perfeitas, erro persiste
3. ❌ VAD permissivo não melhorou resultado

---

## 🎯 CAUSA RAIZ IDENTIFICADA

**Hipótese Final:** Hotwords funcionam melhor com FALA (speech) clara que com MÚSICA.

**Razões:**
1. **Música tem melodia/ritmo** que distorce a pronúncia
2. **Contexto fonético** similar: "janela" e "Janelle" soam parecidos em português brasileiro
3. **Modelo treinado em fala** não em música
4. **Nome próprio estrangeiro** ("Janelle Monáe") vs palavra comum portuguesa ("janela")

---

## 💡 ESTRATÉGIAS DE CORREÇÃO

### Opção A: Pós-processamento Inteligente ⭐ RECOMENDADO
**Implementar substituição com contexto:**
```python
# Detectar padrão: "som de janela e monê"
# Substituir por: "som de Janelle Monáe"

patterns = [
    (r'som de janela e monê', 'som de Janelle Monáe'),
    (r'som de janela e mone', 'som de Janelle Monáe'),
    (r'ao som de janela', 'ao som de Janelle Monáe'),
]
```

**Vantagens:**
- ✅ Resolve o problema específico
- ✅ Não depende de hotwords funcionarem
- ✅ Pode ser expandido para outros casos
- ✅ Baseado em análise da letra oficial

**Desvantagens:**
- ⚠️ Específico para cada música
- ⚠️ Requer conhecimento da letra oficial

### Opção B: Initial Prompt Mais Forte
**Testar frases completas:**
```python
asr_options = {
    "initial_prompt": "Esta é uma música brasileira que menciona Janelle Monáe, a cantora americana. A letra diz: Eu e você ao som de Janelle Monáe.",
    "hotwords": "Janelle Monáe Vagalumes Pollo"
}
```

**Vantagens:**
- ✅ Usa recursos nativos do Whisper
- ✅ Contextualiza o modelo

**Desvantagens:**
- ❌ Já testamos e não funcionou efetivamente
- ⚠️ Pode influenciar negativamente outras partes

### Opção C: Modelo Fine-tuned (longo prazo)
**Treinar modelo específico para música brasileira**

**Vantagens:**
- ✅ Solução definitiva
- ✅ Funciona para todas as músicas

**Desvantagens:**
- ❌ Requer dataset grande
- ❌ Processo demorado e custoso
- ❌ Fora do escopo atual

### Opção D: Aceitar Limitação
**Documentar que hotwords têm limitações com música**

**Vantagens:**
- ✅ Honesto com usuários
- ✅ Sem trabalho adicional

**Desvantagens:**
- ❌ Não resolve o problema
- ❌ Deixa usuários insatisfeitos

---

## 📋 RECOMENDAÇÃO FINAL

**Implementar OPÇÃO A (Pós-processamento) com as seguintes características:**

### 1. Sistema de Correção Baseado em Contexto
```python
class LyricCorrector:
    def __init__(self, official_lyrics: str, hotwords: List[str]):
        self.lyrics = official_lyrics
        self.hotwords = hotwords
        self.corrections = self._build_correction_patterns()

    def _build_correction_patterns(self):
        """
        Criar padrões de correção baseados em:
        1. Hotwords da letra oficial
        2. Palavras foneticamente similares
        3. Contexto (palavras ao redor)
        """
        patterns = []
        for hotword in self.hotwords:
            # Detectar variações fonéticas
            similar = self._get_phonetic_variations(hotword)
            patterns.append((similar, hotword))
        return patterns

    def correct_transcription(self, text: str) -> str:
        """
        Aplicar correções baseadas em contexto
        """
        for pattern, correction in self.corrections:
            text = re.sub(pattern, correction, text, flags=re.IGNORECASE)
        return text
```

### 2. Integração no lrclib_integration.py
- Aplicar correções APÓS transcrição
- Usar letra oficial do LRCLib como referência
- Log de correções aplicadas para transparência

### 3. Configuração
- Opcional (usuário pode desabilitar)
- Ajustável (usuário pode adicionar padrões)
- Documentado (explicar limitações do Whisper com música)

---

## 🎬 PRÓXIMOS PASSOS

1. ✅ Confirmar estratégia com usuário
2. Implementar LyricCorrector no lrclib_integration.py
3. Adicionar correções baseadas em contexto
4. Testar com Vagalumes.mp3
5. Documentar processo e limitações
6. Atualizar README com explicações

---

**Status**: ⏳ Aguardando decisão do usuário sobre estratégia de correção
