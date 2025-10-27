#!/usr/bin/env python3
"""
Uzbek Whisper STT System
========================

Complete Uzbek speech-to-text system using OpenAI Whisper.
"""

from stt_pipelines.uzbek_whisper_pipeline import UzbekWhisperSTT, create_uzbek_whisper_stt
from stt_pipelines.uzbek_xlsr_pipeline import UzbekXLSRSTT, create_uzbek_xlsr_stt
from stt_pipelines.uzbek_hf_pipeline import UzbekHFSTTPipeline
from utils.uzbek_accuracy_testing_framework import UzbekAccuracyTester, run_xlsr_accuracy_test
from stt_pipelines.uzbek_tts_pipeline import UzbekTTSPipeline, create_uzbek_tts, UZBEK_EDUCATIONAL_PHRASES
from face_recognition.face_recognition_db import FaceRecognitionDB
from face_recognition.face_enrollment import FaceEnrollmentSystem
from face_recognition.face_attendance import FaceRecognitionAttendance
from utils.uzbek_llm_qa_service import create_uzbek_llm_qa_service
import sys
import threading
import queue
import time
import numpy as np
import os

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio not available. Live transcription will not work.")

# def create_uzbek_hf_stt(model_name="sarahai/uzbek-stt-3", device="cpu"):
#     """Create Uzbek STT pipeline using Hugging Face model"""
#     return UzbekHFSTTPipeline(model_name=model_name, device=device)

def create_uzbek_nemo_stt(model_name="lucio/xls-r-uzbek-cv8"):
    """Create Uzbek STT pipeline using XLS-R model (formerly NeMo)"""
    return create_uzbek_xlsr_stt(model_name)

