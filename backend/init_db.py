"""
Database Initialization Script
Creates initial admin user and sets up database

This script is safe to run directly (python backend/init_db.py) from the repo root
even when the repo root is not on PYTHONPATH. It ensures the repository root is
on sys.path, then imports model modules so SQLAlchemy mappers are configured
before any queries/mapper configuration runs.
"""
import os
import sys
import importlib

# Ensure repo root is on sys.path so `import backend...` works when running
# this file directly (no need to run as a module or change CWD).
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.database import SessionLocal, init_db

model_modules = [
    "backend.models.user",
    "backend.models.student",
    "backend.models.group",
    "backend.models.lesson",
    "backend.models.attendance",
    "backend.models.qa_session",
]

for mod in model_modules:
    try:
        importlib.import_module(mod)
    except Exception as e:
        # Don't crash here; print a warning so the user can see missing model issues.
        print(f"Warning importing {mod}: {e}")

from backend.models.user import User, UserRole
from backend.auth import get_password_hash


def create_initial_admin():
    """Create initial admin user if not exists"""
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


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("SUCCESS: Database tables created")
    
    print("\nCreating initial admin user...")
    create_initial_admin()
    
    print("\nSUCCESS: Database initialization complete!")
