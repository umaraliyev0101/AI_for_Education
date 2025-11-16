"""
Complete Model Test Script
Tests model loading, text generation, and Q&A capabilities
"""

import sys
import os
import time
from datetime import datetime

print("=" * 80)
print("🧪 Complete Model Test - Llama 3.1 8B Uzbek")
print("=" * 80)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

MODEL_ID = "behbudiy/Llama-3.1-8B-Instruct-Uz"

# Test results
tests_passed = 0
tests_failed = 0
test_results = []

def log_test(name, passed, message="", error=None):
    global tests_passed, tests_failed, test_results
    
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    
    if message:
        print(f"     {message}")
    
    if error:
        print(f"     Error: {error}")
    
    if passed:
        tests_passed += 1
    else:
        tests_failed += 1
    
    test_results.append({
        "name": name,
        "passed": passed,
        "message": message,
        "error": str(error) if error else None
    })
    print()

################################################################################
# Test 1: Python Packages
################################################################################

print("━" * 80)
print("TEST 1: Python Packages")
print("━" * 80)
print()

# Test torch
try:
    import torch
    log_test(
        "Import torch", 
        True, 
        f"Version: {torch.__version__}"
    )
    
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        log_test(
            "CUDA Available", 
            True, 
            f"GPU: {gpu_name}, VRAM: {gpu_memory:.1f}GB"
        )
        device = "cuda"
    else:
        log_test(
            "CUDA Available", 
            True, 
            "No GPU, will use CPU"
        )
        device = "cpu"
        
except Exception as e:
    log_test("Import torch", False, error=e)
    print("CRITICAL: Cannot continue without torch")
    sys.exit(1)

# Test transformers
try:
    import transformers
    log_test(
        "Import transformers", 
        True, 
        f"Version: {transformers.__version__}"
    )
except Exception as e:
    log_test("Import transformers", False, error=e)
    print("CRITICAL: Cannot continue without transformers")
    sys.exit(1)

# Test huggingface_hub
try:
    import huggingface_hub
    log_test(
        "Import huggingface_hub", 
        True, 
        f"Version: {huggingface_hub.__version__}"
    )
except Exception as e:
    log_test("Import huggingface_hub", False, error=e)

################################################################################
# Test 2: Model Files
################################################################################

print("━" * 80)
print("TEST 2: Model Files in Cache")
print("━" * 80)
print()

try:
    from huggingface_hub import scan_cache_dir
    from pathlib import Path
    
    cache_info = scan_cache_dir()
    model_found = False
    
    for repo in cache_info.repos:
        if MODEL_ID in repo.repo_id:
            model_found = True
            size_gb = repo.size_on_disk / (1024**3)
            
            log_test(
                "Model found in cache",
                True,
                f"Size: {size_gb:.2f}GB, Path: {repo.repo_path}"
            )
            
            # Check for snapshots
            for revision in repo.revisions:
                snapshot_path = Path(repo.repo_path) / "snapshots" / revision.commit_hash
                
                if snapshot_path.exists():
                    # Check essential files
                    essential_files = [
                        "config.json",
                        "tokenizer.json",
                        "tokenizer_config.json"
                    ]
                    
                    all_present = True
                    for file in essential_files:
                        file_path = snapshot_path / file
                        if not file_path.exists():
                            all_present = False
                            log_test(
                                f"Check {file}",
                                False,
                                f"File missing: {file}"
                            )
                    
                    if all_present:
                        log_test(
                            "Essential files present",
                            True,
                            "config.json, tokenizer.json, tokenizer_config.json"
                        )
            break
    
    if not model_found:
        log_test(
            "Model found in cache",
            False,
            "Model not downloaded. Run: python download_model_simple.py"
        )
        print("CRITICAL: Cannot continue without model")
        sys.exit(1)
        
except Exception as e:
    log_test("Check model cache", False, error=e)
    sys.exit(1)

################################################################################
# Test 3: Load Tokenizer
################################################################################

print("━" * 80)
print("TEST 3: Load Tokenizer")
print("━" * 80)
print()

try:
    from transformers import AutoTokenizer
    
    print("Loading tokenizer...")
    start_time = time.time()
    
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        trust_remote_code=True
    )
    
    load_time = time.time() - start_time
    
    log_test(
        "Load tokenizer",
        True,
        f"Loaded in {load_time:.2f}s, Vocab size: {tokenizer.vocab_size:,}"
    )
    
    # Test tokenization
    test_text = "Salom, matematika haqida savol bering."
    tokens = tokenizer.encode(test_text)
    
    log_test(
        "Test tokenization",
        True,
        f"Text: '{test_text}' → {len(tokens)} tokens"
    )
    
except Exception as e:
    log_test("Load tokenizer", False, error=e)
    print("CRITICAL: Cannot continue without tokenizer")
    sys.exit(1)

################################################################################
# Test 4: Load Model
################################################################################

print("━" * 80)
print("TEST 4: Load Model")
print("━" * 80)
print()
print("⏳ This may take 2-5 minutes on first load...")
print()

try:
    from transformers import AutoModelForCausalLM
    
    print(f"Loading model on {device.upper()}...")
    start_time = time.time()
    
    if device == "cuda":
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True,
            trust_remote_code=True
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        )
        model = model.to(device)
    
    load_time = time.time() - start_time
    params = model.num_parameters() / 1e9
    
    log_test(
        "Load model",
        True,
        f"Loaded in {load_time:.1f}s, Parameters: {params:.2f}B, Device: {device.upper()}"
    )
    
