#!/usr/bin/env python3
"""
Uzbek Speech Recognition Accuracy Test
Test recognition accuracy with sample Uzbek phrases
"""

import os
import json
import numpy as np
from typing import List, Dict, Tuple
import time
from vosk import Model, KaldiRecognizer

from uzbek_audio_preprocessor import UzbekAudioPreprocessor
from uzbek_stt_pipeline import UzbekSpeechToText

class UzbekAccuracyTester:
    """
    Test recognition accuracy with sample Uzbek phrases
    """

    def __init__(self, config_path: str = "uzbek_speech_config.yaml"):
        """Initialize the accuracy tester"""

        self.config = self._load_config(config_path)
        self.preprocessor = UzbekAudioPreprocessor(config_path)

        # Sample Uzbek phrases for testing
        self.test_phrases = self._get_test_phrases()

        # Results storage
        self.results = []

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        import yaml
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            return {}

    def _get_test_phrases(self) -> List[Dict[str, str]]:
        """Get sample Uzbek phrases for testing"""

        # Common Uzbek phrases categorized by difficulty
        phrases = [
            # Basic greetings and common words
            {"text": "salom", "category": "basic", "difficulty": "easy"},
            {"text": "rahmat", "category": "basic", "difficulty": "easy"},
            {"text": "iltimos", "category": "basic", "difficulty": "easy"},
            {"text": "keling", "category": "basic", "difficulty": "easy"},
            {"text": "boring", "category": "basic", "difficulty": "easy"},
            {"text": "nima", "category": "basic", "difficulty": "easy"},
            {"text": "qayerda", "category": "basic", "difficulty": "easy"},
            {"text": "qachon", "category": "basic", "difficulty": "easy"},
            {"text": "qanday", "category": "basic", "difficulty": "easy"},
            {"text": "nega", "category": "basic", "difficulty": "easy"},

            # Simple sentences
            {"text": "salom mening ismim aliy", "category": "sentences", "difficulty": "medium"},
            {"text": "siz qayerdan keldingiz", "category": "sentences", "difficulty": "medium"},
            {"text": "bugun ob havo qanday", "category": "sentences", "difficulty": "medium"},
            {"text": "men darsda o'qiyman", "category": "sentences", "difficulty": "medium"},
            {"text": "bizning maktab katta", "category": "sentences", "difficulty": "medium"},

            # Numbers and counting
            {"text": "bir ikki uch", "category": "numbers", "difficulty": "easy"},
            {"text": "o'n yigirma o'ttiz", "category": "numbers", "difficulty": "medium"},
            {"text": "yuz ming million", "category": "numbers", "difficulty": "hard"},

            # Complex phrases with specific Uzbek sounds
            {"text": "qo'shiq kuylayman", "category": "complex", "difficulty": "hard"},
            {"text": "cho'ponning qo'zi", "category": "complex", "difficulty": "hard"},
            {"text": "g'olib g'ozlar", "category": "complex", "difficulty": "hard"},
        ]

        return phrases

    def test_with_microphone(self, duration_per_phrase: int = 5) -> Dict:
        """Test recognition with live microphone input"""

        print("🎤 Starting microphone accuracy test...")
        print("You will be prompted to speak each phrase clearly.")
        print("Press Enter to start each test phrase.\n")

        results = []

        stt = UzbekSpeechToText()

        for i, phrase_data in enumerate(self.test_phrases[:5]):  # Test first 5 phrases
            expected_text = phrase_data["text"]
            category = phrase_data["category"]
            difficulty = phrase_data["difficulty"]

            print(f"\n📝 Test {i+1}: Speak this phrase: '{expected_text}'")
            print(f"Category: {category} | Difficulty: {difficulty}")
            input("Press Enter when ready to speak...")

            # Capture recognition result
            recognized_texts = []

            def capture_result(text: str):
                recognized_texts.append(text)
                print(f"🎯 Recognized: {text}")

            stt.set_result_callback(capture_result)

            # Start listening for short duration
            if stt.start_listening():
                time.sleep(duration_per_phrase)
                stt.stop_listening()

            # Get the best recognition result
            recognized_text = recognized_texts[-1] if recognized_texts else ""

            # Calculate accuracy metrics
            wer = self._calculate_wer(expected_text, recognized_text)
            cer = self._calculate_cer(expected_text, recognized_text)

            result = {
                "expected": expected_text,
                "recognized": recognized_text,
                "category": category,
                "difficulty": difficulty,
                "wer": wer,
                "cer": cer,
                "test_type": "microphone"
            }

            results.append(result)
            print(f"   WER: {wer:.2f}, CER: {cer:.2f}")
        stt._cleanup()
        return self._analyze_results(results)

    def test_with_simulated_audio(self) -> Dict:
        """Test recognition with simulated audio data"""

        print("🔊 Starting simulated audio accuracy test...")

        model_path = self.config.get('general', {}).get('model_path', 'models/uzbek/vosk-model-small-uz-0.22')
        sample_rate = self.config.get('general', {}).get('sample_rate', 16000)

        if not os.path.exists(model_path):
            print(f"❌ Model not found at {model_path}")
            return {}

        # Load model
        model = Model(model_path)
        rec = KaldiRecognizer(model, sample_rate)

        results = []

        for phrase_data in self.test_phrases:
            expected_text = phrase_data["text"]

            # Create simulated audio (silence + noise)
            # In a real scenario, you'd load actual audio files
            duration = len(expected_text.split()) * 0.3  # Rough estimate
            samples = int(duration * sample_rate)
            rng = np.random.default_rng(seed=42)
            audio = rng.normal(0, 0.01, samples).astype(np.float32)

            # Preprocess audio
            processed_audio = self.preprocessor.preprocess_audio(audio, sample_rate)

            # Convert to bytes for Vosk
            audio_bytes = (processed_audio * 32767).astype(np.int16).tobytes()

            # Recognize
            rec.AcceptWaveform(audio_bytes)
            result = json.loads(rec.FinalResult())
            recognized_text = result.get('text', '')

            # Calculate metrics
            wer = self._calculate_wer(expected_text, recognized_text)
            cer = self._calculate_cer(expected_text, recognized_text)

            result_data = {
                "expected": expected_text,
                "recognized": recognized_text,
                "category": phrase_data["category"],
                "difficulty": phrase_data["difficulty"],
                "wer": wer,
                "cer": cer,
                "test_type": "simulated"
            }

            results.append(result_data)

        return self._analyze_results(results)

    def _calculate_wer(self, reference: str, hypothesis: str) -> float:
        """Calculate Word Error Rate"""
        if not reference:
            return 1.0 if hypothesis else 0.0

        ref_words = reference.lower().split()
        hyp_words = hypothesis.lower().split()

        # Simple WER calculation (not perfect, but good enough for testing)
        if not ref_words:
            return 0.0

        # Count substitutions, deletions, insertions
        errors = 0
        for i, ref_word in enumerate(ref_words):
            if i >= len(hyp_words) or ref_word != hyp_words[i]:
                errors += 1

        # Add extra words in hypothesis
        if len(hyp_words) > len(ref_words):
            errors += len(hyp_words) - len(ref_words)

        return errors / len(ref_words)

    def _calculate_cer(self, reference: str, hypothesis: str) -> float:
        """Calculate Character Error Rate"""
        if not reference:
            return 1.0 if hypothesis else 0.0

        ref_chars = list(reference.lower())
        hyp_chars = list(hypothesis.lower())

        if not ref_chars:
            return 0.0

        # Simple CER calculation
        errors = 0
        for i, ref_char in enumerate(ref_chars):
            if i >= len(hyp_chars) or ref_char != hyp_chars[i]:
                errors += 1

        # Add extra characters
        if len(hyp_chars) > len(ref_chars):
            errors += len(hyp_chars) - len(ref_chars)

        return errors / len(ref_chars)

    def _analyze_results(self, results: List[Dict]) -> Dict:
        """Analyze test results and generate summary"""

        if not results:
            return {}

        # Calculate overall metrics
        total_wer = sum(r['wer'] for r in results) / len(results)
        total_cer = sum(r['cer'] for r in results) / len(results)

        # Group by category
        categories = {}
        difficulties = {}

        for result in results:
            cat = result['category']
            diff = result['difficulty']

            if cat not in categories:
                categories[cat] = []
            if diff not in difficulties:
                difficulties[diff] = []

            categories[cat].append(result)
            difficulties[diff].append(result)

        # Calculate category-wise metrics
        category_metrics = {}
        for cat, cat_results in categories.items():
            category_metrics[cat] = {
                "count": len(cat_results),
                "avg_wer": sum(r['wer'] for r in cat_results) / len(cat_results),
                "avg_cer": sum(r['cer'] for r in cat_results) / len(cat_results)
            }

        difficulty_metrics = {}
        for diff, diff_results in difficulties.items():
            difficulty_metrics[diff] = {
                "count": len(diff_results),
                "avg_wer": sum(r['wer'] for r in diff_results) / len(diff_results),
                "avg_cer": sum(r['cer'] for r in diff_results) / len(diff_results)
            }

        analysis = {
            "overall": {
                "total_tests": len(results),
                "average_wer": total_wer,
                "average_cer": total_cer
            },
            "by_category": category_metrics,
            "by_difficulty": difficulty_metrics,
            "detailed_results": results
        }

        return analysis

    def print_results(self, analysis: Dict):
        """Print formatted test results"""

        if not analysis:
            print("❌ No results to display")
            return

        overall = analysis.get('overall', {})

        print("\n" + "="*60)
        print("🎯 UZBEK SPEECH RECOGNITION ACCURACY TEST RESULTS")
        print("="*60)

        print("\n📊 OVERALL PERFORMANCE:")
        print(f"   Average WER: {overall.get('average_wer', 0):.1f}%")
        print(f"   Average CER: {overall.get('average_cer', 0):.1f}%")
        print(f"   Total Tests: {overall.get('total_tests', 0)}")

        print("\n📈 PERFORMANCE BY CATEGORY:")
        for cat, metrics in analysis.get('by_category', {}).items():
            print(f"   {cat.title()}:")
            print(f"      WER: {metrics['avg_wer']:.1f}%, CER: {metrics['avg_cer']:.1f}%")
            print(f"      Tests: {metrics['count']}")

        print("\n🎚️  PERFORMANCE BY DIFFICULTY:")
        for diff, metrics in analysis.get('by_difficulty', {}).items():
            print(f"   {diff.title()}:")
            print(f"      WER: {metrics['avg_wer']:.1f}%, CER: {metrics['avg_cer']:.1f}%")
            print(f"      Tests: {metrics['count']}")

        print("\n📝 SAMPLE RECOGNITIONS:")
        for result in analysis.get('detailed_results', [])[:5]:  # Show first 5
            print(f"   Expected: '{result['expected']}'")
            print(f"   Recognized: '{result['recognized']}'")
            print(f"   WER: {result['wer']:.1f}%, CER: {result['cer']:.1f}%")
            print()

def run_accuracy_tests():
    """Run all accuracy tests"""

    tester = UzbekAccuracyTester()

    print("🧪 UZBEK SPEECH RECOGNITION ACCURACY TESTING")
    print("=" * 50)

    # Test 1: Simulated audio test
    print("\n🔊 TEST 1: Simulated Audio Recognition")
    simulated_results = tester.test_with_simulated_audio()
    tester.print_results(simulated_results)

    # Test 2: Microphone test (optional - requires user interaction)
    print("\n🎤 TEST 2: Live Microphone Recognition")
    try:
        response = input("Do you want to run live microphone tests? (y/n): ").lower().strip()
        if response == 'y':
            mic_results = tester.test_with_microphone()
            tester.print_results(mic_results)
        else:
            print("Skipping microphone test.")
    except KeyboardInterrupt:
        print("\nMicrophone test cancelled.")

    print("\n✅ Accuracy testing completed!")

if __name__ == "__main__":
    run_accuracy_tests()
