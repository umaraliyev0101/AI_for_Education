#!/usr/bin/env python3
"""
Docker Import Test Script
Tests if all backend imports work correctly in Docker environment
"""

import sys
import os

print("=" * 60)
print("Docker Import Verification Script")
print("=" * 60)
print()

# Add /app to Python path (simulating Docker environment)
sys.path.insert(0, '/app')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print(f"Python version: {sys.version}")
print(f"Python path: {sys.path[:3]}...")
print()

# Test imports
tests = [
    ("backend", "Backend package"),
    ("backend.database", "Database module"),
    ("backend.config", "Config module"),
    ("backend.main", "Main app module"),
    ("backend.auth", "Auth module"),
    ("backend.models.user", "User model"),
    ("backend.models.student", "Student model"),
    ("backend.models.lesson", "Lesson model"),
    ("backend.routes.auth", "Auth routes"),
    ("backend.routes.students", "Students routes"),
    ("backend.routes.lessons", "Lessons routes"),
    ("backend.services.lesson_session_service", "Lesson session service"),
    ("face_recognition", "Face recognition package"),
    ("utils.uzbek_llm_qa_service", "Q&A service"),
    ("stt_pipelines", "STT pipelines"),
]

passed = 0
failed = 0
errors = []

print("Testing imports...")
print("-" * 60)

for module_name, description in tests:
    try:
        __import__(module_name)
        print(f"✓ {description:40} OK")
        passed += 1
    except Exception as e:
        print(f"✗ {description:40} FAILED")
        failed += 1
        errors.append((module_name, str(e)))

print("-" * 60)
print()
print(f"Results: {passed} passed, {failed} failed")
print()

if errors:
    print("=" * 60)
    print("ERRORS:")
    print("=" * 60)
    for module, error in errors:
        print(f"\n{module}:")
        print(f"  {error}")
    print()
    sys.exit(1)
else:
    print("✓ All imports successful! Docker environment is correctly configured.")
    sys.exit(0)
