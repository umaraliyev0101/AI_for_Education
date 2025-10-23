"""
End-to-End Integration Test: STT → NLP/QA → TTS (Simplified)
Demonstrates the full workflow of the AI Education system.
"""

import os
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.uzbek_nlp_qa_service import UzbekQAService
from stt_pipelines.uzbek_xlsr_pipeline import UzbekXLSRSTT


def main():
    """Main function for end-to-end test."""
    print("="*70)
    print("AI EDUCATION SYSTEM - END-TO-END INTEGRATION TEST")
    print("STT (XLSR) → NLP/QA → Display Answer")
    print("="*70)
    
    # Initialize components
    print("\n📚 Komponentlar yuklanmoqda...\n")
    
    print("🎤 STT (Speech-to-Text) yuklanmoqda...")
    stt = UzbekXLSRSTT()
    print("   ✓ STT tayyor\n")
    
    print("🧠 NLP/QA xizmati yuklanmoqda...")
    qa_service = UzbekQAService(
        model_type="huggingface",
        vector_store_type="faiss",
        k_documents=3
    )
    print("   ✓ NLP/QA tayyor\n")
    
    print("✅ Barcha komponentlar yuklandi!\n")
    
    # Prepare lesson materials
    print("="*70)
    print("DARS MATERIALLARINI TAYYORLASH")
    print("="*70)
    
    lesson_id = "python_basics"
    file_paths = [
        "sample_materials/python_asoslari.txt",
        "sample_materials/python_web.txt"
    ]
    
    # Check if materials exist
    if not os.path.exists(file_paths[0]):
        print("⚠️  Namuna materiallar topilmadi, yaratilmoqda...")
        _create_sample_materials()
    
    print(f"\n📖 Dars ID: {lesson_id}")
    print(f"📄 Fayllar: {len(file_paths)}")
    
    success = qa_service.prepare_lesson_materials(file_paths, lesson_id)
    
    if not success:
        print("❌ Materiallar tayyorlanmadi!")
        return
    
    print("✅ Materiallar tayyor!")
    
    # Test questions
    test_questions = [
        "Python nima?",
        "Funksiya qanday yaratiladi?",
        "O'zgaruvchi nima?",
        "Python'da qanday ma'lumot turlari bor?"
    ]
    
    print("\n" + "="*70)
    print("TEST SAVOLLARI")
    print("="*70)
    
    for i, q in enumerate(test_questions, 1):
        print(f"{i}. {q}")
    
    print("\n🎯 Rejim tanlang:")
    print("  1. Test savollari bilan avtomatik")
    print("  2. Matn kiritish")
    print("  3. Mikrofon (audio yozish)")
    
    try:
        choice = input("\nTanlang (1-3) [1]: ").strip() or "1"
        
        if choice == "1":
            # Automated test mode
            for i, question in enumerate(test_questions, 1):
                print("\n" + "="*70)
                print(f"TEST {i}/{len(test_questions)}")
                print("="*70)
                _process_question(question, qa_service, lesson_id)
                
                if i < len(test_questions):
                    input("\n⏸️  Enter bosing (davom etish uchun)...")
        
        elif choice == "2":
            # Manual text input
            while True:
                question = input("\n📝 Savolingizni yozing (chiqish uchun 'exit'): ")
                if question.lower() in ['exit', 'chiqish', 'quit']:
                    break
                _process_question(question, qa_service, lesson_id)
        
        elif choice == "3":
            # Microphone mode
            print("\n🎤 Mikrofon rejimi tanlandi")
            audio_file = _record_audio(duration=5)
            
            if audio_file:
                # Transcribe
                print("\n" + "="*70)
                print("1️⃣  SAVOL (Speech-to-Text)")
                print("="*70)
                
                print(f"🎤 Audio fayl: {audio_file}")
                print("🔄 Transkripsiya...")
                
                result = stt.transcribe_file(audio_file)
                question = result['text']
                confidence = result.get('confidence', 0)
                
                print(f"✅ Tanib olingan matn: \"{question}\"")
                print(f"📊 Ishonch: {confidence:.2%}")
                
                # Clean up
                os.remove(audio_file)
                
                # Process question
                _process_question(question, qa_service, lesson_id)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  To'xtatildi")
    except Exception as e:
        print(f"\n❌ Xatolik: {str(e)}")
        import traceback
        traceback.print_exc()


def _process_question(question: str, qa_service, lesson_id: str):
    """Process a single question through the QA system."""
    
    print("\n" + "="*70)
    print("2️⃣  JAVOB QIDIRISH (NLP/QA)")
    print("="*70)
    
    print(f"❓ Savol: {question}")
    print("🔍 Qidiruv...")
    
    # Find answer
    answer, found, docs = qa_service.answer_question(
        question,
        lesson_id,
        use_llm=False
    )
    
    if found:
        print(f"✅ Javob topildi!\n")
        print("💬 JAVOB:")
        print("-" * 70)
        print(answer)
        print("-" * 70)
        
        print(f"\n📚 Manba hujjatlar ({len(docs)}):")
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            print(f"   {i}. {source}")
            print(f"      {doc.page_content[:80]}...")
    else:
        print("❌ Javob topilmadi")
        print(f"💬 JAVOB: {answer}")


def _record_audio(duration: int = 5) -> str:
    """Record audio from microphone."""
    print(f"\n🎤 Audio yozish ({duration} soniya)...")
    print("   Savolingizni bering...")
    
    output_file = "temp_question.wav"
    
    try:
        import pyaudio
        import wave
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        audio = pyaudio.PyAudio()
        
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        frames = []
        
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
            
            if i % (RATE // CHUNK) == 0:
                print(f"   {'●' * (i // (RATE // CHUNK) + 1)}", end='\r')
        
        print("\n   ✓ Yozish tugadi")
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        
        return output_file
        
    except Exception as e:
        print(f"   ⚠️  Xatolik: {str(e)}")
        return None


def _create_sample_materials():
    """Create sample materials."""
    os.makedirs("sample_materials", exist_ok=True)
    
    sample_text = """# Python Dasturlash Tilining Asoslari

## 1. Python Nima?
Python - bu yuqori darajali, talqin qilinadigan, umumiy maqsadli dasturlash tili.
Python 1991-yilda Guido van Rossum tomonidan yaratilgan.

## 2. Funksiyalar
Funksiya - bu ma'lum bir vazifani bajaruvchi kod bloki.

Funksiya yaratish:
def salom(ism):
    return f"Salom, {ism}!"

## 3. O'zgaruvchilar
O'zgaruvchi - bu ma'lumotlarni saqlash uchun konteyner.
Misol: ism = "Ali", yosh = 20

## 4. Ma'lumot Turlari
- int (butun sonlar): 10, -5
- float (o'nlik sonlar): 3.14
- str (matnlar): "Salom"
- bool (mantiqiy): True, False
"""
    
    with open("sample_materials/python_asoslari.txt", "w", encoding="utf-8") as f:
        f.write(sample_text)
    
    print("✓ Namuna materiallar yaratildi")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDastur to'xtatildi.")
