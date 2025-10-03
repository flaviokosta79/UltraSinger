"""
LLM Rescoring System

Advanced language model rescoring for improving ASR transcription accuracy,
specifically optimized for karaoke lyrics with context-aware corrections.
"""

import os
import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from pathlib import Path
import time
import json
import re
from dataclasses import dataclass

try:
    from transformers import (
        AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM,
        pipeline, GPT2LMHeadModel, T5ForConditionalGeneration
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from modules.console_colors import (
    ULTRASINGER_HEAD,
    blue_highlighted,
    green_highlighted,
    yellow_highlighted,
    red_highlighted
)
from .config_manager import SpeechBrainConfig


class LLMModel(Enum):
    """Available LLM models for rescoring"""
    
    # GPT-2 based models
    GPT2_SMALL = "gpt2"
    GPT2_MEDIUM = "gpt2-medium"
    GPT2_LARGE = "gpt2-large"
    
    # T5 based models
    T5_SMALL = "t5-small"
    T5_BASE = "t5-base"
    T5_LARGE = "t5-large"
    
    # Multilingual models
    MBART_LARGE = "facebook/mbart-large-50"
    MT5_SMALL = "google/mt5-small"
    MT5_BASE = "google/mt5-base"
    
    # Specialized models
    DISTILGPT2 = "distilgpt2"
    
    @classmethod
    def get_model_info(cls, model: 'LLMModel') -> Dict[str, Any]:
        """Get detailed information about a specific LLM model"""
        model_info = {
            cls.GPT2_SMALL: {
                "type": "causal",
                "parameters": "124M",
                "languages": ["en"],
                "speed": "Very Fast",
                "quality": "Good",
                "memory_gb": 0.5,
                "recommended_for": "Fast rescoring, English lyrics"
            },
            cls.GPT2_MEDIUM: {
                "type": "causal",
                "parameters": "355M",
                "languages": ["en"],
                "speed": "Fast",
                "quality": "Very Good",
                "memory_gb": 1.5,
                "recommended_for": "Balanced performance, English lyrics"
            },
            cls.GPT2_LARGE: {
                "type": "causal",
                "parameters": "774M",
                "languages": ["en"],
                "speed": "Medium",
                "quality": "Excellent",
                "memory_gb": 3.0,
                "recommended_for": "High quality, English lyrics"
            },
            cls.T5_SMALL: {
                "type": "seq2seq",
                "parameters": "60M",
                "languages": ["en"],
                "speed": "Very Fast",
                "quality": "Good",
                "memory_gb": 0.3,
                "recommended_for": "Fast correction, English lyrics"
            },
            cls.T5_BASE: {
                "type": "seq2seq",
                "parameters": "220M",
                "languages": ["en"],
                "speed": "Fast",
                "quality": "Very Good",
                "memory_gb": 1.0,
                "recommended_for": "Balanced correction, English lyrics"
            },
            cls.T5_LARGE: {
                "type": "seq2seq",
                "parameters": "770M",
                "languages": ["en"],
                "speed": "Medium",
                "quality": "Excellent",
                "memory_gb": 3.0,
                "recommended_for": "High quality correction, English lyrics"
            },
            cls.MBART_LARGE: {
                "type": "seq2seq",
                "parameters": "610M",
                "languages": ["multilingual"],
                "speed": "Medium",
                "quality": "Very Good",
                "memory_gb": 2.5,
                "recommended_for": "Multilingual lyrics"
            },
            cls.MT5_SMALL: {
                "type": "seq2seq",
                "parameters": "300M",
                "languages": ["multilingual"],
                "speed": "Fast",
                "quality": "Good",
                "memory_gb": 1.2,
                "recommended_for": "Fast multilingual correction"
            },
            cls.MT5_BASE: {
                "type": "seq2seq",
                "parameters": "580M",
                "languages": ["multilingual"],
                "speed": "Medium",
                "quality": "Very Good",
                "memory_gb": 2.3,
                "recommended_for": "Multilingual lyrics"
            },
            cls.DISTILGPT2: {
                "type": "causal",
                "parameters": "82M",
                "languages": ["en"],
                "speed": "Very Fast",
                "quality": "Good",
                "memory_gb": 0.3,
                "recommended_for": "Ultra-fast rescoring, English lyrics"
            }
        }
        return model_info.get(model, {})
    
    @classmethod
    def get_recommended_model(cls, language: str = "en", priority: str = "balanced") -> 'LLMModel':
        """Get recommended LLM model based on language and priority"""
        if language.lower() in ["en", "english"]:
            if priority == "speed":
                return cls.DISTILGPT2
            elif priority == "quality":
                return cls.GPT2_LARGE
            else:  # balanced
                return cls.GPT2_MEDIUM
        else:
            # Multilingual
            if priority == "speed":
                return cls.MT5_SMALL
            elif priority == "quality":
                return cls.MBART_LARGE
            else:  # balanced
                return cls.MT5_BASE
    
    @classmethod
    def filter_by_language(cls, language: str) -> List['LLMModel']:
        """Filter models by language support"""
        models = []
        for model in cls:
            info = cls.get_model_info(model)
            if language.lower() in ["en", "english"] and "en" in info["languages"]:
                models.append(model)
            elif "multilingual" in info["languages"]:
                models.append(model)
        return models


@dataclass
class RescoringCandidate:
    """Container for rescoring candidate"""
    text: str
    score: float
    confidence: float
    start_time: float = 0.0
    end_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "score": self.score,
            "confidence": self.confidence,
            "start_time": self.start_time,
            "end_time": self.end_time
        }


