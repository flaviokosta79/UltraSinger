"""
Teste rápido: Modo CORRECTION com Vagalumes
"""

import os
import sys

# Configurar modo via variável de ambiente
os.environ['LRCLIB_MODE'] = 'correction'

print("=" * 80)
print("TESTE RÁPIDO - MODO CORRECTION")
print("=" * 80)
print(f"🔧 LRCLIB_MODE={os.environ['LRCLIB_MODE']}")
print()

# Executar UltraSinger
audio = r"E:\VSCode\Projects\UltraSinger\output\Pollo - Vagalumes\Pollo - Vagalumes.mp3"
output = "output_test_correction_only"

cmd = f'python src/UltraSinger.py -i "{audio}" -o {output} --lrclib --language pt --disable_hyphenation'

print(f"📝 Executando: {cmd}")
print("⏱️  Aguarde...")
print("=" * 80)
print()

os.system(cmd)
