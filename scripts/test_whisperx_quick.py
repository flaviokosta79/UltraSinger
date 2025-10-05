"""
Teste rápido: verificar se WhisperX 3.1.5 funciona corretamente
"""
import sys

print("=" * 80)
print("TESTE RÁPIDO - WhisperX 3.1.5")
print("=" * 80)
print()

try:
    print("[1/3] Importando WhisperX...")
    import whisperx
    print("✅ WhisperX importado")

    print("\n[2/3] Verificando vad.py...")
    import whisperx.vad
    import os
    vad_file = whisperx.vad.__file__
    vad_size = os.path.getsize(vad_file)
    print(f"✅ vad.py encontrado: {vad_file}")
    print(f"   Tamanho: {vad_size} bytes (original: ~11697 bytes)")

    if vad_size > 12000:
        print("   ⚠️  AVISO: Arquivo maior que o esperado (pode ter modificações)")
    else:
        print("   ✅ Tamanho correto (arquivo original)")

    print("\n[3/3] Testando carga do modelo (simulação)...")
    print("   Verificando função load_vad_model...")

    # Verificar se a função existe
    from whisperx.vad import load_vad_model
    print("✅ Função load_vad_model disponível")

    print("\n" + "=" * 80)
    print("✅ TESTE BÁSICO PASSOU!")
    print("=" * 80)
    print()
    print("Próximo passo: Testar com uma música real")
    print("Execute: python src/UltraSinger.py --interactive")
    print()

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
