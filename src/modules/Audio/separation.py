"""Separate vocals from audio"""
import os
import shutil
from enum import Enum
from typing import Optional, Tuple

import demucs.separate
import torch

from modules.console_colors import (
    ULTRASINGER_HEAD,
    blue_highlighted,
    red_highlighted, 
    green_highlighted,
    yellow_highlighted
)
from modules.os_helper import check_file_exists

class DemucsModel(Enum):
    HTDEMUCS = "htdemucs"           # first version of Hybrid Transformer Demucs. Trained on MusDB + 800 songs. Default model.
    HTDEMUCS_FT = "htdemucs_ft"     # fine-tuned version of htdemucs, separation will take 4 times more time but might be a bit better. Same training set as htdemucs.
    HTDEMUCS_6S = "htdemucs_6s"     # 6 sources version of htdemucs, with piano and guitar being added as sources. Note that the piano source is not working great at the moment.
    HDEMUCS_MMI = "hdemucs_mmi"     # Hybrid Demucs v3, retrained on MusDB + 800 songs.
    MDX = "mdx"                     # trained only on MusDB HQ, winning model on track A at the MDX challenge.
    MDX_EXTRA = "mdx_extra"         # trained with extra training data (including MusDB test set), ranked 2nd on the track B of the MDX challenge.
    MDX_Q = "mdx_q"                 # quantized version of the previous models. Smaller download and storage but quality can be slightly worse.
    MDX_EXTRA_Q = "mdx_extra_q"     # quantized version of mdx_extra. Smaller download and storage but quality can be slightly worse.
    SIG = "SIG"                     # Placeholder for a single model from the model zoo.

    @classmethod
    def get_model_info(cls, model: 'DemucsModel') -> dict:
        """Get detailed information about a specific model"""
        model_info = {
            cls.HTDEMUCS: {
                "description": "Hybrid Transformer Demucs - Default model, good balance of quality and speed",
                "quality": "High",
                "speed": "Fast",
                "sources": 4,
                "recommended_for": "General use"
            },
            cls.HTDEMUCS_FT: {
                "description": "Fine-tuned HTDEMUCS - Better quality but 4x slower",
                "quality": "Very High",
                "speed": "Slow",
                "sources": 4,
                "recommended_for": "High quality separation"
            },
            cls.HTDEMUCS_6S: {
                "description": "6-source HTDEMUCS - Includes piano and guitar separation",
                "quality": "High",
                "speed": "Medium",
                "sources": 6,
                "recommended_for": "Complex music with multiple instruments"
            },
            cls.HDEMUCS_MMI: {
                "description": "Hybrid Demucs v3 - Retrained version",
                "quality": "High",
                "speed": "Fast",
                "sources": 4,
                "recommended_for": "Alternative to HTDEMUCS"
            },
            cls.MDX: {
                "description": "MDX Challenge winner - Excellent for vocals",
                "quality": "Very High",
                "speed": "Medium",
                "sources": 4,
                "recommended_for": "Vocal-focused separation"
            },
            cls.MDX_EXTRA: {
                "description": "MDX with extra training data - Top quality",
                "quality": "Excellent",
                "speed": "Medium",
                "sources": 4,
                "recommended_for": "Professional vocal separation"
            },
            cls.MDX_Q: {
                "description": "Quantized MDX - Smaller size, slightly lower quality",
                "quality": "High",
                "speed": "Fast",
                "sources": 4,
                "recommended_for": "Limited storage/memory"
            },
            cls.MDX_EXTRA_Q: {
                "description": "Quantized MDX Extra - Best balance of size and quality",
                "quality": "Very High",
                "speed": "Fast",
                "sources": 4,
                "recommended_for": "Optimal balance"
            },
            cls.SIG: {
                "description": "Single model from model zoo",
                "quality": "Variable",
                "speed": "Variable",
                "sources": 4,
                "recommended_for": "Experimental use"
            }
        }
        return model_info.get(model, {})

def check_device_compatibility(device: str) -> str:
    """Check and validate device compatibility"""
    if device == "cuda":
        if not torch.cuda.is_available():
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} CUDA not available, falling back to CPU")
            return "cpu"
        else:
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
            print(f"{ULTRASINGER_HEAD} Using GPU: {blue_highlighted(gpu_name)} (CUDA {torch.version.cuda})")
            return "cuda"
    return "cpu"

