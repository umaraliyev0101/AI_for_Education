#!/usr/bin/env python3
"""
AI Education System - Unified Startup Script
Starts the entire system: database initial        # First, create a demo lesson
        lesson_data = {
            "title": "Demo Lesson - Algebra Basics",
            "description": "Introduction to basic algebra concepts",
            "date": "2024-01-15T10:00:00",  # Required datetime field
            "subject": "Mathematics"
        } backend server + demo setup

Usage:
    python start_all.py

This script will:
1. Initialize the database (create tables and admin user)
2. Start the FastAPI backend server on http://localhost:8001
3. Create a demo lesson and ask a question to download LLM models
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

# Global variable for server process
server_process = None

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8+ required. Current version:", sys.version)
        sys.exit(1)
    print(f"SUCCESS: Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required packages are installed."""
    required = ['fastapi', 'uvicorn', 'sqlalchemy', 'torch']
    missing = []

    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"ERROR: Missing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)

    print("SUCCESS: Dependencies installed")

def initialize_database():
    """Initialize database with tables and admin user."""
    print("\nInitializing database...")

    try:
        # Run the init_db script
        result = subprocess.run([
            sys.executable, "-m", "backend.init_db"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)

        if result.returncode == 0:
            print("SUCCESS: Database initialized successfully")
            if result.stdout:
                print(result.stdout.strip())
        else:
            print("ERROR: Database initialization failed:")
            print(result.stderr.strip())
            return False

    except Exception as e:
        print(f"ERROR: Error initializing database: {e}")
        return False

    return True

def initialize_demo_data():
    """Create demo lesson and ask a question to trigger LLM model download."""
    print("\nInitializing demo data and downloading LLM models...")

    try:
        # Wait for server to be ready with health check
        base_url = "http://localhost:8001"
        max_retries = 10
        retry_delay = 2
        
        print("Waiting for server to be ready...")
        for attempt in range(max_retries):
            try:
                # Test server health endpoint
                response = requests.get(f"{base_url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"SUCCESS: Server ready after {(attempt + 1) * retry_delay} seconds")
                    break
            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    print(f"Server not ready, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    raise requests.exceptions.ConnectionError("Server failed to start after all retries")
        else:
            raise requests.exceptions.ConnectionError("Server health check failed")

        # Login as admin to get JWT token
        print("Authenticating as admin...")
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        login_response = requests.post(f"{base_url}/api/auth/login", data=login_data)

        if login_response.status_code != 200:
            raise Exception(f"Admin login failed: {login_response.status_code} - {login_response.text}")

        token_data = login_response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        print("SUCCESS: Admin authentication successful")

        # First, create a demo lesson
        lesson_data = {
            "title": "Demo Lesson - Algebra Basics",
            "description": "Introduction to basic algebra concepts",
            "date": "2024-01-15T10:00:00",  # Required datetime field
            "subject": "Mathematics"
        }

        print("Creating demo lesson...")
        response = requests.post(f"{base_url}/api/lessons/", json=lesson_data, headers=headers)

        if response.status_code == 201:
            lesson = response.json()
            lesson_id = lesson["id"]
            print(f"SUCCESS: Demo lesson created with ID {lesson_id}")

            # Skip materials processing for demo - materials need to be uploaded first
            print("INFO: Skipping materials processing (no materials uploaded yet)")

            # Ask a demo question to trigger LLM download
            print("Asking demo question to download LLM models...")
            print("   Note: This may take several minutes for first-time model download")
            question_data = {
                "lesson_id": lesson_id,
                "question_text": "Algebra nima?"
            }

            # Increase timeout for LLM model download (5 minutes)
            try:
                qa_response = requests.post(f"{base_url}/api/qa/", json=question_data, headers=headers, timeout=300)

                if qa_response.status_code == 201:
                    qa_result = qa_response.json()
                    print("SUCCESS: Demo question answered")
                    print(f"   Question: {qa_result['question_text']}")
                    print(f"   Answer: {qa_result['answer_text'][:100]}...")
                    print("SUCCESS: LLM models downloaded and ready!")
                else:
                    print(f"WARNING: Demo question failed: {qa_response.status_code}")
                    print(f"   Response: {qa_response.text}")
                    print("   This is normal on first startup - models will download on first real question")
            except requests.exceptions.Timeout:
                print("WARNING: Demo question timed out (normal for first startup)")
                print("   LLM models will download on first real question")
            except requests.exceptions.RequestException as e:
                print(f"WARNING: Demo question request failed: {e}")
                print("   Models will download on first real question")
        else:
            print(f"WARNING: Demo lesson creation failed: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("WARNING: Could not connect to server for demo initialization")
        print("   Server may not be ready yet - models will download on first real question")
    except Exception as e:
        print(f"WARNING: Demo initialization failed: {e}")
        print("   Models will download on first real question")

def start_backend():
    """Start the FastAPI backend server in background."""
    print("\nStarting backend server...")

    try:
        # Start uvicorn server in background
        cmd = [
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", "0.0.0.0",
            "--port", "8001",
            "--reload"
        ]

        print(f"Starting server with command: {' '.join(cmd)}")
        print("Server will be available at: http://localhost:8001")
        print("API documentation at: http://localhost:8001/docs")
        print("Press Ctrl+C to stop the server")
        print("=" * 60)

        # Start server in background
        global server_process
        server_process = subprocess.Popen(cmd, cwd=Path(__file__).parent)

        # Wait for server to start (initial wait)
        time.sleep(8)
        print("SUCCESS: Server started successfully")

        return True

    except Exception as e:
        print(f"ERROR: Error starting server: {e}")
        return False

def main():
    """Main startup function."""
    print("=" * 60)
    print("AI EDUCATION SYSTEM - UNIFIED STARTUP")
    print("=" * 60)

    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    print(f"Working directory: {project_root}")

    # Run checks
    check_python_version()
    check_dependencies()

    # Initialize database
    if not initialize_database():
        print("ERROR: Cannot continue without database initialization")
        sys.exit(1)

    # Small delay
    time.sleep(1)

    # Start backend server in background
    if not start_backend():
        print("ERROR: Cannot continue without backend server")
        sys.exit(1)

    # Initialize demo data (downloads LLM models)
    initialize_demo_data()

    print("\n" + "=" * 60)
    print("SYSTEM READY!")
    print("Server: http://localhost:8001")
    print("Docs: http://localhost:8001/docs")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    try:
        # Keep the script running to maintain the server
        if server_process:
            server_process.wait()
    except KeyboardInterrupt:
        print("\nStopping server...")
        if server_process:
            server_process.terminate()
            server_process.wait()
        print("SUCCESS: Server stopped")

if __name__ == "__main__":
    main()
