"""Enhanced MIDI creator module with advanced features"""

import math
import os
import json
from collections import Counter
from typing import Optional, List, Dict, Any
from datetime import datetime

import librosa
import numpy as np
import pretty_midi
import unidecode

from modules.Midi.MidiSegment import MidiSegment
from modules.Speech_Recognition.TranscribedData import TranscribedData
from modules.console_colors import (
    ULTRASINGER_HEAD, blue_highlighted, red_highlighted, green_highlighted
)
from modules.Ultrastar.ultrastar_txt import UltrastarTxtValue
from modules.Pitcher.pitched_data import PitchedData
from modules.Pitcher.pitched_data_helper import get_frequencies_with_high_confidence


def create_midi_instrument(midi_segments: list[MidiSegment]) -> object:
    """Converts an Ultrastar data to a midi instrument"""

    print(f"{ULTRASINGER_HEAD} Creating midi instrument")

    instrument = pretty_midi.Instrument(program=0, name="Vocals")
    velocity = 100

    for i, midi_segment in enumerate(midi_segments):
        note = pretty_midi.Note(velocity, librosa.note_to_midi(midi_segment.note), midi_segment.start, midi_segment.end)
        instrument.notes.append(note)

    return instrument

def sanitize_for_midi(text):
    """
    Sanitize text for MIDI compatibility.
    Uses unidecode to approximate characters to ASCII.
    """
    return unidecode.unidecode(text)

def __create_midi(instruments: list[object], bpm: float, midi_output: str, midi_segments: list[MidiSegment]) -> None:
    """Write instruments to midi file"""

    print(f"{ULTRASINGER_HEAD} Creating midi file -> {midi_output}")

    midi_data = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    for i, midi_segment in enumerate(midi_segments):
        sanitized_word = sanitize_for_midi(midi_segment.word)
        midi_data.lyrics.append(pretty_midi.Lyric(text=sanitized_word, time=midi_segment.start))
    for instrument in instruments:
        midi_data.instruments.append(instrument)
    midi_data.write(midi_output)