def estimate_memory_usage(model: DemucsModel, device: str) -> dict:
    """Estimate memory usage for different models"""
    base_memory = {
        "cpu": {"ram": 2.0},  # GB
        "cuda": {"vram": 1.5, "ram": 1.0}  # GB
    }
    
    model_multipliers = {
        DemucsModel.HTDEMUCS: 1.0,
        DemucsModel.HTDEMUCS_FT: 1.2,
        DemucsModel.HTDEMUCS_6S: 1.5,
        DemucsModel.HDEMUCS_MMI: 1.1,
        DemucsModel.MDX: 1.3,
        DemucsModel.MDX_EXTRA: 1.4,
        DemucsModel.MDX_Q: 0.8,
        DemucsModel.MDX_EXTRA_Q: 0.9,
        DemucsModel.SIG: 1.0
    }
    
    multiplier = model_multipliers.get(model, 1.0)
    memory_info = base_memory[device].copy()
    
    for key in memory_info:
        memory_info[key] *= multiplier
    
    return memory_info

def separate_audio(input_file_path: str, output_folder: str, model: DemucsModel, device="cpu", 
                  shifts: int = 1, overlap: float = 0.25, jobs: int = 0) -> None:
    """Separate vocals from audio with demucs with advanced options."""
    
    # Validate device
    device = check_device_compatibility(device)
    
    # Show memory estimation
    memory_info = estimate_memory_usage(model, device)
    if device == "cuda":
        vram_usage = f"{memory_info['vram']:.1f} GB"
        print(f"{ULTRASINGER_HEAD} Estimated VRAM usage: {blue_highlighted(vram_usage)}")
    ram_usage = f"{memory_info['ram']:.1f} GB"
    print(f"{ULTRASINGER_HEAD} Estimated RAM usage: {blue_highlighted(ram_usage)}")

    model_info = DemucsModel.get_model_info(model)
    if model_info:
        print(f"{ULTRASINGER_HEAD} Model: {blue_highlighted(model.value)} - {model_info['description']}")
        print(f"{ULTRASINGER_HEAD} Quality: {blue_highlighted(model_info['quality'])}, Speed: {blue_highlighted(model_info['speed'])}")

    print(f"{ULTRASINGER_HEAD} Separating vocals from audio with {blue_highlighted('demucs')} using {red_highlighted(device)} as worker.")

    # Prepare demucs arguments
    demucs_args = [
        "--two-stems", "vocals",
        "-d", f"{device}",
        "--float32",
        "-n", model.value,
        "--out", f"{os.path.join(output_folder, 'separated')}",
    ]
    
    # Add advanced options
    if shifts > 1:
        demucs_args.extend(["--shifts", str(shifts)])
        print(f"{ULTRASINGER_HEAD} Using {blue_highlighted(str(shifts))} shifts for better quality")
    
    if overlap != 0.25:
        demucs_args.extend(["--overlap", str(overlap)])
        print(f"{ULTRASINGER_HEAD} Using overlap of {blue_highlighted(str(overlap))}")
    
    if jobs > 0:
        demucs_args.extend(["--jobs", str(jobs)])
        print(f"{ULTRASINGER_HEAD} Using {blue_highlighted(str(jobs))} parallel jobs")
    
    demucs_args.append(f"{input_file_path}")

    try:
        # Clear GPU cache before separation
        if device == "cuda":
            torch.cuda.empty_cache()
        
        demucs.separate.main(demucs_args)
        
        print(f"{ULTRASINGER_HEAD} {green_highlighted('Success:')} Audio separation completed successfully")
        
    except Exception as e:
        if "out of memory" in str(e).lower() or "cuda" in str(e).lower():
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} GPU out of memory. Try:")
            print(f"  - Using CPU: --force_cpu")
            print(f"  - Smaller model: {DemucsModel.MDX_Q.value} or {DemucsModel.MDX_EXTRA_Q.value}")
            print(f"  - Reduce shifts: --shifts 1")
        else:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Separation failed: {str(e)}")
        raise e

