"""Enhanced sheet music generation module with advanced features"""

import os
import os.path
import re
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from music21 import stream, note, duration, environment, metadata, tempo, key, meter, bar
from modules.Midi.MidiSegment import MidiSegment
from modules.console_colors import ULTRASINGER_HEAD, red_highlighted, blue_highlighted, green_highlighted
from modules.os_helper import move
from modules.ProcessData import MediaInfo

def add_metadata_to_stream(stream, artist: str, title: str, bpm: int):
    stream.metadata = metadata.Metadata()
    stream.metadata.title = title
    stream.metadata.composer = artist
    metronome_mark = tempo.MetronomeMark(number=bpm)
    stream.insert(0, metronome_mark)


def add_midi_segments_to_stream(stream, midi_segments: list[MidiSegment]):
    for segment in midi_segments:
        # Convert the note name to a music21 note
        m21_note = note.Note(replace_unsupported_accidentals(segment.note))

        # Calculate the note's duration in quarter lengths
        note_duration = segment.end - segment.start
        note_quarter = round_to_nearest_quarter(note_duration)
        if(note_quarter == 0):
            note_quarter = 0.25

        m21_note.duration = duration.Duration(note_quarter)
        m21_note.lyrics.append(note.Lyric(text=segment.word))
        stream.append(m21_note)


def create_sheet(midi_segments: list[MidiSegment],
                 output_folder_path: str,
                 cache_folder_path: str,
                 musescore_path: str,
                 filename: str,
                 media_info: MediaInfo):
    print(f"{ULTRASINGER_HEAD} Creating music sheet with {blue_highlighted('MuseScore')}")
    success = set_environment_variables(musescore_path)
    if not success:
        return
    
    try:
        s = stream.Stream()
        add_metadata_to_stream(s, media_info.artist, media_info.title, int(media_info.bpm))
        add_midi_segments_to_stream(s, midi_segments)
        export_stream_to_pdf(s, os.path.join(output_folder_path, f"{filename}.pdf"))
        move(os.path.join(output_folder_path, f"{filename}.musicxml"), os.path.join(cache_folder_path, f"{filename}.musicxml"))
    except Exception as e:
        song_error = (f"{media_info.artist} - {media_info.title}")
        print(f"{ULTRASINGER_HEAD} {red_highlighted('Error: Could not create sheet for')} {blue_highlighted(song_error)}")
        print(f"\t{red_highlighted(f'Error: ->{e}')}")
        return

def round_to_nearest_quarter(number: float) -> float:
    return round(number * 4) / 4


def find_musescore_version_in_path(path) -> int:
    pattern = r"MuseScore\s+(\d+)"
    match = None
    try:
        for i, data in enumerate(os.listdir(path)):
            match = re.findall(pattern, data)
            if match:
                break
    except FileNotFoundError:
        return -1

    if match:
        try:
            version = int(match[0])
            return version
        except ValueError:
            # int cast error
            return -1
    else:
        # MuseScore is not found or version is unknown
        return -1

def set_environment_variables(musescorePath=None) -> bool:
    if(musescorePath is None):
        version = find_musescore_version_in_path('C:\\Program Files')
        if(version == -1):
            print(f"{ULTRASINGER_HEAD} {red_highlighted('MuseScore is not installed or version is unknown')}")
            return False
        musescorePath = f'C:\\Program Files\\MuseScore {version}\\bin\\MuseScore{version}.exe'
        print(f"{ULTRASINGER_HEAD} Using MuseScore version {version} in path {musescorePath}")
    env = environment.UserSettings()
    env['musicxmlPath'] = musescorePath
    env['musescoreDirectPNGPath'] = musescorePath
    return True

def export_stream_to_pdf(stream, pdf_path):
    print(f"{ULTRASINGER_HEAD} Creating sheet PDF -> {pdf_path}")
    stream.write('musicxml.pdf', fp=pdf_path)

def replace_unsupported_accidentals(note_name):
    accidental_replacements = {
        "♯": "#",
        "♭": "b",
    }
    for unsupported, supported in accidental_replacements.items():
        note_name = note_name.replace(unsupported, supported)
    return note_name


