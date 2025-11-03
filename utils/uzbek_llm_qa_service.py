#!/usr/bin/env python3
"""
Uzbek LLM QA Service
Integrates FLAN-T5 for question answering with RAG (Retrieval-Augmented Generation)

Note: Model can be changed in backend/llm_config.py
"""

import os
import json
import logging
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
    BitsAndBytesConfig
)
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import faiss
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UzbekLLMQAService:
    """
    Uzbek Language Question Answering Service using FLAN-T5
    with Retrieval-Augmented Generation (RAG)
    """

    def __init__(
        self,
        model_name: str = None,  # If None, loads from backend/llm_config.py
        embedding_model: str = None,  # If None, loads from backend/llm_config.py
        vector_store_type: str = "faiss",
        device: str = "auto",
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        k_documents: int = 3
    ):
        """
        Initialize the Uzbek LLM QA Service.

        Args:
            model_name: HuggingFace model name (if None, loads from llm_config.py)
            embedding_model: Model for text embeddings (if None, loads from llm_config.py)
            vector_store_type: Type of vector store ('faiss' or 'chroma')
            device: Device to run models on ('auto', 'cpu', 'cuda')
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature for generation
            k_documents: Number of documents to retrieve for context
        """
        # Load from config if not provided
        if model_name is None or embedding_model is None:
            try:
                from backend.llm_config import get_llm_config
                config = get_llm_config()
                model_name = model_name or config["model_name"]
                embedding_model = embedding_model or config["embedding_model"]
                logger.info(f"Loaded model configuration from llm_config.py")
            except ImportError:
                # Fallback to default if config not found
                # model_name = model_name or "behbudiy/Llama-3.1-8B-Instruct-Uz"
                model_name = model_name or "google/flan-t5-xl"
                embedding_model = embedding_model or "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
                logger.warning("llm_config.py not found, using default models")
        
        self.model_name = model_name
        self.embedding_model_name = embedding_model
        self.vector_store_type = vector_store_type
        self.device = device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.k_documents = k_documents

        # Initialize components
        self.tokenizer = None
        self.model = None
        self.embedding_model = None
        self.vector_stores = {}  # lesson_id -> vector_store
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        logger.info(f"Initializing Uzbek LLM QA Service on device: {self.device}")
        self._initialize_models()

    def _initialize_models(self):
        """Initialize the LLM and embedding models."""
        try:
            # Initialize tokenizer and model
            logger.info(f"Loading LLM: {self.model_name}")
            
            if "flan-t5" in self.model_name.lower():
                # Use T5ForConditionalGeneration for T5 models
                from transformers import T5ForConditionalGeneration
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
                
                # Create text2text generation pipeline for T5
                self.pipe = pipeline(
                    "text2text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    max_length=self.max_new_tokens,
                    temperature=self.temperature,
                    do_sample=True
                )
            else:
                # Use standard causal LM for Llama/GPT models
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

                # Configure quantization for memory efficiency
                if self.device == "cuda":
                    quantization_config = BitsAndBytesConfig(
                        load_in_8bit=True,  # Changed to 8-bit for offloading support
                        llm_int8_enable_fp32_cpu_offload=True,  # Moved here for 8-bit quantization
                        bnb_8bit_compute_dtype=torch.float16,
                        bnb_8bit_use_double_quant=True
                    )
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_name,
                        # load_in_8bit=True,
                        quantization_config=quantization_config,
                        # llm_int8_enable_fp32_cpu_offload=True,
                        device_map="auto",
                        torch_dtype=torch.float16
                    )
                else:  # CPU
                    quantization_config = BitsAndBytesConfig(
                        load_in_8bit=True,  # Use 8-bit quantization for CPU
                        bnb_8bit_compute_dtype=torch.float16,
                        bnb_8bit_use_double_quant=True
                    )
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_name,
                        quantization_config=quantization_config,
                        torch_dtype=torch.float32
                    )

                # Create text generation pipeline
                self.pipe = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    max_new_tokens=self.max_new_tokens,
                    temperature=self.temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Initialize embedding model
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name,
                model_kwargs={'device': self.device}
            )

            logger.info("✅ Models initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize models: {e}")
            raise

    def prepare_lesson_materials(
        self,
        file_paths: List[str],
        lesson_id: str,
        force_recreate: bool = False
    ) -> bool:
        """
        Process lesson materials and create vector store.

        Args:
            file_paths: List of file paths to process
            lesson_id: Unique identifier for the lesson
            force_recreate: Whether to recreate vector store if it exists

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if vector store already exists
            if lesson_id in self.vector_stores and not force_recreate:
                logger.info(f"Vector store for lesson {lesson_id} already exists")
                return True

            # Process materials using the existing processor
            from utils.uzbek_materials_processor import UzbekMaterialsProcessor
            processor = UzbekMaterialsProcessor()
            chunks = processor.process_materials(file_paths)

            if not chunks:
                logger.warning(f"No content extracted from files for lesson {lesson_id}")
                return False

            # Convert to LangChain documents
            documents = []
            for chunk in chunks:
                doc = Document(
                    page_content=chunk['text'],
                    metadata={
                        'source': chunk['source'],
                        'chunk_id': chunk['chunk_id'],
                        'file_path': chunk['file_path'],
                        'lesson_id': lesson_id
                    }
                )
                documents.append(doc)

            # Create vector store
            if self.vector_store_type == "faiss":
                self.vector_stores[lesson_id] = FAISS.from_documents(
                    documents, self.embedding_model
                )
            elif self.vector_store_type == "chroma":
                self.vector_stores[lesson_id] = Chroma.from_documents(
                    documents,
                    self.embedding_model,
                    collection_name=f"lesson_{lesson_id}"
                )
            else:
                raise ValueError(f"Unsupported vector store type: {self.vector_store_type}")

            logger.info(f"✅ Created vector store for lesson {lesson_id} with {len(documents)} chunks")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to prepare lesson materials: {e}")
            return False

    def search_similar_documents(
        self,
        query: str,
        lesson_id: str,
        k: Optional[int] = None
    ) -> List[Document]:
        """
        Search for similar documents in the lesson materials.

        Args:
            query: Search query
            lesson_id: Lesson identifier
            k: Number of documents to retrieve

        Returns:
            List of similar documents
        """
        if lesson_id not in self.vector_stores:
            # Try to load from disk
            load_path = f"vector_stores/{lesson_id}"
            if os.path.exists(load_path):
                try:
                    self.load_vector_store(lesson_id, load_path)
                except Exception as e:
                    logger.warning(f"Could not load vector store for lesson {lesson_id}: {e}")
                    return []
            else:
                return []

        if k is None:
            k = self.k_documents

        try:
            vector_store = self.vector_stores[lesson_id]
            docs = vector_store.similarity_search(query, k=k)
            return docs
        except Exception as e:
            logger.error(f"❌ Failed to search documents: {e}")
            return []

    def generate_answer_with_context(
        self,
        question: str,
        context_docs: List[Document]
    ) -> str:
        """
        Generate an answer using the LLM with retrieved context.

        Args:
            question: User's question
            context_docs: Retrieved context documents

        Returns:
            Generated answer
        """
        import time
        start_time = time.time()
        
        try:
            print(f"[LLM] Preparing context for question: '{question[:50]}...'")
            
            # Prepare context
            context = "\n\n".join([doc.page_content for doc in context_docs])
            context_length = len(context.split())
            
            print(f"[LLM] Context prepared: {context_length} words from {len(context_docs)} documents")
            print(f"[LLM] Starting inference with {self.model_name} on {self.device}...")

            if "flan-t5" in self.model_name.lower():
                # Use T5-style prompt
                prompt = f"Answer the question based on the context.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:"
                
                print(f"[LLM] Using T5-style prompt (length: {len(prompt)} chars)")
                
                # Generate answer with T5
                inference_start = time.time()
                print(f"[LLM] {time.strftime('%H:%M:%S')} - Starting T5 inference...")
                
                outputs = self.pipe(
                    prompt,
                    max_length=self.max_new_tokens,
                    temperature=self.temperature,
                    do_sample=True
                )
                
                inference_time = time.time() - inference_start
                print(f"[LLM] {time.strftime('%H:%M:%S')} - T5 inference completed in {inference_time:.1f}s")
                
                answer = outputs[0]['generated_text'].strip()
            else:
                # Use Llama/GPT-style prompt
                prompt = f"""Siz o'zbek tilidagi savollarga javob beruvchi yordamchi assistentsiz.