except torch.cuda.OutOfMemoryError:
    log_test(
        "Load model",
        False,
        "CUDA out of memory. Try: pip install bitsandbytes and use 4-bit quantization"
    )
    sys.exit(1)
except MemoryError:
    log_test(
        "Load model",
        False,
        "Not enough RAM. Need 16GB+ for CPU inference"
    )
    sys.exit(1)
except Exception as e:
    log_test("Load model", False, error=e)
    sys.exit(1)

################################################################################
# Test 5: Simple Text Generation
################################################################################

print("━" * 80)
print("TEST 5: Simple Text Generation")
print("━" * 80)
print()

test_prompts = [
    "Assalomu alaykum! Mening ismim",
    "Matematikada algebra",
    "O'zbekiston poytaxti"
]

for i, prompt in enumerate(test_prompts, 1):
    try:
        print(f"Test {i}/{len(test_prompts)}: '{prompt}'")
        
        inputs = tokenizer(prompt, return_tensors="pt")
        if device == "cuda":
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        
        start_time = time.time()
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=30,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )
        
        gen_time = time.time() - start_time
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        log_test(
            f"Generation {i}",
            True,
            f"Output: '{generated_text}' ({gen_time:.2f}s)"
        )
        
    except Exception as e:
        log_test(f"Generation {i}", False, error=e)

################################################################################
# Test 6: Question & Answer Test
################################################################################

print("━" * 80)
print("TEST 6: Question & Answer Capability")
print("━" * 80)
print()

qa_tests = [
    {
        "question": "2 + 2 nechaga teng?",
        "expected_contains": ["4", "to'rt", "turt"]
    },
    {
        "question": "O'zbekiston poytaxti qaysi shahar?",
        "expected_contains": ["Toshkent", "Tashkent"]
    },
    {
        "question": "Matematikada ikki bilan ikkini ko'paytirsak nima hosil bo'ladi?",
        "expected_contains": ["4", "to'rt", "turt"]
    }
]

for i, qa in enumerate(qa_tests, 1):
    try:
        question = qa["question"]
        print(f"Q{i}: {question}")
        
        # Format as instruction
        messages = [
            {"role": "user", "content": question}
        ]
        
        # Try to use chat template if available
        if hasattr(tokenizer, 'apply_chat_template'):
            try:
                inputs = tokenizer.apply_chat_template(
                    messages,
                    return_tensors="pt",
                    add_generation_prompt=True
                )
            except:
                # Fallback to simple tokenization
                inputs = tokenizer(question, return_tensors="pt").input_ids
        else:
            inputs = tokenizer(question, return_tensors="pt").input_ids
        
        if device == "cuda":
            inputs = inputs.to("cuda")
        
        start_time = time.time()
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=100,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )
        
        gen_time = time.time() - start_time
        
        answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove question from answer if present
        if question in answer:
            answer = answer.replace(question, "").strip()
        
        print(f"A{i}: {answer}")
        print(f"    (Generated in {gen_time:.2f}s)")
        
        # Check if answer contains expected content
        contains_expected = any(
            exp.lower() in answer.lower() 
            for exp in qa["expected_contains"]
        )
        
        log_test(
            f"Q&A Test {i}",
            contains_expected,
            f"Answer quality: {'Good' if contains_expected else 'Check manually'}"
        )
        
    except Exception as e:
        log_test(f"Q&A Test {i}", False, error=e)

################################################################################
# Summary
################################################################################

print("━" * 80)
print("SUMMARY")
print("━" * 80)
print()

total_tests = tests_passed + tests_failed
pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0

print(f"Total Tests: {total_tests}")
print(f"✅ Passed: {tests_passed}")
print(f"❌ Failed: {tests_failed}")
print(f"Pass Rate: {pass_rate:.1f}%")
print()

if tests_failed == 0:
    print("=" * 80)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 80)
    print()
    print("✅ Your model is fully functional and ready to use!")
    print()
    print("You can now:")
    print("  1. Start the backend: python -m uvicorn backend.main:app --port 8001 --reload")
    print("  2. Use the model in your code")
    print("  3. Test Q&A API endpoints")
    print()
else:
    print("=" * 80)
    print(f"⚠️  {tests_failed} TEST(S) FAILED")
    print("=" * 80)
    print()
    print("Failed tests:")
    for result in test_results:
        if not result["passed"]:
            print(f"  ❌ {result['name']}")
            if result["error"]:
                print(f"     Error: {result['error']}")
    print()
    print("Check the errors above and:")
    print("  1. Install missing packages: pip install -r requirements.txt")
    print("  2. Re-download model: python download_model_simple.py")
    print("  3. Check system resources (RAM/VRAM)")
    print()

# Save results to file
try:
    import json
    results_file = f"model_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "model_id": MODEL_ID,
            "device": device,
            "total_tests": total_tests,
            "passed": tests_passed,
            "failed": tests_failed,
            "pass_rate": pass_rate,
            "results": test_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Results saved to: {results_file}")
    print()
except Exception as e:
    print(f"⚠️  Could not save results: {e}")

sys.exit(0 if tests_failed == 0 else 1)
