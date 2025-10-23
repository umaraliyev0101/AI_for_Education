"""
Uzbek NLP QA Service
Question-Answering system using local LLM and RAG (Retrieval Augmented Generation)
"""

import os
import json
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path

# Vector store and embeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# LLM imports (multiple options)
try:
    from langchain_community.llms import LlamaCpp
    LLAMACPP_AVAILABLE = True
except ImportError:
    LLAMACPP_AVAILABLE = False

try:
    from langchain_community.llms import HuggingFacePipeline
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Chains and prompts
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

from utils.uzbek_materials_processor import UzbekMaterialsProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UzbekQAService:
    """
    Question-Answering service for educational materials in Uzbek.
    Uses RAG (Retrieval Augmented Generation) with local LLM.
    """
    
    def __init__(
        self,
        model_type: str = "huggingface",  # "llamacpp" or "huggingface"
        model_path: Optional[str] = None,
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        vector_store_type: str = "faiss",  # "faiss" or "chroma"
        vector_store_path: Optional[str] = None,
        k_documents: int = 3
    ):
        """
        Initialize the QA service.
        
        Args:
            model_type: Type of LLM to use ("llamacpp" or "huggingface")
            model_path: Path to the LLM model
            embedding_model: Name or path of the embedding model
            vector_store_type: Type of vector store ("faiss" or "chroma")
            vector_store_path: Path to save/load vector store
            k_documents: Number of documents to retrieve for context
        """
        self.model_type = model_type
        self.model_path = model_path
        self.k_documents = k_documents
        self.vector_store_type = vector_store_type
        self.vector_store_path = vector_store_path or "./vector_stores"
        
        # Initialize materials processor
        self.materials_processor = UzbekMaterialsProcessor()
        
        # Initialize embeddings
        logger.info(f"Embedding modeli yuklanmoqda: {embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize LLM
        self.llm = None
        self._initialize_llm()
        
        # Vector stores cache (lesson_id -> vector_store)
        self.vector_stores: Dict[str, any] = {}
        
        # Create prompt template in Uzbek
        self.prompt_template = """Siz o'quv materiallariga asoslangan savollarga javob beradigan AI yordamchisiz.
        
Quyidagi kontekst ma'lumotlaridan foydalanib, savolga aniq va qisqa javob bering.
Agar kontekstda javob bo'lmasa, "Kechirasiz, bu savol bo'yicha ma'lumot topa olmadim" deb javob bering.

Kontekst:
{context}

Savol: {question}

Javob (o'zbek tilida):"""

        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )
    
    def _initialize_llm(self):
        """Initialize the language model based on configuration."""
        if self.model_type == "llamacpp" and LLAMACPP_AVAILABLE:
            self._initialize_llamacpp()
        elif self.model_type == "huggingface" and TRANSFORMERS_AVAILABLE:
            self._initialize_huggingface()
        else:
            logger.warning("LLM yuklanmadi. Faqat retrieval rejimida ishlaydi.")
    
    def _initialize_llamacpp(self):
        """Initialize LlamaCpp model."""
        if not self.model_path or not os.path.exists(self.model_path):
            logger.error(f"LlamaCpp model fayli topilmadi: {self.model_path}")
            return
        
        try:
            logger.info(f"LlamaCpp modeli yuklanmoqda: {self.model_path}")
            self.llm = LlamaCpp(
                model_path=self.model_path,
                temperature=0.3,
                max_tokens=512,
                n_ctx=2048,
                n_batch=512,
                verbose=False
            )
            logger.info("LlamaCpp modeli muvaffaqiyatli yuklandi")
        except Exception as e:
            logger.error(f"LlamaCpp modelini yuklashda xatolik: {str(e)}")
    
    def _initialize_huggingface(self):
        """Initialize HuggingFace model."""
        # Default to a small multilingual model if no path specified
        model_name = self.model_path or "google/flan-t5-base"
        
        try:
            logger.info(f"HuggingFace modeli yuklanmoqda: {model_name}")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                low_cpu_mem_usage=True
            )
            
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=512,
                temperature=0.3,
                do_sample=True
            )
            
            self.llm = HuggingFacePipeline(pipeline=pipe)
            logger.info("HuggingFace modeli muvaffaqiyatli yuklandi")
        except Exception as e:
            logger.error(f"HuggingFace modelini yuklashda xatolik: {str(e)}")
    
    def create_vector_store(
        self,
        documents: List[Dict[str, str]],
        lesson_id: str
    ) -> any:
        """
        Create a vector store from processed documents.
        
        Args:
            documents: List of document dictionaries with 'text' and metadata
            lesson_id: Unique identifier for the lesson
            
        Returns:
            Vector store object
        """
        if not documents:
            logger.warning("Hujjatlar ro'yxati bo'sh")
            return None
        
        # Convert to LangChain Document objects
        langchain_docs = [
            Document(
                page_content=doc['text'],
                metadata={
                    'source': doc.get('source', 'unknown'),
                    'chunk_id': doc.get('chunk_id', 0),
                    'lesson_id': lesson_id
                }
            )
            for doc in documents
        ]
        
        logger.info(f"Vector store yaratilmoqda: {len(langchain_docs)} hujjat")
        
        try:
            if self.vector_store_type == "faiss":
                vector_store = FAISS.from_documents(langchain_docs, self.embeddings)
                
                # Save to disk
                store_path = os.path.join(self.vector_store_path, f"faiss_{lesson_id}")
                os.makedirs(store_path, exist_ok=True)
                vector_store.save_local(store_path)
                logger.info(f"FAISS vector store saqlandi: {store_path}")
                
            elif self.vector_store_type == "chroma":
                persist_directory = os.path.join(self.vector_store_path, f"chroma_{lesson_id}")
                vector_store = Chroma.from_documents(
                    langchain_docs,
                    self.embeddings,
                    persist_directory=persist_directory
                )
                vector_store.persist()
                logger.info(f"Chroma vector store saqlandi: {persist_directory}")
            
            else:
                raise ValueError(f"Noto'g'ri vector store turi: {self.vector_store_type}")
            
            # Cache the vector store
            self.vector_stores[lesson_id] = vector_store
            return vector_store
            
        except Exception as e:
            logger.error(f"Vector store yaratishda xatolik: {str(e)}")
            return None
    
    def load_vector_store(self, lesson_id: str) -> Optional[any]:
        """
        Load a previously saved vector store.
        
        Args:
            lesson_id: Unique identifier for the lesson
            
        Returns:
            Vector store object or None
        """
        # Check cache first
        if lesson_id in self.vector_stores:
            logger.info(f"Vector store keshdan yuklandi: {lesson_id}")
            return self.vector_stores[lesson_id]
        
        try:
            if self.vector_store_type == "faiss":
                store_path = os.path.join(self.vector_store_path, f"faiss_{lesson_id}")
                if os.path.exists(store_path):
                    vector_store = FAISS.load_local(
                        store_path, 
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                    self.vector_stores[lesson_id] = vector_store
                    logger.info(f"FAISS vector store yuklandi: {store_path}")
                    return vector_store
                    
            elif self.vector_store_type == "chroma":
                persist_directory = os.path.join(self.vector_store_path, f"chroma_{lesson_id}")
                if os.path.exists(persist_directory):
                    vector_store = Chroma(
                        persist_directory=persist_directory,
                        embedding_function=self.embeddings
                    )
                    self.vector_stores[lesson_id] = vector_store
                    logger.info(f"Chroma vector store yuklandi: {persist_directory}")
                    return vector_store
            
            logger.warning(f"Vector store topilmadi: {lesson_id}")
            return None
            
        except Exception as e:
            logger.error(f"Vector store yuklashda xatolik: {str(e)}")
            return None
    
    def prepare_lesson_materials(
        self,
        file_paths: List[str],
        lesson_id: str,
        force_rebuild: bool = False
    ) -> bool:
        """
        Prepare lesson materials by processing files and creating vector store.
        
        Args:
            file_paths: List of material file paths
            lesson_id: Unique identifier for the lesson
            force_rebuild: Force rebuild even if vector store exists
            
        Returns:
            Success status
        """
        # Check if vector store already exists
        if not force_rebuild and self.load_vector_store(lesson_id):
            logger.info(f"Vector store allaqachon mavjud: {lesson_id}")
            return True
        
        logger.info(f"Dars materiallari tayyorlanmoqda: {lesson_id}")
        
        # Process materials
        documents = self.materials_processor.process_materials(file_paths)
        
        if not documents:
            logger.error("Hujjatlar qayta ishlanmadi")
            return False
        
        # Create vector store
        vector_store = self.create_vector_store(documents, lesson_id)
        
        return vector_store is not None
    
    def search_similar_documents(
        self,
        query: str,
        lesson_id: str,
        k: Optional[int] = None
    ) -> List[Document]:
        """
        Search for similar documents using semantic search.
        
        Args:
            query: Search query
            lesson_id: Lesson identifier
            k: Number of documents to return (default: self.k_documents)
            
        Returns:
            List of relevant documents
        """
        k = k or self.k_documents
        
        # Load vector store
        vector_store = self.load_vector_store(lesson_id)
        if not vector_store:
            logger.warning(f"Vector store topilmadi: {lesson_id}")
            return []
        
        try:
            # Similarity search
            docs = vector_store.similarity_search(query, k=k)
            logger.info(f"{len(docs)} tegishli hujjat topildi")
            return docs
        except Exception as e:
            logger.error(f"Qidirishda xatolik: {str(e)}")
            return []
    
    def answer_question(
        self,
        question: str,
        lesson_id: str,
        use_llm: bool = True
    ) -> Tuple[str, bool, List[Document]]:
        """
        Answer a question based on lesson materials.
        
        Args:
            question: User's question
            lesson_id: Lesson identifier
            use_llm: Whether to use LLM for generation (if False, returns context only)
            
        Returns:
            Tuple of (answer, found_answer, source_documents)
        """
        logger.info(f"Savol: {question}")
        
        # Search for relevant documents
        docs = self.search_similar_documents(question, lesson_id)
        
        if not docs:
            return "Kechirasiz, bu savol bo'yicha ma'lumot topa olmadim.", False, []
        
        # If LLM is not available or not requested, return context only
        if not use_llm or not self.llm:
            context = "\n\n".join([doc.page_content for doc in docs])
            answer = f"Topilgan ma'lumot:\n\n{context[:500]}..."
            return answer, True, docs
        
        try:
            # Use LLM with retrieved context (simple implementation)
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create prompt with context and question
            prompt_text = self.prompt.format(context=context, question=question)
            
            # Get answer from LLM
            answer = self.llm(prompt_text).strip()
            
            # Check if answer was found (basic heuristic)
            found = len(docs) > 0 and len(answer) > 20
            
            logger.info(f"Javob: {answer[:100]}...")
            return answer, found, docs
            
        except Exception as e:
            logger.error(f"Javob berishda xatolik: {str(e)}")
            # Fallback to context-only answer
            context = "\n\n".join([doc.page_content for doc in docs])
            return f"Topilgan ma'lumot:\n\n{context[:500]}...", True, docs
    
    def get_lesson_statistics(self, lesson_id: str) -> Dict:
        """
        Get statistics about a lesson's vector store.
        
        Args:
            lesson_id: Lesson identifier
            
        Returns:
            Dictionary with statistics
        """
        vector_store = self.load_vector_store(lesson_id)
        if not vector_store:
            return {"error": "Vector store topilmadi"}
        
        try:
            if self.vector_store_type == "faiss":
                num_docs = vector_store.index.ntotal
            elif self.vector_store_type == "chroma":
                num_docs = vector_store._collection.count()
            else:
                num_docs = 0
            
            return {
                "lesson_id": lesson_id,
                "num_documents": num_docs,
                "vector_store_type": self.vector_store_type,
                "embedding_model": self.embeddings.model_name
            }
        except Exception as e:
            logger.error(f"Statistika olishda xatolik: {str(e)}")
            return {"error": str(e)}


if __name__ == "__main__":
    # Example usage
    print("Uzbek NLP QA Service tayyor!")
    print("Misol:")
    print("  qa_service = UzbekQAService()")
    print("  qa_service.prepare_lesson_materials(['dars1.pdf', 'dars1.pptx'], 'lesson_001')")
    print("  answer, found, docs = qa_service.answer_question('Pythonda funksiya nima?', 'lesson_001')")
