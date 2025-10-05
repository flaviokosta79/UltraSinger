"""
Script para corrigir o problema de URL do modelo VAD no WhisperX
Corrige o erro HTTP 301: Moved Permanently
"""
import os
import sys

def fix_whisperx_vad():
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

        # URL antiga (causando erro 301)
        old_url = 'https://whisperx.s3.eu-west-2.amazonaws.com/model_weights/segmentation/0b5b3216d60a2d32fc086b47ea8c67589aaeb26b7e07fcbe620d6d0b83e209ea/pytorch_model.bin'

        # Nova URL corrigida (Hugging Face mirror)
        new_url = 'https://huggingface.co/thomasmol/whisperx-vad/resolve/main/pytorch_model.bin'

        if old_url in content:
            print("[FIX] URL antiga encontrada. Aplicando correção...")
            content = content.replace(old_url, new_url)

            # Fazer backup do arquivo original
            backup_file = vad_file + '.backup'
            if not os.path.exists(backup_file):
                with open(backup_file, 'w', encoding='utf-8') as f:
                    with open(vad_file, 'r', encoding='utf-8') as orig:
                        f.write(orig.read())
                print(f"[FIX] Backup criado: {backup_file}")

            # Salvar o arquivo corrigido
            with open(vad_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print("[FIX] ✅ Correção aplicada com sucesso!")
            print(f"[FIX] URL antiga: {old_url}")
            print(f"[FIX] URL nova: {new_url}")
            return True
        else:
            print("[FIX] URL já está atualizada ou não foi encontrada.")
            return True

    except Exception as e:
        print(f"[ERRO] Falha ao aplicar correção: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("CORREÇÃO DO WHISPERX - ERRO HTTP 301 NO MODELO VAD")
    print("=" * 70)
    print()

    success = fix_whisperx_vad()

    print()
    if success:
        print("✅ Correção concluída!")
        print("Execute novamente: python src/UltraSinger.py --interactive")
        sys.exit(0)
    else:
        print("❌ Correção falhou!")
        print("Tente reinstalar o WhisperX: pip install --force-reinstall whisperx==3.4.3")
        sys.exit(1)
