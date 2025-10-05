#!/usr/bin/env python3
"""
Script de teste para verificar a detecção de CUDA 13.0.1 e cuDNN 9.x no UltraSinger
Testa todos os componentes: PyTorch, TensorFlow, CUDA libraries e sistema de detecção
"""

import os
import sys
import subprocess
import platform

# Adicionar o diretório src ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_header(title):
    """Imprime um cabeçalho formatado"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """Imprime uma seção formatada"""
    print(f"\n--- {title} ---")

def test_system_info():
    """Testa informações do sistema"""
    print_header("INFORMAÇÕES DO SISTEMA")
    
    print(f"Sistema Operacional: {platform.system()} {platform.release()}")
    print(f"Arquitetura: {platform.architecture()[0]}")
    print(f"Python: {sys.version}")
    
    # Verificar variáveis de ambiente CUDA
    cuda_path = os.environ.get('CUDA_PATH', 'Não definido')
    cuda_path_v13_0 = os.environ.get('CUDA_PATH_V13_0', 'Não definido')
    
    print(f"CUDA_PATH: {cuda_path}")
    print(f"CUDA_PATH_V13_0: {cuda_path_v13_0}")

def test_nvidia_driver():
    """Testa o driver NVIDIA"""
    print_section("Driver NVIDIA")
    
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Driver Version:' in line:
                    print(f"✓ {line.strip()}")
                    break
        else:
            print("✗ nvidia-smi falhou")
    except Exception as e:
        print(f"✗ Erro ao executar nvidia-smi: {e}")

def test_cuda_version():
    """Testa a versão do CUDA"""
    print_section("Versão CUDA")
    
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'release' in line.lower():
                    print(f"✓ NVCC: {line.strip()}")
                    if '13.0' in line:
                        print("✓ CUDA 13.0 detectado corretamente!")
                    break
        else:
            print("✗ nvcc não encontrado")
    except Exception as e:
        print(f"✗ Erro ao executar nvcc: {e}")

def test_pytorch():
    """Testa PyTorch com CUDA"""
    print_section("PyTorch")
    
    try:
        import torch
        print(f"✓ PyTorch versão: {torch.__version__}")
        print(f"✓ CUDA disponível: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"✓ Versão CUDA do PyTorch: {torch.version.cuda}")
            print(f"✓ Número de GPUs: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                print(f"✓ GPU {i}: {gpu_name}")
                
                # Verificar se é RTX 5060TI
                if "RTX 5060" in gpu_name or "5060" in gpu_name:
                    print("✓ RTX 5060TI detectada!")
                    
                    # Testar alocação de memória
                    try:
                        device = torch.device(f'cuda:{i}')
                        x = torch.randn(1000, 1000, device=device)
                        y = torch.randn(1000, 1000, device=device)
                        z = torch.matmul(x, y)
                        print("✓ Teste de operação CUDA bem-sucedido!")
                        
                        # Verificar VRAM
                        total_memory = torch.cuda.get_device_properties(i).total_memory
                        print(f"✓ VRAM total: {total_memory / (1024**3):.1f} GB")
                        
                    except Exception as e:
                        print(f"✗ Erro no teste CUDA: {e}")
        else:
            print("✗ CUDA não disponível no PyTorch")
            
    except ImportError:
        print("✗ PyTorch não instalado")
    except Exception as e:
        print(f"✗ Erro no PyTorch: {e}")

def test_tensorflow():
    """Testa TensorFlow com CUDA"""
    print_section("TensorFlow")
    
    try:
        import tensorflow as tf
        print(f"✓ TensorFlow versão: {tf.__version__}")
        
        # Verificar GPUs físicas
        physical_devices = tf.config.list_physical_devices('GPU')
        print(f"✓ GPUs físicas detectadas: {len(physical_devices)}")
        
        for device in physical_devices:
            print(f"✓ Dispositivo: {device}")
            
        # Testar operação simples
        if physical_devices:
            try:
                with tf.device('/GPU:0'):
                    a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
                    b = tf.constant([[1.0, 1.0], [0.0, 1.0]])
                    c = tf.matmul(a, b)
                    print("✓ Teste de operação TensorFlow GPU bem-sucedido!")
            except Exception as e:
                print(f"✗ Erro no teste TensorFlow GPU: {e}")
        else:
            print("✗ Nenhuma GPU detectada pelo TensorFlow")
            
    except ImportError:
        print("✗ TensorFlow não instalado")
    except Exception as e:
        print(f"✗ Erro no TensorFlow: {e}")

def test_ultrasinger_detection():
    """Testa o sistema de detecção do UltraSinger"""
    print_section("Sistema de Detecção UltraSinger")
    
    try:
        from modules.DeviceDetection.device_detection import check_gpu_support, get_device_info
        
        print("Executando check_gpu_support()...")
        check_gpu_support()
        
        print("\nExecutando get_device_info()...")
        device_info = get_device_info()
        print(f"✓ Dispositivo recomendado: {device_info}")
        
    except ImportError as e:
        print(f"✗ Erro ao importar módulos do UltraSinger: {e}")
    except Exception as e:
        print(f"✗ Erro no sistema de detecção: {e}")

def test_cuda_compatibility_checker():
    """Testa o verificador de compatibilidade CUDA"""
    print_section("Verificador de Compatibilidade CUDA")
    
    try:
        from modules.DeviceDetection.cuda_compatibility_checker import CUDACompatibilityChecker
        
        checker = CUDACompatibilityChecker()
        print("Executando verificação completa de compatibilidade...")
        checker.check_full_compatibility()
        
    except ImportError as e:
        print(f"✗ Erro ao importar CUDACompatibilityChecker: {e}")
    except Exception as e:
        print(f"✗ Erro no verificador de compatibilidade: {e}")

def main():
    """Função principal do teste"""
    print_header("TESTE COMPLETO DE DETECÇÃO CUDA 13.0.1 + cuDNN 9.x")
    print("Testando todos os componentes do sistema de detecção GPU...")
    
    # Executar todos os testes
    test_system_info()
    test_nvidia_driver()
    test_cuda_version()
    test_pytorch()
    test_tensorflow()
    test_ultrasinger_detection()
    test_cuda_compatibility_checker()
    
    print_header("TESTE CONCLUÍDO")
    print("Verifique os resultados acima para confirmar se tudo está funcionando corretamente.")
    print("✓ = Sucesso | ✗ = Erro/Problema")

if __name__ == "__main__":
    main()