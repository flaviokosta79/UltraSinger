"""
Teste dos 3 modos de correção LRCLib com música real
Música: Pollo - Vagalumes
"""

import sys
import os
from pathlib import Path

# Configurar paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Música de teste
AUDIO_FILE = r"E:\VSCode\Projects\UltraSinger\output\Pollo - Vagalumes\Pollo - Vagalumes.mp3"

# Verificar se arquivo existe
if not os.path.exists(AUDIO_FILE):
    print(f"❌ Arquivo não encontrado: {AUDIO_FILE}")
    sys.exit(1)

print("=" * 80)
print("TESTE DOS 3 MODOS DE CORREÇÃO LRCLIB - MÚSICA REAL")
print("=" * 80)
print(f"\n🎵 Música: {os.path.basename(AUDIO_FILE)}")
print(f"📁 Caminho: {AUDIO_FILE}")

# Configurações para cada modo
test_configs = [
    {
        'mode': 'correction',
        'name': 'CORRECTION',
        'output': 'output_test_mode_correction',
        'description': 'Correção palavra por palavra (PADRÃO)'
    },
    {
        'mode': 'hybrid',
        'name': 'HYBRID',
        'output': 'output_test_mode_hybrid',
        'description': 'Híbrido - estrutura WhisperX + letra LRCLib'
    },
    {
        'mode': 'sync',
        'name': 'SYNC',
        'output': 'output_test_mode_sync',
        'description': 'Sincronização pura - 100% LRCLib'
    }
]

print("\n" + "=" * 80)
print("CONFIGURAÇÃO DOS TESTES")
print("=" * 80)

for i, config in enumerate(test_configs, 1):
    print(f"\n{i}. Modo {config['name']}:")
    print(f"   Descrição: {config['description']}")
    print(f"   Output: {config['output']}/")

print("\n" + "=" * 80)
print("INICIANDO TESTES")
print("=" * 80)

import subprocess

for i, config in enumerate(test_configs, 1):
    print(f"\n{'='*80}")
    print(f"TESTE {i}/3: MODO {config['name']}")
    print(f"{'='*80}")
    
    # Montar comando
    cmd = [
        'python',
        'src/UltraSinger.py',
        '-i', AUDIO_FILE,
        '-o', config['output'],
        '--lrclib',
        '--language', 'pt',
        '--disable_hyphenation'
    ]
    
    # Configurar variável de ambiente para o modo
    env = os.environ.copy()
    env['LRCLIB_MODE'] = config['mode']
    
    print(f"\n📝 Comando: {' '.join(cmd)}")
    print(f"🔧 Variável: LRCLIB_MODE={config['mode']}")
    print(f"⏱️  Aguarde... (pode demorar alguns minutos)")
    print("-" * 80)
    
    # Executar
    try:
        result = subprocess.run(
            cmd,
            capture_output=False,  # Mostrar output em tempo real
            text=True,
            cwd=PROJECT_ROOT,
            env=env  # ✅ Passar variável de ambiente
        )
        
        if result.returncode == 0:
            print(f"\n✅ Teste {config['name']} concluído com sucesso!")
        else:
            print(f"\n⚠️  Teste {config['name']} terminou com código {result.returncode}")
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Teste {config['name']} interrompido pelo usuário")
        break
    except Exception as e:
        print(f"\n❌ Erro no teste {config['name']}: {e}")
        continue

print("\n" + "=" * 80)
print("ANÁLISE DOS RESULTADOS")
print("=" * 80)

# Verificar arquivos gerados
resultados = []

for config in test_configs:
    txt_file = os.path.join(
        PROJECT_ROOT,
        config['output'],
        "Pollo - Vagalumes",
        "Pollo - Vagalumes.txt"
    )
    
    if os.path.exists(txt_file):
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar se "Janelle Monáe" foi corrigido
        has_janelle = 'Janelle' in content
        has_monae = 'Monáe' in content or 'Monae' in content
        has_janela = 'janela' in content.lower() and 'janelle' not in content.lower()
        
        # Contar linhas
        num_lines = content.count('\n: ')
        
        # Extrair score
        score_line = [l for l in content.split('\n') if '#COMMENT:' in l]
        score = score_line[0].split('Score:')[1].strip() if score_line else "N/A"
        
        resultados.append({
            'mode': config['name'],
            'file_size': os.path.getsize(txt_file),
            'num_lines': num_lines,
            'has_janelle': has_janelle,
            'has_monae': has_monae,
            'has_error': has_janela,
            'score': score,
            'path': txt_file
        })
        
        print(f"\n📄 {config['name']}:")
        print(f"   Arquivo: {os.path.basename(txt_file)}")
        print(f"   Tamanho: {os.path.getsize(txt_file)} bytes")
        print(f"   Linhas: {num_lines}")
        print(f"   Score: {score}")
        print(f"   Janelle: {'✅' if has_janelle else '❌'}")
        print(f"   Monáe: {'✅' if has_monae else '❌'}")
        print(f"   Erro 'janela': {'❌ SIM' if has_janela else '✅ NÃO'}")
    else:
        print(f"\n❌ {config['name']}: Arquivo não encontrado")

# Comparação final
if resultados:
    print("\n" + "=" * 80)
    print("COMPARAÇÃO FINAL")
    print("=" * 80)
    
    print("\n🎯 Correção 'Janelle Monáe':")
    print("-" * 80)
    print(f"{'Modo':<15} {'Janelle':<10} {'Monáe':<10} {'Sem Erro':<12} {'Status'}")
    print("-" * 80)
    
    for r in resultados:
        janelle = "✅" if r['has_janelle'] else "❌"
        monae = "✅" if r['has_monae'] else "❌"
        no_error = "✅" if not r['has_error'] else "❌"
        
        if r['has_janelle'] and r['has_monae'] and not r['has_error']:
            status = "🏆 PERFEITO"
        elif r['has_janelle'] or r['has_monae']:
            status = "⚠️  PARCIAL"
        else:
            status = "❌ FALHOU"
        
        print(f"{r['mode']:<15} {janelle:<10} {monae:<10} {no_error:<12} {status}")
    
    print("\n📊 Estatísticas:")
    print("-" * 80)
    print(f"{'Modo':<15} {'Linhas':<10} {'Tamanho':<15} {'Score'}")
    print("-" * 80)
    
    for r in resultados:
        print(f"{r['mode']:<15} {r['num_lines']:<10} {r['file_size']:<15} {r['score']}")
    
    print("\n💡 RECOMENDAÇÃO:")
    print("-" * 80)
    
    # Encontrar melhor resultado
    melhores = [r for r in resultados if r['has_janelle'] and r['has_monae'] and not r['has_error']]
    
    if melhores:
        melhor = max(melhores, key=lambda x: x['num_lines'])
        print(f"🏆 Modo recomendado: {melhor['mode']}")
        print(f"   ✅ Corrigiu 'Janelle Monáe' perfeitamente")
        print(f"   ✅ {melhor['num_lines']} linhas geradas")
        print(f"   ✅ Score: {melhor['score']}")
        print(f"\n📁 Arquivo: {melhor['path']}")
    else:
        print("⚠️  Nenhum modo corrigiu perfeitamente o erro")

print("\n" + "=" * 80)
print("TESTE CONCLUÍDO")
print("=" * 80)