Quyidagi kontekst ma'lumotlariga asosan savolga aniq va foydali javob bering.

Kontekst:
{context}

Savol: {question}

Javob:"""

                prompt_length = len(prompt.split())
                print(f"[LLM] Using Llama-style prompt (length: {prompt_length} words)")
                
                # Generate answer with progress monitoring
                inference_start = time.time()
                print(f"[LLM] {time.strftime('%H:%M:%S')} - Starting Llama inference...")
                
                # Start a progress monitoring thread
                import threading
                stop_progress = threading.Event()
                
                def progress_monitor():
                    elapsed = 0
                    while not stop_progress.is_set():
                        time.sleep(30)  # Check every 30 seconds
                        elapsed += 30
                        print(f"[LLM] {time.strftime('%H:%M:%S')} - Still generating... ({elapsed}s elapsed)")
                        if elapsed > 600:  # 10 minutes
                            print(f"[LLM] {time.strftime('%H:%M:%S')} - WARNING: Generation taking very long (>10min)")
                
                progress_thread = threading.Thread(target=progress_monitor, daemon=True)
                progress_thread.start()
                
                try:
                    outputs = self.pipe(
                        prompt,
                        max_new_tokens=self.max_new_tokens,
                        temperature=self.temperature,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                finally:
                    stop_progress.set()
                    progress_thread.join(timeout=1)
                
                inference_time = time.time() - inference_start
                print(f"[LLM] {time.strftime('%H:%M:%S')} - Llama inference completed in {inference_time:.1f}s")

                # Extract the generated answer
                generated_text = outputs[0]['generated_text']
                answer = generated_text[len(prompt):].strip()

            total_time = time.time() - start_time
            print(f"[LLM] Total generation time: {total_time:.1f}s")
            print(f"[LLM] Generated answer length: {len(answer)} chars")

            return answer

        except Exception as e:
            total_time = time.time() - start_time
            print(f"[LLM] ERROR after {total_time:.1f}s: {e}")
            logger.error(f"❌ Failed to generate answer: {e}")
            return "Kechirasiz, javob generatsiya qilishda xatolik yuz berdi."

    def generate_answer_general_knowledge(self, question: str) -> str:
        """
        Generate an answer using the LLM's general knowledge without context.

        Args:
            question: User's question

        Returns:
            Generated answer
        """
        import time
        start_time = time.time()
        
        try:
            print(f"[LLM] Generating general knowledge answer for: '{question[:50]}...'")
            print(f"[LLM] Starting inference with {self.model_name} on {self.device}...")

            # First, try some basic pattern matching for common questions
            # answer = self._try_basic_fallbacks(question)
            # if answer:
            #     return answer

            if "flan-t5" in self.model_name.lower():
                # Use better T5 prompts for general knowledge
                # Try multiple prompt formats to see which works better
                prompts = [
                    f"Please answer this question: {question}",
                    f"Question: {question} Answer:",
                    f"What is the answer to: {question}",
                    f"Answer this question in Uzbek: {question}"
                ]
                
                for prompt in prompts:
                    try:
                        print(f"[LLM] Trying T5 prompt: '{prompt[:50]}...'")
                        
                        inference_start = time.time()
                        print(f"[LLM] {time.strftime('%H:%M:%S')} - Starting T5 inference...")
                        
                        outputs = self.pipe(
                            prompt,
                            max_length=self.max_new_tokens,
                            temperature=self.temperature,
                            do_sample=True
                        )
                        
                        inference_time = time.time() - inference_start
                        print(f"[LLM] {time.strftime('%H:%M:%S')} - T5 inference completed in {inference_time:.1f}s")
                        
                        answer = outputs[0]['generated_text'].strip()
                        
                        # Check if the answer is not just repeating the question or repetitive/irrelevant
                        if (answer and 
                            not self._is_repeating_question(question, answer) and 
                            not self._is_repetitive_text(answer) and
                            not self._is_irrelevant_answer(question, answer)):
                            total_time = time.time() - start_time
                            print(f"[LLM] Total generation time: {total_time:.1f}s")
                            print(f"[LLM] Generated answer length: {len(answer)} chars")
                            return answer
                    except Exception as e:
                        print(f"[LLM] T5 prompt failed: {e}")
                        continue
                
                # If all prompts fail or generate repetitive text, return a generic response
                total_time = time.time() - start_time
                print(f"[LLM] All T5 prompts failed, total time: {total_time:.1f}s")
                return "Kechirasiz, bu savolga umumiy bilimim yetarli emas. Dars materiallariga oid savollar bering."
            else:
                # Use Llama/GPT-style prompt for general knowledge
                prompt = f"""Siz o'zbek tilidagi savollarga javob beruvchi yordamchi assistentsiz.
