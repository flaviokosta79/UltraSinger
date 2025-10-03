"""Enhanced Pitcher module with Crepe pitch detection"""
import os
import json
import numpy as np
import torch
from enum import Enum
from typing import Optional, Dict, List, Tuple

import crepe
from scipy.io import wavfile

from modules.console_colors import ULTRASINGER_HEAD, blue_highlighted, red_highlighted, green_highlighted, yellow_highlighted
from modules.Midi.midi_creator import convert_frequencies_to_notes, most_frequent
from modules.Pitcher.pitched_data import PitchedData
from modules.Pitcher.pitched_data_helper import get_frequencies_with_high_confidence

class CrepeModel(Enum):
    """Crepe model capacities with detailed information"""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    FULL = "full"
    
    @classmethod
    def get_model_info(cls, model: 'CrepeModel') -> dict:
        """Get detailed information about a specific model"""
        model_info = {
            cls.TINY: {
                "parameters": "~0.5M",
                "vram_required": "~0.5GB",
                "relative_speed": "~8x",
                "accuracy": "Low",
                "description": "Fastest model, lowest accuracy"
            },
            cls.SMALL: {
                "parameters": "~1M", 
                "vram_required": "~1GB",
                "relative_speed": "~4x",
                "accuracy": "Medium-Low",
                "description": "Good balance of speed and accuracy"
            },
            cls.MEDIUM: {
                "parameters": "~2M",
                "vram_required": "~2GB", 
                "relative_speed": "~2x",
                "accuracy": "Medium",
                "description": "Better accuracy, moderate speed"
            },
            cls.LARGE: {
                "parameters": "~4M",
                "vram_required": "~3GB",
                "relative_speed": "~1.5x", 
                "accuracy": "High",
                "description": "High accuracy, slower processing"
            },
            cls.FULL: {
                "parameters": "~8M",
                "vram_required": "~4GB",
                "relative_speed": "1x",
                "accuracy": "Highest",
                "description": "Highest accuracy, slowest processing"
            }
        }
        return model_info.get(model, {})
    
    @classmethod
    def get_recommended_model(cls, device: str = "cpu", vram_gb: float = 2.0, quality_priority: str = "balanced") -> 'CrepeModel':
        """Get recommended model based on device, VRAM and quality priority"""
        if quality_priority == "speed":
            return cls.TINY if device == "cpu" else cls.SMALL
        elif quality_priority == "quality":
            if device == "cpu":
                return cls.MEDIUM
            elif vram_gb >= 4:
                return cls.FULL
            elif vram_gb >= 3:
                return cls.LARGE
            else:
                return cls.MEDIUM
        else:  # balanced
            if device == "cpu":
                return cls.SMALL
            elif vram_gb >= 3:
                return cls.LARGE
            elif vram_gb >= 2:
                return cls.MEDIUM
            else:
                return cls.SMALL

def check_crepe_device_compatibility(device: str) -> str:
    """Check and validate Crepe device compatibility"""
    if device == "cuda":
        if not torch.cuda.is_available():
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} CUDA not available for Crepe, falling back to CPU")
            return "cpu"
        else:
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
            print(f"{ULTRASINGER_HEAD} GPU Memory Available: {blue_highlighted(f'{gpu_memory:.1f} GB')}")
            return "cuda"
    return "cpu"

def estimate_pitch_detection_time(audio_duration_seconds: float, model: CrepeModel, step_size: int, device: str) -> float:
    """Estimate pitch detection time based on audio duration, model, step size and device"""
    model_info = CrepeModel.get_model_info(model)
    
    # Base processing time per second of audio
    base_time_per_second = {
        "cpu": 2.0,  # seconds of processing per second of audio
        "cuda": 0.3
    }
    
    # Model speed multipliers
    speed_multipliers = {
        CrepeModel.TINY: 8,
        CrepeModel.SMALL: 4,
        CrepeModel.MEDIUM: 2,
        CrepeModel.LARGE: 1.5,
        CrepeModel.FULL: 1
    }
    
    # Step size affects processing time (smaller step = more processing)
    step_size_multiplier = 10.0 / step_size  # Default step size is 10ms
    
    base_time = base_time_per_second.get(device, 2.0)
    speed_multiplier = speed_multipliers.get(model, 1)
    
    estimated_time = (audio_duration_seconds * base_time * step_size_multiplier) / speed_multiplier
    return max(estimated_time, 1.0)  # Minimum 1 second

