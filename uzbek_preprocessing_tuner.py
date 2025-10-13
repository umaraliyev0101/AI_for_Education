#!/usr/bin/env python3
"""
Uzbek Audio Preprocessing Tuning
Optimize preprocessing parameters for Uzbek speech recognition
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import json
import os
from vosk import Model, KaldiRecognizer

from uzbek_audio_preprocessor import UzbekAudioPreprocessor

class UzbekPreprocessingTuner:
    """
    Tune audio preprocessing parameters for optimal Uzbek speech recognition
    """

    def __init__(self, config_path: str = "uzbek_speech_config.yaml"):
        """Initialize the tuner"""

        self.config = self._load_config(config_path)
        self.base_preprocessor = UzbekAudioPreprocessor(config_path)

        # Parameter ranges to test
        self.parameter_ranges = {
            'noise_reduction': [True, False],
            'normalization': [True, False],
            'frequency_range': [
                [50, 8000],    # Wide range
                [80, 8000],    # Standard speech
                [100, 4000],   # Telephone quality
                [200, 3400],   # Narrow band
            ],
            'speech_threshold': [0.005, 0.01, 0.02, 0.05],
            'compression_ratio': [2.0, 4.0, 6.0, 8.0],
            'compression_threshold': [0.3, 0.5, 0.7]
        }

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        import yaml
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            return {}

    def generate_test_audio(self, duration: float = 2.0, sample_rate: int = 16000) -> np.ndarray:
        """Generate test audio with simulated Uzbek speech characteristics"""

        # Create time array
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

        # Generate simulated speech-like signal
        # Mix of vowels and consonants with Uzbek characteristics
        audio = np.zeros_like(t)

        # Add vowel-like sounds (formants around 700, 1200, 2500 Hz)
        f1, f2, f3 = 700, 1200, 2500
        audio += 0.3 * np.sin(2 * np.pi * f1 * t)
        audio += 0.2 * np.sin(2 * np.pi * f2 * t)
        audio += 0.1 * np.sin(2 * np.pi * f3 * t)

        # Add some noise to simulate real speech
        rng = np.random.default_rng(seed=42)
        noise = 0.1 * rng.normal(0, 1, len(t))
        audio += noise

        # Add background noise
        background_noise = 0.05 * rng.normal(0, 1, len(t))
        audio += background_noise

        # Normalize
        audio = audio / np.max(np.abs(audio))

        return audio.astype(np.float32)

    def test_parameter_combination(self, params: Dict, test_audio: np.ndarray,
                                 sample_rate: int = 16000) -> Dict:
        """Test a specific parameter combination"""

        # Create preprocessor with test parameters
        test_config = self.config.copy()
        test_config['audio_preprocessing'].update(params)

        # Create temporary preprocessor with modified config
        import tempfile
        import yaml

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_config_path = f.name

        try:
            preprocessor = UzbekAudioPreprocessor(temp_config_path)

            # Apply preprocessing
            processed_audio = preprocessor.preprocess_audio(test_audio, sample_rate)

            # Calculate quality metrics
            metrics = self._calculate_audio_quality_metrics(test_audio, processed_audio, sample_rate)

            # Test recognition with Vosk
            recognition_result = self._test_recognition(processed_audio, sample_rate)

            result = {
                'parameters': params,
                'metrics': metrics,
                'recognition': recognition_result
            }

            return result

        finally:
            os.unlink(temp_config_path)

    def _calculate_audio_quality_metrics(self, original: np.ndarray, processed: np.ndarray,
                                       sample_rate: int) -> Dict:
        """Calculate audio quality metrics"""

        metrics = {}

        # Signal-to-noise ratio improvement
        def calculate_snr(audio):
            signal_power = np.mean(audio ** 2)
            noise_power = np.var(audio - np.mean(audio))
            return 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 0

        original_snr = calculate_snr(original)
        processed_snr = calculate_snr(processed)
        metrics['snr_improvement'] = processed_snr - original_snr

        # Dynamic range
        original_dynamic_range = np.max(original) - np.min(original)
        processed_dynamic_range = np.max(processed) - np.min(processed)
        metrics['dynamic_range_preservation'] = processed_dynamic_range / original_dynamic_range if original_dynamic_range > 0 else 0

        # Frequency content analysis
        from scipy import signal

        # Compute power spectral density
        freqs_orig, psd_orig = signal.welch(original, fs=sample_rate, nperseg=1024)
        freqs_proc, psd_proc = signal.welch(processed, fs=sample_rate, nperseg=1024)

        # Speech frequency band preservation (300-3400 Hz)
        speech_band_orig = np.sum(psd_orig[(freqs_orig >= 300) & (freqs_orig <= 3400)])
        speech_band_proc = np.sum(psd_proc[(freqs_proc >= 300) & (freqs_proc <= 3400)])
        total_power_proc = np.sum(psd_proc)

        metrics['speech_band_ratio'] = speech_band_proc / total_power_proc if total_power_proc > 0 else 0
        metrics['speech_band_preservation'] = speech_band_proc / speech_band_orig if speech_band_orig > 0 else 0

        # Crest factor (peak-to-RMS ratio)
        rms_orig = np.sqrt(np.mean(original ** 2))
        rms_proc = np.sqrt(np.mean(processed ** 2))
        crest_orig = np.max(np.abs(original)) / rms_orig if rms_orig > 0 else 0
        crest_proc = np.max(np.abs(processed)) / rms_proc if rms_proc > 0 else 0
        metrics['crest_factor_change'] = crest_proc - crest_orig

        return metrics

    def _test_recognition(self, audio: np.ndarray, sample_rate: int) -> Dict:
        """Test recognition quality with processed audio"""

        model_path = self.config.get('general', {}).get('model_path', 'models/uzbek/vosk-model-small-uz-0.22')

        if not os.path.exists(model_path):
            return {'error': 'Model not found'}

        # Load model (reuse if already loaded)
        if not hasattr(self, '_model'):
            self._model = Model(model_path)
            self._recognizer = KaldiRecognizer(self._model, sample_rate)

        # Convert to bytes
        audio_bytes = (audio * 32767).astype(np.int16).tobytes()

        # Recognize
        self._recognizer.AcceptWaveform(audio_bytes)
        result = json.loads(self._recognizer.FinalResult())

        recognized_text = result.get('text', '').strip()

        return {
            'recognized_text': recognized_text,
            'confidence': len(recognized_text) > 0  # Simple confidence measure
        }

    def run_parameter_sweep(self, test_audio: np.ndarray, sample_rate: int = 16000) -> List[Dict]:
        """Run parameter sweep to find optimal settings"""

        print("🔧 Running parameter sweep for Uzbek audio preprocessing...")

        results = []

        # Test different combinations
        test_cases = [
            # Baseline
            {
                'noise_reduction': True,
                'normalization': True,
                'frequency_range': [80, 8000],
                'speech_threshold': 0.01,
                'compression_ratio': 4.0,
                'compression_threshold': 0.6
            },
            # High quality settings
            {
                'noise_reduction': True,
                'normalization': True,
                'frequency_range': [50, 8000],
                'speech_threshold': 0.005,
                'compression_ratio': 2.0,
                'compression_threshold': 0.3
            },
            # Telephone quality
            {
                'noise_reduction': True,
                'normalization': True,
                'frequency_range': [100, 4000],
                'speech_threshold': 0.02,
                'compression_ratio': 6.0,
                'compression_threshold': 0.5
            },
            # Minimal processing
            {
                'noise_reduction': False,
                'normalization': True,
                'frequency_range': [80, 8000],
                'speech_threshold': 0.01,
                'compression_ratio': 1.0,
                'compression_threshold': 1.0
            }
        ]

        for i, params in enumerate(test_cases):
            print(f"Testing parameter set {i+1}/{len(test_cases)}: {params}")
            result = self.test_parameter_combination(params, test_audio, sample_rate)
            results.append(result)

        return results

    def analyze_results(self, results: List[Dict]) -> Dict:
        """Analyze parameter sweep results"""

        if not results:
            return {}

        # Find best parameters based on multiple criteria
        best_snr = max(results, key=lambda x: x['metrics']['snr_improvement'])
        best_speech_preservation = max(results, key=lambda x: x['metrics']['speech_band_preservation'])
        best_recognition = max(results, key=lambda x: len(x['recognition'].get('recognized_text', '')))

        # Calculate average scores
        avg_metrics = {}
        for key in results[0]['metrics'].keys():
            avg_metrics[key] = sum(r['metrics'][key] for r in results) / len(results)

        analysis = {
            'best_parameters': {
                'snr_improvement': best_snr['parameters'],
                'speech_preservation': best_speech_preservation['parameters'],
                'recognition_quality': best_recognition['parameters']
            },
            'average_metrics': avg_metrics,
            'all_results': results,
            'recommendations': self._generate_recommendations(results)
        }

        return analysis

    def _generate_recommendations(self, results: List[Dict]) -> Dict:
        """Generate parameter recommendations"""

        # Simple recommendation logic
        recommendations = {
            'optimal_frequency_range': [80, 8000],  # Default
            'recommended_noise_reduction': True,
            'recommended_normalization': True,
            'recommended_compression': {'ratio': 4.0, 'threshold': 0.6}
        }

        # Analyze frequency range performance
        freq_performance = {}
        for result in results:
            freq_range = tuple(result['parameters']['frequency_range'])
            speech_preservation = result['metrics']['speech_band_preservation']
            freq_performance[freq_range] = speech_preservation

        if freq_performance:
            best_freq = max(freq_performance.items(), key=lambda x: x[1])
            recommendations['optimal_frequency_range'] = list(best_freq[0])

        return recommendations

    def print_analysis(self, analysis: Dict):
        """Print parameter tuning analysis"""

        if not analysis:
            print("❌ No analysis results to display")
            return

        print("\n" + "="*60)
        print("🔧 UZBEK AUDIO PREPROCESSING TUNING RESULTS")
        print("="*60)

        print("\n📊 RECOMMENDED PARAMETERS:")
        recs = analysis.get('recommendations', {})
        print(f"   Frequency Range: {recs.get('optimal_frequency_range', [80, 8000])} Hz")
        print(f"   Noise Reduction: {recs.get('recommended_noise_reduction', True)}")
        print(f"   Normalization: {recs.get('recommended_normalization', True)}")
        comp = recs.get('recommended_compression', {})
        print(f"   Compression: Ratio {comp.get('ratio', 4.0)}, Threshold {comp.get('threshold', 0.6)}")

        print("\n📈 AVERAGE METRICS:")
        avg = analysis.get('average_metrics', {})
        for metric, value in avg.items():
            print(f"   {metric.replace('_', ' ').title()}: {value:.3f}")
        print("\n🏆 BEST PARAMETER SETS:")
        best = analysis.get('best_parameters', {})
        for criterion, params in best.items():
            print(f"   {criterion.replace('_', ' ').title()}: {params}")

def run_preprocessing_tuning():
    """Run the preprocessing tuning process"""

    tuner = UzbekPreprocessingTuner()

    print("🎛️  UZBEK AUDIO PREPROCESSING PARAMETER TUNING")
    print("=" * 50)

    # Generate test audio
    print("Generating test audio...")
    test_audio = tuner.generate_test_audio(duration=3.0)

    # Run parameter sweep
    results = tuner.run_parameter_sweep(test_audio)

    # Analyze results
    analysis = tuner.analyze_results(results)

    # Print analysis
    tuner.print_analysis(analysis)

    print("\n✅ Preprocessing tuning completed!")

    return analysis

if __name__ == "__main__":
    run_preprocessing_tuning()
