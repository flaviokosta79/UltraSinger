"""Whisper Speech Recognition Module"""
import inspect
import textwrap
import torch
import whisperx
import os
import json
from enum import Enum
from torch.cuda import OutOfMemoryError
from typing import Optional, Dict, List, Tuple

from modules.Speech_Recognition.TranscriptionResult import TranscriptionResult
from modules.console_colors import ULTRASINGER_HEAD, blue_highlighted, red_highlighted, green_highlighted, yellow_highlighted
from modules.Speech_Recognition.TranscribedData import TranscribedData, from_whisper

#Addition for numbers to words
import re
import ast
from num2words import num2words

#Addition for numbers to words
re_split_preserve_space = re.compile(r'(\d+|\W+|\w+)')

MEMORY_ERROR_MESSAGE = f"{ULTRASINGER_HEAD} {blue_highlighted('whisper')} ran out of GPU memory; reduce --whisper_batch_size or force usage of cpu with --force_cpu"

class WhisperModel(Enum):
    """Whisper model with detailed information"""
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE_V1 = "large-v1"
    LARGE_V2 = "large-v2"
    LARGE_V3 = "large-v3"
    LARGE_V3_TURBO = "large-v3-turbo"

    # English-only models
    TINY_EN = "tiny.en"
    BASE_EN = "base.en"
    SMALL_EN = "small.en"
    MEDIUM_EN = "medium.en"

    @classmethod
    def get_model_info(cls, model: 'WhisperModel') -> dict:
        """Get detailed information about a specific model"""
        model_info = {
            cls.TINY: {
                "parameters": "39M",
                "vram_required": "~1GB",
                "relative_speed": "~32x",
                "multilingual": True,
                "description": "Fastest model, lowest accuracy"
            },
            cls.BASE: {
                "parameters": "74M",
                "vram_required": "~1GB",
                "relative_speed": "~16x",
                "multilingual": True,
                "description": "Good balance of speed and accuracy"
            },
            cls.SMALL: {
                "parameters": "244M",
                "vram_required": "~2GB",
                "relative_speed": "~6x",
                "multilingual": True,
                "description": "Better accuracy, moderate speed"
            },
            cls.MEDIUM: {
                "parameters": "769M",
                "vram_required": "~5GB",
                "relative_speed": "~2x",
                "multilingual": True,
                "description": "High accuracy, slower processing"
            },
            cls.LARGE_V1: {
                "parameters": "1550M",
                "vram_required": "~10GB",
                "relative_speed": "1x",
                "multilingual": True,
                "description": "Highest accuracy, slowest processing"
            },
            cls.LARGE_V2: {
                "parameters": "1550M",
                "vram_required": "~10GB",
                "relative_speed": "1x",
                "multilingual": True,
                "description": "Improved large model with better performance"
            },
            cls.LARGE_V3: {
                "parameters": "1550M",
                "vram_required": "~10GB",
                "relative_speed": "1x",
                "multilingual": True,
                "description": "Latest large model with best accuracy"
            },
            cls.LARGE_V3_TURBO: {
                "parameters": "809M",
                "vram_required": "~6GB",
                "relative_speed": "~8x",
                "multilingual": True,
                "description": "Optimized V3 with 4 decoder layers - 8x faster with minimal quality loss"
            },
            cls.TINY_EN: {
                "parameters": "39M",
                "vram_required": "~1GB",
                "relative_speed": "~32x",
                "multilingual": False,
                "description": "English-only, fastest model"
            },
            cls.BASE_EN: {
                "parameters": "74M",
                "vram_required": "~1GB",
                "relative_speed": "~16x",
                "multilingual": False,
                "description": "English-only, good balance"
            },
            cls.SMALL_EN: {
                "parameters": "244M",
                "vram_required": "~2GB",
                "relative_speed": "~6x",
                "multilingual": False,
                "description": "English-only, better accuracy"
            },
            cls.MEDIUM_EN: {
                "parameters": "769M",
                "vram_required": "~5GB",
                "relative_speed": "~2x",
                "multilingual": False,
                "description": "English-only, high accuracy"
            }
        }
        return model_info.get(model, {})

    @classmethod
    def get_recommended_model(cls, language: str = None, device: str = "cpu", vram_gb: float = 4.0) -> 'WhisperModel':
        """Get recommended model based on language, device and available VRAM"""
        if language == "en":
            # English-only models are more accurate for English
            if device == "cpu":
                return cls.BASE_EN
            elif vram_gb >= 10:
                return cls.MEDIUM_EN
            elif vram_gb >= 5:
                return cls.SMALL_EN
            else:
                return cls.BASE_EN
        else:
            # Multilingual models
            if device == "cpu":
                return cls.BASE
            elif vram_gb >= 10:
                return cls.LARGE_V3_TURBO  # Prefer turbo for better performance
            elif vram_gb >= 6:
                return cls.LARGE_V3_TURBO  # Turbo fits in 6GB
            elif vram_gb >= 5:
                return cls.MEDIUM
            elif vram_gb >= 2:
                return cls.SMALL
            else:
                return cls.BASE

