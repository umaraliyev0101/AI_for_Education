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

    def __init__(self, model_name: str = "sarahai/uzbek-stt-3", device: str = "cpu"):
        self.model_name = model_name
        self.device = device

        # Set device
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info(f"Using device: {self.device}")

        # Load model
        try:
            logger.info(f"Loading HF model: {self.model_name}")
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=self.model_name,
                device=self.device,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                chunk_length_s=30,
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

            return {
                'text': result['text'].strip() if isinstance(result, dict) and 'text' in result else str(result).strip(),
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
        try:
            result = self.pipe(file_path)
            return {
                'text': result['text'].strip() if isinstance(result, dict) and 'text' in result else str(result).strip(),
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
