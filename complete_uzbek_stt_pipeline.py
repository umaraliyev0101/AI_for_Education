#!/usr/bin/env python3
"""
Complete Uzbek Speech-to-Text Pipeline
Integration of all components: preprocessing, recognition, and post-processing
"""

import time
import threading
import queue
import numpy as np
from typing import Optional, Callable, Dict, Any
import json
import os

from uzbek_stt_pipeline import UzbekSpeechToText
from uzbek_text_postprocessor import UzbekTextPostProcessor

class CompleteUzbekSTTPipeline:
    """
    Complete Uzbek Speech-to-Text pipeline with all components integrated
    """

    def __init__(self, config_path: str = "uzbek_speech_config.yaml"):
        """Initialize the complete pipeline"""

        self.config = self._load_config(config_path)

        # Initialize components
        self.stt_engine = UzbekSpeechToText(config_path)
        self.post_processor = UzbekTextPostProcessor(config_path)

        # Pipeline state
        self.is_running = False
        self.audio_queue = queue.Queue(maxsize=100)
        self.result_queue = queue.Queue(maxsize=50)

        # Processing thread
        self.processing_thread = None

        # Callbacks
        self.on_result_callback: Optional[Callable[[str, float], None]] = None
        self.on_error_callback: Optional[Callable[[str], None]] = None

        print("🎯 Complete Uzbek STT Pipeline initialized")

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        import yaml
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            return {}

    def start_listening(self, on_result: Optional[Callable[[str, float], None]] = None,
                       on_error: Optional[Callable[[str], None]] = None) -> bool:
        """
        Start the continuous listening pipeline

        Args:
            on_result: Callback function for recognition results (text, confidence)
            on_error: Callback function for errors

        Returns:
            True if started successfully, False otherwise
        """

        if self.is_running:
            print("⚠️  Pipeline is already running")
            return False

        self.on_result_callback = on_result
        self.on_error_callback = on_error

        try:
            # Set callback on STT engine
            def stt_callback(text: str):
                # Post-process the text
                processed_text = self.post_processor.post_process_text(text)

                # Calculate post-processing confidence (simplified)
                post_confidence = self.post_processor.get_confidence_score(text, processed_text)

                # Use a default confidence since STT engine doesn't provide it
                final_confidence = post_confidence  # Could be improved

                print(f"📝 Recognized: '{processed_text}' (confidence: {final_confidence:.2f})")

                # Call result callback
                if self.on_result_callback:
                    self.on_result_callback(processed_text, final_confidence)

            self.stt_engine.set_result_callback(stt_callback)

            # Start the STT engine
            if not self.stt_engine.start_listening():
                raise RuntimeError("Failed to start STT engine")

            self.is_running = True

            print("🎤 Uzbek STT Pipeline started - listening for speech...")
            return True

        except Exception as e:
            error_msg = f"Failed to start pipeline: {str(e)}"
            print(f"❌ {error_msg}")
            if self.on_error_callback:
                self.on_error_callback(error_msg)
            return False

    def stop_listening(self) -> bool:
        """
        Stop the listening pipeline

        Returns:
            True if stopped successfully, False otherwise
        """

        if not self.is_running:
            print("⚠️  Pipeline is not running")
            return False

        try:
            self.is_running = False

            # Stop STT engine
            self.stt_engine.stop_listening()

            print("🛑 Uzbek STT Pipeline stopped")
            return True

        except Exception as e:
            error_msg = f"Error stopping pipeline: {str(e)}"
            print(f"❌ {error_msg}")
            if self.on_error_callback:
                self.on_error_callback(error_msg)
            return False

    def recognize_file(self, audio_file_path: str) -> Optional[tuple[str, float]]:
        """
        Recognize speech from an audio file

        Args:
            audio_file_path: Path to the audio file

        Returns:
            Tuple of (recognized_text, confidence) or None if failed
        """

        # Note: File recognition not implemented in current STT engine
        # This would require extending the UzbekSpeechToText class
        print(f"⚠️  File recognition not implemented in current version (file: {audio_file_path})")
        return None

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""

        return {
            'is_running': self.is_running,
            'stt_engine_listening': self.stt_engine.is_listening if hasattr(self.stt_engine, 'is_listening') else False,
        }

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_listening()

def demo_pipeline():
    """Demonstrate the complete Uzbek STT pipeline"""

    def on_result(text: str, confidence: float):
        """Handle recognition results"""
        print(f"🎯 Result: '{text}' (confidence: {confidence:.2f})")

    def on_error(error: str):
        """Handle errors"""
        print(f"❌ Error: {error}")

    print("🚀 UZBEK SPEECH-TO-TEXT PIPELINE DEMO")
    print("=" * 45)

    # Create pipeline
    pipeline = CompleteUzbekSTTPipeline()

    try:
        # Test file recognition first
        print("\n📁 Testing file recognition...")

        # Create a simple test audio file (you would normally have a real audio file)
        # For demo purposes, we'll skip file testing if no test file exists

        test_file = "test_uzbek_audio.wav"
        if os.path.exists(test_file):
            result = pipeline.recognize_file(test_file)
            if result:
                text, confidence = result
                print(f"File recognition result: '{text}' (confidence: {confidence:.2f})")
        else:
            print("No test audio file found - skipping file recognition test")

        # Test real-time recognition
        print("\n🎤 Testing real-time recognition...")
        print("Speak some Uzbek words/phrases. Press Ctrl+C to stop.")

        # Start listening
        if pipeline.start_listening(on_result=on_result, on_error=on_error):
            try:
                # Listen for 10 seconds
                time.sleep(10)
            except KeyboardInterrupt:
                print("\n⏹️  Interrupted by user")
            finally:
                pipeline.stop_listening()
        else:
            print("❌ Failed to start listening")

    except Exception as e:
        print(f"❌ Demo error: {str(e)}")
    finally:
        # Ensure pipeline is stopped
        pipeline.stop_listening()

    print("\n✅ Demo completed")

if __name__ == "__main__":
    demo_pipeline()