def separate_vocal_from_audio(cache_folder_path: str,
                              audio_output_file_path: str,
                              use_separated_vocal: bool,
                              create_karaoke: bool,
                              pytorch_device: str,
                              model: DemucsModel,
                              skip_cache: bool = False,
                              shifts: int = 1,
                              overlap: float = 0.25,
                              jobs: int = 0) -> str:
    """Separate vocal from audio with enhanced caching and options"""
    
    demucs_output_folder = os.path.splitext(os.path.basename(audio_output_file_path))[0]
    audio_separation_path = os.path.join(cache_folder_path, "separated", model.value, demucs_output_folder)

    vocals_path = os.path.join(audio_separation_path, "vocals.wav")
    instrumental_path = os.path.join(audio_separation_path, "no_vocals.wav")
    
    if use_separated_vocal or create_karaoke:
        cache_available = check_file_exists(vocals_path) and check_file_exists(instrumental_path)
        
        if skip_cache or not cache_available:
            print(f"{ULTRASINGER_HEAD} Starting vocal separation...")
            
            # Create output directory if it doesn't exist
            os.makedirs(audio_separation_path, exist_ok=True)
            
            try:
                separate_audio(audio_output_file_path, cache_folder_path, model, pytorch_device, shifts, overlap, jobs)
                
                # Verify separation was successful
                if not (check_file_exists(vocals_path) and check_file_exists(instrumental_path)):
                    raise FileNotFoundError("Separation completed but output files not found")
                    
                # Show file sizes for verification
                vocals_size = os.path.getsize(vocals_path) / (1024 * 1024)  # MB
                instrumental_size = os.path.getsize(instrumental_path) / (1024 * 1024)  # MB
                print(f"{ULTRASINGER_HEAD} Generated files:")
                print(f"  - Vocals: {blue_highlighted(f'{vocals_size:.1f} MB')}")
                print(f"  - Instrumental: {blue_highlighted(f'{instrumental_size:.1f} MB')}")
                
            except Exception as e:
                print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Vocal separation failed: {str(e)}")
                # Clean up partial files
                if os.path.exists(audio_separation_path):
                    shutil.rmtree(audio_separation_path, ignore_errors=True)
                raise e
        else:
            print(f"{ULTRASINGER_HEAD} {green_highlighted('cache')} reusing cached separated vocals")
            # Show cached file info
            vocals_size = os.path.getsize(vocals_path) / (1024 * 1024)  # MB
            instrumental_size = os.path.getsize(instrumental_path) / (1024 * 1024)  # MB
            print(f"{ULTRASINGER_HEAD} Cached files:")
            print(f"  - Vocals: {blue_highlighted(f'{vocals_size:.1f} MB')}")
            print(f"  - Instrumental: {blue_highlighted(f'{instrumental_size:.1f} MB')}")

    return audio_separation_path

def get_available_models() -> list[DemucsModel]:
    """Get list of available Demucs models"""
    return list(DemucsModel)

def get_recommended_model(use_case: str = "general") -> DemucsModel:
    """Get recommended model based on use case"""
    recommendations = {
        "general": DemucsModel.HTDEMUCS,
        "high_quality": DemucsModel.MDX_EXTRA,
        "fast": DemucsModel.MDX_Q,
        "vocal_focused": DemucsModel.MDX,
        "complex_music": DemucsModel.HTDEMUCS_6S,
        "low_memory": DemucsModel.MDX_EXTRA_Q
    }
    return recommendations.get(use_case, DemucsModel.HTDEMUCS)

def validate_separation_quality(vocals_path: str, instrumental_path: str) -> dict:
    """Validate the quality of separation results"""
    results = {
        "vocals_exists": check_file_exists(vocals_path),
        "instrumental_exists": check_file_exists(instrumental_path),
        "vocals_size": 0,
        "instrumental_size": 0,
        "quality_score": 0.0
    }
    
    if results["vocals_exists"]:
        results["vocals_size"] = os.path.getsize(vocals_path)
    
    if results["instrumental_exists"]:
        results["instrumental_size"] = os.path.getsize(instrumental_path)
    
    # Basic quality assessment based on file sizes
    if results["vocals_exists"] and results["instrumental_exists"]:
        if results["vocals_size"] > 1000 and results["instrumental_size"] > 1000:  # At least 1KB each
            results["quality_score"] = 1.0
        else:
            results["quality_score"] = 0.5
    
    return results
