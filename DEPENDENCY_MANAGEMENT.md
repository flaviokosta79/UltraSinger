# Sistema de Gerenciamento de Dependências do UltraSinger

Este documento descreve como usar o sistema de gerenciamento de versões implementado no UltraSinger para alternar facilmente entre diferentes versões de dependências críticas como `pyannote.audio` e `speechbrain`.

## Visão Geral

O UltraSinger agora inclui um sistema robusto de gerenciamento de dependências que permite:
- Alternar entre diferentes versões de bibliotecas
- Verificar compatibilidade antes da instalação
- Testar avisos de deprecação
- Instalar/desinstalar versões automaticamente

## Ferramentas Disponíveis

### 1. install_dependencies.py

Script principal para gerenciar dependências.

#### Comandos Básicos

```bash
# Listar pacotes gerenciados
python install_dependencies.py --list

# Ver informações sobre uma versão específica
python install_dependencies.py --package pyannote.audio --version 4.0.0 --info
python install_dependencies.py --package tensorflow --version 2.20.0 --info

# Verificar compatibilidade
python install_dependencies.py --package pyannote.audio --version 4.0.0 --check
python install_dependencies.py --package tensorflow --version 2.20.0 --check

# Instalar uma versão específica
python install_dependencies.py --package pyannote.audio --version 4.0.0 --install
python install_dependencies.py --package tensorflow --version 2.10.0 --install

# Forçar instalação (ignorar avisos de incompatibilidade)
python install_dependencies.py --package tensorflow --version 2.20.0 --install --force
```

### pyannote.audio
```bash
# Verificar informações
python install_dependencies.py --package pyannote.audio --version 4.0.0 --info

# Verificar compatibilidade
python install_dependencies.py --package pyannote.audio --version 4.0.0 --check

# Instalar versão específica
python install_dependencies.py --package pyannote.audio --version 4.0.0 --install
python install_dependencies.py --package pyannote.audio --version 3.3.2 --install
```

### speechbrain
```bash
# Verificar informações
python install_dependencies.py --package speechbrain --version 1.0.3 --info

# Verificar compatibilidade
python install_dependencies.py --package speechbrain --version 1.0.3 --check

# Instalar versão específica
python install_dependencies.py --package speechbrain --version 1.0.3 --install
```

### tensorflow
```bash
# Verificar informações
python install_dependencies.py --package tensorflow --version 2.10.0 --info
python install_dependencies.py --package tensorflow --version 2.20.0 --info

# Verificar compatibilidade
python install_dependencies.py --package tensorflow --version 2.10.0 --check
python install_dependencies.py --package tensorflow --version 2.20.0 --check

# Instalar versão específica
python install_dependencies.py --package tensorflow --version 2.10.0 --install
python install_dependencies.py --package tensorflow --version 2.20.0 --install --force
```

### numpy
```bash
# Verificar informações
python install_dependencies.py --package numpy --version 1.23.5 --info
python install_dependencies.py --package numpy --version 2.3.3 --info

# Verificar compatibilidade
python install_dependencies.py --package numpy --version 1.23.5 --check
python install_dependencies.py --package numpy --version 2.3.3 --check

# Instalar versão específica (com detecção automática de conflitos)
python install_dependencies.py --package numpy --version 1.23.5 --install
python install_dependencies.py --package numpy --version 2.3.3 --install
```

#### Modo Interativo

```bash
# Modo interativo completo
python install_dependencies.py --interactive

# Configuração rápida com versões recomendadas
python install_dependencies.py --quick-setup
```

### 2. test_tensorflow_versions.py

Script para testar compatibilidade do TensorFlow com CREPE e outras dependências.

```bash
# Testar versão atual do TensorFlow
python test_tensorflow_versions.py
```

### 3. test_deprecation_warnings.py

Script para testar avisos de deprecação.

```bash
# Testar configuração atual
python test_deprecation_warnings.py --current

# Testar uma versão específica
python test_deprecation_warnings.py --package pyannote.audio --version 4.0.0

# Executar teste abrangente
python test_deprecation_warnings.py --comprehensive
```

## Versões Suportadas

### tensorflow
- **2.10.0** (versão estável recomendada)
  - ✅ Suporte GPU nativo no Windows
  - ✅ Compatível com CREPE
  - ✅ Estável para produção
- **2.20.0** (versão experimental)
  - ⚠️ tensorflow-io-gcs-filesystem opcional <mcreference link="https://github.com/tensorflow/tensorflow/releases/tag/v2.20.0" index="0">0</mcreference>
  - ⚠️ tf.lite será depreciado em favor do LiteRT <mcreference link="https://github.com/tensorflow/tensorflow/releases/tag/v2.20.0" index="0">0</mcreference>
  - ❌ Pode não ter suporte GPU no Windows
  - ⚠️ Requer testes extensivos com CREPE

### pyannote.audio
- **3.3.2** (versão estável atual)
- **4.0.0** (versão mais recente com breaking changes)

### speechbrain
- **1.0.3** (versão atual)

### numpy
- **1.23.5** (compatível com TensorFlow 2.10.0)
  - ✅ Resolve conflitos _ARRAY_API
  - ✅ Estável para produção
  - ✅ Compatível com TensorFlow 2.10.0
- **2.3.3** (versão mais recente) <mcreference link="https://github.com/numpy/numpy/releases/tag/v2.3.3" index="0">0</mcreference>
  - ✅ Suporte Python 3.11-3.14
  - ✅ Compatível com TensorFlow 2.20.0+
  - ⚠️ Breaking changes do NumPy 1.x
  - ❌ Incompatível com TensorFlow 2.10.0

## Matriz de Compatibilidade TensorFlow + NumPy