@dataclass
class RescoringResult:
    """Container for rescoring results"""
    original_text: str
    rescored_text: str
    improvement_score: float
    candidates: List[RescoringCandidate]
    processing_time: float = 0.0
    model_used: str = ""
    
    @property
    def has_improvement(self) -> bool:
        """Check if rescoring improved the text"""
        return self.improvement_score > 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_text": self.original_text,
            "rescored_text": self.rescored_text,
            "improvement_score": self.improvement_score,
            "has_improvement": self.has_improvement,
            "candidates": [c.to_dict() for c in self.candidates],
            "processing_time": self.processing_time,
            "model_used": self.model_used
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class LLMRescorer:
    """Advanced LLM-based rescoring system for ASR transcriptions"""
    
    def __init__(self, config: SpeechBrainConfig):
        self.config = config
        self.current_model = None
        self.current_tokenizer = None
        self.current_model_name = None
        self.pipeline = None
        
        # Check if transformers is available
        if not TRANSFORMERS_AVAILABLE:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Transformers library not available. LLM rescoring disabled.")
            return
        
        # Performance tracking
        self.rescoring_stats = {
            "total_rescorings": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "improvements": 0,
            "improvement_rate": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def rescore_transcription(self,
                            text: str,
                            model: Optional[LLMModel] = None,
                            context: Optional[str] = None,
                            num_candidates: int = 3,
                            use_cache: bool = True) -> RescoringResult:
        """
        Rescore ASR transcription using LLM
        
        Args:
            text: Original transcription text
            model: Specific LLM model to use
            context: Additional context for rescoring
            num_candidates: Number of candidate corrections to generate
            use_cache: Whether to use cached results
            
        Returns:
            RescoringResult with improved transcription
        """
        if not TRANSFORMERS_AVAILABLE:
            # Return original text if transformers not available
            return RescoringResult(
                original_text=text,
                rescored_text=text,
                improvement_score=0.0,
                candidates=[RescoringCandidate(text, 1.0, 1.0)]
            )
        
        start_time = time.time()
        
        # Determine model
        model = model or LLMModel.get_recommended_model(
            self.config.llm.language,
            self.config.llm.priority
        )
        model_info = LLMModel.get_model_info(model)
        
        print(f"{ULTRASINGER_HEAD} Starting LLM rescoring with {blue_highlighted(model.value)}")
        print(f"{ULTRASINGER_HEAD} Model type: {blue_highlighted(model_info['type'])} - Quality: {blue_highlighted(model_info['quality'])}")
        
        # Check cache
        cache_key = self._get_cache_key(text, model.value, context, num_candidates)
        if use_cache:
            cached_result = self._check_cache(cache_key)
            if cached_result:
                self.rescoring_stats["cache_hits"] += 1
                print(f"{ULTRASINGER_HEAD} {green_highlighted('Cache:')} Using cached rescoring results")
                return cached_result
        
        self.rescoring_stats["cache_misses"] += 1
        
        # Load model
        self._load_model(model)
        
        # Perform rescoring
        try:
            result = self._perform_rescoring(
                text,
                model,
                model_info,
                context,
                num_candidates
            )
            
            # Set metadata
            result.processing_time = time.time() - start_time
            result.model_used = model.value
            
            # Update statistics
            self._update_stats(result.processing_time, result.has_improvement)
            
            # Cache result
            if use_cache:
                self._save_cache(cache_key, result)
            
            print(f"{ULTRASINGER_HEAD} {green_highlighted('Success:')} Rescoring completed in {blue_highlighted(f'{result.processing_time:.1f}s')}")
            if result.has_improvement:
                print(f"{ULTRASINGER_HEAD} Improvement score: {blue_highlighted(f'{result.improvement_score:.2f}')}")
                print(f"{ULTRASINGER_HEAD} Original: {yellow_highlighted(result.original_text[:50])}...")
                print(f"{ULTRASINGER_HEAD} Rescored: {green_highlighted(result.rescored_text[:50])}...")
            else:
                print(f"{ULTRASINGER_HEAD} No significant improvement found")
            
            return result
            
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Rescoring failed: {str(e)}")
            # Return original text on error
            return RescoringResult(
                original_text=text,
                rescored_text=text,
                improvement_score=0.0,
                candidates=[RescoringCandidate(text, 1.0, 1.0)],
                processing_time=time.time() - start_time,
                model_used=model.value
            )
    
    def _load_model(self, model: LLMModel):
        """Load LLM model and tokenizer"""
        if self.current_model_name != model.value:
            print(f"{ULTRASINGER_HEAD} Loading LLM model: {blue_highlighted(model.value)}")
            
            try:
                model_info = LLMModel.get_model_info(model)
                device = "cuda" if self.config.llm.use_gpu and torch.cuda.is_available() else "cpu"
                
                # Load tokenizer
                self.current_tokenizer = AutoTokenizer.from_pretrained(model.value)
                
                # Add pad token if missing
                if self.current_tokenizer.pad_token is None:
                    self.current_tokenizer.pad_token = self.current_tokenizer.eos_token
                
                # Load model based on type
                if model_info["type"] == "causal":
                    self.current_model = AutoModelForCausalLM.from_pretrained(
                        model.value,
                        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                        device_map="auto" if device == "cuda" else None
                    )
                    
                    # Create text generation pipeline
                    self.pipeline = pipeline(
                        "text-generation",
                        model=self.current_model,
                        tokenizer=self.current_tokenizer,
                        device=0 if device == "cuda" else -1,
                        torch_dtype=torch.float16 if device == "cuda" else torch.float32
                    )
                    
                elif model_info["type"] == "seq2seq":
                    self.current_model = AutoModelForSeq2SeqLM.from_pretrained(
                        model.value,
                        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                        device_map="auto" if device == "cuda" else None
                    )
                    
                    # Create text2text generation pipeline
                    self.pipeline = pipeline(
                        "text2text-generation",
                        model=self.current_model,
                        tokenizer=self.current_tokenizer,
                        device=0 if device == "cuda" else -1,
                        torch_dtype=torch.float16 if device == "cuda" else torch.float32
                    )
                
                self.current_model_name = model.value
                print(f"{ULTRASINGER_HEAD} Model loaded on {blue_highlighted(device)}")
                
            except Exception as e:
                print(f"{ULTRASINGER_HEAD} {red_highlighted('Error:')} Failed to load model: {str(e)}")
                raise e
    
    def _perform_rescoring(self,
                          text: str,
                          model: LLMModel,
                          model_info: Dict[str, Any],
                          context: Optional[str],
                          num_candidates: int) -> RescoringResult:
        """Perform LLM rescoring"""
        
        # Preprocess text
        cleaned_text = self._preprocess_text(text)
        
        # Generate candidates
        candidates = []
        
        if model_info["type"] == "causal":
            candidates = self._generate_causal_candidates(
                cleaned_text, context, num_candidates
            )
        elif model_info["type"] == "seq2seq":
            candidates = self._generate_seq2seq_candidates(
                cleaned_text, context, num_candidates
            )
        
        # Select best candidate
        best_candidate = self._select_best_candidate(candidates, cleaned_text)
        
        # Calculate improvement score
        improvement_score = self._calculate_improvement_score(
            cleaned_text, best_candidate.text
        )
        
        return RescoringResult(
            original_text=text,
            rescored_text=best_candidate.text,
            improvement_score=improvement_score,
            candidates=candidates
        )
    
    def _generate_causal_candidates(self,
                                   text: str,
                                   context: Optional[str],
                                   num_candidates: int) -> List[RescoringCandidate]:
        """Generate candidates using causal language model"""
        candidates = []
        
        # Create prompt for correction
        if context:
            prompt = f"Context: {context}\nCorrect this text: {text}\nCorrected text:"
        else:
            prompt = f"Correct this text for lyrics: {text}\nCorrected text:"
        
        try:
            # Generate multiple candidates
            outputs = self.pipeline(
                prompt,
                max_new_tokens=len(text.split()) + 20,
                num_return_sequences=num_candidates,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.current_tokenizer.eos_token_id
            )
            
            for i, output in enumerate(outputs):
                generated_text = output["generated_text"]
                
                # Extract corrected text
                corrected = self._extract_corrected_text(generated_text, prompt)
                
                # Calculate score (simplified)
                score = 1.0 - (i * 0.1)  # Decrease score for later candidates
                confidence = min(1.0, score + 0.1)
                
                candidates.append(RescoringCandidate(
                    text=corrected,
                    score=score,
                    confidence=confidence
                ))
                
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Causal generation failed: {str(e)}")
            # Fallback to original text
            candidates.append(RescoringCandidate(
                text=text,
                score=1.0,
                confidence=1.0
            ))
        
        return candidates
    
    def _generate_seq2seq_candidates(self,
                                    text: str,
                                    context: Optional[str],
                                    num_candidates: int) -> List[RescoringCandidate]:
        """Generate candidates using sequence-to-sequence model"""
        candidates = []
        
        # Create input for correction
        if context:
            input_text = f"correct lyrics: {text} context: {context}"
        else:
            input_text = f"correct lyrics: {text}"
        
        try:
            # Generate multiple candidates
            outputs = self.pipeline(
                input_text,
                max_length=len(text.split()) + 20,
                num_return_sequences=num_candidates,
                temperature=0.7,
                do_sample=True
            )
            
            for i, output in enumerate(outputs):
                corrected_text = output["generated_text"].strip()
                
                # Calculate score (simplified)
                score = 1.0 - (i * 0.1)
                confidence = min(1.0, score + 0.1)
                
                candidates.append(RescoringCandidate(
                    text=corrected_text,
                    score=score,
                    confidence=confidence
                ))
                
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Seq2seq generation failed: {str(e)}")
            # Fallback to original text
            candidates.append(RescoringCandidate(
                text=text,
                score=1.0,
                confidence=1.0
            ))
        
        return candidates
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for rescoring"""
        # Basic cleaning
        text = text.strip()
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common ASR errors
        text = self._fix_common_asr_errors(text)
        
        return text
    
    def _fix_common_asr_errors(self, text: str) -> str:
        """Fix common ASR errors"""
        # Common replacements for lyrics
        replacements = {
            r'\bi\b': 'I',  # Capitalize 'i'
            r'\byou\s+are\b': "you're",  # Contractions
            r'\bdo\s+not\b': "don't",
            r'\bcan\s+not\b': "can't",
            r'\bwill\s+not\b': "won't",
            r'\bis\s+not\b': "isn't",
            r'\bare\s+not\b': "aren't",
            r'\bwas\s+not\b': "wasn't",
            r'\bwere\s+not\b': "weren't",
            r'\bhave\s+not\b': "haven't",
            r'\bhas\s+not\b': "hasn't",
            r'\bhad\s+not\b': "hadn't",
            r'\bwould\s+not\b': "wouldn't",
            r'\bshould\s+not\b': "shouldn't",
            r'\bcould\s+not\b': "couldn't",
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _extract_corrected_text(self, generated_text: str, prompt: str) -> str:
        """Extract corrected text from generated output"""
        # Remove the prompt from the generated text
        if prompt in generated_text:
            corrected = generated_text.replace(prompt, "").strip()
        else:
            corrected = generated_text.strip()
        
        # Clean up the result
        corrected = re.sub(r'^[:\-\s]*', '', corrected)  # Remove leading punctuation
        corrected = corrected.split('\n')[0]  # Take only first line
        
        return corrected.strip()
    
    def _select_best_candidate(self,
                              candidates: List[RescoringCandidate],
                              original_text: str) -> RescoringCandidate:
        """Select the best candidate from the list"""
        if not candidates:
            return RescoringCandidate(original_text, 1.0, 1.0)
        
        # For now, select the first candidate (highest score)
        # In a more sophisticated implementation, we could use additional metrics
        best_candidate = max(candidates, key=lambda c: c.score)
        
        # Ensure the candidate is different enough from original
        if self._text_similarity(original_text, best_candidate.text) > 0.95:
            # Too similar, return original
            return RescoringCandidate(original_text, 1.0, 1.0)
        
        return best_candidate
    
    def _calculate_improvement_score(self, original: str, corrected: str) -> float:
        """Calculate improvement score between original and corrected text"""
        # Simple improvement score based on:
        # 1. Length difference (penalize too much change)
        # 2. Character-level similarity
        # 3. Word-level similarity
        
        if original == corrected:
            return 0.0
        
        # Length penalty
        len_ratio = len(corrected) / len(original) if len(original) > 0 else 1.0
        len_penalty = abs(1.0 - len_ratio)
        
        # Character similarity
        char_sim = self._text_similarity(original, corrected)
        
        # Word similarity
        word_sim = self._word_similarity(original, corrected)
        
        # Calculate improvement (higher is better)
        # We want some change but not too much
        improvement = (1.0 - char_sim) * 0.3 + (1.0 - word_sim) * 0.4 - len_penalty * 0.3
        
        return max(0.0, min(1.0, improvement))
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate character-level similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        # Simple character-based similarity
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _word_similarity(self, text1: str, text2: str) -> float:
        """Calculate word-level similarity between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _get_cache_key(self, text: str, model_name: str, context: Optional[str], num_candidates: int) -> str:
        """Generate cache key for rescoring"""
        import hashlib
        
        cache_string = f"{text}_{model_name}_{context or ''}_{num_candidates}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[RescoringResult]:
        """Check for cached rescoring result"""
        cache_dir = os.path.join(os.path.dirname(__file__), ".cache", "rescoring")
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct candidates
            candidates = []
            for cand_data in data["candidates"]:
                candidate = RescoringCandidate(
                    text=cand_data["text"],
                    score=cand_data["score"],
                    confidence=cand_data["confidence"],
                    start_time=cand_data.get("start_time", 0.0),
                    end_time=cand_data.get("end_time", 0.0)
                )
                candidates.append(candidate)
            
            result = RescoringResult(
                original_text=data["original_text"],
                rescored_text=data["rescored_text"],
                improvement_score=data["improvement_score"],
                candidates=candidates,
                processing_time=data.get("processing_time", 0.0),
                model_used=data.get("model_used", "")
            )
            
            return result
            
        except Exception:
            return None
    
    def _save_cache(self, cache_key: str, result: RescoringResult):
        """Save rescoring result to cache"""
        cache_dir = os.path.join(os.path.dirname(__file__), ".cache", "rescoring")
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to save rescoring cache: {str(e)}")
    
    def _update_stats(self, processing_time: float, has_improvement: bool):
        """Update performance statistics"""
        self.rescoring_stats["total_rescorings"] += 1
        self.rescoring_stats["total_time"] += processing_time
        
        if has_improvement:
            self.rescoring_stats["improvements"] += 1
        
        # Calculate averages
        total_rescorings = self.rescoring_stats["total_rescorings"]
        self.rescoring_stats["average_time"] = self.rescoring_stats["total_time"] / total_rescorings
        self.rescoring_stats["improvement_rate"] = self.rescoring_stats["improvements"] / total_rescorings
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.rescoring_stats.copy()
    
    def print_performance_stats(self):
        """Print performance statistics"""
        stats = self.rescoring_stats
        
        print(f"\n{ULTRASINGER_HEAD} {blue_highlighted('LLM Rescoring Performance Stats:')}")
        print(f"  Total Rescorings: {blue_highlighted(str(stats['total_rescorings']))}")
        avg_time_text = f"{stats['average_time']:.1f}s"
        print(f"  Average Time: {blue_highlighted(avg_time_text)}")
        improvement_text = f"{stats['improvement_rate']:.1%}"
        print(f"  Improvement Rate: {blue_highlighted(improvement_text)}")
        cache_rate = f"{stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%" if stats['cache_hits']+stats['cache_misses'] > 0 else '0%'
        print(f"  Cache Hit Rate: {blue_highlighted(cache_rate)}")
    
    def clear_cache(self):
        """Clear rescoring cache"""
        cache_dir = os.path.join(os.path.dirname(__file__), ".cache", "rescoring")
        try:
            if os.path.exists(cache_dir):
                import shutil
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
                print(f"{ULTRASINGER_HEAD} Cleared rescoring cache")
        except Exception as e:
            print(f"{ULTRASINGER_HEAD} {yellow_highlighted('Warning:')} Failed to clear cache: {str(e)}")


def get_available_models() -> List[LLMModel]:
    """Get list of available LLM models"""
    return list(LLMModel)


def get_recommended_model(language: str = "en", priority: str = "balanced") -> LLMModel:
    """Get recommended LLM model based on language and priority"""
    return LLMModel.get_recommended_model(language, priority)