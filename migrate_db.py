"""
Database Migration Script
Add group_id column to students table
"""
import sqlite3
import os

def migrate_database():
    """Add group_id column to students table"""
    db_path = os.path.join(os.path.dirname(__file__), "ai_education.db")

    if not os.path.exists(db_path):
        print("Database file not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if groups table exists, create if not
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL,
                year_level INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Check if group_id column exists in students table
        cursor.execute("PRAGMA table_info(students)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'group_id' not in column_names:
            print("Adding group_id column to students table...")
            # Add the column as nullable first
            cursor.execute("ALTER TABLE students ADD COLUMN group_id INTEGER REFERENCES groups(id)")

            # For existing records, we need to assign them to a default group
            # But since this is a fresh setup, there might not be existing students
            # Let's check if there are any students
            cursor.execute("SELECT COUNT(*) FROM students")
            count = cursor.fetchone()[0]

            if count > 0:
                print(f"Found {count} existing students. Creating a default group...")

                # Create a default group
                cursor.execute("INSERT INTO groups (name, year_level) VALUES (?, ?)", ("Default", 1))
                default_group_id = cursor.lastrowid

                # Assign all existing students to the default group
                cursor.execute("UPDATE students SET group_id = ?", (default_group_id,))

            # Now make the column NOT NULL (SQLite doesn't support this directly)
            # We'll recreate the table with the constraint
            print("Recreating students table with NOT NULL constraint...")

            # Get the current table schema
            cursor.execute("PRAGMA table_info(students)")
            columns_info = cursor.fetchall()

            # Create new table with NOT NULL constraint
            cursor.execute("""
                CREATE TABLE students_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id VARCHAR(50) NOT NULL UNIQUE,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    phone VARCHAR(20),
                    group_id INTEGER NOT NULL REFERENCES groups(id),
                    face_encoding BLOB,
                    face_image_path VARCHAR(255),
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Copy data from old table to new table
            columns_list = [col[1] for col in columns_info]
            columns_str = ", ".join(columns_list)
            cursor.execute(f"INSERT INTO students_new ({columns_str}) SELECT {columns_str} FROM students")

            # Drop old table and rename new one
            cursor.execute("DROP TABLE students")
            cursor.execute("ALTER TABLE students_new RENAME TO students")

            # Recreate indexes
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_students_student_id ON students (student_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_students_email ON students (email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_students_id ON students (id)")

            conn.commit()
            print("Migration completed successfully!")
        else:
            print("group_id column already exists")

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