| TensorFlow | NumPy 1.23.5 | NumPy 2.3.3 | Status |
|------------|---------------|-------------|---------|
| 2.10.0     | ✅ Compatível | ❌ Conflito _ARRAY_API | Usar NumPy 1.23.5 |
| 2.20.0     | ⚠️ Funciona   | ✅ Recomendado | Usar NumPy 2.3.3 |

## Compatibilidade TensorFlow 2.20.0

### Requisitos
- Python >= 3.8
- Verificação de compatibilidade com CREPE

### Breaking Changes Importantes <mcreference link="https://github.com/tensorflow/tensorflow/releases/tag/v2.20.0" index="0">0</mcreference>
1. **tensorflow-io-gcs-filesystem opcional**: Agora deve ser instalado separadamente se necessário
2. **tf.lite deprecation**: tf.lite será depreciado em favor do LiteRT
3. **Suporte GPU**: Pode não ter suporte GPU nativo no Windows

### Instalação Especial
Para usar GCS filesystem com TensorFlow 2.20.0:
```bash
pip install "tensorflow[gcs-filesystem]"
```

## Compatibilidade pyannote.audio 4.0.0

### Requisitos
- Python >= 3.10 (✓ Compatível - você tem Python 3.10.11)
- Dependências atualizadas

### Breaking Changes Importantes
1. **Remoção de backends de áudio**: `sox` e `soundfile` não são mais suportados
2. **Mudanças na API**: 
   - `use_auth_token` → `token`
   - Inference agora requer modelos já instanciados
3. **Cache**: Agora usa diretório de cache do huggingface_hub

### Resultados dos Testes

#### Configuração Atual (pyannote.audio 3.3.2)
- ✅ Importações funcionam corretamente
- ✅ Nenhum aviso crítico do SpeechBrain
- ⚠️ Alguns avisos menores de outras bibliotecas (matplotlib, pkg_resources)

#### Após Atualização (pyannote.audio 4.0.0)
- ✅ Importações funcionam corretamente
- ⚠️ 1 aviso do SpeechBrain relacionado ao torchaudio (não crítico)
- ✅ Funcionalidade principal mantida

## Recomendações

### Para Uso em Produção
- **Mantenha pyannote.audio 3.3.2** para estabilidade máxima
- Use o sistema de versões para testes pontuais da v4.0.0

### Para Desenvolvimento/Testes
- **Teste pyannote.audio 4.0.0** para aproveitar melhorias de performance
- Monitore avisos de deprecação com o script de teste

## Fluxo de Trabalho Recomendado

### Para TensorFlow

1. **Verificar versão atual**:
   ```bash
   python install_dependencies.py --list
   ```

2. **Testar compatibilidade**:
   ```bash
   python test_tensorflow_versions.py
   ```

3. **Instalar versão estável (recomendado)**:
   ```bash
   python install_dependencies.py --package tensorflow --version 2.10.0 --install
   ```

4. **Testar versão experimental (opcional)**:
   ```bash
   python install_dependencies.py --package tensorflow --version 2.20.0 --install --force
   python test_tensorflow_versions.py
   ```

5. **Reverter se necessário**:
   ```bash
   python install_dependencies.py --package tensorflow --version 2.10.0 --install
   ```

### Para pyannote.audio

1. **Verificar versão atual**:
   ```bash
   python install_dependencies.py --list
   ```

2. **Testar nova versão**:
   ```bash
   python test_deprecation_warnings.py --package pyannote.audio --version 4.0.0
   ```

3. **Instalar se compatível**:
   ```bash
   python install_dependencies.py --package pyannote.audio --version 4.0.0 --install
   ```

4. **Reverter se necessário**:
   ```bash
   python install_dependencies.py --package pyannote.audio --version 3.3.2 --install
   ```

## Solução de Problemas

### Conflito TensorFlow + NumPy (_ARRAY_API not found)
Se encontrar o erro `_ARRAY_API not found`:
```bash
# Solução 1: Usar NumPy compatível com TensorFlow 2.10.0
python install_dependencies.py --package numpy --version 1.23.5 --install

# Solução 2: Atualizar para TensorFlow 2.20.0 + NumPy 2.3.3
python install_dependencies.py --package tensorflow --version 2.20.0 --install --force
python install_dependencies.py --package numpy --version 2.3.3 --install
```

### Erro de Importação
Se encontrar erros como `ModuleNotFoundError`, verifique se o pacote foi instalado corretamente:
```bash
python install_dependencies.py --list
```

### Avisos de Deprecação
Use o script de teste para identificar avisos:
```bash
python test_deprecation_warnings.py --package pyannote.audio --version 4.0.0
```

### Teste de Compatibilidade TensorFlow + NumPy
Para verificar se a combinação está funcionando:
```bash
python test_tensorflow_versions.py
```

### Incompatibilidade
- Use `--force` apenas se tiver certeza da compatibilidade
- Sempre teste em ambiente de desenvolvimento primeiro
- Mantenha backup da configuração funcional

## Estrutura dos Arquivos

```
UltraSingerX/
├── install_dependencies.py      # Gerenciador principal
├── test_deprecation_warnings.py # Testador de avisos
├── src/modules/
│   ├── version_manager.py       # Classe VersionManager
│   └── console_colors.py        # Cores do console
└── DEPENDENCY_MANAGEMENT.md     # Esta documentação
```

## Conclusão

O sistema implementado permite alternar facilmente entre versões do pyannote.audio, com a v4.0.0 sendo tecnicamente compatível mas com breaking changes que requerem atenção. Para uso imediato, recomenda-se manter a v3.3.2 estável, usando a v4.0.0 para testes e desenvolvimento futuro.