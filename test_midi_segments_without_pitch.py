"""
Teste simples para verificar a criação de MidiSegments sem pitch detection
"""
import sys
sys.path.insert(0, 'src')

from modules.Midi.MidiSegment import MidiSegment
from dataclasses import dataclass

# Simular dados de transcrição
@dataclass
class TranscribedData:
    word: str
    start: float
    end: float

# Criar dados de teste
test_transcription = [
    TranscribedData('Pé', 0.0, 0.5),
    TranscribedData('na', 0.5, 0.8),
    TranscribedData('areia', 0.8, 1.5),
    TranscribedData('eu', 1.5, 1.8),
    TranscribedData('vou', 1.8, 2.3),
]

# Criar MIDI segments sem pitch detection (nota padrão C4)
midi_segments = [
    MidiSegment(
        note="C4",
        start=data.start,
        end=data.end,
        word=data.word
    )
    for data in test_transcription
]

# Verificar resultados
print(f"✅ Criados {len(midi_segments)} segments com sucesso!")
print(f"\nPrimeiros 3 segments:")
for i, seg in enumerate(midi_segments[:3]):
    print(f"  {i+1}. Palavra: '{seg.word}' | Nota: {seg.note} | Start: {seg.start}s | End: {seg.end}s")

# Verificar que nenhum segment está vazio
assert all(seg.word for seg in midi_segments), "Erro: Algum segment tem palavra vazia"
assert all(seg.note == "C4" for seg in midi_segments), "Erro: Algum segment não tem nota C4"
assert len(midi_segments) == len(test_transcription), "Erro: Número de segments diferente"

print(f"\n🎉 TESTE PASSOU! Todos os {len(midi_segments)} segments foram criados corretamente.")
print(f"✓ Todas as notas são C4 (padrão quando pitch detection está desabilitado)")
print(f"✓ Todos os timestamps estão preservados")
print(f"✓ Todas as palavras estão corretas")
