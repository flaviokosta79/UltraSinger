"""Ultrastar writer module"""

import re
import os
import langcodes
from packaging import version
from typing import Optional, List, Dict, Any
import json
from datetime import datetime

from modules.console_colors import ULTRASINGER_HEAD, red_highlighted, green_highlighted, blue_highlighted
from modules.Ultrastar.coverter.ultrastar_converter import (
    real_bpm_to_ultrastar_bpm,
    second_to_beat, )
from modules.Ultrastar.coverter.ultrastar_midi_converter import convert_midi_note_to_ultrastar_note
from modules.Ultrastar.ultrastar_txt import UltrastarTxtValue, UltrastarTxtTag, UltrastarTxtNoteTypeTag, \
    FILE_ENCODING
from modules.Ultrastar.ultrastar_score_calculator import Score
from modules.Midi.MidiSegment import MidiSegment


def get_multiplier(real_bpm: float) -> int:
    """Calculates the multiplier for the BPM"""

    if real_bpm == 0:
        raise Exception("BPM is 0")

    multiplier = 1
    result = 0
    while result < 400:
        result = real_bpm * multiplier
        multiplier += 1
    return multiplier - 2


def get_language_name(language: str) -> str:
    """Creates the language name from the language code"""

    return langcodes.Language.make(language=language).display_name()


def create_ultrastar_txt(
        midi_segments: list[MidiSegment],
        ultrastar_file_output: str,
        ultrastar_class: UltrastarTxtValue,
        real_bpm: float) -> None:
    """Creates an Ultrastar txt file from the automation data"""

    print(f"{ULTRASINGER_HEAD} Creating UltraStar file {ultrastar_file_output}")

    ultrastar_bpm = real_bpm_to_ultrastar_bpm(real_bpm)
    multiplication = get_multiplier(ultrastar_bpm)
    ultrastar_bpm = ultrastar_bpm * get_multiplier(ultrastar_bpm)
    silence_split_duration = calculate_silent_beat_length(midi_segments)

    with open(ultrastar_file_output, "w", encoding=FILE_ENCODING) as file:
        gap = midi_segments[0].start

        if version.parse(ultrastar_class.version) >= version.parse("1.0.0"):
            file.write(f"#{UltrastarTxtTag.VERSION}:{ultrastar_class.version}\n"),
        file.write(f"#{UltrastarTxtTag.ARTIST}:{ultrastar_class.artist}\n")
        file.write(f"#{UltrastarTxtTag.TITLE}:{ultrastar_class.title}\n")
        if ultrastar_class.year is not None:
            file.write(f"#{UltrastarTxtTag.YEAR}:{ultrastar_class.year}\n")
        if ultrastar_class.language is not None:
            file.write(f"#{UltrastarTxtTag.LANGUAGE}:{get_language_name(ultrastar_class.language)}\n")
        if ultrastar_class.genre:
            file.write(f"#{UltrastarTxtTag.GENRE}:{ultrastar_class.genre}\n")
        if ultrastar_class.cover is not None:
            file.write(f"#{UltrastarTxtTag.COVER}:{ultrastar_class.cover}\n")
        if version.parse(ultrastar_class.version) >= version.parse("1.2.0"):
            if ultrastar_class.coverUrl is not None:
                file.write(f"#{UltrastarTxtTag.COVERURL}:{ultrastar_class.coverUrl}\n")
        if ultrastar_class.background is not None:
            file.write(f"#{UltrastarTxtTag.BACKGROUND}:{ultrastar_class.background}\n")
        file.write(f"#{UltrastarTxtTag.MP3}:{ultrastar_class.mp3}\n")
        if version.parse(ultrastar_class.version) >= version.parse("1.1.0"):
            file.write(f"#{UltrastarTxtTag.AUDIO}:{ultrastar_class.audio}\n")
            if ultrastar_class.vocals is not None:
                file.write(f"#{UltrastarTxtTag.VOCALS}:{ultrastar_class.vocals}\n")
            if ultrastar_class.instrumental is not None:
                file.write(f"#{UltrastarTxtTag.INSTRUMENTAL}:{ultrastar_class.instrumental}\n")
            if ultrastar_class.tags is not None:
                file.write(f"#{UltrastarTxtTag.TAGS}:{ultrastar_class.tags}\n")
        if ultrastar_class.video is not None:
            file.write(f"#{UltrastarTxtTag.VIDEO}:{ultrastar_class.video}\n")
        if ultrastar_class.videoGap is not None:
            file.write(f"#{UltrastarTxtTag.VIDEOGAP}:{ultrastar_class.videoGap}\n")
        if version.parse(ultrastar_class.version) >= version.parse("1.2.0"):
            if ultrastar_class.videoUrl is not None:
                file.write(f"#{UltrastarTxtTag.VIDEOURL}:{ultrastar_class.videoUrl}\n")
        file.write(f"#{UltrastarTxtTag.BPM}:{round(ultrastar_bpm, 2)}\n")  # not the real BPM!
        file.write(f"#{UltrastarTxtTag.GAP}:{int(gap * 1000)}\n")
        file.write(f"#{UltrastarTxtTag.CREATOR}:{ultrastar_class.creator}\n")
        file.write(f"#{UltrastarTxtTag.COMMENT}:{ultrastar_class.comment}\n")

        # Write the singing part
        previous_end_beat = 0
        separated_word_silence = []  # This is a workaround for separated words that get his ends to far away

        for i, midi_segment in enumerate(midi_segments):
            start_time = (midi_segment.start - gap) * multiplication
            end_time = (
                               midi_segment.end - midi_segment.start
                       ) * multiplication
            start_beat = round(second_to_beat(start_time, real_bpm))
            duration = round(second_to_beat(end_time, real_bpm))

            # Fix the round issue, so the beats don’t overlap
            start_beat = max(start_beat, previous_end_beat)
            previous_end_beat = start_beat + duration

            # Calculate the silence between the words
            if i < len(midi_segments) - 1:
                silence = (midi_segments[i + 1].start - midi_segment.end)
            else:
                silence = 0

            # : 10 10 10 w
            # ':'   start midi part
            # 'n1'  start at real beat
            # 'n2'  duration at real beat
            # 'n3'  pitch where 0 == C4
            # 'w'   lyric
            line = f"{UltrastarTxtNoteTypeTag.NORMAL} " \
                   f"{str(start_beat)} " \
                   f"{str(duration)} " \
                   f"{str(convert_midi_note_to_ultrastar_note(midi_segment))} " \
                   f"{midi_segment.word}\n"

            file.write(line)

            # detect silence between words
            if not midi_segment.word.endswith(" "):
                separated_word_silence.append(silence)
                continue

            if i != len(midi_segments) - 1 and silence_split_duration != 0 and silence > silence_split_duration or any(
                    s > silence_split_duration for s in separated_word_silence):
                # - 10
                # '-' end of current sing part
                # 'n1' show next at time in real beat
                show_next = (
                        second_to_beat(midi_segment.end - gap, real_bpm)
                        * multiplication
                )
                linebreak = f"{UltrastarTxtTag.LINEBREAK} " \
                            f"{str(round(show_next))}\n"
                file.write(linebreak)
            separated_word_silence = []
        file.write(f"{UltrastarTxtTag.FILE_END}")