def validate_step_size(step_size: int) -> int:
    """Validate and adjust step size for optimal performance"""
    if step_size < 1:
        print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Step size too small, setting to 1ms")
        return 1
    elif step_size > 100:
        print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Step size too large, setting to 100ms")
        return 100
    return step_size

def save_pitch_cache(cache_path: str, pitched_data: PitchedData) -> None:
    """Save pitch detection result to cache"""
    try:
        cache_data = {
            "times": pitched_data.times.tolist() if hasattr(pitched_data.times, 'tolist') else list(pitched_data.times),
            "frequencies": pitched_data.frequencies.tolist() if hasattr(pitched_data.frequencies, 'tolist') else list(pitched_data.frequencies),
            "confidence": pitched_data.confidence if isinstance(pitched_data.confidence, list) else list(pitched_data.confidence)
        }
        
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
        print(f"{ULTRASINGER_HEAD} {green_highlighted('cache')} Pitch data saved to cache")
        
    except Exception as e:
        print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to save pitch cache: {str(e)}")

def load_pitch_cache(cache_path: str) -> Optional[PitchedData]:
    """Load pitch detection result from cache"""
    try:
        if not os.path.exists(cache_path):
            return None
            
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        pitched_data = PitchedData(
            times=np.array(cache_data["times"]),
            frequencies=np.array(cache_data["frequencies"]),
            confidence=cache_data["confidence"]
        )
        
        print(f"{ULTRASINGER_HEAD} {green_highlighted('cache')} Loaded pitch data from cache")
        return pitched_data
        
    except Exception as e:
        print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to load pitch cache: {str(e)}")
        return None

def validate_pitch_quality(pitched_data: PitchedData, confidence_threshold: float = 0.4) -> Dict:
    """Validate the quality of pitch detection results"""
    if not pitched_data.confidence:
        return {
            "total_frames": 0,
            "high_confidence_frames": 0,
            "confidence_ratio": 0.0,
            "avg_confidence": 0.0,
            "quality_score": 0.0
        }
    
    total_frames = len(pitched_data.confidence)
    high_confidence_frames = sum(1 for conf in pitched_data.confidence if conf > confidence_threshold)
    confidence_ratio = high_confidence_frames / total_frames if total_frames > 0 else 0.0
    avg_confidence = sum(pitched_data.confidence) / total_frames if total_frames > 0 else 0.0
    
    # Calculate quality score
    quality_score = (confidence_ratio * 0.7) + (avg_confidence * 0.3)
    
    return {
        "total_frames": total_frames,
        "high_confidence_frames": high_confidence_frames,
        "confidence_ratio": confidence_ratio,
        "avg_confidence": avg_confidence,
        "quality_score": quality_score
    }

