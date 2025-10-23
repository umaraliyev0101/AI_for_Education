# NLP/QA System - Quick Start Guide

## 🚀 Tezkor Boshlash

### 1. Paketlar o'rnatilganligini tekshirish

```bash
python -c "import sentence_transformers, langchain, faiss; print('✓ Barcha paketlar o'rnatilgan!')"
```

### 2. Test Scriptni Ishga Tushirish

```bash
python test_qa_system.py
```

Bu script avtomatik ravishda:
- Namuna materiallar yaratadi
- Materials processor'ni test qiladi  
- Embedding modelni test qiladi
- QA service'ni test qiladi

### 3. O'z Materiallaringiz bilan Sinab Ko'rish

```python
from utils.uzbek_nlp_qa_service import UzbekQAService

# QA service yaratish (LLM siz - tez test uchun)
qa_service = UzbekQAService(
    model_type="huggingface",
    vector_store_type="faiss"
)

# Materiallaringizni tayyorlash
lesson_id = "mening_darsim"
file_paths = [
    "path/to/your/presentation.pdf",
    "path/to/your/notes.txt"
]

# Vector store yaratish
if qa_service.prepare_lesson_materials(file_paths, lesson_id):
    print("✓ Materiallar tayyorlandi!")
    
    # Savolga javob berish (faqat retrieval - LLM siz)
    answer, found, docs = qa_service.answer_question(
        "Sizning savolingiz?",
        lesson_id,
        use_llm=False  # Tez test uchun
    )
    
    print(f"\nTopilgan hujjatlar: {len(docs)}")
    for i, doc in enumerate(docs, 1):
        print(f"\n{i}. {doc.metadata['source']}")
        print(f"   {doc.page_content[:150]}...")
```

## 📦 LLM Model O'rnatish (Ixtiyoriy - Yaxshi javoblar uchun)

### Variant 1: Kichik Model (Tez test uchun)

```python
# Bu avtomatik yuklanadi
qa_service = UzbekQAService(
    model_type="huggingface",
    model_path="google/flan-t5-small"
)
```

### Variant 2: Katta Model (Production uchun)

1. **Model yuklab oling:**

```bash
# Llama 2 model (4GB) - Tavsiya etiladi
# https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF
```

2. **`models/` papkaga joylashtiring:**

```
AI_in_Education/
├── models/
│   └── llama-2-7b-chat.Q4_K_M.gguf
```

3. **Kodda ishlatish:**

```python
qa_service = UzbekQAService(
    model_type="llamacpp",
    model_path="models/llama-2-7b-chat.Q4_K_M.gguf"
)
```

## 🔍 Tizimni Test Qilish

### Birinchi Test - Materials Processor

```python
from utils.uzbek_materials_processor import UzbekMaterialsProcessor

processor = UzbekMaterialsProcessor()

# Matn ajratish
text = processor.extract_text("your_file.pdf")
print(f"Ajratilgan matn: {len(text)} belgi")

# Chunklarga bo'lish
chunks = processor.split_text_into_chunks(text)
print(f"Yaratilgan chunklar: {len(chunks)}")
```

### Ikkinchi Test - Similarity Search

```python
# Vector store yaratish
qa_service.prepare_lesson_materials(file_paths, "test_lesson")

# O'xshash hujjatlarni topish
docs = qa_service.search_similar_documents(
    query="Your query here",
    lesson_id="test_lesson",
    k=3
)

print(f"Topilgan hujjatlar: {len(docs)}")
for doc in docs:
    print(f"- {doc.metadata['source']}: {doc.page_content[:100]}...")
```

### Uchinchi Test - Full QA (LLM bilan)

```python
# LLM bilan to'liq javob
answer, found, docs = qa_service.answer_question(
    "Sizning savolingiz?",
    "test_lesson",
    use_llm=True  # LLM ishlatish
)

print(f"Savol javob topildi: {'Ha' if found else 'Yo\'q'}")
print(f"Javob: {answer}")
```

## ⚙️ Sozlamalar

### Chunk Size Sozlash

```python
processor = UzbekMaterialsProcessor(
    chunk_size=1500,    # Katta chunklar = ko'proq kontekst
    chunk_overlap=300   # Katta overlap = yaxshiroq uzilmaydigan kontekst
)
```

### Retrieval Count Sozlash

```python
qa_service = UzbekQAService(
    k_documents=5  # Ko'proq hujjat = ko'proq kontekst
)
```

### Vector Store Turini Tanlash

```python
# FAISS (tez, RAM'da)
qa_service = UzbekQAService(vector_store_type="faiss")

# Chroma (sekinroq, disk'da)
qa_service = UzbekQAService(vector_store_type="chroma")
```

## 📊 Statistika va Monitoring

```python
# Dars statistikasi
stats = qa_service.get_lesson_statistics("test_lesson")
print(f"Hujjatlar: {stats['num_documents']}")
print(f"Vector store: {stats['vector_store_type']}")

# Materials processor statistikasi
chunks = processor.process_materials(file_paths)
print(f"Jami chunklar: {len(chunks)}")
print(f"O'rtacha chunk uzunligi: {sum(len(c['text']) for c in chunks) / len(chunks):.0f}")
```

## 🐛 Tez-tez Uchraydigan Muammolar

### 1. Model topilmadi

```python
# Tekshirish
import os
print(f"Model mavjud: {os.path.exists('models/your_model.gguf')}")
```

### 2. Memory error

```python
# Kichikroq model ishlating
qa_service = UzbekQAService(
    model_type="huggingface",
    model_path="google/flan-t5-small"
)
```

### 3. Fayl o'qilmayapti

```python
# Encoding'ni tekshiring
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()
```

## 📚 Keyingi Qadamlar

1. ✅ `test_qa_system.py` ni ishga tushiring
2. ✅ O'z materiallaringiz bilan test qiling
3. ✅ Yaxshi LLM model yuklab oling
4. ✅ Production uchun sozlang
5. ✅ Backend'ga integratsiya qiling

## 📖 To'liq Qo'llanma

To'liq qo'llanma uchun qarang: [NLP_QA_SYSTEM_README.md](docs/NLP_QA_SYSTEM_README.md)

---

**Omad tilaymiz! 🎉**
