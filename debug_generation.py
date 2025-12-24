#!/usr/bin/env python3
"""
Debug script to identify LLM generation crash causes.

Usage:
    python debug_generation.py

This script tests each step of the generation pipeline and reports
memory usage and potential crash points.
"""

import torch
import gc
import traceback
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_gpu_memory():
    """Print current GPU memory usage."""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        free = total - reserved
        print(f"   GPU Memory: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved, {free:.2f}GB free, {total:.2f}GB total")
    else:
        print("   CUDA not available - running on CPU")


def print_system_info():
    """Print system and PyTorch info."""
    print(f"   Python: {sys.version}")
    print(f"   PyTorch: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   CUDA version: {torch.version.cuda}")
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   GPU count: {torch.cuda.device_count()}")


def clear_memory():
    """Clear GPU and CPU memory."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def main():
    print("=" * 70)
    print("LLM Generation Debug Script")
    print("=" * 70)
    
    print("\n[0] System Information")
    print("-" * 40)
    print_system_info()
    print_gpu_memory()
    
    # Step 1: Load config
    print("\n[1] Loading LLM configuration...")
    print("-" * 40)
    try:
        from backend.llm_config import CURRENT_LLM_MODEL, get_llm_config
        config = get_llm_config()
        print(f"   Model: {CURRENT_LLM_MODEL}")
        print(f"   Config: {config}")
    except Exception as e:
        print(f"   FAILED: {e}")
        traceback.print_exc()
        return False
    
    # Step 2: Load tokenizer
    print("\n[2] Loading tokenizer...")
    print("-" * 40)
    try:
        from transformers import AutoTokenizer
        
        tokenizer = AutoTokenizer.from_pretrained(CURRENT_LLM_MODEL)
        
        # Ensure pad_token is set
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            print("   Set pad_token = eos_token")
        
        print(f"   Tokenizer loaded successfully")
        print(f"   Vocab size: {tokenizer.vocab_size}")
        print(f"   EOS token: {tokenizer.eos_token} (id: {tokenizer.eos_token_id})")
        print(f"   PAD token: {tokenizer.pad_token} (id: {tokenizer.pad_token_id})")
    except Exception as e:
        print(f"   FAILED: {e}")
        traceback.print_exc()
        return False
    
    print_gpu_memory()
    
    # Step 3: Load model
    print("\n[3] Loading model...")
    print("-" * 40)
    print("   This may take a few minutes...")
    
    clear_memory()
    
    try:
        from transformers import AutoModelForCausalLM, BitsAndBytesConfig
        
        # Determine device and dtype
        if torch.cuda.is_available():
            device_map = "auto"
            torch_dtype = torch.float16
            print("   Using CUDA with float16")
            
            # Try 8-bit quantization if available
            try:
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                    llm_int8_threshold=6.0,
                )
                print("   8-bit quantization available")
                use_quantization = True
            except Exception:
                quantization_config = None
                use_quantization = False
                print("   8-bit quantization not available, using float16")
        else:
            device_map = None
            torch_dtype = torch.float32
            quantization_config = None
            use_quantization = False
            print("   Using CPU with float32 (will be slow!)")
        
        # Load model
        model_kwargs = {
            "torch_dtype": torch_dtype,
            "low_cpu_mem_usage": True,
            "trust_remote_code": True,
        }
        
        if device_map:
            model_kwargs["device_map"] = device_map
        
        # Don't use quantization for now to test baseline
        # if use_quantization and quantization_config:
        #     model_kwargs["quantization_config"] = quantization_config
        
        model = AutoModelForCausalLM.from_pretrained(
            CURRENT_LLM_MODEL,
            **model_kwargs
        )
        
        print(f"   Model loaded successfully")
        print(f"   Model type: {type(model).__name__}")
        if hasattr(model, 'device'):
            print(f"   Model device: {model.device}")
        if hasattr(model, 'dtype'):
            print(f"   Model dtype: {model.dtype}")
        
    except torch.cuda.OutOfMemoryError:
        print("   FAILED: CUDA Out of Memory during model loading!")
        print("   Try using 8-bit quantization or a smaller model")
        print_gpu_memory()
        return False
    except Exception as e:
        print(f"   FAILED: {e}")
        traceback.print_exc()
        return False
    
    print_gpu_memory()
    
    # Step 4: Test tokenization
    print("\n[4] Testing tokenization...")
    print("-" * 40)
    try:
        test_prompts = [
            "Savol: Toshkent qayerda joylashgan?\nJavob:",
            "Savol: O'zbekiston poytaxti qaysi shahar?\nJavob:",
            "Savol: 2 + 2 nechaga teng?\nJavob:",
        ]
        
        for i, prompt in enumerate(test_prompts):
            inputs = tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512,
                padding=True
            )
            print(f"   Prompt {i+1}: {len(prompt)} chars -> {inputs['input_ids'].shape[1]} tokens")
        
        # Use last prompt for generation test
        test_prompt = test_prompts[0]
        inputs = tokenizer(
            test_prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512,
            padding=True
        )
        
        # Move to device
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
            print(f"   Inputs moved to CUDA")
        
        print(f"   Tokenization successful")
        
    except Exception as e:
        print(f"   FAILED: {e}")
        traceback.print_exc()
        return False
    
    print_gpu_memory()
    
    # Step 5: Test generation (small)
    print("\n[5] Testing generation (max_new_tokens=20)...")
    print("-" * 40)
    
    clear_memory()
    
    try:
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=20,
                min_new_tokens=5,
                do_sample=False,  # Greedy for determinism
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True,
            )
        
        print(f"   Generation successful")
        print(f"   Output shape: {outputs.shape}")
        
        # Decode
        generated_ids = outputs[0][inputs['input_ids'].shape[1]:]
        answer = tokenizer.decode(generated_ids, skip_special_tokens=True)
        print(f"   Generated text: '{answer[:100]}...' ({len(answer)} chars)")
        
    except torch.cuda.OutOfMemoryError:
        print("   FAILED: CUDA Out of Memory during generation!")
        print_gpu_memory()
        print("\n   SUGGESTIONS:")
        print("   - Reduce max_new_tokens")
        print("   - Use 8-bit quantization")
        print("   - Use a smaller model (e.g., flan-t5-base)")
        return False
    except Exception as e:
        print(f"   FAILED: {e}")
        traceback.print_exc()
        return False
    
    print_gpu_memory()
    
    # Step 6: Test generation (larger)
    print("\n[6] Testing generation (max_new_tokens=100)...")
    print("-" * 40)
    
    clear_memory()
    
    try:
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                min_new_tokens=10,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True,
            )
        
        print(f"   Generation successful")
        print(f"   Output shape: {outputs.shape}")
        
        # Decode
        generated_ids = outputs[0][inputs['input_ids'].shape[1]:]
        answer = tokenizer.decode(generated_ids, skip_special_tokens=True)
        print(f"   Generated text: '{answer[:200]}...' ({len(answer)} chars)")
        
    except torch.cuda.OutOfMemoryError:
        print("   FAILED: CUDA Out of Memory during generation!")
        print_gpu_memory()
        return False
    except Exception as e:
        print(f"   FAILED: {e}")
        traceback.print_exc()
        return False
    
    print_gpu_memory()
    
    # Step 7: Test full pipeline
    print("\n[7] Testing full Q&A pipeline...")
    print("-" * 40)
    
    clear_memory()
    
    try:
        # Simulate full prompt with context
        full_prompt = """Siz o'zbek tilidagi savollarga javob beruvchi yordamchi assistentsiz.
