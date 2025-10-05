"""
Correção avançada do WhisperX VAD - Adiciona suporte a redirecionamentos HTTP
"""
import os
import sys

def fix_whisperx_vad_advanced():
    """Modifica o vad.py para seguir redirecionamentos HTTP"""
    try:
        import whisperx
        whisperx_path = os.path.dirname(whisperx.__file__)
        vad_file = os.path.join(whisperx_path, 'vad.py')

        print(f"[FIX] Localizando arquivo vad.py: {vad_file}")

        if not os.path.exists(vad_file):
            print(f"[ERRO] Arquivo não encontrado: {vad_file}")
            return False

        # Fazer backup se ainda não existe
        backup_file = vad_file + '.backup_original'
        if not os.path.exists(backup_file):
            with open(vad_file, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            print(f"[FIX] Backup criado: {backup_file}")

        # Ler o conteúdo atual
        with open(vad_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Código antigo que falha com 301
        old_download_code = """    if not os.path.isfile(model_fp):
        with urllib.request.urlopen(VAD_SEGMENTATION_URL) as source, open(model_fp, "wb") as output:
            with tqdm(
                total=int(source.info().get("Content-Length")),
                ncols=80,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as loop:
                while True:
                    buffer = source.read(8192)
                    if not buffer:
                        break

                    output.write(buffer)
                    loop.update(len(buffer))"""

        # Novo código com suporte a redirecionamento e fallback
        new_download_code = """    if not os.path.isfile(model_fp):
        import urllib.request
        from urllib.error import HTTPError, URLError

        # Tentar URLs alternativas
        urls = [
            VAD_SEGMENTATION_URL,
            "https://huggingface.co/pyannote/segmentation-3.0/resolve/main/pytorch_model.bin",
        ]

        download_success = False
        for url_attempt in urls:
            try:
                print(f"Tentando baixar modelo VAD de: {url_attempt[:60]}...")
                # Usar urllib com suporte a redirecionamento
                opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
                urllib.request.install_opener(opener)

                with urllib.request.urlopen(url_attempt, timeout=30) as source:
                    total_size = int(source.info().get("Content-Length", 0))

                    with open(model_fp, "wb") as output:
                        if total_size > 0:
                            with tqdm(
                                total=total_size,
                                ncols=80,
                                unit="iB",
                                unit_scale=True,
                                unit_divisor=1024,
                            ) as loop:
                                while True:
                                    buffer = source.read(8192)
                                    if not buffer:
                                        break
                                    output.write(buffer)
                                    loop.update(len(buffer))
                        else:
                            # Fallback sem progress bar
                            output.write(source.read())

                download_success = True
                print(f"✅ Download concluído com sucesso!")
                break

            except (HTTPError, URLError) as e:
                print(f"⚠️  Falha: {e}")
                if url_attempt != urls[-1]:
                    print("   Tentando URL alternativa...")
                continue
            except Exception as e:
                print(f"⚠️  Erro inesperado: {e}")
                if url_attempt != urls[-1]:
                    print("   Tentando URL alternativa...")
                continue

        if not download_success:
            raise RuntimeError(
                "Falha ao baixar modelo VAD de todas as URLs. "
                "Por favor, baixe manualmente de https://huggingface.co/pyannote/segmentation-3.0 "
                f"e salve em {model_fp}"
            )"""

        if old_download_code in content:
            print("[FIX] Aplicando correção avançada com suporte a redirecionamentos...")
            content = content.replace(old_download_code, new_download_code)

            with open(vad_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print("[FIX] ✅ Correção avançada aplicada com sucesso!")
            return True
        else:
            print("[FIX] Código de download não encontrado ou já foi modificado.")
            # Verificar se já foi aplicada uma correção similar
            if "urls = [" in content and "url_attempt" in content:
                print("[FIX] ✅ Correção avançada já estava aplicada!")
                return True
            return False

    except Exception as e:
        print(f"[ERRO] Falha ao aplicar correção: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 80)
    print("CORREÇÃO AVANÇADA DO WHISPERX VAD")
    print("Adiciona suporte a redirecionamentos HTTP e URLs de fallback")
    print("=" * 80)
    print()

    success = fix_whisperx_vad_advanced()

    print()
    if success:
        print("✅ Correção avançada concluída!")
        print()
        print("O sistema agora tentará automaticamente URLs alternativas se uma falhar.")
        print()
        print("Execute: python scripts/test_whisperx_environment.py")
        sys.exit(0)
    else:
        print("❌ Correção falhou!")
        print()
        print("Tente restaurar do backup:")
        print("  1. Localize o arquivo .backup_original")
        print("  2. Copie de volta para vad.py")
        print("  3. Execute novamente este script")
        sys.exit(1)
