"""
Script para corrigir o checksum do modelo VAD no WhisperX
Remove a verificação de checksum que causa problemas com a nova URL
"""
import os
import sys

def fix_whisperx_checksum():
    try:
        import whisperx
        whisperx_path = os.path.dirname(whisperx.__file__)
        vad_file = os.path.join(whisperx_path, 'vad.py')

        print(f"[FIX] Localizando arquivo vad.py: {vad_file}")

        if not os.path.exists(vad_file):
            print(f"[ERRO] Arquivo não encontrado: {vad_file}")
            return False

        # Ler o conteúdo do arquivo
        with open(vad_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Código antigo com verificação de checksum
        old_code = """    model_bytes = open(model_fp, "rb").read()
    if hashlib.sha256(model_bytes).hexdigest() != VAD_SEGMENTATION_URL.split('/')[-2]:
        raise RuntimeError(
            "Model has been downloaded but the SHA256 checksum does not not match. Please retry loading the model."
        )"""

        # Novo código sem verificação (apenas comentário informativo)
        new_code = """    # Checksum verification disabled for compatibility with alternative URLs
    # model_bytes = open(model_fp, "rb").read()
    # if hashlib.sha256(model_bytes).hexdigest() != VAD_SEGMENTATION_URL.split('/')[-2]:
    #     raise RuntimeError(
    #         "Model has been downloaded but the SHA256 checksum does not not match. Please retry loading the model."
    #     )"""

        if old_code in content:
            print("[FIX] Verificação de checksum encontrada. Aplicando correção...")
            content = content.replace(old_code, new_code)

            # Salvar o arquivo corrigido
            with open(vad_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print("[FIX] ✅ Verificação de checksum desabilitada com sucesso!")
            return True
        else:
            print("[FIX] Verificação de checksum já está desabilitada ou código foi alterado.")
            return True

    except Exception as e:
        print(f"[ERRO] Falha ao aplicar correção: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("CORREÇÃO DO WHISPERX - DESABILITAR CHECKSUM VAD")
    print("=" * 70)
    print()

    success = fix_whisperx_checksum()

    print()
    if success:
        print("✅ Correção concluída!")
        print("Agora você pode executar: python src/UltraSinger.py --interactive")
        sys.exit(0)
    else:
        print("❌ Correção falhou!")
        sys.exit(1)
