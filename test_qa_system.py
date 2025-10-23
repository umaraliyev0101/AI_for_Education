"""
Uzbek QA System - Example and Test Script
Demonstrates how to use the NLP/QA system with sample materials.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.uzbek_nlp_qa_service import UzbekQAService
from utils.uzbek_materials_processor import UzbekMaterialsProcessor


def create_sample_materials():
    """Create sample educational materials for testing."""
    os.makedirs("sample_materials", exist_ok=True)
    
    # Create sample text file
    sample_text = """
# Python Dasturlash Tilining Asoslari

## 1. Python Nima?
Python - bu yuqori darajali, talqin qilinadigan, umumiy maqsadli dasturlash tili. 
Python 1991-yilda Guido van Rossum tomonidan yaratilgan. Python dasturlash tilining 
nomi Monty Python's Flying Circus komediya guruhidan olingan.

## 2. Python'ning Afzalliklari
- O'rganish oson
- Keng qo'llanilish sohasi
- Katta jamiyat va kutubxonalar
- Platformadan mustaqil
- Bepul va ochiq kodli

## 3. Funksiyalar
Funksiya - bu ma'lum bir vazifani bajaruvchi kod bloki. Funksiyalar kodni qayta 
ishlatish imkonini beradi va dasturni tartibli qiladi.

Funksiya yaratish sintaksisi:
def funksiya_nomi(parametrlar):
    # funksiya tanasi
    return natija

Misol:
def salom(ism):
    return f"Salom, {ism}!"

result = salom("Ali")
print(result)  # Chiqish: Salom, Ali!

## 4. O'zgaruvchilar
O'zgaruvchi - bu ma'lumotlarni saqlash uchun ishlatiladigan konteyner. Python'da 
o'zgaruvchilarni e'lon qilish uchun maxsus kalit so'z ishlatilmaydi.

Misollar:
ism = "Aziza"
yosh = 20
talaba = True

