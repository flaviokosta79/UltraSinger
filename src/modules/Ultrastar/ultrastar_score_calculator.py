"""Ultrastar score calculator - Enhanced with comprehensive scoring system."""
import os
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from pathlib import Path

from dataclasses_json import dataclass_json

import librosa
import numpy as np

from modules.ProcessData import ProcessData
from modules.Ultrastar import ultrastar_parser

from modules.console_colors import (
    ULTRASINGER_HEAD,
    blue_highlighted,
    cyan_highlighted,
    gold_highlighted,
    light_blue_highlighted,
    underlined,
    green_highlighted,
    red_highlighted,
    yellow_highlighted,
)
from modules.Midi.midi_creator import create_midi_note_from_pitched_data
from modules.Ultrastar.coverter.ultrastar_converter import (
    get_end_time_from_ultrastar,
    get_start_time_from_ultrastar,
    ultrastar_note_to_midi_note,
)
from modules.Ultrastar.ultrastar_txt import UltrastarTxtValue, UltrastarTxtNoteTypeTag
from modules.Pitcher.pitched_data import PitchedData

MAX_SONG_SCORE = 10000
MAX_SONG_LINE_BONUS = 1000


@dataclass_json
@dataclass
class Points:
    """Enhanced points tracking with detailed metrics"""
    notes: int = 0
    golden_notes: int = 0
    rap: int = 0
    golden_rap: int = 0
    line_bonus: int = 0
    parts: int = 0
    
    # Enhanced metrics
    perfect_notes: int = 0
    good_notes: int = 0
    missed_notes: int = 0
    timing_accuracy: float = 0.0
    pitch_accuracy: float = 0.0
    total_duration: float = 0.0
    
    def get_total_notes(self) -> int:
        """Get total number of notes"""
        return self.notes + self.golden_notes + self.rap + self.golden_rap
    
    def get_accuracy_percentage(self) -> float:
        """Get overall accuracy percentage"""
        total = self.get_total_notes()
        if total == 0:
            return 0.0
        return ((self.perfect_notes + self.good_notes) / total) * 100
    
    def get_performance_grade(self) -> str:
        """Get performance grade based on accuracy"""
        accuracy = self.get_accuracy_percentage()
        if accuracy >= 95:
            return "S+"
        elif accuracy >= 90:
            return "S"
        elif accuracy >= 85:
            return "A+"
        elif accuracy >= 80:
            return "A"
        elif accuracy >= 75:
            return "B+"
        elif accuracy >= 70:
            return "B"
        elif accuracy >= 65:
            return "C+"
        elif accuracy >= 60:
            return "C"
        else:
            return "D"


