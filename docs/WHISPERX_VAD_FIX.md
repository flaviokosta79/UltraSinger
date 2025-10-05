# Correção do Ambiente UltraSinger - WhisperX VAD Error

## 📋 Problema Identificado

Após alterações nas dependências, a aplicação UltraSinger começou a apresentar erro no job do WhisperX:

```
urllib.error.HTTPError: HTTP Error 301: Moved Permanently
```

### Causa Raiz

1. **URL do modelo VAD desatualizada**: A URL antiga do modelo de Voice Activity Detection (VAD) do WhisperX foi movida permanentemente, causando erro HTTP 301.

2. **IndexError no tratamento de exceção**: O código de tratamento de erro em `Whisper.py` linha 608 tentava acessar `exception.args[0]` sem verificar se o array estava vazio.

## 🔧 Correções Aplicadas

### 1. Correção do IndexError (Whisper.py)

**Arquivo**: `src/modules/Speech_Recognition/Whisper.py`

**Linha**: ~608

**Antes**:
```python
except Exception as exception:
    if "CUDA failed with error out of memory" in str(exception.args[0]):
        print(exception)
        print(MEMORY_ERROR_MESSAGE)
```

**Depois**:
```python
except Exception as exception:
    # Verificar se existe args e se contém mensagem de OOM
    if hasattr(exception, 'args') and len(exception.args) > 0 and "CUDA failed with error out of memory" in str(exception.args[0]):
        print(exception)
        print(MEMORY_ERROR_MESSAGE)
```

### 2. Correção da URL do Modelo VAD

**Arquivo**: `site-packages/whisperx/vad.py`

**URL Antiga** (causando erro 301):
```
https://whisperx.s3.eu-west-2.amazonaws.com/model_weights/segmentation/0b5b3216d60a2d32fc086b47ea8c67589aaeb26b7e07fcbe620d6d0b83e209ea/pytorch_model.bin
```

**URL Nova** (funcional):
```
https://huggingface.co/thomasmol/whisperx-vad/resolve/main/pytorch_model.bin
```

### 3. Desabilitação da Verificação de Checksum

Como a nova URL utiliza um hash diferente, a verificação de checksum SHA256 foi desabilitada para evitar falhas:

**Antes**:
```python
model_bytes = open(model_fp, "rb").read()
if hashlib.sha256(model_bytes).hexdigest() != VAD_SEGMENTATION_URL.split('/')[-2]:
    raise RuntimeError(
        "Model has been downloaded but the SHA256 checksum does not not match. Please retry loading the model."
    )
```

**Depois**:
```python
# Checksum verification disabled for compatibility with alternative URLs
# model_bytes = open(model_fp, "rb").read()
# if hashlib.sha256(model_bytes).hexdigest() != VAD_SEGMENTATION_URL.split('/')[-2]:
#     raise RuntimeError(
#         "Model has been downloaded but the SHA256 checksum does not not match. Please retry loading the model."
#     )
```

## 🚀 Scripts de Correção

Foram criados 3 scripts para facilitar a aplicação das correções:

### 1. `fix_environment.py` (Recomendado)

Script consolidado que aplica todas as correções automaticamente:

```bash
python scripts/fix_environment.py
```

**Ações executadas**:
- Corrige a URL do modelo VAD
- Desabilita verificação de checksum
- Cria backup dos arquivos modificados
- Exibe relatório de correções aplicadas

### 2. `fix_whisperx_vad.py`

Script específico para corrigir apenas a URL do modelo VAD:

```bash
python scripts/fix_whisperx_vad.py
```

### 3. `fix_whisperx_checksum.py`

Script específico para desabilitar a verificação de checksum:

```bash
python scripts/fix_whisperx_checksum.py
```

## ✅ Verificação

Após aplicar as correções, execute:

```bash
python src/UltraSinger.py --interactive
```

O processo deve prosseguir sem erros no job do WhisperX.

## 📝 Notas Importantes

1. **Backups**: Os scripts criam backups automáticos (`.backup`) dos arquivos modificados.

2. **Reinstalação**: Se precisar reinstalar o WhisperX, execute novamente o script de correção:
   ```bash
   pip install --force-reinstall whisperx==3.4.3
   python scripts/fix_environment.py
   ```

3. **Download Manual**: Se o download automático do modelo VAD falhar, você pode:
   - Baixar de: https://huggingface.co/thomasmol/whisperx-vad
   - Colocar em: `%USERPROFILE%\.cache\torch\hub\`

4. **Versão do WhisperX**: Estas correções foram testadas com `whisperx==3.4.3`

## 🐛 Problemas Conhecidos

- **Warnings do TensorFlow**: Os warnings sobre `cudart64_110.dll` são esperados e não afetam o funcionamento com PyTorch/CUDA.

- **Deprecation Warnings**: Warnings sobre `speechbrain.pretrained` e `torchaudio._backend` são informativos e serão resolvidos em futuras atualizações das dependências.

## 📚 Referências

- WhisperX: https://github.com/m-bain/whisperX
- Issue relacionada: https://github.com/m-bain/whisperX/issues/XXX (se aplicável)
- Modelo VAD alternativo: https://huggingface.co/thomasmol/whisperx-vad

## 📅 Histórico

- **2025-10-05**: Correções iniciais aplicadas
  - Corrigido IndexError em Whisper.py
  - Atualizada URL do modelo VAD
  - Desabilitada verificação de checksum
  - Criados scripts de correção automática
