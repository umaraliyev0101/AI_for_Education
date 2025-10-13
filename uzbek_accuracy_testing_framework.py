#!/usr/bin/env python3
"""
Uzbek Speech Recognition Accuracy Testing Framework
Comprehensive testing framework with WER/CER metrics and detailed reporting
"""

import os
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    import matplotlib.pyplot as plt
    VISUALIZATION_AVAILABLE = False
from collections import defaultdict
import jiwer  # For WER/CER calculations

from uzbek_stt_pipeline import UzbekSpeechToText
from uzbek_text_postprocessor import UzbekTextPostProcessor
from uzbek_test_audio_collection import UzbekTestSample
from uzbek_test_audio_collection import UzbekTestSample

@dataclass
class UzbekAccuracyResult:
    """Result of accuracy testing for a single sample"""

    sample_id: str
    reference_text: str
    recognized_text: str
    postprocessed_text: str
    wer_score: float  # Word Error Rate
    cer_score: float  # Character Error Rate
    confidence_score: float
    processing_time: float  # seconds
    speaker_profile: str
    difficulty_level: str
    category: str
    metadata: Dict[str, Any]

@dataclass
class UzbekAccuracyReport:
    """Comprehensive accuracy report"""

    test_session_id: str
    timestamp: str
    total_samples: int
    overall_wer: float
    overall_cer: float
    average_confidence: float
    average_processing_time: float
    results_by_speaker: Dict[str, Dict[str, float]]
    results_by_difficulty: Dict[str, Dict[str, float]]
    results_by_category: Dict[str, Dict[str, float]]
    detailed_results: List[UzbekAccuracyResult]
    recommendations: List[str]

