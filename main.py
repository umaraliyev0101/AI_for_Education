#!/usr/bin/env python3
"""
Uzbek Whisper STT System
========================

Complete Uzbek speech-to-text system using OpenAI Whisper.
"""

from uzbek_whisper_pipeline import UzbekWhisperSTT, create_uzbek_whisper_stt
from uzbek_accuracy_testing_framework import UzbekAccuracyTester, run_whisper_accuracy_test
import sys

def main():
    """Main entry point for the Uzbek STT system"""

    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [args...]")
        print("Commands:")
        print("  test          - Run accuracy testing")
        print("  transcribe    - Transcribe audio file")
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
        print("Available commands: test, transcribe, interactive")

if __name__ == "__main__":
    main()
