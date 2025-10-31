# 🤖 LLM Model Configuration Guide

## Quick Model Change

To change the LLM model, edit **`backend/llm_config.py`** and uncomment your preferred model:

```python
# Current selection (uncomment one):
CURRENT_LLM_MODEL = "google/flan-t5-base"  # ✅ For testing
# CURRENT_LLM_MODEL = "google/flan-t5-large"  # Better quality
# CURRENT_LLM_MODEL = "behbudiy/Llama-3.1-8B-Instruct-Uz"  # Production
```

That's it! No other files need to be changed.

---

## 📋 Available Models

### 🚀 Testing & Development

#### 1. **google/flan-t5-base** (CURRENT) ⭐ RECOMMENDED
- **Size**: ~250MB
- **Speed**: ⚡⚡⚡⚡⚡ Very Fast
- **Quality**: ⭐⭐⭐ Good
- **Memory**: ~1GB RAM
- **Best for**: Testing, development, CPU-only machines
- **Download time**: ~30 seconds

```python
CURRENT_LLM_MODEL = "google/flan-t5-base"
```

#### 2. **google/flan-t5-large**
- **Size**: ~1GB
- **Speed**: ⚡⚡⚡⚡ Fast
- **Quality**: ⭐⭐⭐⭐ Very Good
- **Memory**: ~2GB RAM
- **Best for**: Better quality on decent hardware
- **Download time**: ~2 minutes

```python
CURRENT_LLM_MODEL = "google/flan-t5-large"
```

#### 3. **google/flan-t5-xl**
- **Size**: ~3GB
- **Speed**: ⚡⚡⚡ Medium
- **Quality**: ⭐⭐⭐⭐⭐ Excellent
- **Memory**: ~4GB RAM
- **Best for**: Production-ready quality
- **Download time**: ~5 minutes

```python
CURRENT_LLM_MODEL = "google/flan-t5-xl"
```

---

### 🎯 Production Models

#### 4. **behbudiy/Llama-3.1-8B-Instruct-Uz** (Uzbek Optimized)
- **Size**: ~16GB
- **Speed**: ⚡⚡ Slow on CPU, Fast on GPU
- **Quality**: ⭐⭐⭐⭐⭐ Excellent for Uzbek
- **Memory**: ~8GB VRAM (GPU) or 16GB+ RAM (CPU)
- **Best for**: Production with Uzbek language focus
- **Requirements**: GPU with 8GB+ VRAM recommended
- **Download time**: ~30 minutes

```python
CURRENT_LLM_MODEL = "behbudiy/Llama-3.1-8B-Instruct-Uz"
```

#### 5. **meta-llama/Llama-2-7b-chat-hf**
- **Size**: ~13GB
- **Speed**: ⚡⚡ Requires GPU
- **Quality**: ⭐⭐⭐⭐⭐ Excellent general purpose
- **Memory**: ~7GB VRAM
- **Best for**: Multilingual production with GPU
- **Requirements**: Requires HuggingFace authentication
- **Download time**: ~20 minutes

```python
CURRENT_LLM_MODEL = "meta-llama/Llama-2-7b-chat-hf"
```

---

## 🔧 How to Change Models

### Step 1: Edit Configuration
```bash
# Open the config file
code backend/llm_config.py
```

### Step 2: Uncomment Your Choice
```python
# Comment out current model
# CURRENT_LLM_MODEL = "google/flan-t5-base"

# Uncomment your preferred model
CURRENT_LLM_MODEL = "google/flan-t5-large"
```

### Step 3: Restart Server
```bash
# The new model will be downloaded automatically on first use
cd backend
python -m uvicorn main:app --reload
```

---

## 💡 Model Selection Guide

### For Testing/Development
👉 **Use: google/flan-t5-base** (current)
- Fast download
- Works on any machine
- Good enough for testing features
- No GPU required

### For Better Quality (Still Testing)
👉 **Use: google/flan-t5-large**
- Significantly better answers
- Still manageable size
- Works on CPU
- Good compromise

### For Production (Uzbek Language)
👉 **Use: behbudiy/Llama-3.1-8B-Instruct-Uz**
- Best Uzbek language understanding
- Requires GPU
- Large download
- Worth it for production

### For Production (Multilingual)
👉 **Use: google/flan-t5-xl or Llama-2-7b-chat**
- Great general purpose
- Good multilingual support
- Excellent quality

---

## 🖥️ System Requirements

### Minimum (for flan-t5-base)
- **CPU**: Any modern CPU
- **RAM**: 4GB
- **Storage**: 1GB free
- **GPU**: Not required

### Recommended (for flan-t5-large)
- **CPU**: 4+ cores
- **RAM**: 8GB
- **Storage**: 5GB free
- **GPU**: Optional, helps with speed

### Production (for Llama models)
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 20GB free
- **GPU**: 8GB+ VRAM (NVIDIA)

---

## 📊 Performance Comparison

| Model | Size | CPU Speed | GPU Speed | Quality | Uzbek Support |
|-------|------|-----------|-----------|---------|---------------|
| flan-t5-base | 250MB | ⚡⚡⚡⚡⚡ | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | ⭐⭐⭐ |
| flan-t5-large | 1GB | ⚡⚡⚡⚡ | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| flan-t5-xl | 3GB | ⚡⚡⚡ | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Llama-Uz | 16GB | ⚡ | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Llama-2 | 13GB | ⚡ | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🔍 Testing Your Model

After changing the model, test it:

```bash
# Test the configuration
python backend/llm_config.py

# Test the Q&A system
python test_qa_system.py

# Or test directly
python -c "from utils.uzbek_llm_qa_service import create_uzbek_llm_qa_service; s = create_uzbek_llm_qa_service(); print('✅ Model loaded!')"
```

---

## 🚨 Troubleshooting

### Model Download Issues
```bash
# Clear HuggingFace cache if download fails
rm -rf ~/.cache/huggingface/

# Re-download
python test_qa_system.py
```

### Out of Memory
If you get OOM errors:
1. Switch to a smaller model (flan-t5-base)
2. Reduce MAX_NEW_TOKENS in llm_config.py
3. Close other applications
4. Restart your computer

### Slow Performance
If the model is too slow:
1. Use a smaller model
2. Reduce K_DOCUMENTS (fewer context docs)
3. Check if GPU is being used (DEVICE setting)

---

## 📝 Configuration File Location

```
AI_in_Education/
├── backend/
│   └── llm_config.py  ← EDIT THIS FILE
```

---

## ⚙️ Advanced Configuration

You can also customize other parameters in `llm_config.py`:

```python
# Generation parameters
MAX_NEW_TOKENS = 256  # Length of answers
TEMPERATURE = 0.7     # Creativity (0.0-1.0)

# RAG parameters
K_DOCUMENTS = 3       # Context documents to use
CHUNK_SIZE = 1000     # Text chunk size
```

---

## 💬 Need Help?

- **Model not downloading?** Check your internet connection
- **Out of memory?** Use a smaller model
- **Poor quality answers?** Try a larger model
- **Want Uzbek support?** Use behbudiy/Llama-3.1-8B-Instruct-Uz

---

**Current Model**: `google/flan-t5-base` ✅  
**Perfect for**: Testing and development  
**To change**: Edit `backend/llm_config.py`