class UzbekAccuracyTester:
    """
    Comprehensive accuracy testing framework for Uzbek speech recognition
    """

    def __init__(self, config_path: str = "uzbek_speech_config.yaml",
                 test_audio_dir: str = "test_audio/uzbek_samples"):
        """Initialize the accuracy tester"""

        self.config_path = config_path
        self.test_audio_dir = test_audio_dir

        # Initialize components
        self.stt_engine = UzbekSpeechToText(config_path)
        self.post_processor = UzbekTextPostProcessor(config_path)

        # Test results storage
        self.results: List[UzbekAccuracyResult] = []
        self.current_session_id = None

        # Performance tracking
        self.session_stats = defaultdict(list)

        print("🧪 Uzbek Accuracy Testing Framework initialized")

    def run_accuracy_test(self, test_samples: List[UzbekTestSample],
                         session_name: str = None) -> UzbekAccuracyReport:
        """
        Run comprehensive accuracy testing on a set of samples

        Args:
            test_samples: List of test samples to evaluate
            session_name: Optional name for the test session

        Returns:
            Comprehensive accuracy report
        """

        if session_name is None:
            session_name = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.current_session_id = session_name
        print(f"🧪 Starting accuracy test session: {session_name}")
        print(f"📊 Testing {len(test_samples)} samples...")

        # Clear previous results
        self.results = []

        # Process each sample
        for i, sample in enumerate(test_samples):
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(test_samples)} samples...")

            result = self._test_single_sample(sample)
            self.results.append(result)

        # Generate comprehensive report
        report = self._generate_accuracy_report()

        print("✅ Accuracy testing completed!")
        print(f"📊 Overall WER: {report.overall_wer:.2f}, CER: {report.overall_cer:.2f}")
        return report

    def _test_single_sample(self, sample: UzbekTestSample) -> UzbekAccuracyResult:
        """
        Test accuracy on a single sample

        Args:
            sample: Test sample to evaluate

        Returns:
            Accuracy result
        """

        start_time = time.time()

        try:
            # Load audio file
            if not os.path.exists(sample.file_path):
                raise FileNotFoundError(f"Audio file not found: {sample.file_path}")

            # Recognize speech (using file-based recognition if available)
            # For now, we'll simulate recognition using the reference text
            # In a real implementation, you'd load and process the actual audio

            # Simulate recognition result (replace with actual STT processing)
            recognized_text = self._simulate_recognition(sample.text, sample.speaker_profile)

            # Post-process the recognized text
            postprocessed_text = self.post_processor.post_process_text(recognized_text)

            # Calculate accuracy metrics
            wer_score = jiwer.wer(sample.text, postprocessed_text)
            cer_score = jiwer.cer(sample.text, postprocessed_text)

            # Calculate confidence (simplified)
            confidence_score = self.post_processor.get_confidence_score(recognized_text, postprocessed_text)

            processing_time = time.time() - start_time

            result = UzbekAccuracyResult(
                sample_id=sample.sample_id,
                reference_text=sample.text,
                recognized_text=recognized_text,
                postprocessed_text=postprocessed_text,
                wer_score=wer_score,
                cer_score=cer_score,
                confidence_score=confidence_score,
                processing_time=processing_time,
                speaker_profile=sample.speaker_profile.name,
                difficulty_level="intermediate",  # Could be determined from sample
                category="general",  # Could be determined from sample
                metadata={
                    "audio_file": sample.file_path,
                    "sample_quality": sample.quality_score,
                    "tags": sample.tags
                }
            )

            return result

        except Exception as e:
            # Handle errors gracefully
            processing_time = time.time() - start_time

            result = UzbekAccuracyResult(
                sample_id=sample.sample_id,
                reference_text=sample.text,
                recognized_text="",
                postprocessed_text="",
                wer_score=1.0,  # 100% error
                cer_score=1.0,  # 100% error
                confidence_score=0.0,
                processing_time=processing_time,
                speaker_profile=sample.speaker_profile.name,
                difficulty_level="unknown",
                category="error",
                metadata={"error": str(e)}
            )

            return result

    def _simulate_recognition(self, reference_text: str, speaker_profile) -> str:
        """
        Simulate speech recognition result (for testing purposes)
        In a real implementation, this would process actual audio

        Args:
            reference_text: Original text
            speaker_profile: Speaker characteristics

        Returns:
            Simulated recognized text with realistic errors
        """

        # Simulate recognition errors based on speaker profile and text complexity
        recognized = reference_text

        # Simulate common recognition errors
        error_patterns = [
            ("o'", "o"),  # Missing hamza
            ("u'", "u"),  # Missing hamza
            ("q", "k"),   # q -> k confusion
            ("sh", "s"),  # sh -> s confusion
            ("ch", "s"),  # ch -> s confusion
            ("ng", "n"),  # ng -> n confusion
        ]

        # Apply errors based on speaker profile difficulty
        error_rate = 0.1  # Base error rate

        if speaker_profile.age_group == "child":
            error_rate += 0.1  # Children have more pronunciation variations
        if speaker_profile.accent_type == "regional":
            error_rate += 0.05  # Regional accents may cause recognition issues
        if speaker_profile.background_noise != "none":
            error_rate += 0.05  # Background noise affects recognition

        # Apply random errors
        rng = np.random.default_rng(seed=hash(reference_text) % 2**32)

        for original, replacement in error_patterns:
            if rng.random() < error_rate and original in recognized:
                recognized = recognized.replace(original, replacement, 1)
                break  # Only apply one error per word for realism

        # Simulate partial recognition (missing words)
        if rng.random() < 0.05:  # 5% chance of partial recognition
            words = recognized.split()
            if len(words) > 1:
                # Remove a random word
                remove_idx = rng.integers(0, len(words))
                words.pop(remove_idx)
                recognized = " ".join(words)

        return recognized

    def _generate_accuracy_report(self) -> UzbekAccuracyReport:
        """Generate comprehensive accuracy report"""

        if not self.results:
            return UzbekAccuracyReport(
                test_session_id=self.current_session_id or "empty",
                timestamp=datetime.now().isoformat(),
                total_samples=0,
                overall_wer=1.0,
                overall_cer=1.0,
                average_confidence=0.0,
                average_processing_time=0.0,
                results_by_speaker={},
                results_by_difficulty={},
                results_by_category={},
                detailed_results=[],
                recommendations=["No test results available"]
            )

        # Calculate overall metrics
        overall_wer = np.mean([r.wer_score for r in self.results])
        overall_cer = np.mean([r.cer_score for r in self.results])
        average_confidence = np.mean([r.confidence_score for r in self.results])
        average_processing_time = np.mean([r.processing_time for r in self.results])

        # Group results by categories
        results_by_speaker = self._group_results("speaker_profile")
        results_by_difficulty = self._group_results("difficulty_level")
        results_by_category = self._group_results("category")

        # Generate recommendations
        recommendations = self._generate_recommendations(overall_wer, overall_cer)

        report = UzbekAccuracyReport(
            test_session_id=self.current_session_id,
            timestamp=datetime.now().isoformat(),
            total_samples=len(self.results),
            overall_wer=overall_wer,
            overall_cer=overall_cer,
            average_confidence=average_confidence,
            average_processing_time=average_processing_time,
            results_by_speaker=results_by_speaker,
            results_by_difficulty=results_by_difficulty,
            results_by_category=results_by_category,
            detailed_results=self.results,
            recommendations=recommendations
        )

        return report

    def _group_results(self, group_by: str) -> Dict[str, Dict[str, float]]:
        """Group results by a specific attribute"""

        groups = defaultdict(list)

        for result in self.results:
            group_key = getattr(result, group_by)
            groups[group_key].append(result)

        # Calculate metrics for each group
        group_metrics = {}
        for group_name, group_results in groups.items():
            group_metrics[group_name] = {
                "wer": np.mean([r.wer_score for r in group_results]),
                "cer": np.mean([r.cer_score for r in group_results]),
                "confidence": np.mean([r.confidence_score for r in group_results]),
                "count": len(group_results)
            }

        return dict(group_metrics)

    def _generate_recommendations(self, overall_wer: float, overall_cer: float) -> List[str]:
        """Generate recommendations based on accuracy results"""

        recommendations = []

        if overall_wer > 0.3:
            recommendations.append("High word error rate detected. Consider improving acoustic model training.")
        elif overall_wer > 0.2:
            recommendations.append("Moderate word error rate. Fine-tuning the language model may help.")

        if overall_cer > 0.15:
            recommendations.append("High character error rate suggests pronunciation variations. Consider expanding phonetic dictionary.")

        if overall_wer < 0.1 and overall_cer < 0.05:
            recommendations.append("Excellent accuracy achieved! Consider testing with more diverse speakers.")

        # Speaker-specific recommendations
        speaker_results = self._group_results("speaker_profile")
        for speaker, metrics in speaker_results.items():
            if metrics["wer"] > overall_wer + 0.1:
                recommendations.append(f"Speaker '{speaker}' shows significantly lower accuracy. Consider additional training data for this profile.")

        if not recommendations:
            recommendations.append("Accuracy testing completed successfully. No specific recommendations at this time.")

        return recommendations

    def save_report(self, report: UzbekAccuracyReport, output_file: str = None):
        """Save accuracy report to file"""

        if output_file is None:
            output_file = f"uzbek_accuracy_report_{report.test_session_id}.json"

        # Convert report to dictionary
        report_dict = asdict(report)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2)

        print(f"💾 Accuracy report saved to {output_file}")

    def generate_visual_report(self, report: UzbekAccuracyReport, output_dir: str = "accuracy_reports"):
        """Generate visual report with charts and graphs"""

        os.makedirs(output_dir, exist_ok=True)

        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Uzbek STT Accuracy Report - {report.test_session_id}', fontsize=16)

        # Overall metrics
        axes[0, 0].bar(['WER', 'CER'], [report.overall_wer, report.overall_cer],
                      color=['skyblue', 'lightcoral'])
        axes[0, 0].set_title('Overall Accuracy Metrics')
        axes[0, 0].set_ylabel('Error Rate')
        axes[0, 0].set_ylim(0, 1)

        # Speaker performance
        if report.results_by_speaker:
            speakers = list(report.results_by_speaker.keys())
            wer_scores = [report.results_by_speaker[s]['wer'] for s in speakers]

            axes[0, 1].bar(speakers, wer_scores)
            axes[0, 1].set_title('WER by Speaker Profile')
            axes[0, 1].set_ylabel('Word Error Rate')
            axes[0, 1].tick_params(axis='x', rotation=45)

        # Processing time distribution
        processing_times = [r.processing_time for r in report.detailed_results]
        axes[1, 0].hist(processing_times, bins=20, alpha=0.7, color='green')
        axes[1, 0].set_title('Processing Time Distribution')
        axes[1, 0].set_xlabel('Time (seconds)')
        axes[1, 0].set_ylabel('Frequency')

        # Confidence vs WER scatter plot
        confidences = [r.confidence_score for r in report.detailed_results]
        wers = [r.wer_score for r in report.detailed_results]
        axes[1, 1].scatter(confidences, wers, alpha=0.6)
        axes[1, 1].set_title('Confidence vs Word Error Rate')
        axes[1, 1].set_xlabel('Confidence Score')
        axes[1, 1].set_ylabel('Word Error Rate')

        plt.tight_layout()

        # Save the plot
        plot_file = os.path.join(output_dir, f"{report.test_session_id}_accuracy_report.png")
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"📊 Visual report saved to {plot_file}")

    def print_report_summary(self, report: UzbekAccuracyReport):
        """Print a summary of the accuracy report"""

        print("\n" + "="*60)
        print("🧪 UZBEK SPEECH RECOGNITION ACCURACY REPORT")
        print("="*60)
        print(f"Session ID: {report.test_session_id}")
        print(f"Timestamp: {report.timestamp}")
        print(f"Total Samples: {report.total_samples}")
        print(".2f")
        print(".2f")
        print(".2f")
        print(".3f")

        print("\n📊 PERFORMANCE BY SPEAKER:")
        for speaker, metrics in report.results_by_speaker.items():
            print(f"  {speaker}:")
            print(f"    WER: {metrics['wer']:.2f}, CER: {metrics['cer']:.2f}, Samples: {metrics['count']}")
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")