class MidiCreator:
    """Enhanced MIDI creator with advanced features and caching"""
    
    def __init__(self, cache_folder: Optional[str] = None):
        self.cache_folder = cache_folder
        self.validation_errors = []
        
    def validate_midi_data(self, midi_segments: List[MidiSegment], bpm: float) -> bool:
        """Validate MIDI data before creation"""
        self.validation_errors = []
        
        if not midi_segments:
            self.validation_errors.append("No MIDI segments provided")
            return False
            
        if bpm <= 0:
            self.validation_errors.append("Invalid BPM value")
            
        for i, segment in enumerate(midi_segments):
            if segment.start >= segment.end:
                self.validation_errors.append(f"Invalid timing in segment {i}")
            if not segment.note:
                self.validation_errors.append(f"Missing note in segment {i}")
            if not segment.word.strip():
                self.validation_errors.append(f"Empty word in segment {i}")
                
        return len(self.validation_errors) == 0
    
    def get_validation_errors(self) -> List[str]:
        """Get validation errors"""
        return self.validation_errors
    
    def estimate_midi_size(self, midi_segments: List[MidiSegment]) -> Dict[str, Any]:
        """Estimate MIDI file properties"""
        if not midi_segments:
            return {"duration": 0, "notes": 0, "size_estimate": 0}
            
        duration = max(segment.end for segment in midi_segments)
        notes = len(midi_segments)
        
        # Rough estimate: base size + notes * average_note_size
        size_estimate = 1024 + notes * 50  # bytes
        
        return {
            "duration": duration,
            "notes": notes,
            "size_estimate": size_estimate,
            "note_range": self._get_note_range(midi_segments)
        }
    
    def _get_note_range(self, midi_segments: List[MidiSegment]) -> Dict[str, str]:
        """Get the range of notes in the MIDI segments"""
        if not midi_segments:
            return {"lowest": "", "highest": ""}
            
        notes = [segment.note for segment in midi_segments if segment.note]
        if not notes:
            return {"lowest": "", "highest": ""}
            
        # Convert to MIDI numbers for comparison
        midi_numbers = []
        for note in notes:
            try:
                midi_numbers.append(librosa.note_to_midi(note))
            except:
                continue
                
        if not midi_numbers:
            return {"lowest": "", "highest": ""}
            
        lowest_midi = min(midi_numbers)
        highest_midi = max(midi_numbers)
        
        return {
            "lowest": librosa.midi_to_note(lowest_midi),
            "highest": librosa.midi_to_note(highest_midi)
        }
    
    def save_midi_metadata(self, midi_segments: List[MidiSegment], output_path: str, bpm: float):
        """Save MIDI metadata to cache"""
        if not self.cache_folder:
            return
            
        metadata = {
            "output_path": output_path,
            "bpm": bpm,
            "created_at": datetime.now().isoformat(),
            "properties": self.estimate_midi_size(midi_segments),
            "segments_count": len(midi_segments)
        }
        
        try:
            os.makedirs(self.cache_folder, exist_ok=True)
            metadata_file = os.path.join(self.cache_folder, "midi_metadata.json")
            
            # Load existing metadata
            existing_metadata = []
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    existing_metadata = json.load(f)
            
            # Add new metadata
            existing_metadata.append(metadata)
            
            # Keep only last 50 entries
            if len(existing_metadata) > 50:
                existing_metadata = existing_metadata[-50:]
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(existing_metadata, f, indent=2)
                
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Failed to save MIDI metadata:')} {e}")
    
    def create_enhanced_midi_file(self, 
                                real_bpm: float,
                                song_output: str,
                                midi_segments: List[MidiSegment],
                                basename_without_ext: str,
                                metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create MIDI file with enhanced features and validation"""
        
        if not self.validate_midi_data(midi_segments, real_bpm):
            print(f"{ULTRASINGER_HEAD} {red_highlighted('MIDI validation failed:')}")
            for error in self.validation_errors:
                print(f"  - {error}")
            return None
        
        print(f"{ULTRASINGER_HEAD} Creating enhanced MIDI with {blue_highlighted('pretty_midi')}")
        
        try:
            # Create instrument with enhanced features
            instrument = self._create_enhanced_instrument(midi_segments, metadata)
            
            # Create MIDI file
            midi_output = os.path.join(song_output, f"{basename_without_ext}.mid")
            self._create_enhanced_midi(instrument, real_bpm, midi_output, midi_segments, metadata)
            
            # Save metadata
            self.save_midi_metadata(midi_segments, midi_output, real_bpm)
            
            print(f"{ULTRASINGER_HEAD} {green_highlighted('MIDI file created successfully:')} {midi_output}")
            return midi_output
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Error creating MIDI file:')} {e}")
            return None
    
    def _create_enhanced_instrument(self, midi_segments: List[MidiSegment], metadata: Optional[Dict[str, Any]] = None) -> pretty_midi.Instrument:
        """Create enhanced MIDI instrument with better velocity and expression"""
        
        print(f"{ULTRASINGER_HEAD} Creating enhanced MIDI instrument")
        
        # Use different program based on metadata or default to vocals
        program = 0  # Acoustic Grand Piano (default for vocals)
        if metadata and "instrument_program" in metadata:
            program = metadata["instrument_program"]
            
        instrument = pretty_midi.Instrument(program=program, name="Enhanced Vocals")
        
        for i, midi_segment in enumerate(midi_segments):
            try:
                # Calculate dynamic velocity based on segment properties
                velocity = self._calculate_dynamic_velocity(midi_segment, i, len(midi_segments))
                
                # Create note with enhanced properties
                note = pretty_midi.Note(
                    velocity=velocity,
                    pitch=librosa.note_to_midi(midi_segment.note),
                    start=midi_segment.start,
                    end=midi_segment.end
                )
                instrument.notes.append(note)
                
            except Exception as e:
                print(f"{ULTRASINGER_HEAD} {red_highlighted('Warning: Skipping invalid note')} {midi_segment.note}: {e}")
                continue
        
        return instrument
    
    def _calculate_dynamic_velocity(self, segment: MidiSegment, index: int, total_segments: int) -> int:
        """Calculate dynamic velocity based on segment properties"""
        base_velocity = 80
        
        # Vary velocity based on position (crescendo/diminuendo effects)
        position_factor = 1.0
        if total_segments > 1:
            position = index / (total_segments - 1)
            # Slight crescendo towards middle, then diminuendo
            if position < 0.5:
                position_factor = 0.8 + 0.4 * (position * 2)
            else:
                position_factor = 1.2 - 0.4 * ((position - 0.5) * 2)
        
        # Vary based on note duration (longer notes slightly louder)
        duration = segment.end - segment.start
        duration_factor = min(1.2, 0.8 + duration * 0.1)
        
        # Calculate final velocity
        velocity = int(base_velocity * position_factor * duration_factor)
        return max(40, min(127, velocity))  # Clamp between 40-127
    
    def _create_enhanced_midi(self, instrument: pretty_midi.Instrument, bpm: float, 
                            midi_output: str, midi_segments: List[MidiSegment], 
                            metadata: Optional[Dict[str, Any]] = None) -> None:
        """Create enhanced MIDI file with metadata and lyrics"""
        
        print(f"{ULTRASINGER_HEAD} Writing enhanced MIDI file -> {midi_output}")
        
        midi_data = pretty_midi.PrettyMIDI(initial_tempo=bpm)
        
        # Add lyrics with better timing
        for i, midi_segment in enumerate(midi_segments):
            sanitized_word = sanitize_for_midi(midi_segment.word)
            # Add lyric at note start time
            midi_data.lyrics.append(pretty_midi.Lyric(text=sanitized_word, time=midi_segment.start))
        
        # Add instrument
        midi_data.instruments.append(instrument)
        
        # Add metadata as text events if provided
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, str):
                    text_event = pretty_midi.Text(text=f"{key}: {value}", time=0)
                    midi_data.text_events.append(text_event)
        
        # Write MIDI file
        midi_data.write(midi_output)


def convert_frequencies_to_notes(frequency: [str]) -> list[list[str]]:
    """Converts frequencies to notes"""
    notes = []
    for freq in frequency:
        notes.append(librosa.hz_to_note(float(freq)))
    return notes


def most_frequent(array: [str]) -> list[tuple[str, int]]:
    """Get most frequent item in array"""
    return Counter(array).most_common(1)


def find_nearest_index(array: list[float], value: float) -> int:
    """Nearest index in array"""
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (
        idx == len(array)
        or math.fabs(value - array[idx - 1]) < math.fabs(value - array[idx])
    ):
        return idx - 1

    return idx


def create_midi_notes_from_pitched_data(start_times: list[float], end_times: list[float], words: list[str], pitched_data: PitchedData) -> list[
    MidiSegment]:
    """Create midi notes from pitched data"""
    print(f"{ULTRASINGER_HEAD} Creating midi_segments")

    midi_segments = []

    for index, start_time in enumerate(start_times):
        end_time = end_times[index]
        word = str(words[index])

        midi_segment = create_midi_note_from_pitched_data(start_time, end_time, pitched_data, word)
        midi_segments.append(midi_segment)

        # todo: Progress?
        # print(filename + " f: " + str(mean))
    return midi_segments


def create_midi_note_from_pitched_data(start_time: float, end_time: float, pitched_data: PitchedData, word: str) -> MidiSegment:
    """Create midi note from pitched data"""

    start = find_nearest_index(pitched_data.times, start_time)
    end = find_nearest_index(pitched_data.times, end_time)

    if start == end:
        freqs = [pitched_data.frequencies[start]]
        confs = [pitched_data.confidence[start]]
    else:
        freqs = pitched_data.frequencies[start:end]
        confs = pitched_data.confidence[start:end]

    conf_f = get_frequencies_with_high_confidence(freqs, confs)

    notes = convert_frequencies_to_notes(conf_f)

    note = most_frequent(notes)[0][0]

    return MidiSegment(note, start_time, end_time, word)


def create_midi_segments_from_transcribed_data(transcribed_data: list[TranscribedData], pitched_data: PitchedData) -> list[MidiSegment]:
    start_times = []
    end_times = []
    words = []

    if transcribed_data:
        for i, midi_segment in enumerate(transcribed_data):
            start_times.append(midi_segment.start)
            end_times.append(midi_segment.end)
            words.append(midi_segment.word)
        midi_segments = create_midi_notes_from_pitched_data(start_times, end_times, words,
                                                            pitched_data)
        return midi_segments


def create_repitched_midi_segments_from_ultrastar_txt(pitched_data: PitchedData, ultrastar_txt: UltrastarTxtValue) -> list[MidiSegment]:
    start_times = []
    end_times = []
    words = []

    for i, note_lines in enumerate(ultrastar_txt.UltrastarNoteLines):
        start_times.append(note_lines.startTime)
        end_times.append(note_lines.endTime)
        words.append(note_lines.word)
    midi_segments = create_midi_notes_from_pitched_data(start_times, end_times, words, pitched_data)
    return midi_segments


def create_midi_file(
        real_bpm: float,
        song_output: str,
        midi_segments: list[MidiSegment],
        basename_without_ext: str,
) -> None:
    """Create midi file"""
    print(f"{ULTRASINGER_HEAD} Creating Midi with {blue_highlighted('pretty_midi')}")

    voice_instrument = [
        create_midi_instrument(midi_segments)
    ]

    midi_output = os.path.join(song_output, f"{basename_without_ext}.mid")
    __create_midi(voice_instrument, real_bpm, midi_output, midi_segments)
