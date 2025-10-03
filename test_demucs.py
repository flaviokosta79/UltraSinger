#!/usr/bin/env python3
"""Test script for Demucs functionality"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.Audio.separation import DemucsModel, check_device_compatibility, estimate_memory_usage

def test_demucs():
    print("=== Teste de Funcionalidade Demucs ===\n")
    
    print("Modelos Demucs disponíveis:")
    for model in DemucsModel:
        info = DemucsModel.get_model_info(model)
        print(f"  - {model.value}: {info}")
    
    print("\nCompatibilidade de dispositivo:")
    cpu_compat = check_device_compatibility("cpu")
    cuda_compat = check_device_compatibility("cuda")
    print(f"CPU: {cpu_compat}")
    print(f"CUDA: {cuda_compat}")
    
    print("\nEstimativa de uso de memória (modelo htdemucs):")
    try:
        vram, ram = estimate_memory_usage(DemucsModel.HTDEMUCS, "cuda")
        print(f"VRAM: {vram}GB, RAM: {ram}GB")
    except Exception as e:
        print(f"Erro ao estimar memória: {e}")
    
    print("\n=== Teste Concluído ===")

if __name__ == "__main__":
    test_demucs()