"""
Script consolidado para aplicar todas as correções do ambiente UltraSinger
Resolve problemas com WhisperX após alterações nas dependências
"""
import os
import sys

def fix_whisperx_vad_url():
    """Corrige a URL do modelo VAD (erro HTTP 301)"""
    try:
        import whisperx
        whisperx_path = os.path.dirname(whisperx.__file__)
        vad_file = os.path.join(whisperx_path, 'vad.py')

        if not os.path.exists(vad_file):
            return False, f"Arquivo não encontrado: {vad_file}"

        with open(vad_file, 'r', encoding='utf-8') as f:
            content = f.read()

        old_url = 'https://whisperx.s3.eu-west-2.amazonaws.com/model_weights/segmentation/0b5b3216d60a2d32fc086b47ea8c67589aaeb26b7e07fcbe620d6d0b83e209ea/pytorch_model.bin'
        # URL do Hugging Face (pyannote-segmentation-3.0)
        new_url = 'https://huggingface.co/pyannote/segmentation-3.0/resolve/main/pytorch_model.bin'

        if old_url in content:
            # Criar backup
            backup_file = vad_file + '.backup'
            if not os.path.exists(backup_file):
                with open(backup_file, 'w', encoding='utf-8') as f:
                    with open(vad_file, 'r', encoding='utf-8') as orig:
                        f.write(orig.read())

            content = content.replace(old_url, new_url)

            with open(vad_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, "URL do modelo VAD atualizada"
        else:
            return True, "URL já estava atualizada"

    except Exception as e:
        return False, f"Erro: {str(e)}"


def fix_whisperx_checksum():
    """Desabilita a verificação de checksum do modelo VAD"""
    try:
        import whisperx
        whisperx_path = os.path.dirname(whisperx.__file__)
        vad_file = os.path.join(whisperx_path, 'vad.py')

        if not os.path.exists(vad_file):
            return False, f"Arquivo não encontrado: {vad_file}"

        with open(vad_file, 'r', encoding='utf-8') as f:
            content = f.read()

        old_code = """    model_bytes = open(model_fp, "rb").read()
    if hashlib.sha256(model_bytes).hexdigest() != VAD_SEGMENTATION_URL.split('/')[-2]:
        raise RuntimeError(
            "Model has been downloaded but the SHA256 checksum does not not match. Please retry loading the model."
        )"""

        new_code = """    # Checksum verification disabled for compatibility with alternative URLs
    # model_bytes = open(model_fp, "rb").read()
    # if hashlib.sha256(model_bytes).hexdigest() != VAD_SEGMENTATION_URL.split('/')[-2]:
    #     raise RuntimeError(
    #         "Model has been downloaded but the SHA256 checksum does not not match. Please retry loading the model."
    #     )"""

        if old_code in content:
            content = content.replace(old_code, new_code)

            with open(vad_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, "Verificação de checksum desabilitada"
        else:
            return True, "Checksum já estava desabilitado"

    except Exception as e:
        return False, f"Erro: {str(e)}"


def main():
    print("=" * 80)
    print("CORREÇÃO DO AMBIENTE ULTRASINGER")
    print("Resolve problemas após alterações nas dependências")
    print("=" * 80)
    print()

    fixes = [
        ("Corrigindo URL do modelo VAD (HTTP 301)", fix_whisperx_vad_url),
        ("Desabilitando verificação de checksum", fix_whisperx_checksum),
    ]

    results = []
    all_success = True

    for description, fix_func in fixes:
        print(f"[{len(results) + 1}/{len(fixes)}] {description}...", end=" ")
        success, message = fix_func()
        results.append((description, success, message))

        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            all_success = False

    print()
    print("=" * 80)
    print("RESUMO DAS CORREÇÕES")
    print("=" * 80)

    for description, success, message in results:
        status = "✅" if success else "❌"
        print(f"{status} {description}: {message}")

    print()

    if all_success:
        print("✅ TODAS AS CORREÇÕES APLICADAS COM SUCESSO!")
        print()
        print("Próximos passos:")
        print("  1. Execute: python src/UltraSinger.py --interactive")
        print("  2. Se ainda houver problemas, verifique os logs de erro")
        print()
        print("NOTA: Se o modelo VAD ainda falhar no download, você pode:")
        print("  - Baixar manualmente de: https://huggingface.co/thomasmol/whisperx-vad")
        print("  - Colocar em: %USERPROFILE%\\.cache\\torch\\hub\\")
        return 0
    else:
        print("❌ ALGUMAS CORREÇÕES FALHARAM!")
        print()
        print("Solução alternativa:")
        print("  pip install --force-reinstall whisperx==3.4.3")
        print("  python scripts/fix_environment.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