def get_supported_languages() -> Dict[str, str]:
    """Get list of supported languages with their codes"""
    return {
        "en": "English",
        "zh": "Chinese",
        "de": "German",
        "es": "Spanish",
        "ru": "Russian",
        "ko": "Korean",
        "fr": "French",
        "ja": "Japanese",
        "pt": "Portuguese",
        "tr": "Turkish",
        "pl": "Polish",
        "ca": "Catalan",
        "nl": "Dutch",
        "ar": "Arabic",
        "sv": "Swedish",
        "it": "Italian",
        "id": "Indonesian",
        "hi": "Hindi",
        "fi": "Finnish",
        "vi": "Vietnamese",
        "he": "Hebrew",
        "uk": "Ukrainian",
        "el": "Greek",
        "ms": "Malay",
        "cs": "Czech",
        "ro": "Romanian",
        "da": "Danish",
        "hu": "Hungarian",
        "ta": "Tamil",
        "no": "Norwegian",
        "th": "Thai",
        "ur": "Urdu",
        "hr": "Croatian",
        "bg": "Bulgarian",
        "lt": "Lithuanian",
        "la": "Latin",
        "mi": "Maori",
        "ml": "Malayalam",
        "cy": "Welsh",
        "sk": "Slovak",
        "te": "Telugu",
        "fa": "Persian",
        "lv": "Latvian",
        "bn": "Bengali",
        "sr": "Serbian",
        "az": "Azerbaijani",
        "sl": "Slovenian",
        "kn": "Kannada",
        "et": "Estonian",
        "mk": "Macedonian",
        "br": "Breton",
        "eu": "Basque",
        "is": "Icelandic",
        "hy": "Armenian",
        "ne": "Nepali",
        "mn": "Mongolian",
        "bs": "Bosnian",
        "kk": "Kazakh",
        "sq": "Albanian",
        "sw": "Swahili",
        "gl": "Galician",
        "mr": "Marathi",
        "pa": "Punjabi",
        "si": "Sinhala",
        "km": "Khmer",
        "sn": "Shona",
        "yo": "Yoruba",
        "so": "Somali",
        "af": "Afrikaans",
        "oc": "Occitan",
        "ka": "Georgian",
        "be": "Belarusian",
        "tg": "Tajik",
        "sd": "Sindhi",
        "gu": "Gujarati",
        "am": "Amharic",
        "yi": "Yiddish",
        "lo": "Lao",
        "uz": "Uzbek",
        "fo": "Faroese",
        "ht": "Haitian Creole",
        "ps": "Pashto",
        "tk": "Turkmen",
        "nn": "Nynorsk",
        "mt": "Maltese",
        "sa": "Sanskrit",
        "lb": "Luxembourgish",
        "my": "Myanmar",
        "bo": "Tibetan",
        "tl": "Tagalog",
        "mg": "Malagasy",
        "as": "Assamese",
        "tt": "Tatar",
        "haw": "Hawaiian",
        "ln": "Lingala",
        "ha": "Hausa",
        "ba": "Bashkir",
        "jw": "Javanese",
        "su": "Sundanese"
    }

def validate_language_code(language: str) -> bool:
    """Validate if language code is supported"""
    supported_languages = get_supported_languages()
    return language.lower() in supported_languages

