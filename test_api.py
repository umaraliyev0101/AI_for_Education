"""
API Test Script
Quick test to verify all API endpoints are working
"""
import requests
import json
from datetime import datetime, timedelta

# Base URL
BASE_URL = "http://localhost:8000"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message):
    print(f"{RED}❌ {message}{RESET}")


def print_info(message):
    print(f"{YELLOW}ℹ️  {message}{RESET}")


def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*50)
    print("Testing Health Check")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print_success("Health check passed")
        print(f"Response: {response.json()}")
        return True
    else:
        print_error(f"Health check failed: {response.status_code}")
        return False


def test_login():
    """Test login endpoint"""
    print("\n" + "="*50)
    print("Testing Login")
    print("="*50)
    
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", data=data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print_success("Login successful")
        print(f"Token (first 50 chars): {token[:50]}...")
        return token
    else:
        print_error(f"Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def test_get_current_user(token):
    """Test get current user endpoint"""
    print("\n" + "="*50)
    print("Testing Get Current User")
    print("="*50)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        print_success("Get current user successful")
        print(f"User: {user['username']} ({user['role']})")
        return True
    else:
        print_error(f"Get current user failed: {response.status_code}")
        return False


def test_create_student(token):
    """Test create student endpoint"""
    print("\n" + "="*50)
    print("Testing Create Student")
    print("="*50)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "student_id": f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "name": "Test Student",
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "phone": "+998901234567",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/api/students", headers=headers, json=data)
    
    if response.status_code == 201:
        student = response.json()
        print_success("Student created successfully")
        print(f"Student ID: {student['student_id']}, Name: {student['name']}")
        return student['id']
    else:
        print_error(f"Create student failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def test_list_students(token):
    """Test list students endpoint"""
    print("\n" + "="*50)
    print("Testing List Students")
    print("="*50)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/students", headers=headers)
    
    if response.status_code == 200:
        students = response.json()
        print_success(f"Listed {len(students)} students")
        if students:
            print(f"First student: {students[0]['student_id']} - {students[0]['name']}")
        return True
    else:
        print_error(f"List students failed: {response.status_code}")
        return False


def test_create_lesson(token):
    """Test create lesson endpoint"""
    print("\n" + "="*50)
    print("Testing Create Lesson")
    print("="*50)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    lesson_date = (datetime.now() + timedelta(days=1)).isoformat()
    
    data = {
        "title": "Test Lesson - API Test",
        "description": "This is a test lesson created by API test script",
        "date": lesson_date,
        "duration_minutes": 90,
        "subject": "Testing"
    }
    
    response = requests.post(f"{BASE_URL}/api/lessons", headers=headers, json=data)
    
    if response.status_code == 201:
        lesson = response.json()
        print_success("Lesson created successfully")
        print(f"Lesson ID: {lesson['id']}, Title: {lesson['title']}")
        return lesson['id']
    else:
        print_error(f"Create lesson failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def test_list_lessons(token):
    """Test list lessons endpoint"""
    print("\n" + "="*50)
    print("Testing List Lessons")
    print("="*50)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/lessons", headers=headers)
    
    if response.status_code == 200:
        lessons = response.json()
        print_success(f"Listed {len(lessons)} lessons")
        if lessons:
            print(f"First lesson: {lessons[0]['title']} ({lessons[0]['status']})")
        return True
    else:
        print_error(f"List lessons failed: {response.status_code}")
        return False


def test_mark_attendance(token, student_id, lesson_id):
    """Test mark attendance endpoint"""
    print("\n" + "="*50)
    print("Testing Mark Attendance")
    print("="*50)
    
    if not student_id or not lesson_id:
        print_info("Skipping attendance test (no student or lesson)")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "student_id": student_id,
        "lesson_id": lesson_id,
        "entry_method": "manual",
        "notes": "Test attendance via API"
    }
    
    response = requests.post(f"{BASE_URL}/api/attendance", headers=headers, json=data)
    
    if response.status_code == 201:
        attendance = response.json()
        print_success("Attendance marked successfully")
        print(f"Attendance ID: {attendance['id']}")
        return attendance['id']
    else:
        print_error(f"Mark attendance failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def test_list_attendance(token):
    """Test list attendance endpoint"""
    print("\n" + "="*50)
    print("Testing List Attendance")
    print("="*50)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/attendance", headers=headers)
    
    if response.status_code == 200:
        attendance_records = response.json()
        print_success(f"Listed {len(attendance_records)} attendance records")
        if attendance_records:
            print(f"Latest record: Student ID {attendance_records[0]['student_id']} at {attendance_records[0]['timestamp']}")
        return True
    else:
        print_error(f"List attendance failed: {response.status_code}")
        return False


def test_create_qa_session(token, lesson_id):
    """Test create Q&A session endpoint"""
    print("\n" + "="*50)
    print("Testing Create Q&A Session")
    print("="*50)
    
    if not lesson_id:
        print_info("Skipping Q&A test (no lesson)")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "lesson_id": lesson_id,
        "question_text": "Bu test savoli. API orqali yaratilgan."
    }
    
    response = requests.post(f"{BASE_URL}/api/qa", headers=headers, json=data)
    
    if response.status_code == 201:
        qa = response.json()
        print_success("Q&A session created successfully")
        print(f"Q&A ID: {qa['id']}, Question: {qa['question_text'][:50]}...")
        print_info(f"Note: {qa['answer_text']}")
        return qa['id']
    else:
        print_error(f"Create Q&A session failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def test_list_qa_sessions(token):
    """Test list Q&A sessions endpoint"""
    print("\n" + "="*50)
    print("Testing List Q&A Sessions")
    print("="*50)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/qa", headers=headers)
    
    if response.status_code == 200:
        qa_sessions = response.json()
        print_success(f"Listed {len(qa_sessions)} Q&A sessions")
        if qa_sessions:
            print(f"Latest Q&A: {qa_sessions[0]['question_text'][:50]}...")
        return True
    else:
        print_error(f"List Q&A sessions failed: {response.status_code}")
        return False


def main():
    """Run all API tests"""
    print("\n" + "="*70)
    print("🚀 AI Education Backend API Test Suite")
    print("="*70)
    
    # Test health check
    if not test_health_check():
        print_error("\nHealth check failed. Is the server running?")
        return
    
    # Test login
    token = test_login()
    if not token:
        print_error("\nLogin failed. Cannot continue tests.")
        return
    
    # Test authenticated endpoints
    test_get_current_user(token)
    
    # Test student endpoints
    student_id = test_create_student(token)
    test_list_students(token)
    
    # Test lesson endpoints
    lesson_id = test_create_lesson(token)
    test_list_lessons(token)
    
    # Test attendance endpoints
    test_mark_attendance(token, student_id, lesson_id)
    test_list_attendance(token)
    
    # Test Q&A endpoints
    test_create_qa_session(token, lesson_id)
    test_list_qa_sessions(token)
    
    # Summary
    print("\n" + "="*70)
    print("✅ API Test Suite Completed!")
    print("="*70)
    print("\n📚 For full API documentation, visit:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("   - Documentation: docs/API_DOCUMENTATION.md")
    print()


if __name__ == "__main__":
    main()
