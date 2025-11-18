"""
Uzbek Speech-to-Text Pipeline using OpenAI Whisper
==================================================

A high-accuracy STT system for Uzbek language using Whisper model.
"""

import torch
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor
import numpy as np
import wave
from typing import Optional, Dict, Any
import logging
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UzbekSTTConfig:
    """Configuration for Uzbek Whisper STT"""
    model_name: str = "openai/whisper-small"
    language: str = "uz"
    task: str = "transcribe"
    device: str = "auto"  # auto, cpu, cuda
    torch_dtype: torch.dtype = torch.float16
    chunk_length_s: int = 30
    batch_size: int = 16

class UzbekWhisperSTT:
    """
    Uzbek Speech-to-Text using OpenAI Whisper
    """

    def __init__(self, config: Optional[UzbekSTTConfig] = None):
        self.config = config or UzbekSTTConfig()

        # Set device with GPU optimization
        if self.config.device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
                torch.cuda.empty_cache()
                logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
            else:
                self.device = "cpu"
                logger.info("GPU not available, using CPU")
        else:
            self.device = self.config.device

        logger.info(f"Using device: {self.device}")

        # Load model and processor with GPU optimizations
        model_kwargs = {}
        if self.device == "cuda":
            model_kwargs = {
                "torch_dtype": torch.float16,
                "device_map": "auto",
                "low_cpu_mem_usage": True,
            }
            torch.cuda.set_per_process_memory_fraction(0.8)
        else:
            model_kwargs = {
                "torch_dtype": torch.float32,
            }

        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.config.model_name,
            **model_kwargs
        )
        
        self.processor = AutoProcessor.from_pretrained(self.config.model_name)
        
        # Create pipeline with optimized settings
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            chunk_length_s=self.config.chunk_length_s,
            batch_size=self.config.batch_size,
            generate_kwargs={"language": self.config.language, "task": self.config.task},
            low_cpu_mem_usage=True,
            use_safetensors=True
        )

        logger.info("✅ Uzbek Whisper STT initialized successfully")

    def transcribe_audio(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Transcribe audio data to Uzbek text

        Args:
            audio_data: Audio as numpy array
            sample_rate: Sample rate (should be 16000 for Whisper)

        Returns:
            Dict with transcription results
        """

        try:
            # Ensure audio is float32
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            # Normalize if needed
            if np.max(np.abs(audio_data)) > 1.0:
                audio_data = audio_data / np.max(np.abs(audio_data))

            # Transcribe
            result = self.pipe(
                {"array": audio_data, "sampling_rate": sample_rate},
                generate_kwargs={"language": self.config.language, "task": self.config.task}
            )

            return {
                "text": result["text"],
                "chunks": result.get("chunks", []),
                "language": self.config.language,
                "confidence": self._estimate_confidence(result),
                "timestamp": datetime.now().isoformat(),
                "model": self.config.model_name
            }

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                "text": "",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def transcribe_file(self, file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio from WAV file

        Args:
            file_path: Path to WAV audio file

        Returns:
            Dict with transcription results
        """
        try:
            # Load WAV file
            with wave.open(file_path, 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                audio_bytes = wav_file.readframes(n_frames)
                audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

                # Handle stereo to mono
                if wav_file.getnchannels() == 2:
                    audio_data = audio_data.reshape(-1, 2).mean(axis=1)

            return self.transcribe_audio(audio_data, sample_rate)

        except Exception as e:
            logger.error(f"File transcription failed: {e}")
            return {
                "text": "",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _estimate_confidence(self, result: Dict[str, Any]) -> float:
        """
        Estimate transcription confidence (simplified)

        Args:
            result: Whisper result dict

        Returns:
            Confidence score (0-1)
        """

        # Simple confidence estimation based on text length and chunks
        text = result.get("text", "").strip()
        chunks = result.get("chunks", [])

        if not text:
            return 0.0

        # Basic heuristics
        confidence = min(len(text) / 100, 1.0)  # Longer text = higher confidence
        confidence *= min(len(chunks) / 10, 1.0) if chunks else 0.5

        return round(confidence, 3)

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_name": self.config.model_name,
            "device": self.device,
            "language": self.config.language,
            "torch_dtype": str(self.config.torch_dtype),
            "chunk_length_s": self.config.chunk_length_s,
            "batch_size": self.config.batch_size
        }

def create_uzbek_whisper_stt(model_name: str = "openai/whisper-small") -> UzbekWhisperSTT:
    """
    Factory function to create Uzbek Whisper STT instance

    Args:
        model_name: Whisper model to use

    Returns:
        UzbekWhisperSTT instance
    """

    config = UzbekSTTConfig(model_name=model_name)
    return UzbekWhisperSTT(config)

# Example usage
if __name__ == "__main__":
    # Initialize STT
    stt = create_uzbek_whisper_stt()

    print("🎙️ Uzbek Whisper STT Pipeline")
    print("=" * 40)
    print(f"Model: {stt.get_model_info()['model_name']}")
    print(f"Device: {stt.get_model_info()['device']}")
    print("Ready for transcription!")