def estimate_transcription_time(audio_duration_seconds: float, model: WhisperModel, device: str) -> float:
    """Estimate transcription time based on audio duration, model and device"""
    model_info = WhisperModel.get_model_info(model)

    # Base processing time per second of audio
    base_time_per_second = {
        "cpu": 0.5,  # seconds of processing per second of audio
        "cuda": 0.1
    }

    # Model speed multipliers (relative to large model)
    speed_multipliers = {
        WhisperModel.TINY: 32,
        WhisperModel.TINY_EN: 32,
        WhisperModel.BASE: 16,
        WhisperModel.BASE_EN: 16,
        WhisperModel.SMALL: 6,
        WhisperModel.SMALL_EN: 6,
        WhisperModel.MEDIUM: 2,
        WhisperModel.MEDIUM_EN: 2,
        WhisperModel.LARGE_V1: 1,
        WhisperModel.LARGE_V2: 1,
        WhisperModel.LARGE_V3: 1,
        WhisperModel.LARGE_V3_TURBO: 8  # 8x faster than regular large models
    }

    base_time = base_time_per_second.get(device, 0.5)
    speed_multiplier = speed_multipliers.get(model, 1)

    estimated_time = (audio_duration_seconds * base_time) / speed_multiplier
    return max(estimated_time, 1.0)  # Minimum 1 second

def check_whisper_device_compatibility(device: str) -> str:
    """Check and validate Whisper device compatibility"""
    if device == "cuda":
        if not torch.cuda.is_available():
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} CUDA not available for Whisper, falling back to CPU")
            return "cpu"
        else:
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
            print(f"{ULTRASINGER_HEAD} GPU Memory Available: {blue_highlighted(f'{gpu_memory:.1f} GB')}")
            return "cuda"
    return "cpu"

#Addition for numbers to words (Using previous code from louispan in PR#135)
def number_to_words(line, language='en'):
    # https://github.com/m-bain/whisperX
    # Transcript words which do not contain characters in the alignment models dictionary e.g. "2014." or "£13.60" cannot be aligned and therefore are not given a timing.
    # Therefore, convert numbers to words
    out_tokens = []
    in_tokens = re_split_preserve_space.findall(line)
    for token in in_tokens:
        try:
            num = ast.literal_eval(token)
            try:
                out_tokens.append(num2words(num, lang=language))
            except NotImplementedError:
                print(
                    f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Unknown language for number transcription. Keeping number as numeric characters for line: {line}, token: {token}"
                )
                out_tokens.append(token)
        except Exception:
            out_tokens.append(token)
    return ''.join(out_tokens)

def replace_code_lines(source, start_token, end_token,
                       replacement, escape_tokens=True):
    """Replace the source code between `start_token` and `end_token`
    in `source` with `replacement`. The `start_token` portion is included
    in the replaced code. If `escape_tokens` is True (default),
    escape the tokens to avoid them being treated as a regular expression."""

    if escape_tokens:
        start_token = re.escape(start_token)
        end_token = re.escape(end_token)

    def replace_with_indent(match):
        indent = match.group(1)
        return textwrap.indent(replacement, indent)

    return re.sub(r"^(\s+)({}[\s\S]+?)(?=^\1{})".format(start_token, end_token),
                  replace_with_indent, source, flags=re.MULTILINE)

def save_transcription_cache(cache_path: str, transcription_result: TranscriptionResult) -> None:
    """Save transcription result to cache"""
    try:
        cache_data = {
            "transcribed_data": [
                {
                    "word": td.word,
                    "start": td.start,
                    "end": td.end,
                    "is_hyphen": getattr(td, 'is_hyphen', False),
                    "is_word_end": getattr(td, 'is_word_end', True)
                }
                for td in transcription_result.transcribed_data
            ],
            "detected_language": transcription_result.detected_language
        }

        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)

        print(f"{ULTRASINGER_HEAD} {green_highlighted('cache')} Transcription saved to cache")

    except Exception as e:
        print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to save transcription cache: {str(e)}")

