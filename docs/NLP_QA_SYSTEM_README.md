# Uzbek NLP/QA System - To'liq Qo'llanma

## Mundarija
1. [Umumiy Ma'lumot](#umumiy-malumot)
2. [Tizim Arxitekturasi](#tizim-arxitekturasi)
3. [O'rnatish](#ornatish)
4. [Modellarni Sozlash](#modellarni-sozlash)
5. [Foydalanish](#foydalanish)
6. [API Reference](#api-reference)
7. [Maslahatlar va Xatoliklarni Bartaraf Etish](#maslahatlar)

---

## Umumiy Ma'lumot

Uzbek NLP/QA System - bu o'quv materiallari asosida savollarга javob beradigan sun'iy intellekt tizimi. Tizim RAG (Retrieval Augmented Generation) texnologiyasidan foydalanadi va mahalliy (local) LLM modellar bilan ishlaydi.

### Asosiy Xususiyatlar

- ✅ **Ko'p formatli materiallar**: PDF, PPTX, DOCX, TXT fayllarni qo'llab-quvvatlaydi
- ✅ **Semantik qidiruv**: O'xshash mazmundagi hujjatlarni topadi
- ✅ **Offline ishlash**: Internet aloqasi talab qilinmaydi
- ✅ **O'zbek tili**: To'liq o'zbek tilida ishlaydi
- ✅ **Moslashuvchan**: Turli LLM modellar bilan ishlaydi
- ✅ **Tez**: FAISS vector store orqali tez qidiruv

### Tizim Komponentlari

1. **UzbekMaterialsProcessor**: Hujjatlardan matn ajratadi
2. **UzbekQAService**: Savol-javob tizimini boshqaradi
3. **Embedding Model**: Matnlarni vektorlarga aylantiradi
4. **Vector Store**: Vektorlarni saqlaydi va qidiradi (FAISS/Chroma)
5. **LLM Model**: Javoblarni generatsiya qiladi (LlamaCpp/HuggingFace)

---

## Tizim Arxitekturasi

```
┌─────────────────────────────────────────────────────────────┐
│                    O'QUV MATERIALLARI                        │
│            (PDF, PPTX, DOCX, TXT fayllar)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│             UzbekMaterialsProcessor                          │
│   • Matn ajratish (text extraction)                          │
│   • Chunklarga bo'lish (text splitting)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                Embedding Model                               │
│   (paraphrase-multilingual-MiniLM-L12-v2)                    │
│   • Matnlarni vektorlarga aylantirish                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Vector Store (FAISS/Chroma)                     │
│   • Vektorlarni saqlash                                      │
│   • O'xshashlik qidiruvi (similarity search)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                TALABA SAVOLI                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Retriever (Qidiruv tizimi)                      │
│   • Savolga mos hujjatlarni topish                          │
│   • Top-K eng mos hujjatlarni qaytarish                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                LLM Model (Local)                             │
│   • Topilgan kontekst + Savol                               │
│   • Javobni generatsiya qilish                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    JAVOB                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## O'rnatish

### 1. Dependencies o'rnatish

```bash
pip install -r requirements.txt
```

### 2. Zarur kutubxonalar

```
# Asosiy kutubxonalar
sentence-transformers    # Embedding model uchun
langchain               # LLM framework
langchain-community     # Qo'shimcha komponentlar
faiss-cpu              # Vector store (CPU versiyasi)
# yoki
faiss-gpu              # Vector store (GPU versiyasi - tezroq)

# Hujjat qayta ishlash
PyPDF2                 # PDF fayllar
python-pptx            # PowerPoint fayllar
python-docx            # Word hujjatlari

# LLM modellar
llama-cpp-python       # LlamaCpp (GGUF modellar)
transformers           # HuggingFace modellar
torch                  # PyTorch

# Qo'shimcha
tiktoken              # Tokenizatsiya
chromadb              # Muqobil vector store
```

### 3. Disk bo'sh joyi

- Embedding model: ~500MB
- LLM model: 4GB - 13GB (modelga qarab)
- Vector store: 10MB - 1GB (materiallar hajmiga qarab)

---

## Modellarni Sozlash

### Embedding Model (Avtomatik yuklanadi)

Tizim avtomatik ravishda embedding modelni yuklab oladi:
```python
model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

Bu model:
- Hajmi: ~500MB
- Ko'p tilni qo'llab-quvvatlaydi (shu jumladan o'zbek)
- Tez ishlaydi
- Yaxshi natija beradi

### LLM Model (Qo'lda yuklab olish kerak)

#### Variant 1: LlamaCpp (Tavsiya etiladi)

**1. GGUF modelini yuklab oling:**

Masalan, Llama-2 modelini:
```bash
# Hugging Face'dan yuklab olish
# https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF

# Yoki wget bilan:
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf
```

**Tavsiya etiladigan modellar:**

| Model | Hajmi | RAM | Sifat |
|-------|-------|-----|-------|
| Llama-2-7B-Chat Q4 | 4GB | 8GB | Yaxshi |
| Llama-2-13B-Chat Q4 | 7GB | 16GB | Juda yaxshi |
| Mistral-7B Q4 | 4GB | 8GB | A'lo |
| Zephyr-7B Q4 | 4GB | 8GB | A'lo |

**2. Modelni joylashtiring:**
```
AI_in_Education/
├── models/
│   └── llama-2-7b-chat.Q4_K_M.gguf
```

**3. Kodda sozlang:**
```python
qa_service = UzbekQAService(
    model_type="llamacpp",
    model_path="models/llama-2-7b-chat.Q4_K_M.gguf"
)
```

#### Variant 2: HuggingFace Transformers

```python
qa_service = UzbekQAService(
    model_type="huggingface",
    model_path="google/flan-t5-base"  # Avtomatik yuklanadi
)
```

**HuggingFace modellari:**
- `google/flan-t5-small` - 300MB, tez, oddiy savollar
- `google/flan-t5-base` - 1GB, yaxshi, umumiy maqsad
- `google/flan-t5-large` - 3GB, a'lo, murakkab savollar

---

## Foydalanish

### Asosiy Misol

```python
from utils.uzbek_nlp_qa_service import UzbekQAService

# 1. QA Service yaratish
qa_service = UzbekQAService(
    model_type="llamacpp",
    model_path="models/llama-2-7b-chat.Q4_K_M.gguf",
    vector_store_type="faiss",
    k_documents=3  # Nechta hujjat topish
)

# 2. Dars materiallarini tayyorlash
lesson_id = "python_asoslari_dars_1"
file_paths = [
    "materials/python_lecture.pdf",
    "materials/python_slides.pptx",
    "materials/python_notes.txt"
]

success = qa_service.prepare_lesson_materials(file_paths, lesson_id)

if success:
    print("✓ Materiallar tayyorlandi!")
    
    # 3. Savolga javob berish
    question = "Python'da funksiya qanday yaratiladi?"
    answer, found, docs = qa_service.answer_question(question, lesson_id)
    
    print(f"Savol: {question}")
    print(f"Javob: {answer}")
    print(f"Topildi: {'Ha' if found else 'Yo\'q'}")
    
    # Manba hujjatlarni ko'rish
    for i, doc in enumerate(docs, 1):
        print(f"\nManba {i}: {doc.metadata['source']}")
        print(f"Matn: {doc.page_content[:200]}...")
```

### Ilg'or Foydalanish

#### Vector Store ni qayta yuklash

```python
# Yangi materiallar qo'shish (force_rebuild=True)
qa_service.prepare_lesson_materials(
    file_paths,
    lesson_id,
    force_rebuild=True
)
```

#### Mavjud Vector Store ni yuklash

```python
# Oldindan tayyorlangan vector store'ni yuklash
vector_store = qa_service.load_vector_store(lesson_id)

if vector_store:
    print("Vector store yuklandi!")
```

#### Faqat qidiruv (LLM siz)

```python
# Faqat tegishli hujjatlarni topish
docs = qa_service.search_similar_documents(
    query="Python'da loop nima?",
    lesson_id=lesson_id,
    k=5  # 5 ta hujjat
)

for doc in docs:
    print(doc.page_content)
```

#### LLM siz javob berish

```python
# Agar LLM yuklangan bo'lmasa yoki faqat kontekst kerak bo'lsa
answer, found, docs = qa_service.answer_question(
    question,
    lesson_id,
    use_llm=False  # Faqat topilgan kontekstni qaytaradi
)
```

#### Statistika olish

```python
stats = qa_service.get_lesson_statistics(lesson_id)
print(f"Hujjatlar soni: {stats['num_documents']}")
print(f"Vector store: {stats['vector_store_type']}")
```

### Materials Processor ni alohida ishlatish

```python
from utils.uzbek_materials_processor import UzbekMaterialsProcessor

processor = UzbekMaterialsProcessor(
    chunk_size=1000,    # Har bir chunkning hajmi
    chunk_overlap=200   # Chunklar orasidagi kesishma
)

# Bitta fayl
text = processor.extract_text("lecture.pdf")

# Ko'p fayllar
chunks = processor.process_materials([
    "file1.pdf",
    "file2.pptx",
    "file3.docx"
])

# To'liq papka
chunks = processor.process_directory("materials/")

# Saqlash va yuklash
processor.save_processed_materials(chunks, "processed.json")
loaded_chunks = processor.load_processed_materials("processed.json")
```

---

## API Reference

### UzbekQAService

#### Constructor

```python
UzbekQAService(
    model_type: str = "huggingface",
    model_path: Optional[str] = None,
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    vector_store_type: str = "faiss",
    vector_store_path: Optional[str] = None,
    k_documents: int = 3
)
```

**Parametrlar:**
- `model_type`: LLM turi ("llamacpp" yoki "huggingface")
- `model_path`: LLM model fayli yo'li
- `embedding_model`: Embedding model nomi
- `vector_store_type`: Vector store turi ("faiss" yoki "chroma")
- `vector_store_path`: Vector store'lar saqlanadigan papka
- `k_documents`: Nechta hujjat retrieval qilish

#### prepare_lesson_materials()

```python
prepare_lesson_materials(
    file_paths: List[str],
    lesson_id: str,
    force_rebuild: bool = False
) -> bool
```

Dars materiallarini qayta ishlaydi va vector store yaratadi.

**Parametrlar:**
- `file_paths`: Material fayllari yo'llari
- `lesson_id`: Dars identifikatori (unique)
- `force_rebuild`: Mavjud vector store'ni qayta yarat

**Qaytaradi:** Muvaffaqiyat holati (True/False)

#### answer_question()

```python
answer_question(
    question: str,
    lesson_id: str,
    use_llm: bool = True
) -> Tuple[str, bool, List[Document]]
```

Savolga javob beradi.

**Parametrlar:**
- `question`: Talaba savoli
- `lesson_id`: Dars identifikatori
- `use_llm`: LLM'dan foydalanish

**Qaytaradi:** (javob, topildi, manba_hujjatlar)

#### search_similar_documents()

```python
search_similar_documents(
    query: str,
    lesson_id: str,
    k: Optional[int] = None
) -> List[Document]
```

O'xshash hujjatlarni qidiradi.

#### load_vector_store()

```python
load_vector_store(lesson_id: str) -> Optional[VectorStore]
```

Saqlangan vector store'ni yuklaydi.

#### get_lesson_statistics()

```python
get_lesson_statistics(lesson_id: str) -> Dict
```

Dars statistikasini qaytaradi.

### UzbekMaterialsProcessor

#### Constructor

```python
UzbekMaterialsProcessor(
    chunk_size: int = 1000,
    chunk_overlap: int = 200
)
```

#### extract_text()

```python
extract_text(file_path: str) -> str
```

Fayldan matn ajratadi.

#### process_materials()

```python
process_materials(file_paths: List[str]) -> List[Dict[str, str]]
```

Ko'p fayllarni qayta ishlaydi.

#### process_directory()

```python
process_directory(directory_path: str) -> List[Dict[str, str]]
```

Papkadagi barcha qo'llab-quvvatlanadigan fayllarni qayta ishlaydi.

---

## Maslahatlar

### Performans Optimizatsiyasi

1. **GPU ishlatish** (agar mavjud bo'lsa):
```bash
pip uninstall faiss-cpu
pip install faiss-gpu
```

2. **Chunk size sozlash**:
- Katta chunk (1500-2000): Kam chunk, ko'proq kontekst
- Kichik chunk (500-800): Ko'p chunk, aniqroq qidiruv

3. **k_documents sozlash**:
- Ko'proq hujjat (5-7): Ko'proq kontekst, sekinroq
- Kamroq hujjat (2-3): Kamroq kontekst, tezroq

### Xotira Tejash

1. Kichikroq LLM modeldan foydalaning (Q4 quantized)
2. Vector store'larni disk'da saqlang va kerak bo'lganda yuklang
3. `use_llm=False` bilan faqat retrieval qiling

### Sifatni Oshirish

1. **Materiallarni to'g'ri formatda tayyorlang**:
   - Aniq va tushunarli matn
   - Mantiqiy tuzilma
   - Keraksiz ma'lumotlarsiz

2. **Chunk overlap'ni oshiring** (200-300):
   - Kontekst uzilmasligi uchun

3. **Ko'proq k_documents** (5-7):
   - Ko'proq kontekst = yaxshiroq javoblar

4. **Yaxshi LLM model tanlang**:
   - Mistral-7B, Llama-2-13B - eng yaxshi natija

### Xatoliklarni Bartaraf Etish

#### Xatolik: "Model file not found"

```python
# Model yo'lini tekshiring
import os
model_path = "models/llama-2-7b.gguf"
print(f"Model mavjudmi: {os.path.exists(model_path)}")
```

#### Xatolik: "Out of memory"

```python
# Kichikroq model ishlating yoki LLM'siz ishlang
qa_service = UzbekQAService(
    model_type="huggingface",
    model_path="google/flan-t5-small"  # Kichik model
)
```

#### Xatolik: "Vector store not found"

```python
# Vector store'ni qayta yarating
qa_service.prepare_lesson_materials(file_paths, lesson_id, force_rebuild=True)
```

#### Xatolik: "Encoding error"

```python
# UTF-8 encoding'ni tekshiring
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()
```

### Tavsiyalar

1. **Birinchi marta test qiling**: Kichik materiallar bilan boshlang
2. **LLM'siz test qiling**: Avval retrieval ishlashini tekshiring
3. **Loglarni kuzating**: `logging.INFO` level'da ishlating
4. **Backup oling**: Vector store'larni saqlang
5. **Versiyalarni kuzatib boring**: Model versiyalarini yozib qo'ying

---

## Test Qilish

Test scriptni ishga tushiring:

```bash
python test_qa_system.py
```

Bu script:
1. Namuna materiallar yaratadi
2. Materials processor'ni test qiladi
3. Embedding va similarity search'ni test qiladi
4. QA service'ni test qiladi

---

## Keyingi Qadamlar

1. **Real materiallarni tayyorlang**: PDF, PPTX fayllaringizni tayyorlang
2. **LLM modelni yuklab oling**: Mistral yoki Llama-2 modelini oling
3. **Test qiling**: Turli savollar bilan test qiling
4. **Backend integratsiya**: FastAPI bilan integratsiya qiling
5. **Production deploy**: Serverdа ishga tushiring

---

## Qo'shimcha Resurslar

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [Llama.cpp](https://github.com/ggerganov/llama.cpp)
- [HuggingFace Models](https://huggingface.co/models)

---

## Muallif va Yordam

Savol va takliflar uchun:
- GitHub Issues
- Telegram: @your_username
- Email: your_email@example.com

**Omad tilaymiz! 🚀**
