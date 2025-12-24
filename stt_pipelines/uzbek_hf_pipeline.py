#!/usr/bin/env python3
"""
Uzbek Speech-to-Text Pipeline using Hugging Face Transformers
=============================================================

High-accuracy STT system for Uzbek language using fine-tuned transformer models.
"""

import torch
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor
import numpy as np
from typing import Optional, Dict, Any, Union
import logging
from dataclasses import dataclass
import io
import tempfile
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UzbekHFSTTConfig:
    """Configuration for Uzbek HF STT"""
    model_name: str = "sarahai/uzbek-stt-3"
    device: str = "auto"  # auto, cpu, cuda
    torch_dtype: torch.dtype = torch.float16
    chunk_length_s: int = 30

class UzbekHFSTTPipeline:
    """
    Uzbek Speech-to-Text using Hugging Face transformer models
    """

    def __init__(self, model_name: str = "sarahai/uzbek-stt-3", device: str = "auto"):
        self.model_name = model_name
        self.device = device

        # Set device with GPU optimization
        if self.device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
                # Set GPU memory optimization
                torch.cuda.empty_cache()
                logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
            else:
                self.device = "cpu"
                logger.info("GPU not available, using CPU")

        logger.info(f"Using device: {self.device}")

        # Load model with GPU optimizations
        try:
            logger.info(f"Loading HF model: {self.model_name}")
            
            # GPU-specific configurations
            if self.device == "cuda":
                model_kwargs = {
                    "torch_dtype": torch.float16,  # Use FP16 for memory efficiency
                    "device_map": "auto",  # Automatic device placement
                    "low_cpu_mem_usage": True,  # Reduce CPU memory usage during loading
                }
                # Set CUDA memory fraction if needed
                torch.cuda.set_per_process_memory_fraction(0.8)  # Use 80% of GPU memory
                # When using device_map, don't specify device in pipeline
                self.pipe = pipeline(
                    "automatic-speech-recognition",
                    model=self.model_name,
                    chunk_length_s=30,
                    model_kwargs=model_kwargs
                )
            else:
                model_kwargs = {
                    "torch_dtype": torch.float32,
                }
                self.pipe = pipeline(
                    "automatic-speech-recognition",
                    model=self.model_name,
                    device=self.device,
                    chunk_length_s=30,
                    model_kwargs=model_kwargs
                )
            
            logger.info("✅ Uzbek HF STT initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to load HF model: {e}")
            raise

    def transcribe_audio(self, audio_data: Union[np.ndarray, bytes], sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Transcribe audio data to text.

        Args:
            audio_data: Audio data as numpy array or bytes
            sample_rate: Sample rate of the audio

        Returns:
            Dict with 'text' and 'confidence' keys
        """
        # Import text normalizer for Uzbek characters (oʻ, gʻ variants)
        try:
            from utils.uzbek_text_postprocessor import normalize_uzbek_text
        except ImportError:
            normalize_uzbek_text = lambda x: x  # Fallback to no normalization

        try:
            import time
            start_time = time.time()

            # Convert bytes to numpy array if needed
            if isinstance(audio_data, bytes):
                audio_data = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Ensure audio is 1D
            if isinstance(audio_data, np.ndarray) and audio_data.ndim > 1:
                audio_data = audio_data.flatten()

            # Transcribe using pipeline
            result = self.pipe({"array": audio_data, "sampling_rate": sample_rate})

            processing_time = time.time() - start_time

            # Get raw text and normalize for LLM compatibility
            # Use ASCII apostrophe for better tokenization with Llama Uzbek model
            raw_text = result['text'].strip() if isinstance(result, dict) and 'text' in result else str(result).strip()
            normalized_text = normalize_uzbek_text(raw_text, use_ascii_apostrophe=True)

            return {
                'text': normalized_text,
                'confidence': 0.8,  # Placeholder confidence
                'processing_time': processing_time,
                'model': self.model_name
            }

        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'error': str(e),
                'model': self.model_name
            }

    def transcribe_file(self, file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio from file.

        Args:
            file_path: Path to audio file

        Returns:
            Dict with transcription results
        """
        # Import text normalizer for Uzbek characters (oʻ, gʻ variants)
        try:
            from utils.uzbek_text_postprocessor import normalize_uzbek_text
        except ImportError:
            normalize_uzbek_text = lambda x: x  # Fallback to no normalization

        try:
            result = self.pipe(file_path)
            raw_text = result['text'].strip() if isinstance(result, dict) and 'text' in result else str(result).strip()
            # Use ASCII apostrophe for better tokenization with Llama Uzbek model
            normalized_text = normalize_uzbek_text(raw_text, use_ascii_apostrophe=True)
            
            return {
                'text': normalized_text,
                'confidence': 0.8,  # Placeholder
                'file': file_path,
                'model': self.model_name
            }

        except Exception as e:
            logger.error(f"❌ File transcription failed: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'error': str(e),
                'file': file_path,
                'model': self.model_name
            }

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            'model_name': self.model_name,
            'device': self.device,
            'framework': 'huggingface_transformers',
            'language': 'uzbek',
            'architecture': 'transformer'
        }