## 5. Ma'lumot Turlari
Python'da asosiy ma'lumot turlari:
- int (butun sonlar): 10, -5, 0
- float (o'nlik sonlar): 3.14, -0.5
- str (matnlar): "Salom", 'Python'
- bool (mantiqiy): True, False
- list (ro'yxat): [1, 2, 3]
- dict (lug'at): {"ism": "Ali", "yosh": 25}
- tuple (o'zgarmas ro'yxat): (1, 2, 3)
- set (to'plam): {1, 2, 3}

## 6. Shartli Operatorlar
if operatori shartni tekshirish uchun ishlatiladi.

Sintaksis:
if shart:
    # agar shart to'g'ri bo'lsa
elif boshqa_shart:
    # agar birinchi shart noto'g'ri, lekin bu shart to'g'ri bo'lsa
else:
    # barcha shartlar noto'g'ri bo'lsa

## 7. Sikllar
Sikllar - bu kod blokini bir necha marta takrorlash uchun ishlatiladi.

for sikli:
for element in ro'yxat:
    # har bir element uchun bajariladigan kod

while sikli:
while shart:
    # shart to'g'ri bo'lguncha bajariladigan kod

## 8. Obyektga Yo'naltirilgan Dasturlash (OOP)
Class - bu obyektlar uchun shablon. Obyektlar - bu class'dan yaratilgan nusxalar.

Misol:
class Talaba:
    def __init__(self, ism, yosh):
        self.ism = ism
        self.yosh = yosh
    
    def tanishish(self):
        return f"Mening ismim {self.ism}, yoshim {self.yosh}"

talaba1 = Talaba("Olim", 19)
print(talaba1.tanishish())

## 9. Modullar va Kutubxonalar
Modul - bu Python kodlari saqlanadigan fayl. Kutubxona - bu bir nechta modullar 
to'plami.

Import qilish:
import math
from datetime import datetime
import numpy as np

## 10. Xatolarni Boshqarish
try-except bloki xatolarni tutish va boshqarish uchun ishlatiladi.

try:
    natija = 10 / 0
except ZeroDivisionError:
    print("Nolga bo'lish mumkin emas!")
finally:
    print("Bu har doim bajariladi")
"""
    
    with open("sample_materials/python_asoslari.txt", "w", encoding="utf-8") as f:
        f.write(sample_text)
    
    # Create another sample file
    sample_text2 = """
# Python Web Dasturlash

## Flask Framework
Flask - bu Python uchun kichik va sodda web framework. Flask minimal va moslashuvchan.

## Django Framework
Django - bu Python uchun yuqori darajali web framework. Django "batteries included" 
falsafasiga amal qiladi, ya'ni ko'p narsalar tayyor holda keladi.

## FastAPI
FastAPI - bu zamonaviy, tez (yuqori samarali) web framework API yaratish uchun. 
FastAPI Python 3.7+ uchun mo'ljallangan va type hints'lardan foydalanadi.

## REST API
REST (Representational State Transfer) - bu veb xizmatlar uchun arxitektura uslubi.
REST API HTTP protokoli orqali ishlaydi va JSON formatida ma'lumot almashadi.

## Database
Python'da ma'lumotlar bazasi bilan ishlash uchun:
- SQLite: O'rnatilgan, oddiy database
- PostgreSQL: Kuchli va ishonchli database
- MongoDB: NoSQL database
- MySQL: Ommabop SQL database

SQLAlchemy - Python uchun kuchli ORM (Object-Relational Mapping) kutubxonasi.
"""
    
    with open("sample_materials/python_web.txt", "w", encoding="utf-8") as f:
        f.write(sample_text2)
    
    print("✓ Namuna materiallar yaratildi:")
    print("  - sample_materials/python_asoslari.txt")
    print("  - sample_materials/python_web.txt")


def test_materials_processor():
    """Test the materials processor."""
    print("\n" + "="*60)
    print("MATERIALS PROCESSOR TEST")
    print("="*60)
    
    processor = UzbekMaterialsProcessor(chunk_size=500, chunk_overlap=100)
    
    # Process sample materials
    file_paths = [
        "sample_materials/python_asoslari.txt",
        "sample_materials/python_web.txt"
    ]
    
    documents = processor.process_materials(file_paths)
    
    print(f"\n✓ Qayta ishlangan hujjatlar: {len(documents)} qism")
    print(f"\nBirinchi qism:")
    print("-" * 60)
    print(f"Manba: {documents[0]['source']}")
    print(f"Matn: {documents[0]['text'][:200]}...")
    
    return documents


def test_qa_service():
    """Test the QA service."""
    print("\n" + "="*60)
    print("QA SERVICE TEST")
    print("="*60)
    
    # Initialize QA service (without LLM for faster testing)
    qa_service = UzbekQAService(
        model_type="huggingface",
        vector_store_type="faiss",
        k_documents=3
    )
    
    # Prepare lesson materials
    lesson_id = "test_lesson_python"
    file_paths = [
        "sample_materials/python_asoslari.txt",
        "sample_materials/python_web.txt"
    ]
    
    print(f"\n📚 Dars materiallari tayyorlanmoqda: {lesson_id}")
    success = qa_service.prepare_lesson_materials(file_paths, lesson_id)
    
    if success:
        print("✓ Materiallar muvaffaqiyatli tayyorlandi")
    else:
        print("✗ Materiallarni tayyorlashda xatolik")
        return
    
    # Get statistics
    stats = qa_service.get_lesson_statistics(lesson_id)
    print(f"\n📊 Statistika:")
    print(f"  - Hujjatlar soni: {stats.get('num_documents', 'N/A')}")
    print(f"  - Vector store: {stats.get('vector_store_type', 'N/A')}")
    print(f"  - Embedding model: {stats.get('embedding_model', 'N/A')}")
    
    # Test questions
    questions = [
        "Python nima?",
        "Funksiya nima va qanday yaratiladi?",
        "Python'da qanday ma'lumot turlari bor?",
        "Flask nima?",
        "REST API nima?",
        "Python'da modullar qanday import qilinadi?",
        "Java dasturlash tili haqida ma'lumot bering"  # Should not find answer
    ]
    
    print("\n" + "="*60)
    print("SAVOLLAR VA JAVOBLAR")
    print("="*60)
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. Savol: {question}")
        print("-" * 60)
        
        # Search similar documents (without LLM)
        docs = qa_service.search_similar_documents(question, lesson_id, k=2)
        
        if docs:
            print(f"✓ {len(docs)} tegishli hujjat topildi:")
            for j, doc in enumerate(docs, 1):
                print(f"\n   Hujjat {j}:")
                print(f"   Manba: {doc.metadata.get('source', 'N/A')}")
                print(f"   Matn: {doc.page_content[:150]}...")
        else:
            print("✗ Tegishli hujjat topilmadi")
        
        # Try to answer with LLM (will fallback to context if LLM not available)
        # answer, found, source_docs = qa_service.answer_question(
        #     question, lesson_id, use_llm=False
        # )
        # print(f"\nJavob: {answer[:200]}...")
        # print(f"Topildi: {'Ha' if found else 'Yo\'q'}")


def test_similarity_search():
    """Test semantic similarity search."""
    print("\n" + "="*60)
    print("SEMANTIC SIMILARITY TEST")
    print("="*60)
    
    from sentence_transformers import SentenceTransformer, util
    
    # Load embedding model
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    # Sample texts
    texts = [
        "Python - bu dasturlash tili",
        "Funksiya kod blokidir",
        "O'zgaruvchi ma'lumot saqlaydi",
        "Java - bu boshqa dasturlash tili",
        "HTML markup tili",
    ]
    
    query = "Python haqida ma'lumot"
    
    # Encode
    query_embedding = model.encode(query, convert_to_tensor=True)
    text_embeddings = model.encode(texts, convert_to_tensor=True)
    
    # Compute similarity
    similarities = util.cos_sim(query_embedding, text_embeddings)[0]
    
    print(f"\nSo'rov: '{query}'")
    print("\nO'xshashlik natijalari:")
    print("-" * 60)
    
    for text, score in zip(texts, similarities):
        print(f"  {score:.4f} - {text}")


def main():
    """Main test function."""
    print("="*60)
    print("UZBEK NLP/QA SYSTEM - TEST VA MISOL")
    print("="*60)
    
    # Create sample materials
    create_sample_materials()
    
    # Test materials processor
    test_materials_processor()
    
    # Test similarity search
    test_similarity_search()
    
    # Test QA service
    test_qa_service()
    
    print("\n" + "="*60)
    print("TEST TUGADI")
    print("="*60)
    print("\nKeyingi qadamlar:")
    print("1. Local LLM modelini yuklab oling (masalan, llama-2-7b)")
    print("2. model_path parametrini to'g'ri yo'lga o'zgartiring")
    print("3. use_llm=True bilan answer_question() chaqiring")
    print("4. Real dars materiallarini tayyorlang")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest to'xtatildi.")
    except Exception as e:
        print(f"\n✗ Xatolik: {str(e)}")
        import traceback
        traceback.print_exc()
