#!/usr/bin/env python3
"""
AI Education System - Unified Startup Script
Starts the entire system: database initialization and backend server

Usage:
    python start_all.py

This script will:
1. Initialize the database (create tables and admin user)
2. Start the FastAPI backend server on http://localhost:8001
"""

import os
import sys
import subprocess
import time
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
        # Import required modules
        from backend.database import SessionLocal, init_db
        from backend.models.user import User, UserRole
        from backend.auth import get_password_hash

        # Initialize database tables
        print("Creating database tables...")
        init_db()
        print("SUCCESS: Database tables created")

        # Create initial admin user
        print("\nCreating initial admin user...")
        db = SessionLocal()

        try:
            # Check if admin exists
            admin = db.query(User).filter(User.username == "admin").first()

            if not admin:
                # Create admin user
                admin = User(
                    username="admin",
                    email="admin@example.com",
                    full_name="System Administrator",
                    password_hash=get_password_hash("admin123"),
                    role=UserRole.ADMIN,
                    is_active=True
                )
                db.add(admin)
                db.commit()
                print("SUCCESS: Initial admin user created")
                print("   Username: admin")
                print("   Password: admin123")
                print("   WARNING: Please change the password after first login!")
            else:
                print("INFO: Admin user already exists")

        finally:
            db.close()

        print("\nSUCCESS: Database initialization complete!")
        return True

    except Exception as e:
        print(f"ERROR: Error initializing database: {e}")
        return False

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
