# Modo Interativo com Seleção de Jobs - UltraSinger

## 📋 Visão Geral

O modo interativo do UltraSinger agora permite que você escolha exatamente quais jobs de processamento deseja executar, oferecendo controle granular sobre o pipeline de criação de karaoke.

## 🚀 Como Usar

### Comando Básico

```bash
python src/UltraSinger.py --interactive
```

## 🎯 Jobs Disponíveis

O modo interativo apresenta os seguintes jobs que podem ser ativados/desativados:

### 1. 🎤 **Separação Vocal (Demucs)**
- **Descrição**: Separa vocais do instrumental da música
- **Padrão**: Ativo
- **Modelos**: htdemucs, htdemucs_ft, htdemucs_6s, mdx, mdx_extra
- **Quando desativar**: Se você já tem vocais separados ou quer processar áudio completo

### 2. 📝 **Transcrição (Whisper)**
- **Descrição**: Transcreve automaticamente as letras da música
- **Padrão**: Ativo
- **Modelos**: tiny, base, small, medium, large-v2, large-v3
- **Quando desativar**: Se você já tem um arquivo UltraStar.txt existente para re-pitch

### 3. 🎵 **Detecção de Pitch (Crepe)**
- **Descrição**: Detecta as notas musicais cantadas
- **Padrão**: Ativo
- **Modelos**: tiny, small, medium, large, full
- **Configurações**: Step size (10ms padrão - menor = mais preciso)
- **Quando desativar**: Raramente - essencial para qualidade

### 4. 🎹 **Geração de MIDI**
- **Descrição**: Cria arquivo MIDI com as notas detectadas
- **Padrão**: Desativado
- **Quando ativar**: Se você quer editar as notas em um DAW

### 5. 📊 **Geração de Gráficos**
- **Descrição**: Cria visualizações do pitch e timing
- **Padrão**: Desativado
- **Quando ativar**: Para análise visual ou debug

### 6. 🎼 **Partitura PDF (MuseScore)**
- **Descrição**: Gera partitura musical em PDF
- **Padrão**: Desativado
- **Requisito**: MuseScore instalado
- **Quando ativar**: Se você quer sheet music para leitura

### 7. ✂️ **Hifenização**
- **Descrição**: Divide palavras em sílabas para melhor sincronização
- **Padrão**: Ativo
- **Quando desativar**: Se a sincronização automática estiver boa o suficiente

### 8. 🔊 **Audio Chunks**
- **Descrição**: Cria segmentos de áudio separados
- **Padrão**: Desativado
- **Quando ativar**: Para debug ou processamento específico

### 9. 🎤 **Arquivo Karaokê**
- **Descrição**: Cria arquivo UltraStar.txt com timing de karaoke
- **Padrão**: Ativo
- **Quando desativar**: Raramente - é o objetivo principal

## 📖 Fluxo de Uso

### Modo Rápido (Configuração Padrão)

```
1. Execute: python src/UltraSinger.py --interactive
2. Informe o arquivo de entrada
3. Escolha pasta de saída
4. Quando perguntado "Personalizar jobs?", responda: N
5. Continue com modelos padrão
```

**Jobs executados:**
- ✅ Separação Vocal
- ✅ Transcrição (Whisper)
- ✅ Detecção de Pitch (Crepe)
- ✅ Hifenização
- ✅ Arquivo Karaokê
- ❌ MIDI
- ❌ Gráficos
- ❌ Partitura

### Modo Personalizado

```
1. Execute: python src/UltraSinger.py --interactive
2. Informe o arquivo de entrada
3. Escolha pasta de saída
4. Quando perguntado "Personalizar jobs?", responda: Y
5. Selecione individualmente cada job
6. Configure modelos para jobs ativos
```

## 🎨 Interface Visual

O modo interativo usa a biblioteca Rich para criar uma interface amigável:

### Tela de Seleção de Jobs

```
┌─────────────── Jobs Disponíveis ───────────────┐
│ Job                    │ Descrição            │
├────────────────────────┼──────────────────────┤
│ 🎤 Separação Vocal     │ Separa vocais...     │
│ 📝 Transcrição         │ Transcreve letras... │
│ 🎵 Detecção de Pitch   │ Detecta notas...     │
│ 🎹 Geração de MIDI     │ Cria arquivo MIDI... │
│ 📊 Geração de Gráficos │ Visualizações...     │
│ 🎼 Partitura           │ Sheet music PDF...   │
│ ✂️ Hifenização         │ Divide sílabas...    │
└────────────────────────┴──────────────────────┘
```

### Resumo Final

```
┌─────────── Jobs de Processamento ─────────────┐
│ Job                        │ Status   │ Config │
├────────────────────────────┼──────────┼────────┤
│ 🎤 Separação Vocal         │ ✓ Ativo  │ htdemucs│
│ 📝 Transcrição (Whisper)   │ ✓ Ativo  │ large-v2│
│ 🎵 Detecção de Pitch       │ ✓ Ativo  │ full    │
│ 🎹 Geração de MIDI         │ ○ Desativado│ -   │
│ 📊 Geração de Gráficos     │ ○ Desativado│ -   │
│ ✂️ Hifenização             │ ✓ Ativo  │ -      │
└────────────────────────────┴──────────┴────────┘
```

