"""Device detection module."""

import torch
import os
import subprocess
import sys
import platform
import tensorflow as tf

from modules.console_colors import ULTRASINGER_HEAD, red_highlighted, blue_highlighted, green_highlighted, yellow_highlighted

tensorflow_gpu_supported = False
pytorch_gpu_supported = False

def check_gpu_support() -> tuple[bool, bool]:
    """Check worker device (e.g cuda or cpu) supported by tensorflow and pytorch"""

    print(f"{ULTRASINGER_HEAD} Checking GPU support.")
    
    # Verificar drivers NVIDIA primeiro
    nvidia_driver_ok = __check_nvidia_driver()
    if not nvidia_driver_ok:
        print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Drivers NVIDIA não detectados ou desatualizados")
    
    # Verificar CUDA
    cuda_version = __check_cuda_installation()
    if cuda_version:
        print(f"{ULTRASINGER_HEAD} CUDA detectado: {blue_highlighted(cuda_version)}")
    else:
        print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} CUDA não detectado ou incompatível")

    pytorch_gpu_supported = __check_pytorch_support()
    tensorflow_gpu_supported = __check_tensorflow_support()

    tensorflow_device = 'cuda' if tensorflow_gpu_supported else 'cpu'
    pytorch_device = 'cuda' if pytorch_gpu_supported else 'cpu'

    return tensorflow_device, pytorch_device


def __check_tensorflow_support():
    tensorflow_gpu_supported = False
    try:
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            tensorflow_gpu_supported = True
            print(f"{ULTRASINGER_HEAD} {blue_highlighted('tensorflow')} - using {green_highlighted('cuda')} gpu.")
            for i, gpu in enumerate(gpus):
                print(f"{ULTRASINGER_HEAD} TensorFlow GPU {i}: {blue_highlighted(gpu.name)}")
        else:
            print(
                f"{ULTRASINGER_HEAD} {blue_highlighted('tensorflow')} - there are no {red_highlighted('cuda')} devices available -> Using {red_highlighted('cpu')}.")
            if os.name == 'nt':
                print(
                    f"{ULTRASINGER_HEAD} {blue_highlighted('tensorflow')} - versions above 2.10 dropped GPU support for Windows, refer to the readme for possible solutions.")
                # Verificar versão CUDA para sugestões específicas
                cuda_version = __check_cuda_installation()
                if cuda_version and "13.0" in cuda_version:
                    print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Suggestion:')} CUDA 13.0 detectado - considere usar TensorFlow 2.16+ ou Docker com suporte CUDA 13.0")
                    print(f"{ULTRASINGER_HEAD} {blue_highlighted('Info:')} TensorFlow nativo no Windows não suporta CUDA 13.0 oficialmente")
                else:
                    print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Suggestion:')} Consider using CUDA 11.x with TensorFlow 2.10 or use Docker container")
    except Exception as e:
        print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} TensorFlow GPU check failed: {str(e)}")
        print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Suggestion:')} Reinstall TensorFlow with GPU support or check CUDA installation")
    return tensorflow_gpu_supported


def __check_pytorch_support():
    pytorch_gpu_supported = False
    try:
        pytorch_gpu_supported = torch.cuda.is_available()
        if not pytorch_gpu_supported:
            print(
                f"{ULTRASINGER_HEAD} {blue_highlighted('pytorch')} - there are no {red_highlighted('cuda')} devices available -> Using {red_highlighted('cpu')}."
            )
            # Detectar versão CUDA instalada para sugestão apropriada
            cuda_version = __check_cuda_installation()
            if cuda_version and "13.0" in cuda_version:
                print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Suggestion:')} Install PyTorch with CUDA 13.0 support: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130")
            elif cuda_version and "12.4" in cuda_version:
                print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Suggestion:')} Install PyTorch with CUDA 12.4 support: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124")
            elif cuda_version and "12.1" in cuda_version:
                print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Suggestion:')} Install PyTorch with CUDA 12.1 support: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
            elif cuda_version and "11.8" in cuda_version:
                print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Suggestion:')} Install PyTorch with CUDA 11.8 support: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
            else:
                print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Suggestion:')} Install PyTorch with CUDA 13.0 support (latest): pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130")
        else:
            gpu_count = torch.cuda.device_count()
            print(f"{ULTRASINGER_HEAD} PyTorch detectou {green_highlighted(str(gpu_count))} GPU(s)")
            
            for i in range(gpu_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_properties = torch.cuda.get_device_properties(i)
                gpu_vram = round(gpu_properties.total_memory / 1024 ** 3, 2)  # Convert bytes to GB and round to 2 decimal places
                compute_capability = f"{gpu_properties.major}.{gpu_properties.minor}"
                
                print(f"{ULTRASINGER_HEAD} GPU {i}: {blue_highlighted(gpu_name)}")
                print(f"{ULTRASINGER_HEAD} VRAM: {blue_highlighted(str(gpu_vram))} GB, Compute: {blue_highlighted(compute_capability)}")
                
                # Verificar se é RTX 5060TI
                if "RTX 5060" in gpu_name.upper() or "5060" in gpu_name:
                    if gpu_vram >= 15.5:
                        print(f"{ULTRASINGER_HEAD} ✅ {green_highlighted('RTX 5060TI 16GB detectada!')}")
                        print(f"{ULTRASINGER_HEAD} 💡 {blue_highlighted('Dica:')} RTX 5060TI funciona melhor com CUDA 13.0 ou 12.4+")
                    else:
                        print(f"{ULTRASINGER_HEAD} ⚠️ RTX 5060 detectada mas com {gpu_vram}GB VRAM (esperado 16GB)")
                
                if gpu_vram < 6:
                    print(
                        f"{ULTRASINGER_HEAD} {red_highlighted('Warning:')} GPU VRAM is less than 6GB. Program may crash due to insufficient memory.")
                elif gpu_vram >= 16:
                    print(f"{ULTRASINGER_HEAD} ✅ {green_highlighted('Excelente!')} GPU com VRAM suficiente para modelos grandes")
                    
            print(f"{ULTRASINGER_HEAD} {blue_highlighted('pytorch')} - using {green_highlighted('cuda')} gpu.")
    except Exception as e:
        print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} PyTorch GPU check failed: {str(e)}")
        print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Suggestion:')} Reinstall PyTorch with CUDA support")
    return pytorch_gpu_supported