def get_pitch_with_crepe_file(
    filename: str, 
    model_capacity: str, 
    step_size: int = 10, 
    device: str = "cpu",
    cache_path: str = None,
    skip_cache: bool = False
) -> PitchedData:
    """Enhanced pitch detection with crepe from file"""
    
    # Check cache first
    if cache_path and not skip_cache:
        cached_result = load_pitch_cache(cache_path)
        if cached_result:
            return cached_result
    
    # Validate device
    device = check_crepe_device_compatibility(device)
    
    # Validate step size
    step_size = validate_step_size(step_size)
    
    # Convert string model to enum if needed
    if isinstance(model_capacity, str):
        try:
            model_enum = CrepeModel(model_capacity.lower())
        except ValueError:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Unknown model '{model_capacity}', using 'medium'")
            model_enum = CrepeModel.MEDIUM
    else:
        model_enum = model_capacity
    
    # Show model information
    model_info = CrepeModel.get_model_info(model_enum)
    if model_info:
        print(f"{ULTRASINGER_HEAD} Model: {blue_highlighted(model_enum.value)} ({model_info['parameters']} parameters)")
        print(f"{ULTRASINGER_HEAD} VRAM Required: {blue_highlighted(model_info['vram_required'])}")
        print(f"{ULTRASINGER_HEAD} Speed: {blue_highlighted(model_info['relative_speed'])}")
        print(f"{ULTRASINGER_HEAD} Accuracy: {blue_highlighted(model_info['accuracy'])}")

    print(f"{ULTRASINGER_HEAD} Pitching with {blue_highlighted('crepe')} and model {blue_highlighted(model_enum.value)} and {red_highlighted(device)} as worker")
    
    try:
        sample_rate, audio = wavfile.read(filename)
        
        # Estimate processing time
        try:
            audio_duration = len(audio) / sample_rate
            estimated_time = estimate_pitch_detection_time(audio_duration, model_enum, step_size, device)
            print(f"{ULTRASINGER_HEAD} Audio Duration: {blue_highlighted(f'{audio_duration:.1f}s')}")
            print(f"{ULTRASINGER_HEAD} Step Size: {blue_highlighted(f'{step_size}ms')}")
            print(f"{ULTRASINGER_HEAD} Estimated Processing Time: {blue_highlighted(f'{estimated_time:.1f}s')}")
        except:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Could not estimate processing time")
        
        pitched_data = get_pitch_with_crepe(audio, sample_rate, model_enum.value, step_size, device)
        
        # Validate quality
        quality_info = validate_pitch_quality(pitched_data)
        quality_score = f"{quality_info['quality_score']:.2f}"
        confidence_text = f"{quality_info['high_confidence_frames']}/{quality_info['total_frames']} ({quality_info['confidence_ratio']:.1%})"
        print(f"{ULTRASINGER_HEAD} Quality Score: {blue_highlighted(quality_score)}")
        print(f"{ULTRASINGER_HEAD} High Confidence Frames: {blue_highlighted(confidence_text)}")
        
        # Save to cache
        if cache_path:
            save_pitch_cache(cache_path, pitched_data)
        
        print(f"{ULTRASINGER_HEAD} {green_highlighted('Success:')} Pitch detection completed successfully")
        
        return pitched_data
        
    except Exception as e:
        print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Pitch detection failed: {str(e)}")
        raise e

def get_pitch_with_crepe(
    audio, 
    sample_rate: int, 
    model_capacity: str, 
    step_size: int = 10,
    device: str = "cpu"
) -> PitchedData:
    """Enhanced pitch detection with crepe from audio data"""

    # Info: The model is trained on 16 kHz audio, so if the input audio has a different sample rate, it will be first resampled to 16 kHz using resampy inside crepe.
    
    try:
        # Clear GPU cache if using CUDA
        if device == "cuda":
            torch.cuda.empty_cache()
            
        times, frequencies, confidence, activation = crepe.predict(
            audio, sample_rate, model_capacity, step_size=step_size, viterbi=True
        )

        # convert to native float for serialization
        confidence = [float(x) for x in confidence]

        return PitchedData(times, frequencies, confidence)
        
    except Exception as e:
        if "CUDA out of memory" in str(e):
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} GPU out of memory for pitch detection")
            print(f"{ULTRASINGER_HEAD} Try:")
            print(f"  - Smaller model: {CrepeModel.SMALL.value} or {CrepeModel.TINY.value}")
            print(f"  - Larger step size: --crepe_step_size 20")
            print(f"  - Use CPU: --force_crepe_cpu")
        print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Pitch detection failed: {str(e)}")
        raise e

def get_pitched_data_with_high_confidence(
    pitched_data: PitchedData, threshold: float = 0.4
) -> PitchedData:
    """Get frequency with high confidence - enhanced version"""
    if not pitched_data.confidence:
        print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} No confidence data available")
        return pitched_data
    
    new_pitched_data = PitchedData([], [], [])
    high_conf_count = 0
    
    for i, conf in enumerate(pitched_data.confidence):
        if conf > threshold:
            new_pitched_data.times.append(pitched_data.times[i])
            new_pitched_data.frequencies.append(pitched_data.frequencies[i])
            new_pitched_data.confidence.append(pitched_data.confidence[i])
            high_conf_count += 1

    total_frames = len(pitched_data.confidence)
    confidence_ratio = high_conf_count / total_frames if total_frames > 0 else 0.0
    
    print(f"{ULTRASINGER_HEAD} High confidence frames: {blue_highlighted(f'{high_conf_count}/{total_frames} ({confidence_ratio:.1%})')}")
    
    if confidence_ratio < 0.3:
        print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Low confidence ratio, consider using a different model or adjusting parameters")
    
    return new_pitched_data

