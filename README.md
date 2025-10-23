# AI in Education - Uzbek STT & Attendance System

Complete AI-powered system for education featuring speech-to-text and automatic face recognition attendance for Uzbek schools.

## 🎯 Features

### Speech-to-Text System
- **High-Accuracy STT**: XLS-R model (15.07% WER) for Uzbek speech recognition
- **Multiple Models**: XLS-R (primary), Whisper (backup), HF Pipeline (general)
- **Live Transcription**: Real-time speech-to-text from microphone
- **Text-to-Speech**: Natural Uzbek speech synthesis for educational content
- **Interactive Teaching**: AI-powered lessons combining STT and TTS
- **Accuracy Testing**: Comprehensive WER/CER metrics and reporting

### Face Recognition Attendance
- **Automatic Attendance**: FaceNet-based recognition at entrance camera
- **Student Enrollment**: Easy webcam or image-based enrollment
- **SQLite Database**: Local storage for students and attendance records
- **Real-time Processing**: ~100ms recognition per frame
- **Attendance Reports**: Daily, weekly, monthly statistics by class
- **Privacy-Focused**: Local processing, no cloud dependency

## 📁 Project Structure

```
AI_in_Education/
├── main.py                    # Main CLI entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── stt_pipelines/            # Speech-to-Text modules
│   ├── uzbek_xlsr_pipeline.py      # XLS-R (primary, 15% WER)
│   ├── uzbek_whisper_pipeline.py   # Whisper (backup, 30% WER)
│   ├── uzbek_hf_pipeline.py        # HuggingFace ASR
│   └── uzbek_tts_pipeline.py       # Text-to-Speech
│
├── face_recognition/         # Attendance system
│   ├── face_recognition_db.py      # SQLite database
│   ├── face_enrollment.py          # Student enrollment
│   └── face_attendance.py          # Real-time attendance
│
├── utils/                    # Utilities
│   ├── uzbek_text_postprocessor.py
│   └── uzbek_accuracy_testing_framework.py
│
├── docs/                     # Documentation
│   ├── FACE_RECOGNITION_README.md
│   ├── COMPLETE_SYSTEM_DOCS.md
│   └── PROJECT_STRUCTURE.md
│
└── data/                     # Data files & reports
    ├── students.db           # SQLite database (runtime)
    └── *.json                # Accuracy reports
```

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/umaraliyev0101/AI_for_Education.git
cd AI_in_Education

# Install dependencies
pip install -r requirements.txt
```

### STT Usage

```python
from stt_pipelines.uzbek_xlsr_pipeline import create_uzbek_xlsr_stt

# Create STT instance
stt = create_uzbek_xlsr_stt()

# Transcribe audio file
result = stt.transcribe_file("audio.wav")
print(result["text"])
```

### Command Line Usage

**STT Commands:**
```bash
# Run accuracy tests
python main.py test

# Transcribe audio file
python main.py transcribe audio.wav xlsr

# Live transcription from microphone
python main.py live

# Text-to-speech
python main.py speak "Salom, bolalar!"

# Interactive teaching mode
python main.py teach
```

**Attendance Commands:**
```bash
# Enroll new student
python main.py enroll

# Start entrance camera
python main.py attendance

# View attendance report
python main.py report

# List all students
python main.py students
```

### Face Recognition Setup

```python
from face_recognition.face_enrollment import FaceEnrollmentSystem
from face_recognition.face_recognition_db import FaceRecognitionDB

# Enroll student
enrollment = FaceEnrollmentSystem()
db = FaceRecognitionDB()

student_id, name, class_name, encoding = enrollment.enroll_student_interactive()
db.add_student(student_id, name, class_name, encoding)
```

## 📊 Model Performance

| Model | WER | CER | Language | Use Case |
|-------|-----|-----|----------|----------|
| XLS-R | 15.07% | 3.08% | Uzbek | Primary STT |
| Whisper | ~30-35% | ~8-10% | Uzbek | Backup STT |
| FaceNet | 99.3% | - | - | Face Recognition |

## 📚 Documentation

- **[Complete System Docs](docs/COMPLETE_SYSTEM_DOCS.md)**: Full technical documentation
- **[Face Recognition Guide](docs/FACE_RECOGNITION_README.md)**: Attendance system usage
- **[Project Structure](docs/PROJECT_STRUCTURE.md)**: Detailed file organization

## 🔧 Requirements

- Python 3.8+
- PyTorch 2.0+
- Transformers 4.30+
- OpenCV 4.8+
- facenet-pytorch
- SQLite3 (included with Python)

## 🎓 Use Cases

1. **Classroom Attendance**: Automatic student attendance via entrance camera
2. **Uzbek Language Learning**: Interactive STT/TTS lessons
3. **Speech Recognition**: Transcribe Uzbek audio files
4. **Attendance Analytics**: Track student attendance patterns
5. **Educational Research**: Measure STT accuracy for Uzbek

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Umar Aliyev** - [GitHub](https://github.com/umaraliyev0101)

## 🙏 Acknowledgments

- XLS-R model by Meta AI
- Whisper model by OpenAI
- FaceNet by Google
- Uzbek speech data contributors
python main.py interactive
```

## Project Structure

```
├── main.py                          # Main entry point
├── uzbek_whisper_pipeline.py        # Core Whisper STT pipeline
├── uzbek_tts_pipeline.py           # Text-to-speech pipeline
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

### UzbekTTSPipeline

```python
class UzbekTTSPipeline:
    def speak_text(text: str, save_to_file=None) -> bool
    def generate_speech(text: str) -> bytes
    def get_available_voices() -> Dict[str, str]
    def test_tts() -> bool
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