Quyidagi kontekst ma'lumotlariga asosan savolga aniq va foydali javob bering.

Kontekst:
O'zbekiston Markaziy Osiyoda joylashgan davlat. Poytaxti Toshkent shahri.
Aholisi 35 million kishidan oshiq. Rasmiy tili o'zbek tili.

Savol: O'zbekiston poytaxti qaysi shahar?

Javob:"""
        
        inputs = tokenizer(
            full_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
            padding=True
        )
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        print(f"   Full prompt: {inputs['input_ids'].shape[1]} tokens")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                min_new_tokens=10,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True,
            )
        
        generated_ids = outputs[0][inputs['input_ids'].shape[1]:]
        answer = tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        print(f"   Full pipeline successful!")
        print(f"   Answer: '{answer}'")
        
    except torch.cuda.OutOfMemoryError:
        print("   FAILED: CUDA Out of Memory!")
        print_gpu_memory()
        return False
    except Exception as e:
        print(f"   FAILED: {e}")
        traceback.print_exc()
        return False
    
    print_gpu_memory()
    
    # Cleanup
    print("\n[8] Cleanup...")
    print("-" * 40)
    del model, tokenizer, inputs, outputs
    clear_memory()
    print("   Cleanup complete")
    print_gpu_memory()
    
    print("\n" + "=" * 70)
    print("SUCCESS! All generation tests passed.")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
