# 🤖 Quick Model Change Guide

## Changed to Lightweight Model! ✅

The system now uses **`google/flan-t5-base`** by default instead of Llama.

### Why?
- ✅ **Much smaller**: ~250MB vs ~16GB
- ✅ **Faster**: Works great on CPU
- ✅ **No GPU needed**: Perfect for testing
- ✅ **Quick download**: ~30 seconds vs ~30 minutes

---

## How to Change Models

### Option 1: Quick Edit (1 minute)

1. Open **`backend/llm_config.py`**
2. Uncomment your preferred model:

```python
# For testing (current)
CURRENT_LLM_MODEL = "google/flan-t5-base"  # ✅

# For better quality
# CURRENT_LLM_MODEL = "google/flan-t5-large"

# For production (Uzbek)
# CURRENT_LLM_MODEL = "behbudiy/Llama-3.1-8B-Instruct-Uz"
```

3. Restart backend server

### Option 2: Read Full Guide

See **`docs/MODEL_CONFIGURATION.md`** for:
- Complete model comparison
- System requirements
- Performance benchmarks
- Troubleshooting

---

## Available Models

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| flan-t5-base ✅ | 250MB | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | Testing |
| flan-t5-large | 1GB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Development |
| flan-t5-xl | 3GB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Production |
| Llama-Uz | 16GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Uzbek Production |

---

## Quick Test

```bash
# Check current configuration
python backend/llm_config.py

# Test the Q&A system
python test_qa_system.py
```

---

## Files Changed

✅ `utils/uzbek_llm_qa_service.py` - Updated to use config file  
✅ `backend/llm_config.py` - New centralized config  
✅ `backend/routes/qa.py` - Updated comments  
✅ `test_qa_system.py` - Updated comments  
✅ `docs/BACKEND_IMPROVEMENTS.md` - Updated model info  
✅ `docs/MODEL_CONFIGURATION.md` - New complete guide  
✅ `docs/DOCUMENTATION_INDEX.md` - Added model config section

---

## Need Help?

📖 **Full Guide**: `docs/MODEL_CONFIGURATION.md`  
⚙️ **Config File**: `backend/llm_config.py`  
🧪 **Test**: `python test_qa_system.py`

---

**Current Model**: google/flan-t5-base (~250MB)  
**Perfect for**: Frontend/Backend testing and integration
