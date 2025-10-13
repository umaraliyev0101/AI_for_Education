"""
Uzbek Speech-to-Text Pipeline using OpenAI Whisper
==================================================

A high-accuracy STT system for Uzbek language using Whisper model.
Supports real-time processing and batch transcription.
"""

import torch
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor
import numpy as np
import wave
import io
from typing import Optional, Dict, Any, List
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

        # Set device
        if self.config.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = self.config.device

        logger.info(f"Using device: {self.device}")

        # Load model and processor
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.config.model_name,
            torch_dtype=self.config.torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        )
        self.model.to(self.device)

        self.processor = AutoProcessor.from_pretrained(self.config.model_name)

        # Create pipeline
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=self.config.chunk_length_s,
            batch_size=self.config.batch_size,
            return_timestamps=True,
            torch_dtype=self.config.torch_dtype,
            device=self.device,
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
        Transcribe audio from file

        Args:
            file_path: Path to audio file (WAV, MP3, etc.)

        Returns:
            Dict with transcription results
        """

        try:
            # Load audio file
            audio_data, sample_rate = self._load_audio_file(file_path)

            # Transcribe
            return self.transcribe_audio(audio_data, sample_rate)

        except Exception as e:
            logger.error(f"File transcription failed: {e}")
            return {
                "text": "",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _load_audio_file(self, file_path: str) -> tuple[np.ndarray, int]:
        """
        Load audio file and return numpy array and sample rate

        Args:
            file_path: Path to audio file

        Returns:
            Tuple of (audio_array, sample_rate)
        """

        # For WAV files
        if file_path.endswith('.wav'):
            with wave.open(file_path, 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                audio_bytes = wav_file.readframes(n_frames)

                # Convert to numpy array
                audio_data = np.frombuffer(audio_bytes, dtype=np.int16)

                # Convert to float32 and normalize
                audio_data = audio_data.astype(np.float32) / 32768.0

                # Handle stereo to mono
                if wav_file.getnchannels() == 2:
                    audio_data = audio_data.reshape(-1, 2).mean(axis=1)

                return audio_data, sample_rate

        else:
            raise ValueError(f"Unsupported file format: {file_path}")

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
