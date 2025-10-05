# ========================================
# Guia Passo a Passo: Teste WhisperX 3.4.3
# ========================================

## 📋 Visão Geral

Este guia mostra como testar WhisperX 3.4.3 em ambiente separado sem afetar sua instalação funcional (3.3.1).

---

## 🎯 Passo 1: Criar Ambiente de Teste

### Opção A: Usar Script Automático (Recomendado)

```powershell
# Executar script de instalação automática
.\test_whisperx_343.ps1
```

### Opção B: Instalação Manual

```powershell
# 1. Criar ambiente virtual
python -m venv venv_test_343

# 2. Ativar ambiente
.\venv_test_343\Scripts\Activate.ps1

# 3. Instalar WhisperX 3.4.3 SEM dependências automáticas
pip install whisperx==3.4.3 --no-deps

# 4. Instalar dependências manualmente (versões compatíveis)
pip install ctranslate2==4.6.0
pip install "numpy<2.0"
pip install "faster-whisper>=1.1.1"
pip install pyannote.audio==3.3.2
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers nltk pandas onnxruntime setuptools
```

---

## 🧪 Passo 2: Executar Teste Comparativo

Com o ambiente de teste ATIVO:

```powershell
# Executar script de comparação
python test_whisperx_comparison.py
```

**O que o script faz:**
- ✅ Carrega modelo WhisperX base
- ✅ Transcreve primeiros 30s do áudio
- ✅ Mostra estatísticas de performance
- ✅ Testa suporte a números (novo na 3.4.3)
- ✅ Salva resultado em `test_result_343.json`

---

## 📊 Passo 3: Testar com Ambiente Principal (3.3.1)

### 3.1. Desativar ambiente de teste

```powershell
deactivate
```

### 3.2. Abrir NOVO terminal (ambiente principal)

### 3.3. Executar mesmo teste na versão 3.3.1

```powershell
# No terminal principal (sem venv_test_343)
cd E:\VSCode\Projects\UltraSinger
python test_whisperx_comparison.py
```

Isso criará `test_result_331.json` com resultado da versão atual.

---

## 🔍 Passo 4: Comparar Resultados

### Análise Manual

Compare os arquivos:
- `test_result_331.json` - WhisperX 3.3.1 (atual)
- `test_result_343.json` - WhisperX 3.4.3 (teste)

**O que verificar:**

1. **Qualidade da transcrição**
   - Textos estão iguais ou melhores?
   - Palavras foram reconhecidas corretamente?

2. **Performance**
   - Tempo de transcrição
   - Velocidade (x tempo real)

3. **Funcionalidades novas**
   - Números têm timestamps? (3.4.3)
   - Qualidade melhorou?

### Script de Comparação Automático

```powershell
# Compare automaticamente os dois resultados
python -c "
import json

with open('test_result_331.json', 'r', encoding='utf-8') as f:
    v331 = json.load(f)

with open('test_result_343.json', 'r', encoding='utf-8') as f:
    v343 = json.load(f)

print('\n=== COMPARAÇÃO DE RESULTADOS ===\n')
print(f'Versão 3.3.1:')
print(f'  - Tempo: {v331[\"transcribe_time\"]:.2f}s')
print(f'  - Segmentos: {v331[\"segments_count\"]}')
print(f'\nVersão 3.4.3:')
print(f'  - Tempo: {v343[\"transcribe_time\"]:.2f}s')
print(f'  - Segmentos: {v343[\"segments_count\"]}')
print(f'\nDiferença:')
diff_time = v343['transcribe_time'] - v331['transcribe_time']
diff_pct = (diff_time / v331['transcribe_time']) * 100
print(f'  - Tempo: {diff_time:+.2f}s ({diff_pct:+.1f}%)')
print(f'  - Segmentos: {v343[\"segments_count\"] - v331[\"segments_count\"]:+d}')
"
```

---

## 🚀 Passo 5: Testar UltraSinger Completo (Opcional)

Se os testes básicos forem bem-sucedidos, teste o UltraSinger completo:

### 5.1. Ativar ambiente de teste

```powershell
.\venv_test_343\Scripts\Activate.ps1
```

### 5.2. Executar UltraSinger

```powershell
python src/UltraSinger.py --interactive
```

### 5.3. Verificar se tudo funciona

- ✅ GPU detectada?
- ✅ Whisper carrega?
- ✅ Demucs funciona?
- ✅ Transcrição completa?
- ✅ Arquivo .txt gerado?

---

## 🔄 Passo 6: Decisão Final

### Se 3.4.3 funcionou BEM:

#### Opção A: Manter ambiente separado para testes
```powershell
# Sempre que quiser usar 3.4.3
.\venv_test_343\Scripts\Activate.ps1
python src/UltraSinger.py --interactive
```

#### Opção B: Migrar definitivamente para 3.4.3
```powershell
# No ambiente principal
pip install whisperx==3.4.3 --no-deps
pip install ctranslate2==4.6.0 "numpy<2.0" faster-whisper>=1.1.1 pyannote.audio==3.3.2
```

### Se 3.4.3 NÃO funcionou bem:

```powershell
# 1. Desativar ambiente de teste
deactivate

# 2. (Opcional) Remover ambiente de teste
Remove-Item -Recurse -Force venv_test_343

# 3. Continuar usando 3.3.1 (ambiente principal intacto!)
```

---

## 📝 Checklist de Teste

- [ ] Ambiente de teste criado (venv_test_343)
- [ ] WhisperX 3.4.3 instalado com dependências corretas
- [ ] Teste comparativo executado (test_whisperx_comparison.py)
- [ ] Resultado 3.4.3 salvo (test_result_343.json)
- [ ] Ambiente principal testado (test_result_331.json)
- [ ] Resultados comparados
- [ ] (Opcional) UltraSinger completo testado
- [ ] Decisão tomada: Manter 3.3.1 ou migrar para 3.4.3

---

## ⚠️ Notas Importantes

### Ambiente Principal INTACTO

Seu ambiente principal com WhisperX 3.3.1 **NÃO será modificado**:
- Todos os testes usam `venv_test_343`
- Para voltar ao ambiente principal, basta abrir novo terminal
- Zero risco de quebrar o que está funcionando

### Problemas Comuns

**1. Erro "ctranslate2<4.5.0 incompatible"**
```
✓ Ignorar - instalamos 4.6.0 manualmente com --no-deps
```

**2. Erro "numpy>=2.0.2 required"**
```
✓ Ignorar - instalamos 1.26.4 manualmente com --no-deps
```

**3. CUDA errors**
```
# Verificar versão PyTorch instalada
python -c "import torch; print(torch.version.cuda)"
# Deve ser 12.1 (compatível com CUDA 12.8)
```

---

## 🎯 Resumo Rápido

```powershell
# 1. Setup (uma vez)
.\test_whisperx_343.ps1

# 2. Testar 3.4.3
python test_whisperx_comparison.py

# 3. Desativar e testar 3.3.1
deactivate
python test_whisperx_comparison.py

# 4. Comparar
# Abrir test_result_331.json e test_result_343.json

# 5. Decidir: manter 3.3.1 ou migrar 3.4.3
```

---

## 📞 Suporte

Se tiver problemas:
1. Verifique se ambiente está ativo: `(venv_test_343)` no prompt
2. Verifique versões: `pip list | grep -E "whisperx|ctranslate2|numpy"`
3. Logs de erro: copie a mensagem completa

---

**Boa sorte com os testes! 🚀**
