#!/usr/bin/env python3
"""
Face Recognition Database Manager
=================================

SQLite database management for student face encodings and attendance.
"""

import sqlite3
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceRecognitionDB:
    """Manages SQLite database for face recognition and attendance"""

    def __init__(self, db_path: str = "attendance.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"✅ Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        
        # Students table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                class_name TEXT,
                face_encoding BLOB NOT NULL,
                enrolled_date TEXT DEFAULT CURRENT_TIMESTAMP,
                photos_count INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1
            )
        """)

        # Attendance table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                date TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                confidence REAL NOT NULL,
                status TEXT DEFAULT 'present',
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                UNIQUE(student_id, date)
            )
        """)

        # Classes table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                class_id TEXT PRIMARY KEY,
                class_name TEXT NOT NULL,
                schedule TEXT,
                room TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        logger.info("✅ Database tables created/verified")

    def add_student(self, student_id: str, name: str, class_name: str, 
                   face_encoding: np.ndarray, photos_count: int = 1) -> bool:
        """
        Add a new student to the database
        
        Args:
            student_id: Unique student identifier
            name: Student's full name
            class_name: Class/grade the student belongs to
            face_encoding: 512-dimensional face encoding vector
            photos_count: Number of photos used for enrollment
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert numpy array to bytes for storage
            encoding_bytes = face_encoding.tobytes()
            
            self.cursor.execute("""
                INSERT INTO students (student_id, name, class_name, face_encoding, photos_count)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, name, class_name, encoding_bytes, photos_count))
            
            self.conn.commit()
            logger.info(f"✅ Added student: {name} (ID: {student_id})")
            return True
            
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ Student {student_id} already exists")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to add student: {e}")
            return False

    def get_student(self, student_id: str) -> Optional[Dict]:
        """Get student information by ID"""
        try:
            self.cursor.execute("""
                SELECT student_id, name, class_name, face_encoding, enrolled_date, photos_count, active
                FROM students WHERE student_id = ?
            """, (student_id,))
            
            row = self.cursor.fetchone()
            if row:
                return {
                    'student_id': row[0],
                    'name': row[1],
                    'class_name': row[2],
                    'face_encoding': np.frombuffer(row[3], dtype=np.float32),
                    'enrolled_date': row[4],
                    'photos_count': row[5],
                    'active': bool(row[6])
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get student: {e}")
            return None

    def get_all_students(self, active_only: bool = True) -> List[Dict]:
        """Get all students from database"""
        try:
            query = "SELECT student_id, name, class_name, face_encoding, enrolled_date, photos_count, active FROM students"
            if active_only:
                query += " WHERE active = 1"
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            students = []
            for row in rows:
                students.append({
                    'student_id': row[0],
                    'name': row[1],
                    'class_name': row[2],
                    'face_encoding': np.frombuffer(row[3], dtype=np.float32),
                    'enrolled_date': row[4],
                    'photos_count': row[5],
                    'active': bool(row[6])
                })
            
            return students
            
        except Exception as e:
            logger.error(f"❌ Failed to get students: {e}")
            return []

    def get_all_encodings(self, active_only: bool = True) -> Tuple[List[np.ndarray], List[str]]:
        """
        Get all face encodings and corresponding student IDs
        Used for batch face recognition
        
        Returns:
            Tuple of (encodings_list, student_ids_list)
        """
        students = self.get_all_students(active_only)
        encodings = [s['face_encoding'] for s in students]
        student_ids = [s['student_id'] for s in students]
        return encodings, student_ids

    def mark_attendance(self, student_id: str, confidence: float, 
                       date: Optional[str] = None) -> bool:
        """
        Mark attendance for a student
        
        Args:
            student_id: Student identifier
            confidence: Recognition confidence (0-1)
            date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # Try to insert, ignore if already marked today
            self.cursor.execute("""
                INSERT OR REPLACE INTO attendance (student_id, date, timestamp, confidence, status)
                VALUES (?, ?, ?, ?, 'present')
            """, (student_id, date, timestamp, confidence))
            
            self.conn.commit()
            logger.info(f"✅ Marked attendance: {student_id} at {timestamp} (confidence: {confidence:.2f})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to mark attendance: {e}")
            return False

    def get_attendance(self, date: Optional[str] = None, class_name: Optional[str] = None) -> List[Dict]:
        """
        Get attendance records for a specific date and/or class
        
        Args:
            date: Date string (YYYY-MM-DD), defaults to today
            class_name: Filter by class name
            
        Returns:
            List of attendance records
        """
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            query = """
                SELECT a.student_id, s.name, s.class_name, a.timestamp, a.confidence, a.status
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.date = ?
            """
            params = [date]
            
            if class_name:
                query += " AND s.class_name = ?"
                params.append(class_name)
            
            query += " ORDER BY a.timestamp"
            
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            
            records = []
            for row in rows:
                records.append({
                    'student_id': row[0],
                    'name': row[1],
                    'class_name': row[2],
                    'timestamp': row[3],
                    'confidence': row[4],
                    'status': row[5]
                })
            
            return records
            
        except Exception as e:
            logger.error(f"❌ Failed to get attendance: {e}")
            return []

    def get_attendance_summary(self, date: Optional[str] = None) -> Dict:
        """Get attendance summary statistics for a date"""
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            # Total enrolled students
            self.cursor.execute("SELECT COUNT(*) FROM students WHERE active = 1")
            total_students = self.cursor.fetchone()[0]
            
            # Present students
            self.cursor.execute("""
                SELECT COUNT(*) FROM attendance WHERE date = ?
            """, (date,))
            present_count = self.cursor.fetchone()[0]
            
            # Absent students
            absent_count = total_students - present_count
            
            # Attendance by class
            self.cursor.execute("""
                SELECT s.class_name, COUNT(*) as present
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.date = ?
                GROUP BY s.class_name
            """, (date,))
            
            class_attendance = {}
            for row in self.cursor.fetchall():
                class_attendance[row[0]] = row[1]
            
            return {
                'date': date,
                'total_students': total_students,
                'present': present_count,
                'absent': absent_count,
                'attendance_rate': (present_count / total_students * 100) if total_students > 0 else 0,
                'by_class': class_attendance
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get attendance summary: {e}")
            return {}

    def update_student(self, student_id: str, **kwargs) -> bool:
        """Update student information"""
        try:
            allowed_fields = ['name', 'class_name', 'face_encoding', 'active']
            updates = []
            values = []
            
            for key, value in kwargs.items():
                if key in allowed_fields:
                    if key == 'face_encoding':
                        value = value.tobytes()
                    updates.append(f"{key} = ?")
                    values.append(value)
            
            if not updates:
                return False
            
            values.append(student_id)
            query = f"UPDATE students SET {', '.join(updates)} WHERE student_id = ?"
            
            self.cursor.execute(query, values)
            self.conn.commit()
            logger.info(f"✅ Updated student: {student_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update student: {e}")
            return False

    def delete_student(self, student_id: str, soft_delete: bool = True) -> bool:
        """Delete or deactivate a student"""
        try:
            if soft_delete:
                # Soft delete - just mark as inactive
                self.cursor.execute("UPDATE students SET active = 0 WHERE student_id = ?", (student_id,))
            else:
                # Hard delete - remove from database
                self.cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
                self.cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
            
            self.conn.commit()
            logger.info(f"✅ Deleted student: {student_id} (soft={soft_delete})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete student: {e}")
            return False

    def get_student_attendance_history(self, student_id: str, days: int = 30) -> List[Dict]:
        """Get attendance history for a specific student"""
        try:
            self.cursor.execute("""
                SELECT date, timestamp, confidence, status
                FROM attendance
                WHERE student_id = ?
                ORDER BY date DESC, timestamp DESC
                LIMIT ?
            """, (student_id, days))
            
            records = []
            for row in self.cursor.fetchall():
                records.append({
                    'date': row[0],
                    'timestamp': row[1],
                    'confidence': row[2],
                    'status': row[3]
                })
            
            return records
            
        except Exception as e:
            logger.error(f"❌ Failed to get student history: {e}")
            return []

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("✅ Database connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Helper functions for testing
def test_database():
    """Test database operations"""
    print("🧪 Testing Face Recognition Database...")
    
    with FaceRecognitionDB("test_attendance.db") as db:
        # Test add student
        test_encoding = np.random.rand(512).astype(np.float32)
        db.add_student("12345", "Ali Karimov", "CS101", test_encoding, 3)
        
        # Test get student
        student = db.get_student("12345")
        print(f"✅ Retrieved student: {student['name']}")
        
        # Test mark attendance
        db.mark_attendance("12345", 0.95)
        
        # Test get attendance
        attendance = db.get_attendance()
        print(f"✅ Attendance records: {len(attendance)}")
        
        # Test summary
        summary = db.get_attendance_summary()
        print(f"✅ Attendance rate: {summary['attendance_rate']:.1f}%")
    
    print("✅ Database tests passed!")


if __name__ == "__main__":
    test_database()