def main():
    """Main entry point for the Uzbek STT system"""

    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [args...]")
        print("\nSTT Commands:")
        print("  test          - Run accuracy testing")
        print("  transcribe    - Transcribe audio file [model: whisper/xlsr/hf]")
        print("  live          - Live transcription from microphone")
        print("  speak         - Convert text to speech")
        print("  teach         - Interactive teaching mode")
        print("\nLLM/Q&A Commands:")
        print("  qa-test       - Test LLM QA system")
        print("  qa-prepare    - Prepare lesson materials for Q&A [lesson_dir]")
        print("  qa-ask        - Ask questions interactively [lesson_id]")
        print("  qa-voice      - Ask questions via voice (STT + LLM) [lesson_id]")
        print("\nAttendance Commands:")
        print("  enroll        - Enroll new student with face recognition")
        print("  attendance    - Start entrance camera for attendance")
        print("  report        - View attendance report [date]")
        print("  students      - List all enrolled students")
        return

    command = sys.argv[1]

    if command == "test":
        print("🧪 Running Uzbek XLS-R Accuracy Tests")
        run_xlsr_accuracy_test()

    elif command == "transcribe":
        if len(sys.argv) < 3:
            print("Usage: python main.py transcribe <audio_file.wav> [model]")
            print("Models: whisper (default), nemo, hf")
            return

        audio_file = sys.argv[2]
        model = sys.argv[3] if len(sys.argv) > 3 else "xlsr"

        print(f"🎙️ Transcribing: {audio_file} using {model} model")

        if model == "nemo" or model == "xlsr":
            stt = create_uzbek_xlsr_stt()
        elif model == "hf":
            stt = create_uzbek_hf_stt()
        else:  # default to xlsr
            stt = create_uzbek_xlsr_stt()

        result = stt.transcribe_file(audio_file)

        print("📝 Transcription Result:")
        print(f"Text: {result['text']}")
        print(f"Model: {model}")
        if 'confidence' in result:
            print(".3f")

    elif command == "live":
        if not PYAUDIO_AVAILABLE:
            print("❌ PyAudio is required for live transcription.")
            print("Install it with: pip install pyaudio")
            return

        model = sys.argv[2] if len(sys.argv) > 2 else "nemo"  # Default to nemo for live as it's faster

        print(f"🎙️ Uzbek STT - Live Transcription Mode using {model} model")
        print("Press Ctrl+C to stop")

        try:
            live_transcription(model)
        except KeyboardInterrupt:
            print("\n👋 Live transcription stopped!")

    elif command == "speak":
        # Lazy import TTS to avoid pygame warning when not using TTS
        try:
            from stt_pipelines.uzbek_tts_pipeline import create_uzbek_tts, UZBEK_EDUCATIONAL_PHRASES
            text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else UZBEK_EDUCATIONAL_PHRASES["greeting"]

            print("🗣️ Uzbek TTS - Text-to-Speech Mode")
            print(f"Text: '{text}'")

            tts = create_uzbek_tts()
            success = tts.speak_text(text)
            if success:
                print("✅ Speech completed!")
            else:
                print("❌ Speech failed!")
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            import traceback
            traceback.print_exc()

    elif command == "teach":
        print("🎓 Uzbek AI Teacher - Interactive Teaching Mode")
        print("Type 'quit' to exit, 'help' for commands")

        model = sys.argv[2] if len(sys.argv) > 2 else "hf"  # Default to hf for teaching

        try:
            # Lazy import TTS for teaching mode
            from stt_pipelines.uzbek_tts_pipeline import create_uzbek_tts
            interactive_teaching(model)
        except KeyboardInterrupt:
            print("\n👋 Teaching session ended!")

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

    elif command == "qa-test":
        print("🤖 Testing Uzbek LLM QA System")
        try:
            from test_qa_system import run_full_test
            success = run_full_test()
            if success:
                print("✅ LLM QA System test passed!")
            else:
                print("❌ LLM QA System test failed!")
        except Exception as e:
            print(f"❌ Test failed: {e}")

    elif command == "qa-prepare":
        if len(sys.argv) < 3:
            print("Usage: python main.py qa-prepare <lesson_directory>")
            print("Example: python main.py qa-prepare ./lesson_materials")
            return

        lesson_dir = sys.argv[2]
        lesson_id = os.path.basename(lesson_dir) or "prepared_lesson"

        print(f"📚 Preparing lesson materials from: {lesson_dir}")
        print(f"📝 Lesson ID: {lesson_id}")

        try:
            # Get all supported files
            file_paths = []
            if os.path.exists(lesson_dir):
                for root, dirs, files in os.walk(lesson_dir):
                    for file in files:
                        if file.endswith(('.pdf', '.pptx', '.docx', '.txt', '.md')):
                            file_paths.append(os.path.join(root, file))

            if not file_paths:
                print(f"❌ No supported files found in {lesson_dir}")
                print("Supported formats: .pdf, .pptx, .docx, .txt, .md")
                return

            print(f"📄 Found {len(file_paths)} files to process")

            # Initialize LLM service
            llm_service = create_uzbek_llm_qa_service()

            # Prepare materials
            success = llm_service.prepare_lesson_materials(file_paths, lesson_id)

            if success:
                stats = llm_service.get_lesson_statistics(lesson_id)
                print("✅ Lesson materials prepared successfully!")
                print(f"📊 Documents processed: {stats.get('num_documents', 'unknown')}")
                print(f"🤖 LLM Model: {stats.get('llm_model', 'unknown')}")
                print(f"🔍 Embedding Model: {stats.get('embedding_model', 'unknown')}")
                
                # Save vector store to disk for persistence
                vector_store_path = f"vector_stores/{lesson_id}"
                os.makedirs(os.path.dirname(vector_store_path), exist_ok=True)
                llm_service.save_vector_store(lesson_id, vector_store_path)
                print(f"💾 Vector store saved to: {vector_store_path}")
            else:
                print("❌ Failed to prepare lesson materials")

        except Exception as e:
            print(f"❌ Preparation failed: {e}")
            import traceback
            traceback.print_exc()

    elif command == "qa-ask":
        lesson_id = sys.argv[2] if len(sys.argv) > 2 else "prepared_lesson"

        print(f"[BOT] Uzbek LLM Q&A - Interactive Mode")
        print(f"Lesson: {lesson_id}")
        print("Type 'quit' to exit, 'help' for commands")

        try:
            llm_service = create_uzbek_llm_qa_service()

            # Check if lesson is prepared
            stats = llm_service.get_lesson_statistics(lesson_id)
            if "error" in stats:
                print(f"WARNING: Lesson '{lesson_id}' not found. Run 'qa-prepare' first.")
                return

            print(f"OK: Lesson ready with {stats.get('num_documents', 'unknown')} documents")

            while True:
                try:
                    question = input("\nYour question (or 'quit'): ").strip()

                    if question.lower() == 'quit':
                        break
                    elif question.lower() == 'help':
                        print("Commands:")
                        print("  quit - Exit Q&A mode")
                        print("  help - Show this help")
                        print("  stats - Show lesson statistics")
                        continue
                    elif question.lower() == 'stats':
                        stats = llm_service.get_lesson_statistics(lesson_id)
                        print(f"📊 Lesson Statistics:")
                        for key, value in stats.items():
                            print(f"   {key}: {value}")
                        continue

                    if not question:
                        continue

                    print("Thinking...", end="", flush=True)

                    # Get answer
                    answer, found, docs = llm_service.answer_question(question, lesson_id, use_llm=True)

                    print(f"\r{' ' * 50}\r", end="")  # Clear thinking message

                    if found:
                        print(f"Answer: {answer}")
                        print(f"Retrieved {len(docs)} relevant documents")
                    else:
                        print(f"ERROR: {answer}")

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"ERROR: {e}")

        except Exception as e:
            print(f"Failed to start Q&A mode: {e}")

        print("\nQ&A session ended!")

    elif command == "qa-voice":
        if not PYAUDIO_AVAILABLE:
            print("❌ PyAudio is required for voice Q&A.")
            print("Install it with: pip install pyaudio")
            return

        lesson_id = sys.argv[2] if len(sys.argv) > 2 else "prepared_lesson"

        print(f"🎤 Uzbek Voice Q&A - STT + LLM Mode")
        print(f"📚 Lesson: {lesson_id}")
        print("💡 Speak your question, then wait for the answer")
        print("   Press Ctrl+C to stop")

        try:
            # Initialize services
            llm_service = create_uzbek_llm_qa_service()
            stt = create_uzbek_xlsr_stt()  # Use HF STT for faster processing
            tts = create_uzbek_tts() 

            # Check if lesson is prepared
            stats = llm_service.get_lesson_statistics(lesson_id)
            if "error" in stats:
                print(f"WARNING: Lesson '{lesson_id}' not found. Run 'qa-prepare' first.")
                return

            print(f"OK: Lesson ready with {stats.get('num_documents', 'unknown')} documents")

            # Voice Q&A loop
            voice_qa_loop(llm_service, stt, tts, lesson_id)

        except KeyboardInterrupt:
            print("\n👋 Voice Q&A stopped!")
        except Exception as e:
            print(f"❌ Failed to start voice Q&A: {e}")

    elif command == "enroll":
        print("👤 Student Enrollment - Face Recognition")
        
        enrollment = FaceEnrollmentSystem()
        db = FaceRecognitionDB()
        
        try:
            student_id, name, class_name, encoding = enrollment.enroll_student_interactive()
            
            if encoding is not None:
                success = db.add_student(student_id, name, class_name, encoding)
                if success:
                    print(f"✅ {name} enrolled successfully!")
                else:
                    print("❌ Enrollment failed - student may already exist")
            else:
                print("❌ Enrollment cancelled or failed")
        finally:
            db.close()

    elif command == "attendance":
        print("📹 Starting Entrance Camera Attendance System")
        
        camera_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        
        attendance = FaceRecognitionAttendance()
        
        try:
            attendance.run_entrance_camera(camera_id=camera_id, display=True)
        finally:
            attendance.close()

    elif command == "report":
        date = sys.argv[2] if len(sys.argv) > 2 else None
        
        db = FaceRecognitionDB()
        
        try:
            summary = db.get_attendance_summary(date)
            records = db.get_attendance(date)
            
            print("\n" + "="*50)
            print("📊 ATTENDANCE REPORT")
            print("="*50)
            print(f"Date: {summary['date']}")
            print(f"Total Students: {summary['total_students']}")
            print(f"Present: {summary['present']}")
            print(f"Absent: {summary['absent']}")
            print(f"Attendance Rate: {summary['attendance_rate']:.1f}%")
            
            if summary.get('by_class'):
                print("\nBy Class:")
                for class_name, count in summary['by_class'].items():
                    print(f"  {class_name}: {count} students")
            
            if records:
                print(f"\nAttendance Records ({len(records)}):")
                for record in records[:20]:  # Show first 20
                    print(f"  {record['timestamp']} - {record['name']} ({record['class_name']}) - {record['confidence']:.2f}")
                
                if len(records) > 20:
                    print(f"  ... and {len(records) - 20} more")
        finally:
            db.close()

    elif command == "students":
        db = FaceRecognitionDB()
        
        try:
            students = db.get_all_students(active_only=True)
            
            print("\n" + "="*50)
            print("👥 ENROLLED STUDENTS")
            print("="*50)
            print(f"Total: {len(students)}\n")
            
            for student in students:
                print(f"ID: {student['student_id']}")
                print(f"  Name: {student['name']}")
                print(f"  Class: {student['class_name']}")
                print(f"  Enrolled: {student['enrolled_date']}")
                print(f"  Photos: {student['photos_count']}")
                print()
        finally:
            db.close()

    else:
        print(f"Unknown command: {command}")
        print("Run 'python main.py' without arguments to see all available commands")

