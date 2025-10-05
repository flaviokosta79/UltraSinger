# 🔧 Guia Rápido de Correção do Ambiente

## ⚡ Correção em 1 Comando

```bash
python scripts/fix_environment.py
```

## 📝 O que foi corrigido?

### Problema Original
```
urllib.error.HTTPError: HTTP Error 301: Moved Permanently
IndexError: tuple index out of range
```

### Solução Aplicada
✅ URL do modelo VAD atualizada
✅ Verificação de checksum desabilitada
✅ Tratamento de exceções corrigido

## 🚀 Como usar após correção

```bash
# Executar modo interativo
python src/UltraSinger.py --interactive

# Ou processar diretamente
python src/UltraSinger.py -i "URL_YOUTUBE"
```

## 🔍 Verificação

Se tudo estiver correto, você verá:

```
[UltraSinger] Loading whisper with model large-v3 and cuda as worker
No language specified, language will be first be detected for each audio file
```

E o processo continuará sem erros.

## ❌ Se ainda houver problemas

### Opção 1: Reinstalar WhisperX
```bash
pip install --force-reinstall whisperx==3.4.3
python scripts/fix_environment.py
```

### Opção 2: Download Manual do Modelo VAD
1. Baixe: https://huggingface.co/thomasmol/whisperx-vad/resolve/main/pytorch_model.bin
2. Salve em: `%USERPROFILE%\.cache\torch\hub\whisperx-vad-segmentation.bin`

### Opção 3: Usar CPU (fallback)
```bash
python src/UltraSinger.py --interactive --force_whisper_cpu
```

## 📚 Documentação Completa

Veja: `docs/WHISPERX_VAD_FIX.md`

## 🐛 Reportar Problemas

Se o problema persistir:
1. Salve o log completo do erro
2. Execute: `python --version` e `pip list | grep whisperx`
3. Abra uma issue com essas informações

---

**Data da Correção**: 2025-10-05
**Versão Testada**: UltraSinger 0.0.13-dev8, WhisperX 3.4.3
