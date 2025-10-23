#!/usr/bin/env python3
"""
Uzbek Speech-to-Text Pipeline using XLS-R
==========================================

High-accuracy STT for Uzbek using lucio/xls-r-uzbek-cv8
"""

import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import numpy as np
from typing import Optional, Dict, Any, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UzbekXLSRSTT:
    """Uzbek Speech-to-Text using XLS-R model"""

    def __init__(self, model_name: str = "lucio/xls-r-uzbek-cv8", device: str = "auto"):
        self.model_name = model_name
        self.device = "cuda" if device == "auto" and torch.cuda.is_available() else device

        logger.info(f"Loading {model_name} on {self.device}")

        self.processor = Wav2Vec2Processor.from_pretrained(model_name)
        self.model = Wav2Vec2ForCTC.from_pretrained(model_name)

        if self.device == "cuda":
            self.model = self.model.cuda()

        logger.info("✅ XLS-R STT ready")

    def transcribe_audio(self, audio_data: Union[np.ndarray, bytes], sample_rate: int = 16000) -> Dict[str, Any]:
        """Transcribe audio to Uzbek text"""
        try:
            # Convert bytes to numpy array if needed
            if isinstance(audio_data, bytes):
                audio_data = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Ensure audio is numpy array and 1D
            audio_data = np.asarray(audio_data)
            if audio_data.ndim > 1:
                audio_data = audio_data.flatten()

            # Resample to 16kHz if needed
            if sample_rate != 16000:
                import librosa
                audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)

            # Process audio
            inputs = self.processor(audio_data, sampling_rate=16000, return_tensors="pt", padding=True)

            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}

            # Transcribe
            with torch.no_grad():
                logits = self.model(**inputs).logits

            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = self.processor.batch_decode(predicted_ids)[0]

            # Calculate confidence
            probs = torch.softmax(logits, dim=-1)
            confidence = torch.max(probs, dim=-1)[0].mean().item()

            return {
                'text': transcription.strip(),
                'confidence': confidence,
                'model': self.model_name
            }

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {'text': '', 'confidence': 0.0, 'error': str(e)}

    def transcribe_file(self, file_path: str) -> Dict[str, Any]:
        """Transcribe audio file"""
        try:
            import soundfile as sf
            audio_data, sample_rate = sf.read(file_path)

            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            return self.transcribe_audio(audio_data, sample_rate)

        except Exception as e:
            logger.error(f"File transcription failed: {e}")
            return {'text': '', 'confidence': 0.0, 'error': str(e)}

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'model_name': self.model_name,
            'device': self.device,
            'architecture': 'wav2vec2_xlsr',
            'expected_wer': 0.1507  # 15.07%
        }

def create_uzbek_xlsr_stt(model_name: str = "lucio/xls-r-uzbek-cv8") -> UzbekXLSRSTT:
    """Create XLS-R STT instance"""
    return UzbekXLSRSTT(model_name)

if __name__ == "__main__":
    # Simple test
    stt = create_uzbek_xlsr_stt()
    print(f"Model: {stt.get_model_info()['model_name']}")
    print("Ready for transcription!")