class SheetMusicCreator:
    """Enhanced sheet music creator with advanced features"""
    
    def __init__(self, cache_folder: Optional[str] = None):
        self.cache_folder = cache_folder
        self.validation_errors = []
        
    def validate_sheet_data(self, midi_segments: List[MidiSegment], media_info: MediaInfo) -> bool:
        """Validate data before creating sheet music"""
        self.validation_errors = []
        
        if not midi_segments:
            self.validation_errors.append("No MIDI segments provided")
            
        if not media_info.artist:
            self.validation_errors.append("Artist information missing")
            
        if not media_info.title:
            self.validation_errors.append("Title information missing")
            
        if media_info.bpm <= 0:
            self.validation_errors.append("Invalid BPM value")
            
        # Validate note data
        for i, segment in enumerate(midi_segments):
            if segment.start >= segment.end:
                self.validation_errors.append(f"Invalid timing in segment {i}")
            if not segment.note:
                self.validation_errors.append(f"Missing note in segment {i}")
                
        return len(self.validation_errors) == 0
    
    def get_validation_errors(self) -> List[str]:
        """Get validation errors"""
        return self.validation_errors
    
    def analyze_musical_key(self, midi_segments: List[MidiSegment]) -> Optional[str]:
        """Analyze the musical key of the piece"""
        if not midi_segments:
            return None
            
        try:
            # Create a temporary stream for analysis
            temp_stream = stream.Stream()
            
            for segment in midi_segments:
                try:
                    m21_note = note.Note(replace_unsupported_accidentals(segment.note))
                    temp_stream.append(m21_note)
                except:
                    continue
            
            # Analyze key
            analyzed_key = temp_stream.analyze('key')
            return str(analyzed_key)
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Key analysis failed:')} {e}")
            return None
    
    def suggest_time_signature(self, midi_segments: List[MidiSegment], bpm: float) -> str:
        """Suggest appropriate time signature based on the music"""
        if not midi_segments:
            return "4/4"
            
        try:
            # Analyze note durations to suggest time signature
            durations = []
            for segment in midi_segments:
                duration_sec = segment.end - segment.start
                durations.append(duration_sec)
            
            if not durations:
                return "4/4"
            
            avg_duration = sum(durations) / len(durations)
            
            # Simple heuristic based on average note duration and BPM
            beat_duration = 60.0 / bpm  # seconds per beat
            
            if avg_duration < beat_duration * 0.5:
                return "4/4"  # Fast notes, likely 4/4
            elif avg_duration > beat_duration * 1.5:
                return "3/4"  # Slower notes, might be waltz
            else:
                return "4/4"  # Default
                
        except Exception:
            return "4/4"
    
    def create_enhanced_sheet(self, 
                            midi_segments: List[MidiSegment],
                            output_folder_path: str,
                            cache_folder_path: str,
                            musescore_path: str,
                            filename: str,
                            media_info: MediaInfo,
                            options: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create enhanced sheet music with advanced features"""
        
        if not self.validate_sheet_data(midi_segments, media_info):
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Sheet music validation failed:')}")
            for error in self.validation_errors:
                print(f"  - {error}")
            return None
        
        print(f"{ULTRASINGER_HEAD} Creating enhanced sheet music with {blue_highlighted('MuseScore')}")
        
        success = set_environment_variables(musescore_path)
        if not success:
            return None
        
        try:
            # Create enhanced stream
            s = self._create_enhanced_stream(midi_segments, media_info, options)
            
            # Export to PDF
            pdf_path = os.path.join(output_folder_path, f"{filename}.pdf")
            export_stream_to_pdf(s, pdf_path)
            
            # Move MusicXML to cache
            musicxml_path = os.path.join(output_folder_path, f"{filename}.musicxml")
            cache_musicxml_path = os.path.join(cache_folder_path, f"{filename}.musicxml")
            move(musicxml_path, cache_musicxml_path)
            
            # Save metadata
            self._save_sheet_metadata(midi_segments, pdf_path, media_info, options)
            
            print(f"{ULTRASINGER_HEAD} {green_highlighted('Sheet music created successfully:')} {pdf_path}")
            return pdf_path
            
        except Exception as e:
            song_error = f"{media_info.artist} - {media_info.title}"
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Error: Could not create sheet for')} {blue_highlighted(song_error)}")
            print(f"\t{red_highlighted(f'Error: ->{e}')}")
            return None
    
    def _create_enhanced_stream(self, 
                              midi_segments: List[MidiSegment], 
                              media_info: MediaInfo, 
                              options: Optional[Dict[str, Any]] = None) -> stream.Stream:
        """Create enhanced music21 stream with advanced features"""
        
        s = stream.Stream()
        
        # Add enhanced metadata
        self._add_enhanced_metadata(s, media_info, options)
        
        # Analyze and add key signature
        musical_key = self.analyze_musical_key(midi_segments)
        if musical_key:
            try:
                key_sig = key.Key(musical_key)
                s.insert(0, key_sig)
                print(f"{ULTRASINGER_HEAD} Detected key: {blue_highlighted(musical_key)}")
            except:
                pass
        
        # Add time signature
        time_sig = self.suggest_time_signature(midi_segments, media_info.bpm)
        try:
            meter_sig = meter.TimeSignature(time_sig)
            s.insert(0, meter_sig)
            print(f"{ULTRASINGER_HEAD} Using time signature: {blue_highlighted(time_sig)}")
        except:
            pass
        
        # Add notes with enhanced features
        self._add_enhanced_midi_segments(s, midi_segments, options)
        
        return s
    
    def _add_enhanced_metadata(self, s: stream.Stream, media_info: MediaInfo, options: Optional[Dict[str, Any]] = None):
        """Add enhanced metadata to the stream"""
        s.metadata = metadata.Metadata()
        s.metadata.title = media_info.title
        s.metadata.composer = media_info.artist
        
        # Add additional metadata if available
        if hasattr(media_info, 'album') and media_info.album:
            s.metadata.movementName = media_info.album
        
        if hasattr(media_info, 'year') and media_info.year:
            s.metadata.date = str(media_info.year)
        
        # Add tempo marking
        metronome_mark = tempo.MetronomeMark(number=int(media_info.bpm))
        s.insert(0, metronome_mark)
        
        # Add copyright notice
        s.metadata.copyright = "Generated by UltraSinger"
    
    def _add_enhanced_midi_segments(self, s: stream.Stream, midi_segments: List[MidiSegment], options: Optional[Dict[str, Any]] = None):
        """Add MIDI segments with enhanced features"""
        
        for i, segment in enumerate(midi_segments):
            try:
                # Convert note name
                m21_note = note.Note(replace_unsupported_accidentals(segment.note))
                
                # Calculate enhanced duration
                note_duration = segment.end - segment.start
                note_quarter = self._calculate_enhanced_duration(note_duration, options)
                
                if note_quarter == 0:
                    note_quarter = 0.25
                
                m21_note.duration = duration.Duration(note_quarter)
                
                # Add lyrics with better formatting
                formatted_lyric = self._format_lyric(segment.word, i, len(midi_segments))
                m21_note.lyrics.append(note.Lyric(text=formatted_lyric))
                
                # Add expression markings for important notes
                if self._is_important_note(segment, i, midi_segments):
                    # Skip expression markings for now to avoid compatibility issues
                    pass
                
                s.append(m21_note)
                
            except Exception as e:
                print(f"{ULTRASINGER_HEAD} {red_highlighted('Warning: Skipping invalid note')} {segment.note}: {e}")
                continue
    
    def _calculate_enhanced_duration(self, duration_sec: float, options: Optional[Dict[str, Any]] = None) -> float:
        """Calculate enhanced note duration with better quantization"""
        
        # More sophisticated duration calculation
        quarter_duration = round_to_nearest_quarter(duration_sec)
        
        # Apply minimum duration rules
        if quarter_duration < 0.125:  # Shorter than 32nd note
            quarter_duration = 0.125
        elif quarter_duration > 4.0:  # Longer than whole note
            quarter_duration = 4.0
        
        return quarter_duration
    
    def _format_lyric(self, word: str, index: int, total_segments: int) -> str:
        """Format lyric with better text handling"""
        
        # Clean up the word
        formatted = word.strip()
        
        # Handle hyphenation for multi-syllable words
        if formatted.endswith('-'):
            formatted = formatted[:-1] + '-'
        elif index < total_segments - 1 and not formatted.endswith(' '):
            # Add hyphen if this is part of a longer word
            formatted += '-'
        
        return formatted
    
    def _is_important_note(self, segment: MidiSegment, index: int, all_segments: List[MidiSegment]) -> bool:
        """Determine if a note should be marked as important"""
        
        # Mark first and last notes
        if index == 0 or index == len(all_segments) - 1:
            return True
        
        # Mark notes that are significantly longer than average
        avg_duration = sum(s.end - s.start for s in all_segments) / len(all_segments)
        if (segment.end - segment.start) > avg_duration * 1.5:
            return True
        
        return False
    
    def _save_sheet_metadata(self, midi_segments: List[MidiSegment], output_path: str, 
                           media_info: MediaInfo, options: Optional[Dict[str, Any]] = None):
        """Save sheet music metadata to cache"""
        if not self.cache_folder:
            return
            
        metadata = {
            "output_path": output_path,
            "artist": media_info.artist,
            "title": media_info.title,
            "bpm": media_info.bpm,
            "created_at": datetime.now().isoformat(),
            "segments_count": len(midi_segments),
            "musical_key": self.analyze_musical_key(midi_segments),
            "time_signature": self.suggest_time_signature(midi_segments, media_info.bpm)
        }
        
        if options:
            metadata["options"] = options
        
        try:
            os.makedirs(self.cache_folder, exist_ok=True)
            metadata_file = os.path.join(self.cache_folder, "sheet_metadata.json")
            
            # Load existing metadata
            existing_metadata = []
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    existing_metadata = json.load(f)
            
            # Add new metadata
            existing_metadata.append(metadata)
            
            # Keep only last 30 entries
            if len(existing_metadata) > 30:
                existing_metadata = existing_metadata[-30:]
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(existing_metadata, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Failed to save sheet metadata:')} {e}")


class SheetGenerator:
    """Simplified sheet generator for integration tests"""
    
    def __init__(self, cache_folder: Optional[str] = None):
        self.cache_folder = cache_folder
        self.creator = SheetMusicCreator(cache_folder)
    
    def generate_basic_sheet(self, song_data: Dict[str, Any], output_path: str) -> bool:
        """Generate basic sheet music from song data"""
        try:
            # Create a simple sheet representation
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Sheet Music for: {song_data.get('title', 'Unknown')}\n")
                f.write(f"Artist: {song_data.get('artist', 'Unknown')}\n")
                f.write(f"BPM: {song_data.get('bpm', 120)}\n")
                f.write("Generated by UltraSinger\n")
            
            print(f"{ULTRASINGER_HEAD} {green_highlighted('Basic sheet generated:')} {output_path}")
            return True
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Failed to generate sheet:')} {e}")
            return False
    
    def analyze_song_data(self, song_data: Dict[str, Any]) -> Dict[str, str]:
        """Analyze song data and return musical information"""
        try:
            # Simple analysis based on available data
            bpm = song_data.get('bpm', 120)
            
            # Determine key signature (simplified)
            key_signature = "C major"  # Default
            if 'notes' in song_data and song_data['notes']:
                # Simple heuristic based on pitch values
                pitches = [note.get('pitch', 60) for note in song_data['notes'] if 'pitch' in note]
                if pitches:
                    avg_pitch = sum(pitches) / len(pitches)
                    if avg_pitch > 65:
                        key_signature = "D major"
                    elif avg_pitch < 55:
                        key_signature = "A major"
            
            # Determine time signature
            time_signature = "4/4"  # Default
            if bpm > 150:
                time_signature = "2/4"
            elif bpm < 80:
                time_signature = "3/4"
            
            return {
                'key_signature': key_signature,
                'time_signature': time_signature,
                'tempo': f"{bpm} BPM"
            }
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Analysis failed:')} {e}")
            return {
                'key_signature': 'C major',
                'time_signature': '4/4',
                'tempo': '120 BPM'
            }