def load_transcription_cache(cache_path: str) -> Optional[TranscriptionResult]:
    """Load transcription result from cache"""
    try:
        if not os.path.exists(cache_path):
            return None

        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        transcribed_data = []
        for td_data in cache_data["transcribed_data"]:
            td = TranscribedData()
            td.word = td_data["word"]
            td.start = td_data["start"]
            td.end = td_data["end"]
            td.is_hyphen = td_data.get("is_hyphen", False)
            td.is_word_end = td_data.get("is_word_end", True)
            transcribed_data.append(td)

        result = TranscriptionResult(transcribed_data, cache_data["detected_language"])
        print(f"{ULTRASINGER_HEAD} {green_highlighted('cache')} Loaded transcription from cache")
        return result

    except Exception as e:
        print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to load transcription cache: {str(e)}")
        return None

def transcribe_with_whisper(
    audio_path: str,
    model: WhisperModel,
    device="cpu",
    alignment_model: str = None,
    batch_size: int = 16,
    compute_type: str = None,
    language: str = None,
    keep_numbers: bool = False,
    cache_path: str = None,
    skip_cache: bool = False
) -> TranscriptionResult:
    """Transcribe with whisper with enhanced features"""

    # Check cache first
    if cache_path and not skip_cache:
        cached_result = load_transcription_cache(cache_path)
        if cached_result:
            return cached_result

    # Validate device
    device = check_whisper_device_compatibility(device)

    # Validate language
    if language and not validate_language_code(language):
        print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Language '{language}' not supported, using auto-detection")
        language = None

    # Show model information
    model_info = WhisperModel.get_model_info(model)
    if model_info:
        print(f"{ULTRASINGER_HEAD} Model: {blue_highlighted(model.value)} ({model_info['parameters']} parameters)")
        print(f"{ULTRASINGER_HEAD} VRAM Required: {blue_highlighted(model_info['vram_required'])}")
        print(f"{ULTRASINGER_HEAD} Speed: {blue_highlighted(model_info['relative_speed'])}")
        print(f"{ULTRASINGER_HEAD} Multilingual: {blue_highlighted(str(model_info['multilingual']))}")

    # Estimate processing time
    try:
        import librosa
        audio_duration = librosa.get_duration(path=audio_path)
        estimated_time = estimate_transcription_time(audio_duration, model, device)
        print(f"{ULTRASINGER_HEAD} Audio Duration: {blue_highlighted(f'{audio_duration:.1f}s')}")
        print(f"{ULTRASINGER_HEAD} Estimated Processing Time: {blue_highlighted(f'{estimated_time:.1f}s')}")
    except:
        print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Could not estimate processing time")
    # Info: Monkey Patch FasterWhisperPipeline.detect_language to include error handling for low confidence
    # Note: In WhisperX v3.4.3, we need to import the asr module directly
    try:
        from whisperx import asr
        src = textwrap.dedent(inspect.getsource(asr.FasterWhisperPipeline.detect_language))
        # Replace the relevant part of the method
        start_token = "if audio.shape[0] < N_SAMPLES:"
        end_token = "return language"
        replacement = """\
        #Added imports
        from modules.console_colors import ULTRASINGER_HEAD, blue_highlighted, red_highlighted
        from Settings import Settings
        from inputimeout import inputimeout, TimeoutOccurred
        #End Import addition
        if audio.shape[0] < N_SAMPLES:
            print("Warning: audio is shorter than 30s, language detection may be inaccurate.")
        model_n_mels = self.model.feat_kwargs.get("feature_size")
        segment = log_mel_spectrogram(audio[: N_SAMPLES],
                                        n_mels=model_n_mels if model_n_mels is not None else 80,
                                        padding=0 if audio.shape[0] >= N_SAMPLES else N_SAMPLES - audio.shape[0])
        encoder_output = self.model.encode(segment)
        results = self.model.model.detect_language(encoder_output)
        language_token, language_probability = results[0][0]
        language = language_token[2:-2]
        print(f"Detected language: {language} ({language_probability:.2f}) in first 30s of audio...")
        #Added handling for low detection probability
        if language_probability < Settings.CONFIDENCE_THRESHOLD:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Warning:')} Language detection probability for detected language {language} is below {Settings.CONFIDENCE_THRESHOLD}, results may be inaccurate.")
            print(f"{ULTRASINGER_HEAD} Override the language below or re-run with parameter {blue_highlighted('--language xx')} to specify the song language...")
            try:
                response = inputimeout(
                    prompt=f"{ULTRASINGER_HEAD} Do you want to continue with {language} (default) or override with another language (y)? (y/n): ",
                    timeout=Settings.CONFIDENCE_PROMPT_TIMEOUT
                ).strip().lower()
            except TimeoutOccurred:
                import locale
                print(f"{ULTRASINGER_HEAD} No user input received in {Settings.CONFIDENCE_PROMPT_TIMEOUT} seconds. Attempting automatic override with system locale.")
                print(f"{ULTRASINGER_HEAD} Trying to get language from default locale...")
                current_locale = locale.getlocale()
                if current_locale[0]:
                    language_code = current_locale[0][:2].strip().lower()
                    print(f"{ULTRASINGER_HEAD} Found language code: {language_code} in locale. Setting language to {blue_highlighted(language_code)}...")
                    language = language_code
                else:
                    print(f"{ULTRASINGER_HEAD} No locale is set.")
                response = 'n'
            language_response = response == 'y'
            if language_response:
                language = input(f"{ULTRASINGER_HEAD} Please enter the language code for the language you want to use (e.g. 'en', 'de', 'es', etc.): ").strip().lower()
        #End addition
        """
        new_src = replace_code_lines(src, start_token, end_token, replacement)
        # Compile it and execute it in the target module's namespace
        exec(compile(new_src, "<string>", "exec"), asr.__dict__)
        asr.FasterWhisperPipeline.detect_language = asr.detect_language
        print(f"{ULTRASINGER_HEAD} Successfully applied language detection patch for WhisperX v3.4.3")
    except ImportError as e:
        print(f"{ULTRASINGER_HEAD} {red_highlighted('Warning:')} Could not apply language detection patch: {e}")
        print(f"{ULTRASINGER_HEAD} Language detection will use default WhisperX behavior")
    except Exception as e:
        print(f"{ULTRASINGER_HEAD} {red_highlighted('Warning:')} Error applying language detection patch: {e}")
        print(f"{ULTRASINGER_HEAD} Language detection will use default WhisperX behavior")
    #End Monkey Patch

    # Info: Regardless of the audio sampling rate used in the original audio file, whisper resample the audio signal to 16kHz (via ffmpeg). So the standard input from (44.1 or 48 kHz) should work.

    print(f"{ULTRASINGER_HEAD} Loading {blue_highlighted('whisper')} with model {blue_highlighted(model.value)} and {red_highlighted(device)} as worker")

    if alignment_model is not None:
        print(f"{ULTRASINGER_HEAD} using alignment model {blue_highlighted(alignment_model)}")

    if compute_type is None:
        compute_type = "float16" if device == "cuda" else "int8"

    try:
        # Clear GPU cache before transcription
        if device == "cuda":
            torch.cuda.empty_cache()
        loaded_whisper_model = whisperx.load_model(
            model.value, language=language, device=device, compute_type=compute_type
        )

        audio = whisperx.load_audio(audio_path)

        print(f"{ULTRASINGER_HEAD} Transcribing {audio_path}")

        result = loaded_whisper_model.transcribe(
            audio, batch_size=batch_size, language=language
        )

        detected_language = result["language"]
        if language is None:
            language = detected_language

        print(f"{ULTRASINGER_HEAD} Detected language: {blue_highlighted(detected_language)}")

        # load alignment model and metadata
        try:
            model_a, metadata = whisperx.load_align_model(
                language_code=language, device=device, model_name=alignment_model
            )
        except ValueError as ve:
            print(
                f"{red_highlighted(f'{ve}')}"
                f"\n"
                f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Unknown language. "
                f"Try add it with --align_model [huggingface]."
            )
            raise ve

        #Addition for numbers to words (Using previous code from louispan in PR#135)
        if keep_numbers == False:
            for obj in result["segments"]:
                obj["text"] = number_to_words(obj["text"], language)

        # align whisper output
        result_aligned = whisperx.align(
            result["segments"],
            model_a,
            metadata,
            audio,
            device,
            return_char_alignments=False,
        )

        transcribed_data = convert_to_transcribed_data(result_aligned)
        transcription_result = TranscriptionResult(transcribed_data, detected_language)

        # Save to cache
        if cache_path:
            save_transcription_cache(cache_path, transcription_result)

        print(f"{ULTRASINGER_HEAD} {green_highlighted('Success:')} Transcription completed successfully")
        print(f"{ULTRASINGER_HEAD} Transcribed {blue_highlighted(str(len(transcribed_data)))} words")

        return transcription_result
    except ValueError as value_error:
        if (
            "Requested float16 compute type, but the target device or backend do not support efficient float16 computation."
            in str(value_error.args[0])
        ):
            print(value_error)
            print(
                f"{ULTRASINGER_HEAD} Your GPU does not support efficient float16 computation; run UltraSinger with '--whisper_compute_type int8'"
            )

        raise value_error
    except OutOfMemoryError as oom_exception:
        print(oom_exception)
        print(MEMORY_ERROR_MESSAGE)
        print(f"{ULTRASINGER_HEAD} Try:")
        print(f"  - Smaller model: {WhisperModel.SMALL.value} or {WhisperModel.BASE.value}")
        print(f"  - Reduce batch size: --whisper_batch_size 8")
        print(f"  - Use CPU: --force_whisper_cpu")
        raise oom_exception
    except Exception as exception:
        # Verificar se existe args antes de acessar (correção para whisperx 3.4.3+)
        # Se usando whisperx 3.1.5, este código é redundante mas não causa problemas
        if hasattr(exception, 'args') and len(exception.args) > 0:
            if "CUDA failed with error out of memory" in str(exception.args[0]):
                print(exception)
                print(MEMORY_ERROR_MESSAGE)
        print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Transcription failed: {str(exception)}")
        raise exception


