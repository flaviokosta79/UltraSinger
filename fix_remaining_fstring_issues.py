#!/usr/bin/env python3
"""
Script para corrigir os problemas restantes de f-strings aninhadas
"""

import os
import re
from pathlib import Path

def fix_remaining_issues():
    """Corrige os problemas restantes de f-strings"""
    
    speechbrain_dir = Path("src/modules/SpeechBrain")
    
    # Correções específicas para cada arquivo
    fixes = {
        "conformer_asr.py": [
            # Linha 659
            ("print(f\"    {lang.upper()}: {blue_highlighted(f'{lang_stats['count']} files')} - RTF: {blue_highlighted(f'{rtf:.2f}x')}\")",
             "count_text = f\"{lang_stats['count']} files\"\n            rtf_text = f\"{rtf:.2f}x\"\n            print(f\"    {lang.upper()}: {blue_highlighted(count_text)} - RTF: {blue_highlighted(rtf_text)}\")"),
        ],
        
        "forced_alignment.py": [
            # Linhas similares
            ("print(f\"  Cache Hit Rate: {blue_highlighted(f'{stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%' if stats['cache_hits']+stats['cache_misses'] > 0 else '0%')}\")",
             "cache_rate = f\"{stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%\" if stats['cache_hits']+stats['cache_misses'] > 0 else '0%'\n        print(f\"  Cache Hit Rate: {blue_highlighted(cache_rate)}\")"),
            
            ("print(f\"    {lang.upper()}: {blue_highlighted(f'{lang_stats['count']} files')} - RTF: {blue_highlighted(f'{rtf:.2f}x')}\")",
             "count_text = f\"{lang_stats['count']} files\"\n            rtf_text = f\"{rtf:.2f}x\"\n            print(f\"    {lang.upper()}: {blue_highlighted(count_text)} - RTF: {blue_highlighted(rtf_text)}\")"),
        ],
        
        "vad_system.py": [
            ("print(f\"  Cache Hit Rate: {blue_highlighted(f'{stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%' if stats['cache_hits']+stats['cache_misses'] > 0 else '0%')}\")",
             "cache_rate = f\"{stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%\" if stats['cache_hits']+stats['cache_misses'] > 0 else '0%'\n        print(f\"  Cache Hit Rate: {blue_highlighted(cache_rate)}\")"),
        ],
        
        "speechbrain_integration.py": [
            ("print(f\"    Separations: {blue_highlighted(f'{stats['successful_separations']}/{stats['total_processed']}')}\"))",
             "separations_text = f\"{stats['successful_separations']}/{stats['total_processed']}\"\n        print(f\"    Separations: {blue_highlighted(separations_text)}\")"),
            
            ("print(f\"    Transcriptions: {blue_highlighted(f'{stats['successful_transcriptions']}/{stats['total_processed']}')}\"))",
             "transcriptions_text = f\"{stats['successful_transcriptions']}/{stats['total_processed']}\"\n        print(f\"    Transcriptions: {blue_highlighted(transcriptions_text)}\")"),
            
            ("print(f\"    Alignments: {blue_highlighted(f'{stats['successful_alignments']}/{stats['total_processed']}')}\"))",
             "alignments_text = f\"{stats['successful_alignments']}/{stats['total_processed']}\"\n        print(f\"    Alignments: {blue_highlighted(alignments_text)}\")"),
        ],
        
        "llm_rescoring.py": [
            ("print(f\"  Cache Hit Rate: {blue_highlighted(f'{stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%' if stats['cache_hits']+stats['cache_misses'] > 0 else '0%')}\")",
             "cache_rate = f\"{stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%\" if stats['cache_hits']+stats['cache_misses'] > 0 else '0%'\n        print(f\"  Cache Hit Rate: {blue_highlighted(cache_rate)}\")"),
        ]
    }
    
    fixed_count = 0
    
    for filename, file_fixes in fixes.items():
        file_path = speechbrain_dir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            for old, new in file_fixes:
                if old in content:
                    content = content.replace(old, new)
                    print(f"Fixed f-string issue in {filename}")
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
                print(f"✅ Corrigido: {filename}")
            else:
                print(f"ℹ️  Sem alterações: {filename}")
        else:
            print(f"❌ Arquivo não encontrado: {filename}")
    
    print(f"\n🎉 Correção concluída! {fixed_count} arquivos foram modificados.")

if __name__ == "__main__":
    fix_remaining_issues()