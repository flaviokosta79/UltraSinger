"""
Script de debug para testar correção de letras
"""

from difflib import SequenceMatcher

# Caso de teste: "janela e monê" -> "Janelle Monáe"
transcribed = ["janela", "e", "monê"]
reference = ["Janelle", "Monáe"]

print("=" * 60)
print("TESTE DE CORREÇÃO - Debug")
print("=" * 60)
print(f"\nTranscrição: {transcribed}")
print(f"Referência:  {reference}")
print()

# Criar matcher
matcher = SequenceMatcher(
    None,
    [w.lower() for w in transcribed],
    [w.lower() for w in reference]
)

print("Opcodes gerados pelo SequenceMatcher:")
print("-" * 60)

for tag, i1, i2, j1, j2 in matcher.get_opcodes():
    trans_slice = transcribed[i1:i2]
    ref_slice = reference[j1:j2]
    
    print(f"\n{tag:10} | Trans[{i1}:{i2}] = {trans_slice}")
    print(f"           | Ref  [{j1}:{j2}] = {ref_slice}")
    
    if tag == 'replace':
        print("           | ✓ CORREÇÃO DETECTADA")
    elif tag == 'equal':
        print("           | = Iguais (nenhuma ação)")
    elif tag == 'delete':
        print("           | - Remover da transcrição")
    elif tag == 'insert':
        print("           | + Adicionar da referência")

print("\n" + "=" * 60)
print("RESULTADO ESPERADO:")
print("=" * 60)
print(f"Corrigido: {reference}")
print()

# Teste com texto completo
print("\n" + "=" * 60)
print("TESTE 2: Contexto completo")
print("=" * 60)

full_trans = "Eu e você ao som de janela e monê Vem"
full_ref = "Eu e você ao som de Janelle Monáe Vem"

print(f"\nTranscrição: '{full_trans}'")
print(f"Referência:  '{full_ref}'")
print()

matcher2 = SequenceMatcher(None, full_trans.lower(), full_ref.lower())

print("Opcodes (nível de caractere):")
print("-" * 60)

for tag, i1, i2, j1, j2 in matcher2.get_opcodes():
    trans_part = full_trans[i1:i2]
    ref_part = full_ref[j1:j2]
    
    print(f"\n{tag:10} | Trans[{i1:3}:{i2:3}] = '{trans_part}'")
    print(f"           | Ref  [{j1:3}:{j2:3}] = '{ref_part}'")
    
    if tag == 'replace':
        print(f"           | ✓ CORREÇÃO: '{trans_part}' -> '{ref_part}'")

print("\n" + "=" * 60)