def convert_to_transcribed_data(result_aligned):
    transcribed_data = []
    for segment in result_aligned["segments"]:
        for obj in segment["words"]:
            vtd = from_whisper(obj)  # create custom Word object
            vtd.word = vtd.word + " "  # add space to end of word
            if len(obj) < 4:
                #Addition for numbers to words (Using previous code from louispan in PR#135)
                if len(transcribed_data) == 0: # if the first word doesn't have any timing data
                    vtd.start = 0.0
                    vtd.end = 0.1
                    msg = f'Error: There is no timestamp for word: "{obj["word"]}". ' \
                        f'Fixing it by placing it at beginning. At start: {vtd.start} end: {vtd.end}. Fix it manually!'
                else:
                    previous = transcribed_data[-1] if len(transcribed_data) != 0 else TranscribedData()
                    vtd.start = previous.end + 0.1
                    vtd.end = previous.end + 0.2
                    msg = f'Error: There is no timestamp for word: "{obj["word"]}". ' \
                          f'Fixing it by placing it after the previous word: "{previous.word}". At start: {vtd.start} end: {vtd.end}. Fix it manually!'
                print(f"{red_highlighted(msg)}")
            transcribed_data.append(vtd)  # and add it to list
    return transcribed_data

def get_available_models() -> List[WhisperModel]:
    """Get list of available Whisper models"""
    return list(WhisperModel)

