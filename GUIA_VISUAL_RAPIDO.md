# 🎬 Guia Visual Rápido - Seleção de Jobs

## 🚀 Início Rápido (30 segundos)

```bash
python src/UltraSinger.py --interactive
```

## 📸 Fluxo Visual

```
┌─────────────────────────────────────────────────────────────┐
│  🎵 UltraSinger Interactive Mode 🎵                         │
│  Transforme áudio em arquivos UltraStar com IA!            │
└─────────────────────────────────────────────────────────────┘

➡️  Caminho do arquivo: minha_musica.mp3
    ✓ Arquivo de áudio válido

➡️  Pasta de saída: output/
    ✓ Pasta de saída: E:\output

┌──────────────── Seleção de Jobs ─────────────────┐
│                                                   │
│  🎤 Separação Vocal    │ Separa vocais...    │ ✓ │
│  📝 Transcrição        │ Transcreve letras.. │ ✓ │
│  🎵 Detecção de Pitch  │ Detecta notas...   │ ✓ │
│  🎹 Geração de MIDI    │ Cria MIDI...       │ ○ │
│  📊 Gráficos           │ Visualizações...   │ ○ │
│  🎼 Partitura          │ Sheet music...     │ ○ │
│  ✂️ Hifenização        │ Divide sílabas...  │ ✓ │
│                                                   │
└───────────────────────────────────────────────────┘

➡️  Personalizar jobs de processamento? (y/N): N
    ✓ Usando configuração padrão de jobs

➡️  Escolha o modelo Whisper: (6) large-v2
    ✓ Modelo selecionado: large-v2

➡️  Escolha o modelo Demucs: (1) htdemucs
    ✓ Modelo selecionado: htdemucs

➡️  Configurar opções avançadas? (y/N): N

┌──────────── Resumo das Configurações ────────────┐
│                                                   │
│  📂 Arquivo   │ minha_musica.mp3                 │
│  📁 Pasta     │ output/                          │
│  🌐 Idioma    │ auto                             │
│  ⚡ GPU       │ Sim                              │
│                                                   │
└───────────────────────────────────────────────────┘

┌─────────── Jobs de Processamento ────────────────┐
│                                                   │
│  🎤 Separação Vocal    │ ✓ Ativo  │ htdemucs    │
│  📝 Transcrição        │ ✓ Ativo  │ large-v2    │
│  🎵 Pitch Detection    │ ✓ Ativo  │ full (10ms) │
│  🎹 MIDI               │ ○ Desativado │ -       │
│  📊 Gráficos           │ ○ Desativado │ -       │
│  ✂️ Hifenização        │ ✓ Ativo  │ -          │
│  🎤 Karaokê            │ ✓ Ativo  │ -          │
│                                                   │
└───────────────────────────────────────────────────┘

➡️  Continuar com essas configurações? (Y/n): Y

🚀 Iniciando processamento...

[████████████████████████] 100% - Concluído!
```

## 🎯 Decisões Rápidas

### ❓ Quando Usar Configuração Padrão?

**✅ SIM** se você quer:
- Qualidade máxima
- Processo automático
- Não sabe o que escolher

**Responda:** `N` para "Personalizar jobs?"

---

### ❓ Quando Personalizar Jobs?

**✅ SIM** se você:
- Já tem arquivo UltraStar.txt (re-pitch)
- Quer economizar tempo
- Não precisa de todos os outputs
- Sabe exatamente o que quer

**Responda:** `Y` para "Personalizar jobs?"

---

## 🎨 Combinações Populares

### 🥇 Opção 1: Qualidade Máxima (Padrão)

```
Personalizar jobs? N
```

**Jobs:**
- ✅ Separação Vocal
- ✅ Transcrição
- ✅ Pitch
- ✅ Hifenização
- ✅ Karaokê

**Tempo:** 5-10 min
**Para:** Primeira vez, qualidade premium

---

### 🥈 Opção 2: Rápido e Eficiente

```
Personalizar jobs? Y
  Separação Vocal? N
  Transcrição? Y
  Pitch? Y
  MIDI? N
  Gráficos? N
  Hifenização? Y
  Karaokê? Y
```

**Jobs:**
- ✅ Transcrição
- ✅ Pitch
- ✅ Hifenização
- ✅ Karaokê

**Tempo:** 3-5 min
**Para:** Processo rápido, áudio limpo

---

### 🥉 Opção 3: Re-pitch Apenas

```
Personalizar jobs? Y
  Separação Vocal? N
  Transcrição? N
  Pitch? Y
  Karaokê? Y
```

**Jobs:**
- ✅ Pitch
- ✅ Karaokê

**Tempo:** 1-2 min
**Para:** Corrigir arquivo existente

---

### 🏆 Opção 4: Análise Completa

```
Personalizar jobs? Y
  Todos? Y
  Partitura? Y
```

**Jobs:**
- ✅ Todos

**Tempo:** 15-20 min
**Para:** Análise profunda, estudo

---

## 🔍 Dicas Visuais

### ✅ Ícones de Status

| Ícone | Significado |
|-------|-------------|
| ✓ | Job ativo |
| ○ | Job desativado |
| ⚠ | Atenção/aviso |
| ✗ | Erro |

### 🎨 Cores

| Cor | Uso |
|-----|-----|
| [green] | Sucesso, ativo |
| [red] | Erro, desativado |
| [yellow] | Aviso |
| [cyan] | Informação |
| [dim] | Opcional desativado |

## ⚡ Atalhos Mentais

### Para Decidir Rapidamente:

1. **Tenho arquivo .txt?**
   - Sim → Desativar Transcrição
   - Não → Manter ativado

2. **Quero analisar?**
   - Sim → Ativar MIDI + Gráficos
   - Não → Desativar

3. **Primeiro uso?**
   - Sim → Usar padrão
   - Não → Personalizar

4. **Preciso de velocidade?**
   - Sim → Desativar Separação Vocal
   - Não → Manter ativado

5. **Tenho MuseScore?**
   - Sim → Ativar Partitura
   - Não → Desativar

## 📊 Comparação Visual

```
┌──────────────┬─────────┬─────────┬──────────┬──────────┐
│   Cenário    │  Tempo  │ Qualid. │ Arquivos │ Complexo │
├──────────────┼─────────┼─────────┼──────────┼──────────┤
│ Padrão       │ 5-10min │ ★★★★★   │ 3-5      │ ★☆☆      │
│ Rápido       │ 3-5min  │ ★★★★☆   │ 2-3      │ ★★☆      │
│ Re-pitch     │ 1-2min  │ ★★★☆☆   │ 1-2      │ ★☆☆      │
│ Completo     │15-20min │ ★★★★★   │ 8-12     │ ★★★★★    │
└──────────────┴─────────┴─────────┴──────────┴──────────┘
```

## 🎯 Regra de Ouro

> **"Não sabe o que fazer? Use o padrão!"**

A configuração padrão foi otimizada para:
- ✅ Melhor qualidade
- ✅ Maior compatibilidade
- ✅ Menos problemas
- ✅ Resultado consistente

## 📞 Precisa de Ajuda?

Durante o processo interativo, você verá:
- 📋 Descrições de cada job
- 💡 Dicas contextuais
- ⚠️ Avisos importantes
- ✓ Confirmações visuais

**Não tenha medo de experimentar!** O cache salvará suas escolhas.

---

**Dica Final:** Pressione `Ctrl+C` a qualquer momento para cancelar.
