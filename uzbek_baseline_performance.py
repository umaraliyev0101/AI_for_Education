#!/usr/bin/env python3
"""
Uzbek STT Baseline Performance Documentation
Comprehensive documentation of baseline performance metrics and tracking system
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

class UzbekPerformanceTracker:
    """
    Track and document baseline performance metrics for Uzbek STT
    """

    def __init__(self, reports_dir: str = "accuracy_reports"):
        """Initialize the performance tracker"""

        self.reports_dir = reports_dir
        os.makedirs(reports_dir, exist_ok=True)

        # Performance history
        self.performance_history: List[Dict[str, Any]] = []
        self.baseline_metrics: Dict[str, Any] = {}

        # Load existing performance data
        self.load_performance_history()

    def load_performance_history(self):
        """Load existing performance reports"""

        history_file = os.path.join(self.reports_dir, "performance_history.json")

        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.performance_history = data.get("history", [])
                    self.baseline_metrics = data.get("baseline", {})
                print(f"📊 Loaded {len(self.performance_history)} performance records")
            except Exception as e:
                print(f"❌ Error loading performance history: {e}")

    def save_performance_history(self):
        """Save performance history to file"""

        history_file = os.path.join(self.reports_dir, "performance_history.json")

        data = {
            "metadata": {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "description": "Uzbek STT Performance Tracking History"
            },
            "baseline": self.baseline_metrics,
            "history": self.performance_history
        }

        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"💾 Performance history saved to {history_file}")

    def add_performance_record(self, report_data: Dict[str, Any]):
        """Add a new performance record"""

        # Extract key metrics
        record = {
            "timestamp": report_data.get("timestamp", datetime.now().isoformat()),
            "session_id": report_data.get("test_session_id", "unknown"),
            "total_samples": report_data.get("total_samples", 0),
            "overall_wer": report_data.get("overall_wer", 0.0),
            "overall_cer": report_data.get("overall_cer", 0.0),
            "average_confidence": report_data.get("average_confidence", 0.0),
            "average_processing_time": report_data.get("average_processing_time", 0.0),
            "speaker_performance": report_data.get("results_by_speaker", {}),
            "difficulty_performance": report_data.get("results_by_difficulty", {}),
            "category_performance": report_data.get("results_by_category", {}),
            "recommendations": report_data.get("recommendations", [])
        }

        self.performance_history.append(record)

        # Update baseline if this is the first record or better performance
        if not self.baseline_metrics or record["overall_wer"] < self.baseline_metrics.get("overall_wer", 1.0):
            self.baseline_metrics = record.copy()
            self.baseline_metrics["baseline_date"] = record["timestamp"]
            print("🏆 New baseline performance established!")

        self.save_performance_history()

    def generate_baseline_report(self) -> str:
        """Generate comprehensive baseline performance report"""

        if not self.baseline_metrics:
            return "No baseline performance data available."

        report = f"""
UZBEK SPEECH-TO-TEXT BASELINE PERFORMANCE REPORT
{'='*55}

📊 BASELINE METRICS (Established: {self.baseline_metrics.get('baseline_date', 'Unknown')})
{'-'*55}
• Word Error Rate (WER): {self.baseline_metrics.get('overall_wer', 0):.2%}
• Character Error Rate (CER): {self.baseline_metrics.get('overall_cer', 0):.2%}
• Average Confidence: {self.baseline_metrics.get('average_confidence', 0):.2%}
• Average Processing Time: {self.baseline_metrics.get('average_processing_time', 0):.3f}s
• Test Samples: {self.baseline_metrics.get('total_samples', 0)}
• Session ID: {self.baseline_metrics.get('session_id', 'Unknown')}

🎯 PERFORMANCE BY SPEAKER PROFILE
{'-'*35}
"""

        speaker_perf = self.baseline_metrics.get('speaker_performance', {})
        if speaker_perf:
            for speaker, metrics in speaker_perf.items():
                report += f"• {speaker}:\n"
                report += f"  - WER: {metrics.get('wer', 0):.2%}\n"
                report += f"  - CER: {metrics.get('cer', 0):.2%}\n"
                report += f"  - Samples: {metrics.get('count', 0)}\n"
        else:
            report += "No speaker-specific data available.\n"

        report += f"""
📈 PERFORMANCE TRENDS
{'-'*20}
Total Performance Records: {len(self.performance_history)}

