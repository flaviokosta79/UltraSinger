# ========================================
# Script de Teste: WhisperX 3.4.3
# ========================================
# Este script cria um ambiente virtual separado para testar WhisperX 3.4.3
# sem afetar o ambiente principal funcional

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Teste WhisperX 3.4.3 - Ambiente Isolado" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Criar ambiente virtual de teste
Write-Host "[1/6] Criando ambiente virtual de teste..." -ForegroundColor Yellow
if (Test-Path "venv_test_343") {
    Write-Host "   Ambiente já existe. Removendo..." -ForegroundColor Gray
    Remove-Item -Recurse -Force venv_test_343
}
python -m venv venv_test_343
Write-Host "   ✓ Ambiente criado: venv_test_343`n" -ForegroundColor Green

# 2. Ativar ambiente
Write-Host "[2/6] Ativando ambiente de teste..." -ForegroundColor Yellow
& .\venv_test_343\Scripts\Activate.ps1
Write-Host "   ✓ Ambiente ativado`n" -ForegroundColor Green

# 3. Atualizar pip
Write-Host "[3/6] Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel --quiet
Write-Host "   ✓ pip atualizado`n" -ForegroundColor Green

# 4. Instalar WhisperX 3.4.3 com overrides de dependências
Write-Host "[4/6] Instalando WhisperX 3.4.3 (SEM dependências automáticas)..." -ForegroundColor Yellow
pip install whisperx==3.4.3 --no-deps --quiet
Write-Host "   ✓ WhisperX 3.4.3 instalado`n" -ForegroundColor Green

# 5. Instalar dependências manualmente com versões corretas
Write-Host "[5/6] Instalando dependências compatíveis..." -ForegroundColor Yellow
Write-Host "   - ctranslate2==4.6.0 (CUDA 12.8 compatível)" -ForegroundColor Gray
pip install ctranslate2==4.6.0 --quiet

Write-Host "   - numpy<2.0 (compatível com music21/numba)" -ForegroundColor Gray
pip install "numpy<2.0" --quiet

Write-Host "   - faster-whisper>=1.1.1" -ForegroundColor Gray
pip install "faster-whisper>=1.1.1" --quiet

Write-Host "   - pyannote.audio==3.3.2" -ForegroundColor Gray
pip install pyannote.audio==3.3.2 --quiet

Write-Host "   - torch e torchaudio (PyTorch)" -ForegroundColor Gray
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet

Write-Host "   - Outras dependências" -ForegroundColor Gray
pip install transformers nltk pandas onnxruntime --quiet

Write-Host "   ✓ Todas as dependências instaladas`n" -ForegroundColor Green

# 6. Verificar instalação
Write-Host "[6/6] Verificando instalação..." -ForegroundColor Yellow
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Versões Instaladas:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
pip show whisperx ctranslate2 numpy pyannote.audio faster-whisper | Select-String "Name:|Version:"
Write-Host "========================================`n" -ForegroundColor Cyan

# Instruções finais
Write-Host "✓ AMBIENTE DE TESTE PRONTO!" -ForegroundColor Green
Write-Host "`nPróximos passos:" -ForegroundColor Yellow
Write-Host "1. O ambiente está ATIVO (venv_test_343)" -ForegroundColor White
Write-Host "2. Execute: python test_whisperx_comparison.py" -ForegroundColor White
Write-Host "3. Compare os resultados com a versão 3.3.1" -ForegroundColor White
Write-Host "`nPara DESATIVAR este ambiente:" -ForegroundColor Yellow
Write-Host "   deactivate" -ForegroundColor White
Write-Host "`nPara VOLTAR ao ambiente principal:" -ForegroundColor Yellow
Write-Host "   Use um novo terminal (o ambiente principal não foi modificado)" -ForegroundColor White
Write-Host "`n========================================`n" -ForegroundColor Cyan
