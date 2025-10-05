"""
Download automático do modelo VAD para WhisperX 3.1.5
Usa múltiplas fontes alternativas
"""
import os
import sys
import urllib.request
from pathlib import Path

def download_vad_model_v1():
    """Tenta baixar o modelo VAD usando diferentes fontes"""

    # Determinar caminho do cache
    cache_dir = Path.home() / ".cache" / "torch"
    cache_dir.mkdir(parents=True, exist_ok=True)

    model_path = cache_dir / "whisperx-vad-segmentation.bin"

    print("=" * 80)
    print("DOWNLOAD AUTOMÁTICO DO MODELO VAD")
    print("=" * 80)
    print()
    print(f"📁 Diretório: {cache_dir}")
    print(f"📄 Arquivo: {model_path}")
    print()

    # Verificar se já existe
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"ℹ️  Modelo já existe ({size_mb:.2f} MB)")
        response = input("Deseja baixar novamente? [y/n]: ").lower()
        if response != 'y':
            print("✅ Usando modelo existente")
            return True
        model_path.unlink()

    # Lista de URLs para tentar
    urls = [
        # Tentativa 1: Modelo Silero VAD (compatível e público)
        {
            "url": "https://github.com/snakers4/silero-vad/raw/master/files/silero_vad.jit",
            "name": "Silero VAD (modelo compatível)"
        },
        # Tentativa 2: URL original do WhisperX (pode estar redirecionada)
        {
            "url": "https://whisperx.s3.eu-west-2.amazonaws.com/model_weights/segmentation/0b5b3216d60a2d32fc086b47ea8c67589aaeb26b7e07fcbe620d6d0b83e209ea/pytorch_model.bin",
            "name": "WhisperX S3 Original"
        },
    ]

    print("🔍 Tentando baixar de fontes alternativas...\n")

    for i, source in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Tentando: {source['name']}")
        print(f"     URL: {source['url'][:70]}...")

        try:
            # Configurar opener para seguir redirecionamentos
            opener = urllib.request.build_opener(
                urllib.request.HTTPRedirectHandler()
            )
            urllib.request.install_opener(opener)

            # Tentar download
            print("     Baixando...", end=" ", flush=True)

            with urllib.request.urlopen(source['url'], timeout=30) as response:
                total_size = int(response.headers.get('Content-Length', 0))

                if total_size > 0:
                    print(f"({total_size / (1024*1024):.2f} MB)")
                else:
                    print("(tamanho desconhecido)")

                # Baixar arquivo
                with open(model_path, 'wb') as f:
                    downloaded = 0
                    chunk_size = 8192

                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r     Progresso: {progress:.1f}%", end="", flush=True)

                print("\n     ✅ Download concluído!")

                # Verificar tamanho
                final_size = model_path.stat().st_size
                print(f"     📊 Tamanho final: {final_size / (1024*1024):.2f} MB")

                if final_size < 100000:  # Menos de 100KB é suspeito
                    print("     ⚠️  Arquivo muito pequeno, pode estar corrompido")
                    model_path.unlink()
                    continue

                return True

        except Exception as e:
            print(f"\n     ❌ Falhou: {e}")
            if model_path.exists():
                model_path.unlink()
            continue

    return False


def main():
    print("\n")

    success = download_vad_model_v1()

    print("\n" + "=" * 80)
    if success:
        print("✅ MODELO VAD BAIXADO COM SUCESSO!")
        print("=" * 80)
        print()
        print("🚀 Próximos passos:")
        print("   1. Execute: python scripts/test_whisperx_quick.py")
        print("   2. Execute: python src/UltraSinger.py --interactive")
        print()
        return 0
    else:
        print("❌ DOWNLOAD FALHOU EM TODAS AS TENTATIVAS")
        print("=" * 80)
        print()
        print("📝 Solução manual:")
        print("   Veja as instruções em: SOLUCAO_VAD.md")
        print()
        print("   Opção mais simples:")
        print("   1. Use token do Hugging Face")
        print("   2. Ou desabilite o VAD temporariamente")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