## 💡 Casos de Uso Comuns

### Caso 1: Criação Completa de Karaoke (Padrão)

```bash
python src/UltraSinger.py --interactive
# Personalizar jobs? N
```

**Jobs:** Separação + Transcrição + Pitch + Hifenização + Karaoke

**Tempo estimado:** 5-15 minutos (música de 3-4 min)

---

### Caso 2: Re-pitch de Arquivo Existente

```bash
python src/UltraSinger.py --interactive
# Arquivo: song.txt
# Personalizar jobs? Y
# Separação Vocal? N
# Transcrição? N
# Pitch? Y (único necessário)
```

**Jobs:** Apenas Pitch Detection

**Tempo estimado:** 1-3 minutos

---

### Caso 3: Criação com Análise Completa

```bash
python src/UltraSinger.py --interactive
# Personalizar jobs? Y
# Selecionar tudo: Y
# MIDI? Y
# Gráficos? Y
# Partitura? Y (informar caminho MuseScore)
```

**Jobs:** Todos ativos

**Tempo estimado:** 10-20 minutos

**Saída:**
- UltraStar.txt
- MIDI
- Gráficos PNG
- Partitura PDF
- Vocais separados

---

### Caso 4: Processamento Rápido (Sem Separação)

```bash
python src/UltraSinger.py --interactive
# Personalizar jobs? Y
# Separação Vocal? N
# Transcrição? Y
# Outros: padrão
```

**Vantagem:** Processamento mais rápido

**Desvantagem:** Qualidade pode ser menor (instrumental interfere)

---

## ⚙️ Configurações Avançadas

Após selecionar os jobs, você ainda pode configurar opções avançadas:

### Opções de Processamento
- Batch size do Whisper
- Compute type (float16/int8)
- Step size do Crepe
- Modelo Crepe específico

### Opções de Dispositivo
- Forçar CPU/GPU
- GPU para Whisper
- GPU para Crepe

### Opções de Idioma
- Código do idioma (pt, en, es, etc.)
- Transcrever números como numerais

### Ferramentas Externas
- Caminho do MuseScore
- Cookies para YouTube
- Caminho do FFmpeg

## 💾 Sistema de Cache

O modo interativo salva suas escolhas:

**Arquivo:** `interactive_settings_cache.json`

**Conteúdo:**
```json
{
  "whisper_model": "large-v2",
  "demucs_model": "htdemucs",
  "use_separated_vocal": true,
  "ignore_audio": false,
  "create_midi": false,
  "create_plot": false,
  "hyphenation": true,
  "create_karaoke": true,
  "crepe_model_capacity": "full",
  "crepe_step_size": 10,
  "timestamp": 1727999999.123
}
```

**Vantagens:**
- Reutiliza configurações anteriores
- Acelera setup recorrente
- Pode ser editado manualmente

## 🎯 Recomendações

### Para Qualidade Máxima
✅ Ativar: Separação Vocal, Transcrição, Pitch, Hifenização
✅ Modelos: Whisper large-v2/v3, Demucs htdemucs, Crepe full
✅ Step size: 10ms ou menos

### Para Velocidade Máxima
✅ Desativar: Separação Vocal
✅ Modelos: Whisper small, Crepe tiny
✅ Step size: 20ms
❌ Desativar: Gráficos, MIDI, Partitura

### Para Análise/Debug
✅ Ativar: MIDI, Gráficos, Audio Chunks
✅ Manter cache ativo
✅ Partitura se disponível MuseScore

## 🚨 Avisos Importantes

### ⚠️ Desativar Transcrição
Se você desativar a transcrição com Whisper, **DEVE** fornecer um arquivo UltraStar.txt existente como entrada, caso contrário o processamento falhará.

### ⚠️ Desativar Separação Vocal
Processar sem separação vocal pode resultar em:
- Transcrição menos precisa
- Pitch detection com mais ruído
- Qualidade geral reduzida

Recomendado apenas se você já tem vocais limpos.

### ⚠️ Partitura PDF
Requer **MuseScore 3 ou 4** instalado no sistema. O caminho do executável deve ser informado.

## 📊 Comparação: CLI vs Interativo

| Aspecto | CLI Tradicional | Modo Interativo |
|---------|----------------|-----------------|
| **Facilidade** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Controle** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Velocidade** | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Visualização** | ❌ | ✅ Tabelas/Cores |
| **Cache** | ❌ | ✅ Auto-save |
| **Validação** | ⚠️ Manual | ✅ Automática |
| **Iniciantes** | ❌ Difícil | ✅ Fácil |

## 🎓 Conclusão

O modo interativo com seleção de jobs oferece:

✅ **Controle Total** - Escolha exatamente o que processar
✅ **Eficiência** - Evite jobs desnecessários
✅ **Flexibilidade** - Adapte ao seu caso de uso
✅ **Usabilidade** - Interface visual amigável
✅ **Produtividade** - Cache de configurações

Ideal para todos os níveis de usuário, desde iniciantes até power users que precisam de controle fino sobre o pipeline de processamento.

---

**Documentação atualizada:** Outubro 2025
**Versão UltraSinger:** 0.0.13-dev8+
