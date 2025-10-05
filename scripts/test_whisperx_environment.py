"""
Teste rápido do ambiente WhisperX após correções
Verifica se o modelo VAD pode ser carregado corretamente
"""
import sys
import os

def test_whisperx_vad():
    """Testa se o WhisperX consegue carregar o modelo VAD"""
    try:
        print("[TEST] Importando WhisperX...")
        import whisperx
        print("✅ WhisperX importado com sucesso")

        print("\n[TEST] Verificando versão...")
        version = whisperx.__version__ if hasattr(whisperx, '__version__') else "desconhecida"
        print(f"✅ Versão do WhisperX: {version}")

        print("\n[TEST] Verificando arquivo vad.py...")
        whisperx_path = os.path.dirname(whisperx.__file__)
        vad_file = os.path.join(whisperx_path, 'vad.py')

        if os.path.exists(vad_file):
            print(f"✅ Arquivo vad.py encontrado: {vad_file}")

            # Verificar se a correção foi aplicada
            with open(vad_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if 'huggingface.co' in content:
                print("✅ URL corrigida detectada (Hugging Face)")
            else:
                print("⚠️  URL antiga ainda presente ou não verificável")

            if '# Checksum verification disabled' in content:
                print("✅ Verificação de checksum desabilitada")
            else:
                print("⚠️  Verificação de checksum ainda ativa")
        else:
            print(f"❌ Arquivo vad.py não encontrado: {vad_file}")
            return False

        print("\n[TEST] Testando carregamento do modelo VAD...")
        print("NOTA: Este teste baixará o modelo VAD (~50MB) se ainda não estiver em cache.")
        print("      O download pode levar alguns minutos dependendo da sua conexão.")

        try:
            import torch
            from whisperx.vad import load_vad_model

            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"[TEST] Usando device: {device}")

            print("[TEST] Carregando modelo VAD...")
            vad_model = load_vad_model(torch.device(device))
            print("✅ Modelo VAD carregado com sucesso!")

            return True

        except Exception as e:
            print(f"❌ Erro ao carregar modelo VAD: {str(e)}")
            print("\nSugestões:")
            print("1. Verifique sua conexão com a internet")
            print("2. Tente novamente (o download pode ter sido interrompido)")
            print("3. Execute: python scripts/fix_environment.py")
            return False

    except ImportError as e:
        print(f"❌ Erro ao importar WhisperX: {str(e)}")
        print("\nSolução:")
        print("  pip install whisperx==3.4.3")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 80)
    print("TESTE DO AMBIENTE WHISPERX")
    print("=" * 80)
    print()

    success = test_whisperx_vad()

    print()
    print("=" * 80)
    if success:
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print()
        print("Seu ambiente está pronto para usar o UltraSinger.")
        print("Execute: python src/UltraSinger.py --interactive")
        return 0
    else:
        print("❌ TESTE FALHOU!")
        print()
        print("Execute as correções novamente:")
        print("  python scripts/fix_environment.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