def get_available_models() -> List[CrepeModel]:
    """Get list of available Crepe models"""
    return list(CrepeModel)

def get_optimal_step_size(audio_duration: float, target_frames: int = 1000) -> int:
    """Calculate optimal step size based on audio duration and target frame count"""
    # Calculate step size to get approximately target_frames
    optimal_step = max(1, int((audio_duration * 1000) / target_frames))  # Convert to milliseconds
    
    # Clamp to reasonable range
    optimal_step = max(1, min(100, optimal_step))
    
    return optimal_step

def analyze_pitch_statistics(pitched_data: PitchedData) -> Dict:
    """Analyze pitch statistics for quality assessment"""
    if not pitched_data.frequencies:
        return {}
    
    frequencies = np.array(pitched_data.frequencies)
    confidence = np.array(pitched_data.confidence)
    
    # Filter out zero frequencies (silence)
    non_zero_freq = frequencies[frequencies > 0]
    
    if len(non_zero_freq) == 0:
        return {"error": "No valid frequencies detected"}
    
    stats = {
        "min_frequency": float(np.min(non_zero_freq)),
        "max_frequency": float(np.max(non_zero_freq)),
        "mean_frequency": float(np.mean(non_zero_freq)),
        "median_frequency": float(np.median(non_zero_freq)),
        "frequency_std": float(np.std(non_zero_freq)),
        "min_confidence": float(np.min(confidence)),
        "max_confidence": float(np.max(confidence)),
        "mean_confidence": float(np.mean(confidence)),
        "silence_ratio": float(np.sum(frequencies == 0) / len(frequencies))
    }
    
    return stats

# Todo: Unused - keeping for compatibility
def pitch_each_chunk_with_crepe(directory: str,
                                crepe_model_capacity: str,
                                crepe_step_size: int,
                                tensorflow_device: str) -> list[str]:
    """Pitch each chunk with crepe and return midi notes"""
    print(f"{ULTRASINGER_HEAD} Pitching each chunk with {blue_highlighted('crepe')}")

    midi_notes = []
    for filename in sorted(
            [f for f in os.listdir(directory) if f.endswith(".wav")],
            key=lambda x: int(x.split("_")[1]),
    ):
        filepath = os.path.join(directory, filename)
        # todo: stepsize = duration? then when shorter than "it" it should take the duration. Otherwise there a more notes
        pitched_data = get_pitch_with_crepe_file(
            filepath,
            crepe_model_capacity,
            crepe_step_size,
            tensorflow_device,
        )
        conf_f = get_frequencies_with_high_confidence(
            pitched_data.frequencies, pitched_data.confidence
        )

        notes = convert_frequencies_to_notes(conf_f)
        note = most_frequent(notes)[0][0]

        midi_notes.append(note)
        # todo: Progress?
        # print(filename + " f: " + str(mean))

    return midi_notes

class Pitcher:
    """Enhanced Pitcher class with advanced pitch detection capabilities"""
    
    def __init__(self, model: CrepeModel = CrepeModel.MEDIUM, device: str = "cpu", step_size: int = 10):
        self.model = model
        self.device = check_crepe_device_compatibility(device)
        self.step_size = validate_step_size(step_size)
        
    def detect_pitch(self, audio_path: str, cache_path: str = None) -> PitchedData:
        """Detect pitch from audio file"""
        return get_pitch_with_crepe_file(
            audio_path, 
            self.model.value, 
            self.step_size, 
            self.device,
            cache_path
        )
    
    def get_model_info(self) -> Dict:
        """Get information about current model"""
        return CrepeModel.get_model_info(self.model)
    
    def set_model(self, model: CrepeModel):
        """Set pitch detection model"""
        self.model = model
        
    def set_device(self, device: str):
        """Set processing device"""
        self.device = check_crepe_device_compatibility(device)
        
    def set_step_size(self, step_size: int):
        """Set step size for pitch detection"""
        self.step_size = validate_step_size(step_size)
