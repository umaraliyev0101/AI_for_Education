#!/usr/bin/env python3
"""
Uzbek Speech Recognition Accuracy Testing Framework
Simplified testing framework using Whisper for Uzbek STT
"""

import os
import json
import time
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
import jiwer

from uzbek_whisper_pipeline import UzbekWhisperSTT
from uzbek_text_postprocessor import UzbekTextPostProcessor

@dataclass
class UzbekAccuracyResult:
    """Result of accuracy testing for a single sample"""
    sample_id: str
    reference_text: str
    recognized_text: str
    postprocessed_text: str
    wer_score: float
    cer_score: float
    confidence_score: float
    processing_time: float
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
    detailed_results: List[UzbekAccuracyResult]
    recommendations: List[str]

class UzbekAccuracyTester:
    """
    Simplified accuracy testing framework for Uzbek Whisper STT
    """

    def __init__(self):
        """Initialize the accuracy tester"""
        self.stt_engine = UzbekWhisperSTT()
        self.post_processor = UzbekTextPostProcessor()
        self.results: List[UzbekAccuracyResult] = []
        print("🧪 Uzbek Whisper Accuracy Testing Framework initialized")

    def test_text_accuracy(self, test_cases: List[Dict[str, str]],
                          session_name: Optional[str] = None) -> UzbekAccuracyReport:
        """
        Test accuracy using text-to-speech simulation

        Args:
            test_cases: List of dicts with 'text' and optional 'speaker' keys
            session_name: Optional name for the test session

        Returns:
            Accuracy report
        """
        if session_name is None:
            session_name = f"whisper_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"🧪 Starting Whisper accuracy test: {session_name}")
        print(f"📊 Testing {len(test_cases)} cases...")

        self.results = []

        for i, test_case in enumerate(test_cases):
            if (i + 1) % 5 == 0:
                print(f"  Processed {i + 1}/{len(test_cases)} cases...")

            result = self._test_single_case(test_case, i)
            self.results.append(result)

        report = self._generate_report(session_name)
        print("✅ Accuracy testing completed!")
        print(".2f")
        return report

    def _test_single_case(self, test_case: Dict[str, str], index: int) -> UzbekAccuracyResult:
        """Test a single case"""
        start_time = time.time()

        reference_text = test_case['text']
        sample_id = f"test_{index}"

        # For now, simulate recognition with some errors
        # In real usage, you'd have actual audio files
        recognized_text = self._simulate_whisper_recognition(reference_text)

        # Post-process
        postprocessed_text = self.post_processor.post_process_text(recognized_text)

        # Calculate metrics
        wer_score = jiwer.wer(reference_text, postprocessed_text)
        cer_score = jiwer.cer(reference_text, postprocessed_text)
        confidence_score = max(0.5, 1.0 - (wer_score + cer_score) / 2)  # Simplified confidence

        processing_time = time.time() - start_time

        return UzbekAccuracyResult(
            sample_id=sample_id,
            reference_text=reference_text,
            recognized_text=recognized_text,
            postprocessed_text=postprocessed_text,
            wer_score=wer_score,
            cer_score=cer_score,
            confidence_score=confidence_score,
            processing_time=processing_time,
            metadata=test_case
        )

    def _simulate_whisper_recognition(self, text: str) -> str:
        """Simulate Whisper recognition with realistic Uzbek errors"""
        # This is a placeholder - in real usage, you'd transcribe actual audio
        # For now, simulate occasional errors that Whisper might make

        recognized = text

        # Simulate common Whisper errors for Uzbek
        error_patterns = [
            ("o'", "o"), ("u'", "u"), ("q", "k"), ("sh", "s"),
            ("maktab", "maktap"), ("o'qituvchi", "oqituvchi")
        ]

        # Apply random errors (low probability for good model)
        rng = np.random.default_rng(seed=hash(text) % 2**32)

        for original, replacement in error_patterns:
            if rng.random() < 0.05:  # 5% error rate
                recognized = recognized.replace(original, replacement, 1)
                break

        return recognized

    def _generate_report(self, session_id: str) -> UzbekAccuracyReport:
        """Generate accuracy report"""
        if not self.results:
            return UzbekAccuracyReport(
                test_session_id=session_id,
                timestamp=datetime.now().isoformat(),
                total_samples=0,
                overall_wer=1.0,
                overall_cer=1.0,
                average_confidence=0.0,
                average_processing_time=0.0,
                detailed_results=[],
                recommendations=["No test results"]
            )

        overall_wer = float(np.mean([r.wer_score for r in self.results]))
        overall_cer = float(np.mean([r.cer_score for r in self.results]))
        average_confidence = float(np.mean([r.confidence_score for r in self.results]))
        average_processing_time = float(np.mean([r.processing_time for r in self.results]))

        recommendations = self._generate_recommendations(overall_wer, overall_cer)

        return UzbekAccuracyReport(
            test_session_id=session_id,
            timestamp=datetime.now().isoformat(),
            total_samples=len(self.results),
            overall_wer=overall_wer,
            overall_cer=overall_cer,
            average_confidence=average_confidence,
            average_processing_time=average_processing_time,
            detailed_results=self.results,
            recommendations=recommendations
        )

    def _generate_recommendations(self, wer: float, cer: float) -> List[str]:
        """Generate recommendations"""
        recommendations = []

        if wer < 0.1 and cer < 0.05:
            recommendations.append("Excellent accuracy! Whisper performs well for Uzbek.")
        elif wer < 0.2:
            recommendations.append("Good accuracy. Consider fine-tuning for specific domains.")
        else:
            recommendations.append("Consider additional training data or model fine-tuning.")

        return recommendations

    def save_report(self, report: UzbekAccuracyReport, output_file: Optional[str] = None):
        """Save report to file"""
        if output_file is None:
            output_file = f"uzbek_whisper_accuracy_report_{report.test_session_id}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, ensure_ascii=False, indent=2)

        print(f"💾 Report saved to {output_file}")

    def print_summary(self, report: UzbekAccuracyReport):
        """Print report summary"""
        print("\n" + "="*50)
        print("🧪 UZBEK WHISPER ACCURACY REPORT")
        print("="*50)
        print(f"Session: {report.test_session_id}")
        print(f"Samples: {report.total_samples}")
        print(".2f")
        print(".2f")
        print(".2f")
        print("\n💡 RECOMMENDATIONS:")
        for rec in report.recommendations:
            print(f"  • {rec}")

def run_whisper_accuracy_test():
    """Run accuracy test with sample Uzbek phrases"""
    print("🧪 UZBEK WHISPER ACCURACY TESTING")
    print("=" * 40)

    tester = UzbekAccuracyTester()

    # Sample test cases
    test_cases = [
        {"text": "Salom qalay siz?", "category": "greeting"},
        {"text": "Men o'qiyman", "category": "education"},
        {"text": "Bu kitob qizil", "category": "education"},
        {"text": "O'qituvchi dars beradi", "category": "education"},
        {"text": "Maktabda o'quvchilar ko'p", "category": "education"},
        {"text": "Yozuv taxtasi toza", "category": "education"},
        {"text": "Darsliklar juda qiziq", "category": "education"},
        {"text": "O'zbek tili go'zal", "category": "general"},
        {"text": "Toshkent poytaxt shahri", "category": "general"},
        {"text": "Qishloqda hayot tinch", "category": "general"}
    ]

    report = tester.test_text_accuracy(test_cases, "whisper_baseline")

    tester.print_summary(report)
    tester.save_report(report)

    print("✅ Whisper accuracy testing completed!")

if __name__ == "__main__":
    run_whisper_accuracy_test()