def run_comprehensive_accuracy_test():
    """Run comprehensive accuracy testing using generated test samples"""

    print("🧪 COMPREHENSIVE UZBEK ACCURACY TESTING")
    print("=" * 45)

    # Initialize tester
    tester = UzbekAccuracyTester()

    # Load test samples (if available)
    test_samples = []
    metadata_file = "test_audio/uzbek_samples/uzbek_test_metadata.json"

    if os.path.exists(metadata_file):
        print("Loading existing test samples...")
        from uzbek_test_audio_collection import UzbekTestSample, UzbekSpeakerProfile

        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for sample_data in data["samples"]:
            # Reconstruct speaker profile
            speaker_data = sample_data.pop("speaker_profile")
            speaker_profile = UzbekSpeakerProfile(**speaker_data)
            sample = UzbekTestSample(speaker_profile=speaker_profile, **sample_data)
            test_samples.append(sample)

        print(f"Loaded {len(test_samples)} test samples")
    else:
        print("No existing test samples found. Generating sample test data...")

        # Create sample test data for demonstration
        from uzbek_test_audio_collection import UzbekSpeakerProfile

        speaker = UzbekSpeakerProfile(
            speaker_id="demo_speaker",
            name="Demo Speaker",
            region="Toshkent",
            age_group="adult",
            gender="male",
            accent_type="standard",
            speech_rate=150.0,
            pitch_range=(85, 180),
            volume_range=(0.7, 0.9),
            background_noise="none"
        )

        test_phrases = [
            "Salom qalay siz?",
            "Men o'qiyman",
            "Bu kitob qizil",
            "O'qituvchi dars beradi"
        ]

        # Create mock test samples
        for i, phrase in enumerate(test_phrases):
            sample = UzbekTestSample(
                sample_id=f"demo_{i}",
                text=phrase,
                speaker_profile=speaker,
                duration=2.0,
                sample_rate=16000,
                audio_format="wav",
                file_path=f"demo_{i}.wav",
                created_date=datetime.now().isoformat(),
                quality_score=0.9,
                transcription_verified=True,
                tags=["demo", "educational"],
                metadata={}
            )
            test_samples.append(sample)

    # Run accuracy testing
    report = tester.run_accuracy_test(test_samples, "comprehensive_test")

    # Print summary
    tester.print_report_summary(report)

    # Save detailed report
    tester.save_report(report)

    # Generate visual report
    tester.generate_visual_report(report)

    print("✅ Comprehensive accuracy testing completed!")

    return report

if __name__ == "__main__":
    run_comprehensive_accuracy_test()
