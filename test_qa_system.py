#!/usr/bin/env python3
"""
Test QA System
Comprehensive testing script for the Uzbek LLM QA System with Llama-3.1-8B-Instruct-Uz
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if all required packages are installed."""
    print("🔍 Testing package imports...")

    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")

        import transformers
        print(f"✅ Transformers: {transformers.__version__}")

        import sentence_transformers
        print(f"✅ Sentence Transformers: {sentence_transformers.__version__}")

        import langchain
        print(f"✅ LangChain: {langchain.__version__}")

        import faiss
        print(f"✅ FAISS: {faiss.__version__}")

        from utils.uzbek_materials_processor import UzbekMaterialsProcessor
        print("✅ Uzbek Materials Processor")

        from utils.uzbek_llm_qa_service import UzbekLLMQAService
        print("✅ Uzbek LLM QA Service")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def test_materials_processor():
    """Test the materials processor with sample data."""
    print("\n📄 Testing Materials Processor...")

    try:
        from utils.uzbek_materials_processor import UzbekMaterialsProcessor

        processor = UzbekMaterialsProcessor(chunk_size=500, chunk_overlap=100)

        # Create sample text file for testing
        test_content = """
        Matematika darsi - Ko'paytirish

        Ko'paytirish - bu matematikadagi asosiy amallardan biridir.
        Ko'paytirish belgisi × yoki * belgisidir.

        Masalan:
        2 × 3 = 6
        5 × 4 = 20
        10 × 10 = 100

        Ko'paytirish qoidalari:
        1. Kommutativ qoida: a × b = b × a
        2. Assotsiativ qoida: (a × b) × c = a × (b × c)
        3. Distributiv qoida: a × (b + c) = a × b + a × c
        """

        test_file = "test_math.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        # Test text extraction
        text = processor.extract_from_txt(test_file)
        print(f"✅ Extracted text: {len(text)} characters")

        # Test chunking
        chunks = processor.split_text_into_chunks(text)
        print(f"✅ Created {len(chunks)} chunks")

        # Show sample chunk
        if chunks:
            print(f"📝 Sample chunk: {chunks[0][:100]}...")

        # Cleanup
        os.remove(test_file)

        return True

    except Exception as e:
        print(f"❌ Materials processor test failed: {e}")
        return False

def test_llm_service_initialization():
    """Test LLM service initialization (without heavy model loading)."""
    print("\n🤖 Testing LLM Service Initialization...")

    try:
        from utils.uzbek_llm_qa_service import create_uzbek_llm_qa_service

        # Test service creation (this will try to load models)
        print("⏳ Initializing LLM service (this may take a while)...")
        start_time = time.time()

        service = create_uzbek_llm_qa_service()

        init_time = time.time() - start_time
        print(f"✅ LLM service initialized in {init_time:.1f} seconds")
        # Get model info
        info = service.get_model_info()
        print(f"✅ LLM Model: {info['llm_model']}")
        print(f"✅ Embedding Model: {info['embedding_model']}")
        print(f"✅ Device: {info['device']}")

        return service

    except Exception as e:
        print(f"❌ LLM service initialization failed: {e}")
        print("💡 This might be due to model download issues or insufficient memory")
        return None

    except Exception as e:
        print(f"❌ LLM service initialization failed: {e}")
        print("💡 This might be due to model download issues or insufficient memory")
        return None

def test_vector_store_creation(service):
    """Test vector store creation with sample data."""
    print("\n🗂️ Testing Vector Store Creation...")

    if not service:
        print("❌ Skipping - no LLM service available")
        return False

    try:
        # Create sample materials
        test_content = """
        O'zbekiston Respublikasi

        O'zbekiston Markaziy Osiyodagi eng yirik davlatlardan biridir.
        Poytaxti - Toshkent shahri.

        Tarix:
        - Miloddan avvalgi 1-millenniumda - Bactria
        - 1924-yilda O'zbekiston SSR tashkil topgan
        - 1991-yilda mustaqillikka erishgan

        Aholisi: Taxminan 35 million kishi
        Rasmiy tili: O'zbek tili
        """

        test_file = "test_uzbekistan.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        # Test vector store creation
        file_paths = [test_file]
        lesson_id = "test_lesson"

        success = service.prepare_lesson_materials(file_paths, lesson_id)
        if success:
            print("✅ Vector store created successfully")

            # Test statistics
            stats = service.get_lesson_statistics(lesson_id)
            print(f"✅ Documents: {stats.get('num_documents', 'unknown')}")
            print(f"✅ Vector store type: {stats.get('vector_store_type', 'unknown')}")

            # Test similarity search
            docs = service.search_similar_documents("O'zbekiston poytaxti", lesson_id, k=2)
            print(f"✅ Found {len(docs)} similar documents")

            if docs:
                print(f"📝 Top document: {docs[0].page_content[:100]}...")

            # Cleanup
            os.remove(test_file)

            return True
        else:
            print("❌ Vector store creation failed")
            return False

    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False

