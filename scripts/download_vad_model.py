"""
Script para baixar manualmente o modelo VAD do WhisperX
Usa o modelo pyannote disponível publicamente
"""
import os
import sys
import urllib.request
import torch
from tqdm import tqdm

def download_vad_model():
    """Baixa o modelo VAD usando pyannote diretamente"""
    try:
        # Determinar o caminho do cache
        model_dir = torch.hub._get_torch_home()
        os.makedirs(model_dir, exist_ok=True)
        model_fp = os.path.join(model_dir, "whisperx-vad-segmentation.bin")

        print(f"[DOWNLOAD] Diretório de cache: {model_dir}")
        print(f"[DOWNLOAD] Arquivo destino: {model_fp}")

        if os.path.exists(model_fp):
            print(f"[INFO] Modelo VAD já existe. Removendo para baixar novamente...")
            os.remove(model_fp)

        print("\n[DOWNLOAD] Usando pyannote.audio para obter modelo...")
        print("[INFO] Isto fará download do modelo de segmentação do pyannote")

        try:
            from pyannote.audio import Model

            print("[DOWNLOAD] Baixando modelo pyannote/segmentation-3.0...")
            print("[INFO] Este download pode levar alguns minutos...")

            # Baixar modelo do pyannote diretamente
            model = Model.from_pretrained("pyannote/segmentation-3.0", use_auth_token=None)

            # Salvar no local esperado pelo WhisperX
            print(f"[DOWNLOAD] Salvando em: {model_fp}")
            torch.save(model.state_dict(), model_fp)

            print("[DOWNLOAD] ✅ Modelo VAD baixado e salvo com sucesso!")

            # Verificar tamanho do arquivo
            file_size = os.path.getsize(model_fp)
            print(f"[INFO] Tamanho do arquivo: {file_size / (1024*1024):.2f} MB")

            return True, model_fp

        except Exception as e:
            print(f"[ERRO] Falha ao baixar modelo do pyannote: {str(e)}")
            print("\n[INFO] Tentando método alternativo...")

            # Método alternativo: baixar do repositório público
            urls = [
                "https://github.com/pyannote/pyannote-audio/raw/develop/tutorials/models/segmentation-3.0/pytorch_model.bin",
                "https://huggingface.co/pyannote/segmentation/resolve/main/pytorch_model.bin",
            ]

            for url in urls:
                try:
                    print(f"[DOWNLOAD] Tentando: {url}")

                    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
                    urllib.request.install_opener(opener)

                    with urllib.request.urlopen(url, timeout=60) as response:
                        total_size = int(response.info().get("Content-Length", 0))

                        with open(model_fp, "wb") as f:
                            if total_size > 0:
                                with tqdm(total=total_size, unit='B', unit_scale=True, desc="Baixando") as pbar:
                                    while True:
                                        chunk = response.read(8192)
                                        if not chunk:
                                            break
                                        f.write(chunk)
                                        pbar.update(len(chunk))
                            else:
                                f.write(response.read())

                    print(f"[DOWNLOAD] ✅ Download concluído!")
                    return True, model_fp

                except Exception as e2:
                    print(f"[ERRO] Falhou: {e2}")
                    continue

            return False, "Todos os métodos de download falharam"

    except Exception as e:
        print(f"[ERRO] Erro fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def main():
    print("=" * 80)
    print("DOWNLOAD MANUAL DO MODELO VAD DO WHISPERX")
    print("=" * 80)
    print()
    print("Este script baixa o modelo de Voice Activity Detection necessário")
    print("para o WhisperX funcionar corretamente.")
    print()

    success, result = download_vad_model()

    print()
    print("=" * 80)
    if success:
        print("✅ DOWNLOAD CONCLUÍDO COM SUCESSO!")
        print()
        print(f"Modelo salvo em: {result}")
        print()
        print("Próximos passos:")
        print("  1. Execute: python scripts/test_whisperx_environment.py")
        print("  2. Execute: python src/UltraSinger.py --interactive")
        return 0
    else:
        print("❌ DOWNLOAD FALHOU!")
        print()
        print(f"Erro: {result}")
        print()
        print("Solução manual:")
        print("  1. Acesse: https://huggingface.co/pyannote/segmentation-3.0")
        print("  2. Baixe o arquivo pytorch_model.bin")
        print("  3. Renomeie para: whisperx-vad-segmentation.bin")
        print("  4. Coloque em: %USERPROFILE%\\.cache\\torch\\hub\\")
        return 1


if __name__ == "__main__":
    sys.exit(main())
