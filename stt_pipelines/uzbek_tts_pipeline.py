#!/usr/bin/env python3
"""
Uzbek Text-to-Speech Pipeline
=============================

Educational TTS system for Uzbek language using Microsoft Edge TTS.
Optimized for teaching children with clear, natural voices.
"""

import asyncio
import io
import os
import tempfile
from typing import Dict, List, Optional, Union
import json
import time

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import simpleaudio as sa
    SIMPLE_AUDIO_AVAILABLE = True
except ImportError:
    SIMPLE_AUDIO_AVAILABLE = False

class UzbekTTSPipeline:
    """
    Uzbek Text-to-Speech Pipeline using Microsoft Edge TTS.
    Optimized for educational content and children's learning.
    """

    # Uzbek voice options (female voices suitable for education)
    UZBEK_VOICES = {
        "female_clear": "uz-UZ-MadinaNeural",  # Clear female voice
        "female_warm": "uz-UZ-SabinaNeural",   # Warm female voice
        "male_clear": "uz-UZ-SardorNeural",    # Clear male voice
    }

    def __init__(self, voice: str = "male_clear", rate: str = "+0%", volume: str = "+0%"):
        """
        Initialize Uzbek TTS Pipeline.

        Args:
            voice: Voice type ('female_clear', 'female_warm', 'male_clear')
            rate: Speech rate adjustment ('-50%' to '+50%')
            volume: Volume adjustment ('-100%' to '+100%')
        """
        if not EDGE_TTS_AVAILABLE:
            raise ImportError("edge-tts is required. Install with: pip install edge-tts")

        self.voice = self.UZBEK_VOICES.get(voice, self.UZBEK_VOICES["male_clear"])
        self.rate = rate
        self.volume = volume
        self.communicate = None

        # Audio playback setup
        self.audio_backend = self._detect_audio_backend()

        print(f"[TTS] Uzbek TTS initialized with voice: {voice} ({self.voice})")

    def _detect_audio_backend(self) -> str:
        """Detect available audio playback backend."""
        if PYGAME_AVAILABLE:
            return "pygame"
        elif SIMPLE_AUDIO_AVAILABLE:
            return "simpleaudio"
        else:
            return "file"  # Save to file only

    async def _generate_speech_async(self, text: str) -> bytes:
        """
        Generate speech audio data asynchronously.

        Args:
            text: Text to convert to speech

        Returns:
            Audio data as bytes
        """
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, volume=self.volume)

        # Collect audio data
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        return audio_data

    def generate_speech(self, text: str) -> bytes:
        """
        Generate speech from text synchronously.

        Args:
            text: Text to convert to speech

        Returns:
            Audio data as bytes
        """
        try:
            # Run async function in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_data = loop.run_until_complete(self._generate_speech_async(text))
            loop.close()
            return audio_data

        except Exception as e:
            print(f"❌ TTS generation failed: {e}")
            return b""

    def speak_text(self, text: str, save_to_file: Optional[str] = None, play_audio: bool = False) -> bool:
        """
        Convert text to speech and optionally play it.

        Args:
            text: Text to speak
            save_to_file: Optional path to save audio file
            play_audio: Whether to play the audio (default: True). Set to False when batch processing.

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"🗣️ Generating speech for: '{text[:50]}...'")

            # Generate speech
            audio_data = self.generate_speech(text)

            if not audio_data:
                return False

            # Save to file if requested
            if save_to_file:
                with open(save_to_file, 'wb') as f:
                    f.write(audio_data)
                print(f"💾 Audio saved to: {save_to_file}")
                
                # If saving to file, don't play audio (for batch processing)
                # This prevents delays when processing presentations
                if not play_audio:
                    return True

            # Play audio only if requested
            if play_audio:
                return self._play_audio(audio_data)
            
            return True

        except Exception as e:
            print(f"❌ Speech generation failed: {e}")
            return False

    def _play_audio(self, audio_data: bytes) -> bool:
        """
        Play audio data using available backend.

        Args:
            audio_data: Audio data as bytes

        Returns:
            True if successful
        """
        try:
            if self.audio_backend == "pygame":
                return self._play_with_pygame(audio_data)
            elif self.audio_backend == "simpleaudio":
                return self._play_with_simpleaudio(audio_data)
            else:
                # Save to temporary file and play with system default
                return self._play_with_system(audio_data)

        except Exception as e:
            print(f"❌ Audio playback failed: {e}")
            return False

    def _play_with_pygame(self, audio_data: bytes) -> bool:
        """Play audio using pygame."""
        if not PYGAME_AVAILABLE or pygame is None:
            return False

        try:
            pygame.mixer.init()
            audio_file = io.BytesIO(audio_data)
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.quit()
            return True

        except Exception as e:
            print(f"❌ Pygame playback failed: {e}")
            return False

    def _play_with_simpleaudio(self, audio_data: bytes) -> bool:
        """Play audio using simpleaudio."""
        try:
            # Convert bytes to numpy array (assuming 16-bit PCM)
            import numpy as np
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            # Play audio
            play_obj = sa.play_buffer(audio_array, 1, 2, 22050)  # mono, 16-bit, 22kHz
            play_obj.wait_done()
            return True

        except Exception as e:
            print(f"❌ Simpleaudio playback failed: {e}")
            return False

    def _play_with_system(self, audio_data: bytes) -> bool:
        """Play audio using system default player."""
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name

            # Play with system default
            if os.name == 'nt':  # Windows
                os.startfile(temp_path)
            else:  # Linux/Mac
                os.system(f"xdg-open {temp_path}")

            # Clean up after a delay
            import threading
            def cleanup():
                time.sleep(5)  # Wait for playback to start
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

            threading.Thread(target=cleanup, daemon=True).start()
            return True

        except Exception as e:
            print(f"❌ System playback failed: {e}")
            return False

    def get_available_voices(self) -> Dict[str, str]:
        """Get available Uzbek voices."""
        return self.UZBEK_VOICES.copy()

    def test_tts(self) -> bool:
        """
        Test TTS functionality with a sample Uzbek phrase.

        Returns:
            True if test successful
        """
        test_text = "Salom, bolalar! Bugun matematika darsimizni boshlaymiz."
        print("🧪 Testing Uzbek TTS...")
        return self.speak_text(test_text)


def create_uzbek_tts(voice: str = "male_clear") -> UzbekTTSPipeline:
    """
    Create and initialize Uzbek TTS pipeline.

    Args:
        voice: Voice type ('female_clear', 'female_warm', 'male_clear')

    Returns:
        Configured UzbekTTSPipeline instance
    """
    return UzbekTTSPipeline(voice=voice)


# Educational phrases for testing and demonstration
UZBEK_EDUCATIONAL_PHRASES = {
    "greeting": "Salom, bolalar! Bugun yangi darsni boshlaymiz.",
    "math": "Matematika - bu raqamlar va shakllar haqida fan.",
    "reading": "O'qish - bilimning kalitidir.",
    "science": "Tabiatshunoslik - dunyoni tushunish uchun muhim.",
    "encouragement": "Ajoyib! Siz juda yaxshi ish qilyapsiz!",
    "practice": "Keling, birga mashq qilaylik.",
}


if __name__ == "__main__":
    # Quick test
    if EDGE_TTS_AVAILABLE:
        tts = create_uzbek_tts()
        tts.test_tts()
    else:
        print("❌ edge-tts not available. Install with: pip install edge-tts")
