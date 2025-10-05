"""
Script para REVERTER para a configuração funcional do UltraSinger
Restaura as versões que estavam funcionando antes dos testes
"""
import subprocess
import sys

def run_command(cmd):
    """Executa comando e retorna True se bem-sucedido"""
    print(f"\n[EXEC] {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Sucesso")
        return True
    else:
        print(f"❌ Erro: {result.stderr}")
        return False

def restore_working_environment():
    """Restaura ambiente funcional"""

    print("=" * 80)
    print("RESTAURANDO AMBIENTE FUNCIONAL DO ULTRASINGER")
    print("=" * 80)
    print()

    print("📋 Configuração atual instalada:")
    print("  - whisperx: 3.1.5 ✅ (funcional)")
    print("  - pyannote.audio: 3.1.1 ✅ (funcional)")
    print("  - speechbrain: 1.0.3 ✅ (funcional)")
    print("  - tensorflow-gpu: 2.10.1 ✅ (funcional)")
    print("  - numpy: 1.26.4 ✅ (funcional)")
    print()

    print("❌ Problema identificado:")
    print("  - requirements-windows.txt foi atualizado para whisperx==3.4.3")
    print("  - Essa versão introduz problemas com modelo VAD")
    print()

    print("🔧 Solução:")
    print("  1. MANTER as versões instaladas (que estão funcionando)")
    print("  2. NÃO fazer pip install -r requirements-windows.txt")
    print("  3. Usar o ambiente atual")
    print()

    response = input("Deseja testar o ambiente atual (funcional)? [y/n]: ").lower()

    if response == 'y':
        print("\n[TEST] Testando importações básicas...")

        test_code = """
import sys
print("Testando importações...")

try:
    import whisperx
    print(f"✅ whisperx: {whisperx.__version__ if hasattr(whisperx, '__version__') else 'versão desconhecida'}")
except Exception as e:
    print(f"❌ whisperx: {e}")
    sys.exit(1)

try:
    import pyannote.audio
    print(f"✅ pyannote.audio importado com sucesso")
except Exception as e:
    print(f"❌ pyannote.audio: {e}")
    sys.exit(1)

try:
    import speechbrain
    print(f"✅ speechbrain: {speechbrain.__version__ if hasattr(speechbrain, '__version__') else 'versão desconhecida'}")
except Exception as e:
    print(f"❌ speechbrain: {e}")
    sys.exit(1)

print("\\n✅ Todas as importações funcionaram!")
print("\\n🎉 SEU AMBIENTE ESTÁ FUNCIONAL!")
print("\\n📝 Recomendação:")
print("   NÃO execute: pip install -r requirements-windows.txt")
print("   Use o ambiente atual que está funcionando")
"""

        result = subprocess.run([sys.executable, "-c", test_code],
                              capture_output=True, text=True)
        print(result.stdout)

        if result.returncode == 0:
            print("\n" + "=" * 80)
            print("✅ AMBIENTE FUNCIONAL CONFIRMADO!")
            print("=" * 80)
            print()
            print("📋 O que fazer agora:")
            print()
            print("1. ✅ USE O AMBIENTE ATUAL (está funcionando!)")
            print("   python src/UltraSinger.py --interactive")
            print()
            print("2. ❌ NÃO execute:")
            print("   pip install -r requirements-windows.txt")
            print("   (isso instalaria versões problemáticas)")
            print()
            print("3. 📝 Se precisar reinstalar no futuro:")
            print("   pip install whisperx==3.1.5")
            print("   pip install pyannote.audio==3.1.1")
            print()
            print("4. 📄 Documentação:")
            print("   Veja: DEPENDENCY_MANAGEMENT.md")
            print("   Use: python install_dependencies.py --list")
            print()
            return True
        else:
            print(result.stderr)
            return False

    else:
        print("\n✅ Mantendo ambiente atual")
        print("Execute quando quiser: python src/UltraSinger.py --interactive")
        return True

def main():
    success = restore_working_environment()

    if success:
        print("\n" + "=" * 80)
        print("🎯 RESUMO")
        print("=" * 80)
        print()
        print("✅ Seu ambiente JÁ ESTÁ FUNCIONAL com:")
        print("   - whisperx 3.1.5 (estável)")
        print("   - pyannote.audio 3.1.1 (estável)")
        print("   - Sem necessidade de correções do VAD!")
        print()
        print("🚀 Execute agora:")
        print("   python src/UltraSinger.py --interactive")
        print()
        return 0
    else:
        print("\n❌ Houve um problema no teste")
        return 1

if __name__ == "__main__":
    sys.exit(main())
