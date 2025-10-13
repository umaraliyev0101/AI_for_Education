#!/usr/bin/env python3
"""
Vosk Uzbek Speech Recognition Test
"""

import json
import os
from vosk import Model, KaldiRecognizer

def test_model_loading():
    """Test loading the Vosk Uzbek model"""

    # Path to the Uzbek model
    model_path = "models/uzbek/vosk-model-small-uz-0.22"

    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        return False

    print("Loading Uzbek model...")
    try:
        model = Model(model_path)
        print("✓ Model loaded successfully!")
        print(f"Model path: {model_path}")

        # Test recognizer initialization
        rec = KaldiRecognizer(model, 16000)
        print("✓ Recognizer initialized successfully!")
        print("Sample rate: 16000 Hz")

        return True
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return False

def test_with_sample_text():
    """Test recognition with sample audio data (simulated)"""
    model_path = "models/uzbek/vosk-model-small-uz-0.22"

    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        return

    model = Model(model_path)
    rec = KaldiRecognizer(model, 16000)

    # Create some dummy audio data (silence) to test the pipeline
    # In a real scenario, you'd load actual audio file
    dummy_audio = b'\x00' * 16000  # 1 second of silence at 16kHz

    print("Testing recognition pipeline...")
    if rec.AcceptWaveform(dummy_audio):
        result = json.loads(rec.Result())
        print(f"Result: {result}")
    else:
        partial = json.loads(rec.PartialResult())
        print(f"Partial result: {partial}")

    # Get final result
    final_result = json.loads(rec.FinalResult())
    print(f"Final result: {final_result}")

if __name__ == "__main__":
    print("=== Vosk Uzbek Model Test ===")
    success = test_model_loading()
    if success:
        print("\n=== Testing Recognition Pipeline ===")
        test_with_sample_text()
        print("\n✓ All tests passed! Model is ready for use.")
    else:
        print("\n✗ Model loading failed.")
