"""
SpeechBrain Integration Module

Main integration module that connects all SpeechBrain components with UltraSinger,
providing a unified interface for advanced audio separation and ASR for karaoke creation.
"""

import os
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import json

from modules.console_colors import (
    ULTRASINGER_HEAD,
    blue_highlighted,
    green_highlighted,
    yellow_highlighted,
    red_highlighted
)
from modules.os_helper import check_file_exists

from .config_manager import SpeechBrainConfig, ProcessingMode
from .model_manager import SpeechBrainModelManager
from .sepformer_separation import SepFormerSeparator, SepFormerModel
from .conformer_asr import ConformerASR, ASRModel, TranscriptionResult
from .forced_alignment import ForcedAligner, AlignmentModel, AlignmentResult
from .vad_system import VADSystem, VADModel, VADResult
from .llm_rescoring import LLMRescorer, LLMModel, RescoringResult


class SpeechBrainPipeline:
    """Complete SpeechBrain processing pipeline for karaoke creation"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize SpeechBrain pipeline
        
        Args:
            config_path: Path to configuration file (optional)
        """
        # Load configuration
        self.config = SpeechBrainConfig()
        if config_path and os.path.exists(config_path):
            self.config.load_config(config_path)
        
        # Initialize components
        self.model_manager = SpeechBrainModelManager(self.config)
        self.separator = SepFormerSeparator(self.config, self.model_manager)
        self.asr = ConformerASR(self.config, self.model_manager)
        self.aligner = ForcedAligner(self.config, self.model_manager)
        self.vad = VADSystem(self.config, self.model_manager)
        self.rescorer = LLMRescorer(self.config)
        
        # Pipeline statistics
        self.pipeline_stats = {
            "total_processed": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "successful_separations": 0,
            "successful_transcriptions": 0,
            "successful_alignments": 0,
            "successful_vad": 0,
            "successful_rescoring": 0
        }
        
        print(f"{ULTRASINGER_HEAD} {green_highlighted('SpeechBrain Pipeline initialized')}")
        print(f"{ULTRASINGER_HEAD} Device: {blue_highlighted(self.config.device)}")
        print(f"{ULTRASINGER_HEAD} Processing mode: {blue_highlighted(self.config.processing_mode.value)}")
    
    def process_audio_for_karaoke(self,
                                 input_path: str,
                                 output_dir: str,
                                 language: str = "en",
                                 lyrics_text: Optional[str] = None,
                                 processing_mode: Optional[ProcessingMode] = None) -> Dict[str, Any]:
        """
        Complete pipeline for processing audio into karaoke format
        
        Args:
            input_path: Path to input audio file
            output_dir: Directory for output files
            language: Language code for ASR
            lyrics_text: Optional reference lyrics for alignment
            processing_mode: Processing mode override
            
        Returns:
            Dictionary with all processing results
        """
        start_time = time.time()
        
        print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('Starting SpeechBrain Karaoke Pipeline')}")
        print(f"{ULTRASINGER_HEAD} Input: {blue_highlighted(os.path.basename(input_path))}")
        print(f"{ULTRASINGER_HEAD} Language: {blue_highlighted(language)}")
        
        # Validate input
        if not check_file_exists(input_path):
            raise FileNotFoundError(f"Input audio file not found: {input_path}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Override processing mode if specified
        if processing_mode:
            self.config.processing_mode = processing_mode
        
        results = {
            "input_path": input_path,
            "output_dir": output_dir,
            "language": language,
            "processing_mode": self.config.processing_mode.value,
            "separation": None,
            "vad": None,
            "transcription": None,
            "rescoring": None,
            "alignment": None,
            "processing_time": 0.0,
            "success": False
        }
        
        try:
            # Step 1: Audio Separation
            print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('Step 1: Audio Separation')}")
            separation_result = self._perform_separation(input_path, output_dir)
            results["separation"] = separation_result
            
            # Use vocal track for further processing
            vocal_path = separation_result.get("vocal_path")
            if not vocal_path or not os.path.exists(vocal_path):
                raise RuntimeError("Vocal separation failed")
            
            # Step 2: Voice Activity Detection
            print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('Step 2: Voice Activity Detection')}")
            vad_result = self._perform_vad(vocal_path)
            results["vad"] = vad_result.to_dict()
            
            # Step 3: Speech Recognition
            print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('Step 3: Speech Recognition')}")
            transcription_result = self._perform_transcription(vocal_path, language)
            results["transcription"] = transcription_result.to_dict()
            
            # Step 4: LLM Rescoring (if enabled)
            if self.config.llm.enabled:
                print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('Step 4: LLM Rescoring')}")
                rescoring_result = self._perform_rescoring(transcription_result.text, language)
                results["rescoring"] = rescoring_result.to_dict()
                final_text = rescoring_result.rescored_text
            else:
                final_text = transcription_result.text
                print(f"\n{ULTRASINGER_HEAD} {yellow_highlighted('Step 4: LLM Rescoring skipped (disabled)')}")
            
            # Step 5: Forced Alignment
            print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('Step 5: Forced Alignment')}")
            alignment_text = lyrics_text if lyrics_text else final_text
            alignment_result = self._perform_alignment(vocal_path, alignment_text, language)
            results["alignment"] = alignment_result.to_dict()
            
            # Step 6: Generate output files
            print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('Step 6: Generating Output Files')}")
            self._generate_output_files(results, output_dir)
            
            # Mark as successful
            results["success"] = True
            results["processing_time"] = time.time() - start_time
            
            # Update statistics
            self._update_pipeline_stats(results)
            
            print(f"\n{ULTRASINGER_HEAD} {green_highlighted('Pipeline completed successfully!')}")
            total_time_text = f"{results['processing_time']:.1f}s"
        print(f"{ULTRASINGER_HEAD} Total time: {blue_highlighted(total_time_text)}")
            
            return results
            
        except Exception as e:
            results["processing_time"] = time.time() - start_time
            results["error"] = str(e)
            print(f"\n{ULTRASINGER_HEAD} {red_highlighted('Pipeline failed:')} {str(e)}")
            raise e
    
    def _perform_separation(self, input_path: str, output_dir: str) -> Dict[str, Any]:
        """Perform audio separation"""
        try:
            # Determine best SepFormer model for the task
            model = SepFormerModel.get_recommended_model(self.config.processing_mode.value)
            
            # Perform separation
            separation_result = self.separator.separate_audio(
                input_path=input_path,
                output_dir=output_dir,
                model=model,
                use_cache=True
            )
            
            self.pipeline_stats["successful_separations"] += 1
            return separation_result.to_dict()
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Separation failed:')} {str(e)}")
            raise e
    
    def _perform_vad(self, audio_path: str) -> VADResult:
        """Perform voice activity detection"""
        try:
            # Determine best VAD model
            model = VADModel.get_recommended_model(self.config.vad.priority)
            
            # Perform VAD
            vad_result = self.vad.detect_voice_activity(
                input_path=audio_path,
                model=model,
                use_cache=True,
                min_speech_duration=self.config.vad.min_speech_duration,
                min_silence_duration=self.config.vad.min_silence_duration
            )
            
            self.pipeline_stats["successful_vad"] += 1
            return vad_result
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('VAD failed:')} {str(e)}")
            raise e
    
    def _perform_transcription(self, audio_path: str, language: str) -> TranscriptionResult:
        """Perform speech recognition"""
        try:
            # Determine best ASR model for language
            model = ASRModel.get_recommended_model(language, self.config.conformer.priority)
            
            # Perform transcription
            transcription_result = self.asr.transcribe_audio(
                input_path=audio_path,
                model=model,
                language=language,
                use_cache=True
            )
            
            self.pipeline_stats["successful_transcriptions"] += 1
            return transcription_result
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Transcription failed:')} {str(e)}")
            raise e
    
    def _perform_rescoring(self, text: str, language: str) -> RescoringResult:
        """Perform LLM rescoring"""
        try:
            # Determine best LLM model for language
            model = LLMModel.get_recommended_model(language, self.config.llm.priority)
            
            # Perform rescoring
            rescoring_result = self.rescorer.rescore_transcription(
                text=text,
                model=model,
                use_cache=True
            )
            
            self.pipeline_stats["successful_rescoring"] += 1
            return rescoring_result
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Rescoring failed:')} {str(e)}")
            raise e
    
    def _perform_alignment(self, audio_path: str, text: str, language: str) -> AlignmentResult:
        """Perform forced alignment"""
        try:
            # Determine best alignment model for language
            model = AlignmentModel.get_recommended_model(language)
            
            # Perform alignment
            alignment_result = self.aligner.align_text_to_audio(
                audio_path=audio_path,
                text=text,
                model=model,
                language=language,
                use_cache=True
            )
            
            self.pipeline_stats["successful_alignments"] += 1
            return alignment_result
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Alignment failed:')} {str(e)}")
            raise e
    
    def _generate_output_files(self, results: Dict[str, Any], output_dir: str):
        """Generate output files from processing results"""
        try:
            # Generate JSON report
            report_path = os.path.join(output_dir, "speechbrain_results.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"{ULTRASINGER_HEAD} Generated report: {blue_highlighted(os.path.basename(report_path))}")
            
            # Generate lyrics file if alignment successful
            if results.get("alignment") and results["alignment"].get("segments"):
                lyrics_path = os.path.join(output_dir, "aligned_lyrics.txt")
                self._generate_lyrics_file(results["alignment"], lyrics_path)
                print(f"{ULTRASINGER_HEAD} Generated lyrics: {blue_highlighted(os.path.basename(lyrics_path))}")
            
            # Generate timing file for karaoke
            if results.get("alignment") and results["alignment"].get("word_segments"):
                timing_path = os.path.join(output_dir, "karaoke_timing.json")
                self._generate_timing_file(results["alignment"], timing_path)
                print(f"{ULTRASINGER_HEAD} Generated timing: {blue_highlighted(os.path.basename(timing_path))}")
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to generate some output files: {str(e)}")
    
    def _generate_lyrics_file(self, alignment_data: Dict[str, Any], output_path: str):
        """Generate aligned lyrics file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Aligned Lyrics\n\n")
            
            for segment in alignment_data.get("segments", []):
                start_time = segment.get("start", 0.0)
                end_time = segment.get("end", 0.0)
                text = segment.get("text", "")
                
                f.write(f"[{start_time:.2f} - {end_time:.2f}] {text}\n")
    
    def _generate_timing_file(self, alignment_data: Dict[str, Any], output_path: str):
        """Generate karaoke timing file"""
        timing_data = {
            "format": "karaoke_timing_v1",
            "words": []
        }
        
        for word_segment in alignment_data.get("word_segments", []):
            timing_data["words"].append({
                "word": word_segment.get("word", ""),
                "start": word_segment.get("start", 0.0),
                "end": word_segment.get("end", 0.0),
                "confidence": word_segment.get("confidence", 1.0)
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(timing_data, f, indent=2, ensure_ascii=False)
    
    def _update_pipeline_stats(self, results: Dict[str, Any]):
        """Update pipeline statistics"""
        self.pipeline_stats["total_processed"] += 1
        self.pipeline_stats["total_time"] += results["processing_time"]
        self.pipeline_stats["average_time"] = (
            self.pipeline_stats["total_time"] / self.pipeline_stats["total_processed"]
        )
    
    def separate_audio_only(self,
                           input_path: str,
                           output_dir: str,
                           model: Optional[SepFormerModel] = None) -> Dict[str, Any]:
        """
        Perform only audio separation (for compatibility with existing UltraSinger)
        
        Args:
            input_path: Path to input audio file
            output_dir: Directory for output files
            model: Specific SepFormer model to use
            
        Returns:
            Separation results
        """
        print(f"{ULTRASINGER_HEAD} {blue_highlighted('SpeechBrain Audio Separation')}")
        
        try:
            model = model or SepFormerModel.get_recommended_model(self.config.processing_mode.value)
            
            separation_result = self.separator.separate_audio(
                input_path=input_path,
                output_dir=output_dir,
                model=model,
                use_cache=True
            )
            
            return separation_result.to_dict()
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Separation failed:')} {str(e)}")
            raise e
    
    def transcribe_audio_only(self,
                             input_path: str,
                             language: str = "en",
                             model: Optional[ASRModel] = None) -> TranscriptionResult:
        """
        Perform only speech recognition (for compatibility with existing UltraSinger)
        
        Args:
            input_path: Path to input audio file
            language: Language code for ASR
            model: Specific ASR model to use
            
        Returns:
            Transcription results
        """
        print(f"{ULTRASINGER_HEAD} {blue_highlighted('SpeechBrain Speech Recognition')}")
        
        try:
            model = model or ASRModel.get_recommended_model(language, self.config.conformer.priority)
            
            transcription_result = self.asr.transcribe_audio(
                input_path=input_path,
                model=model,
                language=language,
                use_cache=True
            )
            
            return transcription_result
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Transcription failed:')} {str(e)}")
            raise e
    
    def align_text_only(self,
                       audio_path: str,
                       text: str,
                       language: str = "en",
                       model: Optional[AlignmentModel] = None) -> AlignmentResult:
        """
        Perform only forced alignment (for compatibility with existing UltraSinger)
        
        Args:
            audio_path: Path to audio file
            text: Text to align
            language: Language code
            model: Specific alignment model to use
            
        Returns:
            Alignment results
        """
        print(f"{ULTRASINGER_HEAD} {blue_highlighted('SpeechBrain Forced Alignment')}")
        
        try:
            model = model or AlignmentModel.get_recommended_model(language)
            
            alignment_result = self.aligner.align_text_to_audio(
                audio_path=audio_path,
                text=text,
                model=model,
                language=language,
                use_cache=True
            )
            
            return alignment_result
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Alignment failed:')} {str(e)}")
            raise e
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        stats = {
            "pipeline": self.pipeline_stats.copy(),
            "separation": self.separator.get_performance_stats(),
            "asr": self.asr.get_performance_stats(),
            "alignment": self.aligner.get_performance_stats(),
            "vad": self.vad.get_performance_stats(),
            "rescoring": self.rescorer.get_performance_stats(),
            "model_manager": self.model_manager.get_cache_info()
        }
        return stats
    
    def print_performance_stats(self):
        """Print comprehensive performance statistics"""
        print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('SpeechBrain Pipeline Performance Stats:')}")
        
        stats = self.pipeline_stats
        print(f"  Total Processed: {blue_highlighted(str(stats['total_processed']))}")
        avg_time_text = f"{stats['average_time']:.1f}s"
        print(f"  Average Time: {blue_highlighted(avg_time_text)}")
        print(f"  Success Rates:")
        print(f"    Separations: {blue_highlighted(f'{stats['successful_separations']}/{stats['total_processed']}')}")
        print(f"    Transcriptions: {blue_highlighted(f'{stats['successful_transcriptions']}/{stats['total_processed']}')}")
        print(f"    Alignments: {blue_highlighted(f'{stats['successful_alignments']}/{stats['total_processed']}')}")
        
        # Print component stats
        self.separator.print_performance_stats()
        self.asr.print_performance_stats()
        self.aligner.print_performance_stats()
        self.vad.print_performance_stats()
        self.rescorer.print_performance_stats()
    
    def clear_all_caches(self):
        """Clear all component caches"""
        print(f"{ULTRASINGER_HEAD} Clearing all SpeechBrain caches...")
        
        self.separator.clear_cache()
        self.asr.clear_cache()
        self.aligner.clear_cache()
        self.vad.clear_cache()
        self.rescorer.clear_cache()
        self.model_manager.clear_memory()
        
        print(f"{ULTRASINGER_HEAD} {green_highlighted('All caches cleared')}")
    
    def save_config(self, config_path: str):
        """Save current configuration"""
        self.config.save_config(config_path)
        print(f"{ULTRASINGER_HEAD} Configuration saved to {blue_highlighted(config_path)}")
    
    def load_config(self, config_path: str):
        """Load configuration from file"""
        self.config.load_config(config_path)
        print(f"{ULTRASINGER_HEAD} Configuration loaded from {blue_highlighted(config_path)}")


# Convenience functions for easy integration with existing UltraSinger code

def create_speechbrain_pipeline(config_path: Optional[str] = None) -> SpeechBrainPipeline:
    """Create a SpeechBrain pipeline instance"""
    return SpeechBrainPipeline(config_path)


def separate_audio_with_speechbrain(input_path: str,
                                   output_dir: str,
                                   processing_mode: str = "balanced") -> Dict[str, Any]:
    """
    Convenience function for audio separation using SpeechBrain
    
    Args:
        input_path: Path to input audio file
        output_dir: Directory for output files
        processing_mode: Processing mode (fast, balanced, high_quality)
        
    Returns:
        Separation results
    """
    pipeline = SpeechBrainPipeline()
    pipeline.config.processing_mode = ProcessingMode(processing_mode)
    
    return pipeline.separate_audio_only(input_path, output_dir)


def transcribe_audio_with_speechbrain(input_path: str,
                                     language: str = "en") -> str:
    """
    Convenience function for speech recognition using SpeechBrain
    
    Args:
        input_path: Path to input audio file
        language: Language code for ASR
        
    Returns:
        Transcribed text
    """
    pipeline = SpeechBrainPipeline()
    result = pipeline.transcribe_audio_only(input_path, language)
    return result.text


def align_text_with_speechbrain(audio_path: str,
                               text: str,
                               language: str = "en") -> List[Dict[str, Any]]:
    """
    Convenience function for forced alignment using SpeechBrain
    
    Args:
        audio_path: Path to audio file
        text: Text to align
        language: Language code
        
    Returns:
        List of aligned segments
    """
    pipeline = SpeechBrainPipeline()
    result = pipeline.align_text_only(audio_path, text, language)
    return [seg.to_dict() for seg in result.segments]