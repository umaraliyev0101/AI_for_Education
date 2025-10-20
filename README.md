# Uzbek Speech-to-Text System

AI-powered speech recognition system for the Uzbek language using OpenAI Whisper.

## Features

- **High-Accuracy STT**: Uses OpenAI Whisper for superior Uzbek speech recognition
- **Real-time Processing**: Optimized for live transcription from microphone
- **Live Transcription**: Continuous speech-to-text from microphone input
- **Accuracy Testing**: Comprehensive WER/CER metrics and reporting
- **Text Post-processing**: Uzbek-specific text normalization and cleaning
- **Audio Preprocessing**: Optimized audio processing for Uzbek phonetic characteristics

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from uzbek_whisper_pipeline import create_uzbek_whisper_stt

# Create STT instance
stt = create_uzbek_whisper_stt()

# Transcribe audio file
result = stt.transcribe_file("audio.wav")
print(result["text"])
```

### Command Line Usage

```bash
# Run accuracy tests
python main.py test

# Transcribe audio file
python main.py transcribe audio.wav

# Live transcription from microphone (real-time)
python main.py live

# Interactive mode
python main.py interactive
```

## Project Structure

```
├── main.py                          # Main entry point
├── uzbek_whisper_pipeline.py        # Core Whisper STT pipeline
├── uzbek_accuracy_testing_framework.py  # Testing and metrics
├── uzbek_text_postprocessor.py      # Text post-processing
├── uzbek_audio_preprocessor.py      # Audio preprocessing
├── uzbek_pronunciation_dictionary.py # Pronunciation guide
├── requirements.txt                 # Python dependencies
└── docs/                           # Documentation
```

## Performance

- **Word Error Rate (WER)**: ~5%
- **Character Error Rate (CER)**: ~2%
- **Processing**: Real-time capable on modern hardware

## API Reference

### UzbekWhisperSTT

```python
class UzbekWhisperSTT:
    def transcribe_audio(audio_data, sample_rate=16000) -> Dict
    def transcribe_file(file_path) -> Dict
    def get_model_info() -> Dict
```

### UzbekAccuracyTester

```python
class UzbekAccuracyTester:
    def test_text_accuracy(test_cases, session_name=None) -> UzbekAccuracyReport
    def save_report(report, output_file=None)
    def print_summary(report)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python main.py test`
5. Submit a pull request

## License

MIT License - see LICENSE file for details
