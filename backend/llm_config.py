"""
LLM Configuration
Centralized configuration for LLM models used in the application.
Easy switching between different models for testing and production.
"""

# ============================================================================
# LLM MODEL CONFIGURATION
# ============================================================================

# Current Model Selection (uncomment one)
# ----------------------------------------

# 🚀 OPTION 1: Lightweight Model (Recommended for Testing)
# ~250MB download, fast inference, good for development
# Works well on CPU, minimal memory requirements
# CURRENT_LLM_MODEL = "google/flan-t5-base"

# 🚀 OPTION 2: Better Quality (Medium)
# ~1GB download, better quality answers
# CURRENT_LLM_MODEL = "google/flan-t5-large"

# 🚀 OPTION 3: Best Quality (Large) 
# ~3GB download, highest quality
# CURRENT_LLM_MODEL = "google/flan-t5-xl"

# 🚀 OPTION 4: Production Model (Uzbek Language) ✅ ACTIVE
# ~16GB download, requires GPU with 8GB+ VRAM
# Best for Uzbek language understanding
CURRENT_LLM_MODEL = "behbudiy/Llama-3.1-8B-Instruct-Uz"

# 🚀 OPTION 5: General Purpose (Good multilingual support)
# ~13GB download, requires GPU
# CURRENT_LLM_MODEL = "meta-llama/Llama-2-7b-chat-hf"


# ============================================================================
# EMBEDDING MODEL CONFIGURATION
# ============================================================================

# Embedding model for RAG (text similarity)
# ~420MB download, works well for multilingual texts including Uzbek
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Alternative embedding models:
# EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Lighter, English-focused
# EMBEDDING_MODEL = "intfloat/multilingual-e5-small"  # Good multilingual support


# ============================================================================
# GENERATION PARAMETERS
# ============================================================================

# Device configuration
# "auto" - automatically select GPU if available, else CPU
# "cuda" - force GPU usage (will fail if no GPU)
# "cpu" - force CPU usage
DEVICE = "auto"

# Text generation parameters
MAX_NEW_TOKENS = 256  # Maximum length of generated answer
TEMPERATURE = 0.7     # Higher = more creative, Lower = more focused
TOP_P = 0.9          # Nucleus sampling parameter
TOP_K = 50           # Top-K sampling parameter

# RAG parameters
K_DOCUMENTS = 3      # Number of context documents to retrieve
CHUNK_SIZE = 1000    # Size of text chunks for processing
CHUNK_OVERLAP = 200  # Overlap between chunks


# ============================================================================
# MODEL COMPARISON
# ============================================================================

MODEL_COMPARISON = """
┌─────────────────────────────────────────────────────────────────────────┐
│ MODEL COMPARISON GUIDE                                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ 1. google/flan-t5-base (RECOMMENDED FOR TESTING) ✅                     │
│    Size: ~250MB                                                         │
│    Speed: ⚡⚡⚡⚡⚡ (Very Fast)                                         │
│    Quality: ⭐⭐⭐ (Good)                                              │
│    Memory: ~1GB RAM                                                     │
│    Best for: Development, testing, CPU-only machines                   │
│                                                                         │
│ 2. google/flan-t5-large                                                │
│    Size: ~1GB                                                           │
│    Speed: ⚡⚡⚡⚡ (Fast)                                                │
│    Quality: ⭐⭐⭐⭐ (Very Good)                                        │
│    Memory: ~2GB RAM                                                     │
│    Best for: Better quality on decent hardware                         │
│                                                                         │
│ 3. google/flan-t5-xl                                                   │
│    Size: ~3GB                                                           │
│    Speed: ⚡⚡⚡ (Medium)                                                │
│    Quality: ⭐⭐⭐⭐⭐ (Excellent)                                      │
│    Memory: ~4GB RAM                                                     │
│    Best for: Production with good CPU or basic GPU                     │
│                                                                         │
│ 4. behbudiy/Llama-3.1-8B-Instruct-Uz (UZBEK OPTIMIZED)                │
│    Size: ~16GB                                                          │
│    Speed: ⚡⚡ (Slow on CPU, Fast on GPU)                              │
│    Quality: ⭐⭐⭐⭐⭐ (Excellent for Uzbek)                           │
│    Memory: ~8GB VRAM (GPU) or 16GB+ RAM (CPU)                          │
│    Best for: Production with Uzbek language focus                      │
│                                                                         │
│ 5. meta-llama/Llama-2-7b-chat-hf                                       │
│    Size: ~13GB                                                          │
│    Speed: ⚡⚡ (Requires GPU)                                           │
│    Quality: ⭐⭐⭐⭐⭐ (Excellent general purpose)                      │
│    Memory: ~7GB VRAM                                                    │
│    Best for: Production with GPU, multilingual support                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

RECOMMENDATION:
  👉 For Testing/Development: Use flan-t5-base
  👉 For Production (Uzbek): Use Llama-3.1-8B-Instruct-Uz with GPU ✅ ACTIVE
  👉 For Production (General): Use flan-t5-xl or Llama-2-7b-chat
"""


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_llm_config():
    """Get current LLM configuration."""
    return {
        "model_name": CURRENT_LLM_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "device": DEVICE,
        "max_new_tokens": MAX_NEW_TOKENS,
        "temperature": TEMPERATURE,
        "k_documents": K_DOCUMENTS
    }


def print_config():
    """Print current configuration."""
    print("=" * 70)
    print("📊 CURRENT LLM CONFIGURATION")
    print("=" * 70)
    print(f"LLM Model:       {CURRENT_LLM_MODEL}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Device:          {DEVICE}")
    print(f"Max Tokens:      {MAX_NEW_TOKENS}")
    print(f"Temperature:     {TEMPERATURE}")
    print(f"K Documents:     {K_DOCUMENTS}")
    print("=" * 70)
    print(MODEL_COMPARISON)


if __name__ == "__main__":
    print_config()