def live_transcription(model="nemo"):
    """Live transcription from microphone using specified model"""

    # Audio parameters
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 3  # Process every 3 seconds

    # Initialize STT based on model
    if model == "nemo":
        stt = create_uzbek_nemo_stt()
    elif model == "whisper":
        stt = create_uzbek_whisper_stt()
    else:  # default to hf
        stt = create_uzbek_hf_stt()

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open microphone stream
    stream = audio.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)

    print("🎤 Listening... (Speak in Uzbek)")
    print("💡 Processing every 3 seconds of audio")

    try:
        while True:
            # Record audio for RECORD_SECONDS
            frames = []

            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            # Convert to numpy array
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0

            # Skip if audio is too quiet (simple voice activity detection)
            if np.max(np.abs(audio_data)) < 0.01:
                print(".", end="", flush=True)
                continue

            # Transcribe
            print("\n🎯 Transcribing...", end="", flush=True)
            result = stt.transcribe_audio(audio_data, RATE)

            # Display result
            if result['text'].strip():
                print(f"\n📝 {result['text']}")
            else:
                print(" (no speech detected)")

    except KeyboardInterrupt:
        print("\n🛑 Stopping...")

    finally:
        # Clean up
        stream.stop_stream()
        stream.close()
        audio.terminate()