def get_multilingual_models() -> List[WhisperModel]:
    """Get list of multilingual Whisper models"""
    return [model for model in WhisperModel if WhisperModel.get_model_info(model).get("multilingual", True)]

def get_english_only_models() -> List[WhisperModel]:
    """Get list of English-only Whisper models"""
    return [model for model in WhisperModel if not WhisperModel.get_model_info(model).get("multilingual", True)]

def validate_transcription_quality(transcribed_data: List[TranscribedData]) -> Dict:
    """Validate the quality of transcription results"""
    if not transcribed_data:
        return {
            "word_count": 0,
            "avg_confidence": 0.0,
            "timing_gaps": 0,
            "quality_score": 0.0
        }

    word_count = len(transcribed_data)
    timing_gaps = 0

    # Check for timing gaps
    for i in range(1, len(transcribed_data)):
        if transcribed_data[i].start > transcribed_data[i-1].end + 0.5:  # Gap > 0.5s
            timing_gaps += 1

    # Calculate quality score
    quality_score = 1.0
    if timing_gaps > word_count * 0.1:  # More than 10% gaps
        quality_score -= 0.3
    if word_count < 10:  # Very short transcription
        quality_score -= 0.2

    return {
        "word_count": word_count,
        "timing_gaps": timing_gaps,
        "quality_score": max(0.0, quality_score)
    }
