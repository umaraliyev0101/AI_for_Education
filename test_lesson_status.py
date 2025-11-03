"""
Test script for lesson status update functionality
"""
import requests
import json

# API Configuration
BASE_URL = "http://localhost:8001"
API_PREFIX = "/api/v1"

# Test credentials (adjust as needed)
TEST_CREDENTIALS = {
    "username": "teacher",
    "password": "teacher123"
}

def login():
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/login",
        data=TEST_CREDENTIALS
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def get_lessons(token):
    """Get list of lessons"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/lessons/",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get lessons: {response.text}")
        return []

def update_lesson_status(token, lesson_id, new_status):
    """Update lesson status"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {"status": new_status}
    
    response = requests.put(
        f"{BASE_URL}{API_PREFIX}/lessons/{lesson_id}",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to update status: {response.text}")
        return None

def main():
    """Main test function"""
    print("=== Testing Lesson Status Update ===\n")
    
    # Login
    print("1. Logging in...")
    token = login()
    if not token:
        print("❌ Login failed. Exiting.")
        return
    print("✅ Login successful\n")
    
    # Get lessons
    print("2. Fetching lessons...")
    lessons = get_lessons(token)
    if not lessons:
        print("❌ No lessons found or failed to fetch lessons.")
        return
    print(f"✅ Found {len(lessons)} lesson(s)\n")
    
    # Display first lesson
    lesson = lessons[0]
    print(f"Selected Lesson:")
    print(f"  ID: {lesson['id']}")
    print(f"  Title: {lesson['title']}")
    print(f"  Current Status: {lesson['status']}")
    print()
    
    # Test status update
    print("3. Testing status update...")
    statuses_to_test = ["scheduled", "in_progress", "completed", "cancelled", "scheduled"]
    
    for new_status in statuses_to_test:
        print(f"\n   Updating status to: {new_status}")
        result = update_lesson_status(token, lesson['id'], new_status)
        
        if result:
            print(f"   ✅ Status updated successfully")
            print(f"   New Status: {result['status']}")
            if result.get('start_time'):
                print(f"   Start Time: {result['start_time']}")
            if result.get('end_time'):
                print(f"   End Time: {result['end_time']}")
        else:
            print(f"   ❌ Failed to update status to {new_status}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
