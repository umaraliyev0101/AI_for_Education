"""
Database Initialization Script
Creates initial admin user and sets up database
"""
from backend.database import SessionLocal, init_db
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