def deviation(silence_parts):
    """Calculates the deviation of the silence parts"""

    if len(silence_parts) < 5:
        return 0

    # Remove the longest part so the deviation is not that high
    sorted_parts = sorted(silence_parts)
    filtered_parts = [part for part in sorted_parts if part < sorted_parts[-1]]

    sum_parts = sum(filtered_parts)
    if sum_parts == 0:
        return 0

    mean = sum_parts / len(filtered_parts)
    return mean


def calculate_silent_beat_length(midi_segments: list[MidiSegment]):
    print(f"{ULTRASINGER_HEAD} Calculating silence parts for linebreaks.")

    silent_parts = []
    for i, data in enumerate(midi_segments):
        if i < len(midi_segments) - 1:
            silent_parts.append(midi_segments[i + 1].start - data.end)

    return deviation(silent_parts)


def create_repitched_txt_from_ultrastar_data(
        input_file: str, note_numbers: list[int], output_repitched_ultrastar: str
) -> None:
    """Creates a repitched ultrastar txt file from the original one"""
    # todo: just add '_repitched' to input_file
    print(f"{ULTRASINGER_HEAD} Creating repitched ultrastar txt -> {input_file}_repitch.txt")

    # todo: to reader
    with open(input_file, "r", encoding=FILE_ENCODING) as file:
        txt = file.readlines()

    i = 0
    # todo: just add '_repitched' to input_file
    with open(output_repitched_ultrastar, "w", encoding=FILE_ENCODING) as file:
        for line in txt:
            if line.startswith(f"{UltrastarTxtNoteTypeTag.NORMAL} "):
                parts = re.findall(r"\S+|\s+", line)
                # between are whitespaces
                # [0] :
                # [2] start beat
                # [4] duration
                # [6] pitch
                # [8] word
                parts[6] = str(note_numbers[i])
                delimiter = ""
                file.write(delimiter.join(parts))
                i += 1
            else:
                file.write(line)


