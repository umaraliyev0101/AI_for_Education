#!/usr/bin/env python3
"""
Test presentation upload with detailed debugging
"""
import requests
import os
import sys

BASE_URL = "http://localhost:8001/api"

print("="*70)
print("PRESENTATION UPLOAD TEST")
print("="*70)

# Step 1: Get credentials
print("\n[1] Please provide credentials:")
username = input("Username: ") or "admin"
password = input("Password: ") or "admin123"

# Step 2: Login
print("\n[2] Logging in...")
try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": username, "password": password}
    )
    print(f"    Status: {response.status_code}")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"    ✅ Login successful")
        print(f"    Token: {token[:20]}...")
    else:
        print(f"    ❌ Login failed: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"    ❌ Error: {e}")
    sys.exit(1)

# Step 3: Get lessons
print("\n[3] Getting lessons...")
try:
    response = requests.get(
        f"{BASE_URL}/lessons/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        lessons = response.json()
        print(f"    ✅ Found {len(lessons)} lessons")
        if lessons:
            print(f"    Available lesson IDs: {[l['id'] for l in lessons]}")
            lesson_id = lessons[0]['id']
            print(f"    Using lesson ID: {lesson_id}")
        else:
            print(f"    ⚠️  No lessons found. Creating one...")
            # Create a lesson
            create_response = requests.post(
                f"{BASE_URL}/lessons/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "title": "Test Lesson",
                    "subject": "Test",
                    "scheduled_at": "2025-11-02T10:00:00"
                }
            )
            if create_response.status_code in [200, 201]:
                lesson_id = create_response.json()['id']
                print(f"    ✅ Created lesson ID: {lesson_id}")
            else:
                print(f"    ❌ Failed to create lesson: {create_response.text}")
                sys.exit(1)
    else:
        print(f"    ❌ Failed to get lessons: {response.text}")
        sys.exit(1)
        
except Exception as e:
    print(f"    ❌ Error: {e}")
    sys.exit(1)

# Step 4: Check for test file
print("\n[4] Checking for test file...")
test_files = [
    "test.pptx",
    "test.pdf",
    "sample.pptx",
    "sample.pdf"
]

test_file = None
for tf in test_files:
    if os.path.exists(tf):
        test_file = tf
        break

if not test_file:
    print("    ⚠️  No test file found")
    test_file_path = input("    Enter path to .pptx or .pdf file: ")
    if not os.path.exists(test_file_path):
        print(f"    ❌ File not found: {test_file_path}")
        sys.exit(1)
    test_file = test_file_path

print(f"    Using file: {test_file}")
print(f"    File size: {os.path.getsize(test_file)} bytes")

# Step 5: Upload presentation
print("\n[5] Uploading presentation...")
try:
    with open(test_file, 'rb') as f:
        files = {'file': (os.path.basename(test_file), f, 'application/octet-stream')}
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"    Endpoint: POST {BASE_URL}/lessons/{lesson_id}/presentation")
        print(f"    File field: 'file'")
        print(f"    Filename: {os.path.basename(test_file)}")
        
        response = requests.post(
            f"{BASE_URL}/lessons/{lesson_id}/presentation",
            files=files,
            headers=headers
        )
        
        print(f"\n    Response Status: {response.status_code}")
        print(f"    Response Headers:")
        for key, value in response.headers.items():
            if key.lower() in ['content-type', 'content-length']:
                print(f"      {key}: {value}")
        
        print(f"\n    Response Body:")
        print(f"    {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n    ✅ Upload successful!")
                print(f"    Message: {data.get('message')}")
                print(f"    Filename: {data.get('filename')}")
                print(f"    File path: {data.get('file_path')}")
                print(f"    File size: {data.get('file_size')} bytes")
            except Exception as e:
                print(f"\n    ⚠️  Response is OK but JSON parsing failed: {e}")
                print(f"    This might be what your frontend is experiencing!")
        else:
            print(f"\n    ❌ Upload failed")
            try:
                error_data = response.json()
                print(f"    Error: {error_data.get('detail', response.text)}")
            except:
                print(f"    Raw error: {response.text}")
                
except Exception as e:
    print(f"    ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("Check server logs for detailed information")
print("="*70)