"""

        if len(self.performance_history) > 1:
            # Calculate trends
            wer_values = [r['overall_wer'] for r in self.performance_history]
            cer_values = [r['overall_cer'] for r in self.performance_history]

            wer_trend = "improving" if wer_values[-1] < wer_values[0] else "declining"
            cer_trend = "improving" if cer_values[-1] < cer_values[0] else "declining"

            report += f"• WER Trend: {wer_trend} ({wer_values[0]:.2%} → {wer_values[-1]:.2%})\n"
            report += f"• CER Trend: {cer_trend} ({cer_values[0]:.2%} → {cer_values[-1]:.2%})\n"
        else:
            report += "Insufficient data for trend analysis.\n"

        report += f"""
🔧 SYSTEM SPECIFICATIONS
{'-'*23}
• Model: Vosk Uzbek Small Model (vosk-model-small-uz-0.22)
• Sample Rate: 16kHz
• Audio Format: WAV (16-bit)
• Language: Uzbek (Latin script)
• Phoneme Coverage: Complete Uzbek phoneme inventory
• Test Dataset: 75 synthetic samples across 5 speaker profiles

💡 BASELINE RECOMMENDATIONS
{'-'*26}
"""

        recommendations = self.baseline_metrics.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
        else:
            report += "No specific recommendations available.\n"

        report += f"""
📋 PERFORMANCE TARGETS
{'-'*21}
• Target WER: < 15% (Current: {self.baseline_metrics.get('overall_wer', 0):.2%})
• Target CER: < 5% (Current: {self.baseline_metrics.get('overall_cer', 0):.2%})
• Target Confidence: > 80% (Current: {self.baseline_metrics.get('average_confidence', 0):.2%})
• Target Processing Time: < 0.1s (Current: {self.baseline_metrics.get('average_processing_time', 0):.3f}s)

📝 NOTES
{'-'*7}
• Baseline established with synthetic test data
• Real-world performance may vary with authentic audio samples
• Performance tracking will continue with future test sessions
• Regular re-evaluation recommended as model improvements are made

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return report

    def generate_performance_comparison(self, output_file: str = None) -> Optional[str]:
        """Generate performance comparison across all recorded sessions"""

        if len(self.performance_history) < 2:
            return "Insufficient data for performance comparison (need at least 2 sessions)."

        # Create DataFrame for analysis
        df_data = []
        for record in self.performance_history:
            df_data.append({
                'session': record['session_id'],
                'timestamp': record['timestamp'],
                'wer': record['overall_wer'],
                'cer': record['overall_cer'],
                'confidence': record['average_confidence'],
                'processing_time': record['average_processing_time'],
                'samples': record['total_samples']
            })

        df = pd.DataFrame(df_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        if VISUALIZATION_AVAILABLE:
            # Create comparison plots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Uzbek STT Performance Comparison Across Sessions', fontsize=16)

            # WER over time
            axes[0, 0].plot(df['timestamp'], df['wer'], marker='o', linewidth=2, markersize=6)
            axes[0, 0].set_title('Word Error Rate (WER) Trend')
            axes[0, 0].set_ylabel('WER')
            axes[0, 0].tick_params(axis='x', rotation=45)

            # CER over time
            axes[0, 1].plot(df['timestamp'], df['cer'], marker='s', linewidth=2, markersize=6, color='orange')
            axes[0, 1].set_title('Character Error Rate (CER) Trend')
            axes[0, 1].set_ylabel('CER')
            axes[0, 1].tick_params(axis='x', rotation=45)

            # Confidence over time
            axes[1, 0].plot(df['timestamp'], df['confidence'], marker='^', linewidth=2, markersize=6, color='green')
            axes[1, 0].set_title('Average Confidence Trend')
            axes[1, 0].set_ylabel('Confidence')
            axes[1, 0].tick_params(axis='x', rotation=45)

            # Processing time over time
            axes[1, 1].plot(df['timestamp'], df['processing_time'], marker='d', linewidth=2, markersize=6, color='red')
            axes[1, 1].set_title('Processing Time Trend')
            axes[1, 1].set_ylabel('Time (seconds)')
            axes[1, 1].tick_params(axis='x', rotation=45)

            plt.tight_layout()

            if output_file is None:
                output_file = os.path.join(self.reports_dir, "performance_comparison.png")

            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"📊 Performance comparison chart saved to {output_file}")

        # Generate text comparison
        comparison = f"""
UZBEK STT PERFORMANCE COMPARISON REPORT
{'='*40}

Sessions Analyzed: {len(df)}
Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}

📊 METRIC SUMMARY
{'-'*15}
"""

        for metric in ['wer', 'cer', 'confidence', 'processing_time']:
            values = df[metric]
            comparison += f"• {metric.upper()}: {values.mean():.3f} ± {values.std():.3f} "
            comparison += f"(Range: {values.min():.3f} - {values.max():.3f})\n"

        comparison += f"""
🏆 BEST PERFORMING SESSION
{'-'*25}
Session: {df.loc[df['wer'].idxmin(), 'session']}
WER: {df['wer'].min():.2%}
CER: {df.loc[df['wer'].idxmin(), 'cer']:.2%}
Confidence: {df.loc[df['wer'].idxmin(), 'confidence']:.2%}

📈 PERFORMANCE IMPROVEMENT
{'-'*24}
"""

        if len(df) > 1:
            wer_improvement = df['wer'].iloc[0] - df['wer'].iloc[-1]
            cer_improvement = df['cer'].iloc[0] - df['cer'].iloc[-1]

            comparison += f"WER Improvement: {wer_improvement:.2%}\n"
            comparison += f"CER Improvement: {cer_improvement:.2%}\n"

        return comparison

    def export_performance_data(self, format: str = "csv") -> str:
        """Export performance data in various formats"""

        if not self.performance_history:
            return "No performance data available for export."

        # Create DataFrame
        records = []
        for record in self.performance_history:
            base_record = {
                'timestamp': record['timestamp'],
                'session_id': record['session_id'],
                'total_samples': record['total_samples'],
                'overall_wer': record['overall_wer'],
                'overall_cer': record['overall_cer'],
                'average_confidence': record['average_confidence'],
                'average_processing_time': record['average_processing_time']
            }

            # Add speaker performance as separate columns
            for speaker, metrics in record.get('speaker_performance', {}).items():
                base_record[f'{speaker}_wer'] = metrics.get('wer', 0)
                base_record[f'{speaker}_cer'] = metrics.get('cer', 0)
                base_record[f'{speaker}_count'] = metrics.get('count', 0)

            records.append(base_record)

        df = pd.DataFrame(records)

        if format.lower() == "csv":
            output_file = os.path.join(self.reports_dir, "performance_data.csv")
            df.to_csv(output_file, index=False)
        elif format.lower() == "excel":
            output_file = os.path.join(self.reports_dir, "performance_data.xlsx")
            df.to_excel(output_file, index=False)
        else:
            return f"Unsupported format: {format}"

        print(f"📊 Performance data exported to {output_file}")
        return f"Data exported successfully to {output_file}"