def interactive_teaching(model="hf"):
    """Interactive teaching mode combining STT and TTS"""

    # Lazy import TTS to avoid pygame warning
    from stt_pipelines.uzbek_tts_pipeline import create_uzbek_tts

    # Initialize STT based on model
    if model == "nemo":
        stt = create_uzbek_nemo_stt()
    elif model == "whisper":
        stt = create_uzbek_whisper_stt()
    else:  # default to hf
        stt = create_uzbek_hf_stt()

    tts = create_uzbek_tts()

    # Teaching scenarios
    lessons = {
        "math": {
            "title": "Matematika darsi",
            "questions": [
                "2 + 2 nechiga teng?",
                "5 dan 3 ni ayirib tashlasak, nechiga teng?",
                "3 ga 4 ni ko'paytirsak, nechiga teng?"
            ],
            "answers": ["4", "2", "12"],
            "explanations": [
                "2 va 2 ni qo'shsak, 4 ga teng bo'ladi.",
                "5 dan 3 ni ayirsak, 2 qoladi.",
                "3 ga 4 ni ko'paytirsak, 12 ga teng bo'ladi."
            ]
        },
        "reading": {
            "title": "O'qish darsi",
            "words": ["kitob", "qalam", "daftar", "o'qituvchi", "bolalar"],
            "sentences": [
                "Men kitob o'qiyman.",
                "Qalam bilan yozaman.",
                "Daftarimga yozaman."
            ]
        }
    }

    print("📚 Choose a lesson:")
    print("1. Math (Matematika)")
    print("2. Reading (O'qish)")

    while True:
        try:
            choice = input("\nEnter lesson number (or 'quit'): ").strip()

            if choice.lower() == 'quit':
                break

            if choice == '1':
                teach_math_lesson(tts, stt, lessons["math"])
            elif choice == '2':
                teach_reading_lesson(tts, stt, lessons["reading"])
            else:
                tts.speak_text("Noto'g'ri tanlov. 1 yoki 2 ni tanlang.")

        except KeyboardInterrupt:
            break

    print("\n👋 Dars tugadi!")

def teach_math_lesson(tts, stt, lesson):
    """Teach a math lesson interactively"""

    tts.speak_text(f"{lesson['title']}ni boshlaymiz!")

    for i, (question, answer, explanation) in enumerate(zip(
        lesson['questions'], lesson['answers'], lesson['explanations']
    )):
        print(f"\n📝 Savol {i+1}: {question}")

        # Ask the question
        tts.speak_text(question)
        time.sleep(1)

        # Listen for answer
        print("🎤 Sizning javobingizni ayting...")
        user_answer = listen_for_answer(stt)

        if user_answer:
            print(f"📝 Siz aytdingiz: {user_answer}")

            # Check if answer is correct
            if answer.lower() in user_answer.lower():
                tts.speak_text("Ajoyib! To'g'ri javob!")
                tts.speak_text(explanation)
            else:
                tts.speak_text(f"To'g'ri javob: {answer}")
                tts.speak_text(explanation)
        else:
            tts.speak_text(f"To'g'ri javob: {answer}")
            tts.speak_text(explanation)

        time.sleep(2)  # Pause between questions

    tts.speak_text("Dars tugadi! Yaxshi o'rgandingiz!")

