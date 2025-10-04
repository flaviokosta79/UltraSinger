"""CUDA Compatibility Checker for RTX 5060TI and CUDA 12.x"""

import subprocess
import os
import sys
import platform
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from modules.console_colors import ULTRASINGER_HEAD, red_highlighted, blue_highlighted, green_highlighted, yellow_highlighted


@dataclass
class CUDACompatibility:
    """CUDA compatibility information"""
    cuda_available: bool = False
    cuda_version: str = "Unknown"
    cudnn_version: str = "Unknown"
    driver_version: str = "Unknown"
    compute_capability: str = "Unknown"
    libraries_found: List[str] = None
    missing_libraries: List[str] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.libraries_found is None:
            self.libraries_found = []
        if self.missing_libraries is None:
            self.missing_libraries = []
        if self.recommendations is None:
            self.recommendations = []


class CUDACompatibilityChecker:
    """Verificador de compatibilidade CUDA para RTX 5060TI"""
    
    def __init__(self):
        self.required_cuda_libs = [
            "cudart64_110.dll",  # CUDA Runtime 11.0
            "cudart64_111.dll",  # CUDA Runtime 11.1
            "cudart64_112.dll",  # CUDA Runtime 11.2
            "cudart64_120.dll",  # CUDA Runtime 12.0
            "cudart64_121.dll",  # CUDA Runtime 12.1
            "cudart64_122.dll",  # CUDA Runtime 12.2
            "cudart64_123.dll",  # CUDA Runtime 12.3
            "cudart64_124.dll",  # CUDA Runtime 12.4
            "cudart64_130.dll",  # CUDA Runtime 13.0
            "cudart64_131.dll",  # CUDA Runtime 13.1
            "cublas64_11.dll",   # CUDA BLAS
            "cublas64_12.dll",   # CUDA BLAS 12.x
            "cublas64_13.dll",   # CUDA BLAS 13.x
            "cublasLt64_11.dll", # CUDA BLAS LT
            "cublasLt64_12.dll", # CUDA BLAS LT 12.x
            "cublasLt64_13.dll", # CUDA BLAS LT 13.x
            "cufft64_10.dll",    # CUDA FFT
            "cufft64_11.dll",    # CUDA FFT 11.x
            "cufft64_12.dll",    # CUDA FFT 12.x
            "cufft64_13.dll",    # CUDA FFT 13.x
            "curand64_10.dll",   # CUDA Random
            "curand64_11.dll",   # CUDA Random 11.x
            "curand64_12.dll",   # CUDA Random 12.x
            "curand64_13.dll",   # CUDA Random 13.x
            "cusolver64_11.dll", # CUDA Solver
            "cusolver64_12.dll", # CUDA Solver 12.x
            "cusolver64_13.dll", # CUDA Solver 13.x
            "cusparse64_11.dll", # CUDA Sparse
            "cusparse64_12.dll", # CUDA Sparse 12.x
            "cusparse64_13.dll", # CUDA Sparse 13.x
            "cudnn64_8.dll",     # cuDNN 8.x
            "cudnn64_9.dll"      # cuDNN 9.x
        ]
        
        self.cuda_paths = [
            os.environ.get('CUDA_PATH', ''),
            os.environ.get('CUDA_HOME', ''),
            r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA',
            r'C:\Program Files (x86)\NVIDIA GPU Computing Toolkit\CUDA',
            r'C:\tools\cuda',
            r'C:\cuda',
            r'E:\cudnn-cuda12\bin'  # Path customizado do usuário para cuDNN
        ]
    
    def check_full_compatibility(self) -> CUDACompatibility:
        """Verificação completa de compatibilidade CUDA"""
        print(f"{ULTRASINGER_HEAD} 🔍 Verificando compatibilidade CUDA...")
        
        compatibility = CUDACompatibility()
        
        # 1. Verificar drivers NVIDIA
        driver_ok, driver_version = self._check_nvidia_driver()
        compatibility.driver_version = driver_version
        
        # 2. Verificar instalação CUDA
        cuda_ok, cuda_version = self._check_cuda_installation()
        compatibility.cuda_available = cuda_ok
        compatibility.cuda_version = cuda_version
        
        # 3. Verificar bibliotecas CUDA
        found_libs, missing_libs = self._check_cuda_libraries()
        compatibility.libraries_found = found_libs
        compatibility.missing_libraries = missing_libs
        
        # 4. Verificar cuDNN
        cudnn_version = self._check_cudnn()
        compatibility.cudnn_version = cudnn_version
        
        # 5. Gerar recomendações
        compatibility.recommendations = self._generate_recommendations(compatibility)
        
        # 6. Mostrar relatório
        self._print_compatibility_report(compatibility)
        
        return compatibility
    
    def _check_nvidia_driver(self) -> Tuple[bool, str]:
        """Verificar driver NVIDIA"""
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Driver Version:' in line:
                        driver_version = line.split('Driver Version:')[1].split()[0]
                        print(f"{ULTRASINGER_HEAD} ✅ Driver NVIDIA: {green_highlighted(driver_version)}")
                        return True, driver_version
                return True, "Unknown"
            else:
                print(f"{ULTRASINGER_HEAD} ❌ nvidia-smi falhou")
                return False, "Not Found"
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} ❌ Erro ao verificar driver: {str(e)}")
            return False, "Error"
    
    def _check_cuda_installation(self) -> Tuple[bool, str]:
        """Verificar instalação CUDA"""
        # Verificar via nvcc
        try:
            result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'release' in line.lower():
                        version_part = line.split('release')[1].split(',')[0].strip()
                        print(f"{ULTRASINGER_HEAD} ✅ NVCC: {green_highlighted(version_part)}")
                        return True, version_part
        except Exception:
            pass
        
        # Verificar via PyTorch
        try:
            import torch
            if torch.cuda.is_available():
                cuda_version = torch.version.cuda
                if cuda_version:
                    print(f"{ULTRASINGER_HEAD} ✅ PyTorch CUDA: {green_highlighted(cuda_version)}")
                    return True, f"PyTorch {cuda_version}"
        except Exception:
            pass
        
        # Verificar paths CUDA
        for cuda_path in self.cuda_paths:
            if cuda_path and os.path.exists(cuda_path):
                print(f"{ULTRASINGER_HEAD} ✅ CUDA Path encontrado: {blue_highlighted(cuda_path)}")
                return True, f"Path: {cuda_path}"
        
        print(f"{ULTRASINGER_HEAD} ❌ CUDA não encontrado")
        return False, "Not Found"
    
    def _check_cuda_libraries(self) -> Tuple[List[str], List[str]]:
        """Verificar bibliotecas CUDA"""
        found_libs = []
        missing_libs = []
        
        # Verificar no PATH do sistema
        system_paths = os.environ.get('PATH', '').split(os.pathsep)
        
        # Adicionar paths CUDA conhecidos
        search_paths = system_paths.copy()
        for path in self.cuda_paths:
            if path and os.path.exists(path):
                # Se o path já termina com 'bin', adicionar diretamente
                if path.endswith('bin'):
                    search_paths.append(path)
                else:
                    # Adicionar o subdiretório bin
                    bin_path = path + r'\bin'
                    if os.path.exists(bin_path):
                        search_paths.append(bin_path)
        
        for lib in self.required_cuda_libs:
            found = False
            for path in search_paths:
                if path and os.path.exists(path):
                    lib_path = os.path.join(path, lib)
                    if os.path.exists(lib_path):
                        found_libs.append(f"{lib} ({path})")
                        found = True
                        break
            
            if not found:
                missing_libs.append(lib)
        
        print(f"{ULTRASINGER_HEAD} 📚 Bibliotecas encontradas: {green_highlighted(str(len(found_libs)))}")
        print(f"{ULTRASINGER_HEAD} ❌ Bibliotecas faltando: {red_highlighted(str(len(missing_libs)))}")
        
        return found_libs, missing_libs
    
    def _check_cudnn(self) -> str:
        """Verificar cuDNN"""
        try:
            # Tentar importar e verificar cuDNN via TensorFlow
            import tensorflow as tf
            if hasattr(tf.config, 'list_physical_devices'):
                gpus = tf.config.list_physical_devices('GPU')
                if gpus:
                    # TensorFlow detectou GPU, provavelmente cuDNN está OK
                    return "Available (via TensorFlow)"
        except Exception:
            pass
        
        # Verificar arquivos cuDNN nos paths conhecidos
        for cuda_path in self.cuda_paths:
            if cuda_path and os.path.exists(cuda_path):
                # Verificar se é um path direto para bin (como E:\cudnn-cuda12\bin)
                if cuda_path.endswith('bin'):
                    # Verificar diretamente no path bin
                    cudnn8_path = os.path.join(cuda_path, 'cudnn64_8.dll')
                    cudnn9_path = os.path.join(cuda_path, 'cudnn64_9.dll')
                    
                    if os.path.exists(cudnn8_path):
                        print(f"{ULTRASINGER_HEAD} ✅ cuDNN 8.x encontrado em: {blue_highlighted(cuda_path)}")
                        return f"cuDNN 8.x found ({cuda_path})"
                    if os.path.exists(cudnn9_path):
                        print(f"{ULTRASINGER_HEAD} ✅ cuDNN 9.x encontrado em: {blue_highlighted(cuda_path)}")
                        return f"cuDNN 9.x found ({cuda_path})"
                else:
                    # Verificar no subdiretório bin
                    cudnn8_path = os.path.join(cuda_path, 'bin', 'cudnn64_8.dll')
                    cudnn9_path = os.path.join(cuda_path, 'bin', 'cudnn64_9.dll')
                    
                    if os.path.exists(cudnn8_path):
                        print(f"{ULTRASINGER_HEAD} ✅ cuDNN 8.x encontrado em: {blue_highlighted(os.path.join(cuda_path, 'bin'))}")
                        return f"cuDNN 8.x found ({os.path.join(cuda_path, 'bin')})"
                    if os.path.exists(cudnn9_path):
                        print(f"{ULTRASINGER_HEAD} ✅ cuDNN 9.x encontrado em: {blue_highlighted(os.path.join(cuda_path, 'bin'))}")
                        return f"cuDNN 9.x found ({os.path.join(cuda_path, 'bin')})"
        
        return "Not Found"
    
    def _generate_recommendations(self, compatibility: CUDACompatibility) -> List[str]:
        """Gerar recomendações baseadas na compatibilidade"""
        recommendations = []
        
        if not compatibility.cuda_available:
            recommendations.append("Instalar CUDA Toolkit 13.0 da NVIDIA (recomendado para RTX 5060TI)")
            recommendations.append("Baixar de: https://developer.nvidia.com/cuda-downloads")
        
        if compatibility.driver_version == "Not Found":
            recommendations.append("Instalar drivers NVIDIA mais recentes (545.84 ou superior)")
            recommendations.append("Baixar de: https://www.nvidia.com/drivers")
        
        if compatibility.missing_libraries:
            recommendations.append("Reinstalar CUDA Toolkit para corrigir bibliotecas faltando")
            if "cudart64_130.dll" in compatibility.missing_libraries:
                recommendations.append("Instalar especificamente CUDA 13.0 Update 1")
            elif "cudart64_120.dll" in compatibility.missing_libraries:
                recommendations.append("Instalar especificamente CUDA 12.0 ou superior")
        
        if compatibility.cudnn_version == "Not Found":
            recommendations.append("Instalar cuDNN 8.9 ou 9.x (compatível com CUDA 13.0)")
            recommendations.append("Baixar de: https://developer.nvidia.com/cudnn")
        
        # Recomendações específicas para RTX 5060TI
        recommendations.append("Para RTX 5060TI: usar CUDA 13.0 para melhor performance e compatibilidade")
        recommendations.append("PyTorch com CUDA 13.0: pip install torch --index-url https://download.pytorch.org/whl/cu130")
        recommendations.append("Configurar variável CUDA_PATH corretamente")
        
        return recommendations
    
    def _print_compatibility_report(self, compatibility: CUDACompatibility):
        """Imprimir relatório de compatibilidade"""
        print(f"\n{ULTRASINGER_HEAD} " + "="*60)
        print(f"{ULTRASINGER_HEAD} 📊 RELATÓRIO DE COMPATIBILIDADE CUDA")
        print(f"{ULTRASINGER_HEAD} " + "="*60)
        
        # Status geral
        if compatibility.cuda_available:
            print(f"{ULTRASINGER_HEAD} ✅ CUDA: {green_highlighted('Disponível')} ({compatibility.cuda_version})")
        else:
            print(f"{ULTRASINGER_HEAD} ❌ CUDA: {red_highlighted('Não Disponível')}")
        
        print(f"{ULTRASINGER_HEAD} 🔧 Driver: {compatibility.driver_version}")
        print(f"{ULTRASINGER_HEAD} 🧠 cuDNN: {compatibility.cudnn_version}")
        
        # Bibliotecas
        if compatibility.libraries_found:
            print(f"{ULTRASINGER_HEAD} ✅ Bibliotecas encontradas: {len(compatibility.libraries_found)}")
        
        if compatibility.missing_libraries:
            print(f"{ULTRASINGER_HEAD} ❌ Bibliotecas faltando: {len(compatibility.missing_libraries)}")
            for lib in compatibility.missing_libraries[:5]:  # Mostrar apenas as primeiras 5
                print(f"{ULTRASINGER_HEAD}   - {red_highlighted(lib)}")
            if len(compatibility.missing_libraries) > 5:
                print(f"{ULTRASINGER_HEAD}   ... e mais {len(compatibility.missing_libraries) - 5}")
        
        # Recomendações
        if compatibility.recommendations:
            print(f"\n{ULTRASINGER_HEAD} 💡 RECOMENDAÇÕES:")
            for i, rec in enumerate(compatibility.recommendations, 1):
                print(f"{ULTRASINGER_HEAD} {i}. {yellow_highlighted(rec)}")
        
        print(f"{ULTRASINGER_HEAD} " + "="*60)
    
    def fix_cuda_path(self):
        """Tentar corrigir automaticamente o CUDA_PATH"""
        print(f"{ULTRASINGER_HEAD} 🔧 Tentando corrigir CUDA_PATH...")
        
        # Procurar instalações CUDA
        possible_paths = []
        base_paths = [
            r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA',
            r'C:\Program Files (x86)\NVIDIA GPU Computing Toolkit\CUDA'
        ]
        
        for base_path in base_paths:
            if os.path.exists(base_path):
                for item in os.listdir(base_path):
                    item_path = os.path.join(base_path, item)
                    if os.path.isdir(item_path) and item.startswith('v'):
                        possible_paths.append(item_path)
        
        if possible_paths:
            # Usar a versão mais recente
            latest_path = sorted(possible_paths)[-1]
            print(f"{ULTRASINGER_HEAD} ✅ CUDA encontrado em: {green_highlighted(latest_path)}")
            bin_path = latest_path + r'\bin'
            print(f"{ULTRASINGER_HEAD} 💡 Adicione ao PATH: {yellow_highlighted(bin_path)}")
            return latest_path
        else:
            print(f"{ULTRASINGER_HEAD} ❌ Nenhuma instalação CUDA encontrada")
            return None


def main():
    """Função principal para teste"""
    checker = CUDACompatibilityChecker()
    compatibility = checker.check_full_compatibility()
    
    if not compatibility.cuda_available:
        checker.fix_cuda_path()


if __name__ == "__main__":
    main()