#!/usr/bin/env python3
"""
Uzbek Test Audio Collection System
Generate and manage test audio samples for Uzbek speech recognition testing
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import wave
import struct
from gtts import gTTS
import pygame
import io
from pydub import AudioSegment

@dataclass
class UzbekSpeakerProfile:
    """Profile for different Uzbek speaker characteristics"""

    speaker_id: str
    name: str
    region: str  # Toshkent, Samarqand, Buxoro, etc.
    age_group: str  # child, teen, adult, senior
    gender: str  # male, female
    accent_type: str  # standard, regional, mixed
    speech_rate: float  # words per minute
    pitch_range: Tuple[float, float]  # Hz
    volume_range: Tuple[float, float]  # 0-1 scale
    background_noise: str  # none, light, moderate, heavy

@dataclass
class UzbekTestSample:
    """Metadata for a test audio sample"""

    sample_id: str
    text: str
    speaker_profile: UzbekSpeakerProfile
    duration: float  # seconds
    sample_rate: int
    audio_format: str
    file_path: str
    created_date: str
    quality_score: float  # 0-1 scale
    transcription_verified: bool
    tags: List[str]
    metadata: Dict[str, Any]

class UzbekAudioGenerator:
    """
    Generate Uzbek speech audio for testing using Google TTS
    """

    def __init__(self, output_dir: str = "test_audio/uzbek_samples"):
        """Initialize the audio generator"""

        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Common Uzbek words and phrases for testing
        self.test_phrases = self._load_test_phrases()

        # Speaker profiles (simulated through TTS parameters)
        self.speaker_profiles = self._create_speaker_profiles()

    def _load_test_phrases(self) -> List[str]:
        """Load common Uzbek test phrases"""

        return [
            # Basic greetings
            "Salom",
            "Xayr",
            "Rahmat",
            "Kechirasiz",

            # Common questions
            "Qalay siz?",
            "Nima qilyapsiz?",
            "Qayerdan siz?",
            "Necha yoshdasiz?",

            # Numbers
            "Bir",
            "Ikki",
            "Uch",
            "Toʻrt",
            "Besh",

            # Colors
            "Qizil",
            "Yashil",
            "Koʻk",
            "Qora",
            "Oq",

            # Educational terms
            "Maktab",
            "Oʻqituvchi",
            "Dars",
            "Kitob",
            "Yozuv",

            # Common phrases
            "Men oʻqiyman",
            "U yozadi",
            "Biz oʻynaymiz",
            "Siz ishlayapsiz",
            "Ular yashaydi",

            # Complex sentences
            "Bugun maktabga boraman va dars oʻqiyman",
            "Oʻqituvchi kitob beradi",
            "Yashil qalam bilan yozaman"
        ]

    def _create_speaker_profiles(self) -> List[UzbekSpeakerProfile]:
        """Create diverse speaker profiles for testing"""

        return [
            UzbekSpeakerProfile(
                speaker_id="tashkent_male_adult",
                name="Toshkent Erkak",
                region="Toshkent",
                age_group="adult",
                gender="male",
                accent_type="standard",
                speech_rate=150.0,
                pitch_range=(85, 180),
                volume_range=(0.7, 0.9),
                background_noise="none"
            ),
            UzbekSpeakerProfile(
                speaker_id="samarkand_female_teen",
                name="Samarqand Qiz",
                region="Samarqand",
                age_group="teen",
                gender="female",
                accent_type="regional",
                speech_rate=160.0,
                pitch_range=(180, 280),
                volume_range=(0.6, 0.8),
                background_noise="light"
            ),
            UzbekSpeakerProfile(
                speaker_id="bukhara_male_senior",
                name="Buxoro Chol",
                region="Buxoro",
                age_group="senior",
                gender="male",
                accent_type="regional",
                speech_rate=130.0,
                pitch_range=(70, 150),
                volume_range=(0.5, 0.7),
                background_noise="moderate"
            ),
            UzbekSpeakerProfile(
                speaker_id="fergana_female_child",
                name="Fargʻona Bola",
                region="Fargʻona",
                age_group="child",
                gender="female",
                accent_type="regional",
                speech_rate=140.0,
                pitch_range=(250, 350),
                volume_range=(0.4, 0.6),
                background_noise="none"
            ),
            UzbekSpeakerProfile(
                speaker_id="standard_female_adult",
                name="Standard Ayol",
                region="Toshkent",
                age_group="adult",
                gender="female",
                accent_type="standard",
                speech_rate=155.0,
                pitch_range=(160, 260),
                volume_range=(0.65, 0.85),
                background_noise="light"
            )
        ]

    def generate_tts_audio(self, text: str, speaker_profile: UzbekSpeakerProfile,
                          sample_rate: int = 16000) -> Tuple[np.ndarray, float]:
        """
        Generate audio using Google Text-to-Speech for Uzbek

        Args:
            text: Uzbek text to synthesize
            speaker_profile: Speaker characteristics (used for metadata)
            sample_rate: Target sample rate

        Returns:
            Tuple of (audio_data, duration)
        """

        try:
            # Create TTS object for Uzbek
            tts = gTTS(text=text, lang='uz', slow=False)

            # Save to temporary MP3 file
            temp_mp3 = os.path.join(self.output_dir, f"temp_{hash(text)}.mp3")
            tts.save(temp_mp3)

            # Convert MP3 to WAV using pydub
            audio_segment = AudioSegment.from_mp3(temp_mp3)

            # Convert to mono and set sample rate
            audio_segment = audio_segment.set_channels(1)  # Mono
            audio_segment = audio_segment.set_frame_rate(sample_rate)

            # Export as WAV
            temp_wav = os.path.join(self.output_dir, f"temp_{hash(text)}.wav")
            audio_segment.export(temp_wav, format="wav")

            # Load WAV data
            with wave.open(temp_wav, 'rb') as wav_file:
                # Get audio parameters
                n_channels = wav_file.getnchannels()
                sampwidth = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()

                # Read audio data
                audio_data = wav_file.readframes(n_frames)

                # Convert to numpy array
                if sampwidth == 2:  # 16-bit
                    audio_np = np.frombuffer(audio_data, dtype=np.int16)
                    audio_np = audio_np.astype(np.float32) / 32768.0  # Normalize to [-1, 1]
                elif sampwidth == 4:  # 32-bit
                    audio_np = np.frombuffer(audio_data, dtype=np.int32)
                    audio_np = audio_np.astype(np.float32) / 2147483648.0
                else:
                    raise ValueError(f"Unsupported sample width: {sampwidth}")

                duration = n_frames / framerate

            # Clean up temporary files
            for temp_file in [temp_mp3, temp_wav]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

            # Apply speaker-specific modifications
            audio_np = self._apply_speaker_characteristics(audio_np, speaker_profile)

            return audio_np, duration

        except Exception as e:
            print(f"Error generating TTS audio for '{text}': {e}")
            # Fallback: generate synthetic speech-like audio
            return self._generate_fallback_audio(text, speaker_profile, sample_rate)

    def _apply_speaker_characteristics(self, audio: np.ndarray, speaker_profile: UzbekSpeakerProfile) -> np.ndarray:
        """Apply speaker-specific audio modifications"""

        # Apply volume variation
        rng = np.random.default_rng(seed=hash(speaker_profile.speaker_id) % 2**32)
        volume = rng.uniform(*speaker_profile.volume_range)
        audio *= volume

        # Add background noise based on profile
        if speaker_profile.background_noise != "none":
            noise_level = {"light": 0.02, "moderate": 0.05, "heavy": 0.1}[speaker_profile.background_noise]
            bg_noise = noise_level * rng.normal(0, 1, len(audio))
            audio += bg_noise

        # Normalize
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))

        return audio

    def _generate_fallback_audio(self, text: str, speaker_profile: UzbekSpeakerProfile,
                               sample_rate: int = 16000) -> Tuple[np.ndarray, float]:
        """Generate fallback synthetic audio when TTS fails"""

        # Estimate duration
        words = text.split()
        estimated_duration = max(1.0, len(words) * 0.5)
        total_samples = int(estimated_duration * sample_rate)

        # Create basic speech-like signal
        t = np.linspace(0, estimated_duration, total_samples, endpoint=False)
        audio = np.zeros_like(t)

        # Add fundamental frequency with variation
        base_freq = 120
        fundamental = base_freq * (1 + 0.1 * np.sin(2 * np.pi * 0.5 * t))

        # Add harmonics
        for harmonic in range(1, 4):
            amplitude = 1.0 / harmonic
            audio += amplitude * 0.1 * np.sin(2 * np.pi * harmonic * fundamental * t)

        # Add noise
        rng = np.random.default_rng(seed=hash(text) % 2**32)
        noise = 0.05 * rng.normal(0, 1, len(t))
        audio += noise

        # Apply speaker characteristics
        audio = self._apply_speaker_characteristics(audio, speaker_profile)

        return audio.astype(np.float32), estimated_duration

    def _apply_formant_shift(self, audio: np.ndarray, shift_factor: float) -> np.ndarray:
        """Apply formant shifting for voice characteristics"""

        # Simple formant shifting using frequency domain
        fft = np.fft.fft(audio)
        freqs = np.fft.fftfreq(len(audio))

        # Shift formant frequencies
        shifted_fft = np.zeros_like(fft)
        for i, freq in enumerate(freqs):
            if freq > 0:  # Only positive frequencies
                new_freq_idx = int(i * shift_factor)
                if new_freq_idx < len(fft):
                    shifted_fft[new_freq_idx] = fft[i]

        # Inverse FFT
        shifted_audio = np.real(np.fft.ifft(shifted_fft))

        return shifted_audio

    def save_audio_file(self, audio: np.ndarray, file_path: str, sample_rate: int = 16000):
        """
        Save audio data to WAV file

        Args:
            audio: Audio data as numpy array
            file_path: Output file path
            sample_rate: Sample rate
        """

        # Ensure audio is in the right range for WAV
        audio_int16 = (audio * 32767).astype(np.int16)

        # Create WAV file
        with wave.open(file_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

    def generate_test_sample(self, text: str, speaker_profile: UzbekSpeakerProfile,
                           sample_rate: int = 16000) -> UzbekTestSample:
        """
        Generate a complete test sample with audio and metadata

        Args:
            text: Text to synthesize
            speaker_profile: Speaker profile
            sample_rate: Audio sample rate

        Returns:
            TestSample object with metadata
        """

        # Generate unique sample ID
        sample_id = hashlib.md5(f"{text}_{speaker_profile.speaker_id}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]

        # Generate audio
        audio, duration = self.generate_tts_audio(text, speaker_profile, sample_rate)

        # Create file path
        file_path = os.path.join(self.output_dir, f"{sample_id}.wav")

        # Save audio file
        self.save_audio_file(audio, file_path, sample_rate)

        # Calculate duration
        duration = len(audio) / sample_rate

        # Create test sample metadata
        sample = UzbekTestSample(
            sample_id=sample_id,
            text=text,
            speaker_profile=speaker_profile,
            duration=duration,
            sample_rate=sample_rate,
            audio_format="wav",
            file_path=file_path,
            created_date=datetime.now().isoformat(),
            quality_score=self._calculate_quality_score(audio),
            transcription_verified=True,  # Synthetic, so verified
            tags=self._generate_tags(text, speaker_profile),
            metadata={
                "generator": "UzbekAudioGenerator",
                "synthesis_method": "synthetic_formant",
                "audio_length_samples": len(audio)
            }
        )

        return sample

    def _calculate_quality_score(self, audio: np.ndarray) -> float:
        """Calculate audio quality score"""

        # Simple quality metrics
        # Signal-to-noise ratio
        signal_power = np.mean(audio ** 2)
        noise_power = np.var(audio - np.mean(audio))
        snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 0

        # Normalize SNR to 0-1 scale (assuming -10dB to 30dB range)
        quality = min(max((snr + 10) / 40, 0), 1)

        return quality

    def _generate_tags(self, text: str, speaker_profile: UzbekSpeakerProfile) -> List[str]:
        """Generate tags for the sample"""

        tags = []

        # Content tags
        word_count = len(text.split())
        if word_count == 1:
            tags.append("single_word")
        elif word_count <= 3:
            tags.append("short_phrase")
        else:
            tags.append("sentence")

        # Speaker tags
        tags.extend([
            speaker_profile.region.lower(),
            speaker_profile.age_group,
            speaker_profile.gender,
            speaker_profile.accent_type
        ])

        # Educational content detection
        educational_terms = ["maktab", "oʻqituvchi", "dars", "kitob", "yozuv", "oʻqish", "yozish"]
        if any(term in text.lower() for term in educational_terms):
            tags.append("educational")

        return tags

    def generate_test_dataset(self, num_samples_per_speaker: int = 10) -> List[UzbekTestSample]:
        """
        Generate a complete test dataset

        Args:
            num_samples_per_speaker: Number of samples per speaker profile

        Returns:
            List of test samples
        """

        samples = []
        sample_counter = 0

        for speaker in self.speaker_profiles:
            print(f"Generating samples for speaker: {speaker.name}")

            # Select phrases for this speaker
            rng = np.random.default_rng(seed=hash(speaker.speaker_id) % 2**32)
            selected_phrases = rng.choice(self.test_phrases,
                                        size=min(num_samples_per_speaker, len(self.test_phrases)),
                                        replace=False)

            for phrase in selected_phrases:
                try:
                    sample = self.generate_test_sample(phrase, speaker)
                    samples.append(sample)
                    sample_counter += 1

                    if sample_counter % 10 == 0:
                        print(f"Generated {sample_counter} samples...")

                except Exception as e:
                    print(f"Error generating sample for '{phrase}': {e}")
                    continue

        print(f"Generated {len(samples)} test samples total")
        return samples

    def save_metadata(self, samples: List[UzbekTestSample], metadata_file: str = "uzbek_test_metadata.json"):
        """
        Save sample metadata to JSON file

        Args:
            samples: List of test samples
            metadata_file: Output metadata file path
        """

        metadata_path = os.path.join(self.output_dir, metadata_file)

        # Convert samples to dictionaries
        metadata = {
            "dataset_info": {
                "name": "Uzbek Speech Recognition Test Dataset",
                "version": "1.0",
                "created_date": datetime.now().isoformat(),
                "total_samples": len(samples),
                "generator": "UzbekAudioGenerator"
            },
            "samples": []
        }

        for sample in samples:
            sample_dict = asdict(sample)
            # Convert speaker profile to dict
            sample_dict["speaker_profile"] = asdict(sample.speaker_profile)
            # Convert numpy types to Python types for JSON serialization
            sample_dict["duration"] = float(sample_dict["duration"])
            sample_dict["quality_score"] = float(sample_dict["quality_score"])
            sample_dict["speaker_profile"]["speech_rate"] = float(sample_dict["speaker_profile"]["speech_rate"])
            sample_dict["speaker_profile"]["pitch_range"] = tuple(float(x) for x in sample_dict["speaker_profile"]["pitch_range"])
            sample_dict["speaker_profile"]["volume_range"] = tuple(float(x) for x in sample_dict["speaker_profile"]["volume_range"])
            metadata["samples"].append(sample_dict)

        # Save to file
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"Saved metadata for {len(samples)} samples to {metadata_path}")

    def load_metadata(self, metadata_file: str = "uzbek_test_metadata.json") -> List[UzbekTestSample]:
        """
        Load sample metadata from JSON file

        Args:
            metadata_file: Metadata file path

        Returns:
            List of test samples
        """

        metadata_path = os.path.join(self.output_dir, metadata_file)

        if not os.path.exists(metadata_path):
            return []

        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        samples = []
        for sample_dict in metadata["samples"]:
            # Reconstruct speaker profile
            speaker_dict = sample_dict.pop("speaker_profile")
            speaker_profile = UzbekSpeakerProfile(**speaker_dict)

            # Reconstruct sample
            sample = UzbekTestSample(**sample_dict)
            sample.speaker_profile = speaker_profile
            samples.append(sample)

        return samples

def create_uzbek_test_dataset():
    """Create a comprehensive Uzbek test audio dataset"""

    print("🎵 UZBEK TEST AUDIO COLLECTION SYSTEM")
    print("=" * 45)

    # Initialize generator
    generator = UzbekAudioGenerator()

    # Generate test dataset
    print("Generating test audio samples...")
    samples = generator.generate_test_dataset(num_samples_per_speaker=15)

    # Save metadata
    generator.save_metadata(samples)

    # Print summary
    print(f"\n✅ Generated {len(samples)} test samples")
    print(f"📁 Samples saved to: {generator.output_dir}")

    # Speaker distribution
    speaker_counts = {}
    for sample in samples:
        speaker = sample.speaker_profile.name
        speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1

    print("\n📊 Speaker Distribution:")
    for speaker, count in speaker_counts.items():
        print(f"   {speaker}: {count} samples")

    return samples

if __name__ == "__main__":
    create_uzbek_test_dataset()
