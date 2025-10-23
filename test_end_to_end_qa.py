"""
End-to-End Integration Test: STT → NLP/QA → TTS
Demonstrates the full workflow of the AI Education system:
1. Record audio question (or use pre-recorded)
2. Convert to text using STT (Uzbek XLSR)
3. Find answer using NLP/QA system
4. Convert answer to speech using TTS
5. Play the audio answer
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.uzbek_nlp_qa_service import UzbekQAService
from stt_pipelines.uzbek_xlsr_pipeline import UzbekXLSRSTT
from stt_pipelines.uzbek_tts_pipeline import UzbekTTSPipeline


class EndToEndQADemo:
    """End-to-end demonstration of the AI Education Q&A system."""
    
    def __init__(self):
        """Initialize all components."""
        print("="*70)
        print("AI EDUCATION SYSTEM - END-TO-END DEMO")
        print("="*70)
        print("\n📚 Komponentlar yuklanmoqda...\n")
        
        # Initialize STT
        print("🎤 STT (Speech-to-Text) yuklanmoqda...")
        self.stt = UzbekXLSRSTT()
        print("   ✓ STT tayyor\n")
        
        # Initialize TTS
        print("🔊 TTS (Text-to-Speech) yuklanmoqda...")
        self.tts = UzbekTTSPipeline()
        print("   ✓ TTS tayyor\n")
        
        # Initialize QA Service
        print("🧠 NLP/QA xizmati yuklanmoqda...")
        self.qa_service = UzbekQAService(
            model_type="huggingface",
            vector_store_type="faiss",
            k_documents=3
        )
        print("   ✓ NLP/QA tayyor\n")
        
        print("✅ Barcha komponentlar muvaffaqiyatli yuklandi!\n")
    
    async def prepare_lesson_materials(self, lesson_id: str = "python_basics"):
        """Prepare lesson materials for Q&A."""
        print("="*70)
        print("DARS MATERIALLARINI TAYYORLASH")
        print("="*70)
        
        # Check if sample materials exist
        file_paths = [
            "sample_materials/python_asoslari.txt",
            "sample_materials/python_web.txt"
        ]
        
        # Verify files exist
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"⚠️  Fayl topilmadi: {file_path}")
                print("   Namuna materiallar yaratilmoqda...")
                self._create_sample_materials()
                break
        
        print(f"\n📖 Dars ID: {lesson_id}")
        print(f"📄 Fayllar soni: {len(file_paths)}")
        
        # Prepare materials
        success = self.qa_service.prepare_lesson_materials(
            file_paths,
            lesson_id,
            force_rebuild=False
        )
        
        if success:
            print("✅ Materiallar tayyor!")
            
            # Show statistics
            stats = self.qa_service.get_lesson_statistics(lesson_id)
            print(f"\n📊 Statistika:")
            print(f"   • Hujjatlar: {stats.get('num_documents', 'N/A')}")
            print(f"   • Vector store: {stats.get('vector_store_type', 'N/A')}")
        else:
            print("❌ Materiallarni tayyorlashda xatolik!")
            return False
        
        return True
    
    def _create_sample_materials(self):
        """Create sample materials if they don't exist."""
        os.makedirs("sample_materials", exist_ok=True)
        
        sample_text = """# Python Dasturlash Tilining Asoslari

## 1. Python Nima?
Python - bu yuqori darajali, talqin qilinadigan, umumiy maqsadli dasturlash tili.
Python 1991-yilda Guido van Rossum tomonidan yaratilgan.

## 2. Funksiyalar
Funksiya - bu ma'lum bir vazifani bajaruvchi kod bloki. 
Funksiyalar kodni qayta ishlatish imkonini beradi.

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
- list (ro'yxat): [1, 2, 3]
"""
        
        with open("sample_materials/python_asoslari.txt", "w", encoding="utf-8") as f:
            f.write(sample_text)
    
    async def record_question(self, duration: int = 5) -> str:
        """
        Record audio question from microphone.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Path to recorded audio file
        """
        print("\n🎤 Audio yozish boshlandi...")
        print(f"   {duration} soniya davomida savol bering...")
        
        output_file = "temp_question.wav"
        
        try:
            import pyaudio
            import wave
            
            # Audio settings
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            
            audio = pyaudio.PyAudio()
            
            # Open stream
            stream = audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            frames = []
            
            # Record for specified duration
            for i in range(0, int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)
                
                # Progress indicator
                if i % (RATE // CHUNK) == 0:
                    print(f"   {'●' * (i // (RATE // CHUNK) + 1)}", end='\r')
            
            print("\n   ✓ Yozish tugadi")
            
            # Close stream
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Save to file
            with wave.open(output_file, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
            
            return output_file
            
        except Exception as e:
            print(f"   ⚠️  Mikrofondan yozishda xatolik: {str(e)}")
            print("   📝 Matn kiritish rejimiga o'tilmoqda...")
            return None
    
    async def transcribe_question(self, audio_file: str = None, text: str = None) -> str:
        """
        Convert audio to text using STT.
        
        Args:
            audio_file: Path to audio file
            text: Direct text input (if no audio)
            
        Returns:
            Transcribed text
        """
        print("\n"+"="*70)
        print("1️⃣  SAVOL (Speech-to-Text)")
        print("="*70)
        
        if text:
            # Direct text input
            print(f"📝 Matn kiritildi: {text}")
            return text
        
        if audio_file and os.path.exists(audio_file):
            # Transcribe audio
            print(f"🎤 Audio fayl: {audio_file}")
            print("🔄 Matunga aylantirilmoqda...")
            
            result = self.stt.transcribe_file(audio_file)
            transcribed_text = result['text']
            confidence = result.get('confidence', 0)
            
            print(f"✅ Tanib olingan matn: \"{transcribed_text}\"")
            print(f"📊 Ishonch darajasi: {confidence:.2%}")
            
            return transcribed_text
        
        # Fallback to text input
        print("⚠️  Audio fayl topilmadi")
        text = input("📝 Savolingizni yozing: ")
        return text
    
    async def find_answer(self, question: str, lesson_id: str = "python_basics") -> tuple:
        """
        Find answer using NLP/QA system.
        
        Args:
            question: Question text
            lesson_id: Lesson identifier
            
        Returns:
            Tuple of (answer, found, source_documents)
        """
        print("\n"+"="*70)
        print("2️⃣  JAVOB QIDIRISH (NLP/QA)")
        print("="*70)
        
        print(f"❓ Savol: {question}")
        print("🔍 Tegishli materiallar qidirilmoqda...")
        
        # Search for answer
        answer, found, docs = self.qa_service.answer_question(
            question,
            lesson_id,
            use_llm=False  # Fast retrieval mode
        )
        
        if found:
            print(f"✅ Javob topildi!")
            print(f"\n💬 Javob:\n{answer}\n")
            
            # Show sources
            print(f"📚 Manba hujjatlar ({len(docs)}):")
            for i, doc in enumerate(docs, 1):
                print(f"   {i}. {doc.metadata.get('source', 'Unknown')}")
                print(f"      {doc.page_content[:80]}...")
        else:
            print("❌ Javob topilmadi")
            answer = "Kechirasiz, bu savol bo'yicha ma'lumot topa olmadim. Iltimos, savolni boshqacha qilib bering."
        
        return answer, found, docs
    
    async def speak_answer(self, answer: str) -> str:
        """
        Convert answer to speech using TTS and play it.
        
        Args:
            answer: Answer text
            
        Returns:
            Path to generated audio file (if saved)
        """
        print("\n"+"="*70)
        print("3️⃣  JAVOBNI O'QISH (Text-to-Speech)")
        print("="*70)
        
        print("🔊 Audio generatsiya qilinmoqda...")
        
        try:
            # Generate speech asynchronously
            output_file = "temp_answer.mp3"
            
            import edge_tts
            
            # Generate speech using edge_tts directly
            communicate = edge_tts.Communicate(
                answer, 
                self.tts.voice,
                rate=self.tts.rate,
                volume=self.tts.volume
            )
            
            await communicate.save(output_file)
            print(f"✅ Audio yaratildi: {output_file}")
            
            # Play the audio
            print("🎵 Audio ijro qilinmoqda...")
            
            # Use pygame to play the audio file directly
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            
            pygame.mixer.quit()
            print("✅ Audio ijro tugadi")
            
            return output_file
            
        except Exception as e:
            print(f"❌ TTS xatolik: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    async def run_demo(self, use_microphone: bool = False, test_question: str = None):
        """
        Run the complete end-to-end demo.
        
        Args:
            use_microphone: Whether to record from microphone
            test_question: Test question text (if not using microphone)
        """
        print("\n"+"="*70)
        print("DEMO BOSHLANDI")
        print("="*70)
        
        # Step 0: Prepare materials
        success = await self.prepare_lesson_materials()
        if not success:
            print("\n❌ Demo to'xtatildi: Materiallar tayyorlanmadi")
            return
        
        # Step 1: Get question (STT)
        if use_microphone:
            audio_file = await self.record_question(duration=5)
            question = await self.transcribe_question(audio_file=audio_file)
            
            # Clean up temp file
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
        else:
            # Use test question or input
            question = test_question or input("\n📝 Savolingizni kiriting: ")
            question = await self.transcribe_question(text=question)
        
        if not question:
            print("\n❌ Savol olinmadi")
            return
        
        # Step 2: Find answer (NLP/QA)
        answer, found, docs = await self.find_answer(question)
        
        # Step 3: Speak answer (TTS) - this includes playback
        audio_file = await self.speak_answer(answer)
        
        # Clean up temp file
        if audio_file and os.path.exists(audio_file):
            os.remove(audio_file)
        
        print("\n"+"="*70)
        print("✅ DEMO TUGADI")
        print("="*70)


async def main():
    """Main function."""
    print("\n🎓 AI EDUCATION SYSTEM - END-TO-END TEST\n")
    
    # Create demo instance
    demo = EndToEndQADemo()
    
    # Test questions in Uzbek
    test_questions = [
        "Python nima?",
        "Funksiya qanday yaratiladi?",
        "O'zgaruvchi nima?",
        "Python'da qanday ma'lumot turlari bor?"
    ]
    
    print("\n📋 Test savollari:")
    for i, q in enumerate(test_questions, 1):
        print(f"  {i}. {q}")
    
    # Choose mode
    print("\n🎯 Rejimni tanlang:")
    print("  1. Test savol bilan avtomatik (tez)")
    print("  2. Mikrofondan savol (real)")
    print("  3. Qo'lda matn kiriting")
    
    try:
        choice = input("\nTanlang (1-3) [1]: ").strip() or "1"
        
        if choice == "1":
            # Automatic mode with test questions
            print("\n🤖 Avtomatik rejim tanlandi")
            for i, question in enumerate(test_questions, 1):
                print(f"\n{'='*70}")
                print(f"TEST {i}/{len(test_questions)}")
                print(f"{'='*70}")
                await demo.run_demo(use_microphone=False, test_question=question)
                
                if i < len(test_questions):
                    input("\n⏸️  Davom ettirish uchun Enter bosing...")
        
        elif choice == "2":
            # Microphone mode
            print("\n🎤 Mikrofon rejimi tanlandi")
            await demo.run_demo(use_microphone=True)
        
        else:
            # Manual text input
            print("\n📝 Qo'lda kiritish rejimi tanlandi")
            await demo.run_demo(use_microphone=False)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo to'xtatildi")
    except Exception as e:
        print(f"\n❌ Xatolik: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDastur to'xtatildi.")