Savolga aniq va foydali javob bering.

Savol: {question}

Javob:"""

                prompt_length = len(prompt.split())
                print(f"[LLM] Using Llama-style prompt (length: {prompt_length} words)")
                
                # Generate answer with progress monitoring
                inference_start = time.time()
                print(f"[LLM] {time.strftime('%H:%M:%S')} - Starting Llama inference...")
                
                # Start a progress monitoring thread
                import threading
                stop_progress = threading.Event()
                
                def progress_monitor():
                    elapsed = 0
                    while not stop_progress.is_set():
                        time.sleep(30)  # Check every 30 seconds
                        elapsed += 30
                        print(f"[LLM] {time.strftime('%H:%M:%S')} - Still generating... ({elapsed}s elapsed)")
                        if elapsed > 600:  # 10 minutes
                            print(f"[LLM] {time.strftime('%H:%M:%S')} - WARNING: Generation taking very long (>10min)")
                
                progress_thread = threading.Thread(target=progress_monitor, daemon=True)
                progress_thread.start()
                
                try:
                    outputs = self.pipe(
                        prompt,
                        max_new_tokens=self.max_new_tokens,
                        temperature=self.temperature,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                finally:
                    stop_progress.set()
                    progress_thread.join(timeout=1)
                
                inference_time = time.time() - inference_start
                print(f"[LLM] {time.strftime('%H:%M:%S')} - Llama inference completed in {inference_time:.1f}s")

                # Extract the generated answer
                generated_text = outputs[0]['generated_text']
                answer = generated_text[len(prompt):].strip()

                # # Clean up the answer (remove any extra content after the answer)
                # if "\n\n" in answer:
                #     answer = answer.split("\n\n")[0]

                total_time = time.time() - start_time
                print(f"[LLM] Total generation time: {total_time:.1f}s")
                print(f"[LLM] Generated answer length: {len(answer)} chars")

                return answer

        except Exception as e:
            total_time = time.time() - start_time
            print(f"[LLM] ERROR after {total_time:.1f}s: {e}")
            logger.error(f"❌ Failed to generate general knowledge answer: {e}")
            return "Kechirasiz, javob generatsiya qilishda xatolik yuz berdi."

    # def _try_basic_fallbacks(self, question: str) -> str:
    #     """
    #     Try basic fallback responses for common question types.
        
    #     Args:
    #         question: User's question
            
    #     Returns:
    #         Answer string if fallback found, empty string otherwise
    #     """
    #     question_lower = question.lower()
        
    #     # Basic country information - Uzbekistan
    #     if "o'zbekiston" in question_lower or "ozbekiston" in question_lower:
    #         if any(word in question_lower for word in ["prezident", "prezidenti", "kim"]):
    #             return "O'zbekiston Respublikasining prezidenti Shavkat Mirziyoyev."
            
    #         if any(word in question_lower for word in ["poytaxt", "poytaxti"]):
    #             return "O'zbekiston poytaxti - Toshkent shahri."
                
    #         if any(word in question_lower for word in ["aholi", "populyatsiya", "aholisi"]):
    #             return "O'zbekiston aholisi taxminan 35 million kishi."
                
    #         # Geography - Area
    #         if any(word in question_lower for word in ["maydon", "hudud", "hududi", "yer", "qancha", "necha"]):
    #             return "O'zbekiston maydoni 448,978 kvadrat kilometr."
                
    #         if any(word in question_lower for word in ["qo'shni", "chegaradosh", "qo'shnilari"]):
    #             return "O'zbekiston qo'shni davlatlari: Qozog'iston, Qirg'iziston, Tojikiston, Turkmaniston va Afg'oniston."
            
    #     # Basic animal information
    #     if "fil" in question_lower and any(word in question_lower for word in ["og'irlik", "vazn", "qancha", "necha"]):
    #         return "Afrika fili og'irligi 4,000-7,000 kg, Osiyo fili esa 2,000-5,000 kg bo'lishi mumkin."
            
    #     if "sher" in question_lower and any(word in question_lower for word in ["og'irlik", "vazn", "qancha", "necha"]):
    #         return "Erkak sher og'irligi 150-250 kg, urg'ochi sher esa 120-180 kg bo'ladi."
            
    #     # Basic math constants
    #     if "pi" in question_lower or "п" in question_lower:
    #         return "Pi (π) soni taxminan 3.14159 ga teng. Bu doira uzunligini diametriga nisbati."
            
    #     # Time/date questions
    #     if any(word in question_lower for word in ["yil", "yili"]) and any(word in question_lower for word in ["hozir", "bugun", "jori"]):
    #         from datetime import datetime
    #         current_year = datetime.now().year
    #         return f"Hozir {current_year}-yil."
            
    #     # Basic science/math questions
    #     if "yer" in question_lower and any(word in question_lower for word in ["quyosh", "kun"]) and any(word in question_lower for word in ["masofa", "uzoq", "qancha"]):
    #         return "Yer Quyoshdan o'rtacha masofasi 149.6 million kilometr."
            
    #     if "yer" in question_lower and any(word in question_lower for word in ["aylan", "davr", "qancha"]):
    #         return "Yer Quyosh atrofida bir marta aylanishi uchun 365 kun 6 soat kerak bo'ladi."
            
    #     # Basic math questions
    #     if any(word in question_lower for word in ["kun", "soat"]) and any(word in question_lower for word in ["necha", "qancha"]):
    #         return "Bir kunda 24 soat bor."
            
    #     if any(word in question_lower for word in ["hafta", "haftada"]) and any(word in question_lower for word in ["kun", "necha"]):
    #         return "Bir haftada 7 kun bor."
            
    #     if any(word in question_lower for word in ["yil", "yilda"]) and any(word in question_lower for word in ["oy", "necha"]):
    #         return "Bir yilda 12 oy bor."
            
    #     # Simple multiplication
    #     if "yetti" in question_lower and "sakkiz" in question_lower and any(word in question_lower for word in ["necha", "teng", "qancha"]):
    #         return "7 karra 8 ga 56 ga teng."
            
    #     if "olti" in question_lower and "to'qqiz" in question_lower and any(word in question_lower for word in ["necha", "teng", "qancha"]):
    #         return "6 karra 9 ga 54 ga teng."
            
    #     # Common animals
    #     if any(word in question_lower for word in ["orgimchak", "o'rgimchak"]) and any(word in question_lower for word in ["oyoq", "necha", "qancha"]):
    #         return "O'rgimchaklarning 8 ta oyoqlari bor."
            
    #     if any(word in question_lower for word in ["qurt", "chervyak"]) and any(word in question_lower for word in ["oyoq", "necha"]):
    #         return "Qurtlarning oyoqlari yo'q, ular sudralib harakat qiladi."
            
    #     # Basic subjects
    #     if "algebr" in question_lower and any(word in question_lower for word in ["nima", "nimani"]):
    #         return "Algebra - bu matematikaning bir bo'limi bo'lib, harflar va raqamlardan foydalangan holda ifodalarni hal qilishni o'rganadi."
            
    #     if "geometriya" in question_lower and any(word in question_lower for word in ["nima", "nimani"]):
    #         return "Geometriya - bu matematikaning shakllar, o'lchamlar va ularning xossalari haqidagi fan."
            
    #     # Basic science
    #     if "fotosintez" in question_lower and any(word in question_lower for word in ["nima", "qanday"]):
    #         return "Fotosintez - bu o'simliklar quyosh nuri yordamida uglerod dioksid va suvdan oziq modda (glyukoza) va kislorod ishlab chiqarish jarayoni."

    def _is_repeating_question(self, question: str, answer: str) -> bool:
        """
        Check if the answer is just repeating the question.
        
        Args:
            question: Original question
            answer: Generated answer
            
        Returns:
            True if answer is just repeating the question
        """
        question_lower = question.lower().strip('?.,!')
        answer_lower = answer.lower().strip()
        
        # Check if answer contains most of the question
        question_words = set(question_lower.split())
        answer_words = set(answer_lower.split())
        
        if len(question_words) == 0:
            return False
            
        overlap = len(question_words.intersection(answer_words))
        overlap_ratio = overlap / len(question_words)
        
        return overlap_ratio > 0.7  # If more than 70% of question words are in answer

    def _is_repetitive_text(self, text: str) -> bool:
        """
        Check if the text contains repetitive patterns that indicate model failure.
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be repetitive/nonsensical
        """
        if not text or len(text.strip()) < 10:
            return True
            
        text_lower = text.lower().strip()
        
        # Check for very short repetitive units (like "edward s." repeated)
        words = text_lower.split()
        if len(words) < 3:
            return False
            
        # Look for repetitive patterns
        # Check if the same word/phrase is repeated many times
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
            
        # If any word appears more than 10 times in a short text, it's likely repetitive
        max_repeats = max(word_counts.values())
        if max_repeats > 10 and len(words) < 50:
            return True
            
        # Check for repetitive phrases (like "st. john s. edward s." pattern)
        if len(words) > 20:
            # Check if first 5 words repeat in the text
            first_phrase = ' '.join(words[:5])
            if text_lower.count(first_phrase) > 3:
                return True
                
        # Check for nonsensical patterns (many short words repeating)
        short_words = [w for w in words if len(w) <= 3]
        if len(short_words) > len(words) * 0.8 and len(words) > 10:
            return True
            
        # Check if answer contains completely irrelevant content (like beetles when asking about algebra)
        irrelevant_indicators = ['beetle', 'genus', 'family', 'species', 'insect', 'animal', 'plant', 'chemical', 'physics', 'biology']
        if any(indicator in text_lower for indicator in irrelevant_indicators):
            return True

    def _is_irrelevant_answer(self, question: str, answer: str) -> bool:
        """
        Check if the answer contains content completely irrelevant to the question.
        
        Args:
            question: Original question
            answer: Generated answer
            
        Returns:
            True if answer appears to be irrelevant to the question
        """
        question_lower = question.lower()
        answer_lower = answer.lower()
        
        # Check for scientific/biological terms that don't match question topics
        irrelevant_indicators = ['beetle', 'genus', 'family', 'species', 'insect', 'animal', 'plant', 'chemical', 'physics', 'biology']
        
        if any(indicator in answer_lower for indicator in irrelevant_indicators):
            # Check if the question is about these topics
            question_topics = ['algebra', 'algebr', 'geometriya', 'geometry', 'fotosintez', 'photosynthesis', 
                             'orgimchak', 'spider', 'qurt', 'worm', 'matematika', 'math']
            if not any(topic in question_lower for topic in question_topics):
                return True
                
        return False

    def answer_question(
        self,
        question: str,
        lesson_id: str,
        use_llm: bool = True
    ) -> Tuple[str, bool, List[Document]]:
        """
        Answer a question using retrieval and optionally LLM.

        Args:
            question: User's question
            lesson_id: Lesson identifier
            use_llm: Whether to use LLM for answer generation

        Returns:
            Tuple of (answer, found_answer, retrieved_docs)
        """
        try:
            # Retrieve relevant documents
            docs = self.search_similar_documents(question, lesson_id)

            # Check if documents are actually relevant to the question
            relevant_docs = self._filter_relevant_documents(question, docs)

            if not use_llm:
                if relevant_docs:
                    # Return the most relevant document content
                    answer = relevant_docs[0].page_content[:500] + "..." if len(relevant_docs[0].page_content) > 500 else relevant_docs[0].page_content
                    return answer, True, relevant_docs
                else:
                    return "Bu dars uchun tegishli ma'lumot topilmadi.", False, []

            # Generate answer with LLM
            if relevant_docs:
                # Use retrieved context for lesson-specific questions
                answer = self.generate_answer_with_context(question, relevant_docs)
                return answer, True, relevant_docs
            else:
                # Fall back to general knowledge for non-lesson questions
                answer = self.generate_answer_general_knowledge(question)
                return answer, True, []

        except Exception as e:
            logger.error(f"❌ Failed to answer question: {e}")
            return "Savolga javob berishda xatolik yuz berdi.", False, []

    def _filter_relevant_documents(self, question: str, docs: List[Document], min_relevance_score: float = 0.5) -> List[Document]:
        """
        Filter documents based on relevance to the question.

        Args:
            question: User's question
            docs: Retrieved documents
            min_relevance_score: Minimum relevance score (0-1)

        Returns:
            Filtered list of relevant documents
        """
        if not docs:
            return []

        # Extract key terms from question (simple approach)
        question_lower = question.lower()
        key_terms = []
        
        # Common Uzbek question words to ignore
        ignore_words = {'nima', 'qanday', 'qayerda', 'qachon', 'kim', 'necha', 'qancha', 'qaysi', 'bu', 'shu', 'va', 'bilan', 'dan', 'ga', 'ni', 'ning', 'da', 'ta', 'chi', 'edi', 'ekan', 'mikan', 'mi', 'mu'}
        
        # Split question and filter out common words
        words = question_lower.split()
        for word in words:
            word = word.strip('.,!?')
            if len(word) > 2 and word not in ignore_words:
                key_terms.append(word)

        # If question has very few key terms, be more lenient
        if len(key_terms) <= 1:
            min_relevance_score = 0.2
        elif len(key_terms) >= 3:
            min_relevance_score = 0.8  # Stricter for questions with many key terms
        elif any(word in question_lower for word in ['kim', 'qayerda', 'qachon', 'qanday', 'necha', 'qancha']):
            min_relevance_score = 0.95  # Very strict for specific fact questions

        relevant_docs = []
        for doc in docs:
            doc_text = doc.page_content.lower()
            relevance_score = 0
            
            # Count how many key terms appear in the document
            matches = 0
            total_terms = len(key_terms)
            
            if total_terms == 0:
                relevance_score = 0.5  # Default relevance if no key terms
            else:
                for term in key_terms:
                    if term in doc_text:
                        matches += 1
                
                # Calculate relevance score
                relevance_score = matches / total_terms
                
                # Bonus for consecutive matches (phrases)
                question_phrase = ' '.join(key_terms)
                if question_phrase in doc_text:
                    relevance_score += 0.3
            
            if relevance_score >= min_relevance_score:
                relevant_docs.append(doc)

        return relevant_docs

    def get_lesson_statistics(self, lesson_id: str) -> Dict[str, Any]:
        """
        Get statistics about a lesson's vector store.

        Args:
            lesson_id: Lesson identifier

        Returns:
            Dictionary with lesson statistics
        """
        if lesson_id not in self.vector_stores:
            # Try to load from disk
            load_path = f"vector_stores/{lesson_id}"
            if os.path.exists(load_path):
                try:
                    self.load_vector_store(lesson_id, load_path)
                except Exception as e:
                    return {"error": f"Failed to load lesson {lesson_id}: {e}"}
            else:
                return {"error": f"Lesson {lesson_id} not found"}

        try:
            vector_store = self.vector_stores[lesson_id]

            if self.vector_store_type == "faiss":
                # Get FAISS index info
                index = vector_store.index
                num_vectors = index.ntotal
            else:
                # For Chroma, we can't easily get the count
                num_vectors = "unknown"

            return {
                "lesson_id": lesson_id,
                "vector_store_type": self.vector_store_type,
                "num_documents": num_vectors,
                "embedding_model": self.embedding_model_name,
                "llm_model": self.model_name
            }

        except Exception as e:
            return {"error": str(e)}

    def save_vector_store(self, lesson_id: str, save_path: str):
        """
        Save vector store to disk.

        Args:
            lesson_id: Lesson identifier
            save_path: Path to save the vector store
        """
        if lesson_id not in self.vector_stores:
            logger.warning(f"Vector store for lesson {lesson_id} not found")
            return

        try:
            vector_store = self.vector_stores[lesson_id]
            vector_store.save_local(save_path)
            logger.info(f"Saved vector store for lesson {lesson_id} to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")

    def load_vector_store(self, lesson_id: str, load_path: str):
        """
        Load vector store from disk.

        Args:
            lesson_id: Lesson identifier
            load_path: Path to load the vector store from
        """
        try:
            if self.vector_store_type == "faiss":
                self.vector_stores[lesson_id] = FAISS.load_local(
                    load_path, self.embedding_model, allow_dangerous_deserialization=True
                )
            elif self.vector_store_type == "chroma":
                self.vector_stores[lesson_id] = Chroma(
                    persist_directory=load_path,
                    embedding_function=self.embedding_model,
                    collection_name=f"lesson_{lesson_id}"
                )

            logger.info(f"Loaded vector store for lesson {lesson_id} from {load_path}")
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models."""
        return {
            "llm_model": self.model_name,
            "embedding_model": self.embedding_model_name,
            "device": self.device,
            "vector_store_type": self.vector_store_type,
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "k_documents": self.k_documents,
            "lessons_prepared": list(self.vector_stores.keys())
        }


def create_uzbek_llm_qa_service(
    model_name: str = None,  # If None, loads from backend/llm_config.py
    device: str = "auto"
) -> UzbekLLMQAService:
    """
    Create an instance of UzbekLLMQAService with default settings.
    
    Model configuration is loaded from backend/llm_config.py
    To change the model, edit the CURRENT_LLM_MODEL in that file.

    Args:
        model_name: LLM model name (if None, uses config from llm_config.py)
        device: Device to run on

    Returns:
        Configured UzbekLLMQAService instance
    """
    return UzbekLLMQAService(
        model_name=model_name,
        device=device,
        vector_store_type="faiss",  # FAISS is faster for this use case
        k_documents=3
    )


if __name__ == "__main__":
    # Example usage
    print("=" * 70)
    print("🤖 Uzbek LLM QA Service")
    print("=" * 70)
    
    # Show current configuration
    try:
        from backend.llm_config import print_config
        print_config()
    except ImportError:
        print("⚠️  backend/llm_config.py not found, using defaults")

    # Test model loading
    print("\n🔄 Initializing service...")
    try:
        service = create_uzbek_llm_qa_service()
        info = service.get_model_info()
        print(f"✅ Service initialized successfully!")
        print(f"   Model: {info['llm_model']}")
        print(f"   Device: {info['device']}")
        print(f"   Embedding: {info['embedding_model']}")
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        print("💡 Tip: Check if all dependencies are installed (pip install -r requirements.txt)")
