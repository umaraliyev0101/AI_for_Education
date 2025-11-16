#!/bin/bash

################################################################################
# Complete LLM Diagnostic Tool
# Tests all aspects of LLM setup and identifies exact problems
################################################################################

set +e  # Don't exit on errors - we want to see all issues

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Status counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Arrays to store issues
declare -a CRITICAL_ISSUES
declare -a WARNINGS
declare -a SOLUTIONS

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}${BOLD}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
    echo ""
}

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED_CHECKS++))
    ((TOTAL_CHECKS++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    CRITICAL_ISSUES+=("$1")
    ((FAILED_CHECKS++))
    ((TOTAL_CHECKS++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS+=("$1")
    ((WARNING_CHECKS++))
    ((TOTAL_CHECKS++))
}

add_solution() {
    SOLUTIONS+=("$1")
}

################################################################################
# Main Diagnostic
################################################################################

print_header "🔍 Complete LLM Diagnostic Tool"

MODEL_ID="behbudiy/Llama-3.1-8B-Instruct-Uz"

echo "Model: $MODEL_ID"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

################################################################################
# SECTION 1: System Environment
################################################################################

print_section "1️⃣  System Environment"

# Check OS
echo "Operating System:"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "   OS: Linux"
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "   Distribution: $NAME $VERSION"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   OS: macOS"
else
    echo "   OS: $OSTYPE"
fi
echo ""

# Check Python
echo "Python:"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "   Version: $PYTHON_VERSION"
    check_pass "Python 3 installed"
else
    check_fail "Python 3 not found"
    add_solution "Install Python 3.8+: apt-get install python3 python3-pip"
fi
echo ""

# Check pip
echo "Package Manager:"
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version 2>&1)
    echo "   $PIP_VERSION"
    check_pass "pip3 installed"
else
    check_fail "pip3 not found"
    add_solution "Install pip: apt-get install python3-pip"
fi
echo ""

################################################################################
# SECTION 2: System Resources
################################################################################

print_section "2️⃣  System Resources"

# Check RAM
echo "Memory (RAM):"
if command -v free &> /dev/null; then
    TOTAL_RAM=$(free -g | awk '/^Mem:/ {print $2}')
    AVAIL_RAM=$(free -g | awk '/^Mem:/ {print $7}')
    echo "   Total: ${TOTAL_RAM}GB"
    echo "   Available: ${AVAIL_RAM}GB"
    
    if [ "$AVAIL_RAM" -lt 16 ]; then
        check_warn "Only ${AVAIL_RAM}GB RAM available (recommended: 16GB+)"
        add_solution "Free up memory: Close other applications or add swap space"
        add_solution "Or use 8-bit quantization: pip install bitsandbytes"
    else
        check_pass "Sufficient RAM available (${AVAIL_RAM}GB)"
    fi
else
    check_warn "Cannot detect RAM (free command not available)"
fi
echo ""

# Check Disk Space
echo "Disk Space:"
DISK_AVAIL=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
echo "   Available: ${DISK_AVAIL}GB"

if [ "$DISK_AVAIL" -lt 20 ]; then
    check_fail "Only ${DISK_AVAIL}GB disk space (need 20GB+)"
    add_solution "Free up disk space: Clean cache or delete unused files"
else
    check_pass "Sufficient disk space (${DISK_AVAIL}GB)"
fi
echo ""

# Check GPU
echo "GPU (CUDA):"
python3 << 'EOF'
import sys
try:
    import torch
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"   GPU: {gpu_name}")
        print(f"   VRAM: {gpu_memory:.1f}GB")
        print("   CUDA: Available")
        
        if gpu_memory < 8:
            print("   WARNING: Low VRAM (need 8GB+)")
            sys.exit(2)
        else:
            sys.exit(0)
    else:
        print("   CUDA: Not available (will use CPU)")
        sys.exit(1)
except ImportError:
    print("   PyTorch not installed")
    sys.exit(3)
EOF

GPU_STATUS=$?
if [ $GPU_STATUS -eq 0 ]; then
    check_pass "GPU available with sufficient VRAM"
elif [ $GPU_STATUS -eq 1 ]; then
    check_warn "No GPU - will use CPU (slower)"
    add_solution "For faster inference: Use GPU-enabled server"
elif [ $GPU_STATUS -eq 2 ]; then
    check_warn "GPU has insufficient VRAM"
    add_solution "Use 4-bit quantization: pip install bitsandbytes"
elif [ $GPU_STATUS -eq 3 ]; then
    check_fail "PyTorch not installed"
    add_solution "Install PyTorch: pip install torch"
fi
echo ""

################################################################################
# SECTION 3: Python Packages
################################################################################

print_section "3️⃣  Python Packages"

# Check required packages
REQUIRED_PACKAGES=(
    "torch:torch"
    "transformers:transformers"
    "huggingface_hub:huggingface-hub"
    "sentence_transformers:sentence-transformers"
    "langchain:langchain"
    "faiss:faiss-cpu"
)

echo "Checking required packages..."
echo ""

for package_spec in "${REQUIRED_PACKAGES[@]}"; do
    IFS=':' read -r import_name pip_name <<< "$package_spec"
    
    python3 -c "import $import_name" 2>/dev/null
    if [ $? -eq 0 ]; then
        VERSION=$(python3 -c "import $import_name; print(getattr($import_name, '__version__', 'unknown'))" 2>/dev/null)
        echo "   ✓ $pip_name ($VERSION)"
        ((PASSED_CHECKS++))
    else
        echo "   ✗ $pip_name (missing)"
        check_fail "$pip_name not installed"
        add_solution "Install: pip install $pip_name"
    fi
    ((TOTAL_CHECKS++))
done
echo ""

################################################################################
# SECTION 4: Model Files
################################################################################

print_section "4️⃣  Model Files in Cache"

# Find cache directory
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    CACHE_BASE="$USERPROFILE/.cache/huggingface/hub"
else
    CACHE_BASE="$HOME/.cache/huggingface/hub"
fi

echo "Cache directory: $CACHE_BASE"
echo ""

# Find model directory
MODEL_DIR=$(find "$CACHE_BASE" -type d -name "models--behbudiy--Llama-3.1-8B-Instruct-Uz" 2>/dev/null | head -1)

if [ -z "$MODEL_DIR" ]; then
    check_fail "Model not found in cache"
    add_solution "Download model: ./download_llama_model.sh"
    echo ""
    echo -e "${RED}▶ CRITICAL: Model not downloaded${NC}"
    echo ""
else
    check_pass "Model directory found"
    echo "   Path: $MODEL_DIR"
    
    # Check size
    MODEL_SIZE=$(du -sh "$MODEL_DIR" 2>/dev/null | cut -f1)
    echo "   Size: $MODEL_SIZE"
    
    # Find snapshot
    SNAPSHOT_DIR=$(find "$MODEL_DIR/snapshots" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | head -1)
    
    if [ -z "$SNAPSHOT_DIR" ]; then
        check_fail "No snapshot directory found"
        add_solution "Re-download model: rm -rf $MODEL_DIR && ./download_llama_model.sh"
    else
        check_pass "Snapshot directory found"
        SNAPSHOT_HASH=$(basename "$SNAPSHOT_DIR")
        echo "   Snapshot: ${SNAPSHOT_HASH:0:12}"
        echo ""
        
        # Check essential files
        echo "   Essential files:"
        ESSENTIAL_FILES=(
            "config.json"
            "tokenizer.json"
            "tokenizer_config.json"
            "special_tokens_map.json"
        )
        
        ALL_FILES_PRESENT=true
        for file in "${ESSENTIAL_FILES[@]}"; do
            if [ -f "$SNAPSHOT_DIR/$file" ]; then
                FILE_SIZE=$(stat -f%z "$SNAPSHOT_DIR/$file" 2>/dev/null || stat -c%s "$SNAPSHOT_DIR/$file" 2>/dev/null)
                echo "      ✓ $file (${FILE_SIZE} bytes)"
                ((PASSED_CHECKS++))
            else
                echo "      ✗ $file (missing)"
                check_fail "$file missing from model cache"
                ALL_FILES_PRESENT=false
            fi
            ((TOTAL_CHECKS++))
        done
        
        if [ "$ALL_FILES_PRESENT" = false ]; then
            add_solution "Download missing files: python3 fix_model_files.py"
            add_solution "Or re-run: ./download_llama_model.sh"
        fi
        
        echo ""
        
        # Check model weight files
        WEIGHT_COUNT=$(find "$SNAPSHOT_DIR" -name "*.safetensors" -o -name "model*.bin" 2>/dev/null | wc -l)
        echo "   Model weights: $WEIGHT_COUNT files"
        
        if [ "$WEIGHT_COUNT" -eq 0 ]; then
            check_fail "No model weight files found"
            add_solution "Re-download model: ./download_llama_model.sh"
        else
            check_pass "Model weight files present ($WEIGHT_COUNT files)"
        fi
    fi
fi
echo ""

################################################################################
# SECTION 5: Model Loading Test
################################################################################

print_section "5️⃣  Model Loading Test"

if [ ! -z "$MODEL_DIR" ] && [ "$ALL_FILES_PRESENT" = true ]; then
    echo "Testing model loading (this may take 2-5 minutes)..."
    echo ""
    
    python3 << 'EOTEST'
import sys
import time

MODEL_ID = "behbudiy/Llama-3.1-8B-Instruct-Uz"

# Test 1: Tokenizer
print("   [1/3] Loading tokenizer...", end=" ", flush=True)
try:
    from transformers import AutoTokenizer
    start = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    elapsed = time.time() - start
    print(f"✓ ({elapsed:.1f}s)")
    print(f"         Vocab size: {tokenizer.vocab_size:,}")
except Exception as e:
    print(f"✗")
    print(f"         Error: {e}")
    sys.exit(1)

# Test 2: Config
print("   [2/3] Loading config...", end=" ", flush=True)
try:
    from transformers import AutoConfig
    start = time.time()
    config = AutoConfig.from_pretrained(MODEL_ID, trust_remote_code=True)
    elapsed = time.time() - start
    print(f"✓ ({elapsed:.1f}s)")
    print(f"         Model type: {config.model_type}")
    print(f"         Layers: {config.num_hidden_layers}")
except Exception as e:
    print(f"✗")
    print(f"         Error: {e}")
    sys.exit(2)

# Test 3: Model
print("   [3/3] Loading model...", end=" ", flush=True)
try:
    from transformers import AutoModelForCausalLM
    import torch
    
    start = time.time()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
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
    
    elapsed = time.time() - start
    print(f"✓ ({elapsed:.1f}s)")
    print(f"         Device: {device.upper()}")
    print(f"         Parameters: {model.num_parameters() / 1e9:.2f}B")
    
    # Quick generation test
    print("   [4/4] Testing generation...", end=" ", flush=True)
    inputs = tokenizer("Salom", return_tensors="pt")
    if device == "cuda":
        inputs = {k: v.to("cuda") for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=10)
    
    print("✓")
    print()
    
except torch.cuda.OutOfMemoryError:
    print(f"✗")
    print(f"         Error: CUDA out of memory")
    sys.exit(3)
except MemoryError:
    print(f"✗")
    print(f"         Error: Not enough RAM")
    sys.exit(4)
except Exception as e:
    print(f"✗")
    print(f"         Error: {type(e).__name__}: {e}")
    sys.exit(5)

EOTEST

    TEST_STATUS=$?
    
    if [ $TEST_STATUS -eq 0 ]; then
        check_pass "Model loads and generates text successfully"
    elif [ $TEST_STATUS -eq 1 ]; then
        check_fail "Tokenizer loading failed"
        add_solution "Fix: python3 fix_model_files.py (missing tokenizer files)"
    elif [ $TEST_STATUS -eq 2 ]; then
        check_fail "Config loading failed"
        add_solution "Fix: python3 fix_model_files.py (missing config.json)"
    elif [ $TEST_STATUS -eq 3 ]; then
        check_fail "CUDA out of memory"
        add_solution "Use 4-bit quantization: pip install bitsandbytes"
        add_solution "Or use CPU: Set CUDA_VISIBLE_DEVICES=-1"
    elif [ $TEST_STATUS -eq 4 ]; then
        check_fail "Not enough RAM"
        add_solution "Free up memory or add swap space"
        add_solution "Use 8-bit quantization: pip install bitsandbytes"
    elif [ $TEST_STATUS -eq 5 ]; then
        check_fail "Model loading failed with unknown error"
        add_solution "Check Python traceback above for details"
    fi
else
    check_warn "Skipping model loading test (prerequisites not met)"
fi
echo ""

################################################################################
# SECTION 6: Project Integration
################################################################################

print_section "6️⃣  Project Integration"

# Check project structure
echo "Project structure:"

PROJECT_FILES=(
    "backend/routes/qa.py"
    "utils/uzbek_llm_qa_service.py"
    "backend/llm_config.py"
    "lesson_materials"
    "vector_stores"
)

for file in "${PROJECT_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo "   ✓ $file"
        ((PASSED_CHECKS++))
    else
        echo "   ✗ $file (missing)"
        check_warn "$file not found"
    fi
    ((TOTAL_CHECKS++))
done
echo ""

# Check if LLM service can be imported
echo "Testing LLM service import:"
python3 << 'EOIMPORT'
import sys
try:
    from utils.uzbek_llm_qa_service import create_uzbek_llm_qa_service
    print("   ✓ uzbek_llm_qa_service can be imported")
    sys.exit(0)
except ImportError as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(2)
EOIMPORT

if [ $? -eq 0 ]; then
    check_pass "LLM service module is importable"
else
    check_fail "Cannot import LLM service module"
    add_solution "Check utils/uzbek_llm_qa_service.py for errors"
fi
echo ""

# Check lesson materials
echo "Lesson materials:"
MATERIALS_FOUND=false

for materials_dir in "lesson_materials" "sample_materials" "uploads/materials"; do
    if [ -d "$materials_dir" ]; then
        FILE_COUNT=$(find "$materials_dir" -type f \( -name "*.txt" -o -name "*.pdf" -o -name "*.docx" -o -name "*.pptx" \) 2>/dev/null | wc -l)
        if [ "$FILE_COUNT" -gt 0 ]; then
            echo "   ✓ $materials_dir ($FILE_COUNT files)"
            MATERIALS_FOUND=true
            ((PASSED_CHECKS++))
        else
            echo "   ⚠ $materials_dir (empty)"
            ((WARNING_CHECKS++))
        fi
    fi
    ((TOTAL_CHECKS++))
done

if [ "$MATERIALS_FOUND" = false ]; then
    check_warn "No lesson materials found"
    add_solution "Add lesson materials to lesson_materials/ directory"
fi
echo ""

################################################################################
# SECTION 7: Summary & Solutions
################################################################################

print_header "📊 Diagnostic Summary"

echo "Test Results:"
echo "   Total checks: $TOTAL_CHECKS"
echo "   ✓ Passed: $PASSED_CHECKS"
echo "   ✗ Failed: $FAILED_CHECKS"
echo "   ⚠ Warnings: $WARNING_CHECKS"
echo ""

# Calculate pass rate
PASS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}${BOLD}🎉 ALL CRITICAL TESTS PASSED! ($PASS_RATE%)${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "✅ Your LLM setup is working correctly!"
    echo ""
    
    if [ $WARNING_CHECKS -gt 0 ]; then
        echo "⚠️  However, there are some warnings to consider:"
        echo ""
        for warning in "${WARNINGS[@]}"; do
            echo "   • $warning"
        done
        echo ""
    fi
    
    echo "Next steps:"
    echo "   1. Test with your backend: uvicorn backend.main:app --reload"
    echo "   2. Try Q&A endpoint with a lesson"
    echo "   3. Monitor memory usage during inference"
    echo ""
    
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}${BOLD}❌ CRITICAL ISSUES FOUND! ($FAILED_CHECKS problems)${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Critical issues:"
    echo ""
    for issue in "${CRITICAL_ISSUES[@]}"; do
        echo "   ✗ $issue"
    done
    echo ""
    
    if [ ${#SOLUTIONS[@]} -gt 0 ]; then
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}${BOLD}🔧 SOLUTIONS${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "Apply these fixes in order:"
        echo ""
        
        solution_num=1
        for solution in "${SOLUTIONS[@]}"; do
            echo "   $solution_num. $solution"
            ((solution_num++))
        done
        echo ""
    fi
    
    # Provide quick fix commands
    echo -e "${CYAN}Quick fix commands:${NC}"
    echo ""
    
    if echo "${CRITICAL_ISSUES[@]}" | grep -q "Model not found"; then
        echo "   # Download the model:"
        echo "   ./download_llama_model.sh"
        echo ""
    fi
    
    if echo "${CRITICAL_ISSUES[@]}" | grep -q "missing"; then
        echo "   # Fix missing model files:"
        echo "   python3 fix_model_files.py"
        echo ""
    fi
    
    if echo "${CRITICAL_ISSUES[@]}" | grep -q "not installed"; then
        echo "   # Install missing packages:"
        echo "   pip install -r requirements.txt"
        echo ""
    fi
    
    if echo "${CRITICAL_ISSUES[@]}" | grep -q "memory\|RAM\|VRAM"; then
        echo "   # Use quantization for lower memory:"
        echo "   pip install bitsandbytes"
        echo ""
    fi
    
    exit 1
fi