def add_score_to_ultrastar_txt(ultrastar_file_output: str, score: Score) -> None:
    """Adds the score to the ultrastar txt file"""
    with open(ultrastar_file_output, "r", encoding=FILE_ENCODING) as file:
        text = file.read()
    text = text.split("\n")

    for i, line in enumerate(text):
        if line.startswith(f"#{UltrastarTxtTag.COMMENT}:"):
            text[
                i
            ] = f"{line} | Score: total: {score.score}, notes: {score.notes} line: {score.line_bonus}, golden: {score.golden}"
            break

        if line.startswith((
                f"{UltrastarTxtNoteTypeTag.FREESTYLE} ",
                f"{UltrastarTxtNoteTypeTag.NORMAL} ",
                f"{UltrastarTxtNoteTypeTag.GOLDEN} ",
                f"{UltrastarTxtNoteTypeTag.RAP} ",
                f"{UltrastarTxtNoteTypeTag.RAP_GOLDEN} ")):
            text.insert(
                i,
                f"#{UltrastarTxtTag.COMMENT}: UltraSinger [GitHub] | Score: total: {score.score}, notes: {score.notes} line: {score.line_bonus}, golden: {score.golden}",
            )
            break

    text = "\n".join(text)

    with open(ultrastar_file_output, "w", encoding=FILE_ENCODING) as file:
        file.write(text)


class UltraStarWriter:
    """Enhanced UltraStar file writer with advanced features"""
    
    def __init__(self, cache_folder: Optional[str] = None):
        self.cache_folder = cache_folder
        self.validation_errors = []
        
    def validate_ultrastar_data(self, ultrastar_class: UltrastarTxtValue, midi_segments: List[MidiSegment]) -> bool:
        """Validate UltraStar data before writing"""
        self.validation_errors = []
        
        # Validate required fields
        if not ultrastar_class.artist:
            self.validation_errors.append("Artist is required")
        if not ultrastar_class.title:
            self.validation_errors.append("Title is required")
        if not ultrastar_class.mp3:
            self.validation_errors.append("MP3 file is required")
            
        # Validate MIDI segments
        if not midi_segments:
            self.validation_errors.append("No MIDI segments found")
        else:
            for i, segment in enumerate(midi_segments):
                if segment.start >= segment.end:
                    self.validation_errors.append(f"Invalid timing in segment {i}: start >= end")
                if not segment.word.strip():
                    self.validation_errors.append(f"Empty word in segment {i}")
                    
        return len(self.validation_errors) == 0
    
    def get_validation_errors(self) -> List[str]:
        """Get validation errors"""
        return self.validation_errors
    
    def create_backup(self, file_path: str) -> Optional[str]:
        """Create backup of existing file"""
        if os.path.exists(file_path):
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                import shutil
                shutil.copy2(file_path, backup_path)
                print(f"{ULTRASINGER_HEAD} Backup created: {backup_path}")
                return backup_path
            except Exception as e:
                print(f"{ULTRASINGER_HEAD} {red_highlighted('Failed to create backup:')} {e}")
        return None
    
    def save_metadata(self, ultrastar_class: UltrastarTxtValue, output_path: str):
        """Save metadata to cache for future use"""
        if not self.cache_folder:
            return
            
        metadata = {
            "artist": ultrastar_class.artist,
            "title": ultrastar_class.title,
            "year": ultrastar_class.year,
            "language": ultrastar_class.language,
            "genre": ultrastar_class.genre,
            "creator": ultrastar_class.creator,
            "version": ultrastar_class.version,
            "created_at": datetime.now().isoformat(),
            "output_path": output_path
        }
        
        try:
            os.makedirs(self.cache_folder, exist_ok=True)
            metadata_file = os.path.join(self.cache_folder, "ultrastar_metadata.json")
            
            # Load existing metadata
            existing_metadata = []
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    existing_metadata = json.load(f)
            
            # Add new metadata
            existing_metadata.append(metadata)
            
            # Keep only last 100 entries
            if len(existing_metadata) > 100:
                existing_metadata = existing_metadata[-100:]
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(existing_metadata, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Failed to save metadata:')} {e}")


def format_separated_string(data: str) -> str:
    temp = re.sub(r'[;/]', ',', data)
    words = temp.split(',')
    words = [s for s in words if s.strip()]

    for i, word in enumerate(words):
        if "-" not in word:
            words[i] = word.strip().capitalize() + ', '
        else:
            dash_words = word.split('-')
            capitalized_dash_words = [dash_word.strip().capitalize() for dash_word in dash_words]
            formatted_dash_word = '-'.join(capitalized_dash_words) + ', '
            words[i] = formatted_dash_word

    formatted_string = ''.join(words)

    if formatted_string.endswith(', '):
        formatted_string = formatted_string[:-2]

    return formatted_string
