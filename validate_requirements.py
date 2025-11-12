"""
Validate requirements.txt - Check all imports are satisfied
This script checks that all imported packages in the codebase
are declared in requirements.txt
"""
import re
import ast
from pathlib import Path
from typing import Set, List

# Package name mappings (import name -> PyPI name)
PACKAGE_MAPPINGS = {
    'cv2': 'opencv-python',
    'PIL': 'Pillow',
    'docx': 'python-docx',
    'pptx': 'python-pptx',
    'jose': 'python-jose',
    'dotenv': 'python-dotenv',
    'pydantic_settings': 'pydantic-settings',
    'bcrypt': 'passlib',
    'edge_tts': 'edge-tts',
    'sklearn': 'scikit-learn',
}

def get_imports_from_file(file_path: Path) -> Set[str]:
    """Extract all imports from a Python file"""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse with AST
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except SyntaxError:
            # Fallback to regex if AST fails
            import_pattern = re.compile(r'^\s*(?:from|import)\s+(\w+)', re.MULTILINE)
            for match in import_pattern.finditer(content):
                imports.add(match.group(1))
                
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
    
    return imports

def get_requirements() -> Set[str]:
    """Parse requirements.txt and extract package names"""
    requirements = set()
    req_file = Path('requirements.txt')
    
    if not req_file.exists():
        print("❌ requirements.txt not found!")
        return requirements
    
    with open(req_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line.startswith('#') or not line:
                continue
            # Extract package name (before >= or ==)
            package = re.split(r'[><=!]', line)[0].strip()
            # Handle extras like [standard]
            package = package.split('[')[0].strip()
            if package:
                requirements.add(package.lower())
    
    return requirements

def get_stdlib_modules() -> Set[str]:
    """Get list of Python standard library modules"""
    # Common stdlib modules (not exhaustive but covers most)
    return {
        'os', 'sys', 'io', 're', 'json', 'time', 'datetime', 'logging',
        'typing', 'pathlib', 'collections', 'itertools', 'functools',
        'unittest', 'sqlite3', 'pickle', 'tempfile', 'uuid', 'enum',
        'dataclasses', 'asyncio', 'concurrent', 'threading', 'multiprocessing',
        'decimal', 'math', 'random', 'string', 'unicodedata', 'wave',
        'abc', 'contextlib', 'copy', 'warnings', 'traceback'
    }

def main():
    print("=" * 70)
    print("🔍 Requirements Validation - AI Education System")
    print("=" * 70)
    print()
    
    # Get all Python files
    python_files = list(Path('.').rglob('*.py'))
    # Exclude virtual environment and cache
    python_files = [f for f in python_files if 'venv' not in str(f) and '__pycache__' not in str(f)]
    
    print(f"📁 Scanning {len(python_files)} Python files...")
    print()
    
    # Collect all imports
    all_imports = set()
    for file in python_files:
        imports = get_imports_from_file(file)
        all_imports.update(imports)
    
    # Get requirements and stdlib
    requirements = get_requirements()
    stdlib = get_stdlib_modules()
    
    # Filter out stdlib and local imports
    external_imports = {
        imp for imp in all_imports 
        if imp not in stdlib and not imp.startswith('backend') 
        and not imp.startswith('face_recognition') and not imp.startswith('stt_pipelines')
        and not imp.startswith('utils')
    }
    
    # Map imports to package names
    mapped_imports = set()
    for imp in external_imports:
        pkg = PACKAGE_MAPPINGS.get(imp, imp)
        if pkg:
            mapped_imports.add(pkg.lower())
    
    # Check for missing or extra packages
    missing = mapped_imports - requirements
    
    # Filter out known subpackages
    subpackages = {'langchain_text_splitters', 'langchain_community', 'langchain_core', 
                   'facenet_pytorch', 'sentence_transformers'}
    missing = {pkg for pkg in missing if pkg not in subpackages}
    
    print("=" * 70)
    print("📊 VALIDATION RESULTS")
    print("=" * 70)
    print()
    
    print(f"✅ Total Python files scanned: {len(python_files)}")
    print(f"✅ Unique external imports found: {len(external_imports)}")
    print(f"✅ Packages in requirements.txt: {len(requirements)}")
    print()
    
    if missing:
        print("⚠️  POTENTIALLY MISSING PACKAGES:")
        print("-" * 70)
        for pkg in sorted(missing):
            print(f"  - {pkg}")
        print()
        print("Note: Some packages may be sub-packages or provided by other dependencies")
    else:
        print("✅ All imports are satisfied by requirements.txt")
    
    print()
    print("=" * 70)
    print("🎯 USED PACKAGES")
    print("=" * 70)
    print()
    
    # Show which packages from requirements are actually used
    used_requirements = requirements & mapped_imports
    print(f"Actively used packages: {len(used_requirements)}")
    for pkg in sorted(used_requirements):
        print(f"  ✓ {pkg}")
    
    print()
    print("=" * 70)
    print("✅ VALIDATION COMPLETE")
    print("=" * 70)
    print()
    
    return len(missing) == 0

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
