"""
Create default groups for testing
"""
import sqlite3
import os

def create_default_groups():
    """Create default groups for each year level"""
    db_path = os.path.join(os.path.dirname(__file__), "ai_education.db")

    if not os.path.exists(db_path):
        print("Database file not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if groups already exist
        cursor.execute("SELECT COUNT(*) FROM groups")
        count = cursor.fetchone()[0]

        if count == 0:
            print("Creating default groups...")

            # Create groups for each year (1-4) with some default names
            groups_data = [
                ("A1", 1), ("B1", 1), ("C1", 1),
                ("A2", 2), ("B2", 2), ("C2", 2),
                ("A3", 3), ("B3", 3), ("C3", 3),
                ("A4", 4), ("B4", 4), ("C4", 4),
            ]

            for name, year_level in groups_data:
                cursor.execute("INSERT INTO groups (name, year_level) VALUES (?, ?)", (name, year_level))

            conn.commit()
            print(f"Created {len(groups_data)} default groups")
        else:
            print(f"Groups already exist: {count} groups found")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_default_groups()