def create_baseline_documentation():
    """Create comprehensive baseline performance documentation"""

    print("📊 UZBEK STT BASELINE PERFORMANCE DOCUMENTATION")
    print("=" * 50)

    # Initialize tracker
    tracker = UzbekPerformanceTracker()

    # Load latest accuracy report if available
    latest_report_file = "uzbek_accuracy_report_comprehensive_test.json"
    if os.path.exists(latest_report_file):
        print("Loading latest accuracy report...")
        with open(latest_report_file, 'r', encoding='utf-8') as f:
            report_data = json.load(f)

        # Add to performance history
        tracker.add_performance_record(report_data)
    else:
        print("No accuracy report found. Using existing performance history.")

    # Generate baseline report
    baseline_report = tracker.generate_baseline_report()
    print(baseline_report)

    # Save baseline report
    baseline_file = os.path.join(tracker.reports_dir, "baseline_performance_report.txt")
    with open(baseline_file, 'w', encoding='utf-8') as f:
        f.write(baseline_report)
    print(f"💾 Baseline report saved to {baseline_file}")

    # Generate performance comparison if multiple records exist
    if len(tracker.performance_history) > 1:
        comparison = tracker.generate_performance_comparison()
        if comparison:
            print("\n" + "="*50)
            print("PERFORMANCE COMPARISON")
            print("="*50)
            print(comparison)

            comparison_file = os.path.join(tracker.reports_dir, "performance_comparison.txt")
            with open(comparison_file, 'w', encoding='utf-8') as f:
                f.write(comparison)
            print(f"💾 Comparison report saved to {comparison_file}")

    # Export performance data
    tracker.export_performance_data("csv")

    print("✅ Baseline performance documentation completed!")

    return tracker

if __name__ == "__main__":
    create_baseline_documentation()
