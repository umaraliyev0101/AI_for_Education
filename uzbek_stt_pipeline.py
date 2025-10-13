#!/usr/bin/env python3
"""
Uzbek Speech-to-Text Pipeline
Real-time speech recognition with microphone input and Uzbek optimizations
"""

import json
import os
import threading
import time
import queue
from typing import Optional, Callable, List
import numpy as np
import pyaudio
from vosk import Model, KaldiRecognizer

from uzbek_audio_preprocessor import UzbekAudioPreprocessor

class UzbekSpeechToText:
    """
    Real-time Uzbek speech-to-text pipeline with microphone input
    """

    def __init__(self, config_path: str = "uzbek_speech_config.yaml"):
        """Initialize the Uzbek STT pipeline"""

        # Load configuration
        self.config = self._load_config(config_path)

        # Initialize components
        self.preprocessor = UzbekAudioPreprocessor(config_path)
        self.model = None
        self.recognizer = None
        self.audio_stream = None
        self.audio_interface = None

        # Audio settings
        self.sample_rate = self.config.get('general', {}).get('sample_rate', 16000)
        self.chunk_size = 4000  # Audio chunk size for processing

        # Recognition settings
        self.silence_timeout = self.config.get('recognition_settings', {}).get('silence_timeout', 1.0)
        self.speech_timeout = self.config.get('recognition_settings', {}).get('speech_timeout', 10.0)

        # State variables
        self.is_listening = False
        self.is_recognizing = False
        self.audio_queue = queue.Queue()
        self.result_callback: Optional[Callable] = None

        # Load the model
        self._load_model()

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        import yaml
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            return {}

    def _load_model(self):
        """Load the Vosk Uzbek model"""
        model_path = self.config.get('general', {}).get('model_path', 'models/uzbek/vosk-model-small-uz-0.22')

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")

        print(f"Loading Uzbek model from {model_path}...")
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
        print("✓ Model loaded successfully")

    def set_result_callback(self, callback: Callable[[str], None]):
        """Set callback function for recognition results"""
        self.result_callback = callback

    def start_listening(self) -> bool:
        """Start microphone listening and speech recognition"""
        if self.is_listening:
            print("Already listening")
            return False

        try:
            # Initialize PyAudio
            self.audio_interface = pyaudio.PyAudio()

            # Find input device
            input_device_index = self._find_input_device()
            if input_device_index is None:
                print("❌ No suitable input device found")
                return False

            # Open audio stream
            self.audio_stream = self.audio_interface.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=self.chunk_size
            )

            self.is_listening = True
            self.is_recognizing = True

            # Start recognition thread
            recognition_thread = threading.Thread(target=self._recognition_loop, daemon=True)
            recognition_thread.start()

            print("🎤 Started listening for Uzbek speech...")
            return True

        except Exception as e:
            print(f"❌ Failed to start listening: {e}")
            self._cleanup()
            return False

    def stop_listening(self):
        """Stop microphone listening and recognition"""
        if not self.is_listening:
            return

        print("🛑 Stopping speech recognition...")
        self.is_recognizing = False
        self.is_listening = False
        self._cleanup()

    def _find_input_device(self) -> Optional[int]:
        """Find a suitable input device"""
        if self.audio_interface is None:
            return None

        try:
            info = self.audio_interface.get_host_api_info_by_index(0)
            num_devices = int(info.get('deviceCount', 0))

            for i in range(num_devices):
                device_info = self.audio_interface.get_device_info_by_host_api_device_index(0, i)
                max_input_channels = device_info.get('maxInputChannels', 0)
                if isinstance(max_input_channels, (int, float)) and max_input_channels > 0:
                    print(f"Found input device: {device_info.get('name')}")
                    return i

        except Exception as e:
            print(f"Error finding input device: {e}")

        return None

    def _recognition_loop(self):
        """Main recognition loop running in separate thread"""
        print("🔄 Recognition loop started")

        last_speech_time = time.time()
        silence_start = None

        try:
            while self.is_recognizing:
                # Read audio chunk
                if self.audio_stream is None:
                    break

                try:
                    data = self.audio_stream.read(self.chunk_size, exception_on_overflow=False)
                except Exception as e:
                    print(f"Audio read error: {e}")
                    break

                # Convert to numpy array
                audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0

                # Preprocess audio
                processed_chunk = self.preprocessor.preprocess_audio(audio_chunk, self.sample_rate)

                # Convert back to bytes for Vosk
                processed_bytes = (processed_chunk * 32767).astype(np.int16).tobytes()

                # Check for speech activity
                if self._has_speech_activity(processed_chunk):
                    last_speech_time = time.time()
                    silence_start = None
                else:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > self.silence_timeout:
                        # Silence timeout - finalize current recognition
                        self._finalize_recognition()
                        silence_start = None

                # Feed to recognizer
                if self.recognizer and self.recognizer.AcceptWaveform(processed_bytes):
                    # Complete utterance
                    result = json.loads(self.recognizer.Result())
                    self._process_result(result)
                elif self.recognizer:
                    # Partial result
                    partial = json.loads(self.recognizer.PartialResult())
                    if partial.get('partial', '').strip():
                        # Optional: handle partial results
                        pass

                # Check for overall timeout
                if time.time() - last_speech_time > self.speech_timeout:
                    print("Speech timeout reached")
                    break

        except Exception as e:
            print(f"Recognition loop error: {e}")

        finally:
            self._finalize_recognition()
            print("🔄 Recognition loop ended")

    def _has_speech_activity(self, audio_chunk: np.ndarray, threshold: float = 0.01) -> bool:
        """Check if audio chunk contains speech activity"""
        # Simple energy-based detection
        energy = np.sqrt(np.mean(audio_chunk ** 2))
        return energy > threshold

    def _finalize_recognition(self):
        """Finalize current recognition and get final result"""
        if self.recognizer:
            final_result = json.loads(self.recognizer.FinalResult())
            self._process_result(final_result)

    def _process_result(self, result: dict):
        """Process recognition result"""
        text = result.get('text', '').strip()
        if text and self.result_callback:
            # Post-process the text
            processed_text = self._post_process_text(text)
            self.result_callback(processed_text)

    def _post_process_text(self, text: str) -> str:
        """Apply Uzbek-specific text post-processing"""
        if not text:
            return text

        # Basic post-processing for Uzbek text
        # This will be expanded in the text post-processing task

        # Remove extra spaces
        text = ' '.join(text.split())

        # Basic capitalization (first word of sentence)
        if text:
            text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()

        return text

    def _cleanup(self):
        """Clean up audio resources"""
        if self.audio_stream:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            except Exception:
                pass
            self.audio_stream = None

        if self.audio_interface:
            try:
                self.audio_interface.terminate()
            except Exception:
                pass
            self.audio_interface = None

    def __del__(self):
        """Destructor - ensure cleanup"""
        self._cleanup()

def test_microphone_input():
    """Test microphone input functionality"""

    def result_handler(text: str):
        print(f"🎯 Recognized: {text}")

    # Initialize STT pipeline
    stt = UzbekSpeechToText()

    # Set result callback
    stt.set_result_callback(result_handler)

    print("Testing microphone input...")
    print("Speak some Uzbek phrases. Press Ctrl+C to stop.")

    try:
        # Start listening
        if stt.start_listening():
            # Keep running until interrupted
            while stt.is_listening:
                time.sleep(0.1)
        else:
            print("❌ Failed to start microphone input")

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stt.stop_listening()

if __name__ == "__main__":
    test_microphone_input()