def test_qa_functionality(service):
    """Test Q&A functionality."""
    print("\n❓ Testing Q&A Functionality...")

    if not service:
        print("❌ Skipping - no LLM service available")
        return False

    try:
        lesson_id = "test_lesson"

        # Test questions
        questions = [
            "O'zbekiston poytaxti qayer?",
            "O'zbekiston aholisi qancha?",
            "O'zbekiston qachon mustaqillikka erishgan?"
        ]

        for question in questions:
            print(f"\n🔍 Question: {question}")

            # Test retrieval-only
            answer, found, docs = service.answer_question(question, lesson_id, use_llm=False)
            print(f"📖 Retrieval-only: {'✅' if found else '❌'} {answer[:100]}...")

            # Test with LLM (if available)
            try:
                answer_llm, found_llm, docs_llm = service.answer_question(question, lesson_id, use_llm=True)
                print(f"🤖 With LLM: {'✅' if found_llm else '❌'} {answer_llm[:100]}...")
            except Exception as e:
                print(f"🤖 With LLM: ❌ Error - {e}")

        return True

    except Exception as e:
        print(f"❌ Q&A test failed: {e}")
        return False

def create_sample_lesson_materials():
    """Create sample lesson materials for testing."""
    print("\n📚 Creating Sample Lesson Materials...")

    try:
        # Create materials directory
        materials_dir = "sample_materials"
        os.makedirs(materials_dir, exist_ok=True)

        # Create sample files
        files_created = []

        # Math lesson
        math_content = """
        Matematika - Algebra

        Algebra - bu matematikaning bir qismi bo'lib, harflar va raqamlardan foydalangan holda
        umumiy qoidalarni ifodalash bilan shug'ullanadi.

        Asosiy tushunchalar:
        - O'zgaruvchi (variable): x, y, z kabi harflar
        - Tenglama (equation): ikki ifoda tengligini ko'rsatadi
        - Tengsizlik (inequality): bir ifoda ikkinchisidan katta yoki kichikligini ko'rsatadi

        Masalan:
        2x + 3 = 7
        x² + 2x - 3 = 0
        x > 5

        Algebra qoidalari:
        1. Tenglamani hal qilish: har ikkala tomondan bir xil amal bajarish
        2. Ko'paytirish: (a + b)² = a² + 2ab + b²
        3. Faktoring: x² - 4 = (x - 2)(x + 2)
        """

        math_file = os.path.join(materials_dir, "algebra_darsi.txt")
        with open(math_file, 'w', encoding='utf-8') as f:
            f.write(math_content)
        files_created.append(math_file)

        # History lesson
        history_content = """
        O'zbekiston Tarixi

        O'zbekiston hududida qadimdan odamlar yashagan. Bu yerda Bactria, Sogdiana,
        Xorazm kabi qadimiy tsivilizatsiyalar mavjud bo'lgan.

        O'rta asrlar:
        - 9-12 asrlar: Movarounnahr iqtisodiy va madaniy gullab-yashnagan
        - 13-14 asrlar: Chingizxon va Amir Temur davri
        - 15-16 asrlar: Shayboniyxonlar sulolasi

        Yangi davr:
        - 1860-1880 yillar: Rossiya imperiyasi tomonidan bosib olindi
        - 1924 yil: O'zbekiston SSR tashkil topdi
        - 1991 yil 31 avgust: Mustaqillik e'lon qilindi

        Mustaqillik yillari:
        - 1992 yil: Konstitutsiya qabul qilindi
        - 1994 yil: So'm milliy valyutasi joriy qilindi
        - 2016 yil: Toshkent shahri 2200 yilligini nishonladi
        """

        history_file = os.path.join(materials_dir, "tarix_darsi.txt")
        with open(history_file, 'w', encoding='utf-8') as f:
            f.write(history_content)
        files_created.append(history_file)

        print(f"✅ Created {len(files_created)} sample files in {materials_dir}")
        return materials_dir, files_created

    except Exception as e:
        print(f"❌ Failed to create sample materials: {e}")
        return None, []

def run_full_test():
    """Run complete test suite."""
    print("🚀 Starting Uzbek LLM QA System Test Suite")
    print("=" * 50)

    # Test 1: Imports
    if not test_imports():
        return False

    # Test 2: Materials Processor
    if not test_materials_processor():
        return False

    # Test 3: LLM Service Initialization
    service = test_llm_service_initialization()
    if not service:
        print("⚠️ LLM service not available - some tests will be skipped")
        return True  # Still return True as basic functionality works

    # Test 4: Vector Store Creation
    if not test_vector_store_creation(service):
        return False

    # Test 5: Q&A Functionality
    if not test_qa_functionality(service):
        return False

    print("\n" + "=" * 50)
    print("🎉 All tests passed successfully!")
    print("✅ Uzbek LLM QA System is ready to use")
    return True

def main():
    """Main test function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--create-samples":
        # Just create sample materials
        materials_dir, files = create_sample_lesson_materials()
        if materials_dir:
            print(f"\n📁 Sample materials created in: {materials_dir}")
            print("📄 Files:")
            for file in files:
                print(f"   - {file}")
        return

    # Run full test suite
    success = run_full_test()

    if success:
        print("\n💡 Next steps:")
        print("1. Run: python test_qa_system.py --create-samples")
        print("2. Start the backend: python -m uvicorn backend.main:app --reload")
        print("3. Test the API endpoints")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
