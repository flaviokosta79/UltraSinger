#!/usr/bin/env python3
"""
Script para corrigir problemas de f-strings aninhadas nos arquivos SpeechBrain
"""

import os
import re
from pathlib import Path

def fix_fstring_issues(file_path):
    """Corrige problemas de f-strings aninhadas em um arquivo"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Padrões problemáticos e suas correções
    patterns = [
        # Padrão: f'{stats['key']:.1f}s'
        (r"f'([^']*)\{([^}]*)\[([^]]+)\]([^}]*)\}([^']*)'", 
         lambda m: f"f'{m.group(1)}{{' + str({m.group(2)}[{m.group(3)}]{m.group(4)}) + '}}{m.group(5)}'"),
        
        # Padrão mais específico para nossos casos
        (r"blue_highlighted\(f'\{([^}]*)\[([^]]+)\]([^}]*)\}'\)", 
         lambda m: f"blue_highlighted(str({m.group(1)}[{m.group(2)}]{m.group(3)}))"),
    ]
    
    # Aplicar correções específicas conhecidas
    fixes = [
        # sepformer_separation.py
        ("print(f\"  Average Time: {blue_highlighted(f'{stats['average_time']:.1f}s')}\")",
         "avg_time_text = f\"{stats['average_time']:.1f}s\"\n        print(f\"  Average Time: {blue_highlighted(avg_time_text)}\")"),
        
        ("print(f\"  Cache Hit Rate: {blue_highlighted(f'{stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%' if stats['cache_hits']+stats['cache_misses'] > 0 else '0%')}\")",
         "cache_rate = f\"{stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%\" if stats['cache_hits']+stats['cache_misses'] > 0 else '0%'\n        print(f\"  Cache Hit Rate: {blue_highlighted(cache_rate)}\")"),
        
        ("print(f\"  Total Processing Time: {blue_highlighted(f'{stats['total_time']:.1f}s')}\")",
         "total_time_text = f\"{stats['total_time']:.1f}s\"\n        print(f\"  Total Processing Time: {blue_highlighted(total_time_text)}\")"),
        
        # conformer_asr.py
        ("print(f\"{ULTRASINGER_HEAD} Expected WER: {blue_highlighted(f'{model_info['wer']:.1f}%')}\")",
         "wer_text = f\"{model_info['wer']:.1f}%\"\n        print(f\"{ULTRASINGER_HEAD} Expected WER: {blue_highlighted(wer_text)}\")"),
        
        # forced_alignment.py
        ("print(f\"  Average Time: {blue_highlighted(f'{stats['average_time']:.1f}s')}\")",
         "avg_time_text = f\"{stats['average_time']:.1f}s\"\n        print(f\"  Average Time: {blue_highlighted(avg_time_text)}\")"),
        
        ("print(f\"  Real-time Factor: {blue_highlighted(f'{stats['real_time_factor']:.2f}x')}\")",
         "rtf_text = f\"{stats['real_time_factor']:.2f}x\"\n        print(f\"  Real-time Factor: {blue_highlighted(rtf_text)}\")"),
        
        # vad_system.py
        ("print(f\"  Average Time: {blue_highlighted(f'{stats['average_time']:.1f}s')}\")",
         "avg_time_text = f\"{stats['average_time']:.1f}s\"\n        print(f\"  Average Time: {blue_highlighted(avg_time_text)}\")"),
        
        ("print(f\"  Real-time Factor: {blue_highlighted(f'{stats['real_time_factor']:.2f}x')}\")",
         "rtf_text = f\"{stats['real_time_factor']:.2f}x\"\n        print(f\"  Real-time Factor: {blue_highlighted(rtf_text)}\")"),
        
        # speechbrain_integration.py
        ("print(f\"{ULTRASINGER_HEAD} Total time: {blue_highlighted(f'{results['processing_time']:.1f}s')}\")",
         "total_time_text = f\"{results['processing_time']:.1f}s\"\n        print(f\"{ULTRASINGER_HEAD} Total time: {blue_highlighted(total_time_text)}\")"),
        
        ("print(f\"  Average Time: {blue_highlighted(f'{stats['average_time']:.1f}s')}\")",
         "avg_time_text = f\"{stats['average_time']:.1f}s\"\n        print(f\"  Average Time: {blue_highlighted(avg_time_text)}\")"),
        
        # llm_rescoring.py
        ("print(f\"  Average Time: {blue_highlighted(f'{stats['average_time']:.1f}s')}\")",
         "avg_time_text = f\"{stats['average_time']:.1f}s\"\n        print(f\"  Average Time: {blue_highlighted(avg_time_text)}\")"),
        
        ("print(f\"  Improvement Rate: {blue_highlighted(f'{stats['improvement_rate']:.1%}')}\")",
         "improvement_text = f\"{stats['improvement_rate']:.1%}\"\n        print(f\"  Improvement Rate: {blue_highlighted(improvement_text)}\")"),
    ]
    
    # Aplicar correções
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            print(f"Fixed f-string issue in {file_path}")
    
    # Salvar se houve mudanças
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Função principal"""
    speechbrain_dir = Path("src/modules/SpeechBrain")
    
    if not speechbrain_dir.exists():
        print("Diretório SpeechBrain não encontrado!")
        return
    
    files_to_fix = [
        "sepformer_separation.py",
        "conformer_asr.py", 
        "forced_alignment.py",
        "vad_system.py",
        "speechbrain_integration.py",
        "llm_rescoring.py"
    ]
    
    fixed_count = 0
    
    for filename in files_to_fix:
        file_path = speechbrain_dir / filename
        if file_path.exists():
            if fix_fstring_issues(file_path):
                fixed_count += 1
                print(f"✅ Corrigido: {filename}")
            else:
                print(f"ℹ️  Sem alterações: {filename}")
        else:
            print(f"❌ Arquivo não encontrado: {filename}")
    
    print(f"\n🎉 Correção concluída! {fixed_count} arquivos foram modificados.")

if __name__ == "__main__":
    main()