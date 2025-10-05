import whisperx
import torch

print(f'CUDA available: {torch.cuda.is_available()}')

# Tentar carregar modelo VAD
print('Tentando carregar modelo WhisperX base...')
try:
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    compute_type = 'float16' if device == 'cuda' else 'int8'
    
    model = whisperx.load_model('base', device, compute_type=compute_type)
    print(' Modelo base carregado com sucesso!')
    print(f'Dispositivo: {device}, Compute Type: {compute_type}')
    print('Modelo WhisperX funcionando corretamente!')
except Exception as e:
    print(f' Erro ao carregar modelo: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