def __check_nvidia_driver():
    """Verificar se os drivers NVIDIA estão instalados e funcionando"""
    try:
        if platform.system() == "Windows":
            # Tentar executar nvidia-smi
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Extrair versão do driver
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Driver Version:' in line:
                        driver_version = line.split('Driver Version:')[1].split()[0]
                        print(f"{ULTRASINGER_HEAD} Driver NVIDIA: {green_highlighted(driver_version)}")
                        return True
                return True
            else:
                return False
        else:
            # Para Linux/Mac, tentar nvidia-smi também
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False


def __check_cuda_installation():
    """Verificar instalação do CUDA"""
    try:
        # Verificar via PyTorch primeiro
        if torch.cuda.is_available():
            cuda_version = torch.version.cuda
            if cuda_version:
                return f"PyTorch CUDA {cuda_version}"
        
        # Tentar nvcc --version
        try:
            result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'release' in line.lower():
                        version_part = line.split('release')[1].split(',')[0].strip()
                        # Detectar CUDA 13.0 especificamente
                        if "13.0" in version_part:
                            return f"NVCC {version_part} (CUDA 13.0 Update 1)"
                        return f"NVCC {version_part}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Verificar variáveis de ambiente CUDA
        cuda_path = os.environ.get('CUDA_PATH') or os.environ.get('CUDA_HOME')
        if cuda_path and os.path.exists(cuda_path):
            # Tentar detectar versão pelo path
            if "13.0" in cuda_path:
                return f"CUDA Path: {cuda_path} (CUDA 13.0)"
            elif "12.4" in cuda_path:
                return f"CUDA Path: {cuda_path} (CUDA 12.4)"
            elif "12.1" in cuda_path:
                return f"CUDA Path: {cuda_path} (CUDA 12.1)"
            return f"CUDA Path: {cuda_path}"
            
        return None
    except Exception:
        return None


def detect_optimal_device() -> str:
    """Detect the optimal device for processing"""
    tensorflow_device, pytorch_device = check_gpu_support()
    
    # Return the best available device
    if pytorch_device == 'cuda':
        return 'cuda'
    elif tensorflow_device == 'cuda':
        return 'cuda'
    else:
        return 'cpu'


def get_gpu_info() -> dict:
    """Obter informações detalhadas da GPU"""
    gpu_info = {
        'available': False,
        'name': 'None',
        'vram_gb': 0,
        'compute_capability': 'Unknown',
        'cuda_version': 'Unknown',
        'driver_version': 'Unknown'
    }
    
    try:
        if torch.cuda.is_available():
            gpu_info['available'] = True
            gpu_info['name'] = torch.cuda.get_device_name(0)
            
            props = torch.cuda.get_device_properties(0)
            gpu_info['vram_gb'] = round(props.total_memory / (1024**3), 2)
            gpu_info['compute_capability'] = f"{props.major}.{props.minor}"
            
            if torch.version.cuda:
                gpu_info['cuda_version'] = torch.version.cuda
                
            # Tentar obter versão do driver via nvidia-ml-py
            try:
                import pynvml
                pynvml.nvmlInit()
                gpu_info['driver_version'] = pynvml.nvmlSystemGetDriverVersion()
            except:
                pass
                
    except Exception as e:
        print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Failed to get GPU info: {str(e)}")
    
    return gpu_info
