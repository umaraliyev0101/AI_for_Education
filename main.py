#!/usr/bin/env python3
"""
Uzbek Whisper STT System
========================

Complete Uzbek speech-to-text system using OpenAI Whisper.
"""

from uzbek_whisper_pipeline import UzbekWhisperSTT, create_uzbek_whisper_stt
from uzbek_accuracy_testing_framework import UzbekAccuracyTester, run_whisper_accuracy_test
import sys
import threading
import queue
import time
import numpy as np

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio not available. Live transcription will not work.")

def main():
    """Main entry point for the Uzbek STT system"""

    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [args...]")
        print("Commands:")
        print("  test          - Run accuracy testing")
        print("  transcribe    - Transcribe audio file")
        print("  live          - Live transcription from microphone")
        print("  interactive   - Interactive transcription")
        return

    command = sys.argv[1]

    if command == "test":
        print("🧪 Running Uzbek Whisper Accuracy Tests")
        run_whisper_accuracy_test()

    elif command == "transcribe":
        if len(sys.argv) < 3:
            print("Usage: python main.py transcribe <audio_file.wav>")
            return

        audio_file = sys.argv[2]
        print(f"🎙️ Transcribing: {audio_file}")

        stt = create_uzbek_whisper_stt()
        result = stt.transcribe_file(audio_file)

        print("📝 Transcription Result:")
        print(f"Text: {result['text']}")
        print(".3f")

    elif command == "live":
        if not PYAUDIO_AVAILABLE:
            print("❌ PyAudio is required for live transcription.")
            print("Install it with: pip install pyaudio")
            return

        print("🎙️ Uzbek Whisper STT - Live Transcription Mode")
        print("Press Ctrl+C to stop")

        try:
            live_transcription()
        except KeyboardInterrupt:
            print("\n👋 Live transcription stopped!")

    elif command == "interactive":
        print("🎙️ Uzbek Whisper STT - Interactive Mode")
        print("Type 'quit' to exit")

        stt = create_uzbek_whisper_stt()

        while True:
            try:
                text = input("\nEnter text to simulate transcription (or 'quit'): ")
                if text.lower() == 'quit':
                    break

                # For demo purposes, we'll just show the model info
                # In a real interactive mode, you'd capture audio
                info = stt.get_model_info()
                print(f"Whisper model ready: {info['model_name']} on {info['device']}")

            except KeyboardInterrupt:
                break

        print("\n👋 Goodbye!")

    else:
        print(f"Unknown command: {command}")
        print("Available commands: test, transcribe, live, interactive")

def live_transcription():
    """Live transcription from microphone using Whisper"""

    # Audio parameters
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 3  # Process every 3 seconds

    # Initialize STT
    stt = create_uzbek_whisper_stt()

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open microphone stream
    stream = audio.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)

    print("🎤 Listening... (Speak in Uzbek)")
    print("💡 Processing every 3 seconds of audio")

    try:
        while True:
            # Record audio for RECORD_SECONDS
            frames = []

            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            # Convert to numpy array
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0

            # Skip if audio is too quiet (simple voice activity detection)
            if np.max(np.abs(audio_data)) < 0.01:
                print(".", end="", flush=True)
                continue

            # Transcribe
            print("\n🎯 Transcribing...", end="", flush=True)
            result = stt.transcribe_audio(audio_data, RATE)

            # Display result
            if result['text'].strip():
                print(f"\n📝 {result['text']}")
                print(".3f")
            else:
                print(" (no speech detected)")

    except KeyboardInterrupt:
        print("\n🛑 Stopping...")

    finally:
        # Clean up
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    main()
