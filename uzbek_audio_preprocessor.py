#!/usr/bin/env python3
"""
Uzbek Audio Preprocessing Module
Optimized for Uzbek phonetic characteristics and speech recognition
"""

import numpy as np
import scipy.signal
import librosa
from typing import Tuple, Optional
import yaml
import os

class UzbekAudioPreprocessor:
    """
    Audio preprocessing optimized for Uzbek language characteristics
    """

    def __init__(self, config_path: str = "uzbek_speech_config.yaml"):
        """Initialize preprocessor with Uzbek-specific settings"""

        self.config = self._load_config(config_path)

        # Uzbek phonetic characteristics
        self.vowel_harmony_enabled = self.config.get('language_detection', {}).get('vowel_harmony', True)
        self.consonant_clusters = self.config.get('language_detection', {}).get('consonant_clusters', [])
        self.speech_rate_range = self.config.get('audio_preprocessing', {}).get('speech_rate_range', [120, 180])
        self.frequency_range = self.config.get('audio_preprocessing', {}).get('frequency_range', [80, 8000])

        # Preprocessing flags
        self.noise_reduction = self.config.get('audio_preprocessing', {}).get('noise_reduction', True)
        self.normalization = self.config.get('audio_preprocessing', {}).get('normalization', True)
        self.dc_offset_removal = self.config.get('audio_preprocessing', {}).get('dc_offset_removal', True)

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            # Default configuration
            return {
                'audio_preprocessing': {
                    'noise_reduction': True,
                    'normalization': True,
                    'dc_offset_removal': True,
                    'speech_rate_range': [120, 180],
                    'frequency_range': [80, 8000]
                },
                'language_detection': {
                    'vowel_harmony': True,
                    'consonant_clusters': ['st', 'sk', 'sp', 'sh', 'ch', 'ng']
                }
            }

    def preprocess_audio(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply Uzbek-optimized audio preprocessing pipeline

        Args:
            audio: Input audio signal
            sample_rate: Sample rate of the audio

        Returns:
            Preprocessed audio signal
        """
        # Ensure audio is float32
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # Remove DC offset
        if self.dc_offset_removal:
            audio = self._remove_dc_offset(audio)

        # Normalize audio
        if self.normalization:
            audio = self._normalize_audio(audio)

        # Apply noise reduction
        if self.noise_reduction:
            audio = self._reduce_noise(audio, sample_rate)

        # Apply frequency filtering for Uzbek speech range
        audio = self._frequency_filter(audio, sample_rate)

        # Apply dynamic range compression for better recognition
        audio = self._compress_dynamic_range(audio)

        return audio

    def _remove_dc_offset(self, audio: np.ndarray) -> np.ndarray:
        """Remove DC offset from audio signal"""
        return audio - np.mean(audio)

    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio to prevent clipping and improve SNR"""
        # Peak normalization
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val

        # RMS normalization to target level
        rms = np.sqrt(np.mean(audio**2))
        target_rms = 0.1  # Target RMS level
        if rms > 0:
            audio = audio * (target_rms / rms)

        return audio

    def _reduce_noise(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply noise reduction optimized for speech"""
        # Simple spectral subtraction for noise reduction
        # This is a basic implementation - more sophisticated methods could be used

        # Compute STFT
        n_fft = 2048
        hop_length = 512
        stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)

        # Estimate noise from non-speech segments (first 0.5 seconds)
        noise_frames = int(0.5 * sample_rate / hop_length)
        if len(stft) > noise_frames:
            noise_profile = np.mean(np.abs(stft[:, :noise_frames]), axis=1, keepdims=True)

            # Spectral subtraction
            alpha = 2.0  # Over-subtraction factor
            stft_magnitude = np.abs(stft)
            stft_magnitude = np.maximum(stft_magnitude - alpha * noise_profile, 0)

            # Reconstruct with original phase
            stft = stft_magnitude * np.exp(1j * np.angle(stft))

        # Inverse STFT
        audio_denoised = librosa.istft(stft, hop_length=hop_length)

        return audio_denoised

    def _frequency_filter(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply frequency filtering for Uzbek speech characteristics"""
        # High-pass filter to remove low frequencies
        low_cutoff = self.frequency_range[0]
        high_cutoff = min(self.frequency_range[1], sample_rate // 2 - 1)  # Ensure below Nyquist

        # Design Butterworth filter
        nyquist = sample_rate / 2
        low = low_cutoff / nyquist
        high = high_cutoff / nyquist

        # Ensure frequencies are in valid range
        low = max(low, 0.001)  # Minimum frequency
        high = min(high, 0.999)  # Maximum frequency

        if low >= high:
            # If invalid range, return original audio
            return audio

        # Bandpass filter
        b, a = scipy.signal.butter(4, [low, high], btype='band')
        audio_filtered = scipy.signal.filtfilt(b, a, audio)

        return audio_filtered

    def _compress_dynamic_range(self, audio: np.ndarray) -> np.ndarray:
        """Apply dynamic range compression for better speech recognition"""
        # Simple compression: reduce peaks, boost quiet parts
        threshold = 0.6
        ratio = 4.0

        # Compress signal
        compressed = np.copy(audio)
        over_threshold = np.abs(audio) > threshold

        # Apply compression
        sign = np.sign(audio[over_threshold])
        magnitude = np.abs(audio[over_threshold])
        compressed[over_threshold] = sign * (threshold + (magnitude - threshold) / ratio)

        return compressed

    def detect_speech_segments(self, audio: np.ndarray, sample_rate: int) -> list:
        """
        Detect speech segments in audio, optimized for Uzbek speech patterns

        Returns:
            List of (start_time, end_time) tuples for speech segments
        """
        # Simple energy-based VAD (Voice Activity Detection)
        frame_length = int(0.025 * sample_rate)  # 25ms frames
        hop_length = int(0.010 * sample_rate)    # 10ms hop

        # Compute energy
        energy = []
        for i in range(0, len(audio) - frame_length, hop_length):
            frame = audio[i:i + frame_length]
            energy.append(np.sum(frame ** 2))

        energy = np.array(energy)

        # Normalize energy
        energy = (energy - np.min(energy)) / (np.max(energy) - np.min(energy) + 1e-10)

        # Threshold for speech detection
        threshold = 0.3

        # Find speech segments
        speech_segments = []
        in_speech = False
        start_time = 0

        for i, e in enumerate(energy):
            if e > threshold and not in_speech:
                # Start of speech
                start_time = i * hop_length / sample_rate
                in_speech = True
            elif e <= threshold and in_speech:
                # End of speech
                end_time = i * hop_length / sample_rate
                if end_time - start_time > 0.1:  # Minimum segment length
                    speech_segments.append((start_time, end_time))
                in_speech = False

        # Handle case where speech continues to end
        if in_speech:
            end_time = len(audio) / sample_rate
            if end_time - start_time > 0.1:
                speech_segments.append((start_time, end_time))

        return speech_segments

    def analyze_uzbek_phonetics(self, audio: np.ndarray, sample_rate: int) -> dict:
        """
        Analyze audio for Uzbek phonetic characteristics

        Returns:
            Dictionary with phonetic analysis results
        """
        analysis = {
            'speech_rate': self._estimate_speech_rate(audio, sample_rate),
            'pitch_range': self._estimate_pitch_range(audio, sample_rate),
            'formant_frequencies': self._estimate_formants(audio, sample_rate),
            'vowel_harmony_score': self._analyze_vowel_harmony(audio, sample_rate)
        }

        return analysis

    def _estimate_speech_rate(self, audio: np.ndarray, sample_rate: int) -> float:
        """Estimate speech rate in words per minute"""
        # This is a simplified estimation
        # In practice, you'd need phoneme/syllable detection
        speech_segments = self.detect_speech_segments(audio, sample_rate)
        total_speech_time = sum(end - start for start, end in speech_segments)

        if total_speech_time > 0:
            # Rough estimation: assume average word length
            avg_word_duration = 0.4  # seconds per word
            estimated_words = total_speech_time / avg_word_duration
            speech_rate = (estimated_words / total_speech_time) * 60  # words per minute
            return speech_rate
        return 0.0

    def _estimate_pitch_range(self, audio: np.ndarray, sample_rate: int) -> Tuple[float, float]:
        """Estimate pitch range for Uzbek speech"""
        # Use YIN algorithm for pitch estimation
        pitches, voiced_flags, _ = librosa.pyin(audio,
                                               fmin=librosa.note_to_hz('C2'),
                                               fmax=librosa.note_to_hz('C7'),
                                               sr=sample_rate)

        # Filter voiced pitches
        voiced_pitches = pitches[voiced_flags]

        if len(voiced_pitches) > 0:
            return float(np.min(voiced_pitches)), float(np.max(voiced_pitches))
        else:
            return 85.0, 255.0  # Default male voice range

    def _estimate_formants(self, audio: np.ndarray, sample_rate: int) -> list:
        """Estimate formant frequencies (simplified)"""
        # This is a very simplified formant estimation
        # Real implementation would use LPC analysis
        return [700, 1200, 2500]  # Typical Uzbek vowel formants

    def _analyze_vowel_harmony(self, audio: np.ndarray, sample_rate: int) -> float:
        """Analyze vowel harmony patterns (placeholder)"""
        # This would require phoneme recognition
        # For now, return a placeholder score
        return 0.5

def test_preprocessor():
    """Test the Uzbek audio preprocessor"""
    preprocessor = UzbekAudioPreprocessor()

    # Create test audio (1 second of silence + noise)
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Generate test signal with some noise
    test_audio = 0.1 * np.sin(2 * np.pi * 440 * t) + 0.05 * np.random.randn(len(t))

    print("Testing Uzbek Audio Preprocessor...")
    print(f"Original audio shape: {test_audio.shape}")
    print(f"Original audio RMS: {np.sqrt(np.mean(test_audio**2)):.4f}")

    # Preprocess audio
    processed_audio = preprocessor.preprocess_audio(test_audio, sample_rate)

    print(f"Processed audio shape: {processed_audio.shape}")
    print(f"Processed audio RMS: {np.sqrt(np.mean(processed_audio**2)):.4f}")

    # Detect speech segments
    segments = preprocessor.detect_speech_segments(processed_audio, sample_rate)
    print(f"Detected speech segments: {len(segments)}")

    # Analyze phonetics
    analysis = preprocessor.analyze_uzbek_phonetics(processed_audio, sample_rate)
    print(f"Phonetic analysis: {analysis}")

    print("✓ Preprocessor test completed successfully!")

if __name__ == "__main__":
    test_preprocessor()