def teach_reading_lesson(tts, stt, lesson):
    """Teach a reading lesson interactively"""

    tts.speak_text(f"{lesson['title']}ni boshlaymiz!")

    # Teach words
    tts.speak_text("Avval so'zlarni o'rganamiz:")
    for word in lesson['words']:
        print(f"📖 So'z: {word}")
        tts.speak_text(word)
        time.sleep(1)

        # Ask student to repeat
        tts.speak_text(f"Endi siz {word} so'zini ayting")
        user_word = listen_for_answer(stt)

        if user_word and word.lower() in user_word.lower():
            tts.speak_text("Yaxshi! To'g'ri!")
        else:
            tts.speak_text(f"To'g'ri so'z: {word}")

    # Teach sentences
    tts.speak_text("Endi jumlalarni o'qiymiz:")
    for sentence in lesson['sentences']:
        print(f"📖 Jumla: {sentence}")
        tts.speak_text(sentence)
        time.sleep(2)

        # Ask student to repeat
        tts.speak_text("Endi siz takrorlang")
        user_sentence = listen_for_answer(stt)

        if user_sentence:
            tts.speak_text("Yaxshi ish!")

    tts.speak_text("O'qish darsi tugadi!")

def listen_for_answer(stt, timeout=5):
    """Listen for a short answer from the user"""

    if not PYAUDIO_AVAILABLE:
        return input("🎤 Type your answer: ").strip()

    # Audio parameters for short answers
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                       input=True, frames_per_buffer=CHUNK)

    print("🎤 Listening for answer...", end="", flush=True)

    frames = []
    start_time = time.time()

    try:
        while time.time() - start_time < timeout:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

            # Simple voice detection
            audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            if np.max(np.abs(audio_chunk)) > 0.05:  # Voice detected
                print(" (voice detected)", end="", flush=True)
                break

        # Transcribe the collected audio
        if frames:
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
            result = stt.transcribe_audio(audio_data, RATE)
            return result['text'].strip()

    except Exception as e:
        print(f"❌ Listening error: {e}")

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

    return ""

def voice_qa_loop(llm_service, stt, tts, lesson_id):
    """Voice-based Q&A loop combining STT and LLM"""
    
    # Audio parameters for questions
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    QUESTION_TIMEOUT = 8  # seconds to listen for question

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                       input=True, frames_per_buffer=CHUNK)

    print("\n🎤 Ready for voice questions! Speak your question...")

    try:
        while True:
            print("\n🎤 Listening for question...", end="", flush=True)
            
            # Listen for question
            frames = []
            start_time = time.time()
            voice_detected = False
            
            while time.time() - start_time < QUESTION_TIMEOUT:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
                
                # Simple voice detection
                audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                if np.max(np.abs(audio_chunk)) > 0.05:  # Voice detected
                    if not voice_detected:
                        print(" (voice detected)", end="", flush=True)
                        voice_detected = True
            
            if not frames:
                print(" (timeout)")
                continue
                
            print(" (processing)")
            
            # Transcribe the question
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
            stt_result = stt.transcribe_audio(audio_data, RATE)
            question = stt_result.get('text', '').strip()
            
            if not question:
                print("❌ Could not understand the question. Please try again.")
                tts.speak_text("Savolingizni tushunmadim. Qaytadan ayting.")
                continue
            
            print(f"❓ Question: {question}")
            
            # Get answer from LLM
            print("🤔 Thinking...", end="", flush=True)
            answer, found, docs = llm_service.answer_question(question, lesson_id, use_llm=True)
            print(f"\r{' ' * 50}\r", end="")
            
            if found:
                print(f"✅ Answer: {answer}")
                # Speak the answer
                try:
                    tts.speak_text(answer)
                except Exception as e:
                    print(f"⚠️ TTS failed: {e}")
            else:
                print(f"❌ {answer}")
                tts.speak_text("Kechirasiz, bu savolga javob topilmadi.")
            
            print("\n🎤 Ready for next question... (or press Ctrl+C to stop)")

    except KeyboardInterrupt:
        print("\n🛑 Stopping voice Q&A...")

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    main()
