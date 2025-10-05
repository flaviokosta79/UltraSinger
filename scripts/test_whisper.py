#!/usr/bin/env python3
"""Test script for Whisper functionality"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.Speech_Recognition.Whisper import WhisperModel, transcribe_with_whisper

def test_whisper():
    print("=== Teste de Funcionalidade Whisper ===\n")
    
    print("Modelos Whisper disponíveis:")
    for model in WhisperModel:
        print(f"  - {model.value}")
    
    print("\nTestando importação do faster-whisper...")
    try:
        import faster_whisper
        print(f"✓ faster-whisper versão: {faster_whisper.__version__}")
    except ImportError as e:
        print(f"✗ Erro ao importar faster-whisper: {e}")
        return
    
    print("\nTestando configuração de dispositivo...")
    try:
        # Test device detection
        import torch
        if torch.cuda.is_available():
            print("✓ CUDA disponível")
            device_count = torch.cuda.device_count()
            print(f"  Dispositivos CUDA: {device_count}")
            if device_count > 0:
                gpu_name = torch.cuda.get_device_name(0)
                print(f"  GPU: {gpu_name}")
        else:
            print("✓ Usando CPU (CUDA não disponível)")
    except Exception as e:
        print(f"✗ Erro na detecção de dispositivo: {e}")
    
    print("\n=== Teste Concluído ===")

if __name__ == "__main__":
    test_whisper()