class UltrastarScoreCalculator:
    """Enhanced UltraStar score calculator with comprehensive analysis"""
    
    def __init__(self, cache_folder: Optional[str] = None):
        """Initialize score calculator with cache support"""
        self.cache_folder = cache_folder or os.path.join(os.getcwd(), "cache", "scores")
        self._ensure_cache_folder()
    
    def _ensure_cache_folder(self):
        """Ensure cache folder exists"""
        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder, exist_ok=True)
    
    def calculate_pitch_accuracy(self, target_note: str, sung_note: str, tolerance: float = 0.5) -> Tuple[bool, float]:
        """Calculate pitch accuracy with tolerance"""
        try:
            target_midi = librosa.note_to_midi(target_note)
            sung_midi = librosa.note_to_midi(sung_note)
            
            difference = abs(target_midi - sung_midi)
            accuracy = max(0, 1 - (difference / 12))  # 12 semitones = 1 octave
            
            is_accurate = difference <= tolerance
            return is_accurate, accuracy
            
        except Exception:
            return False, 0.0
    
    def calculate_timing_accuracy(self, expected_start: float, expected_end: float, 
                                actual_start: float, actual_end: float) -> float:
        """Calculate timing accuracy"""
        expected_duration = expected_end - expected_start
        actual_duration = actual_end - actual_start
        
        start_diff = abs(expected_start - actual_start)
        end_diff = abs(expected_end - actual_end)
        duration_diff = abs(expected_duration - actual_duration)
        
        # Normalize timing differences
        timing_score = max(0, 1 - ((start_diff + end_diff + duration_diff) / expected_duration))
        return timing_score
    
    def analyze_performance_consistency(self, accuracies: List[float]) -> float:
        """Analyze performance consistency"""
        if not accuracies:
            return 0.0
        
        mean_accuracy = np.mean(accuracies)
        std_accuracy = np.std(accuracies)
        
        # Lower standard deviation = higher consistency
        consistency = max(0, 1 - (std_accuracy / mean_accuracy)) if mean_accuracy > 0 else 0
        return consistency
    
    def save_score_analysis(self, score_data: Dict[str, Any], song_name: str):
        """Save score analysis to cache"""
        try:
            analysis_file = os.path.join(self.cache_folder, "score_history.json")
            
            # Load existing analyses
            analyses = []
            if os.path.exists(analysis_file):
                try:
                    with open(analysis_file, 'r', encoding='utf-8') as f:
                        analyses = json.load(f)
                except:
                    analyses = []
            
            # Add new analysis
            new_analysis = {
                "timestamp": datetime.now().isoformat(),
                "song_name": song_name,
                "score_data": score_data
            }
            
            analyses.append(new_analysis)
            
            # Keep only last 100 analyses
            if len(analyses) > 100:
                analyses = analyses[-100:]
            
            # Save analyses
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analyses, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"{yellow_highlighted(f'Aviso: Não foi possível salvar análise: {str(e)}')}")
    
    def calculate_song_score(self, notes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate song score from notes data"""
        if not notes:
            return {
                'total_score': 0,
                'max_score': 0,
                'accuracy': 0.0,
                'grade': 'D',
                'note_count': 0
            }
        
        total_notes = len(notes)
        scored_notes = 0
        total_score = 0
        max_possible_score = 0
        
        for note in notes:
            if note.get('type') == ':':  # Normal note
                max_possible_score += 1
                # Simulate scoring based on note properties
                if 'pitch' in note and 'text' in note:
                    total_score += 1
                    scored_notes += 1
            elif note.get('type') == '*':  # Golden note
                max_possible_score += 2
                if 'pitch' in note and 'text' in note:
                    total_score += 2
                    scored_notes += 1
        
        accuracy = (scored_notes / total_notes * 100) if total_notes > 0 else 0
        
        # Determine grade
        if accuracy >= 95:
            grade = "S+"
        elif accuracy >= 90:
            grade = "S"
        elif accuracy >= 85:
            grade = "A+"
        elif accuracy >= 80:
            grade = "A"
        elif accuracy >= 75:
            grade = "B+"
        elif accuracy >= 70:
            grade = "B"
        elif accuracy >= 65:
            grade = "C+"
        elif accuracy >= 60:
            grade = "C"
        else:
            grade = "D"
        
        return {
            'total_score': total_score,
            'max_score': max_possible_score,
            'accuracy': accuracy,
            'grade': grade,
            'note_count': total_notes,
            'scored_notes': scored_notes
        }


def add_point(note_type: str, points: Points, accuracy: float = 1.0, timing: float = 1.0) -> Points:
    """Add calculated points to the points object with enhanced metrics."""
    
    # Determine hit quality based on accuracy and timing
    combined_quality = (accuracy + timing) / 2
    
    if combined_quality >= 0.9:
        points.perfect_notes += 1
    elif combined_quality >= 0.7:
        points.good_notes += 1
    else:
        points.missed_notes += 1
    
    # Add traditional points
    if note_type == UltrastarTxtNoteTypeTag.NORMAL:
        points.notes += int(accuracy)
    elif note_type == UltrastarTxtNoteTypeTag.GOLDEN:
        points.golden_notes += int(2 * accuracy)
    elif note_type == UltrastarTxtNoteTypeTag.RAP:
        points.rap += int(accuracy)
    elif note_type == UltrastarTxtNoteTypeTag.RAP_GOLDEN:
        points.golden_rap += int(2 * accuracy)
    
    # Update accuracy metrics
    points.pitch_accuracy += accuracy
    points.timing_accuracy += timing
    
    return points


@dataclass_json
@dataclass
class Score:
    """Enhanced score with detailed breakdown and analysis"""
    max_score: int = 0
    notes: int = 0
    golden: int = 0
    line_bonus: int = 0
    score: int = 0
    
    # Enhanced metrics
    accuracy_percentage: float = 0.0
    performance_grade: str = "D"
    timing_score: int = 0
    pitch_score: int = 0
    consistency_score: int = 0
    difficulty_multiplier: float = 1.0
    
    # Detailed breakdown
    perfect_hits: int = 0
    good_hits: int = 0
    missed_hits: int = 0
    total_notes_sung: int = 0
    
    def get_score_breakdown(self) -> Dict[str, Any]:
        """Get detailed score breakdown"""
        return {
            "total_score": self.score,
            "max_possible": self.max_score,
            "percentage": (self.score / self.max_score * 100) if self.max_score > 0 else 0,
            "grade": self.performance_grade,
            "components": {
                "notes": self.notes,
                "golden_bonus": self.golden,
                "line_bonus": self.line_bonus,
                "timing": self.timing_score,
                "pitch": self.pitch_score,
                "consistency": self.consistency_score
            },
            "accuracy": {
                "perfect": self.perfect_hits,
                "good": self.good_hits,
                "missed": self.missed_hits,
                "total": self.total_notes_sung,
                "percentage": self.accuracy_percentage
            }
        }


def get_score(points: Points) -> Score:
    """Enhanced score calculation with detailed analysis."""
    
    score = Score()
    
    # Calculate max score
    score.max_score = (
        MAX_SONG_SCORE
        if points.line_bonus == 0
        else MAX_SONG_SCORE - MAX_SONG_LINE_BONUS
    )
    
    # Calculate component scores
    score.notes = round(
        score.max_score * (points.notes + points.rap) / points.parts
    ) if points.parts > 0 else 0
    
    score.golden = round(points.golden_notes + points.golden_rap)
    score.line_bonus = round(points.line_bonus)
    
    # Calculate enhanced metrics
    total_notes = points.get_total_notes()
    if total_notes > 0:
        score.accuracy_percentage = points.get_accuracy_percentage()
        score.performance_grade = points.get_performance_grade()
        
        # Calculate timing and pitch scores
        score.timing_score = round((points.timing_accuracy / points.parts) * 1000) if points.parts > 0 else 0
        score.pitch_score = round((points.pitch_accuracy / points.parts) * 1000) if points.parts > 0 else 0
        
        # Calculate consistency score
        consistency = 1.0  # Default high consistency
        if points.parts > 1:
            # Simple consistency calculation based on perfect vs good notes ratio
            perfect_ratio = points.perfect_notes / total_notes
            consistency = perfect_ratio
        score.consistency_score = round(consistency * 500)
        
        # Set detailed breakdown
        score.perfect_hits = points.perfect_notes
        score.good_hits = points.good_notes
        score.missed_hits = points.missed_notes
        score.total_notes_sung = total_notes
    
    # Calculate final score
    score.score = round(
        score.notes + 
        score.line_bonus + 
        score.golden + 
        (score.timing_score * 0.1) + 
        (score.pitch_score * 0.1) + 
        (score.consistency_score * 0.05)
    )
    
    return score


def print_score(score: Score) -> None:
    """Print enhanced score with detailed breakdown."""
    
    print(f"{ULTRASINGER_HEAD} {green_highlighted('=== PONTUAÇÃO ULTRASTAR ===')}")
    print(f"{ULTRASINGER_HEAD} Total: {cyan_highlighted(str(score.score))} / {score.max_score}")
    print(f"{ULTRASINGER_HEAD} Nota: {gold_highlighted(score.performance_grade)} ({score.accuracy_percentage:.1f}%)")
    
    print(f"{ULTRASINGER_HEAD} {blue_highlighted('Componentes:')}")
    print(f"  • Notas: {blue_highlighted(str(score.notes))}")
    print(f"  • Bônus de linha: {light_blue_highlighted(str(score.line_bonus))}")
    print(f"  • Notas douradas: {gold_highlighted(str(score.golden))}")
    print(f"  • Timing: {blue_highlighted(str(score.timing_score))}")
    print(f"  • Afinação: {blue_highlighted(str(score.pitch_score))}")
    print(f"  • Consistência: {blue_highlighted(str(score.consistency_score))}")
    
    print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Precisão:')}")
    print(f"  • Perfeitas: {green_highlighted(str(score.perfect_hits))}")
    print(f"  • Boas: {blue_highlighted(str(score.good_hits))}")
    print(f"  • Perdidas: {red_highlighted(str(score.missed_hits))}")
    print(f"  • Total cantadas: {cyan_highlighted(str(score.total_notes_sung))}")


def print_detailed_score_analysis(score: Score) -> None:
    """Print detailed score analysis"""
    
    breakdown = score.get_score_breakdown()
    
    print(f"{ULTRASINGER_HEAD} {green_highlighted('=== ANÁLISE DETALHADA ===')}")
    print(f"Pontuação final: {cyan_highlighted(str(breakdown['total_score']))} ({breakdown['percentage']:.1f}%)")
    print(f"Nota de performance: {gold_highlighted(breakdown['grade'])}")
    
    print(f"\n{blue_highlighted('Componentes da pontuação:')}")
    for component, value in breakdown['components'].items():
        print(f"  • {component.capitalize()}: {value}")
    
    print(f"\n{yellow_highlighted('Análise de precisão:')}")
    accuracy = breakdown['accuracy']
    print(f"  • Acertos perfeitos: {green_highlighted(str(accuracy['perfect']))}")
    print(f"  • Acertos bons: {blue_highlighted(str(accuracy['good']))}")
    print(f"  • Erros: {red_highlighted(str(accuracy['missed']))}")
    accuracy_text = f"{accuracy['percentage']:.1f}%"
    print(f"  • Precisão geral: {cyan_highlighted(accuracy_text)}")
    
    # Performance tips
    if accuracy['percentage'] < 70:
        print(f"\n{yellow_highlighted('💡 Dicas para melhorar:')}")
        print("  • Pratique a afinação das notas")
        print("  • Trabalhe no timing das entradas")
        print("  • Mantenha consistência durante a música")
    elif accuracy['percentage'] >= 90:
        print(f"\n{green_highlighted('🎉 Excelente performance!')}")
        print("  • Sua afinação está muito boa!")
        print("  • Continue praticando para manter a consistência")


def calculate_score(pitched_data: PitchedData, ultrastar_class: UltrastarTxtValue) -> Tuple[Score, Score]:
    """Enhanced score calculation with detailed analysis."""

    print(f"{ULTRASINGER_HEAD} {blue_highlighted('Calculando pontuação UltraStar...')}")

    # Initialize enhanced calculator
    calculator = UltrastarScoreCalculator()
    
    simple_points = Points()
    accurate_points = Points()
    
    # Track accuracies for consistency analysis
    simple_accuracies = []
    accurate_accuracies = []

    reachable_line_bonus_per_word = MAX_SONG_LINE_BONUS / len(ultrastar_class.UltrastarNoteLines)
    step_size = 0.09  # Todo: What is the step size of the game? Its not 1/bps -> one beat in seconds s = 60/bpm

    total_notes = len([line for line in ultrastar_class.UltrastarNoteLines 
                      if line.word != "" and line.noteType != UltrastarTxtNoteTypeTag.FREESTYLE])
    
    print(f"{ULTRASINGER_HEAD} Analisando {total_notes} notas...")

    for i, note_line in enumerate(ultrastar_class.UltrastarNoteLines):
        if note_line.word == "":
            continue

        if note_line.noteType == UltrastarTxtNoteTypeTag.FREESTYLE:
            continue

        start_time = get_start_time_from_ultrastar(ultrastar_class, i)
        end_time = get_end_time_from_ultrastar(ultrastar_class, i)
        duration = end_time - start_time
        parts = int(duration / step_size)
        parts = 1 if parts == 0 else parts

        accurate_part_line_bonus_points = 0
        simple_part_line_bonus_points = 0

        ultrastar_midi_note = ultrastar_note_to_midi_note(int(note_line.pitch))
        ultrastar_note = librosa.midi_to_note(ultrastar_midi_note)

        # Track timing and pitch accuracies for this note
        note_timing_accuracies = []
        note_pitch_accuracies = []

        for part in range(parts):
            start = start_time + step_size * part
            end = start + step_size

            if end_time < end or part == parts - 1:
                end = end_time

            midi_segment = create_midi_note_from_pitched_data(start, end, pitched_data, note_line.word)

            # Calculate timing accuracy
            timing_accuracy = calculator.calculate_timing_accuracy(
                start_time, end_time, start, end
            )
            note_timing_accuracies.append(timing_accuracy)

            # Simple scoring (ignore octave)
            simple_match = midi_segment.note[:-1] == ultrastar_note[:-1]
            if simple_match:
                # Calculate pitch accuracy for simple match
                is_accurate, pitch_accuracy = calculator.calculate_pitch_accuracy(
                    ultrastar_note[:-1] + "4",  # Normalize octave
                    midi_segment.note[:-1] + "4"
                )
                note_pitch_accuracies.append(pitch_accuracy)
                simple_points = add_point(note_line.noteType, simple_points, pitch_accuracy, timing_accuracy)
                simple_part_line_bonus_points += 1
            else:
                note_pitch_accuracies.append(0.0)
                simple_points = add_point(note_line.noteType, simple_points, 0.0, timing_accuracy)

            # Accurate scoring (exact match including octave)
            accurate_match = midi_segment.note == ultrastar_note
            if accurate_match:
                is_accurate, pitch_accuracy = calculator.calculate_pitch_accuracy(
                    ultrastar_note, midi_segment.note
                )
                accurate_points = add_point(note_line.noteType, accurate_points, pitch_accuracy, timing_accuracy)
                accurate_part_line_bonus_points += 1
            else:
                is_accurate, pitch_accuracy = calculator.calculate_pitch_accuracy(
                    ultrastar_note, midi_segment.note
                )
                accurate_points = add_point(note_line.noteType, accurate_points, pitch_accuracy, timing_accuracy)

            accurate_points.parts += 1
            simple_points.parts += 1

        # Calculate average accuracies for this note
        avg_timing = np.mean(note_timing_accuracies) if note_timing_accuracies else 0.0
        avg_pitch_simple = np.mean(note_pitch_accuracies) if note_pitch_accuracies else 0.0
        
        simple_accuracies.append((avg_timing + avg_pitch_simple) / 2)
        accurate_accuracies.append(avg_timing)  # For accurate, timing is more important

        # Line bonus calculation
        if accurate_part_line_bonus_points >= parts:
            accurate_points.line_bonus += reachable_line_bonus_per_word

        if simple_part_line_bonus_points >= parts:
            simple_points.line_bonus += reachable_line_bonus_per_word

        # Update total duration
        simple_points.total_duration += duration
        accurate_points.total_duration += duration

    # Calculate final averages
    if simple_points.parts > 0:
        simple_points.pitch_accuracy /= simple_points.parts
        simple_points.timing_accuracy /= simple_points.parts
        
    if accurate_points.parts > 0:
        accurate_points.pitch_accuracy /= accurate_points.parts
        accurate_points.timing_accuracy /= accurate_points.parts

    print(f"{ULTRASINGER_HEAD} {green_highlighted('Cálculo de pontuação concluído!')}")
    
    return get_score(simple_points), get_score(accurate_points)


def print_score_calculation(simple_points: Score, accurate_points: Score) -> None:
    """Print enhanced score calculation with detailed analysis."""

    print(f"\n{ULTRASINGER_HEAD} {underlined(green_highlighted('PONTUAÇÃO SIMPLES (oitava ignorada)'))}")
    print_score(simple_points)
    print_detailed_score_analysis(simple_points)

    print(f"\n{ULTRASINGER_HEAD} {underlined(gold_highlighted('PONTUAÇÃO PRECISA (oitava exata)'))}")
    print_score(accurate_points)
    print_detailed_score_analysis(accurate_points)
    
    # Comparison analysis
    print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('=== COMPARAÇÃO ===')}")
    simple_percentage = (simple_points.score / simple_points.max_score * 100) if simple_points.max_score > 0 else 0
    accurate_percentage = (accurate_points.score / accurate_points.max_score * 100) if accurate_points.max_score > 0 else 0
    
    print(f"Diferença de pontuação: {cyan_highlighted(str(simple_points.score - accurate_points.score))} pontos")
    print(f"Diferença percentual: {cyan_highlighted(f'{simple_percentage - accurate_percentage:.1f}%')}")
    
    if simple_percentage > accurate_percentage:
        print(f"{yellow_highlighted('💡 Dica:')} Trabalhe na precisão da oitava para melhorar a pontuação precisa")
    elif accurate_percentage > simple_percentage:
        print(f"{green_highlighted('🎉 Excelente!')} Sua precisão de oitava está muito boa!")
    else:
        print(f"{blue_highlighted('ℹ️')} Ambas as pontuações são similares - boa consistência!")


def calculate_score_points_from_txt(pitched_data: PitchedData,
                                    ultrastar_txt: UltrastarTxtValue,
                                    song_name: Optional[str] = None) -> Tuple[Score, Score]:
    """Calculate score points from UltraStar TXT with enhanced analysis"""
    
    print(f"{ULTRASINGER_HEAD} {blue_highlighted('Iniciando cálculo de pontuação...')}")
    
    # Calculate scores
    simple_score, accurate_score = calculate_score(pitched_data, ultrastar_txt)
    
    # Print results
    print_score_calculation(simple_score, accurate_score)
    
    # Save analysis if song name provided
    if song_name:
        calculator = UltrastarScoreCalculator()
        
        analysis_data = {
            "simple_score": simple_score.get_score_breakdown(),
            "accurate_score": accurate_score.get_score_breakdown(),
            "comparison": {
                "simple_percentage": (simple_score.score / simple_score.max_score * 100) if simple_score.max_score > 0 else 0,
                "accurate_percentage": (accurate_score.score / accurate_score.max_score * 100) if accurate_score.max_score > 0 else 0,
                "score_difference": simple_score.score - accurate_score.score
            }
        }
        
        calculator.save_score_analysis(analysis_data, song_name)
        print(f"{ULTRASINGER_HEAD} {green_highlighted('Análise salva no cache!')}")
    
    return simple_score, accurate_score


def calculate_score_points(
        processed_data: ProcessData,
        ultrastar_file_output_path: str,
        ignore_audio: bool = False,
        song_name: Optional[str] = None
) -> Tuple[Score, Score]:
    """Enhanced score points calculation with comprehensive analysis"""
    
    print(f"{ULTRASINGER_HEAD} {green_highlighted('=== CÁLCULO DE PONTUAÇÃO ULTRASTAR ===')}")
    
    if not ignore_audio:
        print(f"{ULTRASINGER_HEAD} {blue_highlighted('Analisando arquivo UltraStar gerado...')}")
        ultrastar_txt = ultrastar_parser.parse(ultrastar_file_output_path)
        simple_score, accurate_score = calculate_score_points_from_txt(
            processed_data.pitched_data, ultrastar_txt, song_name
        )
    else:
        print(f"{ULTRASINGER_HEAD} {blue_highlighted('Pontuação do arquivo UltraStar original:')}")
        original_simple, original_accurate = calculate_score_points_from_txt(
            processed_data.pitched_data, processed_data.parsed_file, f"{song_name}_original" if song_name else None
        )
        
        print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('Pontuação do arquivo UltraStar re-afinado:')}")
        ultrastar_txt = ultrastar_parser.parse(ultrastar_file_output_path)
        simple_score, accurate_score = calculate_score_points_from_txt(
            processed_data.pitched_data, ultrastar_txt, f"{song_name}_repitched" if song_name else None
        )
        
        # Compare original vs repitched
        print(f"\n{ULTRASINGER_HEAD} {yellow_highlighted('=== COMPARAÇÃO ORIGINAL vs RE-AFINADO ===')}")
        print(f"Melhoria simples: {cyan_highlighted(str(simple_score.score - original_simple.score))} pontos")
        print(f"Melhoria precisa: {cyan_highlighted(str(accurate_score.score - original_accurate.score))} pontos")
        
        if simple_score.score > original_simple.score:
            print(f"{green_highlighted('✅ Re-afinação melhorou a pontuação!')}")
        elif simple_score.score < original_simple.score:
            print(f"{red_highlighted('⚠️ Re-afinação piorou a pontuação')}")
        else:
            print(f"{blue_highlighted('ℹ️ Pontuação mantida após re-afinação')}")
    
    return simple_score, accurate_score


def enhanced_score_analysis(processed_data: ProcessData, 
                          ultrastar_file_path: str,
                          song_name: str,
                          options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Comprehensive score analysis with detailed metrics"""
    
    if options is None:
        options = {}
    
    # Calculate scores
    simple_score, accurate_score = calculate_score_points(
        processed_data=processed_data,
        ultrastar_file_output_path=ultrastar_file_path,
        ignore_audio=options.get('ignore_audio', False),
        song_name=song_name
    )
    
    # Generate comprehensive analysis
    analysis = {
        "song_name": song_name,
        "timestamp": datetime.now().isoformat(),
        "simple_analysis": simple_score.get_score_breakdown(),
        "accurate_analysis": accurate_score.get_score_breakdown(),
        "recommendations": [],
        "performance_metrics": {
            "overall_grade": simple_score.performance_grade,
            "accuracy_percentage": simple_score.accuracy_percentage,
            "consistency_score": simple_score.consistency_score,
            "timing_score": simple_score.timing_score,
            "pitch_score": simple_score.pitch_score
        }
    }
    
    # Generate recommendations
    if simple_score.accuracy_percentage < 70:
        analysis["recommendations"].extend([
            "Pratique a afinação das notas principais",
            "Trabalhe no timing das entradas",
            "Mantenha consistência durante toda a música"
        ])
    elif simple_score.accuracy_percentage >= 90:
        analysis["recommendations"].extend([
            "Excelente performance! Continue praticando",
            "Tente melhorar a precisão da oitava",
            "Mantenha a consistência em músicas mais difíceis"
        ])
    else:
        analysis["recommendations"].extend([
            "Boa performance! Continue melhorando",
            "Foque nas notas que você mais erra",
            "Pratique o timing das transições"
        ])
    
    return analysis


    def calculate_song_score(self, notes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate song score from notes data"""
        if not notes:
            return {
                'total_score': 0,
                'max_score': 0,
                'accuracy': 0.0,
                'grade': 'D',
                'note_count': 0
            }
        
        total_notes = len(notes)
        scored_notes = 0
        total_score = 0
        max_possible_score = 0
        
        for note in notes:
            if note.get('type') == ':':  # Normal note
                max_possible_score += 1
                # Simulate scoring based on note properties
                if 'pitch' in note and 'text' in note:
                    total_score += 1
                    scored_notes += 1
            elif note.get('type') == '*':  # Golden note
                max_possible_score += 2
                if 'pitch' in note and 'text' in note:
                    total_score += 2
                    scored_notes += 1
        
        accuracy = (scored_notes / total_notes * 100) if total_notes > 0 else 0
        
        # Determine grade
        if accuracy >= 95:
            grade = "S+"
        elif accuracy >= 90:
            grade = "S"
        elif accuracy >= 85:
            grade = "A+"
        elif accuracy >= 80:
            grade = "A"
        elif accuracy >= 75:
            grade = "B+"
        elif accuracy >= 70:
            grade = "B"
        elif accuracy >= 65:
            grade = "C+"
        elif accuracy >= 60:
            grade = "C"
        else:
            grade = "D"
        
        return {
            'total_score': total_score,
            'max_score': max_possible_score,
            'accuracy': accuracy,
            'grade': grade,
            'note_count': total_notes,
            'scored_notes': scored_notes
        